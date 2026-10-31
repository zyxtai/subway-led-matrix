"""Bounded persistent incident ring. Export while debugging; never log credentials."""
import json
import time

MAGIC = b'MTL1'
SLOT = 128


class IncidentLog:
    def __init__(self, memory, unix_offset=0):
        self.memory = memory
        self.offset = unix_offset
        self.start = max(0,len(memory)-4096)
        self.count = (len(memory)-self.start-4)//SLOT
        if self.count < 1:
            raise ValueError('Not enough NVM for incident log')
        if bytes(memory[self.start:self.start+4]) != MAGIC:
            existing = bytes(memory[self.start:])
            if any(value not in (0,255) for value in existing):
                raise ValueError('NVM contains unknown data; logging not enabled')
            memory[self.start:self.start+4] = MAGIC
        self.sequence = max([row['seq'] for row in self.records()]+[0])
        self.last = {}

    def records(self):
        result=[]
        for index in range(self.count):
            start=self.start+4+index*SLOT
            raw=bytes(self.memory[start:start+SLOT])
            try:
                row=json.loads(raw.split(b'\x00',1)[0].decode())
                if isinstance(row,dict) and 'seq' in row:result.append(row)
            except (ValueError,UnicodeError):pass
        return sorted(result,key=lambda row:row['seq'])

    def record(self,event,detail=''):
        # Log repeated identical failures at most once per five minutes.
        now=time.monotonic();signature=(event,str(detail))
        if signature in self.last and now-self.last[signature]<300:return
        self.last[signature]=now
        if len(self.last)>16:self.last={signature:now}
        self.sequence+=1
        row={'seq':self.sequence,'utc':int(time.time())+self.offset,'event':event,'detail':str(detail)[:52]}
        data=json.dumps(row).encode()
        while len(data)>=SLOT:
            row['detail']=row['detail'][:-1];data=json.dumps(row).encode()
        start=self.start+4+((self.sequence-1)%self.count)*SLOT
        self.memory[start:start+SLOT]=data+b'\x00'*(SLOT-len(data))
        print('Incident:',event,row['detail'])


def export():
    import microcontroller
    offset=946684800-int(time.mktime((2000,1,1,0,0,0,5,1,-1)))
    return json.dumps(IncidentLog(microcontroller.nvm,offset).records())


class StartupDiagnostics:
    """Record milestones once per application start, without exception messages."""
    def __init__(self, log):
        self.log = log
        self.seen = set()
        self.phase = 'BOOT'

    def first(self, event, detail=''):
        if event in self.seen:
            return
        self.seen.add(event)
        self.phase = event
        self._record(event, detail)

    def failure(self, error):
        # Messages can contain private settings; persist only phase and error type.
        self._record('FATAL', self.phase+':'+type(error).__name__)

    def _record(self, event, detail):
        if self.log is not None:
            try:
                self.log.record(event, detail)
            except Exception as error:
                print('Incident write failed:', type(error).__name__)


# Initialized by code.py before the display application is imported.
startup = None
