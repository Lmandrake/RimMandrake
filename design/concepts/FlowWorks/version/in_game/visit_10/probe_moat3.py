"""probe_moat3.py: on the stage probe_moat2 left up, tick and re-read reach (visit 10 sitting)."""
import os, sys, json
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck", "src/RimMandrake/FlowWorks/northstar"):
    sys.path.insert(0, os.path.join(R, *p.split("/")))
import concept_scenes as C, validation_core as V
B = V.Bridge(); S = C._Stage(B, {}, 'probe')
ps = S.call('jawa/site_state').get('pawns') or []
def reach(w, to): return S.sc(C.WALLREACH, 'ProofReachPair', '%s;%d,%d' % (w.replace('Human', ''), to[0], to[1]))
cs = [q for q in ps if (q.get('x'), q.get('z')) in ((65, 54), (68, 54))]
print(cs)
for n in (0, 61, 120, 300):
    if n: S.ticks(n)
    for q in cs:
        for to in ((69, 69), (65, 60)):
            print(n, q['id'], to, reach(q['id'], to))
print(S.sc(C.WALLREACH, 'ProofReach', '')[:1500])
