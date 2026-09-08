import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    for i in range(15):
        s = rb.call("rimworld/step_game_ticks", {"ticks": 2500})
        colonists = rb.call("rimworld/list_colonists", {})["colonists"]
        p = next(c for c in colonists if c["name"] == "Jackalope")
        cell = rb.call("rimworld/get_cell_info", {"x": 111, "z": 117})
        things = [t["defName"] for t in cell["cell"]["things"]]
        print(i, s.get("advancedTicks"), "endTicksGame=", s.get("endTicksGame"), "| job=", p.get("job"), "mentalState=", p.get("mentalState"), "| cell(111,117):", things)
        if any("Graffiti" in t for t in things):
            print("MARK FOUND")
            break
        if p.get("mentalState") is None:
            print("SPREE ENDED without a mark")
            break
