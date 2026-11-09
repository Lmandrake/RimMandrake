#!/usr/bin/env python3
"""Round 3 live check (run on Steve with python.exe from the clone root): optionally load gss_ba_Modern through the sitting stager
(raids off, clock only read, speed never touched), then a close-zoom shot of every crop in ralph/live/r3_crop_list.json (every strip,
wall outlet, lamp/device, battery, pole and the solar panels, positions from the shape lab's own output), unique names; ends on the
lamp spot. Usage: python.exe ralph/live/r3_crops.py [load]"""
import json, os, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "ralph", "live"))
import gss_stage as G  # noqa: E402  (puts run_live on the path)
B = G.RL.LiveBridge()
if "load" in sys.argv and G.load(B, "Modern") != 0:
    sys.exit(2)
stamp = time.strftime("%H%M%S")
B.call("jawa/clear_ui", all=True)
for c in json.load(open(os.path.join(REPO, "ralph", "live", "r3_crop_list.json"))):
    r = B.call("rimworld/screenshot_cell_rect", x=c["x"], z=c["z"], width=c["w"], height=c["h"], paddingCells=0,
               fileName="%s_%s" % (c["name"], stamp), rootSize=max(c["w"], c["h"]) / 2.0 + 0.5)
    print("SHOT", c["name"], r.get("filePath") or r.get("path") or json.dumps(r)[:120])
    time.sleep(0.4)
G.go(B, "Modern", "lamp")
t1, t2, state = G.clock(B)
print("CLOCK", t1, t2, state)
