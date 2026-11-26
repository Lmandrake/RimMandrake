"""The offline twin of the pit draw (Source/Superdeep/RM_ExcavationWalls.cs + Source/RM_PitReliefMath.cs): pits drawn as
RELATIVE TERRAIN. RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (owner by card 2026-11-20, "In 0.1.0, full rebuild").

His words (walk 2026-11-20, his own stepped pit, rows 3.5 m, 3.5 m, 5.5 m): "Clearly you have not implemented the pit visuals
as relative terrain representation, just "pit or no pit" floor. That won't do. Need more generalization."

The law, one rule for every square, canal or pit, at any depth:
  heights     every square has a floor height in notches (0.5 m) below ground: 0 undug, its hollow depth when dug. A square
              off the map, or a natural liquid square, reads as level with its neighbour (no wall into a lake or the map edge).
  seen        a square under a pit cover shows its deck (walking height 0); a COVERED square none of whose 8 neighbours shows a
              hole is CONCEALED (its lid prints the ground, Building_PitCover): it draws no pit art at all.
  edges       every edge between two 4-neighbours of different height is drawn by the DEEPER square, from the drop:
                north neighbour shallower: a rim line and a north face (the face the camera sees), height NorthFace(exposed);
                south neighbour shallower: a south lining (the near edge; its face points away), SouthLining(drop);
                west / east shallower:     a side line and a side face strip, SideFace(exposed).
              exposed = drop less the liquid standing in the deeper square (RM_UnderLiquid.Exposed).
  corners     every convex corner of a shallower block inside a deeper area is closed: where a DIAGONAL neighbour is shallower
              and both squares beside it are not, the deeper square draws the outline's missing quadrant, and for a north
              diagonal (the corner the camera sees) the side face continued down beside the block's face (a corner piece).
  floor       every dug floor is shaded by its own depth, darker the deeper, over the whole dig range (0.5 m .. 20 m):
              floor brightness B(d) = terrain colour T(d) x (1 - FloorShade(d)); strictly falling, so two floors at
              different depths never draw alike (his 3.5 m and 5.5 m rows), and a canal reads darker than plain gravel
              (his walk: "a darker floor would likely help").
  face foot   a face keeps telling drops apart past the tallest face (2.5 m): a dark foot, FaceFootShade(exposed), growing
              by a log of the drop, so a 3.5 m and a 5.5 m wall of the same height read apart.
  redraw      the art of a square depends only on its 3x3 neighbourhood (heights and seen heights), so a change of one
              square's height or deck re-meshes that square and its 8 neighbours (MapMeshDirty with adjacent cells), and
              nothing farther. Every change of height redraws, at every depth (the old draw redrew only on a change of
              floor terrain, and every floor past 2 m is one terrain).

Coordinates: grids are lists of rows, NORTH FIRST (row 0 is the north edge), columns west to east. A segment's "edge" is the
pair of squares it lies between (a diagonal pair for a corner). Everything is a pure function: no game, no Verse.

    python3 src/RimMandrake/FlowWorks/model/pitdraw.py            the sweep (exit 0 when every invariant holds)
"""
from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "Source"
FACE_MATH = SRC / "RM_WallFaceMath.cs"


def _cs_array(text: str, name: str) -> list[float]:
    m = re.search(name + r"\s*=\s*\{([^}]*)\}", text)
    if not m:
        raise ValueError("RM_WallFaceMath.cs has no table " + name)
    return [float(x.strip().rstrip("f")) for x in m.group(1).split(",") if x.strip()]


def _cs_const(text: str, name: str) -> float:
    m = re.search(r"const float " + name + r"\s*=\s*([0-9.]+)f", text)
    if not m:
        raise ValueError("RM_WallFaceMath.cs has no constant " + name)
    return float(m.group(1))


# the face tables are the shipped ones (one source of truth: RM_WallFaceMath.cs)
_FM = FACE_MATH.read_text(encoding="utf-8")
NORTH_BY_DROP = _cs_array(_FM, "NorthByDrop")
SIDE_BY_DROP = _cs_array(_FM, "SideByDrop")
SOUTH_LINING_BY_DROP = _cs_array(_FM, "SouthLiningByDrop")
RIM_LINE = _cs_const(_FM, "RimLine")
SIDE_LINE = _cs_const(_FM, "SideLine")

