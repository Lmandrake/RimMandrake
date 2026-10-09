import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc3_illisk_map_id.txt").read()); S.drop_map(old, 114480)
orig = S.call("jawa/world_tile_get", tiles="114480")["tiles"][0]["biome"]; print("orig", orig)
S.call("jawa/world_tile_set", tiles="114480", biome="RM_Greentide", temperature=22); S.call("jawa/world_commit")
mid = S.biome_map(114480, "RM_Greentide", size=200, keeper=(5, 5))
open("Transient/belt_acc3_illisk_map_id.txt", "w").write(str(mid))
ps = S.call("jawa/list_pawns", limit=500).get("pawns") or []
print(collections.Counter(p["kind"] for p in ps).most_common(15))
ill = [(p["x"], p["z"]) for p in ps if p["kind"] == "RM_Illisk"]
print("illisk", len(ill), sorted(ill)[:30])
