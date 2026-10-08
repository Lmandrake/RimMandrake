#!/usr/bin/env python3
"""Mutation proof for the SWBestiary fuzz: plants each defect in its kernel (livestock, beast mechanics or ikee), demands the fuzz FAILS, restores
the file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_swbestiary_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

BASE = "src/RimStarWars/SWBestiary/Source/"
LIVESTOCK = BASE + "Livestock/Kernel/RSW_LivestockKernel.cs"
BEAST = BASE + "BeastMechanics/Kernel/RSW_BeastKernel.cs"
IKEE = BASE + "JawaIkee/Kernel/RSW_IkeeKernel.cs"

M_LIVESTOCK = [
    ("kiln: spaced needs more than the rushed span", "return span >= rushedSpanTicks && span <= windowTicks;", "return span > rushedSpanTicks && span <= windowTicks;"),
    ("kiln: spaced window exclusive", "return span >= rushedSpanTicks && span <= windowTicks;", "return span >= rushedSpanTicks && span < windowTicks;"),
    ("kiln: any span is spaced", "return span >= rushedSpanTicks && span <= windowTicks;", "return span >= rushedSpanTicks;"),
    ("kiln: cold at exactly the window", "return doses.Count > 0 && now - doses[doses.Count - 1] > windowTicks;", "return doses.Count > 0 && now - doses[doses.Count - 1] >= windowTicks;"),
    ("kiln: cooling ignores the setting", "if (!enabled) return;\n            if (WentCold(doses, now, windowTicks)) doses.Clear();", "if (WentCold(doses, now, windowTicks)) doses.Clear();"),
    ("kiln: cooling never clears", "if (WentCold(doses, now, windowTicks)) doses.Clear();\n        }", "if (WentCold(doses, now, windowTicks)) { }\n        }"),
    ("kiln: dose counted with the setting off", "if (!enabled) return Result.Ignored;", ""),
    ("kiln: any food counts", "if (!feedMatches) return Result.Ignored;", ""),
    ("kiln: dose counted during the cooldown", "if (now < nextFireReadyTick) return Result.Ignored;", ""),
    ("kiln: cooldown ends one tick late", "if (now < nextFireReadyTick) return Result.Ignored;", "if (now <= nextFireReadyTick) return Result.Ignored;"),
    ("kiln: stale doses spliced onto a fresh one", "if (WentCold(doses, now, r.WindowTicks)) doses.Clear();\n            doses.Add(now);", "doses.Add(now);"),
    ("kiln: fires one dose late", "if (doses.Count < r.DosesNeeded) return Result.Counted;", "if (doses.Count <= r.DosesNeeded) return Result.Counted;"),
    ("kiln: ledger kept after firing", "doses.Clear();\n            nextFireReadyTick", "nextFireReadyTick"),
    ("kiln: cooldown ignores the slider", "(int)Math.Round(r.FireCooldownTicks * r.CooldownMultiplier)", "r.FireCooldownTicks"),
    ("kiln: no cooldown after firing", "nextFireReadyTick = now + Math.Max(0, (int)Math.Round(r.FireCooldownTicks * r.CooldownMultiplier));", ""),
    ("kiln: span from the wrong dose", "spaced = IsSpaced(doses[0], doses[doses.Count - 1], r.RushedSpanTicks, r.WindowTicks);", "spaced = IsSpaced(doses[0], doses[doses.Count - 2], r.RushedSpanTicks, r.WindowTicks);"),
    ("kiln: feed rule inverted", "return !hasFeedDef || eatenIsFeedDef;", "return !hasFeedDef && eatenIsFeedDef;"),
    ("grief: tames when owned", "return !hasFaction && !downed && !inMentalState && !fogged;", "return !downed && !inMentalState && !fogged;"),
    ("grief: tames when downed", "return !hasFaction && !downed && !inMentalState && !fogged;", "return !hasFaction && !inMentalState && !fogged;"),
    ("grief: tames in a mental state", "return !hasFaction && !downed && !inMentalState && !fogged;", "return !hasFaction && !downed && !fogged;"),
    ("grief: tames under fog", "return !hasFaction && !downed && !inMentalState && !fogged;", "return !hasFaction && !downed && !inMentalState;"),
    ("grief: release delay ignores the slider", "return (int)Math.Round(releaseDelayTicks * multiplier);", "return releaseDelayTicks;"),
    ("grief: ledger has no ceiling", "return Math.Min(stored + perDay * (TickRareInterval / (float)TicksPerDay), max);", "return stored + perDay * (TickRareInterval / (float)TicksPerDay);"),
    ("grief: ledger grows ten times fast", "perDay * (TickRareInterval / (float)TicksPerDay)", "perDay * (TickRareInterval * 10 / (float)TicksPerDay)"),
    ("grief: join timer restarts every tick", "return joinTick < 0 && playerOwned ? now : joinTick;", "return playerOwned ? now : joinTick;"),
    ("grief: join before ownership", "return joinTick < 0 && playerOwned ? now : joinTick;", "return joinTick < 0 ? now : joinTick;"),
    ("grief: release one tick late", "return joinTick >= 0 && now - joinTick >= delay;", "return joinTick >= 0 && now - joinTick > delay;"),
    ("grief: release without a join", "return joinTick >= 0 && now - joinTick >= delay;", "return now - joinTick >= delay;"),
    ("grief: spike erased by the next update", "return Math.Max(severity, Math.Min(severity + step, target));", "return Math.Min(severity + step, target);"),
    ("grief: unsettled jumps to the target", "return Math.Max(severity, Math.Min(severity + step, target));", "return Math.Max(severity, target);"),
    ("grief: unsettled never rises", "return Math.Max(severity, Math.Min(severity + step, target));", "return severity;"),
    ("grief: new hediff starts empty", "if (!has) return step;", "if (!has) return 0f;"),
    ("grief: release spike is the target", "public static float Spike(float spike) { return spike; }", "public static float Spike(float spike) { return spike * 0.5f; }"),
]

M_BEAST = [
    ("eat: whole-item flag ignored", "if (fullyDestroy) { b.Destroy = true; return b; }", ""),
    ("eat: tiny item eaten forever", "b.HitPoints -= Math.Max(1, (int)Math.Round(maxHitPoints * percentageOfDestruction));", "b.HitPoints -= (int)Math.Round(maxHitPoints * percentageOfDestruction);"),
    ("eat: dies only below zero", "if (b.HitPoints <= 0) b.Destroy = true;", "if (b.HitPoints < 0) b.Destroy = true;"),
    ("eat: ignore flag ignored", "if (useHitPoints && !ignoreUseHitPoints)", "if (useHitPoints)"),
    ("eat: stack bite may be zero", "int bite = Math.Max(1, (int)Math.Round(percentageOfDestruction * stackLimit));", "int bite = (int)Math.Round(percentageOfDestruction * stackLimit);"),
    ("eat: stack floor inclusive", "if (b.StackCount < MinStackLeft) b.Destroy = true;", "if (b.StackCount <= MinStackLeft) b.Destroy = true;"),
    ("eat: stack never runs out", "if (b.StackCount < MinStackLeft) b.Destroy = true;", ""),
    ("eat: stack floor constant", "public const int MinStackLeft = 10;", "public const int MinStackLeft = 5;"),
    ("eat: hungry inclusive", "public static bool Hungry(float foodPct, float wantEatPct) { return foodPct < wantEatPct; }", "public static bool Hungry(float foodPct, float wantEatPct) { return foodPct <= wantEatPct; }"),
    ("eat: priority without the comp", "if (!enabled || !hasFoodNeed || !hasEaterComp) return 0f;", "if (!enabled || !hasFoodNeed) return 0f;"),
    ("eat: priority ignores the setting", "if (!enabled || !hasFoodNeed || !hasEaterComp) return 0f;", "if (!hasFoodNeed || !hasEaterComp) return 0f;"),
    ("eat: priority value", "public const float EatPriorityValue = 9.5f;", "public const float EatPriorityValue = 3f;"),
    ("eat: digs while awake only inverted", "return digEnabled && namesThing && foodPct < hungryPct && awake;", "return digEnabled && namesThing && foodPct < hungryPct && !awake;"),
    ("eat: digs when merely peckish", "return digEnabled && namesThing && foodPct < hungryPct && awake;", "return digEnabled && namesThing && awake;"),
    ("eat: food block ignores its flag", "return enabled && hasEaterComp && blockFlag;", "return enabled && hasEaterComp;"),
    ("eat: food block ignores the setting", "return enabled && hasEaterComp && blockFlag;", "return hasEaterComp && blockFlag;"),
    ("hoard: sleeps through the hoarding", "if (!awake) return false;", ""),
    ("hoard: hoards under threat", "if (!calm) return false;", ""),
    ("hoard: hoards without hands", "if (!canManipulate) return false;", ""),
    ("hoard: hoards while hungry", "if (hasFoodNeed && foodPct < wantEatPct) return false;", ""),
    ("hoard: rest floor inclusive", "if (hasRestNeed && restPct < RestFloor) return false;", "if (hasRestNeed && restPct <= RestFloor) return false;"),
    ("hoard: rest floor constant", "public const float RestFloor = 0.4f", "public const float RestFloor = 0.3f"),
    ("hoard: hoards while laying", "if (layingEggNow) return false;", ""),
    ("hoard: ignores the setting", "if (!enabled) return false;\n            if (!aliveOnMap) return false;", "if (!aliveOnMap) return false;"),
    ("hoard: nest ties go to the last", "if (dist[i] > radius || dist[i] >= bestDist) continue;", "if (dist[i] > radius || dist[i] > bestDist) continue;"),
    ("hoard: nest radius inclusive of nothing", "if (dist[i] > radius || dist[i] >= bestDist) continue;", "if (dist[i] >= radius || dist[i] >= bestDist) continue;"),
    ("hoard: unspawned nests count", "if (!spawned[i]) continue;", ""),
    ("hoard: nearest forgotten", "if (dist[i] > radius || dist[i] >= bestDist) continue;", "if (dist[i] > radius) continue;"),
    ("hoard: reach asked for every nest", "if (dist[i] > radius || dist[i] >= bestDist) continue;\n                if (!reachable(i)) continue;", "if (!reachable(i)) continue;\n                if (dist[i] > radius || dist[i] >= bestDist) continue;"),
    ("hoard: unreachable nests count", "if (!reachable(i)) continue;\n                best = i;", "best = i;"),
    ("hoard: nest cap off by one", "public static bool CanAddNest(int existing, int maxPerMap) { return existing < maxPerMap; }", "public static bool CanAddNest(int existing, int maxPerMap) { return existing <= maxPerMap; }"),
    ("hoard: spacing exclusive", "return !(nearestNestDist < minSpacing);", "return nearestNestDist > minSpacing;"),
    ("hoard: nest in the base", "if (home()) return false;", ""),
    ("hoard: nest on a roof", "if (roofed()) return false;", ""),
    ("hoard: nest on a building", "if (occupied()) return false;", ""),
    ("hoard: nest out of reach", "if (!reachable()) return false;", ""),
    ("hoard: plant cover ignored", "if (requirePlantCover && !nearPlant()) return false;", ""),
    ("hoard: reach asked before the roof", "if (roofed()) return false;\n            if (!reachable()) return false;", "if (!reachable()) return false;\n            if (roofed()) return false;"),
    ("hoard: plant asked eagerly", "if (requirePlantCover && !nearPlant()) return false;", "if (nearPlant() && false) return false;\n            if (requirePlantCover && !nearPlant()) return false;"),
    ("hoard: out of bounds cell probed", "if (!inBounds || !openGround()) return false;", "if (!openGround() || !inBounds) return false;"),
    ("hoard: steals from storage", "if (inAnyStorage()) return false;", ""),
    ("hoard: steals from the base", "if (inHomeArea()) return false;", ""),
    ("hoard: steals from shelves", "if (onStorageBuilding()) return false;", ""),
    ("hoard: shuffles the hoard", "if (distToNest() <= TakeableNestClearance) return false;", ""),
    ("hoard: clearance exclusive", "if (distToNest() <= TakeableNestClearance) return false;", "if (distToNest() < TakeableNestClearance) return false;"),
    ("hoard: takes empty stacks", "if (!spawned || stackCount <= 0 || !hasMap) return false;", "if (!spawned || !hasMap) return false;"),
    ("ability: regrants forever", "if (granted || !enabled) return Step.Nothing;", "if (!enabled) return Step.Nothing;"),
    ("ability: grants with the setting off", "if (granted || !enabled) return Step.Nothing;", "if (granted) return Step.Nothing;"),
    ("ability: non-pawn marked granted", "if (!isPawn) return Step.Nothing;", "if (!isPawn) return Step.MarkGrantedOnly;"),
    ("ability: missing def never settles", "if (!hasAbility) return Step.MarkGrantedOnly;", "if (!hasAbility) return Step.Nothing;"),
    ("toxin: satisfied threshold inclusive", "return level > SatisfiedAbove ? Satisfied", "return level >= SatisfiedAbove ? Satisfied"),
    ("toxin: desire threshold inclusive", "level > DesireAbove ? Desire : Withdrawal", "level >= DesireAbove ? Desire : Withdrawal"),
    ("toxin: harm in the wrong stage", "return category == Withdrawal ? 1 : 0;", "return category == Desire ? 1 : 0;"),
    ("toxin: clamp without a floor", "return Math.Min(Math.Max(level, 0f), max);", "return Math.Min(level, max);"),
    ("toxin: clamp without a ceiling", "return Math.Min(Math.Max(level, 0f), max);", "return Math.Max(level, 0f);"),
    ("toxin: frozen need moves", "if (frozen) return level;", ""),
    ("toxin: off does not fill", "if (!enabled) return max;", "if (!enabled) return level;"),
    ("toxin: fed need falls", "return fed ? level + GainPerTick * IntervalTicks : level - fallPerDay / TicksPerDay * IntervalTicks;", "return fed ? level - GainPerTick * IntervalTicks : level - fallPerDay / TicksPerDay * IntervalTicks;"),
    ("toxin: unfed need rises", "return fed ? level + GainPerTick * IntervalTicks : level - fallPerDay / TicksPerDay * IntervalTicks;", "return fed ? level + GainPerTick * IntervalTicks : level + fallPerDay / TicksPerDay * IntervalTicks;"),
    ("toxin: day length", "public const int IntervalTicks = 150, TicksPerDay = 60000;", "public const int IntervalTicks = 150, TicksPerDay = 6000;"),
    ("toxin: gain rate", "public const float GainPerTick = 0.0001f", "public const float GainPerTick = 0.001f"),
    ("spew: own-cell target not empty", "if (px == tx && pz == tz) { c.Empty = true; return c; }", ""),
    ("spew: aim rounds down", "c.AimX = (int)Math.Round(px + dx * range);", "c.AimX = (int)Math.Floor(px + dx * range);"),
    ("spew: aim stops short", "c.AimZ = (int)Math.Round(pz + dz * range);", "c.AimZ = (int)Math.Round(pz + dz * range * 0.5f);"),
    ("spew: half angle from the full width", "float halfWidth = lineWidthEnd / 2f;", "float halfWidth = lineWidthEnd;"),
    ("spew: half angle small-angle", "c.HalfAngle = (float)(Math.Asin(halfWidth / hyp) * 180.0 / Math.PI);", "c.HalfAngle = halfWidth / aimLen * 57.29578f;"),
    ("spew: angle axes swapped", "return (float)(Math.Atan2(dz, dx) * 180.0 / Math.PI);", "return (float)(Math.Atan2(dx, dz) * 180.0 / Math.PI);"),
    ("spew: angle mirrored", "return (float)(Math.Atan2(dz, dx) * 180.0 / Math.PI);", "return (float)(Math.Atan2(-dz, dx) * 180.0 / Math.PI);"),
    ("spew: delta not wrapped", "d = d - 360f * (float)Math.Floor(d / 360f);\n            if (d > 180f) d -= 360f;\n            return d;", "return d;"),
    ("spew: cone is full-circle half open", "public static bool InCone(Cone c, int cx, int cz) { return Math.Abs(DeltaAngle(AngleOf(cx, cz), c.Heading)) <= c.HalfAngle; }", "public static bool InCone(Cone c, int cx, int cz) { return Math.Abs(DeltaAngle(AngleOf(cx, cz), c.Heading)) <= c.HalfAngle * 2f; }"),
    ("spew: one-sided cone", "return Math.Abs(DeltaAngle(AngleOf(cx, cz), c.Heading)) <= c.HalfAngle; }", "return DeltaAngle(AngleOf(cx, cz), c.Heading) <= c.HalfAngle; }"),
]

M_IKEE = [
    ("ikee: setting ignored", "if (!enabled) return Inactive;", ""),
    ("ikee: animals feel it", "if (!spawnedOnMap || !humanlike) return Inactive;", "if (!spawnedOnMap) return Inactive;"),
    ("ikee: unspawned pawns feel it", "if (!spawnedOnMap || !humanlike) return Inactive;", "if (!humanlike) return Inactive;"),
    ("ikee: no ikee needed", "if (!ikeeNear()) return Inactive;", ""),
    ("ikee: search runs first", "if (!enabled) return Inactive;\n            if (!spawnedOnMap || !humanlike) return Inactive;\n            if (!ikeeNear()) return Inactive;", "if (!ikeeNear()) return Inactive;\n            if (!enabled) return Inactive;\n            if (!spawnedOnMap || !humanlike) return Inactive;"),
    ("ikee: tolerance inverted", "return tolerantXenotype ? Comforted : Unsettled;", "return tolerantXenotype ? Unsettled : Comforted;"),
    ("ikee: radius exclusive", "return !((float)(dx * dx + dz * dz) > r2);", "return (float)(dx * dx + dz * dz) < r2;"),
    ("ikee: radius linear", "float r2 = radius * radius;", "float r2 = radius;"),
    ("ikee: default radius", "public const float DefaultRadius = 12f;", "public const float DefaultRadius = 8f;"),
    ("ikee: stage numbers swapped", "public const int Inactive = -1, Comforted = 0, Unsettled = 1;", "public const int Inactive = -1, Comforted = 1, Unsettled = 0;"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = 0
    for kernel, muts in ((LIVESTOCK, M_LIVESTOCK), (BEAST, M_BEAST), (IKEE, M_IKEE)):
        if only and not any(only in m[0] for m in muts):
            continue
        rc |= run_mutations(kernel, "selftest_swbestiary_fuzz.py", muts, only)
    sys.exit(rc)
