"""probe_moat2.py: stage the raised moat and leave it up; read reach for a colonist and a placed hostile (visit 10 sitting)."""
import os, sys, json
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck", "src/RimMandrake/FlowWorks/northstar"):
    sys.path.insert(0, os.path.join(R, *p.split("/")))
import concept_scenes as C, validation_core as V, test_site_saves as T
B = V.Bridge()
print('site', T.load_site(B.call, 'calm').get('verified'))
S = C._Stage(B, {}, 'probe')
G = C._moat_stage(S, raised=True, raiders=False)
bank, plot = G['raiders_at'][0], (G['col'][0], G['col'][1] + 1)
def reach(w, to): return S.sc(C.WALLREACH, 'ProofReachPair', '%s;%d,%d' % (w.replace('Human', ''), to[0], to[1]))
w = S.pawn('Colonist', bank, 'player')
h = S.pawn(C.MOAT_KIND, (68, 54), C._isl_hostile_faction(S))
wet = [c for c in G['ring'] if c[0] == 65]
print('ring col 65', wet, S.cells(wet))
for nm, p in (('colonist', w), ('hostile', h)):
    print(nm, 'plot', reach(p, plot))
    for c in wet[:5]: print(nm, c, reach(p, c))
print('at', C._at(S, w), C._at(S, h))
print(S.sc(C.WALLREACH, 'ProofReach', ''))
