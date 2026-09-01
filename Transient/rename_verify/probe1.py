import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status", {})
    print("STATUS:", st)
    gi = rb.call("rimworld/get_game_info", {})
    print("GAMEINFO:", gi)
