#!/usr/bin/env python3
"""selftest_pump_station_ports.py -- a multi-cell pump takes a hose at a port on each of its four sides (offline, no game).

HOSE_END_FIX_CELL_SHORT_OF_PORT / PUMP_PORT_FIX_ASSUMES_ONE_CELL: the S5 scene (bridge run 1e, captures s5_st_kludged_v,
s5_st_repaired_v) laid a reel hose to (114,118), the cell beside the east edge of a 3x2 pumping station at (112,118). The
lay reported layOk but the end lay loose, uncoupled: HosePorts.EndSideOn / ReelSideOn measured the side from pump.Position
as if every pump were 1x1 (RM_PumpPortMath.SideOf on the unit offset), so on a 3x2 station only the south side (where
Position + FacingCell happens to leave the footprint) was a port. Owner, 2026-10-20: "a HOSE must connect at one of the
four sides" -- a pumping station is a Building_LiquidPump like any other.

The rule (RM_PumpPortMath.PortCell, mirrored here): side s's port is Position walked out along Rot4(s).FacingCell to the
first cell outside the footprint -- for a 1x1 pump exactly Position + FacingCell, as before. One port per side, one hose
per port (HoseMayTake, unchanged).

Checks: the Python mirror over every footprint up to 4x4; the C# source carries the same rule and HosePorts uses it for
both a free end and a reel body; the fittings gate (selftest_hose_fittings.ports) and the generated UnderCouplerReach table
see the station's four ports; the S5 east end (114,118) is the east port of a station at (112,118).
The C# twin of the sweep is PumpChecks.cs case PumpPorts_station_footprint_ports (selftest_flowworks_stock.py, Windows).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "Source")
fails = []

ROT4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]            # 0 north, 1 east, 2 south, 3 west


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def read(*p):
    with open(os.path.join(SRC, *p), encoding="utf-8") as f:
        return f.read()


def position_of(min_x, min_z, w, h):
    """GenAdj.OccupiedRect inverse for an unrotated (north) thing: Position from the footprint's minimum corner."""
    return min_x + (w - 1) // 2, min_z + (h - 1) // 2


def port_cell(min_x, min_z, w, h, px, pz, side):
    """Mirror of RM_PumpPortMath.PortCell."""
    dx, dz = ROT4[side]
    x, z = px + dx, pz + dz
    while min_x <= x < min_x + w and min_z <= z < min_z + h:
        x, z = x + dx, z + dz
    return x, z


def side_of_port(min_x, min_z, w, h, px, pz, x, z):
    """Mirror of RM_PumpPortMath.SideOfPort: the side whose port is (x, z), or -1."""
    for s in range(4):
        if port_cell(min_x, min_z, w, h, px, pz, s) == (x, z):
            return s
    return -1


def mirror_sweep():
    bad = []
    for w in range(1, 5):
        for h in range(1, 5):
            mx, mz = 10, 20
            px, pz = position_of(mx, mz, w, h)
            cells = set()
            for s in range(4):
                c = port_cell(mx, mz, w, h, px, pz, s)
                cells.add(c)
                inside = mx <= c[0] < mx + w and mz <= c[1] < mz + h
                # edge-adjacent (shares an edge with exactly one footprint cell, not a corner)
                nb = [(c[0] + dx, c[1] + dz) for dx, dz in ROT4]
                touch = sum(1 for (x, z) in nb if mx <= x < mx + w and mz <= z < mz + h)
                if inside or touch != 1:
                    bad.append((w, h, s, c))
                if side_of_port(mx, mz, w, h, px, pz, *c) != s:
                    bad.append((w, h, s, "round trip"))
                if w == 1 and h == 1 and c != (px + ROT4[s][0], pz + ROT4[s][1]):
                    bad.append((w, h, s, "1x1 not Position+FacingCell"))
            if len(cells) != 4:
                bad.append((w, h, "ports not distinct"))
            # every other cell around the footprint (corners, other lanes) is no port
            for x in range(mx - 2, mx + w + 2):
                for z in range(mz - 2, mz + h + 2):
                    if (x, z) not in cells and side_of_port(mx, mz, w, h, px, pz, x, z) != -1:
                        bad.append((w, h, (x, z), "non-port cell read as a port"))
    return bad


