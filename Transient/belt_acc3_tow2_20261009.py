import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
try:
    S.drop_map(int(open("Transient/belt_acc3_slime_map_id.txt").read()), 114480)
except Exception as e: print("drop", e)
fac = S.call("jawa/faction_name_get", limit=200); print("jawa factions", [f.get("defName") or f.get("def") for f in (fac.get("factions") or []) if "Jawa" in json.dumps(f)][:6])
for attempt, size in enumerate((200, 250, 250)):
    mid = S.biome_map(114480, "RM_LongShade", size=size, keeper=(5, 5))
    open("Transient/belt_acc3_tow_map_id.txt", "w").write(str(mid))
    r = S.call("jawa/map_comp_read", comp="CrawlerHull", members="hullCenter,width,height,entered,towStartTick,towed,towTicks")
    print(attempt, size, mid, r.get("values"), flush=True)
    if "-1000" not in str((r.get("values") or {}).get("hullCenter")): break
    S.drop_map(mid, 114480)
