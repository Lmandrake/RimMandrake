import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
time.sleep(5)
with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("alive, ticks:", gi.get("ticksGame"), "speed:", gi.get("timeSpeed", "?"))
    p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 6})
    for c in p.get("pawns", []):
        print(c.get("id"), c.get("name") or c.get("label"), "at", c.get("x"), c.get("z"), "| job:", c.get("job") or c.get("currentJob"))
