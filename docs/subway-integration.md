# Subway integration

## Current scope and evidence

The current CircuitPython prototype displays the next two E/F/M/R predictions per direction at the selected station on a 128×32 display. It retrieves protobuf data directly over HTTPS with a small read-only GTFS-Realtime subset decoder. The Mac tools use official protobuf bindings for inspection and comparison; they are not a proxy required by the sign.

Actual board serial capture verified Wi-Fi, NTP, an 83,052-byte R feed, and four predictions in each direction: approximately 1.78 seconds to download and 1.42 seconds to decode, with 1,976,448 bytes free after cleanup. @zyxtai subsequently provided another successful R-feed run. Both M/R feed decoders matched the official bindings on desktop snapshots, but no M predictions at the selected station appeared in that sample. Recurring two-feed operation, the final buffered layout, and long-run stability are not yet independently confirmed.

## Station and feeds

Official MTA static GTFS downloaded October 24, 2026 identifies the selected station and its two platform IDs. The selected UI directions are Manhattan-bound and Forest Hills-bound. These are direction labels, not a guarantee that each train terminates at Forest Hills.

| Route | Feed suffix | Platform IDs |
| --- | --- | --- |
| R | gtfs-nqrw | Selected platforms |
| M | gtfs-bdfm | Selected platforms |

Prefix each suffix with `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F`. Both feeds were downloaded without an API key during validation. Route operation and availability vary; do not invent M predictions when absent. The desktop inspector also supports the A/C/E feed and E/F filters for exploration; the board now accepts E/F/M/R.

## Deploy to the board

Use CircuitPython 10.3.1 on the MatrixPortal S3. The current board library installation includes adafruit_matrixportal and its dependencies, adafruit_requests, adafruit_connection_manager, and adafruit_ntp. These names describe the working installation; a fully pinned fresh-install bundle has not been prepared. Display text dependencies remain useful for the older checkpoints but the current renderer draws pixels directly. Built-in modules include displayio, wifi, rtc, socketpool, ssl, and gc.

Set the private platform IDs first, then copy these files when CIRCUITPY is mounted:

| Repository file | Board destination |
| --- | --- |
| docs/code.py | CIRCUITPY/code.py |
| firmware/sign_app.py | CIRCUITPY/lib/sign_app.py |
| firmware/diagnostic_log.py | CIRCUITPY/lib/diagnostic_log.py |
| firmware/runtime_policy.py | CIRCUITPY/lib/runtime_policy.py |
| firmware/nyan_overlay.py | CIRCUITPY/lib/nyan_overlay.py |
| firmware/station_config.py | CIRCUITPY/lib/station_config.py |
| firmware/mta_minimal.py | CIRCUITPY/lib/mta_minimal.py |
| firmware/arrival_ui.py | CIRCUITPY/lib/arrival_ui.py |

Update helpers before code.py, then save code.py to trigger auto-reload. Keep credentials and station selection local in CIRCUITPY/settings.toml:

```toml
WIFI_SSID = "Your network name"
WIFI_PASSWORD = "Your password"
MTA_MANHATTAN_STOP = "<Manhattan-bound platform ID>"
MTA_QUEENS_STOP = "<Queens-bound platform ID>"
```

Replace the platform placeholders with the official GTFS platform IDs for your chosen station. Both IDs are required and must differ; missing settings stop startup with an explanatory error. The decoder and renderer share these settings, including the Manhattan-only minute adjustment. The configured platforms must serve the M/R feeds; selecting another route also requires changing the feed configuration. CIRCUITPY_WIFI_SSID/PASSWORD are also accepted. Never commit credentials. The code runs on the board, not desktop Python. Earlier runnable checkpoints are in firmware/checkpoints; they may require matching helper versions. Private station configuration and the latest Manhattan time adjustment exist only in the repository: the board was disconnected during that deployment attempt. Add the settings and copy all required helpers plus code.py before relying on these changes.

## Display behavior

MNTN appears at the top left and FRST HLS at the bottom left. Two train slots per row show circular M/R badges and minute values, sorted together by predicted arrival time. Badge letters are black 5×7 glyphs in 13-pixel circles. Directions use bold 10-pixel-high lettering. Every lit pixel is inside x=2..125 and y=2..29: a two-pixel black border around the combined display, with no extra border at the panel seam.

