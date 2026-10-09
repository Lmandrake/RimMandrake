import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
for d in ("Turret_MiniTurret","Turret_Mortar"):
    for t in S.call("jawa/list_things", defName=d, rect="0,0,100,100", limit=20).get("things") or []:
        r = S.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t["x"], t["z"]), categories="Building"); print(d, t["x"], t["z"], r.get("success"), str(r.get("message"))[:60])
ring = (S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100").get("things") or [{}])[0]; rx, rz = ring["x"], ring["z"]
old = [p["id"] for p in S.call("jawa/list_pawns", limit=100).get("pawns") or [] if p.get("isPlayer")]
cols = []
for dx in (1, 2, 3):
    r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=rx+dx, z=rz-2, faction="player", count=1); cols += [p["id"] for p in r.get("pawns") or []]
for c in cols:
    for n in ("Food", "Rest"): S.call("jawa/pawn_need", pawn=c, action="need", need=n, level=1.0)
print("asthma", S.call("jawa/pawn_health", pawn=cols[0], action="add", hediff="Asthma", severity=0.8).get("success"))
S.call("jawa/lord_clear") if False else None
rs = S.call("jawa/ritual_start", ritual="RUT_Ritual_JoiningWater", targetThingId=ring["id"], organizer=cols[0]); print("ritual", rs.get("success"), rs.get("participants"), rs.get("message"), flush=True)
def show(tag):
    print(tag)
    for c in cols:
        pg = (S.call("jawa/pawn_get", pawn=c).get("pawns") or [{}])[0]
        print(" ", c, [(x["def"], round(x.get("severity") or 0, 2)) for x in pg.get("hediffs", []) if x["def"] in ("Asthma","RM_SharedBurden","Gunshot")], flush=True)
show("start")
for i in range(3):
    S.run(1000); show("t+%d" % ((i+1)*1000))
