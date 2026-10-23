#!/usr/bin/env python3
"""HOSE_FITTING_GATE_BUILD_BELIEVED_HOSEMATH -- every hose port the CODE defines has an opaque DRAWN fitting there (offline).

The joint check (northstar/joint_check.py, selftest_hose_ports.py) measures the hose end to the port the C# defines, never
to anything in the art, so on the Modern tall/IBC/XTall tanks it PASSED while the coupler floated ~0.3 cell off the drawn
wall (MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS, live art look 2026-10-22). This gate reads the INSTALLED textures instead:

  for every hose-coupling building (Building_LiquidTank / Building_LiquidPump defs) x look (ThingStyleDef <def>_<Look>)
  x side x lane, take the port point the C# couples a hose end to --
    * a tank: the midpoint of the footprint edge the end cell shares with it (HoseJointProbe: cell centre + half a step),
      except RM_LiquidTank west/east, which couples at TankPortGeometry.PortPoint (HoseMath.cs PortDz table);
    * a pump: only a side whose Position + FacingCell lies outside the footprint (RM_PumpPortMath.SideOf), at that
      cell's shared edge midpoint --
  map it into the texture (Graphic_Single, not rotatable: drawSize quad centred on the footprint centre + drawOffset)
  and require opaque art (alpha > 128) reaching the footprint edge there, spanning at least the hose's half-width (the
  filing's bar): the inward gap from the edge to the first opaque pixel is <= GAP_TOL cell at every sample within
  +-a quarter of the visible flat hose width (HoseMath.FlatVisible) of the port point.

Known reds are listed in KNOWN with the item that owns them: they print KNOWN and keep the suite green; a NEW red, or a
KNOWN entry that now passes (prune it), is a FAIL. Can-fail: the Modern tall tank art of fb34c9bc2d (before the
2026-10-22 lane fittings) must measure red on west/east.

  python3 selftest_hose_fittings.py            # gate (exit 1 on FAIL)
  python3 selftest_hose_fittings.py --table    # also print every port's gap
"""
import glob
import io
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HOSE_MATH = os.path.join(HERE, "Source", "Hose", "HoseMath.cs")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
GAP_TOL = 0.10          # cell; a coupler face may sit this far off the drawn edge (pump art 0.06-0.08 passes; the Modern float was ~0.3)
ALPHA = 128
SIDES = {"north": (0, 1), "east": (1, 0), "south": (0, -1), "west": (-1, 0)}
PRE_FIX_REV = "fb34c9bc2d"   # Modern tank art before the 2026-10-22 west/east lane fittings

# (def, look, side) -> the filed item that owns the red (measured 2026-10-22). A fixed entry goes red until pruned here.
_TALL = ("RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall")
KNOWN = {}
for _d in _TALL:
    for _l in LOOKS:
        KNOWN[(_d, _l, "south")] = "TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT"
        if _l != "Modern":
            KNOWN[(_d, _l, "west")] = KNOWN[(_d, _l, "east")] = "TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY"
for _l in LOOKS:
    KNOWN[("RM_LiquidTank", _l, "north")] = KNOWN[("RM_LiquidTank", _l, "south")] = "TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR"
    if _l != "Modern":
        KNOWN[("RM_UniversalCargoTank", _l, "north")] = "TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR"
# Pumping stations: south fittings drawn by art_source/TankPorts/port_fittings.py (PUMPSTATION_SOUTH_PORT_REDRAW_ALMOST_THERE).
# The tank fittings are drawn by the same script but not installed: every tank picture is owner-KEPT (art.py refuses).

fails = []
unmeasured = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def vec(s, n):
    if not s:
        return None
    v = [float(x) for x in s.strip().strip("()").split(",")]
    return v[:n]


# ------------------------------------------------------------------ defs
def load_defs():
    """Non-abstract tank/pump ThingDefs with ParentName inheritance resolved, and the ThingStyleDefs by defName."""
    named, things, styles = {}, [], {}
    for f in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag == "ThingDef":
                if d.get("Name"):
                    named[d.get("Name")] = d
                things.append(d)
            elif d.tag == "ThingStyleDef" and d.findtext("defName"):
                styles[d.findtext("defName")] = d

    def field(d, path):
        seen = 0
        while d is not None and seen < 20:
            v = d.findtext(path)
            if v is not None:
                return v
            d = named.get(d.get("ParentName"))
            seen += 1
        return None

    out = []
    for d in things:
        if d.get("Abstract", "").lower() == "true" or not d.findtext("defName"):
            continue
        tc = field(d, "thingClass") or ""
        kind = "tank" if tc.endswith("Building_LiquidTank") else "pump" if tc.endswith("Building_LiquidPump") else None
        if kind is None:
            continue
        name = d.findtext("defName")
        size = vec(field(d, "size") or "(1,1)", 2)
        base = {"texPath": field(d, "graphicData/texPath"), "graphicClass": field(d, "graphicData/graphicClass"),
                "drawSize": vec(field(d, "graphicData/drawSize") or "(1,1)", 2),
                "drawOffset": vec(field(d, "graphicData/drawOffset"), 3) or [0, 0, 0]}
        rot = (field(d, "rotatable") or "true").lower() != "false"
        looks = {}
        for look in LOOKS:
            s = styles.get("%s_%s" % (name, look))
            if s is None:
                continue
            g = s.find("graphicData")
            looks[look] = {"texPath": g.findtext("texPath"), "graphicClass": g.findtext("graphicClass"),
                           "drawSize": vec(g.findtext("drawSize"), 2) or base["drawSize"],
                           "drawOffset": vec(g.findtext("drawOffset"), 3) or [0, 0, 0]}
        if not looks:
            looks["(def)"] = base
        out.append({"def": name, "kind": kind, "size": [int(size[0]), int(size[1])], "rotatable": rot, "looks": looks})
    return out


