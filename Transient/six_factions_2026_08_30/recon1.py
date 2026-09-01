import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status", {})
    print("STATUS", json.dumps(st)[:600])
    gi = rb.call("rimworld/get_game_info", {})
    print("GAMEINFO", json.dumps(gi)[:800])
    tl = rb.call("rimbridge/list_tools", {}) if True else None
    print("TOOLS_RAW_KEYS", list(tl.keys())[:20] if isinstance(tl,dict) else type(tl))
