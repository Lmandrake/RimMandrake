#!/usr/bin/env python3
# selftest-timeout: 600   (stages and builds the FlowWorks C# SelfTest, then runs only the shore-search cases)
"""selftest_swim_shore_reach.py — TIRED_SWIMMER_FIX_UNREACHABLE_SHORE (GPT FA_core_sim_4.1).

WHY: a tired swimmer's shore search (RM_Swim.NearestFooting) accepted a dry ledge beside it that was too high to climb,
ordered an impossible Goto and could pick it again until it drowned. The search now crosses only steps the pawn can climb
(RM_PitTrapMath.StepAllowed, ramp and ladder joins) through the Verse-free RM_SwimMath.NearestReachableFooting.

The proof is three C# Case()s in Source/SelfTest/SwimChecks.cs, run through selftest_flowworks_stock.py --only:
a too-high ledge beside the swimmer loses to a farther ramp (can-fail: a walk-only flood picks the ledge), a 4000-grid
sweep against an independent BFS, and the production source shape. This wrapper fails unless all three report ok.

Before any build it pins the PRODUCTION climb inputs in pure Python (source_pins): the climb limit is exactly
RM_PocketGrid.ClimbLimitOf(p) and never replaced, the step's two depths are StepDepthAt of c (from) and of n (to), the
flood's edge lambda is (c, n) and hands both cells and that limit to CanStep, which hands them to RM_ClimbJoins.ForPawn and
RM_PitTrapMath.StepAllowed; and RM_Drowning.ExitInReach reads the same inputs. A mutant such as `int k = int.MaxValue;`
or `StepDepthAt(map, ex, c)` for toD leaves every math case green yet lets the ledge back in; these pins go red on it.

    python3 src/RimMandrake/FlowWorks/selftest_swim_shore_reach.py              # pins, then the C# cases
    python3 src/RimMandrake/FlowWorks/selftest_swim_shore_reach.py --pins-only  # pins only (seconds)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOCK = HERE.parents[0] / "Utils" / "selftest_flowworks_stock.py"
SWIM = HERE / "Source" / "Swimming" / "RM_Swim.cs"
PIT = HERE / "Source" / "RM_PitFillEffects.cs"
CASES = ("Swim_shore_search_skips_unclimbable_ledge",
         "Swim_shore_search_sweep_answer_is_climbable_and_nearest",
         "Swim_shore_search_production_uses_climb_rule")


def _code(text: str) -> str:
    """Source with comments dropped and whitespace collapsed, so a pin reads code only."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return re.sub(r"\s+", " ", text)


def _method(code: str, head: str) -> str:
    """The body of the method whose signature starts with head (brace-matched)."""
    i = code.find(head)
    if i < 0:
        raise ValueError("method not found: " + head)
    j = code.index("{", i)
    depth = 0
    for e in range(j, len(code)):
        depth += {"{": 1, "}": -1}.get(code[e], 0)
        if depth == 0:
            return code[i:e + 1]
    raise ValueError("unbalanced braces after: " + head)


def source_pins(swim_text: str, pit_text: str) -> list[str]:
    """Failures (empty = all hold) for the production climb inputs of the shore search."""
    fails: list[str] = []

    def need(ok: bool, what: str) -> None:
        if not ok:
            fails.append(what)

    sw, pit = _code(swim_text), _code(pit_text)
    try:
        nf = _method(sw, "public static IntVec3 NearestFooting(Pawn p, Map map, RM_MapComponent_Excavation ex)")
        cs = _method(sw, "private static bool CanStep(Map map, RM_MapComponent_Excavation ex, Pawn p, IntVec3 c, "
                         "IntVec3 n, int k)")
        ex = _method(pit, "public static bool ExitInReach(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 c)")
    except ValueError as e:
        return [str(e)]
    # the climb limit: the pawn's own, assigned once, never overwritten
    need(nf.count("int k = RM_PocketGrid.ClimbLimitOf(p);") == 1, "NearestFooting: k is not exactly ClimbLimitOf(p)")
    need(len(re.findall(r"(?<![\w.])k\s*(=|\+=|-=|\*=|/=|\+\+|--)(?!=)", nf)) == 1,
         "NearestFooting: k is assigned more than once")
    need(not re.search(r"(?<![\w.])k\s*(=|\+=|-=|\*=|/=|\+\+|--)(?!=)", cs), "CanStep: k is overwritten")
    need("MaxValue" not in nf and "MaxValue" not in cs, "a MaxValue climb limit or depth")
    # the edge: (c, n) handed in order, with that k, while the masks are on
    need("(c, n) => n.InBounds(map) && n.Walkable(map) && (!climbRule || CanStep(map, ex, p, c, n, k))" in nf,
         "NearestFooting: the edge lambda does not hand (c, n, k) to CanStep")
    need("bool climbRule = ex != null && RM_CliffMask.On;" in nf, "NearestFooting: climb gate not tied to the cliff masks")
    need("RM_SwimMath.NearestReachableFooting(p.Position, CardinalNeighbours," in nf, "NearestFooting: shared search unused")
    # the step's depths: from at c, to at n, each read once and never overwritten
    need(cs.count("int fromD = RM_SuperdeepTrap.StepDepthAt(map, ex, c);") == 1, "CanStep: fromD is not StepDepthAt(c)")
    need(cs.count("int toD = RM_SuperdeepTrap.StepDepthAt(map, ex, n);") == 1, "CanStep: toD is not StepDepthAt(n)")
    need(len(re.findall(r"(?<![\w.])(fromD|toD)\s*(=|\+=|-=|\+\+|--)(?!=)", cs)) == 2,
         "CanStep: fromD/toD reassigned")
    need("if (fromD == toD) { return true; }" in cs, "CanStep: level-step shortcut changed")
    need("bool joined = RM_ClimbJoins.ForPawn(map, ex, c, n, fromD, toD, p, out _, out _);" in cs,
         "CanStep: joins not read for this pawn between c and n")
    need("return RM_PitTrapMath.StepAllowed(fromD, toD, k, joined);" in cs, "CanStep: StepAllowed not fed (fromD, toD, k, joined)")
    # the drowning rule's exit reads the same inputs (if it ever drifts, the two rules disagree on what is climbable)
    need("int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, c);" in ex and "int k = RM_PocketGrid.ClimbLimitOf(p);" in ex
         and "int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, n);" in ex
         and "RM_ClimbJoins.ForPawn(map, eng, c, n, fromD, toD, p, out _, out _)" in ex,
         "RM_Drowning.ExitInReach no longer reads the inputs the shore search mirrors")
    return fails


