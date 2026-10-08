#!/usr/bin/env python3
"""Mutation proof for the RimProperty fuzz: plants each defect in the kernel (RM_PropertyKernel.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_property_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/RimProperty/Source/Kernel/RM_PropertyKernel.cs"
MUTATIONS = [
    ("lifetime ignores the multiplier", "days *= multiplier;", ""),
    ("claims never expire", "if (ageTicks >= lifetime) return 0f;", ""),
    ("claims expire at half their life", "if (ageTicks >= lifetime) return 0f;", "if (ageTicks >= lifetime / 2f) return 0f;"),
    ("decay is not linear", "return initialStrength * (1f - ageTicks / lifetime);", "return initialStrength * (1f - ageTicks / lifetime) * (1f - ageTicks / lifetime);"),
    ("a claim not yet born decays", "if (ageTicks <= 0) return initialStrength;", "if (ageTicks < 0) return initialStrength;"),
    ("commons outrank pawns", "case KindPawn: return 2;\n                case KindCommons: return 1;", "case KindPawn: return 1;\n                case KindCommons: return 2;"),
    ("ghost commons accepted", "return (kind == KindPawn && pawnMissing) || (kind == KindCommons && factionMissing);", "return (kind == KindPawn && pawnMissing);"),
    ("ghost pawn accepted", "return (kind == KindPawn && pawnMissing) || (kind == KindCommons && factionMissing);", "return (kind == KindCommons && factionMissing);"),
    ("weakest claim wins", "int byStrength = bStrength.CompareTo(aStrength);", "int byStrength = aStrength.CompareTo(bStrength);"),
    ("less specific claimant wins a tie", "int bySpecificity = bSpecificity.CompareTo(aSpecificity);", "int bySpecificity = aSpecificity.CompareTo(bSpecificity);"),
    ("older claim wins a tie", "return bTimestamp.CompareTo(aTimestamp);", "return aTimestamp.CompareTo(bTimestamp);"),
    ("territorial before situational", "if (hasPossessor) return VirtualSituational;\n            if (hasFaction) return VirtualTerritorial;", "if (hasFaction) return VirtualTerritorial;\n            if (hasPossessor) return VirtualSituational;"),
    ("any faction's commons is usable", "return claimantKind == KindCommons && actorKind == KindPawn && sameFaction;", "return claimantKind == KindCommons && actorKind == KindPawn;"),
    ("a pawn may use another pawn's property", "return claimantKind == KindCommons && actorKind == KindPawn && sameFaction;", "return actorKind == KindPawn && sameFaction;"),
    ("unclaimed is forbidden", "if (!hasPriorClaim) return true;\n            return claimantMayUse;", "if (!hasPriorClaim) return false;\n            return claimantMayUse;"),
    ("a purchase is not legitimate", "return act == ActBuy || act == ActClaim ? true : authorized;", "return act == ActClaim ? true : authorized;"),
    ("a paid claim is not legitimate", "return act == ActBuy || act == ActClaim ? true : authorized;", "return act == ActBuy ? true : authorized;"),
    ("an authorized take is recorded stolen", "return !authorized && hasPriorClaim ? WriteStolenFromPrior : WriteNone;", "return hasPriorClaim ? WriteStolenFromPrior : WriteNone;"),
    ("stripping steals nothing", "case ActTake:\n                case ActStrip:\n", "case ActTake:\n"),
    ("theft with no owner writes a claim", "return !authorized && hasPriorClaim ? WriteStolenFromPrior : WriteNone;", "return !authorized ? WriteStolenFromPrior : WriteNone;"),
    ("a purchase records a claim fee", "case ActBuy: return WritePurchased;", "case ActBuy: return WriteClaimFeePaid;"),
    ("perception ignores the master switch", "return !authorizedAfter && perceptionEnabled;", "return !authorizedAfter;"),
    ("perception fires on authorized acts", "return !authorizedAfter && perceptionEnabled;", "return perceptionEnabled;"),
    ("loot origin inverted", "public static bool LootKeepsOrigin(bool originalOwnerUnclaimed) { return !originalOwnerUnclaimed; }", "public static bool LootKeepsOrigin(bool originalOwnerUnclaimed) { return originalOwnerUnclaimed; }"),
    ("any witness is the owner", "return priorHasPawnOwner && witnessIsOwner;", "return priorHasPawnOwner || witnessIsOwner;"),
    ("days use integer division", "return (nowTick - timestamp) / (float)ticksPerDay;", "return (nowTick - timestamp) / ticksPerDay;"),
    ("suspicion expires a day late", "return daysElapsed >= halfLifeDays;", "return daysElapsed > halfLifeDays + 1f;"),
    ("propagation unclamped", "return Clamp01(daysElapsed * ratePerDay);", "return daysElapsed * ratePerDay;"),
    ("suspicion decay unclamped", "return Clamp01(1f - daysElapsed / halfLifeDays);", "return 1f - daysElapsed / halfLifeDays;"),
    ("contribution forgets decay", "return confidence * Propagated(daysElapsed, ratePerDay) * Decay(daysElapsed, halfLifeDays);", "return confidence * Propagated(daysElapsed, ratePerDay);"),
    ("dampen fraction unclamped", "fraction = Clamp01(fraction);\n            if (fraction <= 0f) return confidence;", "if (fraction <= 0f) return confidence;"),
    ("dampen inverts", "return confidence * (1f - fraction);", "return confidence * fraction;"),
    ("wipe drops the colony's pawns", "return keepIsCommonsOfFaction && claimantKind == KindPawn && claimantPawnKnown && pawnInKeepFaction;", "return false;"),
    ("wipe keeps every pawn", "return keepIsCommonsOfFaction && claimantKind == KindPawn && claimantPawnKnown && pawnInKeepFaction;", "return claimantKind == KindPawn;"),
    ("non-stackables score the same", "if (hasDef && stackLimit <= 1) score += NonStackableWeight;", "if (hasDef && stackLimit < 1) score += NonStackableWeight;"),
    ("quality weight halved", "score += QualityWeight * ((float)quality / (float)LegendaryQuality);", "score += QualityWeight * ((float)quality / (float)LegendaryQuality) * 0.5f;"),
    ("worthless things score zero", "float score = Baseline;", "float score = 0f;"),
    ("configured fee can be zero", "return Math.Max(1, Round(setting));", "return Round(setting);"),
    ("price ignores the stack", "float total = unitValue * Math.Max(1, stackCount) * markup;", "float total = unitValue * markup;"),
    ("price ignores the markup", "float total = unitValue * Math.Max(1, stackCount) * markup;", "float total = unitValue * Math.Max(1, stackCount);"),
    ("fee ignores the claim strength", "float strengthFactor = Lerp(unclaimedFloor, 1f, claimStrength);", "float strengthFactor = 1f;"),
    ("fee for the unclaimed uses the prior strength", "float claimStrength = Clamp01(hasPriorClaim ? priorStrength : 0f);", "float claimStrength = Clamp01(priorStrength);"),
    ("fee has no floor", "return Math.Max(1, Round(fee));", "return Round(fee);"),
    ("exact change cannot pay", "public static bool CanPay(int carried, int fee) { return carried >= fee; }", "public static bool CanPay(int carried, int fee) { return carried > fee; }"),
    ("a stack gives up more than the remaining", "return Math.Min(remaining, stackCount);", "return stackCount;"),
    ("pocket value ignores the stack", "return Math.Max(0f, marketValue) * Math.Max(1, stackCount);", "return Math.Max(0f, marketValue);"),
    ("pocket threshold exclusive", "return !(itemValue < minValue);", "return itemValue > minValue;"),
    ("a tie goes to the later item", "public static bool BeatsBest(float value, float bestValue) { return value > bestValue; }", "public static bool BeatsBest(float value, float bestValue) { return value >= bestValue; }"),
    ("animal-theft frequency inverted", "return !(frequencyMultiplier < 1f && draw >= frequencyMultiplier);", "return !(frequencyMultiplier < 1f && draw < frequencyMultiplier);"),
    ("carry limit exclusive", "return !(mass > maxMass);", "return mass < maxMass;"),
    ("fees round half away from zero", "public static int Round(float v) { return (int)Math.Round(v); }", "public static int Round(float v) { return (int)Math.Round(v, MidpointRounding.AwayFromZero); }"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_property_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
