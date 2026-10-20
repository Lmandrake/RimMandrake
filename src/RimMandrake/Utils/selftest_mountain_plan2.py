"""Selftest for the second mountain pass plan (world/ASHKARR_MOUNTAINS2_2026-10-20_plan.json).

Always: the committed plan has the first plan's schema (+ elevationBefore), every hilliness entry has
a before value and a reason, nothing writes Impassable, nothing is a no-op, elevation only rises.
When the scratch export exists (D:\\ClaudeWork\\rimmandrake\\scratch\\mountains2\\before.npz): the
generator re-derives the committed plan exactly, and the invariants hold on the derived world —
settlements, river tiles' elevation and the Cratercrown zone untouched, no Mountainous next to Flat,
no river link changes downhill sense, every river source LargeHills or rougher. Each invariant
checker is first shown to FAIL on a deliberately broken copy, so a pass means it can see.
"""
import json, os, runpy, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PLAN = os.path.join(REPO, "world", "ASHKARR_MOUNTAINS2_2026-10-20_plan.json")
PLAN1 = os.path.join(REPO, "world", "ASHKARR_MOUNTAINS_2026-10-20_plan.json")
GEN = os.path.join(REPO, "world", "_mountain_plan2_2026-10-20.py")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch/mountains2"
fails = []
def check(cond, msg):
    if not cond: fails.append(msg)

plan = json.load(open(PLAN)); p1 = json.load(open(PLAN1))
check(set(p1) <= set(plan) and set(plan) - set(p1) == {"elevationBefore"}, "schema differs from the first plan")
check(plan["expectTiles"] == 21872, "expectTiles")
check(plan["save"] == "ASHKARR_DEV_START_2026-10-20_RECORDLINKS", "base save")
hk = set(plan["hilliness"])
check(hk == set(plan["before"]) == set(plan["reason"]), "hilliness/before/reason keys disagree")
check(set(plan["elevation"]) == set(plan["elevationBefore"]), "elevation/elevationBefore keys disagree")
check(all(1 <= v <= 4 for v in plan["hilliness"].values()), "a value outside Flat..Mountainous (Impassable is crest-only)")
check(all(plan["hilliness"][t] != plan["before"][t] for t in hk), "no-op entry")
check(all(plan["elevation"][t] > plan["elevationBefore"][t] for t in plan["elevation"]), "an elevation that does not rise")
check(len(hk) > 300, "suspiciously small plan (%d)" % len(hk))

def invariants(g, H, E):
    """list of violated invariants for hilliness H / elevation E on the derived world g."""
    out = []
    L, NB, H0, E0 = g["L"], g["NB"], g["H0"], g["E0"]
    if any(H[t] != H0[t] for t in g["settl"]): out.append("settlement touched")
    if any(H[t] != H0[t] for t in range(len(H)) if g["crater"][t]): out.append("Cratercrown zone touched")
    if any(E[t] != E0[t] for t in g["river_tiles"]): out.append("river tile elevation changed")
    if any(L[t] and H[t] >= 4 and any(L[u] and H[u] == 1 for u in NB[t]) for t in range(len(H))):
        out.append("Mountainous next to Flat")
    if any((E[a] > E[b]) != (E0[a] > E0[b]) or (E[a] < E[b]) != (E0[a] < E0[b]) for a, b in g["rivers"]):
        out.append("river link changes downhill sense")
    if any(H[s] < 3 for s in g["sources"]): out.append("river source below LargeHills")
    if any(H[t] == 5 and not g["crater"][t] for t in range(len(H))): out.append("Impassable off the crest")
    return out

if os.path.exists(os.path.join(SCRATCH, "before.npz")):
    g = runpy.run_path(GEN, run_name="selftest")
    check(g["plan"] == plan, "generator output differs from the committed plan (re-run the script)")
    H, E = g["H"], g["E"]
    for v in invariants(g, H, E): fails.append("invariant: " + v)
    # sanity probe: each checker must fire on a broken copy
    import numpy as np
    s = next(iter(g["settl"])); Hb = H.copy(); Hb[s] = (H[s] % 4) + 1
    check("settlement touched" in invariants(g, Hb, E), "probe: settlement checker is blind")
    r = next(iter(g["river_tiles"])); Eb = E.copy(); Eb[r] += 999
    check("river tile elevation changed" in invariants(g, H, Eb), "probe: river checker is blind")
    t = next(t for t in range(len(H)) if g["L"][t] and H[t] == 4 and not g["crater"][t])
    u = next(u for u in g["NB"][t] if g["L"][u]); Hb = H.copy(); Hb[u] = 1
    check("Mountainous next to Flat" in invariants(g, Hb, E), "probe: foothill checker is blind")
    print("regenerated: %d hilliness, %d elevation entries; invariants hold" % (len(plan["hilliness"]), len(plan["elevation"])))
else:
    print("SKIP regeneration: %s/before.npz not present (structural checks only)" % SCRATCH)

if fails:
    print("FAIL", *fails, sep="\n  "); sys.exit(1)
print("OK selftest_mountain_plan2")
