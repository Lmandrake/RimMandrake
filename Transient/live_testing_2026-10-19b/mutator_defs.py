"""get_defs for the 19 ported TileMutatorDefs + 4 reused + 3 landmarks. python.exe mutator_defs.py <out.json>"""
import json, os, sys
UT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "RimMandrake", "Utils")
sys.path.insert(0, UT)
from rimbridge_client import RimBridge, resolve_endpoint
NEW = ["RM_AgariluxPrimeSprout", "RM_AmbientRadiation", "RM_AncientBloodRainVent", "RM_AncientFreezingVent",
       "RM_AncientGrayPallVent", "RM_SwarmHiveNests", "RM_DerelictClusters", "RM_EdibleAirborneMicrofungi",
       "RM_OllathrixNest", "RM_GeothermalHotspots", "RM_GiantFossils", "RM_LocustPlagues", "RM_MagmaVents",
       "RM_MagmaticQuagmire", "RM_MoldyEnvironment", "RM_QuicksandPits", "RM_TarLakes",
       "RSW_WildTattooinePlants", "RSW_WildGalacticPlants"]
REUSED = ["RSW_SarlaccLair", "RSW_DeadSarlaccCave"]
LANDMARKS = ["RM_TarLakes", "RM_MagmaticQuagmire", "RM_QuicksandPits", "RSW_Sarlacc", "RSW_DeadSarlacc"]
pairs = ["TileMutatorDef/" + d for d in NEW + REUSED] + ["LandmarkDef/" + d for d in LANDMARKS]
h, p, t = resolve_endpoint()
with RimBridge(h, p, t, timeout=120.0) as rb:
    r = rb.call("jawa/get_defs", {"defs": ";".join(pairs), "fields": "workerClass,label,chanceOnNonLandmarkTile"})
rows = [{k: d.get(k) for k in ("requested", "found", "packageId", "fields")} for d in r.get("defs") or []]
out = {"message": r.get("message"), "notFound": r.get("notFound"), "malformed": r.get("malformed"), "rows": rows}
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
print(out["message"], "notFound=", out["notFound"], "malformed=", out["malformed"])
for x in rows:
    print(x["requested"], x["found"], x["packageId"], (x.get("fields") or {}).get("workerClass"))
