"""Step ticks after the torch spawn and re-check positions."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token, timeout=60.0) as rb:
    r = rb.call("rimworld/step_game_ticks", {"ticks": 1500})
    print("step:", json.dumps(r)[:300])

    lp = rb.call("jawa/list_pawns", {})
    mine = {p["id"]: (p["x"], p["z"]) for p in lp["pawns"] if p["kind"] in ("RSW_Cindermare", "RSW_Skarnix")}
    print("positions after step:", mine)
