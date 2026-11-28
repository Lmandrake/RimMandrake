#!/usr/bin/env python3
"""BOTTLE_FILL_FIX_SMALL_POND_TOO: the bottle-fill search admits a limited pond that can pay for the bottle, as the
drink search does (TERRAIN_DRINK_FIX_SMALL_POND_REFUSED).

The old gate was `ex.Stock.CanSupply(map, c, ex)`: the pond must hold one whole level (1000 L of water). A bottle
costs a fraction of that, so a pond of 500 L stood beside a pawn who wanted to fill a bottle and was skipped, while the
same pawn could drink from it. The pure rule is pinned in C# (ThirstChecks Thirst_small_pond_drink_admitted:
BodyAffords admits 500 L for a small debit, CanSupply refuses it). This check pins the wiring of the bottle search:
- its Stock gate asks `CanDebitTerrain(map, c, units)` with the units the fill job debits;
- `CanSupply(` is gone from the search;
- the gate comes before the reach check and before a candidate is admitted.

Exit 0 PASS, 1 FAIL (names what is wrong), 2 could not look. `--mutate` plants the old gate and the check must FAIL.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "Source", "LiquidTypes", "RM_LiquidBottleUtility.cs")
OLD_GATE = "if (ex?.Stock != null && !ex.Stock.CanSupply(map, c, ex))"
NEW_GATE = "if (ex?.Stock != null && !CanDebitTerrain(map, c, units))"
UNITS = "int units = container != null ? RM_ContainerMaterials.UnitsIn(container, candidate, size) : candidate.UnitsFor(size);"


def search_body(text):
    """The body of the radial search loop: from the GenRadial foreach to the end of the method that holds it."""
    i = text.find("foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, maxDist, true))")
    if i < 0:
        return None
    j = text.find("public static", i)
    return text[i:j if j > 0 else len(text)]


def check(text):
    body = search_body(text)
    if body is None:
        return 2, "COULD NOT LOOK: the radial bottle search loop is not in %s" % SRC
    bad = []
    if "CanSupply(" in body:
        bad.append("the bottle search still asks CanSupply (one whole level)")
    g = body.find(NEW_GATE)
    if g < 0:
        bad.append("the bottle search has no CanDebitTerrain gate on the bottle's own units")
    u = body.find(UNITS)
    if u < 0 or (g >= 0 and u > g):
        bad.append("the units the gate asks for are not the units the fill job debits, set before the gate")
    reach = body.find("pawn.CanReach(c, PathEndMode.Touch, Danger.Some)")
    if g >= 0 and (reach < 0 or g > reach):
        bad.append("the gate does not come before the reach check")
    if g >= 0 and not re.match(r"\s*\{\s*continue;", body[g + len(NEW_GATE):]):
        bad.append("an unaffordable cell does not `continue` to the next cell")
    if bad:
        return 1, "FAIL: " + "; ".join(bad)
    return 0, "PASS: the bottle search gates on CanDebitTerrain(units) before reach and admission; no CanSupply"


def main():
    if not os.path.isfile(SRC):
        print("COULD NOT LOOK: %s is missing" % SRC)
        return 2
    with open(SRC, encoding="utf-8") as fh:
        text = fh.read()
    if "--mutate" in sys.argv:
        planted = text.replace(NEW_GATE, OLD_GATE)
        if planted == text:
            print("COULD NOT LOOK: the fixed gate is not there to plant the old one over")
            return 2
        rc, msg = check(planted)
        print("MUTANT (old whole-level gate): " + msg)
        return 0 if rc == 1 else 1
    rc, msg = check(text)
    print(msg)
    return rc


if __name__ == "__main__":
    sys.exit(main())
