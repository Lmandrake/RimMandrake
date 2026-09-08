import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    for i in range(10):
        s = rb.call("rimworld/step_game_ticks", {"ticks": 2500})
        colonists = rb.call("rimworld/list_colonists", {})["colonists"]
        b = next(c for c in colonists if c["name"] == "Bundy")
        cell = rb.call("rimworld/get_cell_info", {"x": 109, "z": 106})
        filth = [t["defName"] for t in cell["cell"]["things"] if "Graffiti" in t["defName"] or "Filth" in t.get("className","")]
        print(i, s.get("advancedTicks"), "| job=", b.get("job"), "mentalState=", b.get("mentalState"), "| wall-cell filth:", filth)
        if b.get("mentalState") is None:
            print("SPREE ENDED")
            break