# ── the new numbers (C#: RM_PitReliefMath; the parity golden table carries them) ──
# Floor terrain colour by depth band (Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml: plain Gravel, then 0.78, 0.69, 0.64;
# every depth past 2 m is RM_Channel_Superdeep's 0.64) [measured, the defs]. Deep and Superdeep were lifted from 0.58 and 0.38
# by RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR so the stepped rule's lifted ladder can be drawn by a black shade;
# this law (the relief off, and under liquid) keeps its brightness: the shade takes the difference.
TERRAIN_COLOUR = [1.0, 1.0, 0.78, 0.69, 0.64]
# Floor brightness wanted at 0.5, 1, 1.5, 2 m: even steps of 0.14 down to the 2 m floor (which keeps its 0.38, so a 2 m pit
# looks as it did), so a 0.5 m canal is 20% darker than plain gravel (his walk 2026-11-20 part 2, "a darker floor would likely
# help"). Past 2 m, B = 0.38 x (1 - FLOOR_LOG_K x log2(d / 4)), never under FLOOR_MIN of 0.38: a fixed share darker at every
# doubling of depth (2 -> 4 m 22%, 4 -> 8 m a further 22 points), so 3.5 m vs 5.5 m differ by 17% [the bar: two depths never
# alike; the rate is a choice for his look].
FLOOR_BRIGHTNESS_SHALLOW = [1.0, 0.80, 0.66, 0.52, 0.38]
FLOOR_LOG_K = 0.22
FLOOR_MIN = 0.25
# Face foot past the tallest face (index 5 of NorthByDrop, 2.5 m): FACE_FOOT_K x log2(e / 5), at most FACE_FOOT_MAX (reached
# only past 20 m, the deepest dig) [a choice for his look].
FACE_FOOT_FROM = 5.0
FACE_FOOT_K = 0.22
FACE_FOOT_MAX = 0.70
DEEPEST = 40   # RM_ExcavationDepth.MaxDigCeiling: 20 m


def face_at(table: list[float], exposed: float) -> float:
    """RM_UnderLiquid.FaceAt: the whole-notch entries exactly, a straight line between them, the last entry past the end."""
    if exposed <= 0:
        return 0.0
    last = len(table) - 1
    if exposed >= last:
        return table[last]
    lo = int(exposed)
    t = exposed - lo
    return table[lo] + (table[lo + 1] - table[lo]) * t


def north_face(exposed: float) -> float:
    return face_at(NORTH_BY_DROP, exposed)


def side_face(exposed: float) -> float:
    return face_at(SIDE_BY_DROP, exposed)


def south_lining(drop: int) -> float:
    if drop <= 0:
        return 0.0
    return SOUTH_LINING_BY_DROP[min(drop, len(SOUTH_LINING_BY_DROP) - 1)]


def exposed(my: int, nb: int, level: float) -> float:
    """RM_UnderLiquid.Exposed: the drop to the neighbour less the liquid standing here, never negative."""
    drop = my - nb
    if drop <= 0:
        return 0.0
    return max(0.0, drop - max(0.0, level))


def floor_brightness(d: int) -> float:
    if d <= 0:
        return 1.0
    if d <= 4:
        return FLOOR_BRIGHTNESS_SHALLOW[d]
    return FLOOR_BRIGHTNESS_SHALLOW[4] * max(FLOOR_MIN, 1.0 - FLOOR_LOG_K * math.log2(d / 4.0))


def floor_shade(d: int) -> float:
    """RM_PitReliefMath.FloorShade: the black alpha over the dug floor (its terrain) at depth d notches."""
    if d <= 0:
        return 0.0
    t = TERRAIN_COLOUR[min(d, 4)]
    return round(max(0.0, 1.0 - floor_brightness(d) / t), 5)


def face_foot_shade(e: float) -> float:
    """RM_PitReliefMath.FaceFootShade: the black alpha at the foot of a face of exposed drop e (0 at its top)."""
    if e <= FACE_FOOT_FROM:
        return 0.0
    return round(min(FACE_FOOT_MAX, FACE_FOOT_K * math.log2(e / FACE_FOOT_FROM)), 5)


def redraws_on_change(before: int, after: int) -> bool:
    """RM_PitReliefMath.RedrawsOnDepthChange: every change of a square's height re-meshes it and its 8 neighbours."""
    return before != after


# ── the planner ──────────────────────────────────────────────────

N, S, W, E = (-1, 0), (1, 0), (0, -1), (0, 1)
NW, NE, SW, SE = (-1, -1), (-1, 1), (1, -1), (1, 1)


def _at(grid, r, c, default):
    if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
        return grid[r][c]
    return default


def seen_height(heights, covered, r, c):
    """RM_SuspensionUnderpass.SeenDepthAt: a covered square shows its deck (ground, 0); -1 off the grid."""
    if not (0 <= r < len(heights) and 0 <= c < len(heights[0])):
        return -1
    h = heights[r][c]
    return 0 if h > 0 and covered and covered[r][c] else h


