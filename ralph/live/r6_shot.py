"""One-off crops by name from r3_crop_list.json: python.exe ralph/live/r6_shot.py NAME... (the map stays as it is)"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import gss_stage as G  # noqa: E402
B = G.RL.LiveBridge(); stamp = time.strftime("%H%M%S")
for c in json.load(open("ralph/live/r3_crop_list.json")):
    if any(c["name"].startswith(a) for a in sys.argv[1:]):
        r = B.call("rimworld/screenshot_cell_rect", x=c["x"], z=c["z"], width=c["w"], height=c["h"], paddingCells=0,
                   fileName="%s_%s" % (c["name"], stamp), rootSize=max(c["w"], c["h"]) / 2.0 + 0.5)
        print("SHOT", c["name"], stamp, r.get("filePath") or str(r)[:100]); time.sleep(0.4)
G.go(B, "Modern", "lamp")
