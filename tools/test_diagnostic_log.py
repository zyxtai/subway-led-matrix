import sys,unittest
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
if __name__=='__main__':unittest.main()
