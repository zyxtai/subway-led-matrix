import sys,unittest
import os
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_mta import inspect
from google.transit import gtfs_realtime_pb2 as pb
class Tests(unittest.TestCase):
 def feed(self):
  f=pb.FeedMessage();f.header.gtfs_realtime_version='2.0';f.header.timestamp=1000
  e=f.entity.add();e.id='test';t=e.trip_update;t.trip.trip_id='trip';t.trip.route_id='E'
  s=t.stop_time_update.add();s.stop_id='TEST_INBOUND';s.arrival.time=1061
  return f,t,s
 def test_prediction_and_rounding(self):
  f,t,s=self.feed();a=inspect(f.SerializeToString(),{'TEST_INBOUND'},{'E'},1000)[1];self.assertEqual(a[0]['minutes'],2)
 def test_cancelled_skipped_past_and_other_station(self):
  for kind in ['cancel','skip','past','station','missing']:
   f,t,s=self.feed()
   if kind=='cancel':t.trip.schedule_relationship=3
   if kind=='skip':s.schedule_relationship=1
   if kind=='past':s.arrival.time=999
   if kind=='station':s.stop_id='OTHER'
   if kind=='missing':s.ClearField('arrival')
   self.assertEqual(inspect(f.SerializeToString(),{'TEST_INBOUND'},{'E'},1000)[1],[])
 def test_stale_and_differential(self):
  for kind in ['stale','differential']:
   f,t,s=self.feed()
   if kind=='stale':f.header.timestamp=1
   else:f.header.incrementality=1
   with self.assertRaises(ValueError):inspect(f.SerializeToString(),{'TEST_INBOUND'},{'E'},1000)
 def test_board_decoder_uses_private_platforms(self):
  sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'firmware'))
  with patch.dict(os.environ, {'MTA_MANHATTAN_STOP': 'TEST_INBOUND', 'MTA_QUEENS_STOP': 'TEST_OUTBOUND'}):
   import mta_minimal
  f,t,s=self.feed();t.trip.route_id='R'
  other=t.stop_time_update.add();other.stop_id='TEST_OUTBOUND';other.arrival.time=1120
  ignored=t.stop_time_update.add();ignored.stop_id='UNSELECTED';ignored.arrival.time=1060
  timestamp,arrivals=mta_minimal.decode(f.SerializeToString(),1000)
  self.assertEqual(timestamp,1000)
  self.assertEqual(arrivals, {'TEST_INBOUND':[(1061,'trip','R')], 'TEST_OUTBOUND':[(1120,'trip','R')]})
  official=inspect(f.SerializeToString(),set(arrivals),{'R'},1000)[1]
  self.assertEqual(sum(len(rows) for rows in arrivals.values()),len(official))
unittest.main()
