import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
def brief(x,n=260): return json.dumps(x)[:n]
with RimBridge(h,p,t) as rb:
    print("abandon(force):", brief(rb.call("jawa/settlement_remove", {"mode":"settlement","settlementId":255,"force":True,"dryRun":False})))
    gi=rb.call("rimworld/get_game_info",{}); print("mapCount:", gi.get("mapCount"))
    mi=rb.call("jawa/map_info",{}); print("current map tile:", mi.get("tile"), "| biome:", mi.get("mapBiome"), "| size:", mi.get("sizeX"), mi.get("sizeZ"))
