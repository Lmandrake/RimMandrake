import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("BEFORE", json.dumps(info)[:600])
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Leave settlement now (test harness, tears down this map)"})
    print("LEAVE_RESULT", json.dumps(r)[:2500])
