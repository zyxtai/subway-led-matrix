# Project Decisions

This record separates agreed project direction from choices that still need evaluation. The [project plan](PROJECT_PLAN.md) remains the full statement of goals and milestones.

## Agreed direction

| Decision | Reason | Status |
| --- | --- | --- |
| Use the Matrix Portal S3 and two 64×32 panels | Build around the hardware already reported as owned, targeting a 128×32 display | Single-panel color test reported working; dual-panel script prepared |
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
- Begin with one station, likely Forest Hills–71 Av. Verify current station, route, feed, and stop identifiers before implementation.

## Open decisions

| Question | Evidence needed before choosing |
| --- | --- |
| Arduino/C++ or CircuitPython? | Controller bring-up requirements, display library support, available memory, and feed parsing feasibility |
| Which protobuf decoder? | GTFS-Realtime compatibility and measured memory requirements; nanopb is a candidate, not a selection |
| Which MTA feeds and identifiers? | Current official MTA documentation and observed feed contents |
| What refresh interval and brightness? | Network behavior, readability, measured current, and display testing |
| What enclosure and mounting design? | Working electronics, actual dimensions and hole spacing, ventilation, and serviceability |

When resolving an open decision, record the date, choice, rationale, and validation or remaining uncertainty. Do not install a firmware toolchain as part of Phase 0.

## 2026-10-24 — Display prototype runtime

Use the existing CircuitPython 10.3.1 installation for incremental display and Wi-Fi experiments. Preserve the 128×32 HELLO ALEX checkpoint in [code.py](code.py). This is a prototype choice, not a final decision that direct GTFS-Realtime parsing is feasible: measure memory and decoding performance before committing to CircuitPython or switching to Arduino/C++. No feed decoder or live endpoint has been selected or tested.
