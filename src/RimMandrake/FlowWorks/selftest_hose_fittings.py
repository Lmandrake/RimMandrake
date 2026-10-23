#!/usr/bin/env python3
"""HOSE_FITTING_GATE_BUILD_BELIEVED_HOSEMATH -- every hose port the CODE defines has an opaque DRAWN fitting there (offline).

The joint check (northstar/joint_check.py, selftest_hose_ports.py) measures the hose end to the port the C# defines, never
to anything in the art, so on the Modern tall/IBC/XTall tanks it PASSED while the coupler floated ~0.3 cell off the drawn
wall (MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS, live art look 2026-10-22). This gate reads the INSTALLED textures instead:

  for every hose-coupling building (Building_LiquidTank / Building_LiquidPump defs) x look (ThingStyleDef <def>_<Look>)
  x side x lane, take the port point the C# couples a hose end to --
    * a tank: the midpoint of the footprint edge the end cell shares with it (HoseJointProbe: cell centre + half a step),
      except RM_LiquidTank west/east, which couples at TankPortGeometry.PortPoint (HoseMath.cs PortDz table), and the lanes
      in TankPortGeometry.MovedAlong (OFF_BODY_PORTS), which slide along their edge onto the drawn body;
    * a pump: only a side whose Position + FacingCell lies outside the footprint (RM_PumpPortMath.SideOf), at that
      cell's shared edge midpoint --
  map it into the texture (Graphic_Single, not rotatable: drawSize quad centred on the footprint centre + drawOffset)
  and require opaque art (alpha > 128) reaching the footprint edge there, spanning at least the hose's half-width (the
  filing's bar): the inward gap from the edge to the first opaque pixel is <= GAP_TOL cell at every sample within
  +-a quarter of the visible flat hose width (HoseMath.FlatVisible) of the port point.

UNDER-COUPLERS (owner ruling 2026-10-23, by card: "Make your couplers as needed, but have their art go UNDER the tank or pump
or other fixture"): wherever a hose couples to a non-pipe port the C# draws a collar + pipe BENEATH the fixture
(Machinery/UnderCouplerGeometry.cs, RM_UnderCouplers.cs). The gate composes that draw itself -- the constants parsed from
UnderCouplerGeometry.cs, the sprites read from Textures/RimMandrake/FlowWorks/Joins/<Look>/UnderCollar.png + UnderPipe.png,
placed by this file's own transform, never by the C# under test -- under the fixture's alpha, and a port passes when
  (a) the composite is opaque at the port within the hose's half-width (gap <= GAP_TOL), and
  (b) the coupler really goes beneath: along the port axis (centre and +-half-width) the fixture's own art turns opaque
      at least REACH_TOL before the coupler's inner end (no daylight between the coupler and the fixture).
The fixture-alone gap is still printed (--table, "raw").

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
REACH_TOL = 0.05       # cell the coupler must run on beneath opaque fixture art
UNDER_GEOM = os.path.join(HERE, "Source", "Machinery", "UnderCouplerGeometry.cs")
JOINS = os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Joins")
PRE_FIX_REV = "fb34c9bc2d"   # Modern tank art before the 2026-10-22 west/east lane fittings

# (def, look, side) -> the filed item that owns the red. A fixed entry goes red until pruned here.
# Drained 2026-10-23 by the under-couplers (TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY, TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT,
# TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR): every non-pipe port now has a coupler drawn beneath the fixture.
KNOWN = {}
# OFF_BODY_PORTS (delegated design ruling 2026-10-23) moved the ports that had no body on their axis (cargo tank upper W/E)
# or met a neighbour on open ground (tall/XTall corner lanes): TankPortGeometry.MovedAlong. Nothing is known red.

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


def moved_along():
    """TankPortGeometry.MovedAlong parsed from HoseMath.cs: "def|side|lane" -> the port's offset along its edge (cell)."""
    m = re.search(r"MovedAlong = new Dictionary<string, double>\s*\{(.*?)\};", open(HOSE_MATH).read(), re.S)
    return {k: float(v) for k, v in re.findall(r'\{ "([^"]+)", ([0-9.]+) \}', m.group(1))} if m else {}


