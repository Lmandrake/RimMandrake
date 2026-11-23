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

# ── the two offset functions ──────────────────────────────────────────────
# Up to 2.5 m they are today's tables exactly (RM_WallFaceMath NorthByDrop / SideByDrop), so a single-depth pit at 2.5 m or
# less looks exactly as it does today (his walk: stations 34 to 39 "look good and indicate their depth well"). Past 2.5 m
# they keep rising to 20 m (today's stop at 2.5 m is why his 4 m and 8 m floors showed the same side wall), front-loaded so
# the common 2.5 .. 8 m range gets most of the growth: rise(z) = (1 - (2.5/z)^P) / (1 - (2.5/20)^P).
NORTH_TABLE = [0.0, 0.12, 0.23, 0.35, 0.50, 0.62]   # per 0.5 m notch, 0 .. 2.5 m
SIDE_TABLE = [0.0, 0.06, 0.11, 0.17, 0.23, 0.29]
H_TOP, W_TOP = 0.97, 0.46     # at 20 m (a one-square trench 20 m deep keeps 0.08 of a square of floor in view)
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
    if z <= 0:
        return 0.0
    if z <= 2.5:
        return _table(NORTH_TABLE, z)
    return NORTH_TABLE[-1] + (H_TOP - NORTH_TABLE[-1]) * _rise(min(z, DEEPEST))


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
# K(z) = (1 + z / K_SCALE) ** -K_POW: 0.5 m 0.73, 1 m 0.59, 2 m 0.45, 4 m 0.32, 6 m 0.26, 8 m 0.22, 20 m 0.13. Each doubling
# of depth is about 30 % darker (the fresh judge measured his 4 m and 8 m floors too close at 0.50; his words: "each level
# needs a pretty clear differential in coloration"), at every depth (today's floor stops darkening past about 2 m: measured, the earlier item).
K_SCALE, K_POW = 0.75, 0.62


def K(z: float) -> float:
    return (1.0 + max(0.0, z) / K_SCALE) ** -K_POW


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


def plan_cell(grid, r, c) -> dict | None:
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
    t = H(d) - H(n) if n < d else 0.0
    l = W(d) - W(w) if w < d else 0.0
    rr = W(d) - W(e) if e < d else 0.0
    lt = W(n) - W(w) if (n < d and w < n) else 0.0
    rt = W(n) - W(e) if (n < d and e < n) else 0.0
    hv_l = H(min(w, d)) - H(n) if (n < d and w > n) else 0.0
    hv_r = H(min(e, d)) - H(n) if (n < d and e > n) else 0.0
    sl = south_lining(d - s) if s < d else 0.0
    cnw = (W(d) - W(nw), H(d) - H(nw)) if (n >= d and w >= d and nw < d) else (0.0, 0.0)
    cne = (W(d) - W(ne), H(d) - H(ne)) if (n >= d and e >= d and ne < d) else (0.0, 0.0)
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
