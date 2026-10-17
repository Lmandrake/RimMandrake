"""level_surface_bar.py -- measuring script for the north-star bar `still_water_one_surface_height`.

Bar (design/validation_walks/RimMandrake/FlowWorks.md, owner R9 2026-10-17, OWNER.jsonl tsn 1792258162801304562):
every square of a connected body of still water stands at the same surface height, to within 1 cm, read from the
game's state, not from the picture.

STUB. The live read needs the per-body surface-gap diagnostic that WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (plan P3
of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG) adds to the mod. Until it exists, `measure()` reports UNMEASURED and never PASS.
The pure judgement (`worst_gap_m`) is real and selftested below, so the live half only has to supply surfaces.
"""
import sys

TOLERANCE_M = 0.01


def worst_gap_m(bodies):
    """bodies: {body_id: [surface_m of each square]} -> (worst gap in metres, body id). Empty input is not a pass."""
    if not bodies or not any(bodies.values()):
        raise ValueError("no still-water squares read: the instrument saw nothing")
    worst, which = 0.0, None
    for bid, surf in bodies.items():
        if surf:
            g = max(surf) - min(surf)
            if g > worst or which is None:
                worst, which = max(worst, g), bid
    return worst, which


def read_bodies_live(bridge=None):
    """TODO (P3/P10): read every connected still body's per-square surface (floor + water depth) from game state via
    the solver's diagnostic. Returns {body_id: [surface_m, ...]}."""
    raise NotImplementedError("UNBUILT: the level-surface solver's per-body diagnostic does not exist yet "
                              "(WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES)")


def measure(t=None):
    """Called by validation.py chain `water_level_surface`. Raises ExpectationFailed; UNMEASURED until the read exists."""
    from modcheck import ExpectationFailed
    try:
        bodies = read_bodies_live()
    except NotImplementedError as ex:
        raise ExpectationFailed("UNMEASURED: %s" % ex)
    gap, bid = worst_gap_m(bodies)
    if gap > TOLERANCE_M:
        raise ExpectationFailed("body %s surface varies by %.3f m (> %.2f m)" % (bid, gap, TOLERANCE_M))


def _selftest():
    assert worst_gap_m({"a": [1.44] * 9}) == (0.0, "a")
    g, b = worst_gap_m({"a": [1.0, 1.0], "b": [0.5, 0.52]})
    assert b == "b" and abs(g - 0.02) < 1e-9 and g > TOLERANCE_M
    for bad in ({}, {"a": []}):
        try:
            worst_gap_m(bad)
            raise AssertionError("empty read passed")
        except ValueError:
            pass
    print("level_surface_bar selftest ok")


if __name__ == "__main__":
    sys.exit(_selftest())
