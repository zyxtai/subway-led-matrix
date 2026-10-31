# Work Log

## 2026-10-10 — Development workflow

- Updated the project plan to make Visual Studio Code the primary development environment while allowing alternatives such as Arduino IDE.
- Removed hard line breaks within project-plan paragraphs and list items; verified the text content and fenced code blocks were preserved.
- Revised the setup status to start fresh and verify the board's current state, treating the earlier bootloader result as a historical observation.
- Renamed the document title to Project Plan and updated its preservation instruction to reference `docs/PROJECT_PLAN.md`.
- Added a repository rule requiring the `learn` skill to update this log before opening any PR, including draft PRs, with the log update included in the PR branch.
- Installed the reusable `learn` skill in `~/.codex/skills/learn` and recorded the preference for natural Markdown wrapping in `AGENTS.md`.
- Validated the skill frontmatter and UI metadata with Ruby YAML parsing. The bundled Python validator could not run because PyYAML is unavailable; no application tests were needed for these documentation changes.
- Before opening the PR, applied the `learn` skill to review this entry against the branch changes and confirmed `git diff --check origin/main...HEAD` passed. The `learn` skill is installed locally; other contributors will need to install it to follow the PR workflow.

## 2026-10-12 — Phase 0 documentation

- Created `docs/phase-0-foundation` from the merged `main` branch and expanded the README with project goals, repository setup, documentation links, and the branch-and-PR workflow.
- Added `docs/hardware.md`, `docs/wiring.md`, and `docs/decisions.md` using the project plan as the source. Distinguished reported specifications and proposed designs from physically verified results; preserved uncertainty about ordered parts, supply polarity, USB-C power suitability, and the board's current state.
- Documented the smallest next experiment: connect only the controller to the Mac with a USB data cable and record USB detection before choosing or installing firmware. No hardware was connected or tested and no firmware/toolchain was selected or installed during this documentation work.
- Applied the `learn` skill to record the completed changes and review their purpose and limitations. Checked all relative Markdown links and fenced code blocks across the project documents; `git diff --check` passed. No application tests were needed for documentation changes.
- Added the shared `learn` skill and its UI metadata under `.agents/skills/learn/`. Updated repository instructions, the README, and decisions to use the repository copy as the source of truth and require project-specific skills to be version controlled. This removes the need to distribute @zyxtai's personal installation separately.
- Validated the repository skill's frontmatter and UI metadata with Ruby YAML parsing because PyYAML remains unavailable. Rechecked 11 relative Markdown links and fenced code blocks across eight documents; whitespace checks passed.
- Ran the repository-owned `learn` skill again after commit `f5623b5`: reviewed the complete diff against `origin/main`, confirmed both skill files are tracked, and verified `git diff --check origin/main...HEAD` passed. Updated this entry rather than creating a duplicate.
- Lesson: a PR rule that depends on a personal skill installation is incomplete for a shared repository. Version the skill with the project and explicitly prefer the repository copy so contributors use the same instructions.
- The initial Phase 0 documents are in place. Fresh board verification and toolchain evaluation remain Phase 1 work.

## 2026-10-24 — CircuitPython display bring-up and Phase 4 preparation

- Verified the connected board identified itself in `boot_out.txt` as Adafruit MatrixPortal S3 running CircuitPython 10.3.1. CircuitPython is the current display-prototyping runtime; the final runtime remains subject to feed-decoding memory and performance tests.
- @zyxtai reported the single-panel red/green/blue test worked after increasing the palette values from 0x10 to 0x40 per channel. A successful serial message was also reported. The earlier desktop Python `displayio` import error did not establish a board firmware problem.
- Prepared a single-panel HELLO/WORLD text test, then updated the board script for two attached 64×32 panels: 128×32 framebuffer, double-size HELLO WORLD centered at (64, 16), and dim yellow 0x404000 text. The dual-panel visual result, panel order, orientation, and sustained operation still need explicit confirmation.
- Included the current board script as `docs/code.py` so the display checkpoint is reproducible from the repository. Saving it as CIRCUITPY/code.py runs it on the board; running it with the Mac's Python does not provide CircuitPython hardware modules.
- Updated setup status, hardware notes, wiring observations, and runtime decisions to distinguish verified results from proposed wiring and unfinished tests. No supply voltage, polarity, current draw, or final power distribution measurements were reported.
- Next experiment: confirm the dual-panel text display, then connect the S3 to Wi-Fi and print its IP address. Keep credentials out of Git. Clock synchronization, official MTA endpoint and stop-ID verification, feed inspection, and on-device protobuf feasibility remain pending.
- Validation: parsed the saved Python source with `ast.parse`, compared the repository copy byte-for-byte with the board file, checked local Markdown links, and ran `git diff --check`. These are source checks, not a new hardware execution test.
- Lesson: save known-good display checkpoints and isolate display, network, and feed-decoding experiments; a working display does not yet establish that CircuitPython can process the target MTA feeds.

