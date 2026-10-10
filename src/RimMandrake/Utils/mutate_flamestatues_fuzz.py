#!/usr/bin/env python3
"""Mutation proof for the FlameStatues fuzz: plants each defect in the production kernel, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations).

    python3 src/RimMandrake/Utils/mutate_flamestatues_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

MUTATIONS = [
    ("Abs of int.MinValue indexes negative (the original frame pick)", "return (int)((uint)v & 0x7FFFFFFF) % frameCount;", "return (v < 0 ? -v : v) % frameCount;"),
    ("frame pick ignores the point", "int step = animTicks / 15 + pointIndex * 7;\n            int v = step ^ (thingId * 391 + pointIndex * 131);", "int step = animTicks / 15;\n            int v = step ^ (thingId * 391);"),
    ("frame pick off the end", "% frameCount;\n        }\n\n        /// <summary>Which radial", "% (frameCount + 1);\n        }\n\n        /// <summary>Which radial"),
    ("anim ticks precedence (xor binds after and)", "ticksGame + ((thingId ^ 0x80FD52) & 0x7FFFFFFF)", "ticksGame + (thingId ^ 0x80FD52 & 0x7FFFFFFF)"),
    ("quality table: Legendary half", "{ 0.5f, 0.7f, 1f, 1.2f, 1.4f, 1.7f, 2f }", "{ 0.5f, 0.7f, 1f, 1.2f, 1.4f, 1.7f, 1f }"),
    ("quality table: not monotone", "{ 0.5f, 0.7f, 1f, 1.2f, 1.4f, 1.7f, 2f }", "{ 0.5f, 0.7f, 1f, 1.2f, 1.7f, 1.4f, 2f }"),
    ("quality ignores the setting", "if (!compScalingEnabled || !settingEnabled || quality < 0) return 1f;", "if (!compScalingEnabled || quality < 0) return 1f;"),
    ("unknown quality indexes the table", "if (quality >= QualityScales.Length) return 1f;", ""),
    ("burning ignores the fuel setting", "return !hasRefuelable || hasFuel || !consumeFuelSetting;", "return !hasRefuelable || hasFuel;"),
    ("burning: dry tank without a comp", "return !hasRefuelable || hasFuel || !consumeFuelSetting;", "return hasFuel || !consumeFuelSetting;"),
    ("glow ignores the flames setting", "return glowSetting && flamePointsSetting && burning;", "return glowSetting && burning;"),
    ("flames shown while dark", "return burning && flamePointsSetting;", "return flamePointsSetting;"),
    ("fleck floor removed", "return Math.Max(MinFleckInterval, (int)Math.Round(baseInterval / qualityScale));", "return (int)Math.Round(baseInterval / qualityScale);"),
    ("better statue throws flecks less often", "baseInterval / qualityScale", "baseInterval * qualityScale"),
    ("fleck interval 0 still fires", "if (interval <= 0) return false;", ""),
    ("point phase dropped", "(long)pointIndex * PointPhase", "0"),
    ("fleck base 0 not silent", "if (baseInterval <= 0) return 0;", ""),
    ("multiplier clamp low edge", "Math.Min(Math.Max(m, MinFuelMultiplier), MaxFuelMultiplier)", "Math.Min(Math.Max(m, 0f), MaxFuelMultiplier)"),
    ("multiplier clamp high edge", "Math.Min(Math.Max(m, MinFuelMultiplier), MaxFuelMultiplier)", "Math.Min(Math.Max(m, MinFuelMultiplier), 40f)"),
    ("rate not scaled", "return Math.Abs(m - 1f) < 1e-6f ? rate : rate * m;", "return rate;"),
    ("scaled by the raw multiplier", "float m = ClampFuelMultiplier(multiplier);\n            return", "float m = multiplier;\n            return"),
    ("refill while consuming", "if (consumeFuelSetting || !hasRefuelable || !pollTick) return 0f;", "if (!hasRefuelable || !pollTick) return 0f;"),
    ("refill off the poll tick", "if (consumeFuelSetting || !hasRefuelable || !pollTick) return 0f;", "if (consumeFuelSetting || !hasRefuelable) return 0f;"),
    ("pipe refund ignores the link setting", "if (!linkSetting || !pipeReceiving ||", "if (!pipeReceiving ||"),
    ("pipe refund while unpiped", "if (!linkSetting || !pipeReceiving ||", "if (!linkSetting ||"),
    ("pipe refund off the poll tick", "|| !consumeFuelSetting || !pollTick) return 0f;", "|| !consumeFuelSetting) return 0f;"),
    ("pipe refund ignores the fuel setting", "|| !consumeFuelSetting || !pollTick) return 0f;", "|| !pollTick) return 0f;"),
    ("pipe refunds a rise", "return fuel < lastFuel ? lastFuel - fuel : 0f;", "return Math.Abs(lastFuel - fuel);"),
    ("refill overfills", "return fuel < capacity ? capacity - fuel : 0f;", "return fuel < capacity ? capacity : 0f;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/FlameStatues/Source/Kernel/RM_FlameKernel.cs",
                           "selftest_flamestatues_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
