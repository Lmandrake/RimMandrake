import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc3_slime_map_id.txt").read())
S.drop_map(old, 114480)
for attempt, size in enumerate((250, 250, 200)):
    mid = S.biome_map(114480, "RM_LongShade", size=size, keeper=(5, 5))
    open("Transient/belt_acc3_tow_map_id.txt", "w").write(str(mid))
    r = S.call("jawa/map_comp_read", comp="CrawlerHull", members="hullCenter,width,height,entered,towStartTick,towed,towTicks")
    print(attempt, size, mid, r.get("success"), r.get("values"), flush=True)
    hc = (r.get("values") or {}).get("hullCenter")
    if hc and "-1000" not in str(hc) and "(-1" not in str(hc) and str(hc) != "(-1000, -1000, -1000)": break
    S.drop_map(mid, 114480)
