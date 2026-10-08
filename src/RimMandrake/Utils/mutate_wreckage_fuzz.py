#!/usr/bin/env python3
"""Mutation proof for the Wreckage fuzz: plants each defect in the kernel (RM_WreckageKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught. The first entry is the ORIGINAL shipped behaviour (a Sealed wreck shifted down
kept the name Sealed because ShiftTier fell through to `return tier`).

    python3 src/RimMandrake/Utils/mutate_wreckage_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/Wreckage/Source/Kernel/RM_WreckageKernel.cs"
MUTATIONS = [
    ("Sealed shifted down stays Sealed (original)", 'if (to == 2) return "Sealed";\n            return "Hull";', 'if (to == 2) return "Sealed";\n            return rank == 0 ? "Hull" : tier;'),
    ("same-rung shift renames the tier", "if (to == rank) return tier;", 'if (to == rank) return rank == 1 ? "Hull" : tier;'),
    ("rail not clamped above", "int to = Math.Max(0, Math.Min(2, rank + shift));", "int to = Math.Max(0, rank + shift);"),
    ("rail not clamped below", "int to = Math.Max(0, Math.Min(2, rank + shift));", "int to = Math.Min(2, rank + shift);"),
    ("mid shifted up lands mid", 'if (to == 2) return "Sealed";', 'if (to == 2) return "Tank";'),
    ("Scrap rank is mid", 'return tier == "Scrap" ? 0 : tier == "Sealed" ? 2 : 1;', 'return tier == "Sealed" ? 2 : 1;'),
    ("nothing-inside keeps the rare roll", "if (weatheringNoLoot) { f.noLoot = true; f.rareChance = 0f; }", "if (weatheringNoLoot) { f.noLoot = true; }"),
    ("nothing-inside is not remembered", "if (weatheringNoLoot) { f.noLoot = true; f.rareChance = 0f; }", "if (weatheringNoLoot) { f.rareChance = 0f; }"),
    ("Scrap keeps the rare roll", 'if (f.tier == "Scrap") f.rareChance = 0f;', ""),
    ("shift 0 still renames", "if (totalShift != 0)", "if (true)"),
    ("yield unclamped above", "return v < 0f ? 0f : v > 1f ? 1f : v;\n        }\n\n        /// <summary>Chance of the rare roll", "return v < 0f ? 0f : v;\n        }\n\n        /// <summary>Chance of the rare roll"),
    ("yield ignores the factor", "float v = familyFraction * yieldFactor;", "float v = familyFraction;"),
    ("skill factor at zero 0.5", "SkillFactorAtZero = 0.25f", "SkillFactorAtZero = 0.5f"),
    ("skill factor at max 3", "SkillFactorAtMax = 2f", "SkillFactorAtMax = 3f"),
    ("skill ignores the setting", "if (skillScales && hasSkills)", "if (hasSkills)"),
    ("skill unbounded past 20", "t = t < 0f ? 0f : t > 1f ? 1f : t;", ""),
    ("rare chance not capped", "return c < 0f ? 0f : c > 1f ? 1f : c;", "return c < 0f ? 0f : c;"),
    ("max skill 15", "public const int MaxSkill = 20;", "public const int MaxSkill = 15;"),
    ("stack scaled when unstackable", "if (stackLimit > 1 && Math.Abs(generosity - 1f) >= 1e-6f)", "if (Math.Abs(generosity - 1f) >= 1e-6f)"),
    ("stack can reach zero", "return n < 1 ? 1 : n > stackLimit ? stackLimit : n;", "return n > stackLimit ? stackLimit : n;"),
    ("stack passes the limit", "return n < 1 ? 1 : n > stackLimit ? stackLimit : n;", "return n < 1 ? 1 : n;"),
    ("stack rounds up", "int n = (int)Math.Round(stack * generosity);", "int n = (int)Math.Ceiling(stack * generosity);"),
    ("hazard ignores resistance", "if (toxic) severity *= Math.Max(0f, 1f - toxicResistance);", ""),
    ("hazard resistance can heal", "if (toxic) severity *= Math.Max(0f, 1f - toxicResistance);", "if (toxic) severity *= 1f - toxicResistance;"),
    ("disabled test is a substring", "disabledCsv.Split(',').Any(k => k.Trim() == key)", "disabledCsv.Contains(key)"),
    ("disabled list not trimmed", "disabledCsv.Split(',').Any(k => k.Trim() == key)", "disabledCsv.Split(',').Any(k => k == key)"),
    ("enabling does not remove the key", "Where(k => k.Length > 0 && k != key)", "Where(k => k.Length > 0)"),
    ("empty keys kept", "Where(k => k.Length > 0 && k != key)", "Where(k => k != key)"),
    ("field active ignores the master switch", "return wreckFields && !string.IsNullOrEmpty(key)", "return !string.IsNullOrEmpty(key)"),
    ("field active ignores the gate", "&& !FieldDisabled(disabledCsv, key) && gateEnabled;", "&& !FieldDisabled(disabledCsv, key);"),
    ("negative density places wrecks", "Math.Round(count * Math.Max(0f, density) * placementFactor)", "Math.Round(Math.Abs(count * density) * placementFactor)"),
    ("fixed count ignores the factor", "Math.Round(count * Math.Max(0f, density) * placementFactor)", "Math.Round(count * Math.Max(0f, density))"),
    ("per-10k ignores density", "return rangeSample * Math.Max(0f, density);", "return rangeSample;"),
    ("cluster chance 0 means unset", "return ownChance >= 0f ? ownChance : densityClassChance;", "return ownChance > 0f ? ownChance : densityClassChance;"),
    ("own cluster size at 1", "return ownMax >= 2;", "return ownMax >= 1;"),
    ("four misses allowed", "public const int MaxMisses = 3;", "public const int MaxMisses = 4;"),
    ("two misses allowed", "public const int MaxMisses = 3;", "public const int MaxMisses = 2;"),
    ("placement never stops short", "if (!tryAnchor()) { misses++; continue; }", "if (!tryAnchor()) { continue; }"),
    ("a miss counts as placed", "if (!tryAnchor()) { misses++; continue; }\n                placed++;", "if (!tryAnchor()) { misses++; }\n                placed++;"),
    ("cluster overshoots", "for (int i = 0; i < extra && placed < total; i++)", "for (int i = 0; i < extra; i++)"),
    ("cluster size counts the anchor twice", "int extra = clusterSize() - 1;", "int extra = clusterSize();"),
    ("cluster rolled at the last slot", "if (placed < total && rollCluster())", "if (rollCluster())"),
    ("cluster failure counts placed", "if (tryClusterMember()) placed++;", "{ tryClusterMember(); placed++; }"),
    ("map allowed with no map", "if (!hasMap) return false;", ""),
    ("required mutators ignored", "return anyRequiredPresent;", "return true;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_wreckage_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
