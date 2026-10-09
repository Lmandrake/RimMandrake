import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc3_slime_map_id.txt").read()); S.call("jawa/set_current_map", mapId=mid); S.quiet()
for d in ("HediffDef/RM_SharedBurden", "ThingDef/RM_SlimeHandRing", "PreceptDef/RUT_Ritual_JoiningWater"):
    g = S.call("jawa/get_defs", defs=d, fields="defName"); print(d, g.get("success"), g.get("foundCount"), g.get("notFound"))
things = S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100"); print("rings", things.get("count", things.get("total")), [(t.get("x"), t.get("z")) for t in (things.get("things") or [])])
ring = (things.get("things") or [{}])[0]
for dx in (): S.call("jawa/spawn_pawn", kindDef="Colonist", x=5+dx, z=7, faction="player", count=1)
cols = [p["id"] for p in (S.call("jawa/list_pawns", limit=100).get("pawns") or []) if p.get("isPlayer")]
print("cols", cols)
r = S.call("jawa/ideo_precept_edit", ideo="Masculine Family", action="add", precept="RUT_Ritual_JoiningWater")
print("precept add", r.get("success"), str(r.get("message"))[:300], r.get("acceptance"))
for c in cols[1:]:
    for n in ("Food", "Rest"): S.call("jawa/pawn_need", pawn=c, action="need", need=n, level=1.0)
h = S.call("jawa/pawn_health", pawn=cols[1], action="add", hediff="Flu", severity=0.6); print("flu", h.get("success"), str(h.get("message"))[:100])
rs = S.call("jawa/ritual_start", ritual="RUT_Ritual_JoiningWater", targetThingId=ring["id"], organizer=cols[1])
print("ritual", json.dumps({k: rs.get(k) for k in rs if k not in ("operation", "state")}, default=str)[:700], flush=True)
S.run(1800)
for c in cols:
    pg = (S.call("jawa/pawn_get", pawn=c).get("pawns") or [{}])[0]
    print(c, [(x["def"], round(x.get("severity") or 0, 2)) for x in pg.get("hediffs", []) if x["def"] in ("Flu", "RM_SharedBurden")])
