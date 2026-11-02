"""Check runtime progress and actual scheduled-reset control flow."""
import ast
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'firmware'))
from diagnostic_log import IncidentLog, StartupDiagnostics
import runtime_policy


class ResetRequested(Exception):
    pass


class RuntimeDiagnosticsTests(unittest.TestCase):
    def test_monotonic_heartbeat_interval_and_retained_details(self):
        log = IncidentLog(bytearray(4096))
        diagnostics = StartupDiagnostics(log)
        for tick in (100, 101, 999):
            diagnostics.heartbeat(tick, tick-100, 123456, True)
        self.assertEqual(log.records(), [])
        diagnostics.heartbeat(1000, 900, 123456, True)
        diagnostics.heartbeat(1001, 901, 123456, True)
        diagnostics.heartbeat(1900, 1800, 99999, False)
        rows = log.records()
        self.assertEqual([r['event'] for r in rows], ['RUNTIME_ALIVE', 'RUNTIME_ALIVE'])
        self.assertEqual(rows[0]['detail'], 'up=900s heap=123456 clk=1')
        self.assertEqual(rows[1]['detail'], 'up=1800s heap=99999 clk=0')

    def maintain(self, tick, local=None):
        trace = []
        def reset():
            trace.append(('RESET', ''))
            raise ResetRequested()
        env = {
            'daily_done': None, 'brightness_normal': False, 'last_visual': None,
            'last_watchdog': tick, 'sleep_requested': False, 'boot_tick': 0,
            'reboot_deadline': 5400, 'clock_synced': local is not None,
            'local_time': lambda: local, 'runtime_policy': runtime_policy,
            'time': types.SimpleNamespace(monotonic=lambda: tick),
            'startup': types.SimpleNamespace(heartbeat=lambda *a: trace.append(('HEARTBEAT', '')),
                                             first=lambda *a: trace.append(a)),
            'gc': types.SimpleNamespace(mem_free=lambda: 123456),
            'microcontroller': types.SimpleNamespace(reset=reset),
            'log_incident': lambda *a: trace.append(a), 'print': lambda *a: None,
        }
        tree = ast.parse((ROOT / 'firmware/sign_app.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'maintain')
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<maintain>', 'exec'), env)
        return env['maintain'], trace

    def test_runtime_reset_is_logged_before_reset(self):
        maintain, trace = self.maintain(5400)
        with self.assertRaises(ResetRequested):
            maintain()
        self.assertEqual(trace[-2:], [('RESET_REQUEST', '90-minute runtime'), ('RESET', '')])

    def test_daily_reset_is_logged_before_reset(self):
        maintain, trace = self.maintain(50, (2026, 11, 2, 4, 59, 0))
        with self.assertRaises(ResetRequested):
            maintain()
        self.assertEqual(trace[-2:], [('RESET_REQUEST', '04:59 daily'), ('RESET', '')])

    def test_watchdog_deadline_is_logged_before_rearm(self):
        maintain, trace = self.maintain(5395)
        env = maintain.__globals__
        class Watchdog:
            def __setattr__(self, name, value):
                trace.append((name, value))
        env['last_watchdog'] = -1
        env['watchdog'] = Watchdog()
        env['WatchDogMode'] = types.SimpleNamespace(RESET='reset')
        maintain()
        armed = trace.index(('RESET_ARMED', '90-minute runtime'))
        self.assertLess(armed, trace.index(('timeout', 5)))


    def test_daily_watchdog_deadline_is_identified(self):
        maintain, trace = self.maintain(5, (2026, 11, 2, 4, 58, 57))
        env = maintain.__globals__
        class Watchdog:
            def __setattr__(self, name, value):
                trace.append((name, value))
        env['last_watchdog'] = -1
        env['watchdog'] = Watchdog()
        env['WatchDogMode'] = types.SimpleNamespace(RESET='reset')
        maintain()
        self.assertIn(('RESET_ARMED', '04:59 daily'), trace)
        self.assertIn(('timeout', 3), trace)


if __name__ == '__main__':
    unittest.main()
