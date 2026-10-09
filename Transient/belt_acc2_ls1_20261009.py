import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
out = {}
mid = S.biome_map(114480, "RM_LongShade", keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
mi = S.call("jawa/map_info"); out["map"] = {k: mi.get(k) for k in ("mapId", "mapBiome", "sizeX", "sizeZ")}
r = S.call("jawa/map_comp_read", comp="CrawlerHull", members="hullCenter,width,height,entered,towStartTick,towed,towTicks")
out["hull"] = (r.get("success"), r.get("values"), r.get("missing"), str(r.get("message"))[:150])
r = S.call("jawa/list_things", defName="RM_LongShadeCleanPatch", limit=50)
out["patches"] = (r.get("count", r.get("total")), [(t.get("x"), t.get("z")) for t in (r.get("things") or [])][:10])
r = S.call("jawa/list_pawns", limit=200)
ps = r.get("pawns") or []
import collections
out["pawns"] = dict(collections.Counter(p.get("kind") for p in ps))
out["lairers"] = [(p["kind"], p["x"], p["z"]) for p in ps if p.get("kind") in ("RM_Mirrak", "RM_Gulloth")][:10]
for d in ("HediffDef/RM_TollokInfestation", "ThingDef/RM_LureAwning", "ThingDef/RM_Harrok", "IncidentDef/RM_ShadeStampede", "IncidentDef/RUT_JawaReturnTow"):
    g = S.call("jawa/get_defs", defs=d, fields="defName"); out["def " + d] = (g.get("success"), g.get("foundCount"), g.get("notFound"))
print(json.dumps(out, default=str)[:3500])
