# mine.py <evidence.json> : the capture window of a moat run from its recorded calls (orders, ProofCaptureDown series, end pawns)
import json,sys
d=json.load(open(sys.argv[1])); calls=d['calls']
i0=next((i for i,c in enumerate(calls) if c['tool']=='jawa/ordered_job'),None)
if i0 is None: print('no ordered_job'); sys.exit()
j=i0-8; last={}
for c in calls[j:]:
    t=c['tool']; a=c['args']; r=c['result']
    if t=='jawa/spawn_pawn': print('SPAWN', a.get('kindDef'), a.get('x'),a.get('z'), [p['id'] for p in r.get('pawns',[])], (r.get('state') or {}).get('tick'))
    elif t=='jawa/ordered_job': print('ORDER', a, {k:r.get(k) for k in ('accepted','beforeJobDef','afterJobDef','nowRunningRequested')}, (r.get('state') or {}).get('tick'))
    elif t=='jawa/static_call' and a[1]=='ProofCaptureDown':
        res=str(r.get('result')); tick=(r.get('state') or {}).get('tick')
        if last.get(a[2])!=res: print('CAP', tick, a[2], res)
        last[a[2]]=res
    elif t=='jawa/list_pawns' and a.get('faction')=='player':
        print('PLAYER', [(p['id'],p['x'],p['z'],'downed' if p.get('downed') else 'up') for p in r.get('pawns',[])])
    elif t=='jawa/pawn_force_incapacitate': print('VANISH', a.get('pawn'))
    elif t=='jawa/flowworks_job_probe' or 'Pump' in str(a)[:60]: break
