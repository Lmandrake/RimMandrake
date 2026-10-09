import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = S.biome_map(114480, "RM_GelatinousSlime", size=100, keeper=(5, 7))
open("Transient/belt_acc3_slime_map_id.txt", "w").write(str(mid)); S.quiet()
for dx in (2, 4, 6): S.call("jawa/spawn_pawn", kindDef="Colonist", x=5+dx, z=7, faction="player", count=1)
cols = [p["id"] for p in (S.call("jawa/list_pawns", limit=100).get("pawns") or []) if p.get("isPlayer")]
ideo = (S.call("jawa/pawn_get", pawn=cols[0]).get("pawns") or [{}])[0].get("ideo"); print("cols", cols, "ideo", ideo)
things = S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100"); ring = (things.get("things") or [{}])[0]; print("ring", ring.get("id"), ring.get("x"), ring.get("z"))
print("precept add", S.call("jawa/ideo_precept_edit", ideo=ideo, action="add", precept="RUT_Ritual_JoiningWater").get("success"))
for c in cols[1:]:
    for n in ("Food", "Rest"): S.call("jawa/pawn_need", pawn=c, action="need", need=n, level=1.0)
rs = S.call("jawa/ritual_start", ritual="RUT_Ritual_JoiningWater", targetThingId=ring["id"], organizer=cols[1])
print("ritual", rs.get("success"), rs.get("started"), rs.get("message")); print(json.dumps(rs.get("details") or rs.get("stack") or {k:v for k,v in rs.items() if k not in ("operation","state")}, default=str)[:2200])

if rs.get("success"):
    for h in ("Cut","Scar","Gunshot","Malaria"):
        r=S.call("jawa/pawn_health", pawn=cols[1], action="add", hediff=h, severity=3); print("hediff", h, r.get("success"), str(r.get("message"))[:80])
        if r.get("success"): break
    S.run(2600)
    for c in cols:
        pg = (S.call("jawa/pawn_get", pawn=c).get("pawns") or [{}])[0]
        print(c, [(x["def"], round(x.get("severity") or 0, 2)) for x in pg.get("hediffs", [])])
