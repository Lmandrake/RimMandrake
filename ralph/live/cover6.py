"""cover6.py -- why a covered pit's south row reads as a dark band at play zoom (pass 6, s7 at root 7.5, ~61 px a cell).

  python.exe ralph/live/cover6.py stage  [--x X --z Z]   three 3x2 plots side by side on cleared ground near the colonists:
                                                          A undug, B dug 2 m + cover, C dug 2 m + spikes + cover
  python.exe ralph/live/cover6.py shots  <tag>           the three at root 7.2 (~64 px a cell, the owner's play zoom), 11, 20
  python.exe ralph/live/cover6.py set <field> <value>    one FlowWorks settings field (jawa/mod_settings_field), then re-shoot

Every result line starts with RESULT. Shots go to the game's Screenshots folder as c6_<tag>_<root>_<time>.
"""
import argparse
import json
import os
import sys
import time

import fwb

STATE = os.path.join(fwb.REPO, "Transient", "ralph_fw", "cover6_state.json")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def centre(B):
    cen = B.call("jawa/pawn_census", faction="player") or {}
    cols = [p for p in cen.get("pawns") or [] if p.get("isColonist")]
    return sum(p["x"] for p in cols) // len(cols), sum(p["z"] for p in cols) // len(cols)


def ops(defname, cells):
    return ";".join("%s:%d,%d" % (defname, x, z) for x, z in cells)


def stage(B, a):
    if a.x is None:
        cx, cz = centre(B)
        a.x, a.z = cx - 8, cz - 14
    x0, z0 = a.x, a.z
    # one cleared 13 x 6 field: three 3x2 plots two cells apart, a cell of ground all round
    B.call("jawa/clear_area", rect="%d,%d,%d,%d" % (x0 - 1, z0 - 2, 15, 6), dryRun=False)
    plots = {"A": x0, "B": x0 + 5, "C": x0 + 10}
    for k in ("B", "C"):
        for x in range(plots[k], plots[k] + 3):
            for z in (z0, z0 + 1):
                B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=4, setFill=-1)
    B.step(5)
    cells = lambda k: [(x, z) for x in range(plots[k], plots[k] + 3) for z in (z0, z0 + 1)]
    r = B.call("jawa/build_batch", ops=ops("RM_Spikes", cells("C")), stuff="WoodLog", faction="player", readBack=1) or {}
    log("RESULT spikes C", {k: r.get(k) for k in ("placed", "survived", "failed") if k in r})
    for k in ("B", "C"):
        r = B.call("jawa/build_batch", ops=ops("RM_PitCover_WovenScrap", cells(k)), stuff="WoodLog", faction="player", readBack=1) or {}
        log("RESULT cover", k, {k2: r.get(k2) for k2 in ("placed", "survived", "failed") if k2 in r})
    B.step(5)
    json.dump({"x0": x0, "z0": z0}, open(STATE, "w"))
    log("RESULT staged at", x0, z0, "plots A undug, B covered, C spiked+covered")


def shots(B, a):
    st = json.load(open(STATE))
    x0, z0 = st["x0"], st["z0"]
    for root in (7.2, 11.0, 20.0):
        name = "c6_%s_r%s_%s" % (a.tag, str(root).replace(".", "p"), time.strftime("%H%M%S"))
        kw = dict(x=x0 - 1, z=z0 - 2, width=15, height=6, paddingCells=1, rootSize=root, doNotResetCamera=True)
        B.call("jawa/clear_ui", all=True)
        B.call("rimworld/screenshot_cell_rect", fileName="c6_tmp", **kw)
        time.sleep(1.5)
        r = B.call("rimworld/screenshot_cell_rect", fileName=name, **kw) or {}
        log("RESULT shot", root, r.get("path") or r.get("message"), (r.get("clipRect") or {}))


def setf(B, a):
    r = B.call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings", action="set", field=a.tag, value=a.value) or {}
    log("RESULT set", a.tag, a.value, json.dumps(r, default=str)[:300])


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("tag", nargs="?", default="t")
    ap.add_argument("value", nargs="?", default="")
    ap.add_argument("--x", type=int)
    ap.add_argument("--z", type=int)
    a = ap.parse_args()
    B = fwb.FW()
    B.call("rimworld/set_time_speed", speed="Paused")
    dict(stage=stage, shots=shots, set=setf)[a.cmd](B, a)


if __name__ == "__main__":
    main()
