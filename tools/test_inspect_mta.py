import sys,unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_mta import inspect
from google.transit import gtfs_realtime_pb2 as pb
class Tests(unittest.TestCase):
 def feed(self):
  f=pb.FeedMessage();f.header.gtfs_realtime_version='2.0';f.header.timestamp=1000
  e=f.entity.add();e.id='test';t=e.trip_update;t.trip.trip_id='trip';t.trip.route_id='E'
  s=t.stop_time_update.add();s.stop_id='G10S';s.arrival.time=1061
  return f,t,s
 def test_prediction_and_rounding(self):
  f,t,s=self.feed();a=inspect(f.SerializeToString(),{'G10S'},{'E'},1000)[1];self.assertEqual(a[0]['minutes'],2)
 def test_cancelled_skipped_past_and_other_station(self):
  for kind in ['cancel','skip','past','station','missing']:
   f,t,s=self.feed()
   if kind=='cancel':t.trip.schedule_relationship=3
   if kind=='skip':s.schedule_relationship=1
   if kind=='past':s.arrival.time=999
   if kind=='station':s.stop_id='OTHER'
   if kind=='missing':s.ClearField('arrival')
   self.assertEqual(inspect(f.SerializeToString(),{'G10S'},{'E'},1000)[1],[])
 def test_stale_and_differential(self):
  for kind in ['stale','differential']:
   f,t,s=self.feed()
   if kind=='stale':f.header.timestamp=1
   else:f.header.incrementality=1
   with self.assertRaises(ValueError):inspect(f.SerializeToString(),{'G10S'},{'E'},1000)
unittest.main()
