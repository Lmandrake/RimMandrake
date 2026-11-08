"""capture.py <colonist> <x> <z> -- right-click the pit occupant at x,z with the colonist selected, take the Capture option,
play in slices and report the occupant's state (guest status, downed, position) and the colonist's job; shots at the end."""
import json
import sys
import time

import fwb

B = fwb.FW()
who, x, z = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cols = [p for p in (B.call("jawa/pawn_census", faction="player") or {}).get("pawns") or [] if p.get("isColonist")]
for c in cols:   # the fight is over: everyone undrafted, as a player would
    B.call("jawa/order_pawn", pawnId=c["id"], x=c["x"], z=c["z"], draft=False, waitTicks=0)
B.call("rimworld/clear_selection")
B.call("rimworld/select_pawn", pawnName=who)
r = B.call("rimworld/right_click_cell", x=x, z=z, button="right") or {}
opt = [o for o in r.get("options") or [] if "apture" in (o.get("label") or "")]
print("options", [o.get("label") for o in r.get("options") or []])
if opt:
    e = B.call("rimworld/execute_context_menu_option", optionIndex=opt[0]["index"]) or {}
    print("execute", json.dumps(e, default=str)[:300])
for k in range(int(sys.argv[4]) if len(sys.argv) > 4 else 12):
    B.call("rimworld/play_for", durationMs=3000, speed="Fast", forceRequestedSpeed=True)
    allp = ((B.call("jawa/pawn_census", faction="hostile") or {}).get("pawns") or []) + \
        ((B.call("jawa/pawn_census", faction="player") or {}).get("pawns") or [])
    occ = [p for p in allp if abs(p["x"] - x) <= 2 and abs(p["z"] - z) <= 2 and not p.get("isColonist")]
    me = [p for p in allp if p.get("name") == who]
    print(k, "occ", [(p["name"], p.get("faction"), p.get("guestStatus") or p.get("prisoner") or p.get("isPrisoner"),
                      "DOWN" if p.get("downed") else "", (p.get("job") or {}).get("def")) for p in occ],
          "| me", [(p["x"], p["z"], (p.get("job") or {}).get("def")) for p in me], flush=True)
B.call("rimworld/set_time_speed", speed="Paused")
for root in (20, 11):
    r = B.call("rimworld/screenshot_cell_rect", x=x - 4, z=z - 3, width=9, height=8, paddingCells=1, rootSize=root,
               doNotResetCamera=True, fileName="cap_pit_r%d_%s" % (root, time.strftime("%H%M%S"))) or {}
    print("SHOT", r.get("path"))