def hose_half_width():
    """The fitting must span the hose's half-width: +-a quarter of HoseMath.FlatVisible about the port (returned: that quarter)."""
    src = open(HOSE_MATH).read()
    m = re.search(r"const double FlatVisible = ([0-9.]+)", src)
    return float(m.group(1)) / 4.0 if m else None


def hose_coupling_face():
    """Widest part of a plain (unwidened) hose coupling on a flat hose, cells: HoseMath.FittingSize(FlatVisible, PieceBand,
    CouplingMax) x CouplingMax -- the modern hose girth the under-coupler collar matches (owner 2026-10-23: "connectors that
    match the more modern pipe and hose sizes")."""
    src = open(HOSE_MATH).read()
    vals = {}
    for k in ("FlatVisible", "WrapK", "PieceBand", "CouplingMax"):
        m = re.search(r"\b%s = ([0-9.]+)" % k, src)
        if not m:
            return None
        vals[k] = float(m.group(1))
    v = vals["FlatVisible"]
    size = min(v / vals["PieceBand"], 0.95 * vals["WrapK"] * v / vals["CouplingMax"])
    return size * vals["CouplingMax"]


def ports(b, look, dz_table, moves=None):
    """[(side, lane, (x, z))] in footprint coordinates (footprint minimum at 0,0), deduplicated per point. moves: the
    MovedAlong table to apply (None = the C#'s, {} = every lane at its edge midpoint, as before OFF_BODY_PORTS)."""
    moves = moved_along() if moves is None else moves
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
            mv = moves.get("%s|%d|%d" % (b["def"], {"south": 0, "north": 1, "west": 2, "east": 3}[side], lane))
            if mv is not None:   # TankPortGeometry.HosePort: the lane slides along its edge onto the drawn body (OFF_BODY_PORTS)
                pt = (mv, pt[1]) if dz else (pt[0], mv)
            if b["def"] == "RM_LiquidTank" and dx and dz_table and w == 2 and h == 2:
                i = LOOKS.index(look) if look in LOOKS else 0   # TankPortGeometry.PortPoint: unknown look -> index 0
                pt = (0.0 if dx < 0 else float(w), h / 2.0 + dz_table[i])
            if pt in seen:
                continue
            seen.add(pt)
            out.append((side, lane, pt))
    return out


# ------------------------------------------------------------------ measurement
def fixture_opaque(alpha, g, size):
    """(x, z) -> the fixture's art is opaque there (Graphic_Single quad: drawSize centred on the footprint + drawOffset)."""
    H, W = alpha.shape
    w, h = size
    dw, dh = g["drawSize"]
    ox, oz = g["drawOffset"][0], g["drawOffset"][2]
    cx, cz = w / 2.0 + ox, h / 2.0 + oz

    def f(x, z):
        u = int((x - (cx - dw / 2.0)) / dw * W)
        v = int(((cz + dh / 2.0) - z) / dh * H)
        return 0 <= u < W and 0 <= v < H and alpha[v, u] > ALPHA
    return f, min(dw / W, dh / H) / 2.0


def gap_fn(opaque, step, pt, side, half_w):
    """Largest inward distance (cell) from the port point to the first opaque pixel, over the hose's width (0.6 = none)."""
    nx, nz = SIDES[side]
    tx, tz = -nz, nx
    worst = 0.0
    for t in np.linspace(-half_w, half_w, 9):
        gap = None
        d = step / 2.0
        while d <= 0.6:
            if opaque(pt[0] + tx * t - nx * d, pt[1] + tz * t - nz * d):
                gap = d - step / 2.0
                break
            d += step
        worst = max(worst, 0.6 if gap is None else gap)
    return worst


def gap_at(alpha, g, size, pt, side, half_w):
    """The fixture's art alone: largest inward gap from the port to its first opaque pixel over the hose's width."""
    f, step = fixture_opaque(alpha, g, size)
    return gap_fn(f, step, pt, side, half_w)


