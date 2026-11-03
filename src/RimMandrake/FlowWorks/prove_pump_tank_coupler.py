#!/usr/bin/env python3
"""Live proof of PUMP_ON_TANK_FIX_NO_COUPLER (clause A1): a liquid pump touching a 2x2 RM_LiquidTank on its west or east
prints a coupler ON the tank's drawn nozzle and a drop pipe from its own port to it. Drives the bridge, so run it with
Windows python on a throwaway quicktest colony on a list holding FlowWorks:

    python.exe src/RimMandrake/FlowWorks/prove_pump_tank_coupler.py [x,z]

It calls RM_LiquidJoins.ProofMachineCouplers through jawa/static_call, which spawns a tank at x,z with a pump at
(x+2, z) east and (x-1, z+1) west, regenerates each pump's SectionLayer_RM_LiquidJoins, reads what it printed
(couplers, on-port couplers, drops, the coupler's point against TankPortGeometry.PortPoint, no placeholder art) and
destroys all three. Exit 0 when the reply says ok=True, 1 when it says ok=False, 2 when no verdict came back.

The layer's counters (lastCouplers/lastCouplersOnPort/lastDrops) count EVERY machine in the regenerated section, so
the two pumps must sit in different 17-cell map sections, or the west read sees both pumps (2/2/2) and a correct
build reads ok=False (blind check, 2026-11-03). So the tank's x is chosen with (x-1)//17 != (x+2)//17, i.e.
x % 17 in {15, 16, 0}, and the reply's pump positions are re-checked: a same-section placement is exit 2, never a
verdict. An explicit x,z must satisfy the same rule.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

TYPE = "RimMandrake.FlowWorks.Machinery.RM_LiquidJoins"
SECTION = 17          # Verse.Section.Size
MAX_TRIES = 400


def split_sections(x):
    """True when the west pump (x-1) and the east pump (x+2) of a tank at x fall in different sections."""
    return (x - 1) // SECTION != (x + 2) // SECTION


def candidates(sx, sz):
    """Tank origins whose pumps straddle a section boundary, nearest the map centre first, 3 cells in from every edge."""
    cx, cz = sx // 2, sz // 2
    out = [(x, z) for x in range(3, sx - 4) if split_sections(x) for z in range(3, sz - 4)]
    out.sort(key=lambda p: (p[0] - cx) ** 2 + (p[1] - cz) ** 2)
    return out


def pump_positions(text):
    return {m.group(1): (int(m.group(2)), int(m.group(3))) for m in re.finditer(r"\b([EW])\[pump=(\d+),(\d+)", text)}


def main(argv):
    arg = argv[1] if len(argv) > 1 else None
    if arg is not None and not re.fullmatch(r"\d+,\d+", arg):
        print("usage: prove_pump_tank_coupler.py [x,z]", file=sys.stderr)
        return 2
    if arg is not None and not split_sections(int(arg.split(",")[0])):
        print("x must satisfy x %% %d in {15, 16, 0} so the two pumps sit in different sections" % SECTION, file=sys.stderr)
        return 2
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    if arg is not None:
        tries = [tuple(int(v) for v in arg.split(","))]
    else:
        mi = c.call("jawa/map_info", {}, check=False)
        mi = mi if isinstance(mi, dict) else {}
        sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0)
        if sx <= 8 or sz <= 8:
            print("map_info gave no size: %s" % str(mi)[:200])
            return 2
        tries = candidates(sx, sz)[:MAX_TRIES]
    text = ""
    for x, z in tries:
        r = c.call("jawa/static_call", {"type": TYPE, "method": "ProofMachineCouplers", "args": "%d,%d" % (x, z)}, check=False)
        text = str(r.get("result") if isinstance(r, dict) else r)
        if not text.startswith("REFUSED: no clear"):
            break
    print(text)
    if not text.startswith("COUPLERS "):
        return 2
    pos = pump_positions(text)
    if set(pos) != {"E", "W"} or pos["E"][0] // SECTION == pos["W"][0] // SECTION:
        print("NO VERDICT: the two pumps did not sit in different sections: %s" % pos)
        return 2
    return 0 if text.startswith("COUPLERS ok=True ") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
