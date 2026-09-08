import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    for i in range(4):
        r = rb.call("rimworld/step_game_ticks", {"ticks": 2500})
        print("step", i, r.get("status"), r.get("advancedTicks"))
        colonists = rb.call("rimworld/list_colonists", {})["colonists"]
        b = next(c for c in colonists if c["name"] == "Bundy")
        print("  Bundy:", b.get("mentalState"), b.get("job"), b.get("position"))