## 2026-10-24 — Wi-Fi confirmed and NTP checkpoint prepared

- @zyxtai confirmed the board connected to Wi-Fi. Added startup NTP synchronization using the Adafruit NTP library, the built-in socket pool, and RTC; kept HELLO WORLD displayed and used UTC for future arrival timestamp calculations.
- Installed the Adafruit NTP Python source on the board, synchronized docs/code.py with the board program, and documented the added dependency and expected serial output. Credentials were neither read nor modified during this change.
- Parsed both Python files and verified the repository and board program copies match; `git diff --check` passed. NTP success has not been observed in the serial console and requires @zyxtai's confirmation. No MTA feed retrieval or decoding is implemented yet.

## 2026-10-24 — Phase 4 live feed inspection

- Added tools/inspect_mta.py and pinned desktop GTFS bindings to inspect MTA protobuf feeds before attempting an embedded decoder. Preserved the working board program and existing uncommitted Wi-Fi/NTP changes.
- Downloaded official MTA static GTFS and verified the earlier exploratory station and platform IDs. Station/direction remain configurable pending preference confirmation; no destination or current service pattern is assumed.
- Successfully downloaded and decoded A/C/E, B/D/F/M, and N/Q/R/W feeds without an API key. Observed E/F/R predictions, feed sizes about 67–84 KB, and ages 6–8 seconds in the test run. Added freshness checks and excluded canceled, skipped, past, and missing-time predictions.
- Added runnable semantic unit checks and docs/subway-integration.md explaining feeds, filtering, timestamps, reproduction, and limitations. Three test methods passed, including multiple rejection scenarios; git diff --check and local Markdown link validation passed.
- @zyxtai confirmed Wi-Fi and indicated the clock-sync checkpoint succeeded; Codex has not independently captured board serial output. On-device subway download/decoding, memory feasibility, display arrival rendering, and destination resolution remain unverified. The Mac tool is an experiment, not a required proxy.

## 2026-10-24 — Initial station selection

- @zyxtai chose the selected station for both Manhattan-bound and Queens-bound service. Verified the parent station and both platform IDs in the downloaded official static GTFS; updated inspector defaults, fixtures, project plan, and related documentation. Preserved earlier Forest Hills validation as history.
- Ran all three live feeds successfully with no errors and observed R predictions for both selected platforms. Kept configurable E/F/M/R filtering to accommodate feed predictions without assuming all routes normally stop here. Three semantic test methods and git diff --check passed. The board program is unchanged; on-device integration remains the next experiment.

## 2026-10-24 — On-board R-feed experiment prepared

- Added firmware/mta_minimal.py, a bounded subset parser for R predictions at the selected platforms, labeled Manhattan-bound and Forest Hills-bound as requested. Preserved the previous board script under firmware/checkpoints before deploying the new one-shot HTTPS test.
- Kept HELLO WORLD on screen and added serial predictions, feed freshness, payload bytes, elapsed times, and sampled free-heap metrics. Require successful Wi-Fi/NTP, close the HTTP response, cap payload size, and report failures without removing the greeting. No credentials were read or changed.
- Compared the subset decoder with official protobuf bindings on the same live 85,932-byte feed: all nearest-four predictions matched for both platforms. Malformed/truncated and stale-input checks passed. Python syntax and board/repository copy equality passed; git diff --check passed. On-board execution and memory feasibility remain unconfirmed until serial output is reviewed.

## 2026-10-24 — Recovered startup and verified on-board arrivals