def main():
    bad = mirror_sweep()
    check(not bad, "mirror: every footprint 1..4 x 1..4 has 4 distinct edge-adjacent ports, 1x1 = Position + FacingCell (%s)"
          % (bad[:3] if bad else "16 footprints"))

    # the S5 scene: Kludged at (112,118), 3x2 -> footprint x 111-113, z 118-119
    mx, mz = 111, 118
    px, pz = position_of(mx, mz, 3, 2)
    check((px, pz) == (112, 118), "S5: a 3x2 station at (112,118) has its footprint minimum at (111,118)")
    check(side_of_port(mx, mz, 3, 2, px, pz, 114, 118) == 1, "S5: the end at (114,118) lies on the station's EAST port")
    check(side_of_port(mx, mz, 3, 2, px, pz, 112, 117) == 2, "S5: the end at (112,117) lies on its south port (unchanged)")
    check(side_of_port(mx, mz, 3, 2, px, pz, 114, 119) == -1, "can-fail: (114,119), the east side's other lane, is no port")
    check(side_of_port(mx, mz, 3, 2, px, pz, 114, 117) == -1, "can-fail: the south-east corner is no port")

    # C# production source: the same rule, used by HosePorts for ends AND reel bodies
    pm = read("Machinery", "RM_PumpPortMath.cs")
    check(re.search(r"public static void PortCell\(int minX, int minZ, int w, int h, int posX, int posZ, int side, out int x, out int z\)", pm)
          is not None, "C#: RM_PumpPortMath.PortCell(footprint, Position, side) exists")
    check(re.search(r"while \(x >= minX && x < minX \+ w && z >= minZ && z < minZ \+ h\)", pm) is not None,
          "C#: PortCell walks out of the footprint along the side")
    check(re.search(r"public static int SideOfPort\(", pm) is not None, "C#: RM_PumpPortMath.SideOfPort exists")
    hp = read("Hose", "HosePorts.cs")
    end_fn = re.search(r"private static int EndSideOn\(Thing pump, IntVec3 end\)\s*\{(.*?)\n        \}", hp, re.S)
    reel_fn = re.search(r"private static int ReelSideOn\(Thing pump, CompHoseReel r\)\s*\{(.*?)\n        \}", hp, re.S)
    check(end_fn is not None and "SideOfPort(" in end_fn.group(1) and "OccupiedRect()" in end_fn.group(1)
          and "SideOf(end.x - pump.Position.x" not in end_fn.group(1),
          "C#: HosePorts.EndSideOn reads the side from the pump's footprint (SideOfPort), not the unit offset from Position")
    check(reel_fn is not None and "PortCell(" in reel_fn.group(1) and "OccupiedRect()" in reel_fn.group(1)
          and "pump.Position + new Rot4(s).FacingCell" not in reel_fn.group(1),
          "C#: HosePorts.ReelSideOn tests the reel body against the footprint's port cells (PortCell)")
    pc = read("SelfTest", "PumpChecks.cs")
    check('Case("PumpPorts_station_footprint_ports"' in pc, "C#: PumpChecks carries the footprint sweep twin")

    # the fittings gate and the generated under-coupler table see the station's four ports
    import selftest_hose_fittings as gate
    pp = gate.ports({"def": "P", "kind": "pump", "size": [3, 2]}, "Scrapper", None)
    got = sorted((s, pt) for s, _, pt in pp)
    want = sorted([("north", (1.5, 2.0)), ("east", (3.0, 0.5)), ("south", (1.5, 0.0)), ("west", (0.0, 0.5))])
    check(got == want, "gate: a 3x2 pump has its four port points on the footprint edges (%s)" % got)
    one = sorted(s for s, _, _ in gate.ports({"def": "P", "kind": "pump", "size": [1, 1]}, "Scrapper", None))
    check(one == ["east", "north", "south", "west"], "gate: a 1x1 pump keeps its four ports")
    uc = read("Machinery", "UnderCouplerReach.cs")
    for d in ("RM_PumpingStation_Kludged", "RM_PumpingStation_Repaired"):
        sides = sorted(set(int(m) for m in re.findall(r'"%s\|\|(\d)\|\d"' % d, uc)))
        check(sides == [0, 1, 2, 3], "UnderCouplerReach: %s measured on all four sides (%s)" % (d, sides))

    print("selftest_pump_station_ports.py: %d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
