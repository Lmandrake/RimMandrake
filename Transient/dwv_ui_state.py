import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for tool, args in [("rimworld/get_ui_state", {}), ("jawa/load_stall_probe", {}), ("rimworld/get_game_info", {})]:
        try:
            r = rb.call(tool, args)
            print(tool, "->", json.dumps(r)[:1000])
        except Exception as e:
            print(tool, "EXC:", str(e)[:300])
        print()
