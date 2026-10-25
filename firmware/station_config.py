"""Load station selection from private CircuitPython settings.toml."""
import os

MANHATTAN_STOP = os.getenv("MTA_MANHATTAN_STOP")
QUEENS_STOP = os.getenv("MTA_QUEENS_STOP")
if not MANHATTAN_STOP or not QUEENS_STOP:
    raise ValueError("Set MTA_MANHATTAN_STOP and MTA_QUEENS_STOP in settings.toml")
if MANHATTAN_STOP == QUEENS_STOP:
    raise ValueError("MTA platform IDs must be different for each direction")

STOPS = {MANHATTAN_STOP: "Manhattan-bound", QUEENS_STOP: "Forest Hills-bound"}
