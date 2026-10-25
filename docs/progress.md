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