| Element | Current color |
| --- | --- |
| Direction labels and time digits | 0x101010, dim neutral white |
| M circle | 0x201000, dim orange |
| R circle | 0x202000, dim yellow |
| Badge letters/background | Black |
| Stale exclamation marks | 0x600000, red |

The equal red/green yellow replaced a dimmer yellow that @zyxtai observed as red. The 4-bit panel color depth quantizes low channel values; perceived brightness and color must be judged on the physical display.

Times round upward to minutes. The repository subtracts one displayed minute for the Manhattan-bound platform only and clamps at zero; Forest Hills-bound times are unadjusted. This is @zyxtai's display preference, not an MTA-provided correction. It does not change feed timestamps, sorting, or past-arrival filtering. Values above 99 minutes show 99+. Dashes mean initial loading, missing predictions, or data hidden for age; they do not prove service has stopped.

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
.venv/bin/python tools/inspect_mta.py --stops "PLATFORM_ID" "OTHER_PLATFORM_ID"
.venv/bin/python tools/test_inspect_mta.py
python3 tools/test_arrival_ui.py
python3 tools/test_station_config.py
```

The inspector requires explicit platform IDs and supports E/F/M/R filters across three feeds. Use `--stops "PLATFORM_ID"` to select a platform. Output includes feed bytes, age, entities, timing, predictions, and errors. It exits nonzero if any feed fails. Its payload limit is 2 MB, distinct from the board's 256 KiB limit.

Source checks cover canceled/skipped/past/missing-time predictions, stale/differential feeds, ordering, layout bounds, colors, and stale hiding. Additional checks performed during development covered visual-state changes, Manhattan offset/clamping, syntax, and deployed-copy equality before disconnection. These do not replace visual verification or a multi-hour reliability test.

## Next checks

Reconnect, add the private station settings, and deploy all required helpers and code.py. Verify both rows visually, confirm M/R badge brightness and reduced flicker, and inspect repeated serial updates. Exercise Wi-Fi loss/recovery and stale-data expiry. Record current draw and supply measurements separately before treating the final power design as validated. Keep the current working checkpoint before adding further routes, destinations, or enclosure work.

## Sources

- [MTA developer resources](https://www.mta.info/developers) and [realtime portal](https://api.mta.info/).
- [Official regular static GTFS](https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip).
- [GTFS-Realtime reference](https://gtfs.org/documentation/realtime/reference/) and [Python bindings](https://gtfs.org/documentation/realtime/language-bindings/python/).
- [CircuitPython framebuffer refresh](https://docs.circuitpython.org/en/stable/shared-bindings/framebufferio/index.html).

## Current update: alerts removed and one-minute buffer

As requested on October 25, service-alert requests and route hazard triangles are disabled. The application no longer imports mta_alerts or depends on alert-feed freshness. The unused parser source remains for history but is not part of deployment. Arrival-network stale indicators remain: they report outdated arrival data, not MTA service advisories.

All E/F/M/R arrival times in both directions now subtract one minute after rounding upward, clamped at zero: 7 minutes becomes 6, and 1 minute becomes 0. Source timestamps, train ordering, and expired-arrival filtering are unchanged. This supersedes the earlier Manhattan-only offset. E remains dim blue and F shares M orange. The program and updated arrival_ui.py have been copied to the board and verified byte-for-byte; the change still needs physical confirmation.

Deploy station_config.py, mta_minimal.py, and arrival_ui.py to CIRCUITPY/lib, followed by docs/code.py to CIRCUITPY/code.py. Station selection and Wi-Fi credentials remain private in settings.toml.

## Synchronized scrolling direction labels

Full MANHATTAN and FOREST HILLS names scroll left at 10 pixels per second in a shared cycle based on the longer label, with a short blank interval before both leading letters reenter from the right together. Text clips to x=2..56: two black columns at the left edge and three black columns (57..59) before the first circle at x=60. Circle/minute geometry is unchanged. Stale indicators sit below the label so they do not fill that gap. Both M and F now use a stronger dim orange 0x402000. The renderer still draws off-screen and publishes completed frames. Blocking network/parsing calls may pause animation temporarily; a shared monotonic clock keeps both rows in phase on resumption.

The current code and UI helper were saved to the repository and board. Run `python3 tools/test_scroll_labels.py` to check every phase, the clipping margins, fixed badge/minute pixels, wrap synchronization, stale indicator position, and palette consistency. Physical smoothness, hue, and readability require confirmation on the panel.

## Independent feed recovery and daily schedule

The application now caches and refreshes R, F/M, and E feeds independently. A failed feed retries in 60 seconds without preventing successful feeds from publishing. Each feed's own timestamp controls freshness; predictions older than 180 seconds are excluded individually. The red stale indicator can remain while healthy routes continue displaying. Managed HTTP sockets are closed after failures before recreating the session. Failed periodic NTP resynchronization does not discard an already synchronized clock.

New firmware/runtime_policy.py is a required board helper. Brightness follows America/New_York using current US daylight-saving rules: normal palette daily from 05:00 inclusive until 08:30 exclusive; one-quarter palette values at all other times. The board starts dim until NTP succeeds. Color depth is now 6 bits so the much lower off-hours white/color values remain representable. Real panel brightness, color, and scan shimmer still require observation.

The application resets after 90 minutes of runtime and additionally at 04:59 local time. A boot already within the 04:59 minute counts for that day, avoiding a reset loop. A 30-second hardware watchdog recovers stalled execution; close to the scheduled deadline it is rearmed to expire at that deadline. ESP32 timeout changes require disabling the watchdog briefly before reconfiguration. These are powered-runtime schedules: the board cannot reboot while unpowered, and the daily wall-clock event requires successful NTP. Brief startup/network gaps are expected after each reboot. Future timezone-law changes require updating the helper.

Run `python3 tools/test_runtime_policy.py` for per-feed failure/expiry isolation, New York DST transitions, rush-hour boundaries, the daily reboot minute, and palette scaling. Scheduled hardware reboots have not yet been observed at the actual future times. Keep runtime_policy.py synchronized with docs/code.py when deploying.

## Hourly Nyan Cat overlay and brighter white text

During non-rush hours, the first minute of each New York clock hour (minute 00, seconds 00–59) adds a transparent Nyan Cat pixel-art layer above the normal screen. The cat travels right-to-left at 20 pixels per second, exits fully, and repeats from the right until the minute ends. It is disabled from 05:00 through 08:29 and before clock synchronization. Text and arrivals continue updating underneath, so the overlay temporarily covers pixels as it passes rather than replacing the screen. The first/last two border columns stay black. Network/parsing blocks may pause visible animation; its next frame resumes from the shared monotonic phase.

Copy the new firmware/nyan_overlay.py helper to CIRCUITPY/lib along with runtime_policy.py and the latest code.py. Off-hours white label/time text is now 0x101010 instead of 0x040404 to reduce the low-brightness green cast; route badges retain their off-hours dimming and R readability override. Color balance still requires physical confirmation.

## Persistent failure diagnostics and fixed download buffer

Actual serial capture identified an F/M MemoryError while a growing bytearray requested a contiguous 154,340-byte allocation, despite substantial total free heap. The application now allocates one 256 KiB download buffer at startup and reuses it with bounded slice writes and a memoryview for decoding, avoiding repeated growing-buffer reallocations. Independent feed caches and expiry rules remain active.

The selected logging mode preserves normal CIRCUITPY editing. New diagnostic_log.py stores a bounded ring of incidents in microcontroller.nvm so failures survive resets; it does not make the USB drive read-only or enable unsafe simultaneous writes. The ring uses up to the final 4096 NVM bytes with 128-byte records; actual retained record count depends on board NVM size. It refuses initialization if that region contains unrecognized nonempty data. Repeated identical failures are throttled for five minutes. Records include UTC time (potentially unsynchronized before NTP), sequence, event, and compact detail; no credentials or configured station IDs are logged. Oldest records are overwritten when full, so export promptly after a failure.

Logged events include feed exceptions (such as allocation/HTTP/timeout errors), transition to an empty arrival display with feed ages/failure flags/free heap, and watchdog recovery. The initial BUFFER_FIX record documents the observed root cause. A blank screen caused by a hard crash before logger initialization cannot itself be recorded; the watchdog recovery may supply evidence afterward.

To export separate incident JSON files into CIRCUITPY/logs while debugging, close other serial monitors, then run from the Mac:

```sh
python3 tools/export_board_logs.py --port /dev/cu.usbmodemYOUR_BOARD --drive /Volumes/CIRCUITPY
```

The exporter briefly interrupts the application, retrieves the persistent ring, writes one incident-UTC-sequence.json file per record using the Mac's drive access, and restarts the application. Files are created when exporting, not automatically at the moment of failure; that distinction preserves the editing mode requested by @zyxtai. Deploy diagnostic_log.py with the other helpers. Exported log content is diagnostic information and should be reviewed before sharing.

## Larger cat and persistent rainbow

The overlay cat is now rendered at 2× scale (up to roughly 40×24 pixels), on top of the unchanged arrival layer. Passes start every ten seconds during the one-minute hourly window. The first pass leaves a rainbow across the screen; middle passes retain it. The final pass removes the trail behind the cat as it crosses left, and the overlay clears at the end of the minute. Both sprite and rainbow retain the two-pixel outer border. The larger top layer temporarily covers more text; underlying content is not deleted.

## Four arrivals and overnight sleep

The current renderer shows four nearest E/F/M/R predictions per direction. Scrolling labels are clipped to x=2..26, with x=27..29 blank before the four 13-pixel circles at x=30,54,78,102. Minute digits use a compact 3×5 font; ++ indicates more than 99 minutes. The two-pixel outer border, synchronized scrolling, one-minute time adjustment, and cat top layer remain. E is slightly brighter (normal 0x000030, off-hours 0x000008).

The powered controller blanks and releases the matrix driver at 20:30 New York time, disables its watchdog for the sleep interval, and schedules an alarm for 04:59 the next morning. It also sleeps until 04:59 if started during the overnight interval. Wake calculations account for the DST change during the night. Clock synchronization is required. The panel supply is not physically switched off. CircuitPython simulates deep sleep when connected to a USB host to retain editing access; actual low-power sleep is expected when running standalone. A wake restarts code.py, reconnects Wi-Fi, and resumes the existing 90-minute daytime reboot policy.

Tests cover four-slot bounds, clipping, compact long-time formatting, overnight boundaries, and next-morning wake times including both DST transitions. Actual overnight sleep/wake and physical readability need observation at the scheduled times.

## Two-slot flipping pages (current layout)

The wide label viewport x=2..56 and original slots x=60/94 are restored, with large minute digits. Four upcoming trains remain available, displayed as two pages: arrivals 1–2 and arrivals 3–4. Both directions share a four-second page clock and a short vertical compression/expansion flip affecting only circles and minutes. Direction scrolling, border, brightness, overnight sleep, logging, and Nyan Cat continue unchanged. If a direction has only one or two predictions, both pages repeat those rather than intentionally hiding them. Times above 99 minutes again show 99+.

The page-flip interval is now six seconds, with a 1.6-second multi-stage vertical collapse/expand transition. Both directions remain synchronized; this supersedes the four-second timing above.

## Morning-only awake window (current)

As of October 27, the controller is awake only from 04:59 inclusive until 08:30 exclusive every day in America/New_York. At 08:30 it blanks the display and sleeps until the next 04:59, with DST-aware wake calculations. Starting outside the awake window also enters sleep after clock synchronization. This supersedes the previous 20:30 shutdown. USB-connected sleep may be simulated, and panel power is not physically disconnected. Existing brightness, reboot, and animation rules remain; the hourly non-rush cat window no longer normally occurs while awake under this morning-only schedule.

## Morning wake reliability revision

The deep-sleep wake failure reported October 28 could not be diagnosed on hardware because neither CIRCUITPY nor its serial port was connected. The next repository revision replaces the long overnight alarm with a display-blanked idle loop: Wi-Fi off, hardware RTC running, watchdog fed, and a local-time check every half second. Entering the 04:59–08:30 awake window triggers a reset to reconnect and redraw. It preserves the daily display schedule but is not deep sleep and consumes more standby energy. NIGHT_IDLE and MORNING_WAKE incidents distinguish overnight entry and successful wake in the persistent ring. This revision is not yet on the board; reconnect it for deployment and log export.

## Low-power sleep transition fix (current)

The application again uses the morning-only schedule with true deep sleep when standalone, rather than the higher-power RTC-polling fallback. Shutdown is now deferred to the outer loop: render/maintenance only raises a flag, and an in-progress HTTP request exits normally before its sockets are closed and sleep begins. This avoids the logged Socket not managed error caused by shutting down the socket manager inside an active response. Only the outer loop calls the sleep function, outside HTTP contexts and broad exception handlers.

Shutdown publishes a black frame, closes managed sockets, disables Wi-Fi and watchdog, releases the matrix driver, and arms the DST-aware 04:59 time alarm. The alarm wake is now recorded. This reduces controller energy versus continuously polling all night, but does not physically switch off the panel supply. USB-host connections simulate sleep for editing; disconnect USB data when evaluating standalone power use. A temporary five-second test produced SHORT_SLEEP_START followed by SHORT_SLEEP_WAKE TimeAlarm on the connected board; it verifies the USB simulation path, not a full autonomous overnight test. The corrected application and schedule were restored and checked afterward.


## Current overnight wake policy — October 30

The current implementation supersedes the deep-sleep policies above. The awake window is 04:59–08:30 America/New_York daily, with DST handled by runtime_policy. After HTTP cleanup, standby blanks the panel, releases the matrix driver, and disables Wi-Fi. Short light sleeps of at most one minute keep RTC checks and the 90-second standby watchdog active; the final sleep ends at the 04:59 boundary, records MORNING_WAKE, and resets the controller to reconnect and redraw. A timer exception falls back to watchdog-fed polling. BOOT, NIGHT_STANDBY, and three-hour STANDBY_OK records improve diagnosis. Standby consumes more energy than true deep sleep; panel supply power is still connected and draw has not been measured. Continuous electrical power is required.


## Startup diagnostics

The board entry point docs/code.py opens the persistent incident log before importing firmware/sign_app.py, which contains the display application. Deploy sign_app.py and diagnostic_log.py to CIRCUITPY/lib before copying the new code.py. Normal morning scheduling is unchanged. The existing root runtime_policy.py takes precedence over the lib copy; keep both installed copies synchronized if both exist.

Startup checkpoints are BOOT, DISPLAY_INIT (matrix setup and initial blank frame), IMPORTS_READY, APP_READY, FRAME_READY (a noninitial frame submitted), WIFI_BEGIN, WIFI_READY, NTP_BEGIN, NTP_READY, FEED_R/FEED_FM/FEED_E (first successful decode per feed, with a prediction count), and ARRIVALS_DRAWN (first frame containing predictions submitted). Each checkpoint is recorded once per application start to limit flash writes. A frame submission is software evidence, not confirmation that a person saw light on the panels.

An unhandled application exception records FATAL with the last checkpoint and exception class, then preserves the normal serial traceback. Exception messages are excluded from the new persistent fatal record to avoid copying private settings. Logging failures do not prevent startup. Persistent logging cannot capture a power cut, a native firmware crash, or failure before the logging helper loads. UTC timestamps before NTP may be unset after power loss; use sequence numbers to interpret startup order. The existing incident ring is bounded, so export it promptly after a failed morning.

Run python3 tools/test_startup_diagnostics.py alongside the sleep-transition, schedule, and incident-log tests. Hardware verification must distinguish a USB-connected short standby/reset test from an autonomous overnight run on the usual power supply.


## Temporary hourly wake test — October 31

HOURLY_TEST_DATE in runtime_policy.py enables hourly cycling only on October 31, 2026 in New York. During that date, minutes 00–09 are awake and minutes 10–59 are standby. Standby retains the one-minute checks and watchdog, then records MORNING_WAKE (the existing event name, with a generic awake-window detail) and resets at the next whole hour. The extra daily 04:59 reset is suppressed during this test to avoid interrupting the hourly cycle. Brightness and animation rules remain unchanged; the cat can appear during the first minute of non-rush test hours.

The hourly policy expires at local midnight without another deployment. After 23:10 on the test date, the next awake window is November 1 at 04:59 rather than midnight; wake calculation includes the overnight daylight-saving transition. The normal 04:59–08:30 daily policy then resumes. Update both installed runtime_policy.py copies and sign_app.py when deploying. Run tools/test_hourly_schedule.py for all hour boundaries, final wake seconds, expiry, and the fall DST transition. @zyxtai observed the October 31 13:00 turn-on and approximately 13:10 shutdown. Further cycles and the return to the morning schedule remain to be observed; the power/USB arrangement for that observation was not independently verified.
