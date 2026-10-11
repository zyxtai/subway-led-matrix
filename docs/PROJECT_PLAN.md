# MTA Subway Arrival Sign --- Project Plan

## Project Overview

We are building a DIY New York City MTA subway real-time arrival sign as a father-and-son project.

The goal is to build a standalone Wi-Fi-connected LED display that resembles a real MTA subway arrival board. It should retrieve live MTA subway arrival data, process the arrivals locally, and display them on two chained HUB75 RGB LED matrix panels.

**Visual Studio Code** should be the primary development environment, with **Codex** helping with implementation, command-line work, debugging, documentation, and GitHub workflow. Other IDEs, such as **Arduino IDE**, may also be used as appropriate for the selected firmware/toolchain.

We want the entire project---including source code, setup instructions, design decisions, useful prompts, progress notes, wiring documentation, and eventually enclosure files---to live in a GitHub repository so that we can work on it together and track its history.

------------------------------------------------------------------------

## Primary Goal

Build a standalone display with this architecture:

``` text
                    Internet
                       |
                       v
                MTA real-time data
                       |
                       v
             +---------------------+
             | Matrix Portal S3    |
             | ESP32-S3            |
             |                     |
             | - Wi-Fi             |
             | - Fetch MTA data    |
             | - Parse arrivals    |
             | - Select station    |
             | - Calculate ETA     |
             | - Render display    |
             +----------+----------+
                        |
                     HUB75
                        |
              +---------+---------+
              |                   |
              v                   v
        +-----------+       +-----------+
        | 64 x 32   | ----> | 64 x 32   |
        | P3 Panel  |       | P3 Panel  |
        +-----------+       +-----------+

                 Combined display:
                     128 x 32
```

The desired final system should **not require a Raspberry Pi, ODROID, local Node.js server, or cloud proxy** if we can reasonably implement the MTA data handling directly on the ESP32-S3.

------------------------------------------------------------------------

## Hardware We Already Have

### Controller

**1 × Adafruit Matrix Portal S3 --- Product #5778**

Known features:

-   ESP32-S3
-   Wi-Fi
-   8 MB Flash
-   2 MB PSRAM
-   HUB75 RGB matrix interface
-   USB-C
-   Designed specifically for RGB LED matrix projects
-   CircuitPython and Arduino support

This is the main controller for the project.

------------------------------------------------------------------------

### LED Panels

**2 × Adafruit 64×32 RGB LED Matrix --- 3 mm pitch --- Product #2279**

Each panel:

-   Resolution: 64 × 32
-   Pixel pitch: 3 mm
-   HUB75 interface
-   M3 mounting points
-   Includes HUB75 ribbon cable
-   Includes red/black panel power harness

The two panels will be mounted side-by-side:

``` text
+-------------------+-------------------+
|                   |                   |
|      64 x 32      |      64 x 32      |
|                   |                   |
+-------------------+-------------------+

             128 x 32 pixels
```

Approximate finished LED area:

-   Width: \~38.2 cm
-   Height: \~9.6 cm

------------------------------------------------------------------------

## Power Supply

**1 × Weishuo AC/DC adapter**

Specifications:

-   Input: 100--240V AC
-   Output: **5V DC**
-   Maximum current: **10A**
-   Maximum power: **50W**
-   Barrel connector: **5.5 × 2.5 mm**

This single PSU is intended to power:

1.  LED panel #1
2.  LED panel #2
3.  Matrix Portal S3

We want the finished sign to require only **one AC power adapter**.

------------------------------------------------------------------------

## Power Distribution Parts

We also have / have ordered:

### Main PSU input

**5.5 × 2.5 mm female DC pigtail**

-   18 AWG
-   Connects to the Weishuo PSU barrel plug
-   Provides bare +5V and GND wires for distribution

### Distribution

**WAGO 221 lever connectors**

These will be used to create separate +5V and GND distribution points.

Conceptually:

