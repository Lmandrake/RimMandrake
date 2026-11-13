"""The offline twin of RM_UnderLiquid (Source/Superdeep/RM_UnderLiquid.cs): ONE law for anything in a dug pit under liquid.

Owner looks 2026-11-12: "It's as though each case is independently set in these variables, badly (major fix)" (4:2x PM);
"it's very transparent at first, but it becomes about twice too opaque as it should by the end. Its color should also be
darkened. ... pits are quite dark when dry, then suddenly become light for some reason with just a little water. That
should not be. Keep them darker" (6:12 PM); shadows "only inside the pit ... it should simply be transparent to them as
usual" (4:22 PM).

The C# must agree with this file: selftest_flowworks_underliquid_parity.py compares the constants and writes the golden
table SelfTest/UnderLiquidParityChecks.cs checks RM_UnderLiquid against (python3 ... --write regenerates it).

Law
  seen(clarity, m)  how much of a thing lying m metres under the surface is seen (1 = as dry):
                    1 above the line; 0 for an opaque liquid (clarity 0: tar, oil, blood);
                    else 1 - DEEP_OPACITY * (1 - clarity ** (m + SURFACE_METRES)).
                    clarity = the share of the view left after 1 m (fresh water 0.45). DEEP_OPACITY caps how opaque a
                    clear liquid gets at depth: 0.5 halves the 2026-11-12 law's 0.97 at 4 m (owner: "twice too opaque").
  drawn colour      lerp(liquid * (1 - DARKEN), thing, seen): the drowned part over the liquid darkened by DARKEN (owner:
                    "Its color should also be darkened"), the pit floor drawn in the DRY pit's own dark ground (owner:
                    "Keep them darker"), never the light ground the pit was dug from.
  cut               share(level, base, height): the share of a thing (from its foot) under the line.
  heights           items 0.3 m, minified 0.75, swale 0.05, lying ladder 0.1, stakes 1.0, corpse 0.3; an installed
                    building by its cover: max(MIN_THING_METRES, fillPercent * FULL_COVER_METRES); a standing pawn by
                    its climb-size height (RM_Drowning.HeightOf), a lying one CORPSE_METRES.
  shadow            a thing standing in a pit casts ONE shadow, on the pit floor under it (never the bank, never the
                    surface), THING_SHADOW_ALPHA * seen(clarity, level): the floor lies `level` under.
  label             a thing's label/stack count fades with the thing's top: seen(clarity, level - height); hidden below
                    LABEL_HIDDEN.
"""
from dataclasses import dataclass

NOTCH = 0.5
SURFACE_METRES = 0.35
DEEP_OPACITY = 0.5          # setting underLiquidDeepOpacity
DARKEN = 0.25               # setting underLiquidDarken
THING_SHADOW_ALPHA = 0.30   # setting pitThingShadowAlpha
FULL_COVER_METRES = 2.0     # a building of fillPercent 1 stands this tall
MIN_THING_METRES = 0.3
CORPSE_METRES = 0.3
LABEL_HIDDEN = 0.05

ITEM_METRES, MINIFIED_METRES, SWALE_METRES, LYING_LADDER_METRES, STAKE_METRES = 0.3, 0.75, 0.05, 0.1, 1.0

# colours (0..1) the mock draws with; WATER_BODY is the pawn cover's clear-liquid colour (RM_UnderLiquid.WaterBody)
WATER_BODY = (0.20, 0.32, 0.43)
NORTH_BY_DROP = [0, .12, .23, .35, .50, .62]
SIDE_BY_DROP = [0, .06, .11, .17, .23, .29]


def seen(clarity, metres_over, deep_opacity=DEEP_OPACITY):
    if metres_over <= 0:
        return 1.0
    if clarity <= 0:
        return 0.0
    if clarity >= 1:
        return 1.0
    return 1.0 - deep_opacity * (1.0 - clarity ** (metres_over + SURFACE_METRES))


def seen_old(clarity, metres_over):
    """The 2026-11-12 law (441c321a20dc) the owner judged: kept for the retune rows."""
    if metres_over <= 0:
        return 1.0
    if clarity <= 0:
        return 0.0
    return clarity ** (metres_over + SURFACE_METRES)


def share(level, base, height):
    if level <= base:
        return 0.0
    if height <= 0:
        return 1.0
    return max(0.0, min(1.0, (level - base) / height))


def building_metres(fill_percent):
    return max(MIN_THING_METRES, fill_percent * FULL_COVER_METRES)


def thing_shadow(clarity, level):
    return THING_SHADOW_ALPHA * seen(clarity, level)


def label_alpha(clarity, level, height):
    a = seen(clarity, level - height)
    return 0.0 if a < LABEL_HIDDEN else a


def mix(liquid, thing, s, darken=DARKEN):
    return tuple(l * (1 - darken) * (1 - s) + t * s for l, t in zip(liquid, thing))


def face_at(table, exposed):
    if exposed <= 0:
        return 0.0
    last = len(table) - 1
    if exposed >= last:
        return table[last]
    lo = int(exposed)
    return table[lo] + (table[lo + 1] - table[lo]) * (exposed - lo)


@dataclass
class Look:
    cut: float
    vis_top: float
    vis_foot: float
    shadow: float
    label: float


def look(pit_depth_m, level_m, clarity, height_m):
    """A thing standing on the floor of a pit: its cut, how it is seen at the line and its foot, its floor shadow and
    its label's alpha."""
    level = max(0.0, min(level_m, pit_depth_m))
    c = share(level, 0.0, height_m)
    top_y = c * height_m
    return Look(c, seen(clarity, level - top_y), seen(clarity, level), thing_shadow(clarity, level),
                label_alpha(clarity, level, height_m))


# the golden table both sides check: (clarity, metres over) -> seen
GOLDEN_CLARITY = (0.45, 0.25, 0.0)
GOLDEN_METRES = (0.0, 0.01, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)


def golden_rows():
    return [(c, m, round(seen(c, m), 5)) for c in GOLDEN_CLARITY for m in GOLDEN_METRES]
