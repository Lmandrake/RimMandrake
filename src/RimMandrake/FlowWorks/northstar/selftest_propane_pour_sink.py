#!/usr/bin/env python3
"""PROPANE_POUR_DIAGNOSE_DRAINS_TO_NOWHERE: where the poured propane went, and the two harness fixes.

Run-2 on SteveDesktop (2026-11-05, FlowWorks_20261105T065153Z; extract in
infrastructure/state/evidence/PROPANE_POUR_DIAGNOSE_DRAINS_TO_NOWHERE/fail_row.json): the pump poured 3 levels out of a
30,000-unit Dump tank, yet plot F's dry channel read fill 0,0,0. Two of its three squares reported isSinkCell=true and the
engine's sinkTransferredTotal stood at 2.25 levels: the plot sat in the map-edge sink band, and the propane left the map
as a sink is built to do. The row FAILed against the mod for a fixture that measured the site.

  (a) propane_tank_pours_into_channel refuses UNMEASURED when its channel squares are sinks (red on the old row: FAIL);
      a healthy channel still PASSes and a channel that really lost its propane still FAILs.
  (b) the FlowWorks suite's anchor margin keeps the whole buffered plot grid out of the edge band whatever
      helpers.safe_anchor picks on a 250-cell map (red on the old default margin 20).
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


def propane_game(sink, fill, terrain):
    """A scripted game for fuel_moat_propane: every dug square reports isSinkCell=`sink` and fill `fill`, terrain
    `terrain`; the pump poured 3 levels and emptied its tank (the run-2 readings)."""
    def h(tl, p):
        m = p.get("method")
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
            return {"success": True, "depth": 2, "fill": fill, "isExcavated": True, "isSinkCell": sink,
                    "sinkTransferredTotal": 2.25 if sink else 0.0}
        if tl == "rimworld/get_cell_info":
            return {"success": True, "cell": {"terrainDefName": terrain}}
        if tl == "jawa/list_things":
            if p.get("defName") == "Battery":
                return {"success": True, "things": [{"id": "Battery1"}]}
            return {"success": True, "things": []}
        return {"success": True}
    return h


def row(handler):
    return _ext_run(EXT, "fuel_moat_propane", handler).get(ROW)


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
    print("selftest_propane_pour_sink: PASS -- sink channel UNMEASURED, healthy PASS, dry FAIL; anchor margin %d clears "
          "the edge band for %d colony layouts" % (margin, len(COLONY_SPOTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
