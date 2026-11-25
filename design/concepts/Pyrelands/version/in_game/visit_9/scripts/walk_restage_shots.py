"""The restaged walk save freshly loaded and paused: one capture per station plus tight ones (no tick). Prints each path."""
import json, os, sys, time
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
D = json.load(open(os.path.join(ROOT, "design/concepts/Pyrelands/version/in_game/visit_9/evidence/walk_restage.json")))
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda t, **k: rb.call(t, k)
    c("rimworld/set_time_speed", speed=0); c("jawa/clear_ui")
    print("signs", [(s["title"][:30], s["x"], s["z"]) for s in c("jawa/review_sign", action="list")["signs"]])
    print("storyteller", c("jawa/storyteller_swap")["after"], "camera", c("rimworld/get_camera_state").get("mapPosition"))
    print("pawns", [(q["kindDef"], q["x"], q["z"]) for q in c("jawa/list_pawns", rect="70,18,28,24", limit=50)["pawns"]])
    print("labels", str(c("jawa/review_label", action="list"))[:300])
    tight = [("2t", "ullai", (74, 22, 14, 5)), ("2u", "beast", (79, 27, 15, 6)), ("1t", "front", (18, 18, 12, 10))]
    for k, n, (x, z, w, hh), _ in D["stations"] + [(a, b, r, 0) for a, b, r in tight]:
        c("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + hh // 2)
        c("rimworld/set_camera_zoom", rootSize=8 if len(k) > 1 else 13)
        c("rimworld/frame_cell_rect", x=x, z=z, width=w, height=hh, paddingCells=1); time.sleep(1.2)
        r = c("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=hh, paddingCells=1, rootSize=14, fileName="pw_st_%s_%s" % (k, n.replace(" ", "_")))
        print("SHOT", k, n, r.get("path") or str(r)[:300]); time.sleep(1.2)
    print("tick", c("rimworld/get_game_info")["ticksGame"])
