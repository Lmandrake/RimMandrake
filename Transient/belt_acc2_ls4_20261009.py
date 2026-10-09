import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = S.biome_map(114480, "RM_LongShade", size=100, keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
r = S.call("jawa/shadegrid_read", cells="50,50;10,10")
print(json.dumps({k: v for k, v in r.items() if k not in ("operation", "state")}, default=str)[:1500])
cells = ";".join("%d,%d" % (x, z) for x in range(2, 100, 7) for z in range(2, 100, 7))
rows = S.call("jawa/shadegrid_read", cells=cells[:])
print(list(rows.keys()))
cs = rows.get("cells") or []
print(len(cs), json.dumps(cs[:2], default=str)[:400])