- Captured the MatrixPortal serial traceback: adafruit_requests required missing adafruit_connection_manager. Installed the official dependency and moved subway imports into the guarded experiment after display initialization. Fixed a second error: time.localtime(0) overflowed on this firmware; epoch normalization now uses time.mktime for January 1, 2000.
- Reran the actual board with serial capture: Wi-Fi and NTP succeeded, an 83,052-byte feed downloaded in about 1.78 seconds and decoded in about 1.42 seconds, and four R predictions printed for each of Manhattan-bound and Forest Hills-bound at the selected station. Lowest sampled download free heap was 1,830,768 bytes, with 1,976,448 bytes free after cleanup. These are one-run measurements, not a long-run reliability result.
- Updated both code copies and documented the dependency. Syntax, copy equality, and git diff --check passed. Serial confirms the greeting program initialized; the physical panel appearance still needs @zyxtai's visual confirmation. The serial connection was released after checking.

## 2026-10-24 — Live dual-direction arrival rows

- Replaced the greeting with a station/status header and nearest R arrival rows for Manhattan-bound and Forest Hills-bound. Added one-second countdown formatting, 30-second refresh scheduling, 60-second failure retry, Wi-Fi reconnect attempts, and hourly NTP synchronization. Saved the serial-only checkpoint before deployment.
- Added firmware/arrival_ui.py and countdown/expiry/error tests. Mark prior predictions STALE immediately after update failures or when the feed is older than 90 seconds; hide times beyond 180 seconds. Keep direction labels distinct from train terminal destinations.
- Deployed code and UI helper to the board and verified byte equality with repository copies. Two formatting test methods, Python syntax, and git diff --check passed. Actual recurring board execution and physical layout are pending confirmation: serial capture could not open the port because it was already busy, so no new hardware-run success is claimed. Network and parse operations remain synchronous and can pause countdown updates temporarily.

## 2026-10-24 — Two-train M/R pixel layout

- Implemented @zyxtai's requested bold white MNTN/FRST HLS layout, two-pixel outer border, orange M and yellow R circular badges with white letters, and the next two combined arrivals per direction. Times are minutes; 99+ caps longer values. Preserved stale indication as red exclamation marks without using the outer border.
- Added B/D/F/M feed retrieval and extended the bounded decoder to retain route IDs for M/R predictions. Merge and commit only after both feeds succeed; do not invent M predictions when absent. Preserved the prior R-only program as a checkpoint and deployed both helpers plus code.py.
- Pixel-boundary, sorting, color, expiry, and formatting checks passed. Compared both live feeds against official GTFS decoding: matches for both, four R predictions each direction and no M predictions at the selected station in that snapshot. Syntax, board/repository equality, and git diff --check passed. Hardware appearance and recurrent refreshes for this revision remain pending visual/serial confirmation.

## 2026-10-24 — Dim labels and larger route badges

- Dimmed only the MNTN/FRST HLS labels to neutral 0x404040 while retaining white time digits. Enlarged route circles from 11 to 13 pixels across and replaced white letters with larger black 5×7 M/R glyphs. Adjusted lower-row placement to keep the two-pixel outer border intact.
- Updated the board and repository copies and checked Python syntax, pixel bounds, stale behavior, and train ordering with the renderer checks. Physical appearance still needs visual confirmation.

## 2026-10-24 — Buffered refresh and dim M badges

- Added two off-screen bitmap/group buffers, disabled automatic compositor refresh, and publish completed frames with an explicit framebuffer refresh. Added a visual-state key so unchanged minute/route/status pixels are not cleared and repainted each second. Hardware panel scanning remains active.
- Dimmed M orange to 0x201000 to match the low-brightness yellow/white palette. Preserved the larger black route letters and two-pixel border. Updated board and repository copies.
- Python syntax, layout tests, visual-key countdown/stale checks, deployed-copy equality, and git diff --check passed. Perceived flicker and brightness still require physical confirmation; no claim is made about correcting power or continuous scan-related flicker.

## 2026-10-24 — Learn review and current documentation refresh

