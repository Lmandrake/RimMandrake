"""The offline twin of RM_UnderLiquid (Source/Superdeep/RM_UnderLiquid.cs): ONE law for anything in a dug pit under liquid.

Owner looks 2026-11-12: "It's as though each case is independently set in these variables, badly (major fix)" (4:2x PM);
"it's very transparent at first, but it becomes about twice too opaque as it should by the end. Its color should also be
darkened. ... pits are quite dark when dry, then suddenly become light for some reason with just a little water. That
should not be. Keep them darker" (6:12 PM); shadows "only inside the pit ... it should simply be transparent to them as
usual" (4:22 PM).

The C# must agree with this file: selftest_flowworks_underliquid_parity.py compares the constants and writes the golden
table SelfTest/UnderLiquidParityChecks.cs checks RM_UnderLiquid against (python3 ... --write regenerates it).

Law (RIMMANDRAKE_TINT_PIT_WATER_READS_AS_WATER_NOT_MUD, owner by card 2026-11-12 "Blue that grows with depth", then
8:55 PM: "The water still does not read as water well even at 4m, looks more like faint blue mist patches. I think I asked
you for too little opacity.")
  seen(clarity, m)  how much of a thing lying m metres under the surface is seen (1 = as dry):
                    1 above the line; 0 for an opaque liquid (clarity 0: tar, oil, blood);
                    else 1 - DEEP_OPACITY * rise(m / full(clarity)), rise(x) = 1 - (1 - x) ** CURVE_POWER up to 1 at x = 1.
                    A gentle start (0.5 m of fresh water hides 0.15: "very transparent at first"), clearly water by 2 m
                    (0.56), a body of deep water at 4 m (DEEP_OPACITY 0.90, between the 2026-11-12 law's 0.97 and the
                    halved 0.48, nearer the old). full(clarity) = FULL_METRES x ln(REFERENCE_CLARITY) / ln(clarity): fresh
                    water reaches its full opacity at FULL_METRES; a murkier liquid sooner, a clearer one later.
  drawn colour      lerp(body(liquid), under, seen): ONE even sheet of the liquid's deep body colour over the whole drowned
                    pit (floor and walls drawn OPAQUE in the dry pit's own dark ground, owner: "Keep them darker"; their
                    shadows under the sheet), alpha 1 - seen at each point's depth. body(c) = c ** BODY_GAMMA x (1 - DARKEN):
                    the liquid's own colour made dark and saturated (fresh water a deep blue, acid a dark green), never a
                    pale wash. The 2026-11-12 draw let vanilla's water terrain show through a half-alpha floor: its ripple
                    texture read as "faint blue mist patches"; the opaque floor hides it.
  cut               share(level, base, height): the share of a thing (from its foot) under the line.
  heights           items 0.3 m, minified 0.75, swale 0.05, lying ladder 0.1, stakes 1.0, corpse 0.3; an installed
                    building by its cover: max(MIN_THING_METRES, fillPercent * FULL_COVER_METRES); a standing pawn by
                    its climb-size height (RM_Drowning.HeightOf), a lying one CORPSE_METRES.
  shadow            a thing standing in a pit casts ONE shadow, on the pit floor under it (never the bank, never the
                    surface), THING_SHADOW_ALPHA, drawn UNDER the sheet so the sheet hides it by the law like the floor (the
                    2026-11-12 draw put it over the water, an untinted dark square under every thing); 0 under an opaque
                    liquid.
  label             a thing's label/stack count fades with the thing's top: seen(clarity, level - height); hidden below
                    LABEL_HIDDEN.
"""
from dataclasses import dataclass

import math

NOTCH = 0.5
DEEP_OPACITY = 0.90         # setting underLiquidDeepOpacity: the most a clear liquid hides (its body at full depth)
FULL_METRES = 4.0           # setting underLiquidFullMetres: fresh water reaches DEEP_OPACITY at this depth
REFERENCE_CLARITY = 0.45    # fresh water's seeThrough: the liquid FULL_METRES is stated for
CURVE_POWER = 1.4           # rise(x) = 1 - (1 - x) ** CURVE_POWER: gentle at first, tellable steps to the full depth
BODY_GAMMA = 3.0            # body colour = liquid colour ** BODY_GAMMA x (1 - DARKEN): darker AND more saturated
DARKEN = 0.6                # setting underLiquidDarken: how dark the body colour is
THING_SHADOW_ALPHA = 0.30   # setting pitThingShadowAlpha
FULL_COVER_METRES = 2.0     # a building of fillPercent 1 stands this tall
MIN_THING_METRES = 0.3
CORPSE_METRES = 0.3
LABEL_HIDDEN = 0.05

