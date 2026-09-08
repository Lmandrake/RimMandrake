import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
def brief(x,n=280): return json.dumps(x)[:n]
with RimBridge(h,p,t) as rb:
    print("dry run:", brief(rb.call("jawa/settlement_remove", {"mode":"settlement","settlementId":255,"dryRun":True})))
    print("apply  :", brief(rb.call("jawa/settlement_remove", {"mode":"settlement","settlementId":255,"dryRun":False})))
    gi=rb.call("rimworld/get_game_info",{}); print("mapCount now:", gi.get("mapCount"))
    st=rb.call("rimbridge/get_bridge_status",{}).get("state",{})
    print("currentMapIndex:", st.get("currentMapIndex"), "mapCount:", st.get("mapCount"))
    mi=rb.call("jawa/map_info",{}); print("current map tile:", mi.get("tile"), "biome:", mi.get("mapBiome"))
