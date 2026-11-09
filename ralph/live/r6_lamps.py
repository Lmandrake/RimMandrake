#!/usr/bin/env python3
"""Round 6 item 4 (run on Steve: python.exe ralph/live/r6_lamps.py [load]): every standing/torch lamp style in CordWorldAdapter.BaseOffsets
built on a conduit trunk in a free patch of gss_ba_Modern (131..154, 86..95), a 3x3 close crop of each, unique names, raids off, paused,
nothing unpaused. Prints SHOT lines and which defs failed to build."""
import os, sys, time
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "ralph", "live"))
import gss_stage as G  # noqa: E402
B = G.RL.LiveBridge()
if "load" in sys.argv and G.load(B, "Modern") != 0:
    sys.exit(2)
STYLES = [("StandingLamp", None), ("StandingLamp", "StandingLampColored"), ("StandingLamp", "Morbid_StandingLamp"), ("StandingLamp", "Rustic_StandingLamp"),
          ("StandingLamp", "Spikecore_StandingLamp"), ("StandingLamp", "Techist_StandingLamp"), ("StandingLamp", "Totemic_StandingLamp"),
          ("TorchLamp", None), ("TorchLamp", "Morbid_TorchLamp"), ("TorchLamp", "Rustic_TorchLamp"), ("TorchLamp", "Spikecore_TorchLamp"),
          ("TorchLamp", "Totemic_TorchLamp"), ("TorchLamp", "BuildTorchLamp")]
stamp = time.strftime("%H%M%S")
B.call("jawa/clear_ui", all=True)
B.call("jawa/destroy_batch", rects="131,86,24,10", categories="Plant,Item,Filth,Building")
ops = ["PowerConduit:%d,90" % x for x in range(132, 154)]
r = B.call("jawa/build_batch", ops=";".join(ops), wipeExisting=False)
print("trunk survived", r.get("survived"), "of", len(ops))
spots = []
for i, (d, st) in enumerate(STYLES):
    x = 133 + 3 * (i % 7)
    z = 91 if i < 7 else 89
    r = B.call("jawa/build_batch", ops="%s:%d,%d" % (d, x, z), stuff="Steel", wipeExisting=False)
    print("LAMP", d, st, x, z, "survived", r.get("survived"), r.get("failed") or "")
    if not r.get("survived"):
        continue
    if st:
        th = B.call("jawa/list_things", defName=d, rect="%d,%d,1,1" % (x, z), limit=3).get("things") or []
        rr = B.call("jawa/set_thing_props", thing=(th[0].get("id") or th[0].get("thingId")) if th else "", style=st)
        print("  style", st, "changed", rr.get("changed"), "after", rr.get("styleDefAfter"), rr.get("error") or "")
    spots.append((st or d, x, z))
time.sleep(2.0)
for d, x, z in spots:
    r = B.call("rimworld/screenshot_cell_rect", x=x - 1, z=z - 1, width=3, height=3, paddingCells=0, fileName="r6_lamp_%s_%s" % (d, stamp), rootSize=2.0)
    print("SHOT", d, r.get("filePath") or r.get("path") or str(r)[:120])
    time.sleep(0.4)
G.go(B, "Modern", "lamp")
print("CLOCK", G.clock(B))