``` text
                 Weishuo 5V / 10A
                         |
                5.5x2.5 mm barrel
                         |
                 18 AWG pigtail
                         |
                  +------+------+
                  |             |
               +5V WAGO      GND WAGO
                / | \          / | \
               /  |  \        /  |  \
              P1  P2  S3     P1  P2  S3
```

### Matrix Portal S3 power lead

**USB-C male → bare wire pigtail**

Specifications:

-   22 AWG
-   5V
-   Rated up to 3A
-   USB-C male
-   Red/black bare-wire input

This allows the Matrix Portal S3 to receive 5V through its normal USB-C power input while sharing the same main PSU as the LED panels.

### Additional wire available

We already have **20 AWG red/black parallel wire** at home.

Use this only for short branch runs such as:

-   WAGO → Panel #1
-   WAGO → Panel #2

The 18 AWG PSU pigtail should remain the main high-current feed into the distribution point.

Before relying on the existing 20 AWG wire for final construction, verify its conductor material if possible. Prefer copper over CCA.

------------------------------------------------------------------------

## Other Hardware Already Included

We have:

-   HUB75 ribbon cables
-   LED panel power harnesses
-   USB-C cables
-   M3 mounting holes on the LED panels
-   General electronics / maker tools

Useful tools for assembly and testing include:

-   Multimeter
-   Wire stripper
-   Wire cutter
-   Small screwdrivers
-   M3 hardware as needed later

------------------------------------------------------------------------

## Current Firmware / Setup Status

We are starting the Matrix Portal S3 setup from the beginning. Connect the board to a Mac and verify its current USB, bootloader, and firmware state as part of the new bring-up workflow.

During an earlier attempt, the board appeared as `MATRXS3BOOT` on macOS. Treat this as a historical observation, not confirmation of its current state.

First establish the GitHub repository and use Visual Studio Code + Codex as the primary development environment, with other IDEs available as needed. Choose and install the firmware/toolchain during Phase 1 after evaluating the requirements.

Do not assume the board's current bootloader or firmware state until it is verified.

------------------------------------------------------------------------

## Reference Project

A useful reference implementation is:

`harrisonlingren/mta-led-sign`

It uses a Matrix Portal M4 and a separate Node.js/Express server that parses MTA data and provides simplified data to the display.

We do **not** want to blindly copy its architecture.

Our hardware is significantly more capable:

**Matrix Portal S3 / ESP32-S3 with 2 MB PSRAM**

Our preferred architecture is to investigate whether the S3 can directly:

1.  Connect to Wi-Fi
2.  Fetch the relevant MTA GTFS-Realtime feed
3.  Decode the protobuf data
4.  Filter only the station/routes we care about
5.  Calculate upcoming arrival times
6.  Render the result directly to the 128×32 LED display

Potential implementation approaches include Arduino/C++ and a memory-efficient protobuf decoder such as nanopb.

CircuitPython may also be evaluated, but do not assume it is the best solution until memory usage and GTFS-Realtime parsing requirements are understood.

------------------------------------------------------------------------

# Development Plan

## Phase 0 --- Repository and Development Environment

Before working on the LED hardware:

1.  Create a GitHub repository.
2.  Open it in Visual Studio Code as the primary development environment; use other IDEs, such as Arduino IDE, as needed.
3.  Configure Codex for the repository.
4.  Add this document as project context.
5.  Create a useful README.
6.  Establish a simple project structure.
7.  Document all setup steps so another person can reproduce the project.

Suggested repository structure:

``` text
mta-arrival-sign/
|
+-- README.md
+-- docs/
|   +-- PROJECT_PLAN.md
|   +-- hardware.md
|   +-- wiring.md
|   +-- progress.md
|   +-- decisions.md
|
+-- firmware/
|
+-- tools/
|
+-- enclosure/
|
+-- reference/
|
+-- .gitignore
```

Do not over-engineer the structure before we know which firmware/toolchain we will use.

------------------------------------------------------------------------

## Phase 1 --- Matrix Portal S3 Bring-Up

Goal:

Confirm that the Matrix Portal S3 development environment works independently of the LED panels.

Tasks:

