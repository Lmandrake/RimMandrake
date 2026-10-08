#!/usr/bin/env python3
"""Mutation proof for the ShipVermin fuzz: plants each defect in the kernel (RM_VerminKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_shipvermin_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/ShipVermin/Source/Kernel/RM_VerminKernel.cs"
MUTATIONS = [
    ("rate floor gone", "float mult = Math.Max(MinRateMultiplier, rateMultiplier);", "float mult = rateMultiplier;"),
    ("floor of 0.1 instead of 0.01", "public const float MinRateMultiplier = 0.01f;", "public const float MinRateMultiplier = 0.1f;"),
    ("interval can reach zero", "return Math.Max(1, (int)Math.Round(days * TicksPerDay / mult, MidpointRounding.ToEven));", "return (int)Math.Round(days * TicksPerDay / mult, MidpointRounding.ToEven);"),
    ("rate multiplies instead of divides", "days * TicksPerDay / mult", "days * TicksPerDay * mult"),
    ("day length 24000", "public const int TicksPerDay = 60000;", "public const int TicksPerDay = 24000;"),
    ("burst rescheduled after a reload", "return !respawningAfterLoad && !burstDone && burstTick < 0 && burstMax > 0;", "return !burstDone && burstTick < 0 && burstMax > 0;"),
    ("burst rescheduled when done", "return !respawningAfterLoad && !burstDone && burstTick < 0 && burstMax > 0;", "return !respawningAfterLoad && burstTick < 0 && burstMax > 0;"),
    ("burst rescheduled over an existing one", "return !respawningAfterLoad && !burstDone && burstTick < 0 && burstMax > 0;", "return !respawningAfterLoad && !burstDone && burstMax > 0;"),
    ("burst scheduled with none configured", "return !respawningAfterLoad && !burstDone && burstTick < 0 && burstMax > 0;", "return !respawningAfterLoad && !burstDone && burstTick < 0;"),
    ("disabled nest still acts", "if (!spawned || !wreckSpawningEnabled) return step;", "if (!spawned) return step;"),
    ("despawned nest still acts", "if (!spawned || !wreckSpawningEnabled) return step;", "if (!wreckSpawningEnabled) return step;"),
    ("burst fires again once done", "step.Burst = !burstDone && burstTick >= 0 && now >= burstTick;", "step.Burst = burstTick >= 0 && now >= burstTick;"),
    ("burst fires before it is due", "step.Burst = !burstDone && burstTick >= 0 && now >= burstTick;", "step.Burst = !burstDone && burstTick >= 0;"),
    ("burst due test is exclusive", "now >= burstTick;", "now > burstTick;"),
    ("attempt due test is exclusive", "step.Attempt = now >= nextSpawnTick;", "step.Attempt = now > nextSpawnTick;"),
    ("attempt every tick", "step.Attempt = now >= nextSpawnTick;", "step.Attempt = true;"),
    ("missing population component caps", "if (hasPopulationComponent && currentPopulation >= hardCap) return Refusal.PopulationCap;", "if (currentPopulation >= hardCap) return Refusal.PopulationCap;"),
    ("cap is exclusive", "currentPopulation >= hardCap", "currentPopulation > hardCap"),
    ("cap checked before the map", "if (!hasMap) return Refusal.NoMap;\n            if (hasPopulationComponent && currentPopulation >= hardCap) return Refusal.PopulationCap;", "if (hasPopulationComponent && currentPopulation >= hardCap) return Refusal.PopulationCap;\n            if (!hasMap) return Refusal.NoMap;"),
    ("species checked after the cell", "if (!hasSpecies) return Refusal.NoSpecies;\n            if (!hasCell) return Refusal.NoCell;", "if (!hasCell) return Refusal.NoCell;\n            if (!hasSpecies) return Refusal.NoSpecies;"),
    ("roster ignores the swapped canon kind", "|| (slots[i].ResolvedName != null && slots[i].ResolvedName() == kind)", ""),
    ("roster ignores the free kind", "if (slots[i].Kind == kind ||", "if (false ||"),
    ("roster forbids names outside it", "            return true;\n        }\n\n        /// <summary>The weighted pool", "            return false;\n        }\n\n        /// <summary>The weighted pool"),
    ("roster ignores the checkbox", "return slots[i].Enabled;", "return true;"),
    ("pool keeps zero weights", "|| vw.Value <= 0f ||", "|| vw.Value < 0f ||"),
    ("pool ignores the roster", "|| !allows(vw.Key)) continue;", ") continue;"),
    ("pool keeps unresolved names", "if (r != null) pool.Add", "if (true) pool.Add"),
    ("pick ignores the weights", "double x = roll01 * total;", "double x = roll01 * weights.Count;"),
    ("pick off by one", "if (x < 0) return i;", "if (x <= 0) return i;"),
    ("pick can fall off the end", "return weights.Count - 1;\n        }\n\n        public enum Grant", "return weights.Count;\n        }\n\n        public enum Grant"),
    ("granted twice", "if (alreadyGranted || !settingOn) return Grant.Nothing;", "if (!settingOn) return Grant.Nothing;"),
    ("setting off still grants", "if (alreadyGranted || !settingOn) return Grant.Nothing;", "if (alreadyGranted) return Grant.Nothing;"),
    ("no ability def still grants", "if (abilityDefMissing) return Grant.MarkGrantedOnly;", ""),
    ("non-pawn granted", "if (!isPawn) return Grant.Nothing;", ""),
    ("aim at self moves", "if (px == ax && pz == az) return false;", ""),
    ("aim push-out ignores the range", "px + dx * range", "px + dx * 10f"),
    ("aim z uses x", "outZ = (int)Math.Round(pz + dz * range, MidpointRounding.ToEven);", "outZ = (int)Math.Round(pz + dx * range, MidpointRounding.ToEven);"),
    ("half angle uses the full width", "double half = lineWidthEnd / 2.0;", "double half = lineWidthEnd;"),
    ("half angle uses atan", "return Math.Asin(half / hyp) * 180.0 / Math.PI;", "return Math.Atan(half / hyp) * 180.0 / Math.PI;"),
    ("cone does not wrap through 180", "if (d > 180.0) d -= 360.0;\n            if (d < -180.0) d += 360.0;", ""),
    ("cone exclusive at its edge", "return Math.Abs(d) <= halfAngleDeg;", "return Math.Abs(d) < halfAngleDeg;"),
    ("cone one-sided", "return Math.Abs(d) <= halfAngleDeg;", "return d >= 0 && d <= halfAngleDeg;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_shipvermin_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
