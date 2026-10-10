"""In-session attribution A/B on the 550-mod full list (MUST 17 partial). python.exe Transient/foundry_tps_ab_run_20261010.py
Blocks: per speed, ABBA (on, off, off, on), BLOCK_S wall seconds each, after a 10 s settle discarded.
Writes the schedule (UTC block bounds) to Transient/foundry_tps_ab_schedule_20261010.json; analysis reads the disk record."""
import json, os, sys, time, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, '..', 'src', 'RimMandrake', 'Utils')
for p in (U, os.path.join(U, 'modcheck')):
    sys.path.insert(0, p)
from rimdrive import Session
import helpers as H

BLOCK_S = float(os.environ.get('AB_BLOCK_S', '40'))
SETTLE_S = 10
SPEEDS = os.environ.get('AB_SPEEDS', 'Normal,Superfast,Ultrafast').split(',')
OUT = os.path.join(HERE, 'foundry_tps_ab_schedule_20261010.json')


def now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def c(s, tool, **p):
    r = s.call(tool, **p)
    if isinstance(r, dict) and r.get('content') and isinstance(r['content'], list):
        try:
            r = json.loads(r['content'][0]['text'])
        except Exception:
            pass
    return r


sched = {'started': now(), 'blockS': BLOCK_S, 'settleS': SETTLE_S, 'blocks': []}
with Session(lock=None) as s:
    kh = H.kill_hostiles(s, ())
    sched['killHostiles'] = {'acted': kh.acted, 'verified': kh.verified, 'residue': kh.residue}
    for sp in SPEEDS:
        for on in (True, False, False, True):
            a = c(s, 'jawa/tps_test_attribution', on=on)
            g = c(s, 'jawa/set_game_speed', speed=sp)
            t0 = time.time()
            time.sleep(SETTLE_S)
            b = {'speed': sp, 'attribution': on, 'attrReply': a, 'speedReply': g, 'start': now()}
            time.sleep(BLOCK_S)
            b['end'] = now()
            sched['blocks'].append(b)
            print(sp, on, b['start'], b['end'], flush=True)
            json.dump(sched, open(OUT, 'w'), indent=1, default=str)
    c(s, 'jawa/tps_test_attribution', on=True)
    c(s, 'jawa/set_game_speed', speed='Paused')
sched['ended'] = now()
json.dump(sched, open(OUT, 'w'), indent=1, default=str)
print('DONE', OUT)
