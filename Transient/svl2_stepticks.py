import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    before = rb.call("rimworld/get_game_info", {})
    print("BEFORE_TICKS", before.get("ticksGame"))
    r = rb.call("rimworld/step_game_ticks", {"ticks": 300})
    print("STEP", json.dumps(r)[:800])
    after = rb.call("rimworld/get_game_info", {})
    print("AFTER_TICKS", after.get("ticksGame"))
    ci = rb.call("rimworld/get_cell_info", {"x": 0, "z": 0})
    print("PAUSED_STATE", json.dumps(ci.get("state"))[:400])