-   Decide on CircuitPython vs Arduino/C++ after evaluating requirements.
-   Install the selected firmware/toolchain.
-   Confirm serial output.
-   Run a minimal program.
-   Confirm Wi-Fi functionality.
-   Document every required installation step.

------------------------------------------------------------------------

## Phase 2 --- Single LED Panel

Use only **one 64×32 panel** initially.

Goal:

``` text
+----------------------+
|                      |
|      HELLO ALEX      |
|                      |
+----------------------+
```

Tasks:

-   Connect one HUB75 panel.
-   Verify HUB75 input/output orientation.
-   Connect external 5V panel power.
-   Start at low brightness.
-   Display a test pattern.
-   Display text.
-   Verify color order and panel geometry.

Do not connect the second panel until this works reliably.

------------------------------------------------------------------------

## Phase 3 --- Dual Panel / 128×32

Chain the two panels horizontally.

Target geometry:

``` text
64x32 + 64x32 = 128x32
```

Tasks:

-   Daisy-chain HUB75 data.
-   Power each panel in parallel from the distribution system.
-   Configure the framebuffer as 128×32.
-   Verify panel order and orientation.
-   Display text spanning both panels.
-   Measure current draw at realistic brightness.

------------------------------------------------------------------------

## Phase 4 --- Wi-Fi and MTA Data

Goal:

Retrieve actual NYC subway arrival information.

Tasks:

-   Identify the current official MTA GTFS-Realtime endpoint(s).
-   Understand the protobuf schema.
-   Determine the exact stop IDs and route IDs required.
-   Implement memory-efficient feed retrieval and parsing.
-   Keep only relevant arrival records.
-   Sort arrivals.
-   Convert timestamps into minutes-to-arrival.
-   Handle network failures gracefully.
-   Refresh periodically without blocking display updates.

Initially focus on a single known station before adding configuration.

The intended first station is likely:

**Forest Hills--71 Av**

Relevant services may include:

**E / F / M / R**

However, verify current MTA route/feed/stop identifiers rather than hard-coding assumptions.

------------------------------------------------------------------------

## Phase 5 --- MTA-Style User Interface

Once live arrivals work, create a display inspired by an MTA arrival board.

Possible row format:

``` text
E   World Trade Ctr        2 min
F   Coney Island           5 min
R   Bay Ridge              8 min
E   World Trade Ctr       11 min
```

Exact destinations, routes, colors, typography, spacing, and scrolling behavior should come from actual data and design testing.

Priorities:

-   Readability
-   Accurate route colors
-   Smooth updates
-   No distracting flicker
-   Appropriate brightness indoors
-   Useful information at a glance

------------------------------------------------------------------------

## Phase 6 --- Reliability

Add:

-   Wi-Fi reconnect
-   HTTP retry/backoff
-   Feed timeout handling
-   Clock/time synchronization
-   Graceful stale-data indication
-   Watchdog/recovery behavior if appropriate
-   Configuration mechanism
-   Logging/debug mode

The sign should eventually be capable of:

``` text
Power on
   |
Connect Wi-Fi
   |
Sync time
   |
Fetch MTA data
   |
Display arrivals
   |
Continue indefinitely
```

without requiring a computer.

------------------------------------------------------------------------

## Phase 7 --- Mechanical Design

Only design the final enclosure after the electronics work.

The enclosure should accommodate:

-   2 × Adafruit #2279
-   Matrix Portal S3
-   Power distribution
-   Wiring
-   DC power input
-   Ventilation
-   Serviceability

The two panels use **M3 mounting holes**.

Possible construction:

-   3D-printed joining brackets
-   3D-printed rear enclosure
-   M3 screws/standoffs
-   Optional front diffuser / smoked acrylic
-   Wall-mount or desktop mounting options

A MakerWorld HUB75 joining bracket was considered, but it was designed for a different P2.5 panel. Do not assume its mounting-hole spacing matches the Adafruit #2279. Measure the actual panels before adapting or printing brackets.

------------------------------------------------------------------------

# Electrical Safety / Wiring Rules

