import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        info = rb.call("jawa/world_info_get", {})
        print("WORLD_INFO", json.dumps(info)[:3000])
    except Exception as e:
        print("world_info_get ERROR", e)
    try:
        gi = rb.call("rimworld/get_game_info", {})
        print("GAME_INFO", json.dumps(gi)[:3000])
    except Exception as e:
        print("get_game_info ERROR", e)
