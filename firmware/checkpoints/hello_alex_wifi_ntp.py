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
    text="HELLO ALEX",
    color=0x404000,
    scale=2,
)
message.anchor_point = (0.5, 0.5)
message.anchored_position = (64, 16)
group.append(message)

display.root_group = group
print("Dual-panel 128x32 text test running: HELLO ALEX")

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

# Keep the clock in UTC so arrival timestamp calculations are consistent.
if wifi.radio.ipv4_address is not None:
    print("Synchronizing clock with NTP...")
    try:
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, tz_offset=0, socket_timeout=5)
        rtc.RTC().datetime = ntp.datetime
        now = time.localtime()
        print("Clock synchronized! UTC: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            now.tm_year, now.tm_mon, now.tm_mday,
            now.tm_hour, now.tm_min, now.tm_sec,
        ))
    except Exception as error:
        print("Clock sync failed (save code.py to retry):", error)
else:
    print("Clock sync skipped: Wi-Fi is not connected")

while True:
    time.sleep(1)
