"""Check private station configuration without requiring board hardware."""
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

CONFIG = Path(__file__).resolve().parents[1] / "firmware/station_config.py"


class StationConfigTests(unittest.TestCase):
    def load(self, values):
        with patch.dict(os.environ, values, clear=True):
            return runpy.run_path(str(CONFIG))

    def test_private_platform_selection(self):
        config = self.load({"MTA_MANHATTAN_STOP": "TEST_INBOUND", "MTA_QUEENS_STOP": "TEST_OUTBOUND"})
        self.assertEqual(config["STOPS"], {"TEST_INBOUND": "Manhattan-bound", "TEST_OUTBOUND": "Forest Hills-bound"})

    def test_missing_empty_or_duplicate_platforms(self):
        for values in ({}, {"MTA_MANHATTAN_STOP": "TEST_INBOUND"},
                       {"MTA_MANHATTAN_STOP": "", "MTA_QUEENS_STOP": "TEST_OUTBOUND"},
                       {"MTA_MANHATTAN_STOP": "SAME", "MTA_QUEENS_STOP": "SAME"}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.load(values)


if __name__ == "__main__":
    unittest.main()
