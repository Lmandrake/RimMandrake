import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("ticks:", gi.get("ticksGame"))
    # which save is loaded? experimental had the ship; check for the engine
    e = rb.call("jawa/list_things", {"defName": "GravEngine", "limit": 3})
    th = e.get("things", [])
    print("GravEngine on current map:", len(th), th[:1])
