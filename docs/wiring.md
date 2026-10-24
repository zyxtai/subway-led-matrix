# Wiring Plan

This document captures the proposed wiring from the [project plan](PROJECT_PLAN.md). The connections have not been verified or tested as part of the fresh setup. Confirm component documentation, voltage, polarity, and connector orientation before implementing this plan.

## First bring-up experiment

Connect only the Matrix Portal S3 to the Mac with a USB data cable. Leave LED panels and the external panel power supply disconnected. Record USB detection before installing or changing firmware. The final shared power arrangement below belongs to later milestones.

## Proposed final power distribution

The reported supply is 5 V DC, up to 10 A. Its barrel connector would feed an 18 AWG female pigtail, then separate WAGO distribution points for +5 V and GND. Both panels and the controller would receive their own parallel branches.

```text
Weishuo 5 V DC supply
          |
5.5×2.5 mm female pigtail, 18 AWG
          |
          +-- +5 V distribution --+-- panel 1 positive
          |                      +-- panel 2 positive
          |                      +-- USB-C pigtail positive
          |
          +-- GND distribution ---+-- panel 1 ground
                                 +-- panel 2 ground
                                 +-- USB-C pigtail ground

USB-C pigtail --> Matrix Portal S3 USB-C input
```

This diagram shows logical branches, not physical pin positions or verified connector polarity. Use the panel power harnesses after checking their polarity. The existing 20 AWG wire is proposed only for short panel branches, subject to conductor-material and suitability checks. Keep the 18 AWG pigtail as the main feed.

Confirm the actual WAGO variants have sufficient ports and suitable ratings for the wires and load. Verify the USB-C pigtail is appropriate for the board before relying on the shared supply arrangement. Changing between computer USB power and the proposed final USB-C power lead needs a documented procedure before hardware testing.

## Proposed HUB75 data path

```text
Matrix Portal S3 HUB75 --> panel 1 INPUT
panel 1 OUTPUT        --> panel 2 INPUT
```

Verify each panel's input/output labels and ribbon orientation before connection. Start with panel 1 alone at low brightness. Add panel 2 only after the first panel works reliably, and configure the display geometry as 128×32 when the chosen toolchain supports the arrangement. Each panel retains its own parallel power branch.

## Checks before panel power-up

These checks carry forward the project plan's wiring rules:

1. Disconnect the supply before modifying wiring.
2. Verify supply output is approximately 5 V DC with a multimeter. Never connect 12 V, 19 V, or 20 V directly to the panels.
3. Verify positive and ground at the branch outputs and panel connectors before each first power-up after rewiring. Red/black colors are intended labels, not proof of polarity.
4. Check wire and connector suitability, keep high-current runs short, and power the panels in parallel rather than routing both panels' current through one panel.
5. Power the controller through its USB-C input in the proposed final arrangement. Do not feed power into board pins or terminals documented as outputs.
6. Begin testing one panel at low brightness. If a connector or wire becomes noticeably hot, disconnect power and investigate.

## Measurement record

No measurements have been recorded for the fresh setup. Add dates, configuration, measured supply voltage, verified polarity, panel brightness, and current draw as tests are performed. Update this document whenever the electrical design changes.

## 2026-10-24 — Bring-up observations

Alex reported the single-panel color test worked and subsequently reported both panels attached for a 128×32 test. The [saved script](code.py) targets this geometry. The dual-panel visual result and actual input/output orientation still need confirmation. These observations do not verify the proposed WAGO distribution, USB-C pigtail, supply polarity, voltage, or current draw; no electrical measurements were provided and no wiring changes were made during this documentation update.
