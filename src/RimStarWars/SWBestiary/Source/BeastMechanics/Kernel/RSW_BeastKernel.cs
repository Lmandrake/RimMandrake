// Pure decision kernels of the SWBestiary beast mechanics (metal eating, scrap hoarding, innate abilities, toxin dependence, fuel spew):
// no Verse, no RimWorld, no UnityEngine. The comps, job givers and drivers call these with the same expressions they used inline and keep
// the engine half (defs, reservations, spawning, stat reads).
using System;
using System.Collections.Generic;

namespace RimMandrake.StarWars.SWBestiary
{
    /// <summary>The ferroclaw's steel diet.</summary>
    public static class RSW_EatKernel
    {
        public const float EatPriorityValue = 9.5f;
        public const int MinStackLeft = 10;

        public struct Bite { public bool Destroy; public int HitPoints; public int StackCount; }

        /// <summary>What one bite does to the eaten thing. Fully-destroy eats it whole; a thing with hit points loses that fraction of its
        /// maximum (at least one point, so a tiny item cannot be eaten forever) and dies at zero; anything else loses that fraction of a
        /// full stack (at least one) and is gone once fewer than ten remain.</summary>
        public static Bite Chew(bool fullyDestroy, bool useHitPoints, bool ignoreUseHitPoints, float percentageOfDestruction, int maxHitPoints, int hitPoints, int stackLimit, int stackCount)
        {
            Bite b = new Bite { HitPoints = hitPoints, StackCount = stackCount };
            if (fullyDestroy) { b.Destroy = true; return b; }
            if (useHitPoints && !ignoreUseHitPoints)
            {
                b.HitPoints -= Math.Max(1, (int)Math.Round(maxHitPoints * percentageOfDestruction));
                if (b.HitPoints <= 0) b.Destroy = true;
                return b;
            }
            int bite = Math.Max(1, (int)Math.Round(percentageOfDestruction * stackLimit));
            b.StackCount -= bite;
            if (b.StackCount < MinStackLeft) b.Destroy = true;
            return b;
        }

        /// <summary>Hungry enough to look for metal: below the race's want-to-eat fraction.</summary>
        public static bool Hungry(float foodPct, float wantEatPct) { return foodPct < wantEatPct; }

        /// <summary>Think-node priority: the mechanic is on, the animal has a food need and the eater comp, and it is hungry.</summary>
        public static float Priority(bool enabled, bool hasFoodNeed, bool hasEaterComp, float foodPct, float wantEatPct)
        {
            if (!enabled || !hasFoodNeed || !hasEaterComp) return 0f;
            return Hungry(foodPct, wantEatPct) ? EatPriorityValue : 0f;
        }

        /// <summary>Digging up the diet: only with nothing to eat on the map, the dig configured, a very hungry and awake animal.</summary>
        public static bool DigDue(bool digEnabled, bool namesThing, float foodPct, float hungryPct, bool awake) { return digEnabled && namesThing && foodPct < hungryPct && awake; }

        /// <summary>The prefix that stops an eater seeking ordinary food.</summary>
        public static bool BlocksNormalFood(bool enabled, bool hasEaterComp, bool blockFlag) { return enabled && hasEaterComp && blockFlag; }
    }

    /// <summary>The scrap-nest bird's hoarding drive.</summary>
    public static class RSW_HoardKernel
    {
        public const float RestFloor = 0.4f, TakeableNestClearance = 2f;

        public static bool Eligible(bool enabled, bool aliveOnMap, bool hasHoarderComp, bool awake, bool calm, bool canManipulate,
                                    bool hasFoodNeed, float foodPct, float wantEatPct, bool hasRestNeed, float restPct, bool layingEggNow)
        {
            if (!enabled) return false;
            if (!aliveOnMap) return false;
            if (!hasHoarderComp) return false;
            if (!awake) return false;
            if (!calm) return false;
            if (!canManipulate) return false;
            if (hasFoodNeed && foodPct < wantEatPct) return false;
            if (hasRestNeed && restPct < RestFloor) return false;
            if (layingEggNow) return false;
            return true;
        }

