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
QUIET = [False]
OVERRIDES = {}  # file name -> mutated source text, for the in-memory sabotage pass


def check(ok, msg):
    if not ok:
        FAILS.append(msg)
        if not QUIET[0]:
            print("FAIL " + msg)


def read(name):
    if name in OVERRIDES:
        return OVERRIDES[name]
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


# Each mutant breaks one clause of the item; the call-site checks must go red on every one (the blind check at 2a9561dae3
# found the first two stayed green). (file, original text, mutated text, clause broken).
MUTANTS = [
    ("RM_JobDriver_Burrow.cs", "bool checkDue = map == null", "bool checkDue = true || map == null",
     "every-tick scan back via a constant disjunct"),
    ("RM_JobGiver_BurrowOnFire.cs", "if (RM_FireEcoKernel.FireScanByCells(fires.Count, discCells))",
     "if (!RM_FireEcoKernel.FireScanByCells(fires.Count, discCells))", "costlier scan chosen (negated)"),
    ("RM_JobGiver_BurrowOnFire.cs", "FireScanByCells(fires.Count, discCells)", "FireScanByCells(discCells, fires.Count)",
     "costlier scan chosen (arguments swapped)"),
    ("RM_JobDriver_Burrow.cs", "bool safeToEmerge = checkDue && (", "bool safeToEmerge = (checkDue || true) && (",
     "fire scan escapes the gate"),
    ("RM_JobDriver_Burrow.cs", "pawn.thingIDNumber, PyrelandsTuning.BurrowEmergeCheckIntervalTicks)",
     "pawn.thingIDNumber, 1)", "interval 1 at the call site"),
    ("PyrelandsTuning.cs", "BurrowEmergeCheckIntervalTicks = 30", "BurrowEmergeCheckIntervalTicks = 1", "interval 1 in tuning"),
    ("RM_JobGiver_BurrowOnFire.cs", "                return false;\n            }\n            for (int i",
     "            }\n            for (int i", "radial branch falls through to the all-fires walk"),
    ("FireEcologyHook.cs", "if (rolledFires != null && !rolledFires.Contains(", "if (true || rolledFires != null && !rolledFires.Contains(",
     "3x3 probes run for an already-rolled fire"),
    ("FireEcologyHook.cs", "if (rolledFires != null && !rolledFires.Contains(",
     "int spot0 = FirstLegalFruitSpot(pos, map);\n                if (rolledFires != null && !rolledFires.Contains(",
     "9 probes hoisted above the not-yet-rolled gate"),
]


def stamp_check():
    """The committed FireEcologyHook.dll was built from the committed source (dll_source_stamp recomputed at HEAD)."""
    sys.path.insert(0, HERE)
    import dll_source_stamp as dss
    repo = dss._repo_root()
    stamp = "src/RimMandrake/Pyrelands/Assemblies/FireEcologyHook.dll.srchash"
    cat = dss.BatchCat(repo)
    try:
        r = dss.recompute_stamp(cat, "HEAD", stamp, repo)
    finally:
        cat.close()
    check(r.status == "MATCH", "FireEcologyHook.dll stamp %s at HEAD: %s" % (r.status, "; ".join(r.detail)))


def sabotage():
    """Every mutant must turn the call-site checks red; restores nothing on disk because nothing on disk is touched."""
    survivors = []
    for f, a, b, why in MUTANTS:
        orig = read(f)
        if orig.count(a) < 1:
            survivors.append("%s: mutant anchor missing (%s)" % (f, why))
            continue
        OVERRIDES[f] = orig.replace(a, b, 1)
        before = len(FAILS)
        QUIET[0] = True
        try:
            call_sites()
        finally:
            QUIET[0] = False
            del OVERRIDES[f]
        caught = len(FAILS) > before
        del FAILS[before:]
        print("  sabotage %-28s %-50s -> %s" % (f, why, "RED (caught)" if caught else "GREEN (MISSED)"))
        if not caught:
            survivors.append("%s: %s" % (f, why))
    for m in survivors:
        check(False, "sabotage survived: " + m)


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


