import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DROID_ID = "RSW_DW_Race_guy762_DroidRace_T3series37049"
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/step_game_ticks", {"ticks": 60})
    print("step:", json.dumps(r)[:300])
    r = rb.call("jawa/pawn_get", {"pawn": DROID_ID})
    p = r["pawns"][0]
    print("hediffs after tick step:", [h.get("def") for h in p.get("hediffs", [])])
