import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status", {})
    tools = None
    names = []
    jawa = [n for n in names if n.startswith("jawa/")]
    ui = rb.call("rimworld/get_ui_state", {})
    print("status:", {k: st.get(k) for k in ("version","gameLoaded","mapCount") if isinstance(st, dict)})
    print("jawa tools:", len(jawa))
    print("programState:", ui.get("programState"), "| hasCurrentGame:", ui.get("hasCurrentGame"))
    print("windows:", ui.get("windows"))