- Applied the repository-owned learn skill to review current code, pending changes, validation results, and deployment state. Rewrote README and subway integration instructions around the actual M/R display; refreshed project-plan status, hardware observations, and decisions while preserving earlier work-log history.
- Recorded the final palette values (white 0x101010, yellow 0x202000, orange 0x201000), larger black badge letters, two-pixel border, and buffered change-only refresh. Distinguished successful one-feed board measurements and desktop two-feed comparison from still-pending visual and long-run confirmation.
- The Manhattan-only minus-one-minute display offset is implemented and tested in firmware/arrival_ui.py, clamped at zero. Its attempted board write failed because CIRCUITPY was absent; the repository helper changed but the board did not. No deployment or current board-copy equality is claimed for that offset. Reconnect and copy the helper before expecting the adjustment.
- Rechecked repository Python syntax, semantic inspector tests, UI bounds/order/stale tests, Manhattan offset/clamping and visual-state behavior, local Markdown links, and git diff --check; all passed. No new live requests, hardware changes, commits, pushes, or PRs were performed in this documentation refresh.
- Lessons: missing transitive dependencies can stop display startup; low-bit-depth colors quantize at low brightness; publish complete frames rather than clearing the visible bitmap; preserve pending-deployment distinctions when the board disconnects. Next validate appearance and repeated updates, then exercise network failure/recovery and record electrical measurements.

## 2026-10-24 — E/F badges and service-alert hazards prepared

- Added E to the A/C/E request, F to the shared B/D/F/M request, and route/direction retention in the subset decoder. The next two predictions are selected across E/F/M/R per direction. Added larger black E/F badge glyphs; E is dim blue 0x000020 and F matches M at 0x201000.
- Implemented active MTA subway-alert selectors and lower-right red hazard triangles, defaulting to matching active service alerts while awaiting the trigger preference. Respect route/station/trip/direction constraints and active periods; route-wide notices are not individual-train delay claims. Alert retrieval failures do not discard arrivals; unavailable alert status uses the stale indicator.
- Four E/F/alert test methods passed; the downloaded 505,752-byte alert feed matched official decoding with two relevant selectors. Existing inspector/UI tests, syntax, links, and whitespace checks passed. No board deployment or new hardware test occurred: CIRCUITPY is absent. Alert memory cost and continuous behavior are unverified. The Manhattan offset is still pending deployment with the updated helpers.

## 2026-10-25 — Contributor and station privacy

- Replaced personal contributor names with @zyxtai throughout documentation and historical work-log entries. Generalized station names in prose, serial messages, and checkpoint headers; changed greeting examples to HELLO WORLD and renamed the greeting checkpoint accordingly.
- Moved platform selection into ignored CIRCUITPY/settings.toml using MTA_MANHATTAN_STOP and MTA_QUEENS_STOP. Added firmware/station_config.py, shared the configured IDs between decoder and renderer, retained the Manhattan-only minute adjustment, and made desktop --stops selection required. Replaced station IDs in tests with synthetic fixtures and added privacy rules to AGENTS.md.
- Validation: four feed-inspector/decoder tests, two configuration tests, display bounds/colors/order/stale/offset checks, Python syntax, local Markdown links, the privacy text/filename scan, and git diff --check passed. Installed pinned desktop test requirements in a temporary environment; no live feed requests or board execution were performed.
- Deployment remains pending: add both real platform IDs to the board's private settings and copy all three firmware helpers plus code.py. The current branch removes identifying text from current files; existing Git history and previously published copies remain unchanged.
- Lesson: station IDs disclose the same location as station names, so keep them in private configuration and use synthetic test fixtures.
- Pre-PR learn review: reviewed the final two-commit change against main, confirmed the existing validation record and pending board deployment are accurate, and reran git diff --check main...HEAD successfully.

## 2026-10-25 — PR #6 merge resolution and learn review

- Merged the latest main into next-part-from-phase-4, resolving conflicts in README, the application, renderer, integration guide, and this log. Preserved E/F/M/R feeds, badge colors, direction-aware alert hazards, buffered rendering, and the Manhattan display offset while retaining main's contributor anonymization and private station configuration.
- Removed station identifiers introduced by the feature branch from tracked code, tests, and prose. Alert filtering and badge matching now use the configured platforms plus optional private MTA_PARENT_STOP for station-wide selectors; no parent ID is inferred. Kept both branches' work-log history and updated the decoder expectation for retained direction metadata.
- Applied the repository-owned learn workflow. Four E/F/alert tests, four inspector/decoder tests, two station-configuration tests, pixel-bound/order/stale/offset checks, optional parent-alert matching, Python syntax, local Markdown links, privacy/conflict-marker scans, and git diff --check passed. No board deployment or new hardware validation was performed.
- Lesson: merging feature work with privacy changes requires adapting new alert and test code to configuration, rather than choosing one side wholesale. The service-alert trigger is confirmed as an active MTA alert affecting the route or station.