# ------------------------------------------------------------------ the under-coupler, composed here (never by the C#)
def under_geom():
    """CollarLength, CollarWidth, PipeWidth parsed from UnderCouplerGeometry.cs (None when the shape changed)."""
    m = re.search(r"const double CollarLength = ([0-9.]+), CollarWidth = ([0-9.]+), PipeWidth = ([0-9.]+);", open(UNDER_GEOM).read())
    return tuple(float(x) for x in m.groups()) if m else None


_SPRITES = {}


def under_sprites(look):
    """(collar alpha, pipe alpha) for the look a port draws in (an unstyled def: the pipes' default look, Scrapper)."""
    look = look if look in LOOKS else "Scrapper"
    if look not in _SPRITES:
        out = []
        for piece in ("UnderCollar", "UnderPipe"):
            f = os.path.join(JOINS, look, piece + ".png")
            out.append(np.array(Image.open(f).convert("RGBA"))[..., 3] if os.path.exists(f) else None)
        _SPRITES[look] = tuple(out)
    return _SPRITES[look]


REACH_CS = os.path.join(HERE, "Source", "Machinery", "UnderCouplerReach.cs")
SIDE_INDEX = {"south": 0, "north": 1, "west": 2, "east": 3}


def reach_table():
    """UnderCouplerReach.cs parsed: "def|look|side|lane" -> reach (cell; -1 = no body, no under-coupler)."""
    if not os.path.exists(REACH_CS):
        return None
    return {k: float(v) for k, v in re.findall(r'\{ "([^"]+)", (-?[0-9.]+) \}', open(REACH_CS).read())}


def table_reach(table, b, look, side, pt):
    """The C# table's reach for this port (the lane rule RM_UnderCouplers.Draw uses), or None when it is not listed."""
    along = pt[0] if side in ("north", "south") else pt[1]
    n = b["size"][0] if side in ("north", "south") else b["size"][1]
    lane = max(0, min(n - 1, int(np.floor(along))))
    return table.get("%s|%s|%d|%d" % (b["def"], look if look in LOOKS else "", SIDE_INDEX[side], lane))


def reach_of(pt, side, size, geo):
    """UnderCouplerGeometry.Reach, re-derived: port -> footprint centre line along the inward axis, >= the collar."""
    sx, sz = -SIDES[side][0], -SIDES[side][1]
    d = (size[0] / 2.0 - pt[0]) * sx if sx else (size[1] / 2.0 - pt[1]) * sz
    return max(geo[0], d)


def coupler_opaque(geo, sprites, pt, side, reach):
    """(x, z) -> the under-coupler is opaque there: collar quad [0, CL) x CW, pipe quad [CL/2, reach) x PW along the
    inward axis from the port point, each sprite's +u inward, +v (row 0) on the axis's left."""
    cl, cw, pw = geo
    ca, pa = sprites
    sx, sz = -SIDES[side][0], -SIDES[side][1]

    def f(x, z):
        a = (x - pt[0]) * sx + (z - pt[1]) * sz
        c = (x - pt[0]) * -sz + (z - pt[1]) * sx
        if 0 <= a < cl and abs(c) < cw / 2:
            H, W = ca.shape
            if ca[min(H - 1, int((cw / 2 - c) / cw * H)), min(W - 1, int(a / cl * W))] > ALPHA:
                return True
        if cl / 2 <= a < reach and abs(c) < pw / 2:
            H, W = pa.shape
            if pa[min(H - 1, int((pw / 2 - c) / pw * H)), min(W - 1, int((a - cl / 2) / (reach - cl / 2) * W))] > ALPHA:
                return True
        return False
    return f


def beneath_margin(fix, step, pt, side, half_w, reach):
    """How far the coupler runs on past the first opaque fixture pixel (cell; worst of centre and +-half-width lines);
    negative / None = daylight between the coupler's inner end and the fixture."""
    nx, nz = SIDES[side]
    tx, tz = -nz, nx
    worst = None
    for t in (-half_w, 0.0, half_w):
        d, hit = step / 2.0, None
        while d < reach:
            if fix(pt[0] + tx * t - nx * d, pt[1] + tz * t - nz * d):
                hit = d
                break
            d += step
        m = None if hit is None else reach - hit
        if m is None:
            return None
        worst = m if worst is None else min(worst, m)
    return worst


