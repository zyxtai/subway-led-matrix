import sys,unittest
import os
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
with patch.dict(os.environ, {'MTA_MANHATTAN_STOP': 'TEST_INBOUND', 'MTA_QUEENS_STOP': 'TEST_OUTBOUND', 'MTA_PARENT_STOP': 'TEST_PARENT'}):
 import station_config
import mta_minimal as dec
import arrival_ui as ui
from google.transit import gtfs_realtime_pb2 as pb
class Bitmap:
 def __init__(self):self.p=[0]*4096
 def fill(self,v):self.p[:]=[v]*4096
 def __setitem__(self,k,v):
  x,y=k
  assert 2<=x<=125 and 2<=y<=29,(x,y)
  self.p[y*128+x]=v
class Tests(unittest.TestCase):
 def test_routes_and_directions(self):
  f=pb.FeedMessage();f.header.gtfs_realtime_version='2.0';f.header.timestamp=1000
  for i,route in enumerate(('E','F','M','R')):
   e=f.entity.add();e.id=str(i);t=e.trip_update;t.trip.trip_id=str(i);t.trip.route_id=route;t.trip.direction_id=1
   s=t.stop_time_update.add();s.stop_id='TEST_INBOUND';s.arrival.time=1060+i
  _,rows=dec.decode(f.SerializeToString(),1000)
  self.assertEqual([x[2] for x in rows['TEST_INBOUND']],['E','F','M','R'])
  self.assertTrue(all(x[3]==1 for x in rows['TEST_INBOUND']))
 def test_badges(self):
  b=Bitmap();data={'TEST_INBOUND':[(1120,'e','E',1),(1180,'f','F',1)],'TEST_OUTBOUND':[(1200,'m','M',0),(1300,'r','R',0)]}
  ui.paint(b,data,1000,5);self.assertTrue(all(c in b.p for c in (2,3,6)))
  self.assertEqual(ui.COLORS[2],0x602000);self.assertEqual(ui.COLORS[6],0x000030)
unittest.main()
