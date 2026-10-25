import gc
import ssl
import rtc
import socketpool
import adafruit_ntp
import os
import wifi
import time
import displayio
import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label

# Two 64x32 panels chained horizontally form one 128x32 display.
matrix = Matrix(width=128, height=32, bit_depth=2)
display = matrix.display

group = displayio.Group()
message = label.Label(
    terminalio.FONT,
    text="HELLO WORLD",
    color=0x404000,
    scale=2,
)
message.anchor_point = (0.5, 0.5)
message.anchored_position = (64, 16)
group.append(message)

display.root_group = group
print("Dual-panel 128x32 text test running: HELLO WORLD")

# Read local credentials without including them in the program or Git.
ssid = os.getenv("WIFI_SSID") or os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("WIFI_PASSWORD") or os.getenv("CIRCUITPY_WIFI_PASSWORD")

if not ssid or not password:
    print("Set WIFI_SSID and WIFI_PASSWORD in CIRCUITPY/settings.toml")
else:
    print("Connecting to Wi-Fi...")
    try:
        wifi.radio.connect(ssid, password, timeout=15)
        print("Connected! IP address:", wifi.radio.ipv4_address)
    except Exception as error:
        print("Wi-Fi connection failed:", error)

clock_synced = False

# Keep the clock in UTC so arrival timestamp calculations are consistent.
if wifi.radio.ipv4_address is not None:
    print("Synchronizing clock with NTP...")
    try:
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, tz_offset=0, socket_timeout=5)
        rtc.RTC().datetime = ntp.datetime
        clock_synced = True
        now = time.localtime()
        print("Clock synchronized! UTC: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            now.tm_year, now.tm_mon, now.tm_mday,
            now.tm_hour, now.tm_min, now.tm_sec,
        ))
    except Exception as error:
        print("Clock sync failed (save code.py to retry):", error)
else:
    print("Clock sync skipped: Wi-Fi is not connected")

# One-shot Phase 4 experiment: R predictions for both directions.
# Keep the greeting displayed; no automatic polling until memory is verified.
if clock_synced and wifi.radio.ipv4_address is not None:
    payload = None
    try:
        import adafruit_requests
        import mta_minimal
        gc.collect()
        print("MTA heap before HTTPS:", gc.mem_free(), "bytes")
        session = adafruit_requests.Session(pool, ssl.create_default_context())
        started = time.monotonic()
        payload = bytearray()
        low_heap = gc.mem_free()
        url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw"
        with session.get(url, timeout=15, headers={"Connection": "close"}) as response:
            if response.status_code != 200:
                raise RuntimeError("MTA HTTP status {}".format(response.status_code))
            for chunk in response.iter_content(chunk_size=1024):
                if time.monotonic() - started > 45:
                    raise RuntimeError("MTA download exceeded 45 seconds")
                if len(payload) + len(chunk) > 262144:
                    raise RuntimeError("MTA feed exceeds 256 KiB experiment limit")
                payload.extend(chunk)
                low_heap = min(low_heap, gc.mem_free())
        downloaded = time.monotonic()
        # Normalize CircuitPython's epoch if this firmware uses year 2000.
        epoch_offset = 946684800 - int(time.mktime((2000, 1, 1, 0, 0, 0, 5, 1, -1)))
        now_unix = int(time.time()) + epoch_offset
        feed_time, arrivals = mta_minimal.decode(payload, now_unix)
        print("MTA bytes:", len(payload))
        print("Download seconds:", downloaded - started)
        print("Decode seconds:", time.monotonic() - downloaded)
        print("Lowest sampled download heap:", low_heap, "bytes")
        print("Heap after decode:", gc.mem_free(), "bytes")
        print("Feed age seconds:", now_unix - feed_time)
        for stop_id in ("G10S", "G10N"):
            print("the selected station /", mta_minimal.STOPS[stop_id])
            if not arrivals[stop_id]:
                print("  No upcoming R predictions in this feed")
            for arrival_time, trip_id in arrivals[stop_id]:
                minutes = (arrival_time - now_unix + 59) // 60
                print("  R in", minutes, "min; trip", trip_id)
        print("MTA test complete. Save code.py to run again.")
    except Exception as error:
        print("MTA test failed:", type(error).__name__, error)
        import traceback
        traceback.print_exception(error)
    finally:
        payload = None
        gc.collect()
        print("Heap after cleanup:", gc.mem_free(), "bytes")
else:
    print("MTA test skipped: requires Wi-Fi and successful clock sync")
while True:
    time.sleep(1)
