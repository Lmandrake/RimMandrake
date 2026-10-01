"""Sand-swim: forced AttackMelee on a mech (immunity) vs flesh controls (strike + take signs)."""
import json
from bx import call
from st_sandswim_lib import *  # noqa

OUT = {}
def log(k, v):
    OUT[k] = v
    print(k, json.dumps(v, default=str)[:700], flush=True)
    json.dump(OUT, open("st2.json", "w"), indent=1, default=str)

def inj(pid):
    for p in pawns():
        if p["id"] == pid:
            hp = p.get("health") or {}
            return {"dead": p.get("dead"), "downed": p.get("downed"), "x": p.get("x"), "z": p.get("z"),
                    "inj": [h["def"] + "@" + str(h.get("partLabel")) for h in hp.get("hediffs", [])]}
    return "absent"

def order(v, t):
    r = call("jawa/ordered_job", {"pawnId": v, "jobDef": "AttackMelee", "targetAId": t})
    return {k: r.get(k) for k in ("success", "accepted", "message", "interruptibleBefore")}

log("paint", paint(15, 15, 30, 40, "Sand"))
vM, _ = spawn("RM_Vekka", 22, 22, "none"); mech, _ = spawn("Mech_Militor", 26, 22, "player")
vF, _ = spawn("RM_Vekka", 22, 34, "none"); hare, _ = spawn("Hare", 26, 34, "none")
vL, _ = spawn("RM_Vekka", 22, 46, "none"); chick, _ = spawn("Chicken", 26, 46, "player")
log("spawned", {"vM": vM, "mech": mech, "vF": vF, "hare": hare, "vL": vL, "chick": chick})
step(200)
log("pre", {"vM": hediffs(vM[0]), "vF": hediffs(vF[0]), "vL": hediffs(vL[0]), "mech": inj(mech[0])})
for i in range(6):
    o = {"mech": order(vM[0], mech[0]), "hare": order(vF[0], hare[0]), "chick": order(vL[0], chick[0])}
    step(100)
    log(f"t{i}", {"orders": o, "vM": hediffs(vM[0]), "mech": inj(mech[0]), "vF": hediffs(vF[0]), "hare": inj(hare[0]),
                  "vL": hediffs(vL[0]), "chick": inj(chick[0])})
step(300)
th = call("jawa/list_things", {"group": "Filth", "limit": 2000})
fl = [{k: t.get(k) for k in ("def", "x", "z")} for t in (th.get("things") or []) if str(t.get("def")).startswith("RM_Filth")]
log("filth", fl[:30])
lt = call("jawa/letter_list", {})
log("letters", [((l.get("label") or {}).get("RawText"), l.get("arrivalTick")) for l in lt.get("letters", [])])
print("DONE")
