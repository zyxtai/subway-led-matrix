from diagnostic_log import startup

import gc
import os
import ssl
import time
import displayio
from adafruit_matrixportal.matrix import Matrix

# Initialize the display before network imports. All lit pixels stay inside 2 px border.
matrix = Matrix(width=128, height=32, bit_depth=6)
display = matrix.display
# HUB75 scanning continues in hardware; only publish fully drawn frames.
display.auto_refresh = False
bitmaps = [displayio.Bitmap(128, 32, 8) for _ in range(2)]
bitmap = bitmaps[0]
palette = displayio.Palette(8)
NORMAL_COLORS = (0x000000, 0x101010, 0x602000, 0x202000, 0x600000, 0x101010, 0x000030, 0x602000)
for index, color in enumerate(NORMAL_COLORS):
    palette[index] = sum((max(4, (color >> shift & 255) // 8) if (color >> shift & 255) else 0) << shift for shift in (16, 8, 0))
palette[1] = palette[5] = 0x101010  # Brighter off-hours white text.
palette[6] = 0x000008  # Brighter off-hours E.
palette[3] = 0x080800  # Off-hours R yellow; normal rush palette is unchanged.
groups = []
for frame in bitmaps:
    group = displayio.Group()
    group.append(displayio.TileGrid(frame, pixel_shader=palette))
    groups.append(group)
front = 0
display.root_group = groups[front]
display.refresh(minimum_frames_per_second=0)
startup.first('DISPLAY_INIT', 'Matrix configured; initial blank frame')

try:
    import wifi
    import rtc
    import socketpool
    import adafruit_ntp
    import adafruit_requests
    import diagnostic_log
    import nyan_overlay
    import alarm
    import runtime_policy
    import microcontroller
    from watchdog import WatchDogMode
    import adafruit_connection_manager
    import mta_minimal
    import arrival_ui
except Exception as error:
    for y in range(2, 30):
        for x in range(2, 126):
            bitmap[x, y] = 4
    display.refresh(minimum_frames_per_second=0)
    print("Startup failed:", error)
    raise

startup.first('IMPORTS_READY', 'Display and network helpers imported')

# A transparent top layer leaves the scrolling text/arrivals running underneath.
cat_bitmap = displayio.Bitmap(128,32,len(nyan_overlay.COLORS))
cat_palette = displayio.Palette(len(nyan_overlay.COLORS))
for index,color in enumerate(nyan_overlay.COLORS):
    cat_palette[index] = color
cat_palette.make_transparent(0)
for group in groups:
    group.append(displayio.TileGrid(cat_bitmap,pixel_shader=cat_palette))

REFRESH_SECONDS = 30
MAX_FEED_BYTES = 262144
# Allocate once; repeated bytearray growth caused fragmented-heap MemoryError.
gc.collect()
feed_buffer = bytearray(MAX_FEED_BYTES)
BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F"
FEEDS = (("R", ("R",), BASE + "gtfs-nqrw"),
         ("FM", ("F", "M"), BASE + "gtfs-bdfm"),
         ("E", ("E",), BASE + "gtfs-ace"))
ssid = os.getenv("WIFI_SSID") or os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("WIFI_PASSWORD") or os.getenv("CIRCUITPY_WIFI_PASSWORD")
epoch_offset = 946684800 - int(time.mktime((2000, 1, 1, 0, 0, 0, 5, 1, -1)))
pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=0, socket_timeout=5)
session = None
clock_synced = False
last_clock_sync = -3600
cache = runtime_policy.FeedCache([f[0] for f in FEEDS], mta_minimal.STOPS)
due = {f[0]: 0 for f in FEEDS}
last_render = -1
last_visual = None
brightness_normal = None
boot_tick = time.monotonic()
reboot_deadline = boot_tick + 90 * 60
daily_done = None
watchdog = microcontroller.watchdog
watchdog.mode = None
watchdog.timeout = 30
watchdog.mode = WatchDogMode.RESET
last_watchdog = -1
incidents = startup.log
last_empty = False
sleep_requested = False

class SleepRequested(Exception):
    pass

if alarm.wake_alarm is not None:
    log_wake_pending = True
else:
    log_wake_pending = False


def log_incident(event,detail=''):
    if incidents is not None:
        try:
            incidents.record(event,detail)
        except Exception as error:
            print("Incident write failed:",error)

startup.first('APP_READY', 'Runtime initialized; entering display loop')

if 'WATCHDOG' in str(microcontroller.cpu.reset_reason):
    log_incident('WATCHDOG','Recovered after stalled execution')


def local_time():
    utc = time.localtime()
    return time.localtime(time.time() + runtime_policy.utc_offset(utc)*3600)


def sleep_until_morning():
    # Called only after HTTP cleanup. Keep a watchdog alive throughout standby.
    print("Night standby: display/Wi-Fi off; watchdog and RTC active")
    log_incident('NIGHT_STANDBY','Short sleeps; watchdog checks morning wake')
    for frame in bitmaps:
        frame.fill(0)
    cat_bitmap.fill(0)
    display.refresh(minimum_frames_per_second=0)
    try:
        adafruit_connection_manager.connection_manager_close_all(pool)
    except RuntimeError as error:
        if 'not managed' not in str(error):
            raise
        # Before the first HTTP request, the pool has no managed sockets.
    wifi.radio.enabled = False
    displayio.release_displays()
    watchdog.mode = None
    watchdog.timeout = 90
    watchdog.mode = WatchDogMode.RESET
    heartbeat = time.monotonic()
    while runtime_policy.overnight(local_time()):
        if time.monotonic()-heartbeat >= 10800:
            log_incident('STANDBY_OK','RTC and watchdog active')
            heartbeat = time.monotonic()
        watchdog.feed()
        delay = runtime_policy.standby_interval(time.time())
        try:
            wake = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+delay)
            alarm.light_sleep_until_alarms(wake)
        except Exception as error:
            log_incident('SLEEP_FALLBACK',type(error).__name__)
            # A timer/API failure must not leave the sign off indefinitely.
            until = time.monotonic()+delay
            while time.monotonic()<until:
                watchdog.feed()
                time.sleep(0.2)
        watchdog.feed()
    log_incident('MORNING_WAKE','Awake window reached; restart display')
    print("Awake window reached; restarting")
    microcontroller.reset()


def maintain():
    global daily_done, brightness_normal, last_visual, last_watchdog, sleep_requested
    tick = time.monotonic()
    remaining = reboot_deadline - tick
    if clock_synced:
        local = local_time()
        if runtime_policy.overnight(local):
            sleep_requested = True
        today = tuple(local[:3])
        if daily_done != today:
            if runtime_policy.reboot_minute(local):
                print("Scheduled 04:59 New York reboot")
                microcontroller.reset()
            daily_delay = runtime_policy.daily_remaining(local)
            if daily_delay > 0:
                remaining = min(remaining, daily_delay)
        normal = runtime_policy.rush(local)
    else:
        normal = False
    if remaining <= 0:
        print("Scheduled 90-minute reboot")
        microcontroller.reset()
    # Arm to the earlier deadline even if the following network call stalls.
    if tick - last_watchdog >= 0.5 or remaining < 2:
        timeout = max(0.1, min(30, remaining))
        if timeout < 30:
            # ESP32 cannot re-add an already watched task when changing timeout.
            watchdog.mode = None
            watchdog.timeout = timeout
            watchdog.mode = WatchDogMode.RESET
        else:
            watchdog.feed()
        last_watchdog = tick
    if normal != brightness_normal:
        for index, color in enumerate(runtime_policy.scaled_colors(NORMAL_COLORS,normal)):
            palette[index] = color
        brightness_normal = normal
        last_visual = None
        print("Brightness:", "rush hour" if normal else "very dim")


def render():
    global last_render, last_visual, front, last_empty
    maintain()
    if sleep_requested:
        return
    tick = time.monotonic()
    frame_tick = int(tick*10)
    if frame_tick == last_render:
        return
    last_render = frame_tick
    now = int(time.time()) + epoch_offset
    arrivals, age, warning = cache.snapshot(now)
    empty = clock_synced and not any(arrivals.values())
    if empty and not last_empty and any(item["timestamp"] is not None for item in cache.entries.values()):
        summary = []
        for name,item in cache.entries.items():
            age_text = '-' if item['timestamp'] is None else str(now-item['timestamp'])
            summary.append(name+'='+age_text+('!' if item['failed'] else ''))
        log_incident('DISPLAY_EMPTY',','.join(summary)+' heap='+str(gc.mem_free()))
    last_empty = empty
    local = local_time() if clock_synced else None
    cat_active = clock_synced and runtime_policy.nyan_active(local)
    cat_seconds = local[5] + (tick % 1) if cat_active else 0
    key = (arrival_ui.visual_key(arrivals,now,age,warning), arrival_ui.scroll_x(frame_tick),brightness_normal,cat_active,frame_tick if cat_active else 0,arrival_ui.flip_state(frame_tick))
    if key == last_visual:
        return
    back = 1-front
    arrival_ui.paint(bitmaps[back],arrivals,now,age,warning,scroll_step=frame_tick,flip_step=frame_tick)
    nyan_overlay.paint(cat_bitmap,frame_tick,cat_active,seconds=cat_seconds)
    display.root_group = groups[back]
    display.refresh(minimum_frames_per_second=0)
    front = back
    last_visual = key
    startup.first('FRAME_READY', 'Frame published; not visual confirmation')
    if any(arrivals.values()):
        startup.first('ARRIVALS_DRAWN', 'Frame with predictions published')


print("Independent E/F/M/R feeds; hourly :00-:10 test on", runtime_policy.HOURLY_TEST_DATE, "; morning schedule otherwise")
if log_wake_pending:
    log_incident('MORNING_WAKE','Time alarm resumed code.py')
while True:
    render()
    if sleep_requested:
        sleep_until_morning()
    ready = None
    for candidate in FEEDS:
        if time.monotonic() >= due[candidate[0]]:
            if ready is None or due[candidate[0]] < due[ready[0]]:
                ready = candidate
    if ready is None:
        time.sleep(0.02)
        continue
    name, routes, url = ready
    payload = None
    try:
        if not ssid or not password:
            raise RuntimeError("Set Wi-Fi credentials in settings.toml")
        if not wifi.radio.connected:
            startup.first('WIFI_BEGIN', 'Connecting')
            wifi.radio.connect(ssid,password,timeout=15)
            session = None
        startup.first('WIFI_READY', 'Connected')
        render()
        if not clock_synced or time.monotonic()-last_clock_sync >= 3600:
            try:
                startup.first('NTP_BEGIN', 'Synchronizing UTC')
                rtc.RTC().datetime = ntp.datetime
                if not clock_synced:
                    # A boot already within the reboot minute counts as today's reboot.
                    local = local_time()
                    if runtime_policy.reboot_minute(local):
                        daily_done = tuple(local[:3])
                clock_synced = True
                last_clock_sync = time.monotonic()
                startup.first('NTP_READY', 'UTC synchronized')
                print("UTC clock synchronized")
            except Exception:
                if not clock_synced:
                    raise
                last_clock_sync = time.monotonic()-3540  # Retry in one minute.
                print("NTP retry deferred; existing clock retained")
        render()
        if sleep_requested:
            raise SleepRequested()
        if session is None:
            session = adafruit_requests.Session(pool,ssl.create_default_context())
        started = time.monotonic()
        payload = feed_buffer
        payload_size = 0
        with session.get(url,timeout=15,headers={"Connection":"close"}) as response:
            if response.status_code != 200:
                raise RuntimeError("HTTP {}".format(response.status_code))
            for chunk in response.iter_content(chunk_size=1024):
                if time.monotonic()-started > 45:
                    raise RuntimeError("Download exceeded 45 seconds")
                if payload_size+len(chunk) > MAX_FEED_BYTES:
                    raise RuntimeError("Feed exceeds 256 KiB")
                payload[payload_size:payload_size+len(chunk)] = chunk
                payload_size += len(chunk)
                render()
                if sleep_requested:
                    raise SleepRequested()
        render()
        now = int(time.time())+epoch_offset
        timestamp,rows = mta_minimal.decode(memoryview(payload)[:payload_size],now)
        rows = {stop:[row for row in values if row[2] in routes] for stop,values in rows.items()}
        cache.success(name,rows,timestamp)
        startup.first('FEED_'+name, 'Decoded predictions='+str(sum(len(values) for values in rows.values())))
        due[name] = time.monotonic()+REFRESH_SECONDS
        print("Feed",name,"updated:",payload_size,"bytes; age:",now-timestamp)
    except SleepRequested:
        pass  # Response __exit__ has already closed its socket normally.
    except Exception as error:
        log_incident("FEED_FAIL",name+":"+type(error).__name__+":"+str(error))
        cache.failure(name)
        due[name] = time.monotonic()+60
        print("Feed",name,"failed; others continue:",type(error).__name__,error)
        try:
            adafruit_connection_manager.connection_manager_close_all(pool)
        except Exception:
            pass
        session = None
    finally:
        payload = None
        gc.collect()
        last_render = -1
        render()
        print("Free heap:",gc.mem_free())