def concealed(heights, covered, r, c) -> bool:
    """Building_PitCover's ground print: a covered square none of whose 8 neighbours shows a hole (RM_PitCoverLookMath.ShowsArt
    false). It draws no pit art (RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER)."""
    if not covered or not covered[r][c] or heights[r][c] <= 0:
        return False
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if (dr or dc) and seen_height(heights, covered, r + dr, c + dc) > 0:
                return False
    return True


def corner_piece(d: int, dn: int, dside: int, ddiag: int, level: float):
    """RM_PitReliefMath.CornerPiece: (width, height) of the side face continued into a north corner of a square at depth d whose
    north and side neighbours are not shallower and whose north diagonal is; (0, 0) when there is none."""
    if d <= 0 or dn < d or dside < d or ddiag >= d:
        return 0.0, 0.0
    e = exposed(d, ddiag, level)
    w, h = side_face(e), north_face(e)
    if w <= 0 or h <= 0:
        return 0.0, 0.0
    return w, h


def corner_line(d: int, da: int, db: int, ddiag: int) -> bool:
    """RM_PitReliefMath.ClosesCorner: the outline's missing quadrant at a diagonal: the diagonal is shallower and neither square
    beside it is (so no line of this square's reaches the corner)."""
    return d > 0 and da >= d and db >= d and ddiag < d


def plan_cell(heights, levels, covered, r, c):
    """Everything the walls layer draws on one square: a list of segments, each a dict with kind, edge and its sizes; and
    the floor shade rectangles. Empty for an undug or a concealed square."""
    d = heights[r][c]
    if d <= 0 or concealed(heights, covered, r, c):
        return [], []
    lv = levels[r][c] if levels else 0.0

    def nb(dr, dc):
        return _at(heights, r + dr, c + dc, d)

    hn, hs, hw, he = nb(*N), nb(*S), nb(*W), nb(*E)
    segs = []
    me = (r, c)
    en, ew_, ee = exposed(d, hn, lv), exposed(d, hw, lv), exposed(d, he, lv)
    h = north_face(en)
    ww, ew = side_face(ew_), side_face(ee)
    if d > hn:
        segs.append({"kind": "rim_line", "edge": (me, (r - 1, c)), "size": RIM_LINE})
        if h > 0:
            segs.append({"kind": "north_face", "edge": (me, (r - 1, c)), "size": h, "foot": face_foot_shade(en),
                         "rect": (0.0, 1.0 - h, 1.0, 1.0)})
    if d > hs:
        segs.append({"kind": "south_lining", "edge": (me, (r + 1, c)), "size": south_lining(d - hs)})
    if d > hw:
        segs.append({"kind": "side_line_w", "edge": (me, (r, c - 1)), "size": SIDE_LINE})
        if ww > 0:
            segs.append({"kind": "side_face_w", "edge": (me, (r, c - 1)), "size": ww, "rect": (0.0, 0.0, ww, 1.0)})
    if d > he:
        segs.append({"kind": "side_line_e", "edge": (me, (r, c + 1)), "size": SIDE_LINE})
        if ew > 0:
            segs.append({"kind": "side_face_e", "edge": (me, (r, c + 1)), "size": ew, "rect": (1.0 - ew, 0.0, 1.0, 1.0)})
    # corners: x0,z0,x1,z1 in cell units, z up (north) from the square's south edge
    wnw, hnw = corner_piece(d, hn, hw, nb(*NW), lv)
    wne, hne = corner_piece(d, hn, he, nb(*NE), lv)
    if wnw > 0:
        segs.append({"kind": "corner_nw", "edge": (me, (r - 1, c - 1)), "size": hnw, "rect": (0.0, 1.0 - hnw, wnw, 1.0)})
    if wne > 0:
        segs.append({"kind": "corner_ne", "edge": (me, (r - 1, c + 1)), "size": hne, "rect": (1.0 - wne, 1.0 - hne, 1.0, 1.0)})
    for kind, (dr, dc), a, b in (("corner_line_nw", NW, hn, hw), ("corner_line_ne", NE, hn, he),
                                 ("corner_line_sw", SW, hs, hw), ("corner_line_se", SE, hs, he)):
        dd = nb(dr, dc)
        if corner_line(d, a, b, dd):
            size = RIM_LINE if dr < 0 else south_lining(d - dd)
            segs.append({"kind": kind, "edge": (me, (r + dr, c + dc)), "size": size})
    return segs, floor_rects(ww, ew, h, wnw, hnw, wne, hne)


