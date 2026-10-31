import sys,os,unittest,datetime,time,calendar
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
with patch.dict(os.environ,{'MTA_MANHATTAN_STOP':'TEST_INBOUND','MTA_QUEENS_STOP':'TEST_OUTBOUND'}):
 import arrival_ui as ui
import runtime_policy as policy
class Bitmap:
 def __init__(self):self.p=[0]*4096
 def fill(self,v):self.p[:]=[v]*4096
 def __setitem__(self,k,v):
  x,y=k;assert 2<=x<=125 and 2<=y<=29,(x,y);self.p[y*128+x]=v
class Tests(unittest.TestCase):
 def test_two_slot_pages(self):
  b=Bitmap();rows=[(1120+i*60,str(i),route) for i,route in enumerate(('E','F','M','R','E'))]
  self.assertEqual(len(ui.nearest(rows,1000)),2)
  self.assertEqual([r[2] for r in ui.nearest(rows,1000,1)],["M","R"])
  for step in range(ui.scroll_period()):
   ui.paint(b,{'TEST_INBOUND':rows,'TEST_OUTBOUND':rows},1000,5,scroll_step=step)
   for left in (60,94):self.assertTrue(any(b.p[y*128+left+x] for y in range(2,15) for x in range(13)))
   self.assertFalse(any(b.p[y*128+x] for y in range(32) for x in (57,58,59)))
  ui.paint(b,{'TEST_INBOUND':[(100000,'long','E')]},1000,5)
 def test_overnight_limits(self):
  for h,m,expected in [(8,29,False),(8,30,True),(12,0,True),(20,29,True),(20,30,True),(0,0,True),(4,58,True),(4,59,False),(5,0,False)]:
   self.assertEqual(policy.overnight((2026,10,27,h,m,0)),expected)
 def test_final_wake_seconds(self):
  zone=ZoneInfo('America/New_York')
  now=datetime.datetime(2026,10,30,4,58,57,tzinfo=zone).timestamp()
  with patch.object(policy.time,'localtime',side_effect=time.gmtime),patch.object(policy.time,'mktime',side_effect=calendar.timegm):
   self.assertEqual(policy.standby_interval(now),3)
 def test_wake_dst(self):
  zone=ZoneInfo('America/New_York')
  for date in [(2026,10,27,8,30),(2026,10,31,20,30),(2026,3,7,20,30),(2026,11,1,1,30)]:
   local=datetime.datetime(*date,tzinfo=zone)
   day=local.date()+datetime.timedelta(days=1 if local.hour*60+local.minute>=510 else 0)
   wake=datetime.datetime.combine(day,datetime.time(4,59),tzinfo=zone)
   now=local.timestamp()
   with patch.object(policy.time,'localtime',side_effect=time.gmtime),patch.object(policy.time,'mktime',side_effect=calendar.timegm):
    self.assertEqual(policy.wake_delay(now),wake.timestamp()-now)
    self.assertEqual(policy.standby_interval(now),min(60,wake.timestamp()-now))
if __name__=='__main__':unittest.main()