def call_sites():
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
        # The gate's exact condition, and the scan inside its block: a `true ||` in front keeps every string above.
        pflat = re.sub(r"\s+", "", code)
        g = pflat.find("if(rolledFires!=null&&!rolledFires.Contains(__instance.thingIDNumber)){")
        check(g >= 0, "the roll gate is no longer exactly rolledFires != null && !rolledFires.Contains(__instance.thingIDNumber)")
        block = method_body(pflat[g:], "if(") if g >= 0 else None
        check(block is not None and pflat.count("FirstLegalFruitSpot(") == 1 and "FirstLegalFruitSpot(" in block,
              "FirstLegalFruitSpot (the 9 probes) runs outside the not-yet-rolled block")
    scan = method_body(hook, "private static int FirstLegalFruitSpot(IntVec3 pos, Map map)")
    check(scan is not None and "=>" not in strip_comments(scan), "FirstLegalFruitSpot missing or allocating")

    driver = read("RM_JobDriver_Burrow.cs")
    toil = driver[driver.find("hide.tickAction"):driver.find("hide.AddFinishAction")]
    toil = strip_comments(toil)
    check("BurrowEmergeCheckDue(" in toil, "the burrow wait toil no longer throttles its fire scan (BurrowEmergeCheckDue)")
    due = toil.find("BurrowEmergeCheckDue(")
    near = toil.find("FireIsNear(")
    check(0 <= due < near and "checkDue &&" in toil, "FireIsNear is not behind the checkDue gate in the burrow wait toil")

    # The gate's EXPRESSION, not just its presence: checkDue may be true only off-map, at the timeout, or on the staggered
    # check tick. A constant or extra disjunct (`true || ...`) puts the every-tick scan back while every string above survives.
    flat = re.sub(r"\s+", "", toil)
    m = re.search(r"boolcheckDue=([^;]*);", flat)
    check(m is not None, "the burrow wait toil no longer assigns checkDue")
    if m:
        terms = sorted(m.group(1).split("||"))
        want = sorted(["map==null", "timedOut",
                       "RM_FireEcoKernel.BurrowEmergeCheckDue(now,pawn.thingIDNumber,PyrelandsTuning.BurrowEmergeCheckIntervalTicks)"])
        check(terms == want, "checkDue is assigned from %r, not only map==null || timedOut || BurrowEmergeCheckDue(...)" % m.group(1))
    check(len(re.findall(r"(?<![\w.])checkDue=", flat)) == 0 and flat.count("boolcheckDue=") == 1,
          "checkDue is reassigned after its gate")
    m = re.search(r"boolsafeToEmerge=([^;]*);", flat)
    check(m is not None and m.group(1).startswith("checkDue&&(") and m.group(1).count("FireIsNear(") == 1,
          "safeToEmerge is not checkDue && (...FireIsNear...): the fire scan escapes the gate")
    check(flat.count("FireIsNear(") == 1, "the burrow wait toil calls FireIsNear outside the safeToEmerge gate")
    m = re.search(r"BurrowEmergeCheckIntervalTicks\s*=\s*(\d+)", read("PyrelandsTuning.cs"))
    check(m is not None and int(m.group(1)) > 1, "BurrowEmergeCheckIntervalTicks <= 1 is an every-tick scan")

    giver = strip_comments(method_body(read("RM_JobGiver_BurrowOnFire.cs"), "internal static bool FireIsNear(") or "")
    check("FireScanByCells(" in giver and "ThingsListAtFast(" in giver, "FireIsNear lost its radial-cell path for a big burn")
    # Which branch is which: the FireScanByCells-TRUE branch must be the disc-cell loop, the fall-through the all-fires walk.
    # A negated condition (`!FireScanByCells`) or swapped arguments runs the costlier scan every time.
    gflat = re.sub(r"\s+", "", giver)
    m = re.search(r"if\(([^{]*FireScanByCells[^{]*)\)\{", gflat)
    check(m is not None and m.group(1) == "RM_FireEcoKernel.FireScanByCells(fires.Count,discCells)",
          "FireIsNear's branch condition is %r, not RM_FireEcoKernel.FireScanByCells(fires.Count, discCells)" % (m.group(1) if m else None))
    if m:
        branch = method_body(gflat[m.start():], "if(")
        rest = gflat[m.start() + len(branch or ""):]
        check(branch is not None and "ThingsListAtFast(" in branch and "RadialPattern[" in branch and "fires[" not in branch,
              "the FireScanByCells branch is not the radial-cell loop")
        check(branch is not None and branch.rstrip("}").endswith("returnfalse;"),
              "the radial-cell branch falls through into the all-fires walk")
        check("fires[i]" in rest and "ThingsListAtFast(" not in rest, "the all-fires walk is not the fall-through of FireScanByCells")
    check("discCells=radius>0f&&radius<GenRadial.MaxRadialPatternRadius?GenRadial.NumCellsInRadius(radius):0;" in gflat,
          "discCells is no longer the radius disc's cell count")



def main():
    call_sites()
    if FAILS:
        print("selftest_pyrelands_burn_cost: %d FAIL on the code as it stands" % len(FAILS))
        return 1
    sabotage()
    stamp_check()
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