# ------------------------------------------------------------------ textures
def tex_paths(tex_path):
    return sorted(glob.glob(os.path.join(REPO, "src", "RimMandrake", "*", "Textures", tex_path + ".png")))


def load_alpha(tex_path, rev=None):
    if rev is None:
        hits = tex_paths(tex_path)
        if not hits:
            return None, "no texture %s.png under src/RimMandrake/*/Textures" % tex_path
        return np.array(Image.open(hits[0]).convert("RGBA"))[..., 3], os.path.relpath(hits[0], REPO)
    rel = "src/RimMandrake/FlowWorks/Textures/%s.png" % tex_path
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, rel)], capture_output=True, timeout=120)
    if r.returncode != 0:
        return None, "git show %s:%s failed" % (rev, rel)
    return np.array(Image.open(io.BytesIO(r.stdout)).convert("RGBA"))[..., 3], "%s:%s" % (rev, rel)


# ------------------------------------------------------------------ the C#'s port points
def port_dz_table():
    m = re.search(r"PortDz = \{([^}]*)\}", open(HOSE_MATH).read())
    return [float(x) for x in m.group(1).split(",")] if m else None


def hose_half_width():
    """The fitting must span the hose's half-width: +-a quarter of HoseMath.FlatVisible about the port (returned: that quarter)."""
    src = open(HOSE_MATH).read()
    m = re.search(r"const double FlatVisible = ([0-9.]+)", src)
    return float(m.group(1)) / 4.0 if m else None


def ports(b, look, dz_table):
    """[(side, lane, (x, z))] in footprint coordinates (footprint minimum at 0,0), deduplicated per point."""
    w, h = b["size"]
    out, seen = [], set()
    if b["kind"] == "pump":
        px, pz = (w - 1) // 2, (h - 1) // 2          # Position of a north-facing thing (GenAdj.OccupiedRect inverse)
        for side, (dx, dz) in SIDES.items():
            cx, cz = px + dx, pz + dz
            if 0 <= cx < w and 0 <= cz < h:
                continue                              # Position + FacingCell inside the footprint: no end can lie there
            out.append((side, 0, (cx + 0.5 - dx * 0.5, cz + 0.5 - dz * 0.5)))
        return out
    for side, (dx, dz) in SIDES.items():
        cells = range(w) if dz else range(h)
        for lane in cells:
            if dz:   # end cell north/south of the footprint
                ex, ez = lane, (h if dz > 0 else -1)
            else:
                ex, ez = (w if dx > 0 else -1), lane
            pt = (ex + 0.5 - dx * 0.5, ez + 0.5 - dz * 0.5)
            if b["def"] == "RM_LiquidTank" and dx and dz_table and w == 2 and h == 2:
                i = LOOKS.index(look) if look in LOOKS else 0   # TankPortGeometry.PortPoint: unknown look -> index 0
                pt = (0.0 if dx < 0 else float(w), h / 2.0 + dz_table[i])
            if pt in seen:
                continue
            seen.add(pt)
            out.append((side, lane, pt))
    return out


# ------------------------------------------------------------------ measurement
def gap_at(alpha, g, size, pt, side, half_w):
    """Largest inward distance (cell) from the footprint edge at pt to the first opaque pixel, over the hose's width."""
    H, W = alpha.shape
    w, h = size
    dw, dh = g["drawSize"]
    ox, oz = g["drawOffset"][0], g["drawOffset"][2]
    cx, cz = w / 2.0 + ox, h / 2.0 + oz
    nx, nz = SIDES[side]
    tx, tz = -nz, nx
    step = min(dw / W, dh / H) / 2.0
    worst = 0.0
    for t in np.linspace(-half_w, half_w, 9):
        gap = None
        d = step / 2.0
        while d <= 0.6:
            x = pt[0] + tx * t - nx * d
            z = pt[1] + tz * t - nz * d
            u = int((x - (cx - dw / 2.0)) / dw * W)
            v = int(((cz + dh / 2.0) - z) / dh * H)
            if 0 <= u < W and 0 <= v < H and alpha[v, u] > ALPHA:
                gap = d - step / 2.0
                break
            d += step
        worst = max(worst, 0.6 if gap is None else gap)
    return worst


