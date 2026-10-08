#!/usr/bin/env python3
"""Mutation proof for the OasisMaker fuzz: plants each defect in the kernel (RM_OasisKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_oasismaker_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/OasisMaker/Source/Kernel/RM_OasisKernel.cs"
MUTATIONS = [
    ("clamp01 lets values above 1 through", "return v < 0f ? 0f : (v > 1f ? 1f : v);", "return v < 0f ? 0f : v;"),
    ("lerp unclamped", "return a + (b - a) * Clamp01(t);", "return a + (b - a) * t;"),
    ("inverse lerp unclamped", "return a != b ? Clamp01((value - a) / (b - a)) : 0f;", "return a != b ? (value - a) / (b - a) : 0f;"),
    ("inverse lerp equal ends divide", "return a != b ? Clamp01((value - a) / (b - a)) : 0f;", "return Clamp01((value - a) / (b - a));"),
    ("out of bounds shades", "if (!g.InBounds(x, z)) return 0f;\n            if (g.Roofed(x, z)) return 1f;", "if (g.Roofed(x, z)) return 1f;"),
    ("roof is only partial shade", "if (g.Roofed(x, z)) return 1f;", "if (g.Roofed(x, z)) return 0.4f;"),
    ("roof ignored", "if (g.Roofed(x, z)) return 1f;", ""),
    ("shade search covers the cell itself", "if (dx == 0 && dz == 0) continue;\n                    int nx", "int nx"),
    ("shade ignores bounds of the neighbour", "if (!g.InBounds(nx, nz) || !g.CastsShade(nx, nz)) continue;", "if (!g.CastsShade(nx, nz)) continue;"),
    ("shade ignores casters", "if (!g.InBounds(nx, nz) || !g.CastsShade(nx, nz)) continue;", "if (!g.InBounds(nx, nz)) continue;"),
    ("shade falloff linear in squared distance", "float dist = (float)Math.Sqrt(dx * dx + dz * dz);", "float dist = (float)(dx * dx + dz * dz);"),
    ("shade falloff radius 1", "1f - dist / (ShadeSearchRadius + 1)", "1f - dist / ShadeSearchRadius"),
    ("shade keeps the worst", "if (score > best) best = score;", "if (score < best || best == 0f) best = score;"),
    ("shade search radius 1", "ShadeSearchRadius = 2", "ShadeSearchRadius = 1"),
    ("shade threshold 0.6", "ShadeThreshold = 0.5f", "ShadeThreshold = 0.6f"),
    ("shade threshold 0.3", "ShadeThreshold = 0.5f", "ShadeThreshold = 0.3f"),
    ("score counts out-of-bounds cells", "if (!g.InBounds(x, z)) continue;\n                    if (ShadeAt(g, x, z)", "if (ShadeAt(g, x, z)"),
    ("score swaps rock into shade", "if (g.IsRock(x, z)) rock++;", "if (g.IsRock(x, z)) shade++;"),
    ("score radius off by one", "for (int dz = -radius; dz <= radius; dz++)\n            {\n                for (int dx = -radius; dx <= radius; dx++)\n                {\n                    int x = cx + dx", "for (int dz = -radius; dz < radius; dz++)\n            {\n                for (int dx = -radius; dx <= radius; dx++)\n                {\n                    int x = cx + dx"),
    ("floor exclusive on shade", "return shade >= shadeFloor && rock >= rockFloor;", "return shade > shadeFloor && rock >= rockFloor;"),
    ("floor exclusive on rock", "return shade >= shadeFloor && rock >= rockFloor;", "return shade >= shadeFloor && rock > rockFloor;"),
    ("floor either axis is enough", "return shade >= shadeFloor && rock >= rockFloor;", "return shade >= shadeFloor || rock >= rockFloor;"),
    ("quality takes the better axis", "return Clamp01((shadeQ + rockQ) / 2f);", "return Clamp01(Math.Max(shadeQ, rockQ));"),
    ("quality sums the axes", "return Clamp01((shadeQ + rockQ) / 2f);", "return Clamp01(shadeQ + rockQ);"),
    ("quality swaps the floors", "InverseLerp(shadeFloor, shadeExcellent, shade)", "InverseLerp(rockFloor, rockExcellent, shade)"),
    ("radius cap rounds up", "return (int)Math.Round(Lerp(minCap, maxCap, quality));", "return (int)Math.Ceiling(Lerp(minCap, maxCap, quality));"),
    ("radius cap rounds down", "return (int)Math.Round(Lerp(minCap, maxCap, quality));", "return (int)Math.Floor(Lerp(minCap, maxCap, quality));"),
    ("radius cap ignores quality", "return (int)Math.Round(Lerp(minCap, maxCap, quality));", "return maxCap;"),
    ("radius cap away from zero", "(int)Math.Round(Lerp(minCap, maxCap, quality))", "(int)Math.Round(Lerp(minCap, maxCap, quality), MidpointRounding.AwayFromZero)"),
    ("speed range 1..2", "return Lerp(0.5f, 1.5f, quality);", "return Lerp(1f, 2f, quality);"),
    ("speed ignores quality", "return Lerp(0.5f, 1.5f, quality);", "return 1f;"),
    ("verdict blocks a disabled mechanic", "if (!masterEnabled) return RM_OasisPlacement.Allowed;", ""),
    ("verdict never allows", "if (MeetsFloor(shade, rock, shadeFloor, rockFloor)) return RM_OasisPlacement.Allowed;", ""),
    ("verdict swaps shade and rock", "return needsShade ? RM_OasisPlacement.NeedsShade : RM_OasisPlacement.NeedsRock;", "return needsShade ? RM_OasisPlacement.NeedsRock : RM_OasisPlacement.NeedsShade;"),
    ("verdict never says both", "if (needsShade && needsRock) return RM_OasisPlacement.NeedsBoth;", ""),
    ("machine acts while the mechanic is off", "if (!masterEnabled || !spawned) return;", "if (!spawned) return;"),
    ("machine acts while unspawned", "if (!masterEnabled || !spawned) return;", "if (!masterEnabled) return;"),
    ("dormant starts attuning without a valid site", "case RM_OasisMakerState.Dormant:\n                    if (validNow())", "case RM_OasisMakerState.Dormant:\n                    if (true)"),
    ("attuning keeps counting on an invalid site", "if (!validNow())\n                    {\n                        state = RM_OasisMakerState.Dormant;\n                        ticksInState = 0;\n                        break;\n                    }\n                    ticksInState += RareTickInterval;", "ticksInState += RareTickInterval;"),
    ("attuning one day short", "if (ticksInState >= attuningDays * ticksPerDay)", "if (ticksInState >= (attuningDays - 1) * ticksPerDay)"),
    ("attuning exclusive", "if (ticksInState >= attuningDays * ticksPerDay)", "if (ticksInState > attuningDays * ticksPerDay)"),
    ("attuning count per half tick", "ticksInState += RareTickInterval;", "ticksInState += RareTickInterval / 2;"),
    ("quality locks on every attune", "if (!qualityLocked)\n                        {\n                            lockQuality();\n                            qualityLocked = true;\n                        }", "lockQuality();\n                        qualityLocked = true;"),
    ("quality never locks", "if (!qualityLocked)\n                        {\n                            lockQuality();\n                            qualityLocked = true;\n                        }", "qualityLocked = true;"),
    ("working does not go dormant when invalid", "case RM_OasisMakerState.Working:\n                    if (!validNow())\n                    {\n                        state = RM_OasisMakerState.Dormant;\n                        ticksInState = 0;\n                        break;\n                    }", "case RM_OasisMakerState.Working:\n                    if (!validNow())\n                    {\n                        break;\n                    }"),
    ("working grows past the cap", "if (currentRing >= lockedRadiusCap) return;\n                    grow = true;", "grow = true;"),
    ("working never grows", "if (currentRing >= lockedRadiusCap) return;\n                    grow = true;", "if (currentRing >= lockedRadiusCap) return;"),
    ("working checks validity twice", "case RM_OasisMakerState.Working:\n                    if (!validNow())", "case RM_OasisMakerState.Working:\n                    validNow();\n                    if (!validNow())"),
    ("pool zone is distance 0 only", "lo = ring == 0 ? 0 : ring + 1;\n            hi = ring == 0 ? 1 : ring + 1;", "lo = ring == 0 ? 0 : ring + 1;\n            hi = ring == 0 ? 0 : ring + 1;"),
    ("margin ring starts at its own index", "lo = ring == 0 ? 0 : ring + 1;", "lo = ring == 0 ? 0 : ring;"),
    ("margin ring is two wide", "hi = ring == 0 ? 1 : ring + 1;", "hi = ring == 0 ? 1 : ring + 2;"),
    ("chebyshev becomes manhattan", "return Math.Max(Math.Abs(dx), Math.Abs(dz));", "return Math.Abs(dx) + Math.Abs(dz);"),
    ("ring duration ignores growth", "double days = baseRingDays * Math.Pow(growthFactor, ring);", "double days = baseRingDays;"),
    ("ring duration grows linearly", "Math.Pow(growthFactor, ring)", "(1 + (growthFactor - 1) * ring)"),
    ("ring duration in half days", "return (long)(days * ticksPerDay);", "return (long)(days * ticksPerDay / 2);"),
    ("per rung floor gone", "return Math.Max(1L, RingDurationTicks(ring, baseRingDays, growthFactor, ticksPerDay) / RungsForRing(ring));", "return RingDurationTicks(ring, baseRingDays, growthFactor, ticksPerDay) / RungsForRing(ring);"),
    ("per rung ignores the rung count", "/ RungsForRing(ring));", "/ 1);"),
    ("pool ladder skips marsh", '{ "Sand", "Gravel", "Soil", "Mud", "Marsh", "WaterShallow" }', '{ "Sand", "Gravel", "Soil", "Mud", "WaterShallow" }'),
    ("margin ladder ends at soil", '{ "Sand", "Gravel", "Soil", "SoilRich" }', '{ "Sand", "Gravel", "Soil" }'),
    ("margin ladder swaps gravel and soil", '{ "Sand", "Gravel", "Soil", "SoilRich" }', '{ "Sand", "Soil", "Gravel", "SoilRich" }'),
    ("softsand unfolded", 'string name = currentDefName == "SoftSand" ? "Sand" : currentDefName;', "string name = currentDefName;"),
    ("terminal terrain climbs", "return i >= ladder.Length - 1 ? null : ladder[i + 1];", "return ladder[(i + 1) % ladder.Length];"),
    ("ring 0 uses the margin ladder", "public static string[] LadderForRing(int ring) { return ring == 0 ? PoolLadder : MarginLadder; }", "public static string[] LadderForRing(int ring) { return MarginLadder; }"),
    ("progress ignores speed", "rungProgressTicks += (int)(deltaTicks * speedMultiplier);", "rungProgressTicks += deltaTicks;"),
    ("progress double speed", "rungProgressTicks += (int)(deltaTicks * speedMultiplier);", "rungProgressTicks += (int)(deltaTicks * speedMultiplier * 2f);"),
    ("growth rung cost not paid", "rungProgressTicks -= (int)PerRungTicks(currentRing, baseRingDays, growthFactor, ticksPerDay);", ""),
    ("growth climbs wrong ring", "climbRung(currentRing);", "climbRung(currentRing + 1);"),
    ("growth does not count climbs", "climbed++;\n                ringRungsClimbed++;", "climbed++;"),
    ("growth ring never advances", "currentRing++;\n                    ringRungsClimbed = 0;", "ringRungsClimbed = 0;"),
    ("growth ring advances one rung early", "if (ringRungsClimbed >= RungsForRing(currentRing))", "if (ringRungsClimbed >= RungsForRing(currentRing) - 1)"),
    ("growth keeps progress across rings", "ringRungsClimbed = 0;\n                    rungProgressTicks = 0;", "ringRungsClimbed = 0;"),
    ("growth ring never resets its rung count", "currentRing++;\n                    ringRungsClimbed = 0;\n                    rungProgressTicks = 0;", "currentRing++;\n                    rungProgressTicks = 0;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_oasismaker_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
