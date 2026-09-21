import sys, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
ep = resolve_endpoint()
rb = RimBridge(host=ep[0], port=ep[1], token=ep[2], timeout=60)
rb.connect()
def hawks():
    ps = rb.call("jawa/list_pawns", {})["pawns"]
    return {p["id"]: (p["x"], p["z"]) for p in ps if "FireHawk" in (p.get("kind") or "")}
H = hawks()
target = "RUT_FireHawk68310"
for hid in (target, "RUT_FireHawk68311"):
    rb.call("jawa/set_pawn_rotation", {"pawnId": hid, "dir": "south", "lockRotation": True})
shots = []
for tag in ("A", "B", "C"):
    pos = hawks()[target]
    rb.call("rimworld/jump_camera_to_cell", {"x": pos[0], "z": pos[1]})
    rb.call("rimworld/frame_cell_rect", {"x": pos[0]-3, "z": pos[1]-3, "width": 7, "height": 7, "paddingCells": 0})
    time.sleep(0.8)
    r = rb.call("rimworld/take_screenshot", {"fileName": f"flapzoom_{tag}"})
    shots.append((tag, pos, r.get("path")))
    if tag != "C":
        rb.call("rimworld/step_game_ticks", {"ticks": 12})
for s in shots: print(s)
