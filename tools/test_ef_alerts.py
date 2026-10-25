import sys,unittest
import os
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
with patch.dict(os.environ, {'MTA_MANHATTAN_STOP': 'TEST_INBOUND', 'MTA_QUEENS_STOP': 'TEST_OUTBOUND', 'MTA_PARENT_STOP': 'TEST_PARENT'}):
 import station_config
import mta_minimal as dec
import mta_alerts
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
 def test_alert_scope_and_active_period(self):
  f=pb.FeedMessage();f.header.gtfs_realtime_version='2.0';f.header.timestamp=1000
  e=f.entity.add();e.id='alert';a=e.alert;p=a.active_period.add();p.start=950;p.end=1100
  s=a.informed_entity.add();s.agency_id='MTASBWY';s.route_id='E';s.stop_id='TEST_INBOUND';s.direction_id=1
  _,h=mta_alerts.decode(f.SerializeToString(),1000)
  row=(1060,'trip','E',1)
  self.assertTrue(ui.affected(row,'TEST_INBOUND',1000,h))
  self.assertFalse(ui.affected(row,'TEST_OUTBOUND',1000,h))
  self.assertFalse(ui.affected(row,'TEST_INBOUND',1100,h))
  self.assertFalse(ui.affected((1060,'trip','F',1),'TEST_INBOUND',1000,h))
  self.assertFalse(ui.affected((1060,'trip','E',0),'TEST_INBOUND',1000,h))
  a.informed_entity[0].stop_id='OTHER'
  self.assertEqual(mta_alerts.decode(f.SerializeToString(),1000)[1],[])
 def test_badges_and_hazard(self):
  b=Bitmap();data={'TEST_INBOUND':[(1120,'e','E',1),(1180,'f','F',1)],'TEST_OUTBOUND':[(1200,'m','M',0),(1300,'r','R',0)]}
  ui.paint(b,data,1000,5);self.assertTrue(all(c in b.p for c in (2,3,6)))
  prior=b.p[:];h=[('E','TEST_INBOUND',None,None,((900,1100),))]
  ui.paint(b,data,1000,5,hazards=h);self.assertNotEqual(prior,b.p);self.assertIn(4,b.p)
  self.assertNotEqual(ui.visual_key(data,1000,5),ui.visual_key(data,1000,5,hazards=h))
  self.assertEqual(ui.COLORS[2],0x201000);self.assertEqual(ui.COLORS[6],0x000020)
 def test_stale_alert_header(self):
  f=pb.FeedMessage();f.header.gtfs_realtime_version='2.0';f.header.timestamp=1
  with self.assertRaises(ValueError):mta_alerts.decode(f.SerializeToString(),1000)
unittest.main()
