import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
time.sleep(30)  # settle window
with RimBridge(host, port, token) as rb:
    wi = rb.call("jawa/world_info_get", {})
    print("world_info:", json.dumps(wi)[:400])
    st = rb.call("jawa/world_stats", {})
    print("tiles:", st.get("totalTiles"), "| water%:", st.get("waterPct") or st.get("waterPercent"))
