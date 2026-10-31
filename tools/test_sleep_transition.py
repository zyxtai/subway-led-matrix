import ast,unittest,types
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/'docs/code.py'
class SleepTransitionTests(unittest.TestCase):
 def test_http_closes_before_sleep(self):
  tree=ast.parse(SOURCE.read_text())
  loop=next(n for n in tree.body if isinstance(n,ast.While))
  request=next(n for n in loop.body if isinstance(n,ast.Try))
  trace=[];calls=[0]
  class Response:
   status_code=200
   def __enter__(self):trace.append('enter');return self
   def __exit__(self,*args):trace.append('exit');return False
   def iter_content(self,**kwargs):yield b'abc'
  def render():
   calls[0]+=1
   if calls[0]>=3:env['sleep_requested']=True
  class SleepRequested(Exception):pass
  env={'ssid':'test','password':'test','wifi':types.SimpleNamespace(radio=types.SimpleNamespace(connected=True)),
   'render':render,'clock_synced':True,'time':types.SimpleNamespace(monotonic=lambda:1),'last_clock_sync':1,
   'sleep_requested':False,'session':types.SimpleNamespace(get=lambda *a,**k:Response()),'url':'test',
   'feed_buffer':bytearray(64),'MAX_FEED_BYTES':64,'SleepRequested':SleepRequested,
   'gc':types.SimpleNamespace(collect=lambda:None,mem_free=lambda:1000),'print':lambda *a:None,
   'name':'E','log_incident':lambda *a:trace.append('unexpected_failure')}
  exec(compile(ast.Module(body=[request],type_ignores=[]),str(SOURCE),'exec'),env)
  self.assertEqual(trace,['enter','exit']);self.assertTrue(env['sleep_requested'])
 def test_standby_reaches_morning_and_resets(self):
  tree=ast.parse(SOURCE.read_text())
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='sleep_until_morning')
  trace=[];times=iter([True,False])
  class Reset(Exception):pass
  def reset():trace.append('reset');raise Reset()
  frame=types.SimpleNamespace(fill=lambda v:None)
  env={'print':lambda *a:None,'log_incident':lambda e,*a:trace.append(e),
   'bitmaps':[frame,frame],'cat_bitmap':frame,'display':types.SimpleNamespace(refresh=lambda **k:None),
   'adafruit_connection_manager':types.SimpleNamespace(connection_manager_close_all=lambda p:trace.append('close')),
   'pool':None,'wifi':types.SimpleNamespace(radio=types.SimpleNamespace(enabled=True)),
   'displayio':types.SimpleNamespace(release_displays=lambda:trace.append('release')),
   'watchdog':types.SimpleNamespace(feed=lambda:trace.append('feed')),'WatchDogMode':types.SimpleNamespace(RESET=1),
   'runtime_policy':types.SimpleNamespace(overnight=lambda t:next(times),standby_interval=lambda t:3),
   'local_time':lambda:None,'time':types.SimpleNamespace(time=lambda:0,monotonic=lambda:0),
   'alarm':types.SimpleNamespace(time=types.SimpleNamespace(TimeAlarm=lambda **k:k),light_sleep_until_alarms=lambda a:trace.append('sleep')),
   'microcontroller':types.SimpleNamespace(reset=reset)}
  exec(compile(ast.Module(body=[fn],type_ignores=[]),str(SOURCE),'exec'),env)
  with self.assertRaises(Reset):env['sleep_until_morning']()
  self.assertLess(trace.index('close'),trace.index('sleep'))
  self.assertLess(trace.index('sleep'),trace.index('MORNING_WAKE'))
  self.assertEqual(trace[-1],'reset');self.assertFalse(env['wifi'].radio.enabled)
 def test_sleep_called_only_from_outer_loop(self):
  tree=ast.parse(SOURCE.read_text())
  for n in tree.body:
   if isinstance(n,ast.FunctionDef) and n.name!='sleep_until_morning':
    self.assertFalse(any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='sleep_until_morning' for c in ast.walk(n)))
  loop=next(n for n in tree.body if isinstance(n,ast.While))
  gate=next(n for n in loop.body if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='sleep_requested')
  self.assertEqual(gate.body[0].value.func.id,'sleep_until_morning')
if __name__=='__main__':unittest.main()