def measure(b, look, g, dz_table, half_w, rev=None, geo=None, reach_override=None, table=None, moves=None, clip=False):
    """[(side, lane, pt, raw gap, composed gap, beneath margin, reach, coupler-opaque fn)] -- composed/margin None without
    geo; reach -1 (no under-coupler: the table found no body on the axis) gives composed = raw, margin None."""
    if g["graphicClass"] not in (None, "Graphic_Single"):
        return None, "graphicClass %s is not measured (Graphic_Single only)" % g["graphicClass"], None
    alpha, src = load_alpha(g["texPath"], rev)
    if alpha is None:
        return None, src, None
    fix, step = fixture_opaque(alpha, g, b["size"])
    out = []
    for side, lane, pt in ports(b, look, dz_table, moves):
        raw = gap_fn(fix, step, pt, side, half_w)
        comp = margin = reach = cop = None
        if geo is not None:
            sprites = under_sprites(look)
            if sprites[0] is None or sprites[1] is None:
                return None, "no under-coupler sprites for look %s under %s" % (look, os.path.relpath(JOINS, REPO)), None
            reach = reach_override
            if reach is None and table is not None:
                reach = table_reach(table, b, look, side, pt)
            if reach is None and clip:   # the clipped reach measured afresh (under_coupler_reach.reach), not the C# table
                sys.path.insert(0, os.path.join(HERE, "art_source", "UnderCouplers"))
                import under_coupler_reach as ucr
                reach = ucr.reach(fix, step, pt, side, b["size"], geo)
            if reach is None:
                reach = reach_of(pt, side, b["size"], geo)
            if reach < 0:
                comp = raw
            else:
                cop = coupler_opaque(geo, sprites, pt, side, reach)
                comp = gap_fn(lambda x, z, c=cop: fix(x, z) or c(x, z), step, pt, side, half_w)
                margin = beneath_margin(fix, step, pt, side, half_w, reach)
        out.append((side, lane, pt, raw, comp, margin, reach, cop))
    return out, src, fix


def crossings(fix, size, coupled):
    """Grid points (0.02 cell) where two couplers' VISIBLE parts (coupler opaque, fixture art not) overlap, i.e. two pipes
    meeting on open ground outside the art. coupled: [(label, coupler-opaque fn)]."""
    if len(coupled) < 2:
        return []
    w, h = size
    hits = []
    for x in np.arange(-0.6, w + 0.6, 0.02):
        for z in np.arange(-0.6, h + 0.6, 0.02):
            if fix(x, z):
                continue
            on = [lab for lab, c in coupled if c(x, z)]
            if len(on) > 1:
                hits.append((round(x, 2), round(z, 2), tuple(on)))
    return hits


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


def can_fail(defs, dz_table, half_w, geo):
    tall = next((b for b in defs if b["def"] == "RM_LiquidTankTall"), None)
    if tall is None or "Modern" not in tall["looks"]:
        unmeasured.append("can-fail: no RM_LiquidTankTall Modern look")
        return
    res, src, _ = measure(tall, "Modern", tall["looks"]["Modern"], dz_table, half_w, rev=PRE_FIX_REV)
    if res is None:
        unmeasured.append("can-fail: " + src)
        return
    we = [r[3] for r in res if r[0] in ("west", "east")]
    check(we and all(gap > GAP_TOL for gap in we),
          "can-fail: Modern tall tank art at %s (pre lane fittings), fixture alone, reads red west/east (gaps %s)" % (PRE_FIX_REV, ", ".join("%.2f" % x for x in we)))
    # the beneath check can fail: a coupler cut back to its collar never reaches RM_LiquidTank's body north/south
    lt = next((b for b in defs if b["def"] == "RM_LiquidTank"), None)
    if lt is None or "Scrapper" not in lt["looks"]:
        unmeasured.append("can-fail: no RM_LiquidTank Scrapper look")
        return
    res, src, _ = measure(lt, "Scrapper", lt["looks"]["Scrapper"], dz_table, half_w, geo=geo, reach_override=geo[0])
    if res is None:
        unmeasured.append("can-fail: " + src)
        return
    ns = [r for r in res if r[0] in ("north", "south")]
    check(ns and all(r[4] <= GAP_TOL for r in ns) and all(r[5] is None or r[5] < REACH_TOL for r in ns),
          "can-fail: RM_LiquidTank Scrapper north/south with the coupler cut to its collar: port covered, but daylight before the body (margins %s)"
          % ", ".join("none" if r[5] is None else "%.2f" % r[5] for r in ns))
    # and on an empty fixture the coupler alone covers the port but goes beneath nothing
    b = {"def": "X", "kind": "tank", "size": [2, 2]}
    g = {"drawSize": [2, 2], "drawOffset": [0, 0, 0]}
    fix, step = fixture_opaque(np.zeros((128, 128), np.uint8), g, b["size"])
    sp = under_sprites("Scrapper")
    pt, side = (1.0, 2.0), "north"
    cop = coupler_opaque(geo, sp, pt, side, reach_of(pt, side, b["size"], geo))
    check(gap_fn(lambda x, z: fix(x, z) or cop(x, z), step, pt, side, half_w) <= GAP_TOL
          and beneath_margin(fix, step, pt, side, half_w, reach_of(pt, side, b["size"], geo)) is None,
          "sanity: the coupler alone covers the port of an empty fixture, and the beneath check reads it as daylight")