def floor_rects(ww, ew, h, wnw, hnw, wne, hne):
    """RM_PitReliefMath.FloorRects: the floor left between the faces, as at most two rectangles (x0, z0, x1, z1): below the
    corner pieces the full width between the side faces, beside them the part between the pieces. Never under a face."""
    top = 1.0 - h
    x0, x1 = ww, 1.0 - ew
    if x1 <= x0 or top <= 0:
        return []
    hc = max(hnw, hne)
    if hc <= 0:
        return [(x0, 0.0, x1, top)]
    zc = min(top, 1.0 - hc)
    out = [(x0, 0.0, x1, zc)] if zc > 0 else []
    ux0, ux1 = max(x0, wnw), min(x1, 1.0 - wne)
    if ux1 > ux0 and top > zc:
        out.append((ux0, zc, ux1, top))
    return out


def plan(heights, levels=None, covered=None):
    """Every segment the walls layer draws over a grid of heights (rows north first). Each has "cell" and "edge"."""
    out = []
    for r in range(len(heights)):
        for c in range(len(heights[0])):
            segs, _ = plan_cell(heights, levels, covered, r, c)
            for s in segs:
                s["cell"] = (r, c)
                out.append(s)
    return out


def redraws_on_deepen(before, after, cov_before=None, cov_after=None) -> bool:
    """A grid cut deeper (or a lid laid or lifted) redraws every square whose art changed: each changed square re-meshes with
    its 8 neighbours, and every square whose plan changed lies in one of those blocks (the locality the sweep proves)."""
    def cov(g, r, c):
        return bool(g and g[r][c])
    changed = [(r, c) for r in range(len(before)) for c in range(len(before[0]))
               if before[r][c] != after[r][c] or cov(cov_before, r, c) != cov(cov_after, r, c)]
    if not all(redraws_on_change(before[r][c], after[r][c]) for r, c in changed if before[r][c] != after[r][c]):
        return False
    dirty = {(r + dr, c + dc) for r, c in changed for dr in (-1, 0, 1) for dc in (-1, 0, 1)}
    for r in range(len(before)):
        for c in range(len(before[0])):
            if (_key(plan_cell(before, None, cov_before, r, c)) != _key(plan_cell(after, None, cov_after, r, c))
                    and (r, c) not in dirty):
                return False
    return True


def _key(cell_plan):
    segs, rects = cell_plan
    return (tuple(sorted((s["kind"], round(s["size"], 6)) for s in segs)), tuple(rects))


# ── the lit faces of one square, dry and drowned (the pale frame: RIMMANDRAKE_DIM_FLOWWORKS_DROWNED_WALLS_PALE_FRAME_IN_WATER) ──
# Every face carries the cream wall light (RM_FaceMaterial.ShadeMat at the wall-light alpha). A point washed twice reads pale:
# that was the frame in water (SideUnder drew its strip and wash the square's full height, under the dry north face, and the
# drowned far-wall band ran across the side strips). Each layer is a convex polygon of (x, z) in cell units.

def lit_polys(d, hn, hw, he, hnw, hne, lv, wet_view=True, old=False):
    """The polygons the walls layer lights on one square: dry faces and corner pieces. Under a clear liquid (wet_view) the
    square is drawn as the DRY pit (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE: one sheet over the dry pit,
    model/water_surface.py), so its lit faces are the faces at level 0. old=True draws the drowned parts as the code before the
    pale-frame fix did (plain rectangles across the square: the instrument's red case)."""
    polys = []
    if wet_view and lv > 0 and not old:
        lv = 0.0
    en, ew_, ee = exposed(d, hn, lv), exposed(d, hw, lv), exposed(d, he, lv)
    h, ww, ew = north_face(en), side_face(ew_), side_face(ee)
    top = 1.0
    if d > hn and h > 0:
        polys.append(("north_face", [(ww, top - h), (0.0, top), (1.0, top), (1.0 - ew, top - h)]))
    if d > hw and ww > 0:
        inner = top - h if h > 0 else top
        polys.append(("side_face_w", [(0.0, 0.0), (0.0, top), (ww, inner), (ww, 0.0)]))
    if d > he and ew > 0:
        inner = top - h if h > 0 else top
        polys.append(("side_face_e", [(1.0 - ew, 0.0), (1.0 - ew, inner), (1.0, top), (1.0, 0.0)]))
    wnw, hnwp = corner_piece(d, hn, hw, hnw, lv)
    wne, hnep = corner_piece(d, hn, he, hne, lv)
    if wnw > 0:
        polys.append(("corner_nw", corner_poly(False, wnw, hnwp)))
    if wne > 0:
        polys.append(("corner_ne", corner_poly(True, wne, hnep)))
    if not wet_view or lv <= 0 or not old:
        return polys
    # old: the drowned parts as plain rectangles across the whole square (the pale frame)
    h_full = north_face(exposed(d, hn, 0.0))
    w_full_w, w_full_e = side_face(exposed(d, hw, 0.0)), side_face(exposed(d, he, 0.0))
    floor_top = 1.0 - h_full
    drowned = h_full - h
    if drowned > 0.001:
        polys.append(("drowned_band", _rect(0.0, floor_top, 1.0, floor_top + drowned)))
    for east, wf, wd in ((False, w_full_w, ww), (True, w_full_e, ew)):
        if wf - wd > 0.001:
            x0, x1 = (1.0 - wf, 1.0 - wd) if east else (wd, wf)
            polys.append(("side_under_e" if east else "side_under_w", _rect(x0, 0.0, x1, 1.0)))
    return polys