# Each mutant breaks one production climb input; the pins must go red on every one (the pins' own can-fail check).
SWIM_MUTANTS = {
    "k = int.MaxValue": ("int k = RM_PocketGrid.ClimbLimitOf(p);", "int k = int.MaxValue;"),
    "k = 99": ("int k = RM_PocketGrid.ClimbLimitOf(p);", "int k = 99;"),
    "k overwritten": ("int k = RM_PocketGrid.ClimbLimitOf(p);", "int k = RM_PocketGrid.ClimbLimitOf(p); k = 1000;"),
    "toD reads c": ("int toD = RM_SuperdeepTrap.StepDepthAt(map, ex, n);",
                    "int toD = RM_SuperdeepTrap.StepDepthAt(map, ex, c);"),
    "fromD reads n": ("int fromD = RM_SuperdeepTrap.StepDepthAt(map, ex, c);",
                      "int fromD = RM_SuperdeepTrap.StepDepthAt(map, ex, n);"),
    "edge lambda swapped": ("(c, n) => n.InBounds", "(n, c) => n.InBounds"),
    "CanStep cells swapped": ("CanStep(map, ex, p, c, n, k)", "CanStep(map, ex, p, n, c, k)"),
    "StepAllowed limit dropped": ("StepAllowed(fromD, toD, k, joined)", "StepAllowed(fromD, toD, 1000, joined)"),
    "toD overwritten": ("if (fromD == toD)", "toD = fromD; if (fromD == toD)"),
    "joins always": ("bool joined = RM_ClimbJoins.ForPawn(map, ex, c, n, fromD, toD, p, out _, out _);",
                     "bool joined = true;"),
    "gate off": ("bool climbRule = ex != null && RM_CliffMask.On;", "bool climbRule = false;"),
}


def mutant_survivors(swim_text: str, pit_text: str) -> list[str]:
    """Mutants the pins fail to catch (empty = every one goes red). A mutant whose target text is gone is a survivor."""
    out = []
    for name, (a, b) in SWIM_MUTANTS.items():
        if a not in swim_text or not source_pins(swim_text.replace(a, b, 1), pit_text):
            out.append(name)
    drift = pit_text.replace("int k = RM_PocketGrid.ClimbLimitOf(p);", "int k = 3;", 1)
    if drift == pit_text or not source_pins(swim_text, drift):
        out.append("ExitInReach drifts")
    return out


def main() -> int:
    swim_text, pit_text = SWIM.read_text(encoding="utf-8"), PIT.read_text(encoding="utf-8")
    fails = source_pins(swim_text, pit_text)
    if not fails:
        fails = ["mutant not caught: " + m for m in mutant_survivors(swim_text, pit_text)]
    for f in fails:
        print("FAIL pin: " + f)
    if fails:
        print(f"FAIL: {len(fails)} production climb-input pin(s) broken")
        return 1
    print(f"PASS source pins: production climb inputs (ClimbLimitOf(p), StepDepthAt c->n, joins, StepAllowed); "
          f"{len(SWIM_MUTANTS) + 1}/{len(SWIM_MUTANTS) + 1} mutants red")
    if "--pins-only" in sys.argv[1:]:
        return 0
    r = subprocess.run([sys.executable, str(STOCK), "--only", "Swim_shore_*"], capture_output=True, text=True,
                       timeout=580)
    out = r.stdout + r.stderr
    ok = [c for c in CASES if re.search(r"^ok\s+" + re.escape(c) + r"\s*$", out, re.M)]
    for c in CASES:
        print(("PASS " if c in ok else "FAIL ") + c)
    if r.returncode != 0 or len(ok) != len(CASES):
        print(out[-3000:])
        print(f"FAIL: stock rc={r.returncode}, {len(ok)}/{len(CASES)} shore cases ok")
        return 1
    print(f"PASS: {len(ok)}/{len(CASES)} shore cases ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