def measure(b, look, g, dz_table, half_w, rev=None):
    if g["graphicClass"] not in (None, "Graphic_Single"):
        return None, "graphicClass %s is not measured (Graphic_Single only)" % g["graphicClass"]
    alpha, src = load_alpha(g["texPath"], rev)
    if alpha is None:
        return None, src
    return [(side, lane, pt, gap_at(alpha, g, b["size"], pt, side, half_w)) for side, lane, pt in ports(b, look, dz_table)], src


def sanity(half_w):
    """The instrument can see: an all-opaque canvas is green everywhere, an empty one red everywhere."""
    b = {"def": "X", "kind": "tank", "size": [2, 2]}
    g = {"drawSize": [2, 2], "drawOffset": [0, 0, 0]}
    full, empty = np.full((128, 128), 255, np.uint8), np.zeros((128, 128), np.uint8)
    inset = np.zeros((128, 128), np.uint8)
    inset[16:112, 16:112] = 255                       # art stops 0.25 cell inside every edge
    p = ports(b, "Scrapper", None)
    check(len(p) == 8, "sanity: a 2x2 tank has 8 lane ports (%d)" % len(p))
    check(all(gap_at(full, g, b["size"], pt, s, half_w) <= GAP_TOL for s, _, pt in p), "sanity: opaque canvas -> every port green")
    check(all(gap_at(empty, g, b["size"], pt, s, half_w) > GAP_TOL for s, _, pt in p), "sanity: empty canvas -> every port red")
    gi = [gap_at(inset, g, b["size"], pt, s, half_w) for s, _, pt in p]
    check(all(abs(x - 0.25) < 0.03 for x in gi), "sanity: art inset 0.25 cell reads gap 0.25 (%s)" % ", ".join("%.2f" % x for x in gi))
    pp = ports({"def": "P", "kind": "pump", "size": [3, 2]}, "Scrapper", None)
    check([s for s, _, _ in pp] == ["south"], "sanity: a 3x2 pump takes a hose only on its south side (Position + FacingCell rule)")


def can_fail(defs, dz_table, half_w):
    tall = next((b for b in defs if b["def"] == "RM_LiquidTankTall"), None)
    if tall is None or "Modern" not in tall["looks"]:
        unmeasured.append("can-fail: no RM_LiquidTankTall Modern look")
        return
    res, src = measure(tall, "Modern", tall["looks"]["Modern"], dz_table, half_w, rev=PRE_FIX_REV)
    if res is None:
        unmeasured.append("can-fail: " + src)
        return
    we = [gap for side, _, _, gap in res if side in ("west", "east")]
    check(we and all(gap > GAP_TOL for gap in we),
          "can-fail: Modern tall tank art at %s (pre lane fittings) reads red west/east (gaps %s)" % (PRE_FIX_REV, ", ".join("%.2f" % x for x in we)))


def main():
    table = "--table" in sys.argv
    dz_table, half_w = port_dz_table(), hose_half_width()
    check(dz_table is not None and len(dz_table) == len(LOOKS), "TankPortGeometry.PortDz parsed from HoseMath.cs (%s)" % dz_table)
    check(half_w is not None, "fitting span +-%s cell (half the hose width, from HoseMath.FlatVisible)" % half_w)
    if dz_table is None or half_w is None:
        return 1
    sanity(half_w)
    defs = load_defs()
    names = sorted(b["def"] for b in defs)
    check({"RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall", "RM_LiquidPump"} <= set(names),
          "every hose-coupling building found in Defs (%s)" % ", ".join(names))
    for b in defs:
        check(not b["rotatable"], "%s is not rotatable (one facing to measure; a rotatable port building needs this gate extended)" % b["def"])
    can_fail(defs, dz_table, half_w)
    red, known_seen = {}, set()
    n = 0
    for b in sorted(defs, key=lambda x: x["def"]):
        for look, g in b["looks"].items():
            res, src = measure(b, look, g, dz_table, half_w)
            if res is None:
                check(False, "%s %s: %s" % (b["def"], look, src))
                continue
            for side, lane, pt, gap in res:
                n += 1
                ok = gap <= GAP_TOL
                if table:
                    print("      %-28s %-11s %-5s lane %d at (%.2f, %.2f): gap %.3f %s" % (b["def"], look, side, lane, pt[0], pt[1], gap, "" if ok else "RED"))
                if not ok:
                    red.setdefault((b["def"], look, side), []).append(gap)
    for key, gaps in sorted(red.items()):
        label = "%s %s %s: no drawn fitting at the hose port (gap %s cell > %.2f)" % (key[0], key[1], key[2], "/".join("%.2f" % x for x in gaps), GAP_TOL)
        if key in KNOWN:
            known_seen.add(key)
            print("KNOWN " + label + " -- " + KNOWN[key])
        else:
            check(False, label)
    for key in sorted(set(KNOWN) - known_seen):
        check(False, "KNOWN entry %s now passes: prune it from KNOWN (and close %s if it was the last)" % (" ".join(key), KNOWN[key]))
    print("hose fittings: %d ports measured, %d sides red (%d known)" % (n, len(red), len(known_seen)))
    if unmeasured:
        for u in unmeasured:
            print("UNMEASURED, not a pass or a fail: " + u)
    print("%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
