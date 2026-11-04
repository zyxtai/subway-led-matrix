"""Exercise the safe-mode entry point without crashing physical hardware."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'firmware'))
from diagnostic_log import IncidentLog


class ResetRequested(BaseException):
    pass


class SafeModeLogTests(unittest.TestCase):
    def run_hook(self, reason, memory):
        self.trace = []
        def reset():
            self.trace.append('reset')
            raise ResetRequested()
        micro = types.SimpleNamespace(nvm=memory, watchdog=types.SimpleNamespace(mode=None), reset=reset)
        supervisor = types.SimpleNamespace(runtime=types.SimpleNamespace(safe_mode_reason=reason),
                                           SafeModeReason=types.SimpleNamespace(USER='USER', HARD_FAULT='SafeModeReason.HARD_FAULT'))
        with patch.dict(sys.modules, {'microcontroller': micro, 'supervisor': supervisor}), patch('time.sleep', side_effect=lambda seconds: self.trace.append(('sleep', seconds))):
            runpy.run_path(str(ROOT / 'docs/safemode.py'))

    def test_crash_reason_persists_alongside_previous_records(self):
        memory = bytearray(4096)
        IncidentLog(memory).record('RESET_ARMED', '90-minute runtime')
        with self.assertRaises(ResetRequested):
            self.run_hook('SafeModeReason.HARD_FAULT', memory)
        rows = IncidentLog(memory).records()
        self.assertEqual([row['event'] for row in rows], ['RESET_ARMED', 'SAFE_MODE', 'RECOVERY_REQUEST'])
        self.assertEqual(rows[-2]['detail'], 'SafeModeReason.HARD_FAULT')
        self.assertEqual(rows[-1]['seq'], 3)
        self.assertEqual(self.trace, [('sleep', 30), 'reset'])

    def test_manual_safe_mode_does_not_change_nvm(self):
        memory = bytearray(4096)
        self.run_hook('USER', memory)
        self.assertEqual(memory, bytearray(4096))

    def test_other_safe_mode_stays_available_for_inspection(self):
        memory = bytearray(4096)
        self.run_hook('SafeModeReason.PROGRAMMATIC', memory)
        self.assertEqual(self.trace, [])
        self.assertEqual([r['event'] for r in IncidentLog(memory).records()], ['SAFE_MODE'])

    def test_hard_fault_recovers_even_when_logging_is_unavailable(self):
        memory = bytearray(b'x' * 4096)
        with redirect_stdout(io.StringIO()), self.assertRaises(ResetRequested):
            self.run_hook('SafeModeReason.HARD_FAULT', memory)
        self.assertEqual(self.trace, [('sleep', 30), 'reset'])
        self.assertEqual(memory, bytearray(b'x' * 4096))

    def test_logging_failure_preserves_unknown_nvm(self):
        memory = bytearray(b'x' * 4096)
        with redirect_stdout(io.StringIO()) as output:
            self.run_hook('SafeModeReason.WATCHDOG', memory)
        self.assertEqual(memory, bytearray(b'x' * 4096))
        self.assertIn('ValueError', output.getvalue())


if __name__ == '__main__':
    unittest.main()
