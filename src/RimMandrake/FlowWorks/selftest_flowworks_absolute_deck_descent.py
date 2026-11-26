#!/usr/bin/env python3
"""ABSOLUTE_DESCENT_FIX_MISSES_DECK_SHOVE, offline (no game). With "relative climbing" off (the absolute pit rule), a
pawn shoved or skipped off an intact deck onto an open square of the SAME D = 4 excavation took no fall: the arrival
detector (RM_SuperdeepTrap.IsFallingArrival) compared the raw dug depth of both cells (4 -> 4, no descent), so the deck's
walking height (0 for a cover or a surface deck) never counted.

The fix judges the origin at its walking height through RM_PitTrapMath.AbsoluteArrivalDescends (its arithmetic is the
C# SelfTest case PitTrap_absolute_descent_reads_deck_height). This file pins the wiring: the absolute branch of
IsFallingArrival decides through that function, with the origin's deck read, and no longer through a raw
ExcavatedDepthAt(prev) comparison. Each check carries a planted regression (the pre-fix line) that must fail.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_absolute_deck_descent.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []

PRE_FIX = "return RM_PitTrapMath.IsPitDescent(eng.ExcavatedDepthAt(prev), eng.ExcavatedDepthAt(pos));"


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def code_only(s):
    """Comments stripped and whitespace collapsed, so prose never satisfies a pin."""
    return re.sub(r"\s+", " ", "\n".join(line.split("//")[0] for line in s.splitlines()))


def absolute_branch(trap):
    """The code of IsFallingArrival's `if (!RM_PocketGrid.Relative) { ... }` block, or None."""
    try:
        body = body_of(trap, "private static bool IsFallingArrival(")
    except ValueError:
        return None
    try:
        return code_only(body_of(body, "if (!RM_PocketGrid.Relative)"))
    except ValueError:
        return None


def problems(trap, math):
    probs = []
    br = absolute_branch(trap)
    if br is None:
        return ["IsFallingArrival or its absolute branch not found"]
    if "ExcavatedDepthAt(prev)" in br and "AbsoluteArrivalDescends" not in br:
        probs.append("absolute branch compares the raw dug depth of prev (a deck over the pit reads as D = 4)")
    if "AbsoluteArrivalDescends(" not in br:
        probs.append("absolute branch does not decide through RM_PitTrapMath.AbsoluteArrivalDescends")
    if "IsCovered(map, prev)" not in br:
        probs.append("absolute branch does not read whether the origin is decked (RM_PitCoverUtility.IsCovered(map, prev))")
    if "WalkingDepth(map, prev," not in br:
        probs.append("absolute branch does not read the origin deck's walking depth (RM_SpanUtility.WalkingDepth(map, prev, ...))")
    try:
        fn = code_only(body_of(math, "public static bool AbsoluteArrivalDescends("))
    except ValueError:
        return probs + ["RM_PitTrapMath.AbsoluteArrivalDescends not found"]
    if "IsPitDescent(" not in fn:
        probs.append("AbsoluteArrivalDescends does not use the D = 4 descent rule (IsPitDescent)")
    return probs


def main():
    trap = read(os.path.join("Superdeep", "RM_SuperdeepTrap.cs"))
    math = read("RM_PitTrapMath.cs")
    real = problems(trap, math)
    check("absolute_descent_judges_deck_origin_at_walking_height", not real, "; ".join(real))

    # can-fail: put the pre-fix comparison back in the absolute branch; the check must go red.
    br_src = body_of(body_of(trap, "private static bool IsFallingArrival("), "if (!RM_PocketGrid.Relative)")
    planted = trap.replace(br_src, "{\n\t\t\t\t" + PRE_FIX + "\n\t\t\t}", 1)
    check("planted_pre_fix_line_is_caught", planted != trap and bool(problems(planted, math)),
          "the pre-fix line passed the pin")
    # can-fail: the math helper ignores the descent rule.
    try:
        fn_src = body_of(math, "public static bool AbsoluteArrivalDescends(")
        planted_math = math.replace(fn_src, "{\n\t\t\treturn false;\n\t\t}", 1)
    except ValueError:
        planted_math = math   # no helper to plant in: the real check is red already
    check("planted_inert_helper_is_caught", planted_math != math and bool(problems(trap, planted_math)),
          "an inert helper passed the pin")

    print("selftest_flowworks_absolute_deck_descent: %s (%d checks failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
