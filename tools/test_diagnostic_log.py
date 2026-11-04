import sys,unittest,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
from diagnostic_log import IncidentLog
class Tests(unittest.TestCase):
    def test_persistent_ring_and_truncation(self):
        memory=bytearray(512);log=IncidentLog(memory)
        for i in range(8):log.record('FAIL'+str(i),'x'*200)
        restored=IncidentLog(memory)
        self.assertEqual(len(restored.records()),3)
        self.assertEqual([x['seq'] for x in restored.records()],[6,7,8])
    def test_unknown_data_preserved(self):
        with self.assertRaises(ValueError):IncidentLog(bytearray(b'x'*512))
    def test_duplicate_throttle(self):
        log=IncidentLog(bytearray(512));log.record('FAIL','network');log.record('FAIL','network')
        self.assertEqual(len(log.records()),1)
    def test_watchdog_disabled_during_flash_write_and_restored_on_failure(self):
        watchdog=types.SimpleNamespace(mode='RESET',timeout=0.1)
        class Memory(bytearray):
            fail=False
            modes=[]
            def __setitem__(self,key,value):
                self.modes.append(watchdog.mode)
                if self.fail:raise OSError('test write failure')
                super().__setitem__(key,value)
        memory=Memory(512);log=IncidentLog(memory,watchdog=watchdog)
        log.record('RESET_REQUEST','test')
        self.assertTrue(all(mode is None for mode in memory.modes))
        self.assertEqual(watchdog.mode,'RESET')
        self.assertEqual(watchdog.timeout,0.1)
        memory.fail=True
        with self.assertRaises(OSError):log.record('SECOND','test')
        self.assertEqual(watchdog.mode,'RESET')
if __name__=='__main__':unittest.main()
