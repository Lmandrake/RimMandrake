"""level_surface_bar.py -- measuring script for the north-star bar `still_water_one_surface_height`.

Bar (design/validation_walks/RimMandrake/FlowWorks.md, owner R9 2026-10-17, OWNER.jsonl tsn 1792258162801304562):
every square of a connected body of still water stands at the same surface height, to within 1 cm, read from the
game's state, not from the picture.

THE READ (WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES, plan P3): jawa/static_call
RimMandrake.FlowWorks.RM_NorthstarProofs.ProofLevelSurface("x,z,w,h" | "-") returns the per-body surface-gap diagnostic
(RM_SurfaceGap over the engine's decilitre grid and each pond's exact surface; the Python twin is level_water.surface_gaps):
    "OK <n> worst <G> m;x,z:squares:gap:min:max;..."      (metres, surfaces relative to ground, largest gap first)
A DLL that predates the method, or an answer that is not "OK", is UNMEASURED, never a pass; so is a read that saw no
water at all. Water still moving (a source still filling, a sink draining) is not still water: run it on a settled site.
"""
import sys

TOLERANCE_M = 0.01
PROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"


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


def parse_proof(text):
    """The ProofLevelSurface answer -> {"x,z": [min_m, max_m]} (each body's surface extremes, which carry its gap)."""
    text = (text or "").strip()
    if not text.startswith("OK "):
        raise NotImplementedError("ProofLevelSurface did not answer OK: %r" % text[:200])
    parts = [p for p in text.split(";") if p.strip()]
    bodies = {}
    for p in parts[1:]:
        f = p.split(":")
        if len(f) != 5:
            raise NotImplementedError("unparsed body entry %r" % p)
        bodies[f[0]] = [float(f[3]), float(f[4])]
    return bodies


def read_bodies_live(bridge=None, rect="-"):
    """Every connected body's surface extremes from game state via the solver's diagnostic. `bridge` is anything with
    bridge_call(tool, **args) (the validation suite's `t`) or call(tool, **args)."""
    if bridge is None:
        raise NotImplementedError("no bridge handed to the read")
    call = getattr(bridge, "bridge_call", None) or getattr(bridge, "call")
    r = call("jawa/static_call", type=PROOF, method="ProofLevelSurface", args=rect)
    if not isinstance(r, dict) or r.get("success") is False:
        raise NotImplementedError("static_call ProofLevelSurface did not answer (a DLL older than "
                                  "WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES?): %r" % (r,))
    return parse_proof(str(r.get("result", "")))


def measure(t=None, rect="-"):
    """Called by validation.py chain `water_level_surface`. Raises ExpectationFailed; UNMEASURED when it cannot read."""
    from modcheck import ExpectationFailed
    try:
        bodies = read_bodies_live(t, rect)
        gap, bid = worst_gap_m(bodies)
    except (NotImplementedError, ValueError) as ex:
        raise ExpectationFailed("UNMEASURED: %s" % ex)
    if gap > TOLERANCE_M:
        raise ExpectationFailed("body at %s surface varies by %.3f m (> %.2f m)" % (bid, gap, TOLERANCE_M))


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
    got = parse_proof("OK 2 worst 0.0001 m;5,2:10:0.0001:-0.2632:-0.2631;9,9:1:0.0000:-0.5000:-0.5000;")
    assert got == {"5,2": [-0.2632, -0.2631], "9,9": [-0.5, -0.5]}, got
    g, b = worst_gap_m(got)
    assert b == "5,2" and g < TOLERANCE_M
    g, _ = worst_gap_m(parse_proof("OK 1 worst 0.5000 m;1,1:2:0.5000:-1.0000:-0.5000;"))
    assert g > TOLERANCE_M                                    # the read can go red
    for bad in ("REFUSED no current map", "", "OK 1 worst 0 m;1,1:2:0.5"):
        try:
            parse_proof(bad)
            raise AssertionError("bad answer accepted: %r" % bad)
        except NotImplementedError:
            pass

    class _B(object):
        def bridge_call(self, tool, **a):
            assert tool == "jawa/static_call" and a["method"] == "ProofLevelSurface"
            return {"success": True, "result": "OK 0 worst 0.0000 m;"}
    try:
        worst_gap_m(read_bodies_live(_B()))
        raise AssertionError("a read with no water passed")
    except ValueError:
        pass
    print("level_surface_bar selftest ok")


if __name__ == "__main__":
    sys.exit(_selftest())
