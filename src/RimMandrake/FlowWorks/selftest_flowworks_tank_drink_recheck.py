#!/usr/bin/env python3
"""selftest_flowworks_tank_drink_recheck.py — a tank drink re-checks the tank's CURRENT liquid (TANK_DRINK_FIX_LIQUID_SWAPS_MIDJOB).

WHY: GPT review FA_core_sim_3.5 (2026-10-23): JobDriver_RM_DrinkFromTank's continuing guard asked only whether the
stored liquid had a thirst quality, and its finish toil drank `tank.storedLiquid` with no MayDrink check — so a tank
emptied and refilled with brine or toxic water while the pawn walked over was drunk by an ordinary pawn. The driver is
Verse-bound (the C# SelfTest cannot run it), so this reads the PRODUCTION .cs (comments masked) and asserts:
  1. the driver's FailOn calls RM_ThirstUtility.MayDrinkFromTankNow(pawn, Tank.storedLiquid), not QualityOf alone;
  2. the finish toil calls MayDrinkFromTankNow(pawn, liquid) BEFORE tank.TryRemoveLiquid, in the same guard;
  3. MayDrinkFromTankNow asks MayDrink at the pawn's level and lets BreakOnly through only while the pawn is in
     MentalState_RM_DrinkBrine (JobGiver_RM_DrinkBrine also issues RM_DrinkFromTank jobs for salt tanks).

CAN IT FAIL: each run applies undo mutants (GPT's original shapes, a reordered guard, an unconditional BreakOnly) to an
in-memory copy; every mutant must go RED.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_tank_drink_recheck.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

THIRST = Path(__file__).resolve().parent / "Source" / "Thirst"
JOBS = THIRST / "RM_ThirstJobs.cs"
UTIL = THIRST / "RM_ThirstUtility.cs"


def mask_comments(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def block_after(text: str, anchor: str) -> str | None:
    m = re.search(anchor, text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def flat(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def check(jobs: str, util: str) -> list[str]:
    """Return the list of failures (empty = green)."""
    bad: list[str] = []
    jobs, util = mask_comments(jobs), mask_comments(util)
    drv = block_after(jobs, r"class\s+JobDriver_RM_DrinkFromTank\b")
    if drv is None:
        return ["JobDriver_RM_DrinkFromTank not found"]
    d = flat(drv)
    failons = re.findall(r"this\.FailOn\(\(\) => (.*?)\);", d)
    if not any(re.search(r"!\s*RM_ThirstUtility\.MayDrinkFromTankNow\(\s*pawn\s*,\s*Tank\.storedLiquid\s*\)", f)
               for f in failons):
        bad.append("FailOn does not re-check MayDrinkFromTankNow(pawn, Tank.storedLiquid)")
    if any("QualityOf" in f for f in failons):
        bad.append("FailOn still uses the QualityOf-only guard")
    fin = block_after(d, r"finish\.initAction = delegate")
    if fin is None:
        bad.append("finish toil initAction not found")
    else:
        g = re.search(r"if \((.*?)\)\s*\{\s*return;\s*\}", fin)
        guard = g.group(1) if g else ""
        chk = re.search(r"!\s*RM_ThirstUtility\.MayDrinkFromTankNow\(\s*pawn\s*,\s*liquid\s*\)", guard)
        rem = guard.find("TryRemoveLiquid")
        if not chk:
            bad.append("finish guard does not call MayDrinkFromTankNow(pawn, liquid)")
        elif rem < 0 or chk.start() > rem:
            bad.append("finish guard must check MayDrinkFromTankNow BEFORE TryRemoveLiquid")
        if "||" not in guard or re.search(r"&&", guard):
            bad.append("finish guard is not a plain || chain")
        drink = fin.find("RM_ThirstUtility.Drink(")
        if drink < 0 or (g and drink < g.end()):
            bad.append("Drink call is not after the guard")
    helper = block_after(util, r"public static bool MayDrinkFromTankNow\(\s*Pawn pawn\s*,\s*LiquidDef liquid\s*\)")
    if helper is None:
        bad.append("RM_ThirstUtility.MayDrinkFromTankNow(Pawn, LiquidDef) not found")
    else:
        h = flat(helper)
        if not re.search(r"float level = LevelAny\(pawn\);", h):
            bad.append("helper does not read the pawn's level")
        if not re.search(r"if \(MayDrink\(pawn, liquid, level\)\) \{ return true; \}", h):
            bad.append("helper does not ask the plain MayDrink rule first")
        rets = re.findall(r"return ([^;]*);", h)
        for r in rets:
            if "BreakOnly" in r and not re.search(r"pawn\.MentalState is MentalState_RM_DrinkBrine &&", r):
                bad.append("BreakOnly is allowed outside the salt-water break")
        if not any("BreakOnly" in r for r in rets):
            bad.append("salt-break pawns lose the BreakOnly tank (JobGiver_RM_DrinkBrine issues tank jobs)")
        if any(r.strip() == "true" for r in rets[1:]) and h.count("return true;") > 1:
            bad.append("helper has an extra unconditional return true")
        if not re.search(r"if \(pawn == null \|\| liquid == null\) \{ return false; \}", h):
            bad.append("helper does not refuse a null pawn or liquid")
    return bad


MUTANTS = [
    ("GPT's FailOn", "jobs", "!RM_ThirstUtility.MayDrinkFromTankNow(pawn, Tank.storedLiquid)",
     "!RM_ThirstUtility.QualityOf(Tank.storedLiquid).HasValue"),
    ("GPT's unchecked finish", "jobs", "!RM_ThirstUtility.MayDrinkFromTankNow(pawn, liquid)\n\t\t\t\t\t|| ", ""),
    ("check after the debit", "jobs",
     "liquid == null || !RM_ThirstUtility.MayDrinkFromTankNow(pawn, liquid)\n\t\t\t\t\t|| !tank.TryRemoveLiquid(RM_Volume.Units(RM_ThirstMath.TankDrinkLitres))",
     "liquid == null || !tank.TryRemoveLiquid(RM_Volume.Units(RM_ThirstMath.TankDrinkLitres)) || !RM_ThirstUtility.MayDrinkFromTankNow(pawn, liquid)"),
    ("BreakOnly for everyone", "util", "pawn.MentalState is MentalState_RM_DrinkBrine && ", ""),
    ("break pawns lose salt tanks", "util",
     "return pawn.MentalState is MentalState_RM_DrinkBrine && MayDrink(pawn, liquid, level, RM_DrinkUse.BreakOnly);",
     "return false;"),
    ("helper always yes", "util", "if (MayDrink(pawn, liquid, level))", "if (true)"),
]


def main() -> int:
    jobs, util = JOBS.read_text(encoding="utf-8"), UTIL.read_text(encoding="utf-8")
    fails = check(jobs, util)
    for f in fails:
        print(f"FAIL production: {f}")
    for name, which, new, old in MUTANTS:
        src = jobs if which == "jobs" else util
        if src.count(new) != 1:
            fails.append(name)
            print(f"FAIL mutant '{name}': splice text not found exactly once (fix changed shape?)")
            continue
        mj, mu = (src.replace(new, old), util) if which == "jobs" else (jobs, src.replace(new, old))
        if not check(mj, mu):
            fails.append(name)
            print(f"FAIL mutant '{name}' stayed GREEN: the check cannot see it")
        else:
            print(f"ok   mutant '{name}' goes RED")
    if fails:
        print(f"RED ({len(fails)} failure(s))")
        return 1
    print("GREEN: tank drink re-checks MayDrink mid-job and at the sip; salt break keeps BreakOnly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
