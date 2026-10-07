#!/usr/bin/env python3
"""Mutation proof for the TheSump fuzz: plants each defect in the kernel (RM_SumpKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_thesump_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/TheSump/Source/Kernel/RM_SumpKernel.cs"
MUTATIONS = [
    ("stage threshold exclusive", "if (kg >= stageLoadKg[i]) s = i + 1;", "if (kg > stageLoadKg[i]) s = i + 1;"),
    ("stage off by one", "if (kg >= stageLoadKg[i]) s = i + 1;", "if (kg >= stageLoadKg[i]) s = i;"),
    ("hediff severity", "return stage + 0.01f;", "return stage + 0.1f;"),
    ("downed kethrel still acts", "if (!enabled || dead || !spawned || downed) return KethrelAction.None;", "if (!enabled || dead || !spawned) return KethrelAction.None;"),
    ("dead kethrel still acts", "if (!enabled || dead || !spawned || downed) return KethrelAction.None;", "if (!enabled || !spawned || downed) return KethrelAction.None;"),
    ("molt threshold exclusive", "if (loadKg() >= moltLoadKg) return KethrelAction.Molt;", "if (loadKg() > moltLoadKg) return KethrelAction.Molt;"),
    ("molts without tar check order", "if (!tarNearby()) return KethrelAction.None;\n            if (itemInPickupReach())", "if (itemInPickupReach()) return KethrelAction.PickUp;\n            if (!tarNearby()) return KethrelAction.None;\n            if (itemInPickupReach())"),
    ("picks up away from tar", "if (!tarNearby()) return KethrelAction.None;", ""),
    ("seeks while busy", "if (idle() && seekItemReachable()) return KethrelAction.Seek;", "if (seekItemReachable()) return KethrelAction.Seek;"),
    ("seeks unreachable items", "if (idle() && seekItemReachable()) return KethrelAction.Seek;", "if (idle()) return KethrelAction.Seek;"),
    ("probes the map eagerly", "if (loadKg() >= moltLoadKg) return KethrelAction.Molt;", "bool t0 = tarNearby(); if (loadKg() >= moltLoadKg) return KethrelAction.Molt;"),
    ("wears forbidden items", "if (!thingOk || !isItem || forbiddenForIt) return false;", "if (!thingOk || !isItem) return false;"),
    ("wears non-items", "if (!thingOk || !isItem || forbiddenForIt) return false;", "if (!thingOk || forbiddenForIt) return false;"),
    ("ignores the weapon/list rule", "if (!isWeaponOrListed) return false;", ""),
    ("value ceiling inclusive", "if (marketValueTotal > valueCeiling) return false;", "if (marketValueTotal >= valueCeiling) return false;"),
    ("takes colony property", "if (!takeColonyProperty && onHomeArea) return false;", ""),
    ("tar match is case-insensitive", "return defName != null && defName.Contains(\"Tar\");", "return defName != null && defName.ToLowerInvariant().Contains(\"tar\");"),
    ("fail chance base", "public const float MoltFailBase = 0.45f;", "public const float MoltFailBase = 0.5f;"),
    ("fail chance ceiling", "public const float MoltFailMax = 0.9f;", "public const float MoltFailMax = 1.0f;"),
    ("handler: last of equals", "if (skills[i] > bestSkill) { bestSkill = skills[i]; best = i; }", "if (skills[i] >= bestSkill) { bestSkill = skills[i]; best = i; }"),
    ("handler ignores ability", "if (!able[i]) continue;", ""),
    ("vault never seals arrivals", "sealedThings.Add(t);\n                seal(t);", "sealedThings.Add(t);"),
    ("vault never unseals", "if (t != null && !destroyed(t)) unseal(t);", ""),
    ("vault keeps absent things", "if (t != null && !destroyed(t) && present.Contains(t)) continue;", "if (t != null && !destroyed(t)) continue;"),
    ("vault re-seals every scan", "if (sealedThings.Contains(t)) continue;\n                sealedThings.Add(t);", "sealedThings.Add(t);"),
    ("extraction ignores the seal", "if (target == null || targetDestroyed || !sealedThings.Contains(target)) return ExtractPlan.Ignore;", "if (target == null || targetDestroyed) return ExtractPlan.Ignore;"),
    ("extraction always clean", "return solventOnHand ? ExtractPlan.Clean : ExtractPlan.Ruined;", "return ExtractPlan.Clean;"),
    ("extraction always ruined", "return solventOnHand ? ExtractPlan.Clean : ExtractPlan.Ruined;", "return ExtractPlan.Ruined;"),
    ("forget does nothing", "public void Forget(T target) { sealedThings.Remove(target); }", "public void Forget(T target) { }"),
    ("ruined stack may be empty", "public static int RuinedStack(int count) { return Math.Max(1, count); }", "public static int RuinedStack(int count) { return count; }"),
    ("scan interval ignored", "if (scanIntervalTicks <= 0 || ticksGame % scanIntervalTicks != 0) return false;", "if (scanIntervalTicks <= 0) return false;"),
    ("scan with the setting off", "if (!enabled) return false;", ""),
    ("edge distance uses max", "return Math.Min(distX, distZ);", "return Math.Max(distX, distZ);"),
    ("seed may sit in the edge band", "return EdgeDistance(x, z, g.Width, g.Height) >= MinEdgeDistance && g.CanCarry(x, z);", "return EdgeDistance(x, z, g.Width, g.Height) > MinEdgeDistance && g.CanCarry(x, z);"),
    ("seed ignores the ground", "return EdgeDistance(x, z, g.Width, g.Height) >= MinEdgeDistance && g.CanCarry(x, z);", "return EdgeDistance(x, z, g.Width, g.Height) >= MinEdgeDistance;"),
    ("blob overshoots", "while (placed.Count < targetSize && frontier.Count > 0 && attempts-- > 0)", "while (placed.Count <= targetSize && frontier.Count > 0 && attempts-- > 0)"),
    ("blob grows into blocked ground", "if (placed.Contains(nk) || !g.CanCarry(nx, nz)) continue;", "if (placed.Contains(nk)) continue;"),
    ("blob re-enters its own cells", "if (placed.Contains(nk) || !g.CanCarry(nx, nz)) continue;", "if (!g.CanCarry(nx, nz)) continue;"),
    ("dead frontier cells never dropped", "frontier.RemoveAt(pick);\n                    continue;", "continue;"),
    ("reservoir keeps the last", "if (rng.Range(0, seen) == 0) target = nk;", "target = nk;"),
    ("reservoir biased", "if (rng.Range(0, seen) == 0) target = nk;", "if (rng.Range(0, seen + 1) == 0) target = nk;"),
    ("direction table: no south", "int nz = fz + (i == 0 ? 1 : i == 1 ? 0 : i == 2 ? -1 : 0);", "int nz = fz + (i == 0 ? 1 : i == 1 ? 0 : i == 2 ? 1 : 0);"),
    ("rim includes the blob", "if (!blob.Contains(nk)) rim.Add(nk);", "rim.Add(nk);"),
    ("rim skips a side", "int nx = x + (i == 0 ? 0 : i == 1 ? 1 : i == 2 ? 0 : -1);\n                    int nz = z + (i == 0 ? 1 : i == 1 ? 0 : i == 2 ? -1 : 0);\n                    if (nx < 0", "int nx = x + (i == 0 ? 0 : i == 1 ? 1 : i == 2 ? 0 : 1);\n                    int nz = z + (i == 0 ? 1 : i == 1 ? 0 : i == 2 ? -1 : 0);\n                    if (nx < 0"),
    ("undersized mere accepted", "public static bool Acceptable(int blobCells) { return blobCells >= MinMereCells; }", "public static bool Acceptable(int blobCells) { return blobCells >= MinMereCells - 1; }"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_thesump_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
