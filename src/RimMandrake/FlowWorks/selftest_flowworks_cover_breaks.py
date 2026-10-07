#!/usr/bin/env python3
"""FLOWWORKS_REVIEW_LOOKS_ROUND_1 item 11 (owner, 2026-10-06): "And when something falls into a covered pit, of
course it is no longer covered".

Measured in source, not assumed: the ONLY way anything drops through an intact pit cover is
Building_PitCover.Spring (the deck's mass trigger), and Spring destroys every cover of the deck BEFORE it sends a
single faller down (RM_SuperdeepTrap.OnForcedDescent). Everywhere else an intact cover is ground (IsHeldAt and the
descent detector skip a covered cell), so nothing can be "in the pit" under a cover that still stands.

This check pins both facts so a refactor that reorders Spring, or a new path that drops a pawn/item through a cover
without springing it, fails here. Items/corpses (Explosive Knockback, not built) must call Spring too.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_cover_breaks.py
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source"


def method_body(text, signature):
    i = text.index(signature)
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j:k + 1]
    raise ValueError(signature)


def main():
    cover = (SRC / "Pits" / "Building_PitCover.cs").read_text(encoding="utf-8")
    spring = method_body(cover, "public void Spring(List<Pawn> fallers)")
    destroy = spring.find("c.Destroy(")
    descend = spring.find("OnForcedDescent(")
    assert destroy >= 0, "Spring no longer destroys the covers"
    assert descend >= 0, "Spring no longer sends the fallers down"
    assert destroy < descend, "Spring sends fallers down before the cover is gone"
    assert re.search(r"foreach \(Building_PitCover c in deck\)", spring), "Spring no longer breaks the WHOLE deck"
    # every forced descent outside the trap itself goes through Spring
    callers = []
    for f in SRC.rglob("*.cs"):
        if "SelfTest" in f.parts:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "OnForcedDescent(" in line and "static void OnForcedDescent" not in line and "///" not in line:
                callers.append((f.relative_to(SRC).as_posix(), n))
    probe = [c for c in callers if c[0] == "Pits/Building_PitCover.cs"]
    assert probe, "sanity probe: the Spring call site itself must be found (%s)" % callers
    others = []
    for f, n in callers:
        if f in ("Pits/Building_PitCover.cs", "Superdeep/RM_SuperdeepTrap.cs"):
            continue
        lines = (SRC / f).read_text(encoding="utf-8").splitlines()[max(0, n - 15):n]
        if not any("IsOpenPit(" in ln for ln in lines):   # an open (uncovered) pit only: no cover to break
            others.append((f, n))
    assert not others, "a forced descent outside Spring must break a cover or require an open pit: %s" % others
    trap = (SRC / "Superdeep" / "RM_SuperdeepTrap.cs").read_text(encoding="utf-8")
    held = method_body(trap, "public static bool IsHeldAt(Pawn p, IntVec3 c)")
    assert "IsCovered" in held, "an intact cover no longer reads as ground for the hold"
    print("ok  cover breaks on every fall: Spring destroys the whole deck before %d descent call(s); "
          "intact cover = ground" % len(probe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
