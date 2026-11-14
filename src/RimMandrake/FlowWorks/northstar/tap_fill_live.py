"""TAP FILL live check (RIMMANDRAKE_WEIGH_TAP_BACKS_UP_AT_HALF_FULL_CHANNEL, owner card 2026-11-14 "Pour whatever fits").

  python.exe src/RimMandrake/FlowWorks/northstar/tap_fill_live.py [out.json] [--origin X,Z] [--pulses 400] [--pace 0]

PROVE  on a cleared Soil plot, a 12-square row dug to 2 (24 levels), a mapmaker Source tap (RM_FlowSource, 0.5 level a
       pulse of water) beside square 0 and a Sink (RM_FlowSink, 0.25 a pulse) beside square 11; the clock advances one
       liquid pulse at a time (pulseIntervalTicks, read live) for --pulses pulses, reading every square in decilitres
       (ProofFluidRow) and both taps' state lines (RM_MapControls.Report).
EXPECT TF_channel_fills: the row holds >= 20 of its 24 levels at the end (the whole-notch engine filled it; the whole-level
       pour of 2026-10-17 to 2026-11-14 settled near half full, measured offline in the C# case
       MapControl_source_and_sink_conserve_through_the_kernel).
       TF_conserves: the row's decilitres == the source's poured minus the sink's drained (both from their state lines,
       in levels, to 0.01 level).
LIES   a REFUSED placement or dig, or an unread square, is UNMEASURED(HARNESS/SITE), never PASS. Rain or a pond reaching
       the row would add water the taps did not pour: the plot is cleared and the walk's calm settings apply (run
       water_scenes_walk.py prep first on a quicktest map).
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
ITEM = "RIMMANDRAKE_WEIGH_TAP_BACKS_UP_AT_HALF_FULL_CHANNEL"
MAPCTL = "RimMandrake.FlowWorks.MapControls.RM_MapControls"
W, DEPTH = 12, 2


def state_field(report, kind, at, key):
    """The float `key=` on the `<kind> <id> at x,z` line of RM_MapControls.Report (None when absent)."""
    for line in str(report or "").splitlines():
        if line.startswith(kind + " ") and (" at %d,%d " % at) in line:
            m = re.search(r"\b%s=([-0-9.]+)" % key, line)
            return float(m.group(1)) if m else None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--pulses", type=int, default=400)
    ap.add_argument("--pace", type=float, default=0.0)
    a = ap.parse_args()
    import water_scenes_walk as WS
    w = WS.Walk(argparse.Namespace(mock=False, pace=a.pace, no_shots=True))
    ox, oz = (int(v) for v in a.origin.split(","))
    out = a.out or os.path.join(HERE, "tap_fill_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "tap_fill_live.py", "item": ITEM, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows,
           "args": vars(a)}

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-10s %-18s %s" % (st, rid, json.dumps(det, default=str)[:300]))

    def done(rc):
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        print("wrote", out)
        return rc

    rect = (ox - 2, oz - 2, W + 4, 5)
    w.clear_site(rect)
    chan = WS.run(ox, oz, W)
    for c in chan:
        w.dig(c, DEPTH)
    ok1, src = w.proof(MAPCTL, "PlaceSource", "%d,%d|RM_Fluid_Water|0.5" % (ox - 1, oz))
    ok2, snk = w.proof(MAPCTL, "PlaceSink", "%d,%d|any|0.25" % (ox + W, oz))
    if not (ok1 and ok2) or w.refused:
        row("TF_channel_fills", "UNMEASURED", "HARNESS", {"source": src, "sink": snk, "refused": w.refused})
        return done(2)
    iv = w.interval()
    for _ in range(a.pulses):
        w.ticks(iv)
        if a.pace:
            time.sleep(a.pace)
    m, _ = w.cells(chan)
    held = WS.dl_sum(m, chan)
    ok, rep = w.proof(MAPCTL, "Report", "")
    poured, drained = state_field(rep, "source", (ox - 1, oz), "poured"), state_field(rep, "sink", (ox + W, oz), "drained")
    det = {"held_levels": None if held is None else held / float(WS.LEVEL_UNITS), "of": W * DEPTH,
           "poured_levels": poured, "drained_levels": drained, "cells": {"%d,%d" % c: WS.dl_of(m, c) for c in chan}}
    if held is None:
        row("TF_channel_fills", "UNMEASURED", "HARNESS", dict(det, why="a square was not read"))
        return done(2)
    fills = held >= (W * DEPTH - 4) * WS.LEVEL_UNITS
    row("TF_channel_fills", "PASS" if fills else "FAIL", "MOD", det)
    if poured is None or drained is None:
        row("TF_conserves", "UNMEASURED", "HARNESS", dict(det, why="no poured/drained on the taps' state lines", report=rep))
        return done(2)
    cons = abs(held / float(WS.LEVEL_UNITS) - (poured - drained)) <= 0.01
    row("TF_conserves", "PASS" if cons else "FAIL", "MOD", det)
    return done(0 if fills and cons else 1)


if __name__ == "__main__":
    sys.exit(main())
