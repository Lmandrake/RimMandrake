import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
try: S.drop_map(int(open("Transient/belt_acc3_slime_map_id.txt").read()), 114480)
except Exception as e: print("drop", e)
mid = S.biome_map(114480, "RM_GelatinousSlime", size=100, keeper=(50, 50))
open("Transient/belt_acc3_slime_map_id.txt", "w").write(str(mid)); S.quiet()
ring = (S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100").get("things") or [{}])[0]; rx, rz = ring["x"], ring["z"]; print("ring", ring["id"], rx, rz)
S.call("jawa/kill_hostiles")
cols = []
for dx in (1, 2, 3):
    r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=rx+dx, z=rz+2, faction="player", count=1); cols += [p["id"] for p in r.get("pawns") or []]
ideo = (S.call("jawa/pawn_get", pawn=cols[0]).get("pawns") or [{}])[0].get("ideo")
S.call("jawa/ideo_precept_edit", ideo=ideo, action="add", precept="RUT_Ritual_JoiningWater")
for c in cols:
    for n in ("Food", "Rest"): S.call("jawa/pawn_need", pawn=c, action="need", need=n, level=1.0)
h = S.call("jawa/pawn_health", pawn=cols[0], action="add", hediff="Asthma", severity=0.8); print("asthma", h.get("success"), str(h.get("message"))[:100])
rs = S.call("jawa/ritual_start", ritual="RUT_Ritual_JoiningWater", targetThingId=ring["id"], organizer=cols[0]); print("ritual", rs.get("success"), rs.get("started"), rs.get("participants"), rs.get("message"), flush=True)
def show(tag):
    print(tag)
    for c in cols:
        pg = (S.call("jawa/pawn_get", pawn=c).get("pawns") or [{}])[0]
        print(" ", c, [(x["def"], round(x.get("severity") or 0, 2)) for x in pg.get("hediffs", []) if x["def"] in ("Asthma","RM_SharedBurden","Gunshot")], flush=True)
show("start")
for i in range(3):
    S.run(1000); show("t+%d" % ((i+1)*1000))
