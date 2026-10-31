import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
import nyan_overlay as cat
import runtime_policy as policy

class Bitmap:
    def __init__(self):self.p=[0]*4096
    def fill(self,value):self.p[:]=[value]*4096
    def __setitem__(self,key,value):
        x,y=key
        assert 2<=x<=125 and 2<=y<=29
        self.p[y*128+x]=value

class Tests(unittest.TestCase):
    def test_hour_window(self):
        for hour,minute,expected in [(4,0,True),(5,0,False),(8,0,False),(9,0,True),(9,1,False),(23,0,True)]:
            self.assertEqual(policy.nyan_active((2026,10,26,hour,minute,0)),expected)
        self.assertTrue(policy.nyan_active((2026,10,26,9,0,59)))
    def test_loop_clipping_and_clear(self):
        b=Bitmap()
        for tenth in range(600):
            cat.paint(b,tenth,True,seconds=tenth/10)
        cat.paint(b,120,True,seconds=12)
        self.assertTrue(all(b.p[y*128+50] in range(5,11) for y in range(9,21)))
        cat.paint(b,590,True,seconds=59.9)
        self.assertFalse(any(b.p))
        cat.paint(b,200,False,seconds=20);self.assertFalse(any(b.p))
    def test_brighter_offhour_text(self):
        colors=(0,0x101010,0x602000,0x202000,0x600000,0x101010)
        dim=policy.scaled_colors(colors,False)
        self.assertEqual(dim[1],0x101010);self.assertEqual(dim[5],0x101010)
        self.assertEqual(dim[3],0x080800)

if __name__=='__main__':unittest.main()
