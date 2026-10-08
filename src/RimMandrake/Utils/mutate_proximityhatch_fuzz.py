#!/usr/bin/env python3
"""Mutation proof for the ProximityHatch fuzz: plants each defect in the kernel (RM_ProximityHatchKernel.cs), demands the fuzz FAILS,
restores the file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_proximityhatch_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/ProximityHatch/Source/Kernel/RM_ProximityHatchKernel.cs"
MUTATIONS = [
    ("interval floor gone", "return Math.Max(1, (int)Math.Round(baseTicks * multiplier));", "return (int)Math.Round(baseTicks * multiplier);"),
    ("interval rounds up", "(int)Math.Round(baseTicks * multiplier)", "(int)Math.Ceiling(baseTicks * multiplier)"),
    ("interval rounds down", "(int)Math.Round(baseTicks * multiplier)", "(int)Math.Floor(baseTicks * multiplier)"),
    ("interval ignores the multiplier", "(int)Math.Round(baseTicks * multiplier)", "(int)Math.Round(baseTicks * 1f)"),
    ("radius floor gone", "return Math.Max(MinRadius, baseRadius * multiplier);", "return baseRadius * multiplier;"),
    ("radius floor 0.5", "public const float MinRadius = 0.1f;", "public const float MinRadius = 0.5f;"),
    ("radius ignores the multiplier", "baseRadius * multiplier);", "baseRadius);"),
    ("countdown fires one tick late", "if (--ticksUntilScan > 0) return false;", "if (--ticksUntilScan >= 0) return false;"),
    ("countdown never re-arms", "ticksUntilScan = interval;\n            return true;", "return true;"),
    ("countdown re-arms one short", "ticksUntilScan = interval;\n            return true;", "ticksUntilScan = interval - 1;\n            return true;"),
    ("fired egg still ticks", "return !hatchFired && spawned;\n        }\n\n        /// <summary>Whether a scan", "return spawned;\n        }\n\n        /// <summary>Whether a scan"),
    ("scan ignores the master switch", "return !hatchFired && spawned && settingEnabled && hasHatcherComp && hasMap;", "return !hatchFired && spawned && hasHatcherComp && hasMap;"),
    ("scan ignores fired", "return !hatchFired && spawned && settingEnabled && hasHatcherComp && hasMap;", "return spawned && settingEnabled && hasHatcherComp && hasMap;"),
    ("scan ignores a missing hatcher", "return !hatchFired && spawned && settingEnabled && hasHatcherComp && hasMap;", "return !hatchFired && spawned && settingEnabled && hasMap;"),
    ("tie goes to the last", "if (distSq[i] < bestDist)", "if (distSq[i] <= bestDist)"),
    ("picks the farthest", "if (distSq[i] < bestDist)\n                {\n                    bestDist = distSq[i];", "if (distSq[i] > bestDist || best < 0)\n                {\n                    bestDist = distSq[i];"),
    ("distance 0 never picked", "if (distSq[i] < bestDist)", "if (distSq[i] > 0 && distSq[i] < bestDist)"),
    ("litter-mate taken for the hatchling", "return isPawn && kindMatches && !wasThereBefore;", "return isPawn && kindMatches;"),
    ("any pawn taken for the hatchling", "return isPawn && kindMatches && !wasThereBefore;", "return isPawn && !wasThereBefore;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_proximityhatch_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
