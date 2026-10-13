# MTA Subway Arrival Sign

A father-and-son project by Ryan and Alex to build a standalone Wi-Fi-connected NYC subway arrival sign using an Adafruit Matrix Portal S3 and two 64×32 HUB75 RGB LED panels.

The target display is 128×32 pixels. Our preferred architecture fetches and processes MTA arrival data directly on the ESP32-S3, provided memory usage and feed parsing prove practical. The firmware language, libraries, and data-handling approach are still undecided.

## Current status

The repository contains the initial project documentation. Hardware setup is starting fresh: the board's current USB, bootloader, and firmware state still need to be verified. An earlier `MATRXS3BOOT` observation is historical, not confirmation of the current state.

## Get started

1. Clone the repository and enter its directory:

   ```sh
   git clone https://github.com/zyxtai/subway-led-matrix.git
   cd subway-led-matrix
   ```

2. Open the folder in Visual Studio Code, our primary development environment. Other IDEs, such as Arduino IDE, may also be used as appropriate for the selected toolchain.
3. Read the project plan and repository instructions linked below. When using Codex, open this repository as the workspace so it can read `AGENTS.md`.
4. Use the shared [learn skill](.agents/skills/learn/SKILL.md) before preparing a PR with Codex. Project skills are version controlled under `.agents/skills/`, so they come with the checkout and do not require a separate personal installation. If the skill is not listed in the current session, ask Codex to read its repository path directly.

Firmware installation, build, and flashing instructions will be added after we choose a toolchain in Phase 1.

## Documentation

- [Project plan](docs/PROJECT_PLAN.md): goals, development phases, and project constraints.
- [Hardware inventory](docs/hardware.md): reported parts and details awaiting verification.
- [Wiring plan](docs/wiring.md): proposed power and data connections, plus required checks.
- [Decisions](docs/decisions.md): agreed choices and open questions.
- [Work log](docs/progress.md): completed work, validation, and lessons learned.
- [Repository instructions](AGENTS.md): PR workflow and Markdown formatting conventions.

## Development workflow

1. Start from an up-to-date `main` and create a branch for each change.
2. Work on one small milestone at a time and document what was actually verified.
3. Before opening any PR, including a draft, use the `learn` skill to update `docs/progress.md` and include the update in the PR branch.
4. Push the branch and open a PR targeting `zyxtai/subway-led-matrix:main`. Contributors without write access can push to their fork.
5. Review and merge through GitHub, then sync local `main` before the next change.

Keep each Markdown paragraph and list item on one source line; let the editor wrap the text. Preserve intentional line breaks in diagrams and code blocks.

## Next experiment

Connect only the Matrix Portal S3 to the Mac using a USB data cable, with LED panels and external panel power disconnected. Record whether macOS detects the board and which USB device or mounted volume appears. Do not infer the firmware state from the earlier attempt; investigate bootloader access only if needed, and document the observed result before choosing or installing firmware.

Subsequent milestones are controller bring-up, one panel, two panels, live MTA data, the arrival display, reliability, and enclosure design.