        /// <summary>The nearest spawned, reachable nest within the radius; the first of equals wins. -1 when none. Reachability is asked lazily,
        /// only for a nest the distance rules would take.</summary>
        public static int NearestNest(IList<float> dist, IList<bool> spawned, Func<int, bool> reachable, float radius)
        {
            int best = -1; float bestDist = float.MaxValue;
            for (int i = 0; i < dist.Count; i++)
            {
                if (!spawned[i]) continue;
                if (dist[i] > radius || dist[i] >= bestDist) continue;
                if (!reachable(i)) continue;
                best = i; bestDist = dist[i];
            }
            return best;
        }

        /// <summary>A raiding-flock bird is done once its exit time has passed (vanilla mindState.exitMapAfterTick, -99999 when unset): it
        /// stops hoarding so the vanilla ExitTimedOut node can walk it off the map.</summary>
        public static bool RaidOver(int exitMapAfterTick, int ticksGame) { return exitMapAfterTick >= 0 && ticksGame > exitMapAfterTick; }

        /// <summary>One theft message per map per window, so a flock emptying a shelf is one line, not twenty.</summary>
        public static bool TheftMessageDue(int lastTick, int now, int window) { return lastTick < 0 || now - lastTick >= window; }

        /// <summary>A bird builds only while the map is under the nest cap.</summary>
        public static bool CanAddNest(int existing, int maxPerMap) { return existing < maxPerMap; }

        /// <summary>Nests keep their distance: the nearest existing nest (infinity when there is none) must be at least the spacing away.</summary>
        public static bool SpacingOk(float nearestNestDist, float minSpacing) { return !(nearestNestDist < minSpacing); }

        /// <summary>A free, open, unroofed, reachable cell outside the home area, apart from the other nests (and next to a plant when asked).
        /// The probes are lazy and asked in this order: bounds, open ground, home area, anything on the cell, roof, reach, spacing, plant.</summary>
        public static bool NestCellOk(bool inBounds, Func<bool> openGround, Func<bool> home, Func<bool> occupied, Func<bool> roofed, Func<bool> reachable,
                                      Func<float> nearestNestDist, float minSpacing, bool requirePlantCover, Func<bool> nearPlant)
        {
            if (!inBounds || !openGround()) return false;
            if (home()) return false;
            if (occupied()) return false;
            if (roofed()) return false;
            if (!reachable()) return false;
            if (!SpacingOk(nearestNestDist(), minSpacing)) return false;
            if (requirePlantCover && !nearPlant()) return false;
            return true;
        }

        /// <summary>On the map and not already at the nest. Without stealFromBase, loose scrap only: outside the home area and any storage.
        /// With it (SCRAPNEST_BIRD_BASE_THEFT_1, owner-ruled 2026-10-10) stockpiles, shelves and the home area are fair game and are never
        /// asked. Lazy, in this order.</summary>
        public static bool Takeable(bool spawned, int stackCount, bool hasMap, bool stealFromBase, Func<bool> inHomeArea, Func<bool> inAnyStorage, Func<bool> onStorageBuilding, Func<float> distToNest)
        {
            if (!spawned || stackCount <= 0 || !hasMap) return false;
            if (!stealFromBase && inHomeArea()) return false;
            if (!stealFromBase && inAnyStorage()) return false;
            if (!stealFromBase && onStorageBuilding()) return false;
            if (distToNest() <= TakeableNestClearance) return false;
            return true;
        }
    }

    /// <summary>Granting the voltmaw's and cindermite's ranged ability.</summary>
    public static class RSW_AbilityKernel
    {
        public enum Step { Nothing, MarkGrantedOnly, Grant }

        public static Step Decide(bool granted, bool enabled, bool hasAbility, bool isPawn)
        {
            if (granted || !enabled) return Step.Nothing;
            if (!hasAbility) return Step.MarkGrantedOnly;
            if (!isPawn) return Step.Nothing;
            return Step.Grant;
        }
    }

