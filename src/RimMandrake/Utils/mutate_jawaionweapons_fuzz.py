#!/usr/bin/env python3
"""Mutation proof for the JawaIonWeapons fuzz: plants each defect in the kernel (RSW_IonBuildupKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_jawaionweapons_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimStarWars/JawaIonWeapons/Source/Kernel/RSW_IonBuildupKernel.cs"
MUTATIONS = [
    ("size: zero size divides", "if (bodySize <= 0f) return 1f;\n            if (exponent <= 0f) return 1f;", "if (exponent <= 0f) return 1f;"),
    ("size: zero exponent scales", "if (bodySize <= 0f) return 1f;\n            if (exponent <= 0f) return 1f;", "if (bodySize <= 0f) return 1f;"),
    ("size: exponent multiplies", "return (float)Math.Pow(bodySize, exponent);", "return bodySize * exponent;"),
    ("size: exponent off by one", "return (float)Math.Pow(bodySize, exponent);", "return (float)Math.Pow(bodySize, exponent + 1f);"),
    ("size: square is a cube", "if (exponent == 2f) return bodySize * bodySize;", "if (exponent == 2f) return bodySize * bodySize * bodySize;"),
    ("stat: ignores the setting", "if (!thirdPartyScaling) return val;", ""),
    ("stat: acts on non-pawns", "if (isPawn && bodySize > 0f)", "if (bodySize > 0f)"),
    ("stat: acts at zero size", "if (isPawn && bodySize > 0f)", "if (isPawn)"),
    ("stat: forgets the engine's own 1/size", "Math.Pow(bodySize, exponent - 1f)", "Math.Pow(bodySize, exponent)"),
    ("stat: returns the scale not its inverse", "if (scaled > 0f) return 1f / scaled;", "if (scaled > 0f) return scaled;"),
    ("flesh: applies with the setting off", "if (!enabled) return false;\n            if (!isPawn || dead || !hasHealth) return false;", "if (!isPawn || dead || !hasHealth) return false;"),
    ("flesh: applies to the dead", "if (!isPawn || dead || !hasHealth) return false;", "if (!isPawn || !hasHealth) return false;"),
    ("flesh: applies to non-pawns", "if (!isPawn || dead || !hasHealth) return false;", "if (dead || !hasHealth) return false;"),
    ("flesh: applies without health", "if (!isPawn || dead || !hasHealth) return false;", "if (!isPawn || dead) return false;"),
    ("flesh: applies to mechanoids", "if (!hasRaceProps || mechanoid) return false;", "if (!hasRaceProps) return false;"),
    ("flesh: skips every non-flesh", "if (!hasRaceProps || mechanoid) return false;", "if (!hasRaceProps || mechanoid || !hasRaceProps) return false;\n            if (!hasHealth) return false;\n            if (mechanoid) return false;\n            if (!enabled) return false;\n            if (dead) return false;\n            return false;"),
    ("flesh: applies with no entries", "return hasEntries;", "return true;"),
    ("flesh: fixed severity never wins", "float severity = severityFixed > 0f ? severityFixed : severityPerDamageDealt * damageAmount;", "float severity = severityPerDamageDealt * damageAmount;"),
    ("flesh: per-damage never used", "float severity = severityFixed > 0f ? severityFixed : severityPerDamageDealt * damageAmount;", "float severity = severityFixed;"),
    ("flesh: fixed wins at zero", "float severity = severityFixed > 0f ? severityFixed", "float severity = severityFixed >= 0f ? severityFixed"),
    ("flesh: strength ignored", "severity *= strength;", ""),
    ("flesh: divisor ignored", "severity /= divisor;", ""),
    ("flesh: divisor multiplies", "severity /= divisor;", "severity *= divisor;"),
    ("machine: applies with the setting off", "if (!enabled) return 0f;\n            if (!pawnLiveSpawned || !hasRaceProps) return 0f;", "if (!pawnLiveSpawned || !hasRaceProps) return 0f;"),
    ("machine: applies to the dead or unspawned", "if (!pawnLiveSpawned || !hasRaceProps) return 0f;", "if (!hasRaceProps) return 0f;"),
    ("machine: applies without race props", "if (!pawnLiveSpawned || !hasRaceProps) return 0f;", "if (!pawnLiveSpawned) return 0f;"),
    ("machine: flesh is stunned", "if (isFlesh) return 0f;", ""),
    ("machine: any damage def", "if (!isIonDef) return 0f;", ""),
    ("machine: tiers swapped", "float amount = machine ? empAmountMachine : empAmountDroid;", "float amount = machine ? empAmountDroid : empAmountMachine;"),
    ("machine: all machines get the droid amount", "float amount = machine ? empAmountMachine : empAmountDroid;", "float amount = empAmountDroid;"),
    ("machine: slider ignored", "amount *= tierMultiplier;", ""),
    ("machine: size barrier ignored", "amount /= divisor;", ""),
    ("shield: breaks with the setting off", "return enabled && isPawn && !dead && spawned;", "return isPawn && !dead && spawned;"),
    ("shield: breaks a corpse", "return enabled && isPawn && !dead && spawned;", "return enabled && isPawn && spawned;"),
    ("shield: breaks the unspawned", "return enabled && isPawn && !dead && spawned;", "return enabled && isPawn && !dead;"),
    ("shield: breaks non-pawns", "return enabled && isPawn && !dead && spawned;", "return enabled && !dead && spawned;"),
    ("vehicle: stuns unabsorbed hits", "if (!absorbed || !enabled || !isIonDef) return 0;", "if (!enabled || !isIonDef) return 0;"),
    ("vehicle: ignores the setting", "if (!absorbed || !enabled || !isIonDef) return 0;", "if (!absorbed || !isIonDef) return 0;"),
    ("vehicle: any damage def", "if (!absorbed || !enabled || !isIonDef) return 0;", "if (!absorbed || !enabled) return 0;"),
    ("vehicle: no handler check", "if (!hasHandlers || !hasStunner) return 0;", "if (!hasStunner) return 0;"),
    ("vehicle: no stunner check", "if (!hasHandlers || !hasStunner) return 0;", "if (!hasHandlers) return 0;"),
    ("vehicle: footprint ignored", "float area = Math.Max(1, sizeX * sizeZ);", "float area = 1;"),
    ("vehicle: footprint is a perimeter", "float area = Math.Max(1, sizeX * sizeZ);", "float area = Math.Max(1, sizeX + sizeZ);"),
    ("vehicle: zero footprint divides", "float area = Math.Max(1, sizeX * sizeZ);", "float area = sizeX * sizeZ;"),
    ("vehicle: slider ignored", "amount *= tierMultiplier;\n            if (amount <= 0f) return 0;", "if (amount <= 0f) return 0;"),
    ("vehicle: ticks per point", "public const float StunTicksPerEmpPoint = 30f;", "public const float StunTicksPerEmpPoint = 20f;"),
    ("vehicle: truncates not rounds", "int ticks = (int)Math.Round(amount * StunTicksPerEmpPoint);", "int ticks = (int)(amount * StunTicksPerEmpPoint) + 3;"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(run_mutations(KERNEL, "selftest_jawaionweapons_fuzz.py", MUTATIONS, only))
