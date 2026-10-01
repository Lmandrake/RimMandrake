"""Round 2: FIX2 oorrik spawn, FIX3 funnel on a sand-swim take, FIX4 soorrak 5000 ticks with job list."""
import json, sys
from bx import call
from st_sandswim_lib import step, pawns, spawn, paint, hediffs
OUT = {}
def log(k, v):
    OUT[k] = v; print(k, json.dumps(v, default=str)[:600], flush=True)
    json.dump(OUT, open("t1.json", "w"), indent=1, default=str)
def st(pid):
    for p in pawns():
        if p["id"] == pid: return {"dead": p.get("dead"), "x": p.get("x"), "z": p.get("z")}
    return "absent"
def order(v, t):
    r = call("jawa/ordered_job", {"pawnId": v, "jobDef": "AttackMelee", "targetAId": t})
    return r.get("success"), r.get("message")
# FIX2
ids, msg = spawn("RM_Oorrik", 200, 40, "none", 3); log("oorrik", {"ids": ids, "msg": msg})
# FIX4 soorrak
so, msg = spawn("RM_Soorrak", 200, 200, "none", 6); log("soorrak_spawn", {"ids": so, "msg": msg})
# FIX3 funnel: three vekka->chicken pairs on sand
log("paint", paint(15, 15, 30, 50, "Sand"))
pairs = []
for i, z in enumerate((22, 34, 46)):
    v, _ = spawn("RM_Vekka", 22, z, "none"); c, _ = spawn("Chicken", 26, z, "player")
    pairs.append((v[0], c[0]))
log("pairs", pairs)
step(200)
log("pre_sub", {v: hediffs(v) for v, c in pairs})
jobs = {}
for i in range(10):
    for v, c in pairs:
        if st(c) not in ("absent",) and not st(c).get("dead"): order(v, c)
    step(500)
    fr = call("jawa/pawn_flight", {"action": "report", "kind": "RM_Soorrak"}, 90)
    rows = fr.get("pawns") or fr.get("results") or []
    jobs[i] = [(r.get("pawn") or r.get("id") or r.get("thingId"), r.get("curJobDef"), r.get("flying")) for r in rows]
    log(f"t{i}", {"chicks": {c: st(c) for v, c in pairs}, "soorrak_jobs": jobs[i]})
th = call("jawa/list_things", {"group": "Filth", "limit": 3000})
fl = [{k: t.get(k) for k in ("def", "x", "z")} for t in (th.get("things") or []) if str(t.get("def")).startswith("RM_Filth")]
log("filth", fl[:40])
lt = call("jawa/letter_list", {})
log("letters", [((l.get("label") or {}).get("RawText") if isinstance(l.get("label"), dict) else l.get("label"), l.get("arrivalTick"), str(l.get("text"))[:300]) for l in lt.get("letters", [])])
log("oorrik_after", {i: st(i) for i in ids})
print("DONE")
