# Hardware Inventory

This inventory records the parts and specifications reported in the [project plan](PROJECT_PLAN.md). It is not a record of physical inspection, electrical measurements, or successful hardware tests.

## Controller and display

| Item | Quantity | Reported details | Status |
| --- | --- | --- | --- |
| Adafruit Matrix Portal S3, product #5778 | 1 | ESP32-S3, Wi-Fi, 8 MB flash, 2 MB PSRAM, HUB75 interface, USB-C; supports Arduino and CircuitPython | Identified from boot_out.txt as MatrixPortal S3 running CircuitPython 10.3.1; Wi-Fi untested |
| Adafruit RGB LED matrix, product #2279 | 2 | 64×32 pixels, 3 mm pitch, HUB75 interface, M3 mounting points | Single-panel color test reported working; both panels attached per Alex; 128×32 visual result pending |

Two panels are intended to sit side-by-side for a combined 128×32 display. The project plan estimates an LED area of approximately 38.2×9.6 cm; measure the actual panels and mounting-hole spacing before designing the enclosure.

HUB75 ribbon cables and red/black panel power harnesses were reported as included with the panels. USB-C cables and general maker tools are also available.

## Power and distribution

| Item | Reported details | Status |
| --- | --- | --- |
| Weishuo AC/DC adapter | 100–240 V AC input; 5 V DC, up to 10 A / 50 W output; 5.5×2.5 mm barrel connector | Owned; output voltage and polarity still need measurement |
| Female DC pigtail | 5.5×2.5 mm barrel socket; 18 AWG; bare-wire output | Owned or ordered; receipt and connector fit need confirmation |
| WAGO 221 lever connectors | Separate distribution points for +5 V and GND | Owned or ordered; exact variants, port counts, and applicable ratings need confirmation |
| USB-C male to bare-wire pigtail | 22 AWG; reported 5 V, up to 3 A; red/black wires | Owned or ordered; receipt, polarity, and suitability for powering this board need confirmation |
| Red/black parallel wire | 20 AWG | Available; conductor material and suitability for short panel branches need verification |

The intended finished sign uses one power adapter for both panels and the controller. This is a proposed arrangement, not a tested power system; see the [wiring plan](wiring.md).

## Assembly and measurement tools

- Multimeter for voltage and polarity checks.
- Wire stripper, wire cutter, and small screwdrivers.
- M3 screws and standoffs as needed after measuring the mounting geometry.

## Verification still required

- Confirm which ordered distribution parts have arrived and inspect their labels and connector fit.
- Current runtime identification is recorded above; bootloader recovery was not retested and Wi-Fi remains unverified.
- Verify connector polarity and supply voltage before energizing any new wiring.
- Confirm the existing 20 AWG wire's conductor material; the project plan prefers copper over CCA.
- Confirm the dual-panel text result, panel order, and orientation, then measure current at the intended brightness. The single-panel color test was reported successful.
- Measure panel and mounting geometry before adapting brackets or enclosure files.
