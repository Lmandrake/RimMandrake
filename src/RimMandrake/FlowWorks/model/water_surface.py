#!/usr/bin/env python3
"""water_surface.py: the offline model of ONE water surface over a dug square (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE).

Owner, walk of 2026-11-25: "Station 6 still shows odd pit walls under water ... Look at the corners", "I suspect you're applying
multiple layers over each other instead of calculating a single one". The live census (jawa/cell_draw_census) counted, on station
22's corner square, nine sheet pieces at alpha 0..229, a deep-water tint layer and a black tint over 1.29 of the square; and the
drowned walls drawn as plain rectangles in a paler light than the dry pit's.

The rule this model fixes, and Source/Superdeep/RM_ExcavationWalls.cs + RM_PitReliefMath.SheetPieces implement:
  * A square under a clear liquid is drawn as the DRY pit (the plan at level 0: faces, floor, shade, lip bands, cast shadow).
  * Over it lies ONE sheet: one colour and one alpha per square, the same for every square of one body (one level). Its extent is
    the dry pit cut by the waterline on every face: the whole floor, the part of the north face below the line y = W.T (W the
    plan at the liquid's level), the part of each side face beyond W.L / W.R from its edge, the part of each corner piece beyond
    W.CnwW / W.CneW. The pieces never overlap and, with the dry parts above the line, tile the square.
  * A shut sluice whose across-neighbour on one side holds no liquid carries the sheet only on its wet half (the gate parts it).
  * A dry dug square bordering a square whose terrain is a liquid reprints its own floor, so vanilla's terrain edge fade of the
    liquid never lies over it (the drained side of a sluice, stations 7 to 10).

Coordinates: x east, z NORTH (0 at the square's south edge), as the C# draws. Depths in notches (0.5 m).

    python3 src/RimMandrake/FlowWorks/model/water_surface.py          sweep every case; exit 0 all hold, 1 a rule broke (named)
"""
import itertools
import math
import sys

# ── ports of RM_PitReliefMath (the stepped rule) ─────────────────────────────────────────────────────────────────────────
STEP_NORTH = [0.0, 0.7 * 0.12, 0.7 * 0.23, 0.7 * 0.35, 0.7 * 0.50]
STEP_H_SLOPE, STEP_H_LOG = 0.085, 0.078
STEP_SIDE = [0.0, 0.06, 0.11, 0.17, 0.23, 0.29]
STEP_W_TOP, STEP_P, STEP_DEEPEST = 0.46, 0.6, 20.0


def face_at(table, e):
    if e <= 0:
        return 0.0
    last = len(table) - 1
    if e >= last:
        return table[last]
    lo = int(e)
    t = e - lo
    return table[lo] + (table[lo + 1] - table[lo]) * t


def step_h(n):
    if n <= 0:
        return 0.0
    if n <= 4:
        return face_at(STEP_NORTH, n)
    z, h2 = n * 0.5, STEP_NORTH[4]
    if z <= 4.0:
        return h2 + STEP_H_SLOPE * (z - 2.0)
    return h2 + 2.0 * STEP_H_SLOPE + STEP_H_LOG * math.log(min(z, STEP_DEEPEST) / 4.0, 2.0)


def _rise(z):
    return (1.0 - (2.5 / z) ** STEP_P) / (1.0 - (2.5 / STEP_DEEPEST) ** STEP_P)


def step_w(n):
    if n <= 0:
        return 0.0
    z = n * 0.5
    if z <= 2.5:
        return face_at(STEP_SIDE, n)
    return STEP_SIDE[5] + (STEP_W_TOP - STEP_SIDE[5]) * _rise(min(z, STEP_DEEPEST))


