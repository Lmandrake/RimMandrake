import sys; sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("game_info:", rb.call("rimworld/get_game_info", {}))
    try:
        print("list_pawns:", rb.call("jawa/list_pawns", {}))
    except Exception as e:
        print("list_pawns err:", e)
