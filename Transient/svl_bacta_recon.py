import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("GAME_INFO", json.dumps(info)[:600])

    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    print("COLONISTS", json.dumps(cols)[:3000])