def plan(d, n, s, w, e, nw, ne, lv):
    """PlanStep: the sizes (cells) of the faces of a square at depth d whose floor is at de = d - lv."""
    p = dict(T=0.0, L=0.0, R=0.0, Lt=0.0, Rt=0.0, HvL=0.0, HvR=0.0, CnwW=0.0, CnwH=0.0, CneW=0.0, CneH=0.0)
    if d <= 0:
        return p
    de = d - (lv if lv > 0 else 0.0)
    p["T"] = step_h(de) - step_h(n) if n < de else 0.0
    p["L"] = step_w(de) - step_w(w) if w < de else 0.0
    p["R"] = step_w(de) - step_w(e) if e < de else 0.0
    p["Lt"] = step_w(n) - step_w(w) if n < de and w < n else 0.0
    p["Rt"] = step_w(n) - step_w(e) if n < de and e < n else 0.0
    p["HvL"] = step_h(min(w, de)) - step_h(n) if n < de and w > n else 0.0
    p["HvR"] = step_h(min(e, de)) - step_h(n) if n < de and e > n else 0.0
    if n >= d and w >= d and nw < de:
        p["CnwW"], p["CnwH"] = step_w(de) - step_w(nw), step_h(de) - step_h(nw)
    if n >= d and e >= d and ne < de:
        p["CneW"], p["CneH"] = step_w(de) - step_w(ne), step_h(de) - step_h(ne)
    return p


def floor_rects(ww, ew, h, wnw, hnw, wne, hne):
    """FloorRects, as (x0, z0, x1, z1) rectangles."""
    top = 1.0 - h
    x0, x1 = ww, 1.0 - ew
    if x1 <= x0 or top <= 0:
        return []
    hc = max(hnw, hne)
    if hc <= 0:
        return [(x0, 0.0, x1, top)]
    zc = min(top, 1.0 - hc)
    out = []
    if zc > 0:
        out.append((x0, 0.0, x1, zc))
    ux0, ux1 = max(x0, wnw), min(x1, 1.0 - wne)
    if ux1 > ux0 and top > zc:
        out.append((ux0, zc, ux1, top))
    return out


def rect_poly(r):
    x0, z0, x1, z1 = r
    return [(x0, z0), (x0, z1), (x1, z1), (x1, z0)]


def faces(p):
    """The face polygons of a plan, z up: {'N': ..., 'W': ..., 'E': ..., 'CNW': ..., 'CNE': ...} (absent when 0)."""
    out = {}
    t = p["T"]
    if t > 0:
        yd = [(p["Lt"], 0.0), (1 - p["Rt"], 0.0), (1 - p["Rt"], p["HvR"]), (1 - p["R"], t), (p["L"], t), (p["Lt"], p["HvL"])]
        out["N"] = [(x, 1.0 - y) for x, y in yd]
    for east in (False, True):
        full = p["R"] if east else p["L"]
        if full <= 0:
            continue
        top = p["Rt"] if east else p["Lt"]
        hv = p["HvR"] if east else p["HvL"]
        if t <= 0:
            yd = [(0.0, 1.0), (0.0, 0.0), (full, 0.0), (full, 1.0)]
        else:
            yd = [(0.0, 1.0), (0.0, 0.0), (top, 0.0), (top, hv), (full, t), (full, 1.0)]
        q = [((1.0 - x) if east else x, 1.0 - y) for x, y in yd]
        if east:
            q.reverse()
        out["E" if east else "W"] = q
    for east in (False, True):
        w, h = (p["CneW"], p["CneH"]) if east else (p["CnwW"], p["CnwH"])
        if w <= 0:
            continue
        m = min(w, h)
        if east:
            out["CNE"] = [(1 - w, 1 - h + m), (1 - w, 1.0), (1.0, 1.0), (1.0, 1 - h)]
        else:
            out["CNW"] = [(0.0, 1 - h), (0.0, 1.0), (w, 1.0), (w, 1 - h + m)]
    return out


