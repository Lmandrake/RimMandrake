#!/usr/bin/env python3
"""Round 6 item 4, second form (the first one placed lamps touching a conduit, which draws no cord): re-style the lamp the colony already has at 177,101
(the research-bench lamp, its cord drawn from conduit 179,103) through every standing style, then swap it for a TorchLamp and do the same; a 3x3 crop
each (rect corner 176,100). Run on Steve: python.exe ralph/live/r6_lamps2.py   (the map is left changed: reload Modern after)"""
import os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import gss_stage as G  # noqa: E402
B = G.RL.LiveBridge(); stamp = time.strftime("%H%M%S")
B.call("jawa/clear_ui", all=True)
CELL = (177, 101)
RUN = [("StandingLamp", s) for s in [None, "Morbid_StandingLamp", "Rustic_StandingLamp", "Spikecore_StandingLamp", "Techist_StandingLamp", "Totemic_StandingLamp"]] + \
      [("TorchLamp", s) for s in [None, "Morbid_TorchLamp", "Rustic_TorchLamp", "Spikecore_TorchLamp", "Totemic_TorchLamp"]]
cur = "StandingLamp"
for d, st in RUN:
    if d != cur:
        B.call("jawa/destroy_batch", rects="%d,%d,1,1" % CELL, categories="Building")
        r = B.call("jawa/build_batch", ops="%s:%d,%d" % (d, CELL[0], CELL[1]), stuff="Steel", wipeExisting=False)
        print("SWAP", d, "survived", r.get("survived"), r.get("failed") or "")
        cur = d
    if st:
        th = B.call("jawa/list_things", defName=d, rect="%d,%d,1,1" % CELL, limit=3).get("things") or []
        rr = B.call("jawa/set_thing_props", thing=(th[0].get("id") or th[0].get("thingId")) if th else "", style=st)
        print("  style", st, rr.get("changed"), rr.get("styleDefAfter"), rr.get("error") or "")
    time.sleep(1.5)
    r = B.call("rimworld/screenshot_cell_rect", x=CELL[0] - 1, z=CELL[1] - 1, width=3, height=3, paddingCells=0, fileName="r6_lampB_%s_%s" % (st or d, stamp), rootSize=2.0)
    print("SHOT", st or d, stamp)
    time.sleep(0.4)
G.go(B, "Modern", "lamp")