## 2026-10-25 — Deployed E/F update and verified board predictions

- Diagnosed missing E/F display support as deployment drift: CIRCUITPY still contained the older M/R-only program and helpers. Copied the current program and station_config, mta_minimal, mta_alerts, and arrival_ui helpers; migrated existing board platform selection into private settings without printing or changing Wi-Fi credentials. Verified deployed files byte-for-byte.
- Restarted the actual board with serial capture: Wi-Fi/NTP succeeded and all three arrival feeds downloaded (64,149 bytes R, 59,231 bytes F/M, 53,473 bytes E). Confirmed upcoming E/F predictions for both configured directions. Combined update took about 11.23 seconds and post-cleanup free heap was 1,902,256 bytes in this run.
- Service-alert retrieval reported a stale feed; valid arrivals were retained as designed, and hazard status remains unavailable until a fresh alert snapshot is accepted. Do not treat missing hazard triangles as an all-clear. Physical appearance still requires confirmation. The pending Manhattan display adjustment was included in the deployed helper.

## 2026-10-25 — Remove service alerts and buffer both directions

- Removed active service-alert fetching, cache state, and route hazard triangles from the application/renderer. Retained arrival-data stale indicators and E/F/M/R fetching. The old alert decoder source is unused and not required by the deployed application.
- Changed the display offset from Manhattan-only to minus one minute for both directions, clamped at zero; 7 becomes 6 and 1 becomes 0. Original feed timestamps and passed-train filtering remain unchanged.
- Deployed code.py and arrival_ui.py and verified byte equality. Updated offset expectations and retained route/color/bounds/stale checks; UI and route tests, syntax, and whitespace checks passed. Physical appearance remains to be confirmed; credentials were not modified.

## 2026-10-25 — Full synchronized direction scrolling

- Replaced abbreviated direction labels with clipped MANHATTAN/FOREST HILLS scrolling at 10 pixels per second, sharing a monotonic phase and common wrap period. Kept badges/minutes fixed, the left two-pixel border, and three clear columns before the first badge. Moved stale indicators below labels to preserve the gap.
- Set M and F to the same stronger dim orange 0x402000 and retained dim white text. Saved program/helper to the board and repository, verifying byte equality.
- Full-cycle tests passed for bounds, label margins, fixed badge/minute geometry, shared phase, wrap, stale placement, and palette consistency. Existing UI/routes tests, Python syntax, and git diff --check passed. Animation can pause during synchronous network/parsing operations; physical appearance and smoothness remain to be confirmed.

## 2026-10-25 — Shorter scrolling repeat interval

- Changed the scrolling repeat distance to the longer label width plus eight pixels and draw the following copy while the previous one exits. Both rows retain identical leading-letter positions, speed, clipping, and fixed badge/minute geometry. The shorter label has a slightly larger gap to maintain synchronization.
- Updated and passed full-cycle geometry/margin/wrap tests and deployed the helper, triggering board reload.

## 2026-10-26 — Independent feed recovery, reboots, and dimming

- Replaced the all-feeds-or-nothing update with independent timestamped caches and per-feed retries. One failed/expired feed no longer hides fresh predictions from healthy routes. Added managed-socket cleanup on errors and retained the synchronized clock when a later NTP retry fails.
- Added runtime_policy.py for New York DST-aware daily 05:00–08:30 normal brightness, quarter-brightness otherwise, a 90-minute runtime reset, and an additional 04:59 reset. A boot during that minute suppresses a reboot loop. Added a hardware watchdog for stalled calls and scheduled deadlines. Increased color depth to 6 so low off-hours channel values remain representable.
- Hardware startup verification found and corrected ESP32 watchdog reconfiguration errors and CircuitPython's unsupported two-argument next() call. Serial then confirmed very-dim mode, successful NTP, and a fresh R-feed update. Further feed cycles and actual scheduled reset events require observation; powered operation and successful clock synchronization are prerequisites for daily wall-clock scheduling.
- Four runtime-policy test methods passed, covering feed-failure isolation/expiry, New York DST boundary comparisons, rush-hour limits, daily reboot timing helpers, and palette scaling. Existing scroll/layout/offset/route tests, syntax, and deployed-file equality passed. Updated old palette expectations to current M/F 0x602000. No credentials or station selection were changed.

