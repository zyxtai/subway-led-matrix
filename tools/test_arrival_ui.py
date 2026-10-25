import importlib.util
import os
import sys
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'firmware'))
with patch.dict(os.environ, {'MTA_MANHATTAN_STOP': 'TEST_INBOUND', 'MTA_QUEENS_STOP': 'TEST_OUTBOUND'}):
 import station_config
spec=importlib.util.spec_from_file_location('ui',str(Path(__file__).resolve().parents[1]/'firmware/arrival_ui.py'));ui=importlib.util.module_from_spec(spec);spec.loader.exec_module(ui)
class Bitmap:
 def __init__(self):self.p=[0]*4096
 def fill(self,v):self.p[:]=[v]*4096
 def __setitem__(self,k,v):
  x,y=k
  assert 2<=x<=125 and 2<=y<=29,(x,y)
  self.p[y*128+x]=v
b=Bitmap();data={'TEST_INBOUND':[(1060,'m','M'),(1120,'r','R')],'TEST_OUTBOUND':[(1180,'r2','R'),(1240,'m2','M')]}
assert ui.paint(b,data,1000,5)=='LIVE'
assert 2 in b.p and 3 in b.p
assert ui.nearest([(999,'p','R'),(1120,'b','M'),(1060,'a','R')],1000)==[(1060,'a','R'),(1120,'b','M')]
assert ui.paint(b,data,1000,5,True)=='STALE'
assert ui.paint(b,data,1000,181)=='STALE'
assert 2 not in b.p and 3 not in b.p
for minutes in [0,1,9,10,99,100,1440]:
 ui.paint(b,{'TEST_INBOUND':[(1000+60*minutes,'t','R')]},1000,5)
ui.paint(b,data,1000,5)
print('Pixel bounds, route colors, ordering, stale hiding, and time range checks passed')

assert ui.display_minutes(1061,1000,'TEST_INBOUND') == 1
assert ui.display_minutes(1061,1000,'TEST_OUTBOUND') == 2
assert ui.display_minutes(1000,1000,'TEST_INBOUND') == 0
assert ui.visual_key(data,1000,5) != ui.visual_key(data,1000,5,True)
print('Configured direction offset, clamping, and visual state checks passed')
