#!/usr/bin/env python3
"""POND_OUTLET_FIX_REJECTS_FRACTIONAL_ROOM (offline, no game). RM_LiquidSpill.Outlet chose a pond (Body) only when it had a
whole level of room (`ex.CanReturnLevels(c, fluid, 1)`), while its channel test beside it was already exact-aware
(`PourRoomDl(c, fluid, 1) > 0`). A limited pond with 1..U-1 dL of room was refused, so the wet end read Blocked though the
Body leg (BodyRoomDl/BodyTake, exact) could take what fits. Fixed: with exact-level water the pond test is
`BodyRoomDl(ex, c, fluid, 1) > 0`; whole-notch water keeps the whole-level test. The Dump drain then offers a Body only what
fits (OutletRoomDl), not a whole level it cannot take.

Each check reads the source and fails on the pre-fix code (a planted copy of it is run through the same checks), and a
Python model of the decision is swept over every room 0..2U for both water modes.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
U = 1000  # decilitres per level (RM_LevelSolve.U); the sweep only needs 0 < U


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def flat(s):
    s = re.sub(r"//[^\n]*", "", s)
    return re.sub(r"\s+", " ", s)


BODY_TEST = ("if (c.InBounds(map) && (RM_MapComponent_Excavation.LevelExact ? BodyRoomDl(ex, c, fluid, 1) > 0 "
             ": ex.CanReturnLevels(c, fluid, 1))) { cell = c; return RM_OutletKind.Body; }")
OLD_BODY_TEST = "if (c.InBounds(map) && ex.CanReturnLevels(c, fluid, 1)) { cell = c; return RM_OutletKind.Body; }"
BODY_ROOM = ("if (RM_MapComponent_Excavation.LevelExact) { return ex.ReturnRoomDl(cell, fluid, want); }")
DUMP_N = ("RM_MapComponent_Excavation.LevelExact && kind == RM_OutletKind.Body ? (int)RM_LiquidSpill.OutletRoomDl(ex, kind, "
          "cell, fluid, System.Math.Min(left, tank.storedUnits))")
LEG = "case RM_OutletKind.Body: return RM_TransferLeg.World(k => BodyRoomDl(ex, cell, fluid, k) >= k, k => BodyTake(ex, cell, fluid, k));"


def checks(spill, net):
    fails = []
    sp, nt = flat(spill), flat(net)
    i = sp.find("public static RM_OutletKind Outlet(")
    outlet = sp[i:sp.find("public static RM_TransferLeg OutletLeg(", i)] if i >= 0 else ""
    if BODY_TEST not in outlet:
        fails.append("Outlet: pond test is exact-aware (BodyRoomDl > 0 with exact water, whole level otherwise)")
    if "CanReturnLevels(c, fluid, 1)) { cell = c;" in outlet and BODY_TEST not in outlet:
        fails.append("Outlet: whole-level-only pond test is gone")
    if BODY_ROOM not in sp:
        fails.append("BodyRoomDl: exact water reads the pond's decilitre room (ReturnRoomDl)")
    if LEG not in sp:
        fails.append("OutletLeg Body: takes k when BodyRoomDl >= k (the leg the outlet promises)")
    if DUMP_N not in nt:
        fails.append("Dump drain: a Body outlet is offered what fits (OutletRoomDl), not a whole level")
    return fails


# ---- model of the decision (mirrors Outlet's Body branch and BodyRoomDl), swept
def can_return_levels(room, levels):
    return room >= levels * U


def body_room_dl(room, want, exact):
    if exact:
        return max(0, min(room, want))
    return want - want % U if want >= U and can_return_levels(room, want // U) else 0


def outlet_is_body(room, exact, fixed):
    if fixed and exact:
        return body_room_dl(room, 1, exact) > 0
    return can_return_levels(room, 1)


def sweep():
    fails = []
    for room in range(0, 2 * U + 1):
        for exact in (True, False):
            got = outlet_is_body(room, exact, True)
            want = room > 0 if exact else room >= U
            if got != want:
                fails.append("model room=%d exact=%s body=%s want %s" % (room, exact, got, want))
                continue
            # whenever the outlet promises a Body, the leg takes at least 1 dL of what it is offered (no dead promise)
            if got and body_room_dl(room, min(room, U) if exact else U, exact) <= 0:
                fails.append("model room=%d exact=%s: Body chosen but leg takes nothing" % (room, exact))
            # never more than the room (a pond is never over-credited)
            if body_room_dl(room, 10 * U, exact) > room:
                fails.append("model room=%d exact=%s: over-credit" % (room, exact))
    # can-fail: the pre-fix decision refuses a fractional room with exact water
    if outlet_is_body(U // 2, True, False):
        fails.append("model can-fail: pre-fix rule unexpectedly accepted 500 dL room")
    return fails


def main():
    spill = read(os.path.join("Machinery", "RM_LiquidSpill.cs"))
    net = read(os.path.join("Machinery", "RM_LiquidNet.cs"))
    fails = checks(spill, net)
    for f in fails:
        print("  FAIL", f)
    # can-fail: the planted pre-fix source must fail the source checks
    planted_spill = flat(spill).replace(BODY_TEST, OLD_BODY_TEST)
    planted_net = flat(net).replace(DUMP_N, "XX")
    pf = checks(planted_spill, planted_net)
    if len(pf) < 2:
        fails.append("can-fail: planted pre-fix source passed (%s)" % pf)
        print("  FAIL can-fail: planted pre-fix source passed")
    mf = sweep()
    for f in mf[:10]:
        print("  FAIL", f)
    fails += mf
    print("pond outlet fractional room: %s (%d source pins, sweep rooms 0..%d x 2 modes, planted fails %d)"
          % ("FAIL" if fails else "PASS", 5, 2 * U, len(pf)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