ITEM_METRES, MINIFIED_METRES, SWALE_METRES, LYING_LADDER_METRES, STAKE_METRES = 0.3, 0.75, 0.05, 0.1, 1.0

# fresh water's LiquidDef colour: the body colour of a clear liquid whose own colour is unknown (RM_UnderLiquid.WaterColour)
WATER_COLOUR = (0.62, 0.80, 0.98)
NORTH_BY_DROP = [0, .12, .23, .35, .50, .62]
SIDE_BY_DROP = [0, .06, .11, .17, .23, .29]


def full_metres(clarity, full=FULL_METRES):
    """The depth at which a liquid of this clarity reaches its full opacity (0 < clarity < 1)."""
    return full * math.log(REFERENCE_CLARITY) / math.log(clarity)


def rise(x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1.0 - (1.0 - x) ** CURVE_POWER


def seen(clarity, metres_over, deep_opacity=DEEP_OPACITY, full=FULL_METRES):
    if metres_over <= 0:
        return 1.0
    if clarity <= 0:
        return 0.0
    if clarity >= 1:
        return 1.0
    return 1.0 - deep_opacity * rise(metres_over / full_metres(clarity, full))


def seen_old(clarity, metres_over):
    """The 2026-11-12 afternoon law (441c321a20dc), 0.97 at 4 m: 'about twice too opaque'."""
    if metres_over <= 0:
        return 1.0
    if clarity <= 0:
        return 0.0
    return clarity ** (metres_over + 0.35)


def seen_halved(clarity, metres_over):
    """The 2026-11-12 evening retune (4f158b6cb442), 0.48 at 4 m: 'too little opacity'."""
    if metres_over <= 0:
        return 1.0
    if clarity <= 0:
        return 0.0
    return 1.0 - 0.5 * (1.0 - clarity ** (metres_over + 0.35))


def body(colour, darken=DARKEN):
    """A clear liquid's body colour: its own colour, darker and more saturated."""
    return tuple(max(0.0, min(1.0, ch)) ** BODY_GAMMA * (1.0 - darken) for ch in colour)


def share(level, base, height):
    if level <= base:
        return 0.0
    if height <= 0:
        return 1.0
    return max(0.0, min(1.0, (level - base) / height))


def building_metres(fill_percent):
    return max(MIN_THING_METRES, fill_percent * FULL_COVER_METRES)


def thing_shadow(clarity, level):
    """The floor shadow's own alpha; it lies under the sheet, which hides it by the law (sheeted below)."""
    if level > 0 and clarity <= 0:
        return 0.0
    return THING_SHADOW_ALPHA


def label_alpha(clarity, level, height):
    a = seen(clarity, level - height)
    return 0.0 if a < LABEL_HIDDEN else a


def sheet(body_colour, under, s):
    """The drawn colour: the even sheet of the body colour at alpha 1 - s over what lies under it."""
    return tuple(b * (1 - s) + u * s for b, u in zip(body_colour, under))


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
    shadow: float        # the shadow's own alpha (under the sheet)
    shadow_seen: float   # how strongly it reads through the sheet: shadow x seen at the floor
    label: float


def look(pit_depth_m, level_m, clarity, height_m):
    """A thing standing on the floor of a pit: its cut, how it is seen at the line and its foot, its floor shadow and
    its label's alpha."""
    level = max(0.0, min(level_m, pit_depth_m))
    c = share(level, 0.0, height_m)
    top_y = c * height_m
    sh = thing_shadow(clarity, level)
    return Look(c, seen(clarity, level - top_y), seen(clarity, level), sh, sh * seen(clarity, level),
                label_alpha(clarity, level, height_m))


# the golden table both sides check: (clarity, metres over) -> seen
GOLDEN_CLARITY = (0.45, 0.25, 0.0)
GOLDEN_METRES = (0.0, 0.01, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 3.5, 4.0, 6.0)


def golden_rows():
    return [(c, m, round(seen(c, m), 5)) for c in GOLDEN_CLARITY for m in GOLDEN_METRES]
