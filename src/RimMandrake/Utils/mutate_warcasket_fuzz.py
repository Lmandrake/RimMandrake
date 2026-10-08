#!/usr/bin/env python3
"""Mutation proof for the Warcasket fuzz: plants each defect in the kernel (RM_WarcasketKernel.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_warcasket_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/Warcasket/Source/Kernel/RM_WarcasketKernel.cs"
MUTATIONS = [
    ("failure needs only one switch", "public static bool FailureActive(bool master, bool compound) { return master && compound; }", "public static bool FailureActive(bool master, bool compound) { return master || compound; }"),
    ("vacuum edge inclusive", "return roomVacuum > threshold;", "return roomVacuum >= threshold;"),
    ("cold edge exclusive", "return ambient <= coldThreshold || ambient >= heatThreshold;", "return ambient < coldThreshold || ambient >= heatThreshold;"),
    ("heat edge exclusive", "return ambient <= coldThreshold || ambient >= heatThreshold;", "return ambient <= coldThreshold || ambient > heatThreshold;"),
    ("toxin needs ground and fallout", "return toxicGround || toxicFallout;", "return toxicGround && toxicFallout;"),
    ("temperature not counted", "if (temperature) n++;", ""),
    ("one hazard can fail the suit", "return hazards >= 2; }", "return hazards >= 1; }"),
    ("two hazards cannot fail the suit", "return hazards >= 2; }", "return hazards > 2; }"),
    ("extra hazard step off by one", "perExtraHazard * (hazards - 2)", "perExtraHazard * (hazards - 1)"),
    ("damaged suit fails less often", "chance *= Lerp(DamagedFailureFactor, 1f, hpFrac);", "chance *= Lerp(1f, DamagedFailureFactor, hpFrac);"),
    ("chance not clamped", "return Clamp01(chance);", "return chance;"),
    ("no max hit points divides by zero", "int maxHp = maxHitPoints > 0 ? maxHitPoints : 1;", "int maxHp = maxHitPoints;"),
    ("a failure can destroy the suit", "return Math.Max(1, hitPoints - dmg);", "return hitPoints - dmg;"),
    ("failure damage range too wide", "public static int FailureDamageMax(int hazards) { return hazards * 4; }", "public static int FailureDamageMax(int hazards) { return hazards * 6; }"),
    ("breach ignores the hazard count", "return perFailure * hazards;", "return perFailure;"),
    ("immersion gain too fast", "GainPerCheckUnprotected = 0.12f;", "GainPerCheckUnprotected = 0.2f;"),
    ("clear ground heals too slowly", "HealPerCheckClear = -0.35f;", "HealPerCheckClear = -0.1f;"),
    ("no drive floor", "MinDriveFactor = 0.05f;", "MinDriveFactor = 0f;"),
    ("immersion check one tick late", "if (--ticksUntilCheck > 0) return false;", "if (--ticksUntilCheck >= 0) return false;"),
    ("walkable water is hazardous", "return !affordancesKnown || !walkable;", "return true;"),
    ("out of bounds is hazardous", "if (!inBounds) return false;\n            if (!terrainKnown", "if (!terrainKnown"),
    ("protected pawn never heals", "if (driveFactor <= 0f) return hasHediff ? HealPerCheckProtected : 0f;", "if (driveFactor <= 0f) return 0f;"),
    ("clear ground heals nothing present", "if (!hazardous) return hasHediff ? HealPerCheckClear : 0f;", "if (!hazardous) return HealPerCheckClear;"),
    ("core doses every rare tick but the fourth", "if (++rareCount < RaresPerDose) return false;", "if (++rareCount <= RaresPerDose) return false;"),
    ("core cadence five", "public const int RaresPerDose = 4;", "public const int RaresPerDose = 5;"),
    ("rate scale forgets the cadence", "return (float)(tickRareInterval * RaresPerDose) / checkInterval;", "return (float)tickRareInterval / checkInterval;"),
    ("radius edge exclusive", "return !(distance > radius);", "return distance < radius;"),
    ("falloff reaches zero at the radius", "return 1f - distance / (radius + 1f);", "return 1f - distance / radius;"),
    ("dose ignores the toxic factor", "return toxicFactor * falloff * rateScale;", "return falloff * rateScale;"),
    ("bay shields nothing", "return bayOnCell;\n        }\n\n        // ───────────── sarcophagus", "return true;\n        }\n\n        // ───────────── sarcophagus"),
    ("unspawned thing is shielded", "if (!hasMap || !spawned) return false;", "if (!hasMap) return false;"),
    ("bay holds the clock with no field", "return shieldingActive && spawned && fieldFound;", "return shieldingActive && spawned;"),
    ("every suit seals", "return master && sarcophagi && isSarcophagusSuit;", "return master && sarcophagi;"),
    ("crack offered on the living", "return master && sarcophagi && isCorpse && hasSuit;", "return master && sarcophagi && hasSuit;"),
    ("crack offered with the setting off", "return master && sarcophagi && isCorpse && hasSuit;", "return master && isCorpse && hasSuit;"),
    ("salvage stack limit unguarded", "return Math.Min(left, Math.Max(1, stackLimit));", "return Math.Min(left, stackLimit);"),
    ("salvage ignores the stack limit", "return Math.Min(left, Math.Max(1, stackLimit));", "return left;"),
    ("empty salvage row wanted", "return defKnown && count > 0;", "return defKnown && count >= 0;"),
    ("crack ticks default", "return hasTicks ? ticks : 1200;", "return hasTicks ? ticks : 600;"),
    ("chance of one can fail", "if (p >= 1f) return true;", "if (p > 1f) return true;"),
    ("extension applies unsealed", "return hasExtension && isSealed;", "return hasExtension;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_warcasket_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
