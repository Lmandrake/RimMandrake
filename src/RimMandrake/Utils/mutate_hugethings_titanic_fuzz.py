#!/usr/bin/env python3
"""Mutation proof for the titan half of the Huge Things fuzz: plants each defect in the titan kernel (RM_TitanicKernel.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught. The first entry is the ORIGINAL shipped defect (a T3 titan crushed
non-buildings for the T1 damage, less than a T2): the fuzz must have caught it.

    python3 src/RimMandrake/Utils/mutate_hugethings_titanic_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

# Equivalent mutants (not listed): clamp-above on the yield factor (the slider caps the floor at 1), the b = max(size, floor) guard (the clamp hides it),
# the DefQualifies ternary in OverrideFootprint (force-in always qualifies; removed from the kernel), and the day length (lint_hugethings_titanic_defs.py pins 60000).
KERNEL = "src/RimMandrake/HugeThings/Source/Kernel/RM_TitanicKernel.cs"
MUTATIONS = [
    ("T3 crush hits softer than T2 (original bug)", "return (tier >= T2 ? CrushDamageHeavy : CrushDamageLight) * multiplier;", "return (tier == T2 ? CrushDamageHeavy : CrushDamageLight) * multiplier;"),
    ("T3 floor exclusive", "if (bodySize >= t3) tier = T3;", "if (bodySize > t3) tier = T3;"),
    ("T2 floor exclusive", "else if (bodySize >= t2) tier = T2;", "else if (bodySize > t2) tier = T2;"),
    ("T1 floor exclusive", "else if (bodySize >= t1) tier = T1;", "else if (bodySize > t1) tier = T1;"),
    ("force-out ignored", "if (force == ForceOut) return None;\n            int tier;", "int tier;"),
    ("force-in does not floor at T1", "if (tier == None && force == ForceIn) tier = T1;", ""),
    ("DefQualifies ignores force-in", "if (force == ForceIn) return true;\n            return baseBodySize >= t1;", "return baseBodySize >= t1;"),
    ("DefQualifies ignores force-out", "if (force == ForceOut) return false;\n            if (force == ForceIn) return true;", "if (force == ForceIn) return true;"),
    ("DefQualifies floor exclusive", "return baseBodySize >= t1;", "return baseBodySize > t1;"),
    ("footprint T3 is 3", "case T3: return 4;", "case T3: return 3;"),
    ("footprint T2 is 2", "case T2: return 3;", "case T2: return 2;"),
    ("override force-out not 1", "if (force == ForceOut) return 1;\n            return FootprintSize", "if (force == ForceOut) return 2;\n            return FootprintSize"),
    ("qualified tier T3 exclusive", "if (bodySize >= t3) return T3;\n            if (bodySize >= t2) return T2;\n            return T1;", "if (bodySize > t3) return T3;\n            if (bodySize >= t2) return T2;\n            return T1;"),
    ("yield factor unclamped below", "if (v < min) v = min;\n            else if", "if (false) v = min;\n            else if"),
    ("yield curve is linear", "Clamp((float)Math.Sqrt(floor / b), minFactor, 1f)", "Clamp(floor / b, minFactor, 1f)"),
    ("yield floor swapped", "return tier == T1 ? t1 : t2;", "return tier == T1 ? t2 : t1;"),
    ("crush ignores minTier", "return tier != None && crushable && tier >= minTier;", "return tier != None && crushable;"),
    ("crush ignores crushable", "return tier != None && crushable && tier >= minTier;", "return tier != None && tier >= minTier;"),
    ("untiered pawn crushes", "return tier != None && crushable && tier >= minTier;", "return crushable && tier >= minTier;"),
    ("T2 destroys buildings outright", "return tier == T3 && isBuilding;", "return tier >= T2 && isBuilding;"),
    ("T3 destroys pawns' non-buildings", "return tier == T3 && isBuilding;", "return tier == T3;"),
    ("thick roof holed", "return tier >= T2 && hasRoof && !thick;", "return tier >= T2 && hasRoof;"),
    ("T1 holes roofs", "return tier >= T2 && hasRoof && !thick;", "return tier >= T1 && hasRoof && !thick;"),
    ("rubble without a roll", "return tier >= T1 && rolledUnderChance;", "return tier >= T1;"),
    ("untiered pawn leaves rubble", "return tier >= T1 && rolledUnderChance;", "return rolledUnderChance;"),
    ("spoilage floors instead of ceils", "int loss = (int)Math.Ceiling(remaining * perDay);", "int loss = (int)Math.Floor(remaining * perDay);"),
    ("spoilage unclamped", "return Math.Min(remaining, Math.Max(0, loss));", "return loss;"),
    ("harvest takes the whole pool", "return Math.Max(0, Math.Min(remaining, perSession));", "return Math.Max(0, remaining);"),
    ("harvest ignores the pool", "return Math.Max(0, Math.Min(remaining, perSession));", "return Math.Max(0, perSession);"),
    ("ladder accepts t2 == t3", "return t1 > 0f && t1 < t2 && t2 < t3;", "return t1 > 0f && t1 < t2 && t2 <= t3;"),
    ("ladder accepts t1 == 0", "return t1 > 0f && t1 < t2 && t2 < t3;", "return t1 >= 0f && t1 < t2 && t2 < t3;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_hugethings_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
