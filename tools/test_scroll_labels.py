import os,sys,importlib.util
from pathlib import Path
from unittest.mock import patch
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'firmware'))
with patch.dict(os.environ,{'MTA_MANHATTAN_STOP':'TEST_INBOUND','MTA_QUEENS_STOP':'TEST_OUTBOUND'}):import arrival_ui as ui
class Bitmap:
 def __init__(self):self.p=[0]*4096
 def fill(self,v):self.p[:]=[v]*4096
 def __setitem__(self,k,v):
  x,y=k;assert 2<=x<=125 and 2<=y<=29,(x,y);self.p[y*128+x]=v
b=Bitmap();data={'TEST_INBOUND':[(1120,'a','M'),(1180,'b','R')],'TEST_OUTBOUND':[(1120,'c','F'),(1180,'d','E')]}
ui.paint(b,data,1000,5,scroll_step=0);fixed=[b.p[y*128+x] for y in range(32) for x in range(60,128)]
period=ui.scroll_period()
assert period-max(ui.text_width('MANHATTAN'),ui.text_width('FOREST HILLS')) == 8
for step in range(period+1):
 ui.paint(b,data,1000,5,scroll_step=step)
 assert [b.p[y*128+x] for y in range(32) for x in range(60,128)]==fixed
 assert all(b.p[y*128+x]==0 for y in range(32) for x in (0,1,57,58,59))
 assert ui.scroll_x(step)==ui.scroll_x(step+period)
assert ui.scroll_x(1)==ui.scroll_x(0)-1
assert ui.COLORS[2]==ui.COLORS[7]==0x602000
ui.paint(b,data,1000,5,True,scroll_step=50)
assert all(b.p[y*128+x]==0 for y in range(32) for x in (57,58,59))
print('Full scroll-cycle: bounds, margins, shared phase, fixed badges/times, wrap, stale position and orange passed')
