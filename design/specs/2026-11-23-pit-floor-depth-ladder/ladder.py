"""The pit depth ladder (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR), as pure functions.

The art judge's ruling (published db69a1286e): refuse A, B and C. Lift the 2 m floor so the ladder has room; spread the
doubling ladder over that range; never darken a floor so far that its dirt grain disappears; let the north inner wall face
grow taller with depth, so 3 m against 4 m is told by the wall, because tone cannot carry that step. Depth darkening stays a
fixed ground tone; the wall shadows already follow the game's sun.

Two functions of depth z (metres; 0 is undug ground) replace the stepped rule's K and H (pitrule.py):

  K(z)  the tone of a surface at depth z, a multiplier on undug ground (floors draw at K(z); a face at K(its top)).
        K(z) = K_FLOOR + (1 - K_FLOOR) * (1 + z / K_S) ** -K_P. It never goes under K_FLOOR at any depth, so the deepest
        floor keeps its grain by construction (the grain is the texture's own contrast, scaled by K).
  H(z)  how far south of its top edge a north-wall point at depth z shows (cells). Today's table (x 0.7) to 2 m; then a
        straight rise of H_SLOPE a metre to 4 m, so 3 m and 4 m pits show visibly different north faces; then H_LOG more at
        every doubling to 20 m, small enough that a one-square north shelf stays in view to 8 m (the narrow-shelf fix of
        RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM is kept).

W (the side strip) is unchanged. Pure functions: no game, no Verse.
"""
from __future__ import annotations

import math

# ── tone ──
K_FLOOR = 0.22     # the darkest any floor gets (deepest floor keeps its grain)
K_S = 1.6          # metres
K_P = 0.8

# ── north face ──
NORTH_TABLE = [0.7 * v for v in (0.0, 0.12, 0.23, 0.35, 0.50)]   # per 0.5 m notch, 0 .. 2 m: today's, unchanged
H2 = NORTH_TABLE[-1]
H_SLOPE = 0.085    # cells a metre, 2 m .. 4 m
H4 = H2 + 2 * H_SLOPE
H_LOG = 0.078     # cells a doubling of depth past 4 m (to DEEPEST)
DEEPEST = 20.0


def K(z: float) -> float:
    if z <= 0:
        return 1.0
    return K_FLOOR + (1.0 - K_FLOOR) * (1.0 + z / K_S) ** -K_P


def H(z: float) -> float:
    if z <= 0:
        return 0.0
    if z <= 2.0:
        n = z / 0.5
        lo = int(n)
        if lo >= len(NORTH_TABLE) - 1:
            return NORTH_TABLE[-1]
        return NORTH_TABLE[lo] + (NORTH_TABLE[lo + 1] - NORTH_TABLE[lo]) * (n - lo)
    if z <= 4.0:
        return H2 + H_SLOPE * (z - 2.0)
    return H4 + H_LOG * math.log2(min(z, DEEPEST) / 4.0)


# ── perception (for the sweep's verdicts; the game does not read these) ──
GROUND_SRGB = 77.0   # mean grey of cleared ground and of plain gravel in game (soil.png 76.7; the judge's 2 m floor 29 at 0.38)


def lstar(srgb: float) -> float:
    """CIE L* of an sRGB grey 0..255."""
    v = max(0.0, srgb) / 255.0
    y = v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 903.3 * y if y <= 0.008856 else 116.0 * y ** (1.0 / 3.0) - 16.0


def floor_lstar(k: float) -> float:
    return lstar(GROUND_SRGB * k)
