# Project Decisions

This record separates agreed project direction from choices that still need evaluation. The [project plan](PROJECT_PLAN.md) remains the full statement of goals and milestones.

## Agreed direction

| Decision | Reason | Status |
| --- | --- | --- |
| Use the Matrix Portal S3 and two 64×32 panels | Build around the hardware already reported as owned, targeting a 128×32 display | Two panels attached; M/R layout implemented, final visual/reliability checks pending |
| Use Visual Studio Code as the primary environment, allowing other IDEs | Keep a shared repository workflow while allowing tools such as Arduino IDE where useful | Agreed |
| Keep project artifacts and history in GitHub | Allow Ryan and Alex to collaborate and review changes | Established; PR #1 merged |
| Update the work log with `learn` before every PR | Preserve changes, validation, decisions, and useful lessons alongside the code | Required by `AGENTS.md`; shared skill in `.agents/skills/learn/` |
| Version control project-specific Codex skills | Give Ryan and Alex the same workflow with every checkout | Repository copies under `.agents/skills/` are the source of truth |
| Use natural Markdown wrapping | Avoid hard line breaks in paragraphs and list items | Required by `AGENTS.md` |
| Verify hardware state from observations | Earlier bootloader observations are historical | CircuitPython 10.3.1 identified; single-panel color test reported working |
| Work incrementally | Keep each milestone small enough to test and debug independently | Controller, one panel, two panels, data, UI, reliability, then enclosure |

## Preferred designs awaiting validation

- Fetch and parse MTA GTFS-Realtime data directly on the ESP32-S3, avoiding a separate server or proxy if practical. Validate memory usage and parsing before committing to this architecture.
- Use one 5 V supply for both panels and the controller, with parallel panel power and controller power through USB-C. Verify the supply, distribution components, and wiring before construction.
- Begin with 63 Dr–Rego Park in both directions, confirmed by Alex on October 24, 2026. Official static GTFS identifies G10N/G10S; verify current route operation and destination labels against live data.

## Open decisions

| Question | Evidence needed before choosing |
| --- | --- |
| Arduino/C++ or CircuitPython? | Controller bring-up requirements, display library support, available memory, and feed parsing feasibility |
| Which protobuf decoder? | GTFS-Realtime compatibility and measured memory requirements; nanopb is a candidate, not a selection |
| Which MTA feeds and identifiers? | Current official MTA documentation and observed feed contents |
| What refresh interval and brightness? | Network behavior, readability, measured current, and display testing |
| What enclosure and mounting design? | Working electronics, actual dimensions and hole spacing, ventilation, and serviceability |

When resolving an open decision, record the date, choice, rationale, and validation or remaining uncertainty. Do not install a firmware toolchain as part of Phase 0.

## 2026-10-24 — Current prototype decisions

Continue with CircuitPython 10.3.1 for the standalone prototype. Direct R-feed HTTPS/decoding succeeded on the S3 with substantial free heap; the current bounded decoder in firmware/mta_minimal.py supports M/R. Official desktop decoding matched both feed samples. Keep Arduino/C++ as an option if sustained performance or broader feed requirements exceed the prototype's limits; a rewrite is not currently required by the observed one-feed test.

Use 63 Dr–Rego Park, both directions, with M and R predictions sorted together. MNTN and FRST HLS are direction labels, not decoded terminal destinations. Use a two-pixel outer border, larger black route letters, dim route colors, and buffered change-only publishing. Record brightness as actual palette values in the integration guide. Apply Alex's one-minute subtraction only to displayed Manhattan times, clamped at zero; do not alter source predictions. That last helper change is pending deployment after disconnection.

Use the [integration guide](subway-integration.md) for current configuration and limitations. Earlier greeting/Wi-Fi/NTP checkpoints are preserved under firmware/checkpoints. Sustained two-feed refresh, failure recovery, panel appearance, and final power measurements remain open validation tasks.
