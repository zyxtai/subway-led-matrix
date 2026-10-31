"""Export persistent incidents to separate JSON files on CIRCUITPY (Mac/Linux)."""
import argparse,json,os,select,termios,time
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',required=True)
    parser.add_argument('--drive',type=Path,default=Path('/Volumes/CIRCUITPY'))
    args=parser.parse_args()
    fd=os.open(args.port,os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
    try:
        settings=termios.tcgetattr(fd);settings[0]=0;settings[1]=0;settings[3]=0
        settings[2]|=termios.CLOCAL|termios.CREAD
        settings[4]=termios.B115200;settings[5]=termios.B115200
        termios.tcsetattr(fd,termios.TCSANOW,settings)
        os.write(fd,b'\x03');time.sleep(0.2);os.write(fd,b'\x03');time.sleep(0.2)
        os.write(fd,b"import diagnostic_log; print('LOG_BEGIN'); print(diagnostic_log.export()); print('LOG_END')\r")
        raw=b'';deadline=time.monotonic()+12
        while time.monotonic()<deadline:
            if select.select([fd],[],[],.2)[0]:
                raw+=os.read(fd,16384)
                if b'\r\nLOG_END\r\n' in raw:break
        lines=raw.decode(errors='replace').splitlines()
        start=next(i for i,line in enumerate(lines) if line.strip()=='LOG_BEGIN')
        records=json.loads(lines[start+1])
        folder=args.drive/'logs';folder.mkdir(exist_ok=True)
        for row in records:
            target=folder/('incident-{}-{}.json'.format(row['utc'],row['seq']))
            target.write_text(json.dumps(row,indent=2)+'\n')
        print('Exported',len(records),'incident files to',folder)
    finally:
        os.write(fd,b'\x04');os.close(fd)

if __name__=='__main__':main()
