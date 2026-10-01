"""Sand-swim live state reads on an RM_Stillsand quicktest. python.exe, cwd = this folder."""
import json, sys, time
from bx import call

OUT = {}
def log(k, v):
    OUT[k] = v
    print(k, json.dumps(v, default=str)[:600], flush=True)
    json.dump(OUT, open("st_sandswim.json", "w"), indent=1, default=str)

def hediffs(pid):
    r = call("jawa/pawn_get", {"pawn": pid})
    ps = r.get("pawns") or []
    if not ps:
        return None
    p = ps[0]
    return {"hediffs": [h.get("def") for h in (p.get("hediffs") or [])], "pos": p.get("position")}

def pawns():
    r = call("jawa/list_pawns", {"limit": 400, "includeHealth": True, "includeCorpses": True})
    return r.get("pawns") or []

def step(n):
    return call("rimworld/step_game_ticks", {"ticks": n}, 300).get("ticksGame")

def spawn(kind, x, z, faction, count=1):
    r = call("jawa/spawn_pawn", {"kindDef": kind, "x": x, "z": z, "faction": faction, "count": count})
    return [p.get("id") for p in (r.get("pawns") or []) if p.get("ok")], r.get("message")

def paint(x, z, w, h, t):
    call("jawa/destroy_batch", {"rects": f"{x},{z},{w},{h}", "categories": "Plant,Item,Building,Filth"})
    return call("jawa/set_terrain", {"x": x, "z": z, "terrainDef": t, "width": w, "height": h}).get("success")

phase = sys.argv[1] if len(sys.argv) > 1 else "all"
call("rimworld/execute_debug_action", {"path": "Actions\\Destroy hostile pawns"})

# sites: A sand (mech test), C gravel control, B sand (kill signs)
log("paint", {"A": paint(15, 15, 30, 30, "Sand"), "C": paint(15, 200, 30, 30, "Gravel"), "B": paint(195, 15, 40, 30, "Sand")})
vA, m = spawn("RM_Vekka", 30, 30, "none"); vC, m2 = spawn("RM_Vekka", 30, 215, "none")
log("spawn_vekkas", {"A": vA, "C": vC, "msg": [m, m2]})
step(180)
log("p1_terrain", {"A_sand": hediffs(vA[0]), "C_gravel": hediffs(vC[0])})

r = call("jawa/damage", {"damageDef": "Blunt", "amount": 1, "thingId": vA[0]})
log("p2_damage_call", {"success": r.get("success"), "msg": r.get("message")})
step(5)
log("p2_after_hit", hediffs(vA[0]))
step(1500)
log("p2_after_1500", hediffs(vA[0]))

# mech immunity: player militor beside each vekka, both vekkas manhunter
mA, _ = spawn("Mech_Militor", 33, 30, "player"); mC, _ = spawn("Mech_Militor", 33, 215, "player")
log("spawn_mechs", {"A": mA, "C": mC})
for v in (vA[0], vC[0]):
    r = call("jawa/pawn_mental", {"pawn": v, "action": "start", "state": "ManhunterPermanent"})
    log("manhunter_" + v, {"success": r.get("success"), "msg": r.get("message")})
ids = set(vA + vC + mA + mC)
for i in range(8):
    step(250)
    snap = {p["id"]: {"hp": p.get("health"), "x": p.get("x"), "z": p.get("z"), "dead": p.get("dead"), "downed": p.get("downed")} for p in pawns() if p["id"] in ids}
    snap["vA_hediffs"] = hediffs(vA[0])
    log(f"p3_t{i}", snap)

# kill signs: site B
vB, _ = spawn("RM_Vekka", 205, 30, "none")
mu, _ = spawn("Muffalo", 212, 30, "player", 2)
r = call("jawa/pawn_mental", {"pawn": vB[0], "action": "start", "state": "ManhunterPermanent"})
log("siteB", {"vekka": vB, "muffalo": mu, "manhunter": r.get("success"), "msg": r.get("message")})
for i in range(12):
    step(250)
    ps = {p["id"]: p for p in pawns()}
    dead = [m for m in mu if ps.get(m, {}).get("dead") or m not in ps]
    log(f"p4_t{i}", {"dead": dead, "vB": hediffs(vB[0]), "mu": {m: (ps.get(m) or {}).get("health") for m in mu}})
    if dead:
        break
th = call("jawa/list_things", {"group": "Filth", "limit": 500})
fl = [t for t in (th.get("things") or []) if t.get("def") in ("RM_Filth_DisturbedSand", "RM_Filth_DragMark")]
log("p4_filth", fl[:20])
log("p4_letters", call("jawa/letter_list", {}))
print("DONE")
