// Verse-free kernel of titan breakthrough clearing (TITAN_BREAKTHROUGH_CLEARING_1; GPT review B3.4 / C3.5 / D3.2 / B1.3 / C1.3 /
// D1.3). Owner, card #1 of TITANIC_CREATURES_MOD_1 (2026-09-09): "a titan ... smashes through anything built"; the merge adds
// T3-smashes-giant-plants (owner ruling 2026-10-07 by question card).
//
// Why it is needed (decompiled 1.6): Pawn_PathFollower.StartPath refuses a destination that fails
// Reachability.CanReach(PassDoors) and calls PatherFailed before a single step, so a titan whose way is sealed by a wall or a giant
// trunk never reaches the wall the wake would crush; and a reachable destination behind a long detour is simply walked around.
// The clearing behaviour: on such a path start, find the first obstacle (the first blocking edifice of a PassAllDestroyableThings
// path, like vanilla's sappers via PawnPath.FirstBlockingBuilding, or else the first solid cell on the straight line, because 1.6's
// path grid never lets that mode through a part-fill edifice such as a trunk), walk up to it and strike it on a timed cadence
// through the wake's own crush rules, then resume the original job, which repaths.
//
// SelfTest/ClearingFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib.
// Tiers are ints (None 0, T1 1, T2 2, T3 3), the encoding RM_TitanicKernel uses.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>What a blocking cell is, for clearing.</summary>
    public enum ClearKind
    {
        /// <summary>Nothing clearable: open ground, natural rock, water, a protected or unlisted thing.</summary>
        None = 0,
        /// <summary>A built edifice the crush table lets this tier crush.</summary>
        Building = 1,
        /// <summary>A giant plant (its trunk cell or solid root): struck through the plant's own damage route.</summary>
        Trunk = 2,
    }

    /// <summary>Which obstacle a clearing decision picked.</summary>
    public enum ClearSource
    {
        None = 0,
        /// <summary>The first blocker of a PassAllDestroyableThings path.</summary>
        Breach = 1,
        /// <summary>The first solid cell on the straight line to the destination.</summary>
        Probe = 2,
    }

    public static class TitanClearing
    {
        /// <summary>Ticks between two strikes on an obstacle (the "timed cadence"): one heavy blow a second.</summary>
        public const int StrikeIntervalTicks = 60;

        /// <summary>A clearing job gives up after this many strikes (bound: an obstacle the tier cannot really hurt).</summary>
        public const int MaxStrikes = 40;

        /// <summary>The straight-line probe looks this many cells ahead, no further.</summary>
        public const int ProbeMaxCells = 60;

        /// <summary>A reachable path start is checked for a long detour at most once per this many ticks per titan (each check
        /// is two synchronous path searches; an unreachable start is always checked, since it would otherwise fail).</summary>
        public const int DetourCheckCooldownTicks = 600;

        /// <summary>An obstacle a clearing job gave up on is not chosen again by the same titan for this long.</summary>
        public const int GiveUpMemoTicks = 2500;

        /// <summary>A detour must cost at least this many ticks more than the way through, as well as the ratio, before a titan
        /// smashes instead of walking round (a 3-cell detour is never worth a wall).</summary>
        public const float MinSavingTicks = 240f;

        public const float DefaultDetourFactor = 2.5f;
        public const float MinDetourFactor = 1.5f;
        public const float MaxDetourFactor = 6f;

        /// <summary>Clearing is a sub-behaviour of the wake: live only with giant animals, the wake and its own toggle on.</summary>
        public static bool Active(bool giantAnimals, bool wake, bool clearing) => HugeGates.Wake(giantAnimals, wake, clearing);

        /// <summary>
        /// A built obstacle a titan of this tier may strike. Never: anything the crush table refuses at this tier (unlisted,
        /// explicitly protected rows such as chunks, or below the row's tier), an indestructible def, natural rock (not built),
        /// a quest object, a giant trunk (that is the Trunk route), or a building of the titan's own faction or one it is not
        /// hostile to (a tame titan does not knock down its own colony's walls to shorten a walk).
        /// </summary>
        public static bool BuildingEligible(int tier, bool crushAllowedAtTier, bool destroyable, bool naturalRock, bool questObject,
                                            bool friendlyOwned, bool isTrunk)
        {
            return tier >= 1 && tier <= 3 && crushAllowedAtTier && destroyable && !naturalRock && !questObject && !friendlyOwned
                   && !isTrunk;
        }

        /// <summary>A giant plant this tier may strike: only a smasher (GiantSmash.Smashes, T3 by default), only a live owner,
        /// never a quest object.</summary>
        public static bool TrunkEligible(int tier, int minTier, bool smashActive, bool ownerAlive, bool questObject)
        {
            return tier <= 3 && GiantSmash.Smashes(tier, minTier, smashActive) && ownerAlive && !questObject;
        }

        /// <summary>
        /// Is clearing worth it. An unreachable destination: always (it is the only way). A reachable one: only when the walk
        /// round costs more than factor x the way through AND at least MinSavingTicks more. A non-finite or negative cost
        /// never clears; the factor is sanitized into its slider range.
        /// </summary>
        public static bool Worth(bool reachable, float byPawnCost, float throughCost, float factor)
        {
            if (!reachable) return true;
            if (!Finite(byPawnCost) || !Finite(throughCost) || byPawnCost < 0f || throughCost < 0f) return false;
            float f = SaneFactor(factor);
            return byPawnCost > f * throughCost && byPawnCost - throughCost >= MinSavingTicks;
        }

        /// <summary>
        /// The decision. The breach path's first blocker wins when it is clearable and worth it; else the straight-line probe's
        /// first solid cell when that is. Each source offers only its FIRST obstacle, so a protected one is never passed over for
        /// something behind it on the same route: with both sources protected the titan clears nothing and vanilla's pather fails
        /// (or walks round) exactly as before.
        /// </summary>
        public static ClearSource Choose(bool reachable, float byPawnCost, float factor,
                                         ClearKind breachKind, float breachCost, ClearKind probeKind, float probeCost)
        {
            if (breachKind != ClearKind.None && Worth(reachable, byPawnCost, breachCost, factor)) return ClearSource.Breach;
            if (probeKind != ClearKind.None && Worth(reachable, byPawnCost, probeCost, factor)) return ClearSource.Probe;
            return ClearSource.None;
        }

        /// <summary>Is a strike due on this tick of the strike toil (ticks counted from the toil's start, first strike at once).</summary>
        public static bool StrikeDue(int ticksInToil) => ticksInToil >= 0 && ticksInToil % StrikeIntervalTicks == 0;

        public static bool GiveUp(int strikes) => strikes >= MaxStrikes;

        public static bool Finite(float v) => !float.IsNaN(v) && !float.IsInfinity(v);

        public static float SaneFactor(float f)
        {
            if (!Finite(f)) return DefaultDetourFactor;
            return f < MinDetourFactor ? MinDetourFactor : (f > MaxDetourFactor ? MaxDetourFactor : f);
        }

        /// <summary>The probe's cost estimate of the straight way through: octile distance times the titan's cardinal move ticks.</summary>
        public static float StraightCost(int dx, int dz, float ticksPerCardinal)
        {
            int ax = Math.Abs(dx), az = Math.Abs(dz);
            int diag = Math.Min(ax, az), straight = Math.Max(ax, az) - diag;
            return (straight + diag * 1.41421356f) * Math.Max(0f, ticksPerCardinal);
        }

        /// <summary>
        /// The cells of the straight line from (x0,z0) to (x1,z1), excluding the start, including the end, at most maxCells,
        /// 8-connected (Bresenham). Every step moves one cell, so a lane wall one cell thick is never skipped diagonally between
        /// two of its cells: a diagonal step is split into its two orthogonal halves, x first (supercover of the corner).
        /// </summary>
        public static List<int[]> LineCells(int x0, int z0, int x1, int z1, int maxCells)
        {
            List<int[]> cells = new List<int[]>();
            int dx = Math.Abs(x1 - x0), dz = Math.Abs(z1 - z0);
            int sx = x0 < x1 ? 1 : -1, sz = z0 < z1 ? 1 : -1;
            int err = dx - dz, x = x0, z = z0;
            while ((x != x1 || z != z1) && cells.Count < maxCells)
            {
                int e2 = 2 * err;
                bool stepX = e2 > -dz, stepZ = e2 < dx;
                if (stepX && stepZ)
                {
                    err -= dz;
                    x += sx;
                    cells.Add(new[] { x, z });
                    if (cells.Count >= maxCells) break;
                    err += dx;
                    z += sz;
                    cells.Add(new[] { x, z });
                    continue;
                }
                if (stepX)
                {
                    err -= dz;
                    x += sx;
                }
                if (stepZ)
                {
                    err += dx;
                    z += sz;
                }
                cells.Add(new[] { x, z });
            }
            return cells;
        }
    }
}
