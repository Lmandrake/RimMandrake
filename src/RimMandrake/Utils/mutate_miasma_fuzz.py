#!/usr/bin/env python3
"""Mutation proof for the Miasma fuzz: plants each defect in the kernel (RM_MiasmaKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_miasma_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/Miasma/Source/RM_MiasmaKernel.cs"
MUTATIONS = [
    ("lerp unclamped", "return a + (b - a) * Clamp01(t);", "return a + (b - a) * t;"),
    ("clamp01 lets 1+ through", "return v < 0f ? 0f : (v > 1f ? 1f : v);", "return v < 0f ? 0f : v;"),
    ("creche pick strict", "if (distSq[i] <= maxSq && distSq[i] < bestD) { best = i; bestD = distSq[i]; }", "if (distSq[i] < maxSq && distSq[i] < bestD) { best = i; bestD = distSq[i]; }"),
    ("creche pick takes the last of a tie", "if (distSq[i] <= maxSq && distSq[i] < bestD) { best = i; bestD = distSq[i]; }", "if (distSq[i] <= maxSq && distSq[i] <= bestD) { best = i; bestD = distSq[i]; }"),
    ("mother pick inclusive", "for (int i = 0; i < distSq.Count; i++)\n                if (distSq[i] < bestD) { best = i; bestD = distSq[i]; }", "for (int i = 0; i < distSq.Count; i++)\n                if (distSq[i] <= bestD) { best = i; bestD = distSq[i]; }"),
    ("predator pick takes the first", "if (distSq[i] <= bestD) { best = i; bestD = distSq[i]; }", "if (distSq[i] < bestD) { best = i; bestD = distSq[i]; }"),
    ("register allows duplicates", "if (y != null && !young.Contains(y)) young.Add(y);", "if (y != null) young.Add(y);"),
    ("register allows null", "if (y != null && !young.Contains(y)) young.Add(y);", "if (!young.Contains(y)) young.Add(y);"),
    ("betrayal leaves the heir", "successionDone = true;\n                heir = null;", "successionDone = true;"),
    ("betrayal keeps the record", "betrayed = true;\n                recordClean = false;", "betrayed = true;"),
    ("betrayal leaves succession open", "recordClean = false;\n                successionDone = true;\n                heir = null;", "recordClean = false;\n                heir = null;"),
    ("returned young stay owed", "returnedCount++;\n                young.Remove(y);", "returnedCount++;"),
    ("return not counted", "returnedCount++;\n                young.Remove(y);", "young.Remove(y);"),
    ("owed counts nulls", "if (young[i] != null && owed(young[i])) n++;", "if (owed(young[i])) n++;"),
    ("owed ignores the predicate", "if (young[i] != null && owed(young[i])) n++;", "if (young[i] != null) n++;"),
    ("poll ignores the setting", "return !successionDone && settingOn;", "return !successionDone;"),
    ("poll after succession", "return !successionDone && settingOn;", "return settingOn;"),
    ("promotion takes the last eligible", "chosen = young[i];\n                    break;", "chosen = young[i];"),
    ("promotion does not spend the attempt", "successionDone = true;\n                if (chosen != null) heir = chosen;", "if (chosen != null) { successionDone = true; heir = chosen; }"),
    ("promotion forgets the heir", "if (chosen != null) heir = chosen;", ""),
    ("promotion takes the ineligible", "if (young[i] == null || !eligible(young[i])) continue;", "if (young[i] == null) continue;"),
    ("self-tame first look does not schedule", "if (nextCheckTick < 0) { nextCheckTick = now + intervalRoll(); return false; }", "if (nextCheckTick < 0) { return false; }"),
    ("promotion takes nulls", "if (young[i] == null || !eligible(young[i])) continue;", "if (!eligible(young[i])) continue;"),
    ("self-tame fires early", "if (now < nextCheckTick) return false;", "if (now + 1 < nextCheckTick) return false;"),
    ("self-tame never reschedules", "nextCheckTick = now + intervalRoll();\n            if (!settingOn) return false;", "if (!settingOn) return false;"),
    ("self-tame ignores the option", "if (!settingOn) return false;\n            if (hasLedger", "if (hasLedger"),
    ("self-tame ignores a broken record", "if (hasLedger && !recordClean) return false;", ""),
    ("self-tame bars a ledger-less young", "if (hasLedger && !recordClean) return false;", "if (!recordClean) return false;"),
    ("reach default 0 is accepted", "read.HasValue && read.Value > 0f", "read.HasValue && read.Value >= 0f"),
    ("reach default changed", "public const float DefaultReach = 16f;", "public const float DefaultReach = 12f;"),
    ("return needs not be in water", "return inWater && distance <= reach;", "return distance <= reach;"),
    ("return reach exclusive", "return inWater && distance <= reach;", "return inWater && distance < reach;"),
    ("sale counts unstranded young", "return enabled && strandedYoung;", "return enabled;"),
    ("sale ignores the option", "return enabled && strandedYoung;", "return strandedYoung;"),
    ("betrayed mother accepts returns", "return motherBetrayed;", "return false;"),
    ("buyer delay floor changed", "BuyerDelayMin = 60000", "BuyerDelayMin = 30000"),
    ("buyer sent on first sight", "buyerAt[id] = now + rangeExclusive(BuyerDelayMin, BuyerDelayMax);\n                    continue;", "buyerAt[id] = now + rangeExclusive(BuyerDelayMin, BuyerDelayMax);"),
    ("buyer fires a tick early", "if (now >= at)", "if (now + 1 >= at)"),
    ("buyer failure rebooks nothing", "else buyerAt[id] = now + BuyerRetryTicks;", ""),
    ("buyer retry shortened", "BuyerRetryTicks = 60000", "BuyerRetryTicks = 30000"),
    ("offered young offered again", "if (offered.Contains(id)) continue;", ""),
    ("offer keeps its booking", "offered.Add(id);\n                        buyerAt.Remove(id);", "offered.Add(id);"),
    ("empty cell makes power", "if (fullness <= 0f) return 0f;", "if (fullness < 0f) return 0f;"),
    ("output ignores fullness", "return Lerp(minFraction, 1f, Clamp01(fullness));", "return Lerp(minFraction, 1f, 1f);"),
    ("refill counts as digestion", "if (lastFuel >= 0f && fuel < lastFuel) digested += lastFuel - fuel;", "if (lastFuel >= 0f) digested += Math.Abs(lastFuel - fuel);"),
    ("first look digests", "if (lastFuel >= 0f && fuel < lastFuel) digested += lastFuel - fuel;", "if (fuel < lastFuel || lastFuel < 0f) digested += Math.Abs(lastFuel - fuel);"),
    ("spent test exclusive", "return digested >= lifetimeFeed && hasSpentDef && spawned;", "return digested > lifetimeFeed && hasSpentDef && spawned;"),
    ("spent ignores the missing def", "return digested >= lifetimeFeed && hasSpentDef && spawned;", "return digested >= lifetimeFeed && spawned;"),
    ("rot floor gone", "return Math.Max(2500, (int)Math.Round(days * ticksPerDay));", "return (int)Math.Round(days * ticksPerDay);"),
    ("rot rounds down", "Math.Max(2500, (int)Math.Round(days * ticksPerDay))", "Math.Max(2500, (int)Math.Floor(days * ticksPerDay))"),
    ("bones floor gone", "return Math.Max(1, (int)Math.Round(bodySize * perBodySize));", "return (int)Math.Round(bodySize * perBodySize);"),
    ("stack split overfills", "int s = Math.Min(n, stackLimit);", "int s = Math.Min(n, stackLimit + 1);"),
    ("stack split drops the remainder", "while (n > 0)", "while (n >= stackLimit)"),
    ("rot restarts without clearing the clock", "target = candidate;\n                rotTicks = 0;\n                if (target < 0) return;", "target = candidate;\n                if (target < 0) return;"),
    ("rot tick adds 500", "rotTicks += TickRareInterval;", "rotTicks += TickRareInterval * 2;"),
    ("rot exclusive", "if (rotTicks >= rotDown)", "if (rotTicks > rotDown)"),
    ("finished rot keeps its target", "done = true;\n                target = -1;", "done = true;"),
    ("flotsam seeds twice", "if (!seeded)\n            {\n                seeded = true;", "if (true)\n            {\n                seeded = true;"),
    ("flotsam seed 25", "SeedStacks = 24", "SeedStacks = 25"),
    ("flotsam restock on equal recede", "if (recedeTickNow > lastRecedeSeen)", "if (recedeTickNow >= lastRecedeSeen)"),
    ("flotsam restock forgets the tick", "lastRecedeSeen = recedeTickNow;\n                return RestockStacks;", "return RestockStacks;"),
    ("flotsam cap ignores amount", "int room = (int)Math.Round(CapStacks * amount) - placedCount;", "int room = CapStacks - placedCount;"),
    ("flotsam want ignores amount", "int want = (int)Math.Round(baseStacks * amount);", "int want = baseStacks;"),
    ("flotsam cap raised", "CapStacks = 70", "CapStacks = 71"),
    ("flotsam pick never reaches the last row", "if (roll <= 0f) return i;", "if (roll < 0f) return i;"),
    ("flotsam pick ignores weights", "float roll = roll01 * total;", "float roll = roll01 * weights.Count;"),
    ("balm takes 2", "float s = Math.Max(0f, severity - 3f);", "float s = Math.Max(0f, severity - 2f);"),
    ("balm leaves negative", "float s = Math.Max(0f, severity - 3f);", "float s = severity - 3f;"),
    ("balm keeps a trace scar", "removed = s <= 0.01f;", "removed = s <= 0f;"),
    ("biome ignores water", "if (tileNull || waterCovered) return -100f;", "if (tileNull) return -100f;"),
    ("biome rarity gate", "if (rarity <= 0.001f) return -100f;", "if (rarity < 0f) return -100f;"),
    ("biome temperature max inclusive", "if (temperature < r.tempMin || temperature > r.tempMax) return 0f;", "if (temperature < r.tempMin || temperature >= r.tempMax) return 0f;"),
    ("biome rainfall max inclusive", "if (rainfall < r.rainMin || rainfall >= r.rainMax) return 0f;", "if (rainfall < r.rainMin || rainfall > r.rainMax) return 0f;"),
    ("biome ignores hills", "if (hillsBlock) return 0f;", ""),
    ("biome ignores the river", "if (!hasRiver) return 0f;", ""),
    ("biome ignores spawn chance", "if (gate < 1f && !seededChance(gate)) return 0f;", ""),
    ("biome divisor 0 allowed", "(r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f", "r.rainfallDivisor"),
    ("biome score drops the river bonus", "+ r.riverOrCoastBonus;", ";"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_miasma_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