    /// <summary>The mutagenic norphea's toxin dependence: the need and its hediff stage.</summary>
    public static class RSW_ToxinKernel
    {
        public const float GainPerTick = 0.0001f, SatisfiedAbove = 0.1f, DesireAbove = 0.01f;
        public const int IntervalTicks = 150, TicksPerDay = 60000;
        public const int Satisfied = 0, Desire = 1, Withdrawal = 2;

        public static int Category(float level) { return level > SatisfiedAbove ? Satisfied : level > DesireAbove ? Desire : Withdrawal; }

        public static int HediffStage(int category) { return category == Withdrawal ? 1 : 0; }

        public static float Clamp(float level, float max) { return Math.Min(Math.Max(level, 0f), max); }

        /// <summary>The level after one need interval (unclamped; the engine clamps on set). Frozen: unchanged. Mechanic off: full.
        /// Fed (toxic build-up or a polluted cell): rises; otherwise falls by the def's per-day rate.</summary>
        public static float Next(float level, float max, bool frozen, bool enabled, bool fed, float fallPerDay)
        {
            if (frozen) return level;
            if (!enabled) return max;
            return fed ? level + GainPerTick * IntervalTicks : level - fallPerDay / TicksPerDay * IntervalTicks;
        }
    }

    /// <summary>The fuel-spew ability's cone: the cells a spray from the pawn toward a target reaches (the engine adds the cell tests
    /// that need a map: in bounds, not filled, in range, a shoot line).</summary>
    public static class RSW_SpewKernel
    {
        public struct Cone { public bool Empty; public int AimX, AimZ; public float Heading, HalfAngle; }

        /// <summary>Angle of the vector (dx, dz) from the +x axis in degrees, -180..180 (Vector3.SignedAngle(v, right, up)).</summary>
        public static float AngleOf(int dx, int dz) { return (float)(Math.Atan2(dz, dx) * 180.0 / Math.PI); }

        /// <summary>Shortest signed difference between two angles in degrees, -180..180 (Mathf.DeltaAngle).</summary>
        public static float DeltaAngle(float current, float target)
        {
            float d = target - current;
            d = d - 360f * (float)Math.Floor(d / 360f);
            if (d > 180f) d -= 360f;
            return d;
        }

        /// <summary>The spray is aimed along the pawn-to-target line extended out to the full range; its half angle is set by the width at the
        /// end of that range. A target on the pawn's own cell gives an empty cone.</summary>
        public static Cone ConeFor(int px, int pz, int tx, int tz, float range, float lineWidthEnd)
        {
            Cone c = new Cone();
            if (px == tx && pz == tz) { c.Empty = true; return c; }
            float dist = (float)Math.Sqrt((double)((tx - px) * (tx - px) + (tz - pz) * (tz - pz)));
            float dx = (tx - px) / dist, dz = (tz - pz) / dist;
            c.AimX = (int)Math.Round(px + dx * range);
            c.AimZ = (int)Math.Round(pz + dz * range);
            c.Heading = AngleOf(c.AimX - px, c.AimZ - pz);
            float halfWidth = lineWidthEnd / 2f;
            float aimLen = (float)Math.Sqrt((double)((c.AimX - px) * (c.AimX - px) + (c.AimZ - pz) * (c.AimZ - pz)));
            float hyp = (float)Math.Sqrt(aimLen * aimLen + halfWidth * halfWidth);
            c.HalfAngle = (float)(Math.Asin(halfWidth / hyp) * 180.0 / Math.PI);
            return c;
        }

        /// <summary>Is the cell (offset cx, cz from the pawn) inside the cone's angle?</summary>
        public static bool InCone(Cone c, int cx, int cz) { return Math.Abs(DeltaAngle(AngleOf(cx, cz), c.Heading)) <= c.HalfAngle; }
    }
}
