#!/usr/bin/env python3
"""Mutation proof for the Visibility fuzz: plants each defect in the kernel (RM_VisibilityKernel.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught. The first entry is the ORIGINAL shipped behaviour (the point clamp altered a
raid even at factor 1, so "0x = no effect" was false for a raid outside the clamps): the fuzz must catch it.

    python3 src/RimMandrake/Utils/mutate_visibility_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/Visibility/Source/Kernel/RM_VisibilityKernel.cs"
MUTATIONS = [
    ("factor 1 still clamps (original)", "return Clamp(points * factor, lo, hi);", "return Clamp(points * factor, globalMin, PointsCap);"),
    ("band 20 inclusive", "if (v < 20f) return Hidden;", "if (v <= 20f) return Hidden;"),
    ("band 40 inclusive", "if (v < 40f) return Discreet;", "if (v <= 40f) return Discreet;"),
    ("band 60 moved", "if (v < 60f) return Noticed;", "if (v < 65f) return Noticed;"),
    ("band 80 inclusive", "if (v < 80f) return Marked;", "if (v <= 80f) return Marked;"),
    ("curve node 25 wrong", "CurveY = { 0.55f, 0.80f,", "CurveY = { 0.55f, 0.85f,"),
    ("curve top wrong", "1.25f, 1.60f };", "1.25f, 1.50f };"),
    ("curve not flat above 100", "return CurveY[CurveY.Length - 1];\n        }\n\n        /// <summary>The player's strength", "return CurveY[CurveY.Length - 1] + (visibility - 100f) * 0.01f;\n        }\n\n        /// <summary>The player's strength"),
    ("curve below 0 extrapolates", "if (visibility <= CurveX[0]) return CurveY[0];", "if (visibility <= CurveX[0]) return CurveY[0] + visibility * 0.01f;"),
    ("curve interpolation off", "float t = (visibility - CurveX[i - 1]) / (CurveX[i] - CurveX[i - 1]);", "float t = (visibility - CurveX[i - 1]) / (CurveX[i] - CurveX[i - 1]) * 0.9f;"),
    ("strength not centred on 1", "return 1f + (curveFactor - 1f) * strength;", "return curveFactor * strength;"),
    ("strength ignored", "return 1f + (curveFactor - 1f) * strength;", "return curveFactor;"),
    ("adjust unclamped above", "return Clamp(dial + delta, Min, Max);", "return Math.Max(Min, dial + delta);"),
    ("adjust unclamped below", "return Clamp(dial + delta, Min, Max);", "return Math.Min(Max, dial + delta);"),
    ("launch floor 0", "LaunchFloor = 5f", "LaunchFloor = 0f"),
    ("launch ceiling 20", "LaunchCeiling = 15f", "LaunchCeiling = 20f"),
    ("launch ignores multiplier", "return Clamp(dial * multiplier, LaunchFloor, LaunchCeiling);", "return Clamp(dial, LaunchFloor, LaunchCeiling);"),
    ("season is 14 days", "public const int TicksPerSeason = 900000;", "public const int TicksPerSeason = 840000;"),
    ("negative time grows memory", "return Math.Max(0f, ticksAway) / (float)TicksPerSeason;", "return ticksAway / (float)TicksPerSeason;"),
    ("memory thirds per season", "(float)Math.Pow(0.5f, SeasonsAway(ticksAway))", "(float)Math.Pow(0.66f, SeasonsAway(ticksAway))"),
    ("memory never decays", "return atDeparture * (float)Math.Pow(0.5f, SeasonsAway(ticksAway));", "return atDeparture;"),
    ("restore lowers the dial", "return decayed > dial ? decayed - dial : 0f;", "return decayed - dial;"),
    ("restore overshoots", "return decayed > dial ? decayed - dial : 0f;", "return decayed > dial ? decayed : 0f;"),
    ("cap 12000", "public const float PointsCap = 10000f;", "public const float PointsCap = 12000f;"),
    ("floor ignored", "float lo = Math.Min(points, globalMin);", "float lo = Math.Min(points, 0f);"),
    ("band width 25", "public const float BandWidth = 20f;", "public const float BandWidth = 25f;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_visibility_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