# ── polygon helpers ─────────────────────────────────────────────────────────────────────────────────────────────────
def clip(poly, inside, cross):
    """Sutherland-Hodgman against one half-plane: inside(p) -> bool, cross(p, q) -> the crossing point."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        pin, qin = inside(p), inside(q)
        if pin:
            out.append(p)
        if pin != qin:
            out.append(cross(p, q))
    return out


def clip_x_ge(poly, x0):
    return clip(poly, lambda p: p[0] >= x0, lambda p, q: (x0, p[1] + (q[1] - p[1]) * (x0 - p[0]) / (q[0] - p[0])))


def clip_x_le(poly, x1):
    return clip(poly, lambda p: p[0] <= x1, lambda p, q: (x1, p[1] + (q[1] - p[1]) * (x1 - p[0]) / (q[0] - p[0])))


def clip_z_le(poly, z1):
    return clip(poly, lambda p: p[1] <= z1, lambda p, q: (p[0] + (q[0] - p[0]) * (z1 - p[1]) / (q[1] - p[1]), z1))


def clip_z_ge(poly, z0):
    return clip(poly, lambda p: p[1] >= z0, lambda p, q: (p[0] + (q[0] - p[0]) * (z0 - p[1]) / (q[1] - p[1]), z0))


def area(poly):
    if len(poly) < 3:
        return 0.0
    a = 0.0
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        a += p[0] * q[1] - q[0] * p[1]
    return abs(a) * 0.5


def inside_poly(poly, x, z):
    """Point in a convex-or-star polygon (even-odd), boundary excluded by the caller's margin."""
    c = False
    for i, p in enumerate(poly):
        q = poly[i - 1]
        if (p[1] > z) != (q[1] > z):
            xc = p[0] + (q[0] - p[0]) * (z - p[1]) / (q[1] - p[1])
            if x < xc:
                c = not c
    return c


# ── the rule ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def sheet_pieces(d, n, s, w, e, nw, ne, lv, wet_x=(0.0, 1.0), wet_z=(0.0, 1.0)):
    """The ONE sheet over a square: polygons, never overlapping. Empty when no liquid stands (lv <= 0).
    wet_x / wet_z: the part of the square a shut sluice leaves wet (sluice_half)."""
    if lv <= 0 or d <= 0:
        return []
    f = plan(d, n, s, w, e, nw, ne, 0.0)
    wp = plan(d, n, s, w, e, nw, ne, lv)
    pieces = [rect_poly(r) for r in floor_rects(f["L"], f["R"], f["T"], f["CnwW"], f["CnwH"], f["CneW"], f["CneH"])]
    fc = faces(f)
    if "N" in fc:
        pieces.append(clip_z_le(fc["N"], 1.0 - wp["T"]))
    if "W" in fc:
        pieces.append(clip_x_ge(fc["W"], wp["L"]))
    if "E" in fc:
        pieces.append(clip_x_le(fc["E"], 1.0 - wp["R"]))
    if "CNW" in fc:
        pieces.append(clip_x_ge(fc["CNW"], wp["CnwW"]))
    if "CNE" in fc:
        pieces.append(clip_x_le(fc["CNE"], 1.0 - wp["CneW"]))
    out = []
    for q in pieces:
        q = clip_z_le(clip_z_ge(clip_x_le(clip_x_ge(q, wet_x[0]), wet_x[1]), wet_z[0]), wet_z[1])
        if area(q) > 1e-7:
            out.append(q)
    return out


def sluice_half(rot, wet_low, wet_high):
    """The part of a shut sluice's square that carries the sheet. rot 1/3 (side view) parts west (low) from east (high);
    rot 0/2 (face on) parts south (low) from north (high). wet_low / wet_high: the across-neighbour on that side holds liquid.
    Only one wet side halves it; both or neither leave the whole square."""
    if wet_low == wet_high:
        return (0.0, 1.0), (0.0, 1.0)
    half = (0.0, 0.5) if wet_low else (0.5, 1.0)
    if rot in (1, 3):
        return half, (0.0, 1.0)
    return (0.0, 1.0), half


def reprints_floor(dug, holds_liquid, any_neighbour_liquid_terrain):
    """A dry dug square bordering liquid terrain prints its own floor over vanilla's edge fade of that liquid."""
    return bool(dug and not holds_liquid and any_neighbour_liquid_terrain)


def sheet_alpha(clarity, level_m, wet_alpha):
    """The square's one alpha: the liquid's own (1 - Seen at the level) composed with the wet-ground darkening, as one overlay."""
    seen = 1.0 if clarity <= 0 else clarity ** level_m   # a stand-in for RM_UnderLiquid.Seen: monotone in level, same per level
    sa = 1.0 - seen
    return 1.0 - (1.0 - wet_alpha) * (1.0 - sa)


