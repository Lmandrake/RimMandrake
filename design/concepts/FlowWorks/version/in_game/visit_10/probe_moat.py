"""probe_moat.py: the moat walkers' raised-leaf order, read (visit 10 sitting; classes the UNMEASURED MW_raised_leaf row)."""
import os, sys, json
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck", "src/RimMandrake/FlowWorks/northstar"):
    sys.path.insert(0, os.path.join(R, *p.split("/")))
import concept_scenes as C, validation_core as V, test_site_saves as T
B = V.Bridge()
l = T.load_site(B.call, 'calm'); print('site', l.get('verified'))
def body(S):
    G = C._moat_stage(S, raised=True, raiders=False)
    print('geom', {k: (v if k not in ('ring', 'pit') else len(v)) for k, v in G.items()})
    bank, plot = G['raiders_at'][0], (G['col'][0], G['col'][1] + 1)
    for tag, who in (('col', 'player'),):
        w = S.pawn('Colonist', bank, 'player')
        print('pawn', w, C._at(S, w))
        print('reach', S.sc(C.WALLREACH, 'ProofReachPair', '%s;%d,%d' % (w.replace('Human', ''), plot[0], plot[1])))
        r = S.call('jawa/order_pawn', pawnId=w, x=plot[0], z=plot[1], waitTicks=120, draft=True)
        print(json.dumps({k: v for k, v in r.items() if k not in ('operation', 'state', 'effects')})[:2500])
        for _ in range(6):
            S.ticks(60)
            at = C._at(S, w)
            print('at', at, S.sc(C.SWIMP, 'ProofSwim', '%d,%d' % at))
        print(json.dumps(S.call('jawa/pawn_get', pawnId=w))[:1800])
    S.row('probe', True, 'x')
f = C._run('probe', body)
from game_paths import SAVES
n = 'FW_probe_moat'
import time
n += time.strftime('%H%M%S')
res = {}
print(f(B, lambda: T.save_site(B.call, n, SAVES), lambda: T.load_site(B.call, 'calm', name=n, check=False), res)['status'])