This project uses a high-current **5V** supply.

Observe the following rules:

1.  **Never connect 12V, 19V, or 20V directly to the HUB75 panels.**
2.  The panels require approximately **5V**.
3.  Red is intended to be +5V and black GND, but verify wiring rather than relying solely on color.
4.  Before connecting a panel, use a multimeter to verify approximately:

``` text
+5V to GND ≈ 5.0V
```

5.  Verify polarity before every first power-up after rewiring.
6.  Power the two panels in parallel, not by passing all power through one panel.
7.  Keep high-current 5V wiring short.
8.  Use appropriate wire gauge.
9.  Begin testing at low LED brightness.
10. Do not modify wiring while the PSU is energized.
11. Do not back-power the Matrix Portal S3 through pins/terminals that are documented as outputs.
12. Power the Matrix Portal S3 through its USB-C input in the planned final power architecture.
13. If any connector or wire becomes noticeably hot, disconnect power and investigate.

------------------------------------------------------------------------

# Important Engineering Principle

Work incrementally.

Do **not** jump directly from an empty repository to a complete MTA arrival sign.

Every phase should leave behind a known-good milestone.

Preferred progression:

``` text
S3 boots
   ↓
serial works
   ↓
Wi-Fi works
   ↓
one panel works
   ↓
two panels work
   ↓
128×32 rendering works
   ↓
MTA feed downloads
   ↓
protobuf parses
   ↓
one station works
   ↓
arrival UI works
   ↓
reliability
   ↓
enclosure
```

When something fails, debug only the smallest relevant subsystem.

------------------------------------------------------------------------

# Instructions for Codex

Act as the engineering partner for this repository.

Please follow these rules:

1.  **Work incrementally.** Do not implement the entire project in one large change.

2.  **Inspect the repository before making changes.** Understand what currently exists.

3.  **Use the command line when useful.** Build, flash, test, inspect logs, and run tooling directly when appropriate.

4.  **Keep the repository reproducible.** A fresh checkout should have clear setup instructions.

5.  **Document important decisions.** If we choose Arduino instead of CircuitPython, or nanopb instead of another protobuf implementation, record why.

6.  **Do not assume unverified hardware details.** Ask for a measurement, photograph, model number, or test result when necessary.

7.  **Never guess electrical polarity or voltage.**

8.  **Prefer simple solutions.** This is a father-and-son maker project, not a production transit infrastructure system.

9.  **Preserve working milestones.** Commit meaningful checkpoints.

10. **Keep progress notes.** Update `docs/progress.md` as major milestones are completed.

11. **Keep wiring documentation current.** Update `docs/wiring.md` whenever the electrical design changes.

12. **Use GitHub as the project history.** Source code, prompts, documentation, diagrams, and relevant design files should be version controlled whenever practical.

13. **Explain commands before destructive actions.** Never erase firmware, delete files, rewrite Git history, or make destructive changes without making the consequence clear.

14. **Optimize for learning.** When appropriate, explain the reason behind an implementation so that both Ryan and Alex can understand how the system works.

15. **Verify current MTA API details.** Do not rely on old endpoint, route, or stop-ID assumptions from reference projects without checking current official MTA documentation.

------------------------------------------------------------------------

# First Task for Codex

Start with **Phase 0 only**.

1.  Inspect the current repository.
2.  Propose a minimal repository structure.
3.  Create or improve `README.md`.
4.  Preserve this project plan as `docs/PROJECT_PLAN.md`.
5.  Create initial:
    -   `docs/hardware.md`
    -   `docs/wiring.md`
    -   `docs/progress.md`
    -   `docs/decisions.md`
6.  Record the known hardware listed above.
7.  Record that setup is starting fresh and the Matrix Portal S3's current bootloader and firmware state still need to be verified during Phase 1.
8.  Do **not** choose or install the firmware toolchain yet.
9.  After Phase 0 is clean, propose the smallest next experiment for Phase 1.

The immediate objective is to establish a clean, shareable, well-documented GitHub project before continuing hardware bring-up.
