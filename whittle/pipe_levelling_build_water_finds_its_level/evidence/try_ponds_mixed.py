"""A4 beyond the proof's equal-floor rig: two more rigs a player would build, on the map walk_gaps_proof.py --fresh-map leaves.

  rig M (different depth AND area): pit A 3x3 dug 6 notches, full (F=6); pit B 5x5 dug 2 notches, F=1. Levelling by SURFACE
        ends with both surfaces equal and very different water per square (A ~52,600 dL, B ~12,600 dL per square at
        U=10,000 dL per notch); levelling by volume would give equal dL per square. Total conserved.
  rig N (a natural pond): a 5x5 WaterShallow pond painted on dry ground, formed into a limited body at 90% of its capacity
        (RM_NorthstarProofs.ProofSetBodyFraction), joined to a 3x3 pit dug 4 notches holding F=1. The pond runs down into the
        pit until the surfaces meet.
Both rigs use walk_gaps_proof's POND_RIG hose shape (two West reels on one pipe run, hoses to the pools' lips), Intake on the
first pool. Reads per 250-tick cycle: the reel's inspect line, the mouse-over depth text a player sees on each pool's centre
square (ProofReadout), the dug pits' dL (ProofPitWater), each body's surface (ProofLevelSurface), and the link counters.

  python.exe whittle/pipe_levelling_build_water_finds_its_level/evidence/try_ponds_mixed.py <out.json>
"""
import json
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
for p in ("src/RimMandrake/FlowWorks/northstar", "src/RimMandrake/Utils"):
    sys.path.insert(0, os.path.join(REPO, p))
import validation_core as V  # noqa: E402
import proof_hose as PH  # noqa: E402

LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
FLUIDP = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
WATER = "RM_Fluid_Water"
B = V.guard(PH.PB())
out = {"rigs": {}}


def static(ty, m, arg):
    r = B.call("jawa/static_call", type=ty, method=m, args=arg, _answer=True) or {}
    return str(r.get("result") or r.get("message") or r.get("error") or "")


def tick(n):
    B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40))


def build(*ops):
    return B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False) or {}


def dig_fill(x0, z0, w, h, depth, fill):
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + h):
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=depth, setFill=-1)
            if fill:
                static(FLUIDP, "ProofFillWithFluid", "%d,%d,%d,%s" % (x, z, fill, WATER))


def rig(ox, oz):
    """POND_RIG's hose shape at origin (ox, oz): reels (10,2)/(10,4), pipe x12 z2..5, ends at the lips (3,-3) and (3,9)."""
    r1, r2 = (ox + 10, oz + 2), (ox + 10, oz + 4)
    e1, e2 = (ox + 3, oz - 3), (ox + 3, oz + 9)
    build(*(["RM_UniversalPipe:%d,%d" % (ox + 12, oz + z) for z in range(2, 6)] + [V.reel_toward(r1, e1), V.reel_toward(r2, e2)]))
    tick(2)
    for r, e in ((r1, e1), (r2, e2)):
        B.hp("lay:%d,%d,%d,%d" % (r + e), answer=True)
    for r, role in ((r1, "Intake"), (r2, "Outflow")):
        V.settle_census(lambda: B.hp("census", answer=True), lambda h, r=r: V.reel_at(h.get("reel"), r))
        static(LPROOF, "ProofHoseRole", "%d,%d;%s" % (r + (role,)))
    tick(2)
    return r1, r2


def inspect_level(r):
    lt = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,2" % r, limit=1, _answer=True) or {}
    rid = ((lt.get("things") or [{}])[0]).get("id")
    ins = B.call("jawa/inspect_string", thingIds=str(rid), _answer=True) or {}
    return " / ".join(x for t in (ins.get("things") or []) for x in (t.get("inspect") or []) if "Levelling" in x or "Free end" in x)


B.call("rimworld/pause_game", pause=True)
site = []
for rect in ((144, 30, 22, 26), (126, 90, 40, 24)):
    V.prepare_site(B, rect, site, "ponds_mixed_site")
out["site"] = site
# rig M: origin (150, 40): pool A 3x3 at (150,36) depth 6 full; pool B 5x5 at (148,48) depth 2, F=1
MO = (150, 40)
dig_fill(150, 36, 3, 3, 6, 6)
dig_fill(148, 48, 5, 5, 2, 1)
m_reels = rig(*MO)
# rig N: origin (150, 100): a 5x5 natural pond at (148, 94), formed at 90%; pit 3x3 at (150, 108) depth 4, F=1
NO = (150, 100)
B.call("jawa/set_terrain_batch", ops="WaterShallow:148,94,5,5")
tick(2)
out["pondFormed"] = static(NPROOF, "ProofSetBodyFraction", "150;96;0.9")
# control: the same pond with no hose, 12 squares away: a natural pond's stock moves on its own (seepage, rain, season), so
# levelling's conservation is pond loss + control drift == pit gain, not pond loss == pit gain
B.call("jawa/set_terrain_batch", ops="WaterShallow:130,94,5,5")
tick(2)
out["controlFormed"] = static(NPROOF, "ProofSetBodyFraction", "132;96;0.9")
dig_fill(150, 108, 3, 3, 4, 1)
n_reels = rig(*NO)
RIGS = {
    "M_depth_and_area": {"reels": m_reels, "rects": ["150,36,3,3", "148,48,5,5"], "centres": [(151, 37), (150, 50)], "squares": [9, 25]},
    "N_natural_pond": {"reels": n_reels, "rects": ["148,94,5,5", "150,108,3,3"], "centres": [(150, 96), (151, 109)], "squares": [25, 9]},
}


def read(name, t):
    g = RIGS[name]
    rec = {"tick": t,
           "reel": inspect_level(g["reels"][0]),
           "mouseover": [static(NPROOF, "ProofReadout", "%d,%d" % c) for c in g["centres"]],
           "pitWater": [static(LPROOF, "ProofPitWater", rc) for rc in g["rects"]],
           "surface": [static(NPROOF, "ProofLevelSurface", rc)[:160] for rc in g["rects"]],
           "link": static(NPROOF, "ProofLevelLink", "%d,%d" % g["reels"][0])[:200]}
    if name == "N_natural_pond":
        # the pond's exact stock (read only: classify=false forms nothing): with the pit's dL it must hold the starting total
        br = B.call("jawa/flowworks_body_report", x=150, z=96, classify=False, _answer=True) or {}
        rec["pondBody"] = {k: v for k, v in br.items() if k not in ("operation", "state", "footprint", "cells")}
        cb = B.call("jawa/flowworks_body_report", x=132, z=96, classify=False, _answer=True) or {}
        rec["controlStock"] = (cb.get("body") or {}).get("stock")
    out["rigs"].setdefault(name, []).append(rec)
    return rec


for name in RIGS:
    print(json.dumps(read(name, 0))[:700], flush=True)
done = {n: False for n in RIGS}
t = 0
while t < 9000 and not all(done.values()):
    tick(250)
    t += 250
    for name in RIGS:
        if done[name]:
            continue
        rec = read(name, t)
        if "Levelling: level" in rec["reel"]:
            done[name] = True
            print(json.dumps(rec)[:900], flush=True)
out["levelledAt"] = {n: (out["rigs"][n][-1]["tick"] if done[n] else None) for n in RIGS}
print(json.dumps(out["levelledAt"]), flush=True)
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
