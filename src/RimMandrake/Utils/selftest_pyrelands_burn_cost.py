#!/usr/bin/env python3
"""FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: offline guards on the two big-burn hot paths of the Pyrelands DLL, no game.

The diagnosis (GPT pre-release hunt 2026-10-15, confirmed by reading the code 2026-11-02):

1. Patch_FireTick_AshAndScorchFruit.Postfix (FireEcologyHook.cs) runs for EVERY Fire on every TickInterval. Its 3x3 fruit-spot
   test was a lambda capturing the method's top-level locals `pos` and `map`, so C# hoisted both into a closure object that was
   allocated on every call -- every fire, every interval, already rolled or not. Now a static scan (FirstLegalFruitSpot) feeds
   RM_FireEcoKernel.TakeFruitRollAt; the 9 probes still run only for a fire that has not yet taken its one roll.
2. A burrowed pawn's wait toil (RM_JobDriver_Burrow) asked RM_JobGiver_BurrowOnFire.FireIsNear EVERY tick, and FireIsNear walked
   every Fire on the map. Now the scan runs once per PyrelandsTuning.BurrowEmergeCheckIntervalTicks, staggered by pawn id
   (RM_FireEcoKernel.BurrowEmergeCheckDue), and walks the radius's cells instead when the burn holds more fires than the disc
   holds cells (RM_FireEcoKernel.FireScanByCells).

The kernels themselves are proven by the units family of selftest_pyrelands_fuzz.py. This file guards the call sites (a
regression back to a lambda or an every-tick scan) and prints the per-tick cost model of a 250x250 burn before and after.
The live tick-rate row (validation.py big_burn_tick_cost) stays CALIBRATING evidence, never a gate.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "Pyrelands", "Source")

FAILS = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)
        print("FAIL " + msg)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def method_body(text, signature):
    """The brace-balanced body of the first method whose header contains `signature`."""
    i = text.find(signature)
    if i < 0:
        return None
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j:k + 1]
    return None


def strip_comments(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def main():
    hook = read("FireEcologyHook.cs")
    post = method_body(hook, "public static void Postfix(Fire __instance, int delta)")
    check(post is not None, "Patch_FireTick_AshAndScorchFruit.Postfix not found in FireEcologyHook.cs")
    if post:
        code = strip_comments(post)
        check("=>" not in code, "the fire-tick Postfix holds a lambda again: a capture of pos/map allocates a closure per fire per interval")
        check("delegate" not in code, "the fire-tick Postfix holds an anonymous delegate")
        check("TakeFruitRollAt(" in code and "FirstLegalFruitSpot(" in code, "the Postfix no longer rolls through FirstLegalFruitSpot + TakeFruitRollAt")
        roll = code.find("TakeFruitRollAt(")
        gate = code.find("!rolledFires.Contains(__instance.thingIDNumber)")
        check(0 <= gate < roll, "the 3x3 scan is no longer gated on the fire not having rolled yet")
    scan = method_body(hook, "private static int FirstLegalFruitSpot(IntVec3 pos, Map map)")
    check(scan is not None and "=>" not in strip_comments(scan), "FirstLegalFruitSpot missing or allocating")

    driver = read("RM_JobDriver_Burrow.cs")
    toil = driver[driver.find("hide.tickAction"):driver.find("hide.AddFinishAction")]
    toil = strip_comments(toil)
    check("BurrowEmergeCheckDue(" in toil, "the burrow wait toil no longer throttles its fire scan (BurrowEmergeCheckDue)")
    due = toil.find("BurrowEmergeCheckDue(")
    near = toil.find("FireIsNear(")
    check(0 <= due < near and "checkDue &&" in toil, "FireIsNear is not behind the checkDue gate in the burrow wait toil")

    giver = strip_comments(method_body(read("RM_JobGiver_BurrowOnFire.cs"), "internal static bool FireIsNear(") or "")
    check("FireScanByCells(" in giver and "ThingsListAtFast(" in giver, "FireIsNear lost its radial-cell path for a big burn")

    tuning = read("PyrelandsTuning.cs")
    m = re.search(r"BurrowEmergeCheckIntervalTicks\s*=\s*(\d+)", tuning)
    check(m is not None, "PyrelandsTuning.BurrowEmergeCheckIntervalTicks missing")
    interval = int(m.group(1)) if m else 1
    m = re.search(r"BurrowDetectionRadius\s*=\s*([\d.]+)f", tuning)
    radius = float(m.group(1)) if m else 15.0

    # Cost model of a 250x250 standing-grass burn: the front holds `fires` concurrent Fire things; 20 burrowers are down.
    # Distance tests (or cell reads) per tick for the burrowers; closures per tick for the fire postfix, MODELLED (not measured)
    # at one Fire.TickInterval call per fire per 15 ticks -- only the "-> 0" side of that column is a property of the code.
    disc = sum(1 for dx in range(-int(radius), int(radius) + 1) for dz in range(-int(radius), int(radius) + 1)
               if dx * dx + dz * dz <= radius * radius)
    burrowers = 20
    print("cost model, 250x250 burn, %d burrowers, radius %.0f (disc %d cells), check every %d ticks:" % (burrowers, radius, disc, interval))
    for fires in (200, 1000, 4000):
        before = burrowers * fires
        per_scan = min(fires, disc)
        after = burrowers * per_scan / float(interval)
        calls = fires / 15.0
        print("  fires %5d: burrower tests/tick %8d -> %8.0f (x%.0f); fire-postfix closures/tick %6.0f -> 0"
              % (fires, before, after, before / max(after, 1e-9), calls))
        check(after * interval <= burrowers * max(disc, fires) and after < before, "the cost model did not fall at %d fires" % fires)

    if FAILS:
        print("selftest_pyrelands_burn_cost: %d FAIL" % len(FAILS))
        return 1
    print("selftest_pyrelands_burn_cost: PASS (fire postfix closure-free, burrow scan throttled x%d and disc-bounded)" % interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
