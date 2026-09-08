"""Spawn a TorchLamp next to RSW_Skarnix24320 (night, dark ambient) and see if it flees."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

TARGET_ID = "RSW_Skarnix24320"
TX, TZ = 203, 210  # its position just read

with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/spawn_thing", {"defName": "TorchLamp", "x": TX + 1, "z": TZ})
    print("spawn torch:", json.dumps(r)[:400])

    lp = rb.call("jawa/list_pawns", {})
    mine = {p["id"]: (p["x"], p["z"]) for p in lp["pawns"] if p["kind"] in ("RSW_Cindermare", "RSW_Skarnix")}
    print("positions right after torch spawn:", mine)