- Extended serial observation also confirmed an independent F/M update (175,811 bytes, 13-second feed age) while R continued refreshing. Select the oldest-due feed to avoid route starvation when a request is slow. Scheduled reboot times and final low-brightness appearance remain unverified on hardware.

## 2026-10-26 — Hourly Nyan Cat and brighter text

- Added an independent transparent top-layer Nyan Cat sprite/rainbow loop, moving right-to-left during the first minute of each non-rush New York clock hour. The normal direction text and arrival layer continue underneath and reappear behind the passing sprite; rush-hour suppression and clock-sync gating prevent unintended playback.
- Increased off-hours white labels/minutes to 0x101010 while retaining route dimming and the brighter off-hours R override. Added nyan_overlay.py to the required helpers and deployed the code, runtime policy, and overlay source.
- Hour-window/rush exclusion, minute-end suppression, full-loop clipping/repetition, transparent clearing, and white/R palette checks passed, along with runtime/scroll/UI tests, Python syntax, deployed-copy equality, and git diff --check. The actual next-hour playback and perceived text color still require hardware observation.

## 2026-10-26 — Fragmentation diagnosis, persistent incidents, and larger Nyan Cat

- Captured the recurrence before restarting: F/M failed with MemoryError allocating 154,340 contiguous bytes. Replaced growing bytearray downloads with one persistent 256 KiB buffer and memoryview decoding to avoid repeated large growth allocations; kept independent freshness and retry policy.
- @zyxtai selected persistent board-memory logs with export during debugging, preserving normal USB editing. Added a bounded NVM incident ring for feed failures, empty-display transitions, and watchdog recovery, plus a Mac exporter that creates per-incident JSON files in CIRCUITPY/logs and restarts the app. Explicitly documented that files appear at export time rather than on failure. No credentials or station IDs are written to records.
- Enlarged the cat 2× and implemented first-pass rainbow accumulation, retained middle-pass rainbow, and final-pass right-to-left removal. Existing content stays in the underlying layer, and the full overlay clears at minute end.
- NVM retention/wrap/truncation/duplicate-throttle/unknown-data tests and cat schedule/full-minute clipping/trail-clear tests passed, as did runtime, scroll, UI, and syntax checks. Deployed helper/program copies match the repository. Serial confirmed a fresh R update after the buffer change; longer-run fragmentation recovery and final animation appearance require observation.

- Actual board verification also completed a fresh F/M update (169,517 bytes, 24-second age) with about 1.60 MB free. Tested the exporter against real NVM: two incident files were written to CIRCUITPY/logs and the application restarted. Suppressed the initial empty-cache transition so startup does not consume incident slots intended for later disappearances.

## 2026-10-27 — Four arrivals, brighter E, overnight sleep

- Added four nearest trains per direction with unchanged circle diameter, smaller minute digits, and a narrower synchronized label viewport. Preserved the two-pixel outer border and three-pixel label-to-circle gap; ++ caps times over 99 minutes. Increased E blue slightly in normal and off-hours palettes.
- Added overnight blanking/controller deep sleep at 20:30 and a 04:59 New York wake alarm, including overnight DST transitions. Disable watchdog and release the matrix driver before sleep; maintain the panel supply rather than claiming a physical power cutoff. USB-host connections may simulate sleep per CircuitPython behavior. Clock sync is a prerequisite.
- Saved/deployed code.py and both modified helpers with byte equality. Four-slot/long-time/clipping tests, DST-aware wake and sleep-boundary tests, existing UI/scroll/runtime/route tests, syntax and whitespace checks passed. Actual scheduled hardware sleep/wake and final readability remain unverified.

## 2026-10-27 — Restore two-slot layout with flipping pages

- Restored wider scrolling labels, original two circle positions, and large minute digits. Alternate the first and next pair of predictions on a shared four-second page clock; apply a short vertical squash/expand flip only to train areas. Fewer than three predictions repeat instead of producing an empty second page.
- Deployed renderer and program with byte equality. Page selection/timing, squeeze bounds, label gap, scroll, overnight boundary/DST, and syntax/whitespace checks passed. Physical flip smoothness remains unverified; synchronous network/parsing calls can pause animation briefly. Sleep, brightness, diagnostics, and cat behavior are preserved.

