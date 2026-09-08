"""One more step + position re-check for the light-aversion test."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token, timeout=90.0) as rb:
    r = rb.call("rimworld/step_game_ticks", {"ticks": 2500})
    print("step:", json.dumps(r)[:300])
    lp = rb.call("jawa/list_pawns", {})
    mine = {p["id"]: (p["x"], p["z"]) for p in lp["pawns"] if p["kind"] in ("RSW_Cindermare", "RSW_Skarnix")}
    print("positions:", mine)
