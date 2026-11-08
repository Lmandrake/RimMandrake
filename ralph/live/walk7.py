"""walk7.py -- pass 7: one colonist walks a graded trench from undug ground down to 4 m and back up (pawn_lowers_on_deeper_cell,
pawn_rises_on_shallower_cell), at the owner's play zoom (root 7.2, ~64 px a cell).

  python.exe ralph/live/walk7.py <x0> <z0>      on the current map (dig + walk + shots; names w7_<dir>_<k>_<HHMMSS>)

The strip is 3 rows deep (z0 .. z0+2) and 9 columns wide (x0 .. x0+8); column k is dug k levels (0 .. 4 m). The colonist walks
the middle row east then west, one column at a time; at each stop one shot and the real drawn sink (ProofPawnSink).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb  # noqa: E402

LOG = os.path.join(fwb.OUT, "walk7.log")


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    os.makedirs(fwb.OUT, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def shot(B, name, rect, root=7.2):
    B.call("jawa/clear_ui", all=True)
    B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=0,
           rootSize=root, doNotResetCamera=True, fileName="w7_frame_tmp")
    time.sleep(1.2)
    r = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=0,
               rootSize=root, doNotResetCamera=True, fileName="%s_%s" % (name, time.strftime("%H%M%S"))) or {}
    log("SHOT", name, r.get("path") or r.get("message"))


def sink(B, pid):
    r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs", method="ProofPawnSink", args=pid) or {}
    return str(r.get("result") or r.get("message") or r.get("error"))[:200]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    B = fwb.FW()
    x0, z0 = int(sys.argv[1]), int(sys.argv[2])
    zm = z0 + 1
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,14,8" % (x0 - 2, z0 - 2))
    B.call("jawa/clear_area", rect="%d,%d,11,5" % (x0 - 1, z0 - 1), dryRun=False)
    for k in range(9):
        for j in range(3):
            if k:
                B.call("jawa/flowworks_excavation_drive", x=x0 + k, z=z0 + j, deepenLevels=k, setFill=-1)
    B.step(5)
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=x0 - 1, z=zm, faction="player", count=1) or {}
    pid = [p.get("id") for p in r.get("pawns") or [] if p.get("id")][0]
    rect = (x0 - 1, z0 - 1, 11, 5)
    for leg, cols in (("down", range(0, 9)), ("up", range(7, -1, -1))):
        for k in cols:
            o = B.call("jawa/order_pawn", pawnId=pid, x=x0 + k, z=zm, draft=True, waitTicks=240) or {}
            B.call("rimworld/play_for", durationMs=400, speed="Normal")
            log("AT", leg, k, json.dumps(o, default=str)[:100], sink(B, pid))
            shot(B, "w7_%s_%d" % (leg, k), rect)
    B.call("rimworld/set_time_speed", speed="Paused")


if __name__ == "__main__":
    main()
