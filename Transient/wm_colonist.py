import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    mi = rb.call("jawa/map_info", {})
    print("MAP_INFO:", json.dumps(mi)[:700]); print()
    st = rb.call("rimbridge/get_bridge_status", {})
    s=st.get("state",{})
    print("currentMapIndex:", s.get("currentMapIndex"), "currentMapId:", s.get("currentMapId"), "mapCount:", s.get("mapCount"))
