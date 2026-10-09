import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
for attempt in range(3):
    mid = S.biome_map(114480, "RM_LongShade", size=200, keeper=(5, 5))
    S.quiet()
    h = S.call("jawa/map_comp_read", comp="CrawlerHull", members="hullCenter").get("values")
    p = S.call("jawa/list_things", defName="RM_LongShadeCleanPatch", limit=50)
    ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
    c = collections.Counter(x.get("kind") for x in ps)
    print(attempt, mid, h, "patches", p.get("count", p.get("total")), "pawns", dict(c), flush=True)
    if h and "-1000" not in h.get("hullCenter", "-1000"):
        open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid)); break
    S.drop_map(mid, 114480)
