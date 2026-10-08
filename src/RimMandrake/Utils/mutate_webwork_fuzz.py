#!/usr/bin/env python3
"""Mutation proof for the Webwork fuzz: plants each defect in the kernel (RM_WebworkKernel.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_webwork_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/Webwork/Source/Kernel/RM_WebworkKernel.cs"
MUTATIONS = [
    ("adjacency ignores diagonals' margin", "return bMinX <= aMaxX + 1 && bMaxX >= aMinX - 1 && bMinZ <= aMaxZ + 1 && bMaxZ >= aMinZ - 1;", "return bMinX <= aMaxX && bMaxX >= aMinX && bMinZ <= aMaxZ + 1 && bMaxZ >= aMinZ - 1;"),
    ("supporter is any neighbour of equal or lower rank", "return neighbourRank < myRank; }", "return neighbourRank <= myRank; }"),
    ("supported direction flipped", "public static bool IsSupported(int neighbourRank, int myRank) { return neighbourRank > myRank; }", "public static bool IsSupported(int neighbourRank, int myRank) { return neighbourRank >= myRank - 1; }"),
    ("item load ignores the stack", "return mass * stackCount / Math.Max(1f, itemMassPerLoad);", "return mass / Math.Max(1f, itemMassPerLoad);"),
    ("heavy damage at <=", "return hitPoints < maxHitPoints * HeavyDamageFraction;", "return hitPoints <= maxHitPoints * HeavyDamageFraction;"),
    ("lost supports not counted", "load += lostSupports * loadCapacity;", ""),
    ("heavy supporters count half", "load += heavySupporters * loadCapacity;", "load += heavySupporters * loadCapacity * 0.5f;"),
    ("overload edge exclusive", "public static bool Overloaded(float load, float loadCapacity) { return load >= loadCapacity; }", "public static bool Overloaded(float load, float loadCapacity) { return load > loadCapacity; }"),
    ("window floor gone", "return Math.Max(MinWindowTicks, (int)Math.Round(warningHours * TicksPerHour));", "return (int)Math.Round(warningHours * TicksPerHour);"),
    ("examine ticks not doubled when bare", "* (wrapped ? 1 : 2);", "* 1;"),
    ("near radius ignores the piece size", "return d <= nearRadius + Math.Max(sizeX, sizeZ) * 0.5f;", "return d <= nearRadius;"),
    ("unwatched bones still collapse", "if (!anyPawnNear())\n            {\n                return CreakEvent.None;", "if (false)\n            {\n                return CreakEvent.None;"),
    ("settle does not clear the countdown", "creakTicksLeft = -1;\n                return CreakEvent.Settled;", "return CreakEvent.Settled;"),
    ("countdown collapses one step early", "return creakTicksLeft <= 0 ? CreakEvent.Collapse : CreakEvent.Tick;", "return creakTicksLeft <= ticks ? CreakEvent.Collapse : CreakEvent.Tick;"),
    ("countdown never restarts after a settle", "creakTicksLeft = windowTicks;\n                    return CreakEvent.Started;", "creakTicksLeft = windowTicks + 1;\n                    return CreakEvent.Started;"),
    ("quiet piece starts creaking while disabled", "return enabled && !creaking && overloaded;", "return !creaking && overloaded;"),
    ("a creaking piece restarts on loss", "return enabled && !creaking && overloaded;", "return enabled && overloaded;"),
    ("last wrapping opens with a wrapped piece standing", "return isSkull && !wrapped && hasReading && !complete && spawned && everyPieceBare;", "return isSkull && !wrapped && hasReading && !complete && spawned;"),
    ("last wrapping opens twice", "return isSkull && !wrapped && hasReading && !complete && spawned && everyPieceBare;", "return isSkull && !wrapped && hasReading && spawned && everyPieceBare;"),
    ("any bare piece completes", "return isSkull && !wrapped", "return !wrapped"),
    ("examine reads a destroyed piece", "if (!hasExt || !hasReading || !spawned) return ExamineOutcome.Nothing;", "if (!hasExt || !hasReading) return ExamineOutcome.Nothing;"),
    ("weave dropped ignores the setting", "return defKnown && perPiece > 0 ? perPiece : 0;", "return defKnown ? perPiece : 0;"),
    ("chapter recorded twice", "if (!string.IsNullOrEmpty(chapter) && !chapters.Contains(chapter))", "if (!string.IsNullOrEmpty(chapter))"),
    ("chapters not reordered", "foreach (string c in ChapterOrder) if (chapters.Contains(c)) o.Add(c);", "foreach (string c in chapters) o.Add(c);"),
    ("round random always rounds up", "if (u < f) n++;", "if (f > 0f) n++;"),
    ("collapse damage ignores the multiplier", "return RoundRandom(roll * multiplier, u);", "return RoundRandom(roll, u);"),
    ("outline centre off by half a cell", "float dx = (cellX + 0.5f - cx) / a, dz = (cellZ + 0.5f - cz) / b;", "float dx = (cellX - cx) / a, dz = (cellZ + 0.5f - cz) / b;"),
    ("outline band too wide", "return Math.Abs(r - 1f) <= 0.09f;", "return Math.Abs(r - 1f) <= 0.15f;"),
    ("site margin edge off by one", "maxX >= mapX - edgeMargin", "maxX > mapX - edgeMargin"),
    ("chance of one can fail", "if (p >= 1f) return true;", "if (p > 1f) return true;"),
    ("site roll ignores the toggle", "return enabled && Chance(chance, u);", "return Chance(chance, u);"),
    ("relay fires before it is due", "if (now < nextRelayTick) return RelayPlan.NotDue;", "if (now + 250 < nextRelayTick) return RelayPlan.NotDue;"),
    ("dying nest still lays", "if (!motherAlive) return RelayPlan.DyingNest;", "if (!motherAlive) return RelayPlan.Place;"),
    ("lays on top of standing clutches", "if (!clutchDefKnown || clutchNearby) return RelayPlan.Reschedule;", "if (!clutchDefKnown) return RelayPlan.Reschedule;"),
    ("relay interval ignores the multiplier", "return Math.Max(1, (int)Math.Round(days * TicksPerDay * mult));", "return Math.Max(1, (int)Math.Round(days * TicksPerDay));"),
    ("relay multiplier floor gone", "float mult = Math.Max(MinMultiplier, multiplier);", "float mult = multiplier;"),
    ("clutch nearby radius not doubled", "float radius = searchRadius * 2f;", "float radius = searchRadius;"),
    ("nest margin edge", "x < mapX - edgeMargin && z < mapZ - edgeMargin", "x <= mapX - edgeMargin && z < mapZ - edgeMargin"),
    ("emergent fires with the setting off", "if (!enabled) return false;", ""),
    ("emergent fires on Kill", "if (!hadMap || !isVanish) return false;", "if (!hadMap) return false;"),
    ("emergent ignores the multiplier", "return RM_UrravethKernel.Chance(baseChance * multiplier, u);", "return RM_UrravethKernel.Chance(baseChance, u);"),
    ("biome scores water", "if (noTile || water) return -100f;", "if (noTile) return -100f;"),
    ("biome ignores mountains", "if (mountainous) return 0f;", ""),
    ("biome wet floor exclusive", "if (rainfall < RainMin) return 0f;", "if (rainfall <= RainMin) return 0f;"),
    ("biome heat weight", "(temperature - TempMin) * DegreeWeight", "(temperature - TempMin) * DegreeWeight * 0.5f"),
    ("biome scores while disabled", "if (!enabled) return 0f;\n            if (noTile", "if (noTile"),
    ("front interval truncation", "return (int)(baseTicks * multiplier);", "return (int)Math.Round(baseTicks * multiplier + 0.5f);"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_webwork_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
