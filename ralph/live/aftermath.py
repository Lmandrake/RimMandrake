"""aftermath.py -- the story's end on the current map: the raider left in the pit, as the player meets him.

  python.exe ralph/live/aftermath.py <pitX> <pitZ> [colonistName]

Prints: the pit's occupants with health, the occupant's inspect string, and the right-click options a colonist gets on him
from where it stands (the vanilla click path), then shots of the pit at root 20 and root 11.
"""
import json
import sys
import time

import fwb

B = fwb.FW()
px, pz = int(sys.argv[1]), int(sys.argv[2])
who = sys.argv[3] if len(sys.argv) > 3 else None
cen = B.call("jawa/pawn_census", faction="hostile", includeDead=False) or {}
occ = [p for p in cen.get("pawns") or [] if abs(p["x"] - px) <= 3 and abs(p["z"] - pz) <= 3]
pl = B.call("jawa/list_pawns", includeHealth=True) or {}
for p in occ:
    h = [q for q in pl.get("pawns") or [] if q.get("id") == p["id"] or str(q.get("thingId")) == p["id"]]
    hd = [(x.get("def") or x.get("label"), x.get("part"), round(x.get("severity") or 0, 2)) for x in
          ((h[0].get("health") or {}).get("hediffs") or [])] if h else None
    print("OCCUPANT", p["name"], p["id"], p["x"], p["z"], "downed" if p.get("downed") else "standing", "hediffs", hd)
    r = B.call("jawa/inspect_string", thingIds=p["id"]) or {}
    print("INSPECT", json.dumps(r.get("things") or r, default=str)[:1500])
cols = [p for p in (B.call("jawa/pawn_census", faction="player") or {}).get("pawns") or [] if p.get("isColonist")]
c = [p for p in cols if p.get("name") == who] or cols[:1]
if c and occ:
    c = c[0]
    print("COLONIST", c["name"], c["x"], c["z"])
    B.call("rimworld/clear_selection")
    print("select", json.dumps(B.call("rimworld/select_pawn", pawnName=c["name"]) or {}, default=str)[:200])
    r = B.call("rimworld/right_click_cell", x=occ[0]["x"], z=occ[0]["z"], button="right") or {}
    print("rightclick", json.dumps(r, default=str)[:600])
    time.sleep(0.5)
    r = B.call("rimworld/get_context_menu_options") or {}
    for o in r.get("options") or []:
        print("OPTION", (o.get("label") if isinstance(o, dict) else o), "| disabled" if isinstance(o, dict) and o.get("disabled") else "")
    B.call("jawa/clear_ui", all=True)
for root in (20, 11):
    r = B.call("rimworld/screenshot_cell_rect", x=px - 4, z=pz - 3, width=9, height=8, paddingCells=1, rootSize=root,
               doNotResetCamera=True, fileName="am_pit_r%d_%s" % (root, time.strftime("%H%M%S"))) or {}
    print("SHOT", r.get("path"))
