import sys,time,unittest,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
import runtime_policy as p
class Tests(unittest.TestCase):
 def test_dst_matches_new_york(self):
  for date in [(2026,3,8,6,59),(2026,3,8,7,0),(2026,11,1,5,59),(2026,11,1,6,0),(2027,7,1,12,0),(2027,1,1,12,0)]:
   utc=datetime.datetime(*date,tzinfo=datetime.timezone.utc)
   self.assertEqual(p.utc_offset(utc.timetuple()),utc.astimezone(ZoneInfo('America/New_York')).utcoffset().total_seconds()/3600)
 def test_rush_and_daily(self):
  for hour,minute,expected in [(4,59,False),(5,0,True),(8,29,True),(8,30,False),(17,0,False)]:
   self.assertEqual(p.rush((2026,10,26,hour,minute,0)),expected)
  self.assertTrue(p.reboot_minute((2026,10,26,4,59,0)))
  self.assertEqual(p.daily_remaining((2026,10,26,4,58,50)),10)
 def test_independent_expiry(self):
  c=p.FeedCache(['E','R'],['TEST'])
  c.success('E',{'TEST':[(1500,'e','E')]},1000)
  c.success('R',{'TEST':[(1500,'r','R')]},900)
  c.failure('R')
  rows,age,warning=c.snapshot(1100)
  self.assertEqual(rows['TEST'],[(1500,'e','E')]);self.assertTrue(warning)
  self.assertEqual(age,100)
  c.success('E',{'TEST':[(1600,'e2','E')]},1200)
  self.assertEqual(c.snapshot(1200)[0]['TEST'],[(1600,'e2','E')])
 def test_dim_palette(self):
  colors=(0,0x101010,0x602000,0x000020)
  self.assertEqual(p.scaled_colors(colors,True),colors)
  self.assertEqual(p.scaled_colors(colors,False),(0,0x101010,0x0C0400,0x000004))
if __name__=='__main__':unittest.main()
