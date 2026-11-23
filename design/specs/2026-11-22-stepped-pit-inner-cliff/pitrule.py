"""The stepped-pit rule as a pure function (RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM).

His words (2026-11-22): "it can't go all the way up to the original pit outside... that's what's making it look like a
standing wall. The inner "cliff" should only go part way up the side walls. It's all about the side wall interactions. They
need to extend deeper into the pit where it is deeper, and the cliff edge within the pit needs to only come up as far as it
should to make it clear what it is."

The rule. Every square has a floor depth z (metres below ground; 0 is undug ground). Two offset functions of depth, both
strictly rising over the whole dig range (0 .. 20 m), place every point of a wall on screen:
  H(z)  how far south of its top edge a north-wall point at depth z shows (the face the camera sees);
  W(z)  how far in from its edge a side-wall point at depth z shows.
A wall between a shallow floor (depth a) and a deep floor (depth b) is drawn in the deeper square only, and shows the part
of the wall between a and b: a north face of height H(b) - H(a), a side strip of width W(b) - W(a). So:
  - the whole stack of faces down a stepped pit adds up to H(deepest) and W(deepest): a side wall is wider beside the deeper
    floor ("extends deeper into the pit where it is deeper");
  - an inner riser's top edge (depth a) meets each side wall at that wall's depth-a line, W(a) - W(ground beside), never at
    the ground rim: the upper part of the side wall runs on unbroken past the riser ("only part way up the side walls");
  - the riser's lip line (black, as today) runs only between those two points.
Every number a square draws comes from its own depth and its 8 neighbours' depths (the 3x3 locality the game's redraw keeps).

Shading (all multiplicative, so it survives any floor terrain laid later):
  depth value  K(z): every surface point at depth z is darkened to K(z) of its terrain (the sky a pit floor sees shrinks
               with depth); each level of a stepped pit is a clearly different value;
  sun          a fixed sun (azimuth, elevation): Lambert light on each wall by its facing, and cast shadows from a ray march
               over the drawn height field (screen space), so the rim's shadow falls on the floor below it, a riser's lip
               casts onto the deeper floor, and a deeper drop casts a longer shadow.

Coordinates: grids are lists of rows, NORTH FIRST; in a square, x runs 0 (west) .. 1 (east) and y runs 0 (north edge) .. 1
(south edge), "y down". Pure functions: no game, no Verse.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "2026-11-23-pit-floor-depth-ladder"))
import ladder as _LADDER  # noqa: E402

# ── the two offset functions ──────────────────────────────────────────────
# Up to 2.5 m W is today's table exactly and H is today's at NORTH_SCALE (RM_WallFaceMath NorthByDrop / SideByDrop), so a
# single-depth pit at 2.5 m or less keeps today's side walls (his walk: stations 34 to 39 "look good and indicate their depth well"). Past 2.5 m
# they keep rising to 20 m (today's stop at 2.5 m is why his 4 m and 8 m floors showed the same side wall), front-loaded so
# the common 2.5 .. 8 m range gets most of the growth: rise(z) = (1 - (2.5/z)^P) / (1 - (2.5/20)^P).
# The north face (H) is the depth ladder's (ladder.py): today's table at NORTH_SCALE (0.7) to 2 m, then 0.085 a metre to 4 m
# (3 m against 4 m read by the wall: the art judge, 2026-11-23), then 0.078 a doubling to 20 m. His L's 4 m north arm keeps
# 0.475 of a square of floor (0.50 before; his words, 2026-11-22: "the lower-right northern inner shelf is incredibly narrow",
# it showed 0.26), and a one-square north shelf keeps 0.4 in view to 8 m (P7).
NORTH_SCALE = 0.7
NORTH_TABLE = [NORTH_SCALE * v for v in (0.0, 0.12, 0.23, 0.35, 0.50)]   # per 0.5 m notch, 0 .. 2 m (ladder.H's own)
SIDE_TABLE = [0.0, 0.06, 0.11, 0.17, 0.23, 0.29]
W_TOP = 0.46     # at 20 m
P = 0.6
DEEPEST = 20.0


def _rise(z: float) -> float:
    return (1.0 - (2.5 / z) ** P) / (1.0 - (2.5 / DEEPEST) ** P)


def _table(t, z):
    n = z / 0.5
    lo = int(n)
    if lo >= len(t) - 1:
        return t[-1]
    return t[lo] + (t[lo + 1] - t[lo]) * (n - lo)


def H(z: float) -> float:
    """The north face: the depth ladder's (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR,
    design/specs/2026-11-23-pit-floor-depth-ladder/ladder.py): today's table at NORTH_SCALE to 2 m, then taller with depth so
    3 m and 4 m pits read apart by the wall (the art judge's ruling), slowly enough past 4 m that his L's north arm stays wide."""
    return _LADDER.H(z)


def W(z: float) -> float:
    if z <= 0:
        return 0.0
    if z <= 2.5:
        return _table(SIDE_TABLE, z)
    return SIDE_TABLE[-1] + (W_TOP - SIDE_TABLE[-1]) * _rise(min(z, DEEPEST))


def _inv(f, v: float) -> float:
    """The depth z with f(z) = v (f strictly rising on 0 .. DEEPEST), by bisection."""
    if v <= 0:
        return 0.0
    lo, hi = 0.0, DEEPEST
    if v >= f(hi):
        return hi
    for _ in range(40):
        mid = (lo + hi) / 2
        if f(mid) < v:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def H_inv(v: float) -> float:
    return _inv(H, v)


def W_inv(v: float) -> float:
    return _inv(W, v)


# ── depth value: the darkening of a surface point at depth z (a multiplier on its terrain colour) ──
def K(z: float) -> float:
    """The depth ladder's tone (ladder.py): K_FLOOR + (1 - K_FLOOR) (1 + z / K_S)^-K_P. The art judge refused a 2 m floor at
    0.38 with 3 m .. 16 m squeezed into a dozen grey levels: the 2 m floor is lifted to about 0.63, every depth below it keeps
    its grain (never under K_FLOOR, 0.22), and floors and face tops share the one tone."""
    return _LADDER.K(z)


# ── the lines (black, as today) ──
LIP_BAND = 0.07          # the pale edge of an upper floor at its lip (his words: "a differently colored "edge" marked in black")
LIP_LIFT = 1.45          # its brightness over the floor it edges
RIM_LINE = 0.04          # the lip line on a north edge (today's RimLine)
SIDE_LINE = 0.03         # the lip line on a side edge
SOUTH_LINING = [0.0, 0.045, 0.055, 0.065, 0.08]   # today's SouthLiningByDrop, per 0.5 m notch of the drop (last entry on)


def south_lining(drop: float) -> float:
    if drop <= 0:
        return 0.0
    n = int(round(drop / 0.5))
    return SOUTH_LINING[min(max(n, 1), len(SOUTH_LINING) - 1)]


def _at(grid, r, c):
    """Depth of a square; off the grid reads as undug ground (cases are drawn with ground all round)."""
    if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
        return grid[r][c]
    return 0.0


def plan_cell(grid, r, c, lv: float = 0.0) -> dict | None:
    """Everything one square draws, from its depth and its 8 neighbours' depths. None for undug ground.

    Keys (sizes in squares, y down from the north edge):
      d                 this floor's depth
      t                 north face height (0: no north face)
      l, r              west / east side strip width at the floor (0: none)
      lt, rt            west / east side strip width at the TOP of the north face (the side wall above a riser)
      hv_l, hv_r        how far the north face runs straight down its west / east end before it mitres in
      sl                south lining height (0: none)
      cnw, cne          (width, height) of a corner piece, the side face of a shallower block to the NW / NE continued
                        down beside that block's own face; (0, 0) when none
      lip_n             (x0, x1) of the north lip line, or None
      lip_w, lip_e      (y0, y1) of the west / east lip line, or None
      dot_nw, dot_ne    the outline's missing corner (a shallower diagonal block), bool
      zn, zw, ze, znw, zne   the depth at the TOP of each wall (the shallower side), for the depth of each wall point
    """
    d = _at(grid, r, c)
    if d <= 0:
        return None
    n, s, w, e = _at(grid, r - 1, c), _at(grid, r + 1, c), _at(grid, r, c - 1), _at(grid, r, c + 1)
    nw, ne = _at(grid, r - 1, c - 1), _at(grid, r - 1, c + 1)
    # liquid lv metres deep in this square hides the foot of its walls: the faces show down to the waterline de only
    # (the lines are the edges' and stay where they are)
    de = d - max(0.0, lv)
    t = H(de) - H(n) if n < de else 0.0
    l = W(de) - W(w) if w < de else 0.0
    rr = W(de) - W(e) if e < de else 0.0
    lt = W(n) - W(w) if (n < de and w < n) else 0.0
    rt = W(n) - W(e) if (n < de and e < n) else 0.0
    hv_l = H(min(w, de)) - H(n) if (n < de and w > n) else 0.0
    hv_r = H(min(e, de)) - H(n) if (n < de and e > n) else 0.0
    sl = south_lining(d - s) if s < d else 0.0
    cnw = (W(de) - W(nw), H(de) - H(nw)) if (n >= d and w >= d and nw < de) else (0.0, 0.0)
    cne = (W(de) - W(ne), H(de) - H(ne)) if (n >= d and e >= d and ne < de) else (0.0, 0.0)
    return {
        "d": d, "t": t, "l": l, "r": rr, "lt": lt, "rt": rt, "hv_l": hv_l, "hv_r": hv_r, "sl": sl,
        "cnw": cnw, "cne": cne,
        "lip_n": (lt, 1.0 - rt) if n < d else None,
        "lip_w": ((hv_l if n < d else 0.0), 1.0) if w < d else None,
        "lip_e": ((hv_r if n < d else 0.0), 1.0) if e < d else None,
        "dot_nw": n >= d and w >= d and nw < d,
        "dot_ne": n >= d and e >= d and ne < d,
        "zn": n, "zw": w, "ze": e, "znw": nw, "zne": ne,
        # the lip of THIS floor where a 4-neighbour is deeper (a dug floor only; the ground needs no lift): a pale band
        "edge_n": n > d, "edge_s": s > d, "edge_w": w > d, "edge_e": e > d,
    }


def side_boundary(p: dict, side: str, y: float) -> float:
    """The width of the west ('l') or east ('r') wall at height y in the square: below the north face it is the strip at the
    floor; beside the north face it follows the face's end (straight down by hv, then a mitre to the floor strip)."""
    full = p[side]
    top = p["lt" if side == "l" else "rt"]
    hv = p["hv_l" if side == "l" else "hv_r"]
    t = p["t"]
    if t <= 0 or y >= t:
        return full
    if y < hv:
        return top
    if t - hv <= 1e-9:
        return full
    return top + (full - top) * (y - hv) / (t - hv)


# ── the cast shadow at one point (the scalar twin of render.cast_shadow, which the game's C# copies) ──
SUN_AZ = 315.0           # option B, his pick pending: the light comes from the north-west (compass degrees)
SHADOW_K, SHADOW_POW = 0.12, 0.7   # a drop from a to b casts SHADOW_K x (b^0.7 - a^0.7) squares past the face's foot
PENUMBRA = 0.04          # squares: the soft edge
MARCH_STEP = 1.0 / 32.0
SHADOW_REACH = SHADOW_K * DEEPEST ** SHADOW_POW + MARCH_STEP


def point_top(grid, x: float, y: float) -> float:
    """The depth (m) a point casts from: a wall point stands at its wall's TOP, a floor point at its floor, ground at 0.
    x, y in squares from the grid's north-west corner, y down."""
    r, c = math.floor(y), math.floor(x)
    p = plan_cell(grid, r, c)
    if p is None:
        return 0.0
    fx, fy = x - c, y - r
    cw, ch = p["cne"]
    if cw > 0 and (1 - fx) < cw and fy < ch - min(cw, ch) * (1 - fx) / cw:
        return p["zne"]
    cw, ch = p["cnw"]
    if cw > 0 and fx < cw and fy < ch - min(cw, ch) * fx / cw:
        return p["znw"]
    in_w = fx < side_boundary(p, "l", fy)
    in_e = (1 - fx) < side_boundary(p, "r", fy)
    if in_e:
        return p["ze"]
    if in_w:
        return p["zw"]
    if fy < p["t"]:
        return p["zn"]
    return p["d"]


def lit_at(grid, x: float, y: float, az: float = SUN_AZ) -> float:
    """1 lit .. 0 in shadow, at a point: march toward the sun over the heights -SHADOW_K x top^SHADOW_POW at a slope of 1."""
    h0 = -SHADOW_K * point_top(grid, x, y) ** SHADOW_POW
    a = math.radians(az)
    dx, dy = math.sin(a), -math.cos(a)
    excess = -1e9
    k = 1
    while k * MARCH_STEP <= SHADOW_REACH:
        s = k * MARCH_STEP
        hq = -SHADOW_K * point_top(grid, x + dx * s, y + dy * s) ** SHADOW_POW
        if hq > h0 + 1e-6:       # only a higher point casts (level ground beside a point never shades it)
            excess = max(excess, hq - h0 - s)
        k += 1
    return min(1.0, max(0.0, 0.5 - excess / (2 * PENUMBRA)))


# ── the light on a face and on a floor (option B: sun at SUN_AZ, elevation SUN_EL; render.py's numbers) ──
SUN_EL = 55.0
AMBIENT, DIRECT, WALL_AMBIENT, FACE_FADE = 0.55, 0.45, 0.85, 0.30


def face_light(facing: str, az: float = SUN_AZ, el: float = SUN_EL) -> float:
    """A face's light relative to a lit floor: 'n' a north wall (faces south), 'w' a west wall (faces east), 'e' an east wall."""
    a, e = math.radians(az), math.radians(el)
    sx, sy, sz = math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e)
    nx, ny = {"n": (0.0, -1.0), "w": (1.0, 0.0), "e": (-1.0, 0.0)}[facing]
    flat = AMBIENT + DIRECT * sz
    return (WALL_AMBIENT + DIRECT * max(0.0, nx * sx + ny * sy)) / flat


def shadow_dark(el: float = SUN_EL) -> float:
    """How much darker a floor in full shadow is than a lit one (black alpha)."""
    sz = math.sin(math.radians(el))
    return 1.0 - AMBIENT / (AMBIENT + DIRECT * sz)