def can_fail_crossing(defs, dz_table, half_w, geo):
    """The judge's FIX can fail: run to the footprint centre line (the first build), the Modern tall tank's south and west
    pipes meet in a bare T on open ground."""
    tall = next((b for b in defs if b["def"] == "RM_LiquidTankTall"), None)
    if tall is None or "Modern" not in tall["looks"]:
        unmeasured.append("can-fail crossing: no RM_LiquidTankTall Modern look")
        return
    res, src, fix = measure(tall, "Modern", tall["looks"]["Modern"], dz_table, half_w, geo=geo, table={}, moves={})
    if res is None:
        unmeasured.append("can-fail crossing: " + src)
        return
    cross = crossings(fix, tall["size"], [("%s%d" % (r[0], r[1]), r[7]) for r in res if r[7] is not None])
    check(len(cross) > 0, "can-fail: with the pipes run to the centre line, the Modern tall tank's couplers meet on open ground (%d points)" % len(cross))
    # OFF_BODY_PORTS can fail: at the old edge midpoints (no MovedAlong), even clipped to the body, the corner pipes still meet
    res, src, fix = measure(tall, "Modern", tall["looks"]["Modern"], dz_table, half_w, geo=geo, table={}, moves={}, clip=True)
    cross = crossings(fix, tall["size"], [("%s%d" % (r[0], r[1]), r[7]) for r in res if r[7] is not None])
    check(len(cross) > 0, "can-fail: at the unmoved edge midpoints, clipped to the body, the Modern tall tank's corner couplers still meet on open ground (%d points)" % len(cross))
    uct = next((b for b in defs if b["def"] == "RM_UniversalCargoTank"), None)
    if uct is None or "Scrapper" not in uct["looks"]:
        unmeasured.append("can-fail upper port: no RM_UniversalCargoTank Scrapper look")
        return
    res, src, fix = measure(uct, "Scrapper", uct["looks"]["Scrapper"], dz_table, half_w, geo=geo, table={}, moves={}, clip=True)
    up = [r for r in res if r[0] in ("west", "east") and r[1] == 1]
    check(up and all(r[6] is not None and r[6] < 0 for r in up),
          "can-fail: at the unmoved z 1.5, the Scrapper cargo tank's upper west/east ports have no body on their axis (reach %s)"
          % ", ".join("%.2f" % r[6] for r in up))