def corner_poly(east: bool, w: float, h: float):
    """RM_PitReliefMath.CornerPiece's shape: the side face continued down by h beside the block, its foot mitred at 45
    degrees away from the block (vanilla's bevel corners)."""
    m = min(w, h)
    if east:
        return [(1.0 - w, 1.0 - h + m), (1.0 - w, 1.0), (1.0, 1.0), (1.0, 1.0 - h)]
    return [(0.0, 1.0 - h), (0.0, 1.0), (w, 1.0), (w, 1.0 - h + m)]


def _rect(x0, z0, x1, z1):
    return [(x0, z0), (x0, z1), (x1, z1), (x1, z0)]


def _inside(poly, x, z):
    sign = 0
    n = len(poly)
    for i in range(n):
        (ax, az), (bx, bz) = poly[i], poly[(i + 1) % n]
        cr = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if abs(cr) < 1e-9:
            return False          # on an edge two faces share: neither layer counts it (a sample, not an area)
        sg = 1 if cr > 0 else -1
        if sign == 0:
            sign = sg
        elif sg != sign:
            return False
    return True


def max_wash(polys, steps=24):
    """The most layers of wall light over any sampled point of the square (cell-centred samples, never on an edge)."""
    worst, where = 0, None
    for i in range(steps):
        for j in range(steps):
            x, z = (i + 0.5) / steps, (j + 0.5) / steps
            k = [name for name, p in polys if _inside(p, x, z)]
            if len(k) > worst:
                worst, where = len(k), (round(x, 3), round(z, 3), k)
    return worst, where


# ── the sweep: the range of situations, read by the bars' own checks ──

def _differing_edges(h):
    out = []
    for r in range(len(h)):
        for c in range(len(h[0])):
            for dr, dc in ((1, 0), (0, 1)):
                r2, c2 = r + dr, c + dc
                if r2 < len(h) and c2 < len(h[0]) and h[r][c] != h[r2][c2]:
                    out.append(((r, c), (r2, c2)))
    return out


def _convex_corners(h):
    """Every (deeper square, shallower diagonal) where both squares beside the diagonal are at least as deep."""
    out = []
    for r in range(len(h)):
        for c in range(len(h[0])):
            d = h[r][c]
            for dr, dc in (NW, NE, SW, SE):
                r2, c2 = r + dr, c + dc
                if not (0 <= r2 < len(h) and 0 <= c2 < len(h[0])):
                    continue
                if d > 0 and h[r2][c2] < d and h[r + dr][c] >= d and h[r][c + dc] >= d:
                    out.append(((r, c), (r2, c2)))
    return out