# ── the independent oracle: a point's true depth, from the dry plan, by inverting the face curves ───────────────────────────
def _inv(fn, target, hi=40.0):
    lo = 0.0
    for _ in range(60):
        mid = (lo + hi) * 0.5
        if fn(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) * 0.5


def depth_at(d, n, s, w, e, nw, ne, x, z):
    """The depth (notches) of the dry-pit surface seen at (x, z): None on a region boundary (within 1e-3) or outside every region."""
    f = plan(d, n, s, w, e, nw, ne, 0.0)
    fc = faces(f)
    hits = []
    for k, q in fc.items():
        if inside_poly(q, x, z):
            hits.append(k)
    if len(hits) > 1:
        return None
    if not hits:
        for r in floor_rects(f["L"], f["R"], f["T"], f["CnwW"], f["CnwH"], f["CneW"], f["CneH"]):
            if r[0] < x < r[2] and r[1] < z < r[3]:
                return float(d)
        return None
    k = hits[0]
    if k == "N":
        return _inv(step_h, (1.0 - z) + step_h(n))
    if k == "W":
        return _inv(step_w, x + step_w(w))
    if k == "E":
        return _inv(step_w, (1.0 - x) + step_w(e))
    if k == "CNW":
        return _inv(step_w, x + step_w(nw))
    return _inv(step_w, (1.0 - x) + step_w(ne))


# ── the sweep ───────────────────────────────────────────────────────────────────────────────────────────────────────────
GRID = 24


def samples():
    for i in range(GRID):
        for j in range(GRID):
            yield (i + 0.5) / GRID, (j + 0.37) / GRID


def near_edge(polys, x, z, eps=2e-3):
    for q in polys:
        for i, p in enumerate(q):
            r = q[i - 1]
            dx, dz = r[0] - p[0], r[1] - p[1]
            L2 = dx * dx + dz * dz
            if L2 <= 0:
                continue
            t = max(0.0, min(1.0, ((x - p[0]) * dx + (z - p[1]) * dz) / L2))
            if math.hypot(x - (p[0] + t * dx), z - (p[1] + t * dz)) < eps:
                return True
    return False


def check_square(nb, lv, fails, label):
    d, n, s, w, e, nw, ne = nb
    pieces = sheet_pieces(d, n, s, w, e, nw, ne, lv)
    f = plan(d, n, s, w, e, nw, ne, 0.0)
    region = list(faces(f).values()) + [rect_poly(r) for r in floor_rects(f["L"], f["R"], f["T"], f["CnwW"], f["CnwH"], f["CneW"], f["CneH"])]
    de = d - lv
    for x, z in samples():
        if near_edge(pieces + region, x, z):
            continue
        cover = sum(1 for q in pieces if inside_poly(q, x, z))
        if cover > 1:
            fails.append("%s lv=%.2f: %d sheet pieces overlap at (%.3f, %.3f)" % (label, lv, cover, x, z))
            return
        z_true = depth_at(d, n, s, w, e, nw, ne, x, z)
        if z_true is None:
            continue
        wet = lv > 0 and z_true > de + 1e-4
        if abs(z_true - de) < 1e-3:
            continue
        if wet != (cover == 1):
            fails.append("%s lv=%.2f: at (%.3f, %.3f) depth %.3f vs waterline %.3f: sheet %s, truth %s"
                         % (label, lv, x, z, z_true, de, cover == 1, wet))
            return


def pit_grids():
    """The walk map's pit shapes and the stepped ones: dict name -> {(x, z): depth}."""
    out = {}
    def rect(x0, z0, w, h, d, g=None):
        g = {} if g is None else g
        for x in range(x0, x0 + w):
            for z in range(z0, z0 + h):
                g[(x, z)] = d
        return g
    for d in (1, 2, 3, 4, 10):
        out["3x3 d%d" % d] = rect(0, 0, 3, 3, d)
    out["5x1 d1 (E/W sluice)"] = rect(0, 0, 5, 1, 1)
    out["1x5 d1 (N/S sluice)"] = rect(0, 0, 1, 5, 1)
    out["1x1 d2 in 4 (hole in a hole)"] = rect(0, 0, 3, 3, 4, rect(1, 1, 1, 1, 8))
    out["L d4/d2"] = rect(0, 0, 4, 2, 2, rect(0, 2, 2, 2, 4))
    out["stepped 4 beside 8"] = rect(0, 0, 2, 3, 4, rect(2, 0, 2, 3, 8))
    out["inner block d2 in d6 (corner pieces)"] = rect(0, 0, 5, 5, 6, rect(2, 2, 1, 1, 2))
    return out


