import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
try:
    old = int(open("Transient/belt_acc2_ls_map_id.txt").read()); S.drop_map(old, 114480)
except Exception: pass
mid = S.biome_map(114480, "RM_GelatinousSlime", size=100, keeper=(30, 30))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
ring = (S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100").get("things") or [{}])[0]
print("ring", ring.get("id"), ring.get("x"), ring.get("z"))
S.call("jawa/clear_area", rect="%d,%d,10,10" % (ring["x"] - 5, ring["z"] - 5)) if False else None
ids = []
for dx in (-3, -1, 1, 3):
    r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=ring["x"] + dx, z=max(2, ring["z"] + 3), faction="player", count=1)
    if r.get("pawns"): ids.append(r["pawns"][0]["id"])
print("colonists", ids)
pg = (S.call("jawa/pawn_get", pawn=ids[0]).get("pawns") or [{}])[0]
print("pawn keys with ideo:", {k: pg[k] for k in pg if "ideo" in k.lower()})
