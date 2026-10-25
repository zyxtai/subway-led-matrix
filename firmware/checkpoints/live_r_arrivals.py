import gc
import os
import ssl
import time
import displayio
import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label

# Initialize the panel before importing networking dependencies.
matrix = Matrix(width=128, height=32, bit_depth=2)
group = displayio.Group()
header = label.Label(terminalio.FONT, text="STATION CONNECTING", color=0x303000, x=0, y=4)
lines = [label.Label(terminalio.FONT, text=text, color=0x404000, x=0, y=y)
         for text, y in (("MANHATTAN R --", 15), ("FOREST HLS R --", 26))]
group.append(header)
for line in lines:
    group.append(line)
matrix.display.root_group = group

try:
    import wifi
    import rtc
    import socketpool
    import adafruit_ntp
    import adafruit_requests
    import mta_minimal
    import arrival_ui
except Exception as error:
    header.text = "STATION LIB ERROR"
    print("Missing dependency:", error)
    raise

REFRESH_SECONDS = 30
MAX_FEED_BYTES = 262144
URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw"
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


def render():
    global last_render
    tick = time.monotonic()
    if int(tick) == last_render:
        return
    last_render = int(tick)
    age = None if fetched_at is None else feed_age_at_fetch + tick - fetched_at
    status, text = arrival_ui.rows(arrivals, int(time.time()) + epoch_offset, age, failed)
    if fetched_at is not None:
        header.text = "STATION " + status
        header.color = 0x400000 if status == "STALE" else 0x003000
    for line, value in zip(lines, text):
        line.text = value


print("Starting live R arrivals: the selected station, both directions; refresh every 30 seconds")
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
        if fetched_at is None:
            header.text = "STATION LOADING"
        gc.collect()
        started = time.monotonic()
        payload = bytearray()
        with session.get(URL, timeout=15, headers={"Connection": "close"}) as response:
            if response.status_code != 200:
                raise RuntimeError("MTA HTTP {}".format(response.status_code))
            for chunk in response.iter_content(chunk_size=1024):
                if time.monotonic() - started > 45:
                    raise RuntimeError("Download exceeded 45 seconds")
                if len(payload) + len(chunk) > MAX_FEED_BYTES:
                    raise RuntimeError("Feed exceeds 256 KiB limit")
                payload.extend(chunk)
                render()
        now = int(time.time()) + epoch_offset
        feed_time, fresh_arrivals = mta_minimal.decode(payload, now)
        # Commit a complete successful update; retain prior data on failure.
        arrivals = fresh_arrivals
        fetched_at = time.monotonic()
        feed_age_at_fetch = int(time.time()) + epoch_offset - feed_time
        failed = False
        next_refresh = time.monotonic() + REFRESH_SECONDS
        print("MTA updated:", len(payload), "bytes; seconds:", time.monotonic() - started)
        for stop in ('G10S', 'G10N'):
            print(mta_minimal.STOPS[stop], arrivals[stop])
    except Exception as error:
        failed = True
        next_refresh = time.monotonic() + 60
        if fetched_at is None:
            header.text = "STATION RETRY 60s"
            header.color = 0x400000
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
