import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
out = {}
mid = S.biome_map(114480, "RM_Greentide", keeper=(5, 5))
S.quiet()
try:
    # pool of shallow water 40..59 x 40..51 (20 wide x 12 tall); banks of land either side
    S.call("jawa/clear_area", rect="30,30,40,40")
    S.call("jawa/set_terrain_batch", ops="Soil:30,30,40,40")
    r = S.call("jawa/set_terrain_batch", ops="WaterShallow:40,40,20,12")
    out["terrain"] = (r.get("success"), str(r.get("message"))[:160])
    r = S.call("jawa/spawn_pawn", kindDef="RM_Illisk", x=50, z=46, faction="none", count=10)
    ids = [p["id"] for p in (r.get("pawns") or [])]
    out["spawn"] = (r.get("success"), len(ids), str(r.get("message"))[:120])
    time.sleep(1)
    allp = S.call("jawa/list_pawns", rect="38,38,24,16", includeHealth=True, limit=100).get("pawns") or []
    ill = [p for p in allp if p.get("kind") == "RM_Illisk"]
    out["illisk_in_pool"] = len(ill)
    # A2: a Bullet hit of 20 on one Illisk
    t = ill[0]
    def dmg(tid):
        pg = (S.call("jawa/pawn_get", pawn=tid).get("pawns") or [{}])[0]
        return pg
    pre = dmg(t["id"])
    d = S.call("jawa/damage", damageDef="Bullet", amount=20, thingId=t["id"])
    post = dmg(t["id"])
    out["bullet"] = dict(dmgresp=json.dumps(d, default=str)[:600], hediffs_after=[(h.get("def"), h.get("severity")) for h in post.get("hediffs", [])], dead=post.get("dead"))
    t2 = ill[1]
    d = S.call("jawa/damage", damageDef="Cut", amount=20, thingId=t2["id"])
    post = dmg(t2["id"])
    out["cut"] = dict(dmgresp=json.dumps(d, default=str)[:500], hediffs_after=[(h.get("def"), h.get("severity")) for h in post.get("hediffs", [])], dead=post.get("dead"))
    # A3: Bomb 20 on a third
    t3 = ill[2]
    d = S.call("jawa/damage", damageDef="Bomb", amount=20, thingId=t3["id"])
    post = dmg(t3["id"])
    out["bomb"] = dict(dmgresp=json.dumps(d, default=str)[:500], dead=post.get("dead"), hediffs_after=[(h.get("def"), h.get("severity")) for h in post.get("hediffs", [])])
    print(json.dumps(out, default=str), flush=True)
    # A4: wading colonist, across the pool, 10 (minus dead) illisk present
    c = S.call("jawa/spawn_pawn", kindDef="Colonist", x=50, z=37, faction="player", count=1)["pawns"][0]["id"]
    S.call("jawa/set_draft", pawnId=c, drafted=False)
    for n in ("Food", "Rest"):
        S.call("jawa/pawn_need", pawn=c, action="need", need=n, level=1.0)
    path = []
    o = S.call("jawa/order_pawn", pawnId=c, x=50, z=55, unpause=True, waitTicks=1200, undraftAfter=True)
    out["wade_order"] = json.dumps(o, default=str)[:1400]
    pg = (S.call("jawa/pawn_get", pawn=c).get("pawns") or [{}])[0]
    out["wade_end"] = dict(pos=pg.get("position") or (pg.get("x"), pg.get("z")), dead=pg.get("dead"), downed=pg.get("downed"), hediffs=[(h.get("def"), h.get("severity")) for h in pg.get("hediffs", [])])
    allp = S.call("jawa/list_pawns", rect="30,30,40,30", limit=100).get("pawns") or []
    out["illisk_alive_after"] = len([p for p in allp if p.get("kind") == "RM_Illisk" and not p.get("dead")])
finally:
    S.call("jawa/set_terrain_batch", ops="Soil:40,40,20,12")
    S.drop_map(mid, 114480)
print(json.dumps(out, default=str))