def main():
    table = "--table" in sys.argv
    dz_table, half_w, geo = port_dz_table(), hose_half_width(), under_geom()
    check(dz_table is not None and len(dz_table) == len(LOOKS), "TankPortGeometry.PortDz parsed from HoseMath.cs (%s)" % dz_table)
    check(half_w is not None, "fitting span +-%s cell (half the hose width, from HoseMath.FlatVisible)" % half_w)
    check(geo is not None, "under-coupler collar/pipe sizes parsed from UnderCouplerGeometry.cs (%s)" % (geo,))
    if dz_table is None or half_w is None or geo is None:
        return 1
    check(geo[2] / 2 >= half_w and geo[1] >= geo[2], "under-coupler pipe spans the hose's half-width and the collar is the wider part")
    face = hose_coupling_face()
    check(face is not None and geo[1] <= face + 1e-9,
          "UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK: under-coupler collar (%.4f cell) no wider than a plain hose coupling face (%s cell)"
          % (geo[1], "%.4f" % face if face else None))
    sanity(half_w)
    defs = load_defs()
    names = sorted(b["def"] for b in defs)
    check({"RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall", "RM_LiquidPump"} <= set(names),
          "every hose-coupling building found in Defs (%s)" % ", ".join(names))
    for b in defs:
        check(not b["rotatable"], "%s is not rotatable (one facing to measure; a rotatable port building needs this gate extended)" % b["def"])
    can_fail(defs, dz_table, half_w, geo)
    rt = reach_table()
    check(rt is not None and len(rt) > 0, "UnderCouplerReach.cs parsed (%d ports)" % len(rt or {}))
    gen = subprocess.run([sys.executable, os.path.join(HERE, "art_source", "UnderCouplers", "under_coupler_reach.py")],
                         capture_output=True, text=True, timeout=600)
    check(gen.returncode == 0, "UnderCouplerReach.cs is what under_coupler_reach.py measures from the installed art (%s)" % gen.stdout.strip()[-120:])
    can_fail_crossing(defs, dz_table, half_w, geo)
    red, known_seen = {}, set()
    n = raw_red = 0
    for b in sorted(defs, key=lambda x: x["def"]):
        for look, g in b["looks"].items():
            res, src, fix = measure(b, look, g, dz_table, half_w, geo=geo, table=rt or {})
            if res is None:
                check(False, "%s %s: %s" % (b["def"], look, src))
                continue
            for side, lane, pt, raw, comp, margin, reach, cop in res:
                n += 1
                raw_red += raw > GAP_TOL
                ok = comp <= GAP_TOL and margin is not None and margin >= REACH_TOL
                if table:
                    print("      %-28s %-11s %-5s lane %d at (%.2f, %.2f): raw gap %.3f, reach %.3f, with coupler %.3f, beneath by %s %s"
                          % (b["def"], look, side, lane, pt[0], pt[1], raw, reach, comp, "none" if margin is None else "%.2f" % margin, "" if ok else "RED"))
                if not ok:
                    red.setdefault((b["def"], look, side), []).append((comp, margin))
            # every port coupled at once: no two couplers' visible parts may meet outside the art (the judge's bare T)
            cross = crossings(fix, b["size"], [("%s%d" % (r[0], r[1]), r[7]) for r in res if r[7] is not None])
            if cross:
                red[(b["def"], look, "crossing")] = [(len(cross), None)]
            else:
                check(True, "%s %s: no two under-couplers meet on open ground outside the art" % (b["def"], look))
    for key, v in sorted(red.items()):
        label = "%s %s %s: the under-coupler leaves the port uncovered or stops short of the fixture (gap/beneath %s; tol %.2f/%.2f)" % (
            key[0], key[1], key[2], ", ".join("%.2f/%s" % (c, "none" if m is None else "%.2f" % m) for c, m in v) if key[2] != "crossing" else "%d grid points where two couplers meet outside the art" % v[0][0], GAP_TOL, REACH_TOL)
        if key in KNOWN:
            known_seen.add(key)
            print("KNOWN " + label + " -- " + KNOWN[key])
        else:
            check(False, label)
    for key in sorted(set(KNOWN) - known_seen):
        check(False, "KNOWN entry %s now passes: prune it from KNOWN (and close %s if it was the last)" % (" ".join(key), KNOWN[key]))
    print("hose fittings: %d ports measured, %d with no fixture art at the port (covered by under-couplers), %d sides red (%d known)"
          % (n, raw_red, len(red), len(known_seen)))
    if unmeasured:
        for u in unmeasured:
            print("UNMEASURED, not a pass or a fail: " + u)
    print("%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
