# Subway integration

## Current scope and evidence

The current CircuitPython prototype displays the next two E/F/M/R predictions per direction at 63 Dr–Rego Park on a 128×32 display. It retrieves protobuf data directly over HTTPS with a small read-only GTFS-Realtime subset decoder. The Mac tools use official protobuf bindings for inspection and comparison; they are not a proxy required by the sign.

Actual board serial capture verified Wi-Fi, NTP, an 83,052-byte R feed, and four predictions in each direction: approximately 1.78 seconds to download and 1.42 seconds to decode, with 1,976,448 bytes free after cleanup. Alex subsequently provided another successful R-feed run. Both M/R feed decoders matched the official bindings on desktop snapshots, but no M predictions at G10 appeared in that sample. Recurring two-feed operation, the final buffered layout, and long-run stability are not yet independently confirmed.

## Station and feeds

Official MTA static GTFS downloaded October 24, 2026 identifies parent station G10, named 63 Dr-Rego Park, with platform IDs G10S and G10N. The selected UI directions are Manhattan-bound and Forest Hills-bound. These are direction labels, not a guarantee that each train terminates at Forest Hills.

| Route | Feed suffix | Platform IDs |
| --- | --- | --- |
| R | gtfs-nqrw | G10S / G10N |
| M | gtfs-bdfm | G10S / G10N |

Prefix each suffix with `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F`. Both feeds were downloaded without an API key during validation. Route operation and availability vary; do not invent M predictions when absent. The desktop inspector also supports the A/C/E feed and E/F filters for exploration; the board now accepts E/F/M/R.

## Deploy to the board

Use CircuitPython 10.3.1 on the MatrixPortal S3. The current board library installation includes adafruit_matrixportal and its dependencies, adafruit_requests, adafruit_connection_manager, and adafruit_ntp. These names describe the working installation; a fully pinned fresh-install bundle has not been prepared. Display text dependencies remain useful for the older checkpoints but the current renderer draws pixels directly. Built-in modules include displayio, wifi, rtc, socketpool, ssl, and gc.

Copy these files when CIRCUITPY is mounted:

| Repository file | Board destination |
| --- | --- |
| docs/code.py | CIRCUITPY/code.py |
| firmware/mta_minimal.py | CIRCUITPY/lib/mta_minimal.py |
| firmware/arrival_ui.py | CIRCUITPY/lib/arrival_ui.py |

Update helpers before code.py, then save code.py to trigger auto-reload. Keep credentials local in CIRCUITPY/settings.toml:

```toml
WIFI_SSID = "Your network name"
WIFI_PASSWORD = "Your password"
```

CIRCUITPY_WIFI_SSID/PASSWORD are also accepted. Never commit credentials. The code runs on the board, not desktop Python. Earlier runnable checkpoints are in firmware/checkpoints; they may require matching helper versions. The latest Manhattan time adjustment exists only in the repository: the board was disconnected during that deployment attempt. Recopy the current helper before relying on it.

## Display behavior

MNTN appears at the top left and FRST HLS at the bottom left. Two train slots per row show circular M/R badges and minute values, sorted together by predicted arrival time. Badge letters are black 5×7 glyphs in 13-pixel circles. Directions use bold 10-pixel-high lettering. Every lit pixel is inside x=2..125 and y=2..29: a two-pixel black border around the combined display, with no extra border at the panel seam.

| Element | Current color |
| --- | --- |
| Direction labels and time digits | 0x101010, dim neutral white |
| M circle | 0x201000, dim orange |
| R circle | 0x202000, dim yellow |
| Badge letters/background | Black |
| Stale exclamation marks | 0x600000, red |

The equal red/green yellow replaced a dimmer yellow that Alex observed as red. The 4-bit panel color depth quantizes low channel values; perceived brightness and color must be judged on the physical display.

Times round upward to minutes. The repository subtracts one displayed minute for Manhattan-bound G10S only and clamps at zero; Forest Hills-bound times are unadjusted. This is Alex's display preference, not an MTA-provided correction. It does not change feed timestamps, sorting, or past-arrival filtering. Values above 99 minutes show 99+. Dashes mean initial loading, missing predictions, or data hidden for age; they do not prove service has stopped.

The renderer draws into an inactive bitmap and explicitly publishes a complete frame, with automatic compositor refresh disabled. Hardware HUB75 scanning continues. A visual-state key avoids repainting unchanged route/minute/stale pixels. This fixes the visible clear-and-redraw path, but physical flicker reduction still needs confirmation and does not establish that power or scan timing is correct.

## Refresh and failure behavior

Three arrival feeds are fetched sequentially; a complete successful pair replaces the snapshot. The next fetch is scheduled 30 seconds after completion. Failure keeps the prior snapshot, marks it stale, and retries in 60 seconds. Stale indicators also appear above 90 seconds of feed age; all minute predictions are hidden after 180 seconds. Each feed is limited to 256 KiB and a 15-second socket timeout, with a 45-second elapsed check between chunks. Blocking DNS or socket calls can extend wall time. Wi-Fi reconnection and hourly NTP resynchronization are attempted before fetching.

