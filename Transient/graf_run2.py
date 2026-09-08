import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    r = rb.call("rimworld/step_game_ticks", {"ticks": 5000})
    print("step:", json.dumps(r)[:300])
    colonists = rb.call("rimworld/list_colonists", {})["colonists"]
    for c in colonists:
        print(c["name"], "mentalState=", c.get("mentalState"), "job=", c.get("job"), "pos=", c.get("position"))
