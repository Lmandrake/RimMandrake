import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    r = rb.call("rimworld/get_cell_info", {"x": 110, "z": 106})
    print(json.dumps(r["cell"]["things"]))
    for i in range(6):
        s = rb.call("rimworld/step_game_ticks", {"ticks": 2500})
        colonists = rb.call("rimworld/list_colonists", {})["colonists"]
        b = next(c for c in colonists if c["name"] == "Bundy")
        print(i, s.get("status"), s.get("advancedTicks"), "| Bundy:", b.get("mentalState"), b.get("job"), b.get("position"))
