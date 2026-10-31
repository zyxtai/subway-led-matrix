# MTA Subway Arrival Sign

A father-and-son project by @zyxtai to build a standalone Wi-Fi-connected NYC subway arrival sign using an Adafruit Matrix Portal S3 and two 64×32 HUB75 RGB LED panels.

The sign uses a MatrixPortal S3 running CircuitPython 10.3.1 and two chained panels forming a 128×32 display. It fetches MTA feeds directly over Wi-Fi without a proxy server.

## Current status

Wi-Fi, NTP clock synchronization, and direct on-board R-feed retrieval/decoding have been verified through serial output. The current [program](docs/code.py) displays the next two E/F/M/R predictions for each direction at the selected station: MNTN and FRST HLS. It uses large dim labels, colored route circles with black letters, and a two-pixel outer border. Buffered, change-only updates address visible bitmap clearing. Current appearance, flicker reduction, and sustained M/R refresh behavior still need confirmation; [progress](docs/progress.md) separates completed tests from pending checks.

E/F support is deployed. Service-alert fetching and hazard triangles have been removed at @zyxtai's request. The repository now includes a both-direction display adjustment of minus one minute, clamped at zero. It has not been copied to the board because CIRCUITPY was disconnected during the attempted deployment. The underlying MTA timestamps are unchanged. Station selection comes from private settings.toml; that configuration change also awaits deployment.

## Get started

1. Clone the repository and enter its directory:

   ```sh
   git clone https://github.com/zyxtai/subway-led-matrix.git
   cd subway-led-matrix
   ```

2. Open the folder in Visual Studio Code, our primary development environment. Other IDEs, such as Arduino IDE, may also be used as appropriate for the selected toolchain.
3. Read the project plan and repository instructions linked below. When using Codex, open this repository as the workspace so it can read `AGENTS.md`.
4. Use the shared [learn skill](.agents/skills/learn/SKILL.md) before preparing a PR with Codex. Project skills are version controlled under `.agents/skills/`, so they come with the checkout and do not require a separate personal installation. If the skill is not listed in the current session, ask Codex to read its repository path directly.

See the [subway integration guide](docs/subway-integration.md) for dependencies, deployment, tests, serial troubleshooting, and display behavior. Copy all required firmware helpers as well as code.py; copying code.py alone is insufficient. Save credentials and station selection only in CIRCUITPY/settings.toml, which is excluded from Git.

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

Reconnect CIRCUITPY, add the private platform settings, and deploy all current firmware helpers plus code.py to apply station configuration and the Manhattan time adjustment. Confirm both panel rows, badge colors, brightness, two-pixel border, and flicker reduction. Then observe several M/R refresh cycles and test network failure/recovery before adding more features. No new electrical measurements or final power-distribution validation have been recorded.

## Checkpoints and data tools

Earlier greeting, Wi-Fi/NTP, serial-arrival, and R-only programs are preserved under firmware/checkpoints. The board entry point is docs/code.py; the display application is firmware/sign_app.py with helpers under firmware/. The Mac inspector in tools/ is a debugging aid, not a required server. See [the integration guide](docs/subway-integration.md) for reproduction commands.

## Recovery and brightness schedule

The current program updates feeds independently, reboots every 90 minutes and at 04:59 New York time, and uses normal brightness only from 05:00 to 08:30 daily. Other times use one-quarter brightness. Deploy firmware/runtime_policy.py to CIRCUITPY/lib with the other current helpers. Daily scheduling requires a synchronized clock; see the integration guide for watchdog behavior and verification limits.


## Morning startup diagnostics

The startup launcher records display setup, the first submitted frame, Wi-Fi, clock synchronization, first feed updates, and the first submitted frame containing arrivals. Unhandled application errors record the last checkpoint and exception type. These records help distinguish a controller restart from successful display recovery; the physical overnight result still needs observation. See the integration guide for deployment and diagnostic limitations.


## Temporary hourly wake test — October 31

On October 31, 2026 only, the sign is awake from minute 00 inclusive to minute 10 exclusive of each New York hour, then enters display-off standby until the next hour. This repeats the standby/reset/startup path for observation. Startup and feed loading take a few seconds after the boundary. At local midnight the test expires automatically; the next awake window is November 1 at 04:59, accounting for the daylight-saving change. Keep continuous power connected. The startup diagnostic checkpoints remain active.
