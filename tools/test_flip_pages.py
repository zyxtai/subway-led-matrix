import sys,os,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
with patch.dict(os.environ,{'MTA_MANHATTAN_STOP':'TEST_INBOUND','MTA_QUEENS_STOP':'TEST_OUTBOUND'}):import arrival_ui as ui
class Bitmap:
 def __init__(self):self.p=[0]*4096
 def fill(self,v):self.p[:]=[v]*4096
 def __getitem__(self,k):return self.p[k[1]*128+k[0]]
 def __setitem__(self,k,v):
  x,y=k;assert 2<=x<=125 and 2<=y<=29;self.p[y*128+x]=v
class Tests(unittest.TestCase):
 def test_pages_and_flip(self):
  data=[(1120+i*60,str(i),route) for i,route in enumerate(('E','F','M','R'))]
  self.assertEqual([r[2] for r in ui.nearest(data,1000,0)],['E','F'])
  self.assertEqual([r[2] for r in ui.nearest(data,1000,1)],['M','R'])
  self.assertEqual(ui.nearest(data[:2],1000,1),data[:2])
  self.assertEqual(ui.flip_state(0),(0,0));self.assertEqual(ui.flip_state(60),(1,0));self.assertEqual(ui.flip_state(120),(0,0))
  b=Bitmap()
  for step in range(120):
   ui.paint(b,{'TEST_INBOUND':data,'TEST_OUTBOUND':data},1000,5,scroll_step=step,flip_step=step)
   self.assertFalse(any(b[x,y] for x in (57,58,59) for y in range(32)))
  ui.paint(b,{'TEST_INBOUND':data},1000,5,scroll_step=50,flip_step=50);half=b.p[:]
  ui.paint(b,{'TEST_INBOUND':data},1000,5,scroll_step=54,flip_step=54)
  self.assertFalse(any(b[x,y] for x in range(60,126) for y in range(2,15)))
if __name__=='__main__':unittest.main()