The subset decoder skips unrelated fields, rejects unsupported/differential or stale headers, and filters canceled/deleted trips, skipped/no-data stops, missing arrival timestamps, past arrivals, and predictions more than one day away. It retains at most four predictions per platform per feed before merging. It is not a general protobuf implementation. Network operations and parsing remain synchronous; double buffering prevents publishing partial pixels but does not make the application asynchronous.

## Serial diagnostics

Use the MatrixPortal port identified by its USB ID; during testing it was `/dev/cu.usbmodem4ABCF8FA2E4C1`, at 115200 baud. Ports can change. Start monitoring, then save code.py. Look for Wi-Fi/NTP output, each route's feed bytes, `MTA M/R updated`, prediction lists, and free heap. Only one application should own the port at a time; a busy serial monitor prevents Codex from reading it concurrently. Actual board startup failures previously included a missing adafruit_connection_manager dependency and OverflowError from time.localtime(0); both were corrected. The epoch calculation now uses time.mktime for January 1, 2000.

## Desktop inspection and checks

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
.venv/bin/python tools/inspect_mta.py
.venv/bin/python tools/test_inspect_mta.py
python3 tools/test_arrival_ui.py
```

The inspector defaults to both G10 platforms and E/F/M/R filters across three feeds. Use `--stops G10S` or `--stops G10N` for one direction. Output includes feed bytes, age, entities, timing, predictions, and errors. It exits nonzero if any feed fails. Its payload limit is 2 MB, distinct from the board's 256 KiB limit.

Source checks cover canceled/skipped/past/missing-time predictions, stale/differential feeds, ordering, layout bounds, colors, and stale hiding. Additional checks performed during development covered visual-state changes, Manhattan offset/clamping, syntax, and deployed-copy equality before disconnection. These do not replace visual verification or a multi-hour reliability test.

## Next checks

Reconnect and deploy the pending Manhattan helper change. Verify both rows visually, confirm M/R badge brightness and reduced flicker, and inspect repeated serial updates. Exercise Wi-Fi loss/recovery and stale-data expiry. Record current draw and supply measurements separately before treating the final power design as validated. Keep the current working checkpoint before adding further routes, destinations, or enclosure work.

## Sources

- [MTA developer resources](https://www.mta.info/developers) and [realtime portal](https://api.mta.info/).
- [Official regular static GTFS](https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip).
- [GTFS-Realtime reference](https://gtfs.org/documentation/realtime/reference/) and [Python bindings](https://gtfs.org/documentation/realtime/language-bindings/python/).
- [CircuitPython framebuffer refresh](https://docs.circuitpython.org/en/stable/shared-bindings/framebufferio/index.html).

## E/F routes and service-alert hazards

The current repository application fetches gtfs-ace for E, gtfs-bdfm for F/M, and gtfs-nqrw for R, retaining only explicit predictions at G10S/G10N. E/F badges match the larger black-letter circle style: E uses dim blue 0x000020 and F shares M orange 0x201000. The palette now has seven entries. Continue showing the nearest two trains across all supported routes, not two per route. E/F only appear when MTA publishes a prediction at this station, including service changes; no normal stopping pattern is assumed.

A new firmware/mta_alerts.py decodes the standard selectors and active periods in the official camsys%2Fsubway-alerts protobuf feed. Copy this helper to CIRCUITPY/lib along with the updated mta_minimal.py and arrival_ui.py before deploying code.py. The alert payload cap is 768 KiB and it is requested every 120 seconds during normal arrival refreshes. This adds memory/network work that has not yet been measured on the S3.

Default hazard policy is an active MTA service alert with a matching supported route/station/trip/direction selector. This is a stated default pending Alex's response to the trigger question. Selectors within an alert are alternatives; constraints within each selector must all match. Period end times expire markers. Station-specific alerts for other stations are excluded; route-wide selectors can flag a badge without establishing delay to that individual train. Direction restrictions require a matching direction ID in the arrival feed. The marker is a small red triangle at the lower-right of the badge. MTA-specific Mercury display classification is not interpreted, so the marker is not a complete reproduction of the official service-status algorithm.

Alert errors are isolated from arrival updates: keep successful arrivals, retry alerts, and show the existing stale exclamation when alert status is unavailable. Cached hazards expire 180 seconds after retrieval; they are not proof of an all-clear when absent. Incoming alert headers older than 900 seconds are rejected. The 90/180-second arrival freshness rules remain. Tests cover all four routes, active periods, station/route/direction matching, unknown/nonmatching stops, hazard-induced repainting, badge bounds/colors, and stale alert rejection. The 505,752-byte alert sample produced the same two relevant selectors as official protobuf decoding.

This E/F/hazard revision is saved only in the repository because CIRCUITPY is currently unmounted. On-board library compatibility, memory use, repeated refreshes, final colors, and hazard legibility require testing after reconnecting. The pending Manhattan display adjustment will be included when the latest helper is deployed.
