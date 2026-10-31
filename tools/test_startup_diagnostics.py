"""Exercise startup logging and exceptions before the display app can start."""
import builtins
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
import diagnostic_log


class StartupTests(unittest.TestCase):
    def test_milestones_once_and_private_failure_details(self):
        log = diagnostic_log.IncidentLog(bytearray(4096))
        startup = diagnostic_log.StartupDiagnostics(log)
        for _ in range(10):
            startup.first('FRAME_READY', 'Published')
        startup.first('WIFI_BEGIN')
        startup.failure(ValueError('private network and platform settings'))
        rows = log.records()
        self.assertEqual([row['event'] for row in rows], ['FRAME_READY', 'WIFI_BEGIN', 'FATAL'])
        self.assertEqual(rows[-1]['detail'], 'WIFI_BEGIN:ValueError')
        self.assertNotIn('private', str(rows))

    def test_logging_failure_does_not_stop_application(self):
        broken = types.SimpleNamespace(record=lambda *args: (_ for _ in ()).throw(OSError('private')))
        for log in (None, broken):
            startup = diagnostic_log.StartupDiagnostics(log)
            with redirect_stdout(io.StringIO()) as output:
                startup.first('BOOT')
                startup.failure(RuntimeError('private'))
            self.assertNotIn('private', output.getvalue())

    def test_launcher_continues_when_nvm_is_unavailable(self):
        micro = types.SimpleNamespace(nvm=bytearray(b'x' * 4096), cpu=types.SimpleNamespace(reset_reason='SOFTWARE'))
        with patch.dict(sys.modules, {'microcontroller': micro, 'sign_app': types.ModuleType('sign_app')}):
            result = runpy.run_path(str(ROOT / 'docs/code.py'))
        self.assertIsNone(result['incidents'])
        self.assertIn('BOOT', diagnostic_log.startup.seen)

    def test_launcher_records_failure_before_display_import(self):
        memory = bytearray(4096)
        micro = types.SimpleNamespace(nvm=memory, cpu=types.SimpleNamespace(reset_reason='SOFTWARE'))
        original_import = builtins.__import__

        def imports(name, *args, **kwargs):
            if name == 'sign_app':
                raise ImportError('private settings must not be logged')
            return original_import(name, *args, **kwargs)

        with patch.dict(sys.modules, {'microcontroller': micro}), patch('builtins.__import__', side_effect=imports):
            with self.assertRaises(ImportError):
                runpy.run_path(str(ROOT / 'docs/code.py'))
        rows = diagnostic_log.IncidentLog(memory).records()
        self.assertEqual([row['event'] for row in rows], ['BOOT', 'FATAL'])
        self.assertEqual(rows[-1]['detail'], 'BOOT:ImportError')


if __name__ == '__main__':
    unittest.main()
