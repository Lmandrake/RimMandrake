"""probe_und.py: is the under-deck path read stale at the staging instant once the floor-view masks exist? (visit 10 sitting)"""
import os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck"):
    sys.path.insert(0, os.path.join(R, *p.split("/")))
import validation_core as V, test_site_saves as T
B = V.Bridge()
print('site', T.load_site(B.call, 'calm').get('verified'))
PR = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
import re
SRC = open(os.path.join(R, "src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py"), encoding="utf-8").read()
PR = re.search(r'^PROOF\s*=\s*"([^"]+)"', SRC, re.M).group(1)
rows = []
V.site_calm(B); B.call("jawa/kill_hostiles"); V.prepare_site(B, (138, 138, 40, 94), rows, "und")
def pf(m, a): return str((B.call("jawa/static_call", type=PR, method=m, args=a) or {}).get("result"))
def trench(z, d=8):
    for i in range(1, 9): B.call("jawa/flowworks_excavation_drive", x=140 + i, z=z, deepenLevels=d, setBodyWaterM=-1)
def bridge(z): return pf("ProofBuild", "144,%d;145,%d;steel;god" % (z - 1, z + 1))
def pawn(x, z): return ((B.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1) or {}).get("pawns") or [{}])[0].get("id").replace("Human", "")
for n, z in enumerate((160, 170, 180, 190)):
    trench(z); print(z, bridge(z))
    a = pawn(141, z)
    for t in (0, 10, 30, 61, 120):
        if t: B.call("jawa/safe_advance", ticks=t) if False else B.ticks(t)
        at = [(p.get('x'), p.get('z')) for p in B.call("jawa/site_state").get("pawns") or [] if p.get("id") == "Human" + a]
        print('  +%d' % t, at, pf("ProofUnderPath", "%s;148,%d" % (a, z)), '|', pf("ProofReach", "%s;148,%d" % (a, z)))