def neighbours(g, x, z):
    D = lambda a, b: g.get((a, b), 0)
    return (D(x, z), D(x, z + 1), D(x, z - 1), D(x - 1, z), D(x + 1, z), D(x - 1, z + 1), D(x + 1, z + 1))


def sweep():
    fails = []
    squares = 0
    for name, g in pit_grids().items():
        dmax = max(g.values())
        levels = sorted(set([0.25 * k for k in range(1, int(dmax * 4) + 1)]))
        for lv in levels:
            # one body at one level: every square whose floor lies below the surface holds liquid lv - (dmax - d)
            alphas = set()
            for (x, z), d in g.items():
                own = lv - (dmax - d)
                if own <= 0:
                    if sheet_pieces(*neighbours(g, x, z), own):
                        fails.append("%s: a square holding no liquid draws a sheet" % name)
                    continue
                check_square(neighbours(g, x, z), own, fails, "%s (%d,%d)" % (name, x, z))
                alphas.add(round(sheet_alpha(0.6, lv * 0.5, 0.15), 9))
                squares += 1
            if len(alphas) > 1:
                fails.append("%s lv=%.2f: one body draws %d alphas" % (name, lv, len(alphas)))
        # the surface is continuous across square edges inside one pit (two wet squares side by side)
        for (x, z), d in g.items():
            for dx, dz in ((1, 0), (0, 1)):
                o = (x + dx, z + dz)
                if g.get(o) != d:
                    continue
                lv = d
                a = sheet_pieces(*neighbours(g, x, z), lv)
                b = sheet_pieces(*neighbours(g, *o), lv)
                for k in range(1, 20):
                    t = k / 20.0
                    pa = (1 - 1e-4, t) if dx else (t, 1 - 1e-4)
                    pb = (1e-4, t) if dx else (t, 1e-4)
                    ia = any(inside_poly(q, *pa) for q in a)
                    ib = any(inside_poly(q, *pb) for q in b)
                    if ia != ib and not near_edge(a, *pa) and not near_edge(b, *pb):
                        fails.append("%s: the surface breaks between (%d,%d) and (%d,%d) at %.2f" % (name, x, z, o[0], o[1], t))
                        break
    # a sluice in both axes, each side wet and dry
    for rot in (0, 1, 2, 3):
        for wl, wh in itertools.product((False, True), repeat=2):
            wx, wz = sluice_half(rot, wl, wh)
            pieces = sheet_pieces(1, 0, 0, 1, 1, 0, 0, 1.0, wx, wz) if rot in (1, 3) else sheet_pieces(1, 1, 1, 0, 0, 0, 0, 1.0, wx, wz)
            a = sum(area(q) for q in pieces)
            axis_low = (0.25, 0.5) if rot in (1, 3) else (0.5, 0.25)
            axis_high = (0.75, 0.5) if rot in (1, 3) else (0.5, 0.75)
            low_in = any(inside_poly(q, *axis_low) for q in pieces)
            high_in = any(inside_poly(q, *axis_high) for q in pieces)
            want_low = wl or not wh
            want_high = wh or not wl
            if low_in != want_low or high_in != want_high:
                fails.append("sluice rot %d low %s high %s: sheet low %s high %s (area %.3f)" % (rot, wl, wh, low_in, high_in, a))
    # the drained square's floor reprint
    for dug, holds, nbr in itertools.product((False, True), repeat=3):
        if reprints_floor(dug, holds, nbr) != (dug and not holds and nbr):
            fails.append("reprint truth table at dug=%s holds=%s nbr=%s" % (dug, holds, nbr))
    return squares, fails


if __name__ == "__main__":
    squares, fails = sweep()
    for f in fails[:40]:
        print("FAIL", f)
    print("water_surface: %d wet squares swept, %d failures" % (squares, len(fails)))
    sys.exit(1 if fails else 0)
