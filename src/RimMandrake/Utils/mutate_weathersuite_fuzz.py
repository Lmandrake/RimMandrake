#!/usr/bin/env python3
"""Mutation proof for the WeatherSuite fuzz: plants each defect in the kernel (RM_WeatherKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_weathersuite_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

# Equivalent mutant (not listed): dropping the clamp before acos - the sum is computed in double and cast to float, which absorbs the 1e-16 overshoot.
KERNEL = "src/RimMandrake/WeatherSuite/Source/Kernel/RM_WeatherKernel.cs"
MUTATIONS = [
    ("arc: sin/cos swapped", "Math.Sin(lat0) * Math.Sin(lat) + Math.Cos(lat0) * Math.Cos(lat) * Math.Cos(lon - lon0)", "Math.Sin(lat0) * Math.Cos(lat) + Math.Cos(lat0) * Math.Sin(lat) * Math.Cos(lon - lon0)"),
    ("arc: longitude difference dropped", "Math.Cos(lon - lon0)", "1.0"),
    ("arc: radians constant wrong", "Deg2Rad = 0.0174532924f", "Deg2Rad = 0.0175f"),
    ("arc: returns radians", "return (float)Math.Acos(cosArc) * Rad2Deg;", "return (float)Math.Acos(cosArc);"),
    ("arc: ignores the substellar longitude", "Math.Cos(lon - lon0)", "Math.Cos(lon)"),
    ("wall: inner edge exclusive", "return arc >= min && arc <= max;", "return arc > min && arc <= max;"),
    ("wall: outer edge exclusive", "return arc >= min && arc <= max;", "return arc >= min && arc < max;"),
    ("dark: edge inclusive (the 2026-09-02 overlap)", "return arc > nightsideMin;", "return arc >= nightsideMin;"),
    ("dark: swallows the wall", "return arc > nightsideMin;", "return arc > nightsideMin - 60f;"),
    ("sentinel in the dark", "public const float NoArc = -1f;", "public const float NoArc = 150f;"),
    ("tint: no cap at white", "return v > 1f ? 1f : v;", "return v;"),
    ("tint: no vanilla floor", "if (v < floor) v = floor;", ""),
    ("tint: saturation inverted", "float v = (1f + (channel - 1f) * saturation) * brightness;", "float v = (1f + (channel - 1f) * (1f - saturation)) * brightness;"),
    ("tint: brightness ignored", "float v = (1f + (channel - 1f) * saturation) * brightness;", "float v = (1f + (channel - 1f) * saturation);"),
    ("tint: vanilla brightness 0.9", "VanillaBrightness = 0.73f", "VanillaBrightness = 0.9f"),
    ("forecast: share over the shown only", "total > 0f ? weights[idx[i]] / total * 100f : 0f", "100f / Math.Max(1, Math.Min(n, idx.Count))"),
    ("forecast: ascending", "int c = weights[b].CompareTo(weights[a]);", "int c = weights[a].CompareTo(weights[b]);"),
    ("forecast: ties by reverse index", "return c != 0 ? c : a.CompareTo(b);", "return c != 0 ? c : b.CompareTo(a);"),
    ("forecast: keeps zero weights", "if (weights[i] > 0f) { idx.Add(i); total += weights[i]; }", "{ idx.Add(i); total += weights[i]; }"),
    ("forecast: total misses a weight", "total += weights[i]; } }", "} }"),
    ("forecast: one too many rows", "Math.Min(n, idx.Count)", "Math.Min(n + 1, idx.Count)"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_weathersuite_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
