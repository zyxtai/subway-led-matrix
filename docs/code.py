import gc
import os
import ssl
import time
import displayio
from adafruit_matrixportal.matrix import Matrix

# Initialize the display before network imports. All lit pixels stay inside 2 px border.
matrix = Matrix(width=128, height=32, bit_depth=4)
display = matrix.display
# HUB75 scanning continues in hardware; only publish fully drawn frames.
display.auto_refresh = False
bitmaps = [displayio.Bitmap(128, 32, 6) for _ in range(2)]
bitmap = bitmaps[0]
palette = displayio.Palette(6)
for index, color in enumerate((0x000000, 0x101010, 0x201000, 0x202000, 0x600000, 0x101010)):
    palette[index] = color
groups = []
for frame in bitmaps:
    group = displayio.Group()
    group.append(displayio.TileGrid(frame, pixel_shader=palette))
    groups.append(group)
front = 0
display.root_group = groups[front]
display.refresh(minimum_frames_per_second=0)

try:
    import wifi
    import rtc
    import socketpool
    import adafruit_ntp
    import adafruit_requests
    import mta_minimal
    import arrival_ui
except Exception as error:
    for y in range(2, 30):
        for x in range(2, 126):
            bitmap[x, y] = 4
    display.refresh(minimum_frames_per_second=0)
    print("Missing dependency:", error)
    raise

REFRESH_SECONDS = 30
MAX_FEED_BYTES = 262144
BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F"
FEEDS = (("R", BASE + "gtfs-nqrw"), ("M", BASE + "gtfs-bdfm"))
ssid = os.getenv("WIFI_SSID") or os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("WIFI_PASSWORD") or os.getenv("CIRCUITPY_WIFI_PASSWORD")
epoch_offset = 946684800 - int(time.mktime((2000, 1, 1, 0, 0, 0, 5, 1, -1)))
pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=0, socket_timeout=5)
session = None
clock_synced = False
last_clock_sync = -3600
arrivals = {}
feed_age_at_fetch = None
fetched_at = None
failed = False
next_refresh = 0
last_render = -1
last_visual = None


def render():
    global last_render, last_visual, front
    tick = time.monotonic()
    if int(tick) == last_render:
        return
    last_render = int(tick)
    age = None if fetched_at is None else feed_age_at_fetch + tick - fetched_at
    now = int(time.time()) + epoch_offset
    key = arrival_ui.visual_key(arrivals, now, age, failed)
    if key == last_visual:
        return
    back = 1 - front
    arrival_ui.paint(bitmaps[back], arrivals, now, age, failed)
    display.root_group = groups[back]
    display.refresh(minimum_frames_per_second=0)
    front = back
    last_visual = key


print("Starting live M/R arrivals: 63 Dr, both directions; refresh every 30 seconds")
while True:
    render()
    if time.monotonic() < next_refresh:
        time.sleep(0.1)
        continue
    payload = None
    try:
        if not ssid or not password:
            raise RuntimeError("Set WIFI_SSID/WIFI_PASSWORD in settings.toml")
        if not wifi.radio.connected:
            wifi.radio.connect(ssid, password, timeout=15)
            session = None
            print("Wi-Fi connected:", wifi.radio.ipv4_address)
        if not clock_synced or time.monotonic() - last_clock_sync >= 3600:
            rtc.RTC().datetime = ntp.datetime
            clock_synced = True
            last_clock_sync = time.monotonic()
            print("UTC clock synchronized")
        if session is None:
            session = adafruit_requests.Session(pool, ssl.create_default_context())
        # Commit only after both feeds succeed, so a missing feed is not hidden.
        combined = {"G10S": [], "G10N": []}
        oldest_feed = None
        started = time.monotonic()
        for wanted_route, url in FEEDS:
            gc.collect()
            payload = bytearray()
            request_started = time.monotonic()
            with session.get(url, timeout=15, headers={"Connection": "close"}) as response:
                if response.status_code != 200:
                    raise RuntimeError("MTA HTTP {}".format(response.status_code))
                for chunk in response.iter_content(chunk_size=1024):
                    if time.monotonic() - request_started > 45:
                        raise RuntimeError("Download exceeded 45 seconds")
                    if len(payload) + len(chunk) > MAX_FEED_BYTES:
                        raise RuntimeError("Feed exceeds 256 KiB limit")
                    payload.extend(chunk)
                    render()
            now = int(time.time()) + epoch_offset
            feed_time, fresh = mta_minimal.decode(payload, now)
            print(wanted_route, "feed bytes:", len(payload))
            oldest_feed = feed_time if oldest_feed is None else min(oldest_feed, feed_time)
            for stop in combined:
                combined[stop].extend(row for row in fresh[stop] if row[2] == wanted_route)
            payload = None
            gc.collect()
        arrivals = {stop: sorted(set(rows))[:8] for stop, rows in combined.items()}
        fetched_at = time.monotonic()
        feed_age_at_fetch = int(time.time()) + epoch_offset - oldest_feed
        failed = False
        next_refresh = time.monotonic() + REFRESH_SECONDS
        print("MTA M/R updated; seconds:", time.monotonic() - started)
        for stop in ('G10S', 'G10N'):
            print(mta_minimal.STOPS[stop], arrivals[stop])
    except Exception as error:
        failed = True
        next_refresh = time.monotonic() + 60
        print("MTA update failed; retry in 60s:", type(error).__name__, error)
        import traceback
        traceback.print_exception(error)
        session = None
    finally:
        payload = None
        gc.collect()
        last_render = -1
        render()
        print("Free heap:", gc.mem_free())
