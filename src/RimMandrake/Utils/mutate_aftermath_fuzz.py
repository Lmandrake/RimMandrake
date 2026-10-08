#!/usr/bin/env python3
"""Mutation proof for the Aftermath fuzz: plants each defect in the production kernel / classifier, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations). The kernel mutations run first, then the classifier's.

    python3 src/RimMandrake/Utils/mutate_aftermath_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = [
    ("grace never expires", "return now - openedTick >= ArrivalGraceTicks;", "return false;"),
    ("grace expires at once", "return now - openedTick >= ArrivalGraceTicks;", "return true;"),
    ("grace off by one", "return now - openedTick >= ArrivalGraceTicks;", "return now - openedTick > ArrivalGraceTicks;"),
    ("dead count includes the living", "if (raiders[i].deadOrDowned) n++;", "n++;"),
    ("unarrived raiders count as exited (the original pod defect)", "if (!r.deadOrDowned && !r.spawned && (r.seenSpawned || graceExpired)) n++;", "if (!r.deadOrDowned && !r.spawned) n++;"),
    ("exited counts the downed", "if (!r.deadOrDowned && !r.spawned && (r.seenSpawned || graceExpired)) n++;", "if (!r.spawned && (r.seenSpawned || graceExpired)) n++;"),
    ("exited counts raiders still spawned", "if (!r.deadOrDowned && !r.spawned && (r.seenSpawned || graceExpired)) n++;", "if (!r.deadOrDowned && (r.seenSpawned || graceExpired)) n++;"),
    ("accounted-for ignores unarrived raiders (the original pod defect)", "if (!r.seenSpawned && !graceExpired) return false;", ""),
    ("accounted-for ignores standing raiders", "if (r.spawned) return false;", ""),
    ("accounted-for ignores the dead skip", "if (r.deadOrDowned) continue;", ""),
    ("outcome eligibility ignores survivors", "return kindIsBattleOutcome && outcomeListed && survivors >= minSurvivors;", "return kindIsBattleOutcome && outcomeListed;"),
    ("outcome eligibility survivors strict", "return kindIsBattleOutcome && outcomeListed && survivors >= minSurvivors;", "return kindIsBattleOutcome && outcomeListed && survivors > minSurvivors;"),
    ("outcome eligibility ignores the kind", "return kindIsBattleOutcome && outcomeListed && survivors >= minSurvivors;", "return outcomeListed && survivors >= minSurvivors;"),
    ("held eligibility strict", "return kindIsPrisonerHeld && heldDays >= minHeldDays;", "return kindIsPrisonerHeld && heldDays > minHeldDays;"),
    ("held eligibility ignores the kind", "return kindIsPrisonerHeld && heldDays >= minHeldDays;", "return heldDays >= minHeldDays;"),
    ("discipline per faction off by one", "if (liveForFaction >= maxPerFaction) return false;", "if (liveForFaction > maxPerFaction) return false;"),
    ("discipline total off by one", "if (liveTotal >= maxTotal) return false;", "if (liveTotal > maxTotal) return false;"),
    ("discipline ignores the total", "if (liveTotal >= maxTotal) return false;", ""),
    ("window excludes its end", "return !(sinceBattleTicks < 0 || sinceBattleTicks > windowTicks);", "return !(sinceBattleTicks < 0 || sinceBattleTicks >= windowTicks);"),
    ("window admits the past", "return !(sinceBattleTicks < 0 || sinceBattleTicks > windowTicks);", "return !(sinceBattleTicks > windowTicks);"),
    ("window in hours not days", "public static int WindowTicks(float days) { return (int)(days * TicksPerDay); }", "public static int WindowTicks(float days) { return (int)(days * 2500); }"),
    ("delay in hours not days", "public static int DelayTicks(float days) { return (int)(days * TicksPerDay); }", "public static int DelayTicks(float days) { return (int)(days * 2500); }"),
    ("prisoner clock forgets nobody", "foreach (int id in gone) { firstSeen.Remove(id); fired.Remove(id); }", ""),
    ("prisoner clock keeps the fired flag after release", "foreach (int id in gone) { firstSeen.Remove(id); fired.Remove(id); }", "foreach (int id in gone) { firstSeen.Remove(id); }"),
    ("prisoner clock restarts every poll", "foreach (int id in currentAcrossAllMaps) if (!firstSeen.ContainsKey(id)) firstSeen[id] = now;", "foreach (int id in currentAcrossAllMaps) firstSeen[id] = now;"),
    ("prisoner clock never starts", "foreach (int id in currentAcrossAllMaps) if (!firstSeen.ContainsKey(id)) firstSeen[id] = now;", ""),
    ("held days in hours", "return firstSeen.TryGetValue(id, out t) ? (now - t) / (float)RM_AftermathKernel.TicksPerDay : 0f;", "return firstSeen.TryGetValue(id, out t) ? (now - t) / 2500f : 0f;"),
    ("held days of the untracked", "return firstSeen.TryGetValue(id, out t) ? (now - t) / (float)RM_AftermathKernel.TicksPerDay : 0f;", "return firstSeen.TryGetValue(id, out t) ? (now - t) / (float)RM_AftermathKernel.TicksPerDay : 99f;"),
]

CLASSIFIER = [
    ("classifier threshold 50%", "if (fraction >= 0.6f)", "if (fraction >= 0.5f)"),
    ("classifier threshold strict", "if (fraction >= 0.6f)", "if (fraction > 0.6f)"),
    ("classifier casualty before repelled", "if (fraction >= 0.6f)\n                return BattleOutcome.Repelled;\n\n            if (colonistCasualty)\n                return BattleOutcome.Lost;", "if (colonistCasualty)\n                return BattleOutcome.Lost;\n\n            if (fraction >= 0.6f)\n                return BattleOutcome.Repelled;"),
    ("classifier routed without survivors", "if (raidersSurvivedAndExited > 0)", "if (raidersSurvivedAndExited >= 0)"),
    ("classifier degenerate input", "if (totalRaiders <= 0)\n                return BattleOutcome.Stalemate;", "if (totalRaiders < 0)\n                return BattleOutcome.Stalemate;"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = run_mutations("src/RimMandrake/Aftermath/Source/Kernel/RM_AftermathKernel.cs", "selftest_aftermath_fuzz.py", KERNEL, only)
    rc2 = run_mutations("src/RimMandrake/Aftermath/Source/BattleOutcomeClassifier.cs", "selftest_aftermath_fuzz.py", CLASSIFIER, only)
    sys.exit(rc or rc2)