def check_grid(h, levels=None, covered=None):
    """The bar's checks on one grid: (failures list, cases read)."""
    fails = []
    segs = plan(h, levels, covered)
    have = {tuple(sorted(s["edge"])) for s in segs}
    hidden = {(r, c) for r in range(len(h)) for c in range(len(h[0])) if concealed(h, covered, r, c)}
    cases = 0
    for a, b in _differing_edges(h):
        cases += 1
        deeper = a if h[a[0]][a[1]] > h[b[0]][b[1]] else b
        if deeper in hidden:
            continue
        if tuple(sorted((a, b))) not in have:
            fails.append(("edge_without_segment", a, b, h[a[0]][a[1]], h[b[0]][b[1]]))
    pieces = {(s["cell"], s["kind"]) for s in segs}
    for a, b in _convex_corners(h):
        cases += 1
        if a not in hidden and tuple(sorted((a, b))) not in have:
            fails.append(("corner_left_open", a, b))
        # a north diagonal (the corner the camera sees) with a dry drop shows the side face continued down beside it
        if a not in hidden and b[0] < a[0]:
            lv = levels[a[0]][a[1]] if levels else 0.0
            if exposed(h[a[0]][a[1]], h[b[0]][b[1]], lv) > 0:
                kind = "corner_nw" if b[1] < a[1] else "corner_ne"
                if (a, kind) not in pieces:
                    fails.append(("corner_without_its_face", a, b))
    for s in segs:
        if s["cell"] in hidden:
            fails.append(("art_on_concealed_square", s["cell"], s["kind"]))
        x0, z0, x1, z1 = s.get("rect", (0, 0, 1, 1))
        if not (0 <= x0 <= x1 <= 1 and 0 <= z0 <= z1 <= 1):
            fails.append(("rect_outside_square", s["cell"], s["kind"], s.get("rect")))
    for r in range(len(h)):
        for c in range(len(h[0])):
            cs, rects = plan_cell(h, levels, covered, r, c)
            faces = [s["rect"] for s in cs if "rect" in s]
            for fr in rects:
                cases += 1
                for f in faces:
                    if _overlap(fr, f) > 1e-9:
                        fails.append(("floor_shade_over_a_face", (r, c), fr, f))
            # the faces of one square never stack: a corner piece only where no north or side face is
            kinds = {s["kind"] for s in cs}
            if "corner_nw" in kinds and ("north_face" in kinds or "side_face_w" in kinds):
                fails.append(("corner_piece_over_a_face", (r, c)))
            if "corner_ne" in kinds and ("north_face" in kinds or "side_face_e" in kinds):
                fails.append(("corner_piece_over_a_face", (r, c)))
    return fails, cases


def _overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    hgt = min(a[3], b[3]) - max(a[1], b[1])
    return w * hgt if w > 0 and hgt > 0 else 0.0


def _ring(field):
    w = len(field[0])
    return [[0] * (w + 2)] + [[0] + list(row) + [0] for row in field] + [[0] * (w + 2)]


def challenge_grids():
    """The scenes that matter by name: his pit, the review map's holes, the old failures, the L and the terraces."""
    return {
        "his_pit_2026_11_20": _ring([[7, 7, 7], [7, 7, 7], [11, 11, 11]]),
        "stepped_east_west": _ring([[4, 8, 12], [4, 8, 12], [4, 8, 12]]),
        "l_shaped_pit": _ring([[4, 0, 0], [4, 4, 4], [4, 4, 4]]),
        "island_in_a_pit": _ring([[8, 8, 8], [8, 0, 8], [8, 8, 8]]),
        "bowl": _ring([[2, 3, 2], [3, 9, 3], [2, 3, 2]]),
        "terraces": _ring([[1, 1, 1, 1], [2, 2, 2, 2], [4, 4, 4, 4], [8, 8, 8, 8], [16, 16, 16, 16]]),
        "checker_deep": _ring([[40, 1, 40], [1, 40, 1], [40, 1, 40]]),
        "map_edge_pit": [[6, 6, 0], [6, 9, 0], [0, 0, 0]],   # off the grid reads level: no wall into the map edge
        "canal_into_pit": _ring([[1, 1, 1, 8, 8]]),
    }


