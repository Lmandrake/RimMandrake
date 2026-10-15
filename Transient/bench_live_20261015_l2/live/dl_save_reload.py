"""L2 one-off: DL_save_reload_bowl_identical (POND_ELEVATION_BUILD_LAKES_RUN_DEEP owed row).
Run from the export root with python.exe AFTER deep_lake_proof.py on the same map (the painted lake still stands).
Same proof settings as deep_lake_proof; drain to 0.25 -> SHAPE A -> save new slot -> load it -> SHAPE B; A == B.
Saves folder stat-diffed: exactly one new file, none changed. Settings restored."""
import json, os, sys, time
sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar")
sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
sys.path.insert(0, "src/RimMandrake/Utils")
import proof_hose as PH
import deep_lake_proof as DL
import test_site_saves as TSS

SAVES = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"
NAME = "RM_L2_deeplake_reload_check"
mid, out = sys.argv[1], sys.argv[2]
B = PH.PB()
S_FW = DL.S_FW


def lake(a):
    r = B.call("jawa/static_call", type=DL.PROOF_TYPE, method="ProofDeepLake", args=a) or {}
    t = str(r.get("result") or r.get("message") or r.get("error") or "")
    return (DL.parse(t) if r.get("success") is True else {}), t


def sget(f):
    return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")


def sset(f, v):
    return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))


SET = (("deepBedsEnabled", True), ("deepBedCellsPerLevel", 1), ("deepBedMaxDepth", 20), ("drainableLakeMaxCells", 40000),
       ("pondBedHollowEnabled", True), ("recessionEnabled", True), ("refillWaitsForOccupants", False))
before = {f: sget(f) for f, _ in SET}
res = {"mid": mid, "settings_before": before}
try:
    for f, v in SET:
        sset(f, v)
    res["stock"] = lake("stock;%s;%s" % (mid, DL.DRAIN_TO))[1]
    a, ta = lake("shape;" + mid)
    res["shapeA"] = ta
    s0 = TSS.saves_stat(SAVES)
    res["save"] = TSS.save_site(B.call, NAME, SAVES)
    s1 = TSS.saves_stat(SAVES)
    res["saves_diff"] = {"new": sorted(set(s1) - set(s0)), "changed": [f for f in s0 if s1.get(f) != s0[f]]}
    res["load"] = TSS.load_site(B.call, "calm", name=NAME, check=False)
    time.sleep(2)
    b, tb = lake("shape;" + mid)
    res["shapeB"] = tb
    keys = sorted(set(a) | set(b))
    diff = {k: (a.get(k), b.get(k)) for k in keys if a.get(k) != b.get(k)}
    ok = bool(a) and bool(b) and not diff and res["load"].get("load_s") is not None
    res["row"] = {"id": "DL_save_reload_bowl_identical", "status": "PASS" if ok else ("FAIL" if a and b else "UNMEASURED"),
                  "class": "MOD", "diff": diff, "keys": len(keys)}
finally:
    for f, v in before.items():
        if v is not None:
            sset(f, v)
    res["settings_restored"] = {f: sget(f) for f, _ in SET}
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)
print(json.dumps(res.get("row"), default=str))
print("A:", res.get("shapeA", "")[:300])
print("B:", res.get("shapeB", "")[:300])
