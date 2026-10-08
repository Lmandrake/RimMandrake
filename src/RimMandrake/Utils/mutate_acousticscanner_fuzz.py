#!/usr/bin/env python3
"""Mutation proof for the AcousticScanner fuzz: plants each defect in the production kernel, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations).

    python3 src/RimMandrake/Utils/mutate_acousticscanner_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

MUTATIONS = [
    ("band floor dropped", "return Math.Max(bandSize, MinBandSize);", "return bandSize;"),
    ("floor below 7", "public const int MinBandSize = 7;", "public const int MinBandSize = 3;"),
    ("edge band clipped, not slid (the original defect)", "int x0 = Math.Min(Math.Max(minX, 0), mapW - bw);\n                    int z0 = Math.Min(Math.Max(minZ, 0), mapH - bh);\n                    result.Add(new RM_KBand { targetIndex = t, tier = kv.Value, x = x0, z = z0, w = bw, h = bh });",
     "int x0 = Math.Max(minX, 0), z0 = Math.Max(minZ, 0);\n                    int cw = Math.Min(minX + b, mapW) - x0, ch = Math.Min(minZ + b, mapH) - z0;\n                    result.Add(new RM_KBand { targetIndex = t, tier = kv.Value, x = x0, z = z0, w = cw, h = ch });"),
    ("halo dropped", "if (!tiers.ContainsKey(nk)) tiers[nk] = RM_AcousticTier.Faint;", "if (false) tiers[nk] = RM_AcousticTier.Faint;"),
    ("halo only cardinal", "for (int dz = -1; dz <= 1; dz++)\n                        {", "for (int dz = -1; dz <= 1; dz++) if (dx == 0 || dz == 0)\n                        {"),
    ("FloorDiv truncates toward zero", "return a >= 0 ? a / b : -((-a + b - 1) / b);", "return a / b;"),
    ("origin ignored when placing the block", "int minX = KeyX(kv.Key) * b - ox;", "int minX = KeyX(kv.Key) * b;"),
    ("strong share raised", "public const float StrongShare = 0.6f;", "public const float StrongShare = 0.9f;"),
    ("moderate bound exclusive", "share >= ModerateShare ? RM_AcousticTier.Moderate", "share > ModerateShare ? RM_AcousticTier.Moderate"),
    ("lone hit may read Strong", "if (blocks.Count == 1 && hits.Count == 1) tier = RM_AcousticTier.Moderate;", ""),
    ("weight ignored", "blocks[key] = cur + w;", "blocks[key] = cur + 1f;"),
    ("empty-weight target not skipped", "if (max <= 0f) continue;", ""),
    ("block outside the map kept", "if (minX + b <= 0 || minZ + b <= 0 || minX >= mapW || minZ >= mapH) continue;", ""),
    ("gate: power checked before enabled", "            if (!enabled) return RM_PulseGate.Disabled;\n            if (!spawned) return RM_PulseGate.NotSpawned;\n            if (hasPowerComp && !powerOn) return RM_PulseGate.NoPower;",
     "            if (hasPowerComp && !powerOn) return RM_PulseGate.NoPower;\n            if (!enabled) return RM_PulseGate.Disabled;\n            if (!spawned) return RM_PulseGate.NotSpawned;"),
    ("gate: ship required ignored", "if (requireLandedShip && !onLandedShip)", "if (!onLandedShip)"),
    ("gate: cooldown off by one", "if (ticksUntilReady > 0) return RM_PulseGate.Cooldown;", "if (ticksUntilReady >= 0) return RM_PulseGate.Cooldown;"),
    ("ship: engine not needed", "if (gravEnginesOnMap <= 0) return false;", ""),
    ("ship: any cell enough", "if (!coveredCellIsSubstructure[i]) return false;", "if (coveredCellIsSubstructure[i]) return true;"),
    ("overlay may expire at once", "return now + Math.Max(1, durationTicks);", "return now + durationTicks;"),
    ("overlay still on at expiry", "now < expiresTick && bandCount > 0", "now <= expiresTick && bandCount > 0"),
    ("best tier takes the first", "bands[i].tier > best", "bands[i].tier < best"),
    ("cooldown truncates", "return (int)Math.Round(cooldownHours * TicksPerHour);", "return (int)(cooldownHours * TicksPerHour) - 1;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/AcousticScanner/Source/Kernel/RM_AcousticKernel.cs",
                           "selftest_acousticscanner_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