def sweep(seed=20261120, random_grids=4000):
    """Every regime: all neighbour height pairs (dry and wet), every one-square change (locality), the floor and face-foot
    ramps over the whole dig range, random fields with and without covers, and the named challenge scenes. Prints, per
    check, its worst value, its limit and its cases."""
    rows = []
    fails = []

    # 1. every height pair, every direction, dry and at every quarter-notch level: the edge is drawn by the deeper square only
    n = 0
    worst_overreach = 0.0
    for d in range(0, DEEPEST + 1):
        for nbh in range(0, DEEPEST + 1):
            for lq in range(0, 4 * max(d, 1) + 1, 2):
                lv = lq / 4.0
                g = [[nbh, nbh, nbh], [nbh, d, nbh], [nbh, nbh, nbh]]
                levels = [[0.0] * 3, [0.0, lv, 0.0], [0.0] * 3]
                segs, rects = plan_cell(g, levels, None, 1, 1)
                n += 1
                kinds = {s["kind"] for s in segs}
                want_lines = d > nbh
                if want_lines != ({"rim_line", "south_lining", "side_line_w", "side_line_e"} <= kinds):
                    fails.append(("pair_lines", d, nbh, lv, sorted(kinds)))
                if not want_lines and segs:
                    fails.append(("art_from_the_shallower_square", d, nbh, lv, sorted(kinds)))
                # a face never taller than the square, the faces never meet across it
                h = next((s["size"] for s in segs if s["kind"] == "north_face"), 0.0)
                lin = next((s["size"] for s in segs if s["kind"] == "south_lining"), 0.0)
                worst_overreach = max(worst_overreach, h + lin, 2 * next((s["size"] for s in segs if s["kind"] == "side_face_w"), 0.0))
                # dry part only: water covers the foot (exposed falls as the level rises)
                if lv >= d - nbh and d > nbh and h > 0:
                    fails.append(("face_above_drowned_wall", d, nbh, lv, h))
    rows.append(("height pairs x levels: lines exactly on the deeper side", 0, 0, n))
    rows.append(("height pairs: tallest face + lining, or both side faces (cells)", worst_overreach, 1.0, n))
    if worst_overreach > 1.0:
        fails.append(("faces_overreach_the_square", worst_overreach))

    # 2. the floor ramp: strictly darker with depth over the whole dig range; his two floors apart
    bs = [floor_brightness(d) for d in range(0, DEEPEST + 1)]
    worst_step = min(bs[d] - bs[d + 1] for d in range(0, DEEPEST))
    rows.append(("floor brightness falls with every notch (smallest fall)", worst_step, 0.0, DEEPEST))
    if worst_step <= 0:
        fails.append(("floor_not_strictly_darker", worst_step))
    his = 1 - floor_brightness(11) / floor_brightness(7)
    rows.append(("his floors 3.5 m vs 5.5 m, relative contrast", his, 0.10, 1))
    if his < 0.10:
        fails.append(("his_floors_alike", his))
    worst_metre = min(1 - floor_brightness(d + 2) / floor_brightness(d) for d in range(1, 16 - 1))
    rows.append(("floors 1 m apart, down to 8 m: smallest relative contrast", worst_metre, 0.05, 14))
    if worst_metre < 0.05:
        fails.append(("floors_one_metre_apart_alike", worst_metre))
    for d in range(0, DEEPEST + 1):
        a = floor_shade(d)
        if not (0 <= a < 1):
            fails.append(("floor_shade_out_of_range", d, a))
    # the 2 m floor keeps its look: its terrain under its shade draws 0.38 (the shade was 0 while the terrain itself was 0.38)
    drawn2 = (1.0 - floor_shade(4)) * TERRAIN_COLOUR[4]
    rows.append(("2 m floor keeps its look (drawn at 4 notches)", drawn2, 0.38, 1))
    if abs(drawn2 - 0.38) > 1e-4:
        fails.append(("two_metre_floor_changed", drawn2))

    # 3. the face foot: never lighter for a bigger drop, and drops past 2.5 m apart
    es = [x / 4.0 for x in range(0, 4 * DEEPEST + 1)]
    fs = [face_foot_shade(e) for e in es]
    mono = all(fs[i] <= fs[i + 1] for i in range(len(fs) - 1))
    rows.append(("face foot never lighter for a bigger drop", int(mono), 1, len(es)))
    if not mono:
        fails.append(("face_foot_not_monotone",))
    # a fixed step per doubling of the drop (the eye reads ratios), so 1 m apart is told apart down to 8 m, and a
    # doubling anywhere in the dig range
    apart = min(face_foot_shade(e + 2) - face_foot_shade(e) for e in range(5, 16 - 1))
    rows.append(("face foot: drops 1 m apart from 2.5 m to 8 m (smallest alpha step)", apart, 0.02, 11))
    if apart < 0.02:
        fails.append(("face_foot_drops_alike", apart))
    dbl = min(face_foot_shade(min(2 * e, DEEPEST)) - face_foot_shade(e) for e in range(5, DEEPEST // 2 + 1))
    rows.append(("face foot: a doubled drop, 2.5 m to 20 m (smallest alpha step)", dbl, 0.15, DEEPEST // 2 - 4))
    if dbl < 0.15:
        fails.append(("face_foot_doubled_drop_alike", dbl))
    if max(fs) > FACE_FOOT_MAX + 1e-9:
        fails.append(("face_foot_over_max", max(fs)))

    # 3b. the wall light: no point of any square washed twice, dry or at any level (the pale frame in water)
    nw_cases = 0
    worst_wash = (0, None)
    for d in range(1, 13):
        for hn in sorted({0, max(0, d - 1), max(0, d - 3), d, d + 2}):
            for hw in sorted({0, max(0, d - 2), d}):
                for he in sorted({0, max(0, d - 4), d}):
                    for hnw in sorted({0, d}):
                        for hne in sorted({0, d}):
                            for lq in range(0, 4 * d + 1, 2):
                                lv = lq / 4.0
                                k, where = max_wash(lit_polys(d, hn, hw, he, hnw, hne, lv), steps=12)
                                nw_cases += 1
                                if k > worst_wash[0]:
                                    worst_wash = (k, (d, hn, hw, he, hnw, hne, lv, where))
    rows.append(("wall light layers over any point, dry and wet (most)", worst_wash[0], 1, nw_cases))
    if worst_wash[0] > 1:
        fails.append(("point_washed_twice", worst_wash))
    # the instrument sees: the pre-rebuild drowned parts wash a corner twice (its red case, kept as a challenge)
    k_old, _ = max_wash(lit_polys(4, 0, 0, 0, 0, 0, 1.0, old=True))
    rows.append(("challenge: the old drowned parts (2 m pit, 0.5 m water) wash a point twice", k_old, 2, 1))
    if k_old < 2:
        fails.append(("wash_instrument_blind", k_old))

    # 4. locality: one square changed, every square whose art changed is within the 3x3 the redraw dirties
    rng = random.Random(seed)
    nloc = 0
    for _ in range(1500):
        g = [[rng.choice([0, 0, 1, 2, 4, 7, 11, rng.randint(0, DEEPEST)]) for _ in range(6)] for _ in range(6)]
        r, c = rng.randrange(6), rng.randrange(6)
        after = [row[:] for row in g]
        cb = [[rng.random() < 0.5 for _ in range(6)] for _ in range(6)] if rng.random() < 0.5 else None
        ca = [row[:] for row in cb] if cb else None
        if ca and rng.random() < 0.5:
            ca[r][c] = not ca[r][c]          # a lid laid or lifted
        else:
            after[r][c] = rng.randint(0, DEEPEST)
        nloc += 1
        if not redraws_on_deepen(g, after, cb, ca):
            fails.append(("art_changed_outside_the_redraw", g, (r, c), after[r][c]))
    rows.append(("one square re-cut or re-lidded: art changes only within its 3x3", 0, 0, nloc))
    # every change redraws, at every depth (the old draw: only on a floor terrain change)
    nred = sum(1 for b in range(DEEPEST + 1) for a in range(DEEPEST + 1) if a != b)
    if not all(redraws_on_change(b, a) for b in range(DEEPEST + 1) for a in range(DEEPEST + 1) if a != b):
        fails.append(("a_change_without_redraw",))
    rows.append(("every height change redraws", 0, 0, nred))

    # 5. random fields with and without covers
    nf = 0
    ncases = 0
    before = len(fails)
    for i in range(random_grids):
        w, hgt = rng.randint(2, 7), rng.randint(2, 7)
        base = rng.choice([0, 1, 4, 7, 12])
        g = [[max(0, base + rng.choice([0, 0, 0, -1, 1, -3, 4, rng.randint(-8, 20)])) for _ in range(w)] for _ in range(hgt)]
        if rng.random() < 0.5:
            g = _ring(g)
        levels = None
        if rng.random() < 0.4:
            levels = [[rng.choice([0.0, 0.0, 0.25, 1.0, 2.5]) if v else 0.0 for v in row] for row in g]
            levels = [[min(lv, v) for lv, v in zip(lr, gr)] for lr, gr in zip(levels, g)]
        covered = None
        if rng.random() < 0.4:
            covered = [[rng.random() < 0.7 for _ in row] for row in g]
        f, k = check_grid(g, levels, covered)
        nf += 1
        ncases += k
        fails.extend(f[:3])
    rows.append(("random fields (2..9 squares a side, wet, covered): edges, corners, overlaps", len(fails) - before, 0, ncases))

    # 6. the named scenes
    for name, g in challenge_grids().items():
        f, k = check_grid(g)
        rows.append(("scene " + name, len(f), 0, k))
        fails.extend(f)
    # a wholly covered pit draws nothing; one open square makes every lid round it show its planks and walls
    pit = _ring([[4, 4, 4], [4, 4, 4], [4, 4, 4]])
    allcov = [[bool(v) for v in row] for row in pit]
    drawn = plan(pit, None, allcov)
    rows.append(("wholly covered 3x3 pit: segments drawn", len(drawn), 0, 9))
    if drawn:
        fails.append(("covered_pit_shows_walls", len(drawn)))
    onelid = [row[:] for row in allcov]
    onelid[2][2] = False
    if not plan(pit, None, onelid):
        fails.append(("open_square_in_covered_pit_draws_nothing",))
    return rows, fails


def main():
    rows, fails = sweep()
    for label, worst, limit, cases in rows:
        print("%-78s worst %-10s limit %-6s cases %d" % (label, round(worst, 5) if isinstance(worst, float) else worst, limit, cases))
    for f in fails[:20]:
        print("FAIL", f)
    print("%s: %d failures" % ("PASS" if not fails else "FAIL", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
