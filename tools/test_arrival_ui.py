import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('ui',str(Path(__file__).resolve().parents[1]/'firmware/arrival_ui.py'));ui=importlib.util.module_from_spec(spec);spec.loader.exec_module(ui)
class Bitmap:
 def __init__(self):self.p=[0]*4096
 def fill(self,v):self.p[:]=[v]*4096
 def __setitem__(self,k,v):
  x,y=k
  assert 2<=x<=125 and 2<=y<=29,(x,y)
  self.p[y*128+x]=v
b=Bitmap();data={'G10S':[(1060,'m','M'),(1120,'r','R')],'G10N':[(1180,'r2','R'),(1240,'m2','M')]}
assert ui.paint(b,data,1000,5)=='LIVE'
assert 2 in b.p and 3 in b.p
assert ui.nearest([(999,'p','R'),(1120,'b','M'),(1060,'a','R')],1000)==[(1060,'a','R'),(1120,'b','M')]
assert ui.paint(b,data,1000,5,True)=='STALE'
assert ui.paint(b,data,1000,181)=='STALE'
assert 2 not in b.p and 3 not in b.p
for minutes in [0,1,9,10,99,100,1440]:
 ui.paint(b,{'G10S':[(1000+60*minutes,'t','R')]},1000,5)
ui.paint(b,data,1000,5)
print('Pixel bounds, route colors, ordering, stale hiding, and time range checks passed')
