"""Test the temporary hourly schedule and its return to morning operation."""
import calendar
import datetime
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'firmware'))
import runtime_policy as policy


class HourlyScheduleTests(unittest.TestCase):
    def test_all_hour_boundaries(self):
        for hour in range(24):
            for minute, second, asleep in ((0, 0, False), (9, 59, False), (10, 0, True), (59, 59, True)):
                local = (2026, 10, 31, hour, minute, second)
                self.assertEqual(policy.overnight(local), asleep, local)
                self.assertFalse(policy.reboot_minute(local))
                self.assertEqual(policy.daily_remaining(local), 0)

    def test_wake_and_final_seconds(self):
        zone = ZoneInfo('America/New_York')
        for hour in range(23):
            for minute, second in ((10, 0), (35, 20), (59, 57)):
                now = datetime.datetime(2026, 10, 31, hour, minute, second, tzinfo=zone).timestamp()
                target = datetime.datetime(2026, 10, 31, hour + 1, tzinfo=zone).timestamp()
                with patch.object(policy.time, 'localtime', side_effect=time.gmtime), patch.object(policy.time, 'mktime', side_effect=calendar.timegm):
                    self.assertEqual(policy.wake_delay(now), target-now)
                    self.assertEqual(policy.standby_interval(now), min(60, target-now))

    def test_expiry_across_fall_dst(self):
        zone = ZoneInfo('America/New_York')
        now = datetime.datetime(2026, 10, 31, 23, 10, tzinfo=zone).timestamp()
        target = datetime.datetime(2026, 11, 1, 4, 59, tzinfo=zone).timestamp()
        with patch.object(policy.time, 'localtime', side_effect=time.gmtime), patch.object(policy.time, 'mktime', side_effect=calendar.timegm):
            self.assertEqual(policy.wake_delay(now), target-now)
        for hour, minute, asleep in ((0, 0, True), (4, 58, True), (4, 59, False), (8, 29, False), (8, 30, True), (12, 0, True)):
            local = (2026, 11, 1, hour, minute, 0)
            self.assertFalse(policy.hourly_test(local))
            self.assertEqual(policy.overnight(local), asleep)
        self.assertTrue(policy.reboot_minute((2026, 11, 1, 4, 59, 0)))


if __name__ == '__main__':
    unittest.main()