## 2026-10-27 — Slower, clearer page flip

- Changed synchronized arrival page intervals to six seconds and expanded the vertical collapse/expand transition to 1.6 seconds with multiple intermediate heights. Direction scrolling and train positions remain unchanged. Saved/deployed the renderer and reloaded the board.
- Updated and passed two-cycle page/flip geometry tests; Python syntax and whitespace checks passed. Physical animation smoothness still needs visual confirmation.

## 2026-10-27 — Morning-only operation

- Changed the awake window to 04:59–08:30 New York time daily and updated next-day wake calculation for the earlier shutdown. The earlier 20:30 shutdown is superseded. Preserved existing DST handling, watchdog/reboots, and display behavior.
- Updated and passed boundary and DST wake tests and deployed runtime_policy.py, then reloaded the saved program. Physical scheduled sleep/wake remains unobserved; an immediate sleep is expected when reloaded outside the morning window.

## 2026-10-28 — Morning wake reliability fallback prepared

- @zyxtai reported no 04:59 wake. Neither CIRCUITPY nor serial was present, so actual alarm firing, clock state, and prior incident records could not be inspected; the exact failure cause is unconfirmed.
- Replaced the long deep-sleep alarm path with a black-screen, Wi-Fi-off idle loop that keeps RTC and watchdog active and checks the awake window every half second. On entering the morning window, record MORNING_WAKE and hardware-reset to resume the display. Record NIGHT_IDLE on entry. This intentionally trades higher standby power for independence from overnight alarm wake behavior.
- Existing schedule/DST boundary tests, source syntax, and whitespace checks passed. Code is saved only in the repository; deployment and real overnight behavior await board reconnection. No claim is made that this revision has fixed the user's physical board yet.

## 2026-10-28 — Safe low-power deep sleep restored

- Reconciled low-power operation with the wake fix: retain 04:59–08:30 New York operation and real standalone deep sleep, but defer shutdown until the outer loop after HTTP context cleanup. Maintenance only requests sleep; the download abort path unwinds its response before global socket cleanup, driver shutdown, and the time alarm. This directly addresses the logged same-time Socket not managed error.
- Added an explicit alarm-wake incident. Overnight display scanning, Wi-Fi, and watchdog are disabled rather than continuously polling the RTC. Panel power remains connected; actual whole-sign standby draw is unmeasured.
- Two application-control-flow tests passed, including execution of the real request block with a sleep request during chunk processing, verifying response exit before sleep. Schedule/DST and runtime-policy tests passed. A temporary five-second alarm test on the USB-connected board printed SHORT_SLEEP_WAKE TimeAlarm; restored the corrected application and verified board/repository equality. This is simulated USB sleep, not proof of a full autonomous overnight wake.


## 2026-10-30 — Repeated missed morning wake

- Exported the persistent incident ring from the connected board. Overnight NIGHT_SLEEP delays targeted 04:59 correctly, and deployed code matched the deferred HTTP-cleanup revision, but no subsequent morning wake was recorded. The logs cannot distinguish an alarm failure from lost electrical power; the root cause remains unconfirmed.
- Replaced the long deep-sleep alarm with display-off, Wi-Fi-off standby using light sleeps capped at ten seconds and an active watchdog. At the morning boundary the controller records MORNING_WAKE and resets. Added boot and three-hour standby heartbeat incidents, and retained safe socket cleanup before standby. This trades some standby efficiency for repeated wake checks.
- Board serial smoke test returned successfully from a two-second light sleep with its watchdog enabled. Automated tests cover the actual standby function reaching morning/reset, HTTP cleanup ordering, schedule boundaries, and DST. A complete autonomous overnight wake remains to be observed.

- Deployment restart exposed an additional concrete startup failure: SocketPool not managed when standby runs before any HTTP request. Treat this empty-pool cleanup case as already closed so it cannot abort standby.

- Changed standby checks to once per minute at user request, retaining a shorter final interval to target 04:59 precisely. Increased only the standby watchdog to 90 seconds so a normal one-minute sleep does not trigger a reset; daytime watchdog remains unchanged.
