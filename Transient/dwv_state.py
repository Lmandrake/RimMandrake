import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("game_info:", json.dumps(rb.call("rimworld/get_game_info", {}))[:800])
    try:
        print("list_pawns:", json.dumps(rb.call("jawa/list_pawns", {}))[:800])
    except Exception as e:
        print("list_pawns err:", e)
