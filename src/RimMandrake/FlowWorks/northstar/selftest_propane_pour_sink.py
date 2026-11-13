#!/usr/bin/env python3
"""PROPANE_POUR_DIAGNOSE_DRAINS_TO_NOWHERE: where the poured propane went, and the two harness fixes.

Run-2 on SteveDesktop (2026-11-05, FlowWorks_20261105T065153Z; extract in
infrastructure/state/evidence/PROPANE_POUR_DIAGNOSE_DRAINS_TO_NOWHERE/fail_row.json): the pump poured 3 levels out of a
30,000-unit Dump tank, yet plot F's dry channel read fill 0,0,0. Its squares (89..91, 201) read isSinkCell false, true,
true and the engine's sinkTransferredTotal stood at 2.25 levels. The sink rule is the 10-cell edge band, so dug x=89 not
a sink and x=90 a sink means the map was 100 wide; the run was non-situational, so the anchor was the map centre
(50, 200). Plot F (x0 = 86) reached the east sink band and the propane left the map, as a sink is built to do. The
250x250 runs before and after anchor at (125, 125) and PASS. The row FAILed against the mod for a fixture that measured
the site.

  (a) a plot whose buffered rect leaves the map interior refuses UNMEASURED in _prep_plot (run-2's map 100x400, centre
      anchor, sinks by the engine's band rule: FAIL against the mod with the guards removed, UNMEASURED with them);
  (b) propane_tank_pours_into_channel refuses UNMEASURED when its channel squares are sinks (red on the old row: FAIL);
      a healthy channel still PASSes and a channel that really lost its propane still FAILs;
  (c) the FlowWorks suite's anchor margin keeps the whole buffered plot grid out of the edge band whatever
      helpers.safe_anchor picks on a 250-cell map under --situational (red on the old default margin 20).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOD)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, MOD, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import extensions as EXT  # noqa: E402
from selftest_extensions import _ext_run  # noqa: E402
import helpers as H  # noqa: E402

ROW = "propane_tank_pours_into_channel"


def propane_game(sink, fill, terrain, size=None):
    """A scripted game for fuel_moat_propane: every dug square reports isSinkCell=`sink` and fill `fill`, terrain
    `terrain`; the pump poured 3 levels and emptied its tank (the run-2 readings). With `size` (sizeX, sizeZ) the map
    reports that size and `sink` is ignored: a square is a sink by the engine's rule (within EDGE_BAND of an edge)."""
    def h(tl, p):
        m = p.get("method")
        if tl == "jawa/map_info":
            return {"success": True, "sizeX": size[0], "sizeZ": size[1]} if size else {"success": True}
        if size and tl in ("jawa/flowworks_excavation_report", "jawa/flowworks_excavation_drive"):
            x, z, e = int(p.get("x", 0)), int(p.get("z", 0)), EXT.EDGE_BAND
            s = x < e or z < e or x >= size[0] - e or z >= size[1] - e
            return {"success": True, "depth": 2, "waterDl": (0 if s else fill) * 10000, "isExcavated": True, "isSinkCell": s,
                    "sinkTransferredTotal": 2.25 if s else 0.0}
        if tl == "jawa/static_call":
            if m == "ProofResetRect":
                return {"success": True, "result": "RESET x left=0"}
            if m == "ProofTank":
                return {"success": True, "result": "TANK mode=Dump effective=Dump liquid=RM_Liquid_Propane units=30000"}
            if m == "ProofPump":
                poured = ";pour" not in str(p.get("args"))
                return {"success": True, "result": "PUMP running=%s moved=%d pour=True tank=%s"
                        % (poured, 3 if poured else 0, "empty:0" if poured else "RM_Liquid_Propane:30000")}
            if m == "ProofPitWater":
                return {"success": True, "result": "PITWATER dl=0 wet=0 cells=1"}
            return {"success": True, "result": ""}
        if tl in ("jawa/flowworks_excavation_report", "jawa/flowworks_excavation_drive"):
            return {"success": True, "depth": 2, "waterDl": (fill) * 10000, "isExcavated": True, "isSinkCell": sink,
                    "sinkTransferredTotal": 2.25 if sink else 0.0}
        if tl == "rimworld/get_cell_info":
            return {"success": True, "cell": {"terrainDefName": terrain}}
        if tl == "jawa/list_things":
            if p.get("defName") == "Battery":
                return {"success": True, "things": [{"id": "Battery1"}]}
            return {"success": True, "things": []}
        return {"success": True}
    return h


def row(handler, anchor=None):
    return _ext_run(EXT, "fuel_moat_propane", handler, anchor=anchor).get(ROW)


RUN2_MAP, RUN2_ANCHOR = (100, 400), (50, 200)     # 100 wide (sink pattern), centre anchor (50, 200)


def run2(guards):
    """fuel_moat_propane on run-2's map; guards=False removes both refusals (the code that FAILed run-2)."""
    saved = EXT._refuse_plot_off_map, EXT._refuse_sink_cells
    if not guards:
        EXT._refuse_plot_off_map = EXT._refuse_sink_cells = lambda *a, **k: None
    try:
        # fill 0 on every square, x=89 too: run-2's reading (the channel is one connected run, and it drained east)
        return _ext_run(EXT, "fuel_moat_propane", propane_game(None, 0, "RM_Fill_Propane_Trace", RUN2_MAP),
                        anchor=RUN2_ANCHOR)
    finally:
        EXT._refuse_plot_off_map, EXT._refuse_sink_cells = saved


def plots_clear(anchor, size):
    """Every buffered plot rect at `anchor` keeps EDGE_BAND cells from each edge of a `size` map."""
    ax, az = anchor
    n, m = size
    b, e = EXT.PLOT_BUFFER, EXT.EDGE_BAND
    for gx, gz in EXT.PLOTS.values():
        x0, z0 = ax - EXT.PITCH + gx * EXT.PITCH, az - EXT.PITCH + gz * EXT.PITCH
        if x0 - b < e or z0 - b < e or x0 + EXT.PW + b > n - e or z0 + EXT.PH + b > m - e:
            return False
    return True


class _MapSess(object):
    def __init__(self, size, colonists):
        self.size, self.colonists = size, colonists

    def call(self, tool, **kw):
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": self.size[0], "sizeZ": self.size[1]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": "C%d" % i, "x": x, "z": z, "isPlayer": True, "intelligence": "Humanlike",
                                                "dead": False, "spawned": True} for i, (x, z) in enumerate(self.colonists)]}
        return {"success": True}


COLONY_SPOTS = [[], [(125, 125)], [(125, 125), (200, 50)], [(50, 50)], [(200, 200)], [(50, 200), (200, 50)],
                [(125, 125), (60, 190)], [(30, 30), (220, 220), (125, 125)]]


def anchors(margin, size=(250, 250)):
    return [H.safe_anchor(_MapSess(size, c), margin=margin)[:2] for c in COLONY_SPOTS]


def main():
    errs = []
    old = run2(False)
    if old.get(ROW) != "FAIL":
        errs.append("probe is blind: run-2's map without the guards gave %s, want FAIL (the run-2 verdict)" % old)
    new = run2(True)
    setup = str(new.get("<setup>", ""))
    if not setup.startswith("FAIL: UNMEASURED: plot F") or ROW in new:
        errs.append("run-2's map (100x400, anchor (50, 200)) gave %s, want the chain refused UNMEASURED at plot F" % new)
    got = row(propane_game(False, 1, "RM_Fill_Propane_Trace", (250, 250)), anchor=(125, 125))
    if got != "PASS":
        errs.append("the 250x250 map at the centre anchor (the passing runs) gave %s, want PASS" % got)
    got = row(propane_game(True, 0, "RM_Fill_Propane_Trace"))
    if got != "UNMEASURED":
        errs.append("a channel in the edge-sink band (run-2's readings) gave %s, want UNMEASURED" % got)
    got = row(propane_game(False, 1, "RM_Fill_Propane_Trace"))
    if got != "PASS":
        errs.append("a healthy pour (fill 1 on RM_Fill_Propane_*, no sinks) gave %s, want PASS" % got)
    got = row(propane_game(False, 0, "RM_Channel_Mid"))
    if got != "FAIL":
        errs.append("a pour that left the inland channel dry gave %s, want FAIL" % got)

    sys.path.insert(0, MOD)
    import validation as VAL  # the suite the runner runs for FlowWorks (its anchor_margin feeds safe_anchor)
    margin = getattr(VAL.suite, "anchor_margin", 20)
    bad = [a for a in anchors(margin) if not plots_clear(a, (250, 250))]
    if bad:
        errs.append("FlowWorks anchor margin %s lets safe_anchor pick %s, whose plots reach the edge-sink band" % (margin, bad))
    if all(plots_clear(a, (250, 250)) for a in anchors(20)):
        errs.append("probe is blind: the old margin 20 never put a plot in the edge band")
    if margin != EXT.ANCHOR_MARGIN:
        errs.append("validation.suite.anchor_margin %s != extensions.ANCHOR_MARGIN %s" % (margin, EXT.ANCHOR_MARGIN))

    if errs:
        print("selftest_propane_pour_sink: FAIL")
        for e in errs:
            print("  - " + e)
        return 1
    print("selftest_propane_pour_sink: PASS -- run-2's 100-wide map refused UNMEASURED (FAIL without the guard), "
          "250 map PASS; sink channel UNMEASURED, healthy PASS, dry FAIL; anchor margin %d clears "
          "the edge band for %d colony layouts" % (margin, len(COLONY_SPOTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
