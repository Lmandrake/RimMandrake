// Verse-free kernel of Titanic Creatures: the size-tier ladder, the force-in/force-out override, the Large Pawns footprint size, the
// sub-linear butcher yield, the crush decision and damage, the roof rule, and the T3 corpse-site pool arithmetic (daily spoilage and
// per-session harvest). TitanicTierUtility, YieldCurveUtility, CrushTableUtility, TitanicWakeProcessor, LargePawnsBridge and
// Building_TitanicCorpseSite call these with the same expressions; SelfTest/TitanicFuzz.cs compiles this file alone.
// Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks the self-test build, which is the guard rail).
// Tiers are ints (None 0, T1 1, T2 2, T3 3) so they order with the same comparisons the enum TitanicTier gives.
using System;
using System.Collections.Generic;

namespace RimMandrake.TitanicCreatures
{
    public static class RM_TitanicKernel
    {
        public const int None = 0, T1 = 1, T2 = 2, T3 = 3;
        /// <summary>RM_TitanicExtension.forceEnabled: unset (auto), true (force in), false (force out).</summary>
        public const int ForceAuto = 0, ForceIn = 1, ForceOut = -1;

        // PROVISIONAL (BENCH draft, not owner-ruled): crush damage per pass, before the player's multiplier.
        public const float CrushDamageLight = 20f;
        public const float CrushDamageHeavy = 60f;
        public const int TicksPerDay = 60000;

        /// <summary>The player-facing tier ladder is only meaningful when 0 &lt; T1 &lt; T2 &lt; T3.</summary>
        public static bool ThresholdsValid(float t1, float t2, float t3)
        {
            // B3.19 / C3.6 / D3.3: an infinite or NaN rung is never a ladder (NaN fails every comparison already; inf T3 did not).
            return Finite(t1) && Finite(t2) && Finite(t3) && t1 > 0f && t1 < t2 && t2 < t3;
        }

        public static bool Finite(float v) => !float.IsNaN(v) && !float.IsInfinity(v);

        /// <summary>HUGETHINGS_SETTINGS_HARDENING_1 (B3.19): a Scribe-loaded or edited float setting, forced finite and into its slider
        /// range; a NaN/infinite value falls back to the shipped default (itself clamped, so a bad default cannot escape either).</summary>
        public static float SaneSetting(float v, float min, float max, float fallback)
        {
            if (!Finite(v)) v = fallback;
            if (!Finite(v)) v = min;
            return Clamp(v, min, max);
        }

        /// <summary>Integer setting into its slider range.</summary>
        public static int SaneSetting(int v, int min, int max)
        {
            return v < min ? min : (v > max ? max : v);
        }

        /// <summary>Def-level: could any pawn of this race ever be tiered (decides the comp auto-attach).</summary>
        public static bool DefQualifies(float baseBodySize, float t1, int force)
        {
            if (force == ForceOut) return false;
            if (force == ForceIn) return true;
            return baseBodySize >= t1;
        }

        /// <summary>TITAN_WAKE_FIXES_1 (B3.18 / C3.4): Pawn.BodySize is lifestage.bodySizeFactor x baseBodySize, so a race qualifies on its
        /// base times the LARGEST factor any of its life stages reaches (a factor below 1 never shrinks the test below the base).</summary>
        public static bool DefQualifies(float baseBodySize, float maxLifeStageFactor, float t1, int force)
        {
            float f = Finite(maxLifeStageFactor) && maxLifeStageFactor > 1f ? maxLifeStageFactor : 1f;
            return DefQualifies(baseBodySize * f, t1, force);
        }

        /// <summary>TITAN_WAKE_FIXES_1 (B3.6): a multi-cell thing is registered in every cell it covers, so a footprint scan sees it once per
        /// covered cell. Each thing comes back once, in first-seen order, so one titan step strikes it once.</summary>
        public static List<T> UniqueInOrder<T>(IEnumerable<IEnumerable<T>> cells) where T : class
        {
            var seen = new HashSet<T>();
            var outList = new List<T>();
            foreach (IEnumerable<T> cell in cells)
            {
                if (cell == null) continue;
                foreach (T t in cell)
                    if (t != null && seen.Add(t)) outList.Add(t);
            }
            return outList;
        }

        /// <summary>Runtime tier of one pawn: bodySize ladder, force-out wins, force-in floors at T1.</summary>
        public static int TierFor(float bodySize, float t1, float t2, float t3, int force)
        {
            if (force == ForceOut) return None;
            int tier;
            if (bodySize >= t3) tier = T3;
            else if (bodySize >= t2) tier = T2;
            else if (bodySize >= t1) tier = T1;
            else tier = None;
            if (tier == None && force == ForceIn) tier = T1;
            return tier;
        }

        /// <summary>Tier a body size would reach if it qualified at all (never None): what the Large Pawns footprint is projected from.</summary>
        public static int QualifiedTier(float bodySize, float t2, float t3)
        {
            if (bodySize >= t3) return T3;
            if (bodySize >= t2) return T2;
            return T1;
        }

        /// <summary>Large Pawns footprint edge for a tier (its hard ceiling is 4).</summary>
        public static int FootprintSize(int tier)
        {
            switch (tier)
            {
                case T3: return 4;
                case T2: return 3;
                default: return 2;
            }
        }

        /// <summary>The Large Pawns size-override row for a def that carries an RM_TitanicExtension with forceEnabled set (force-in always qualifies;
        /// a force-in race below the T1 floor is T1).</summary>
        public static int OverrideFootprint(float baseBodySize, float t1, float t2, float t3, int force)
        {
            if (force == ForceOut) return 1;
            return FootprintSize(QualifiedTier(baseBodySize, t2, t3));
        }

        /// <summary>Unity Mathf.Clamp semantics (min wins when min &gt; max).</summary>
        public static float Clamp(float v, float min, float max)
        {
            if (v < min) v = min;
            else if (v > max) v = max;
            return v;
        }

        /// <summary>Yield multiplier for a T1/T2 corpse: sqrt(floor / bodySize), kept in [minFactor, 1].</summary>
        public static float SubLinearFactor(float bodySize, float floor, float minFactor)
        {
            float b = Math.Max(bodySize, floor);
            return Clamp((float)Math.Sqrt(floor / b), minFactor, 1f);
        }

        /// <summary>The tier floor the yield curve measures against (T1 floor for T1, else T2's).</summary>
        public static float YieldFloor(int tier, float t1, float t2)
        {
            return tier == T1 ? t1 : t2;
        }

        /// <summary>One crush-table row against a tier: unlisted things never reach here (they are protected by default).</summary>
        public static bool CrushAllowed(int tier, bool crushable, int minTier)
        {
            return tier != None && crushable && tier >= minTier;
        }

        /// <summary>Crush damage per pass for a non-destroyed crushable. A bigger tier never hits softer than a smaller one.</summary>
        public static float CrushDamage(int tier, float multiplier)
        {
            return (tier >= T2 ? CrushDamageHeavy : CrushDamageLight) * multiplier;
        }

        /// <summary>T3 destroys a crushable Building outright; everything else crushable takes damage.</summary>
        public static bool DestroysOutright(int tier, bool isBuilding)
        {
            return tier == T3 && isBuilding;
        }

        /// <summary>Thin roofs are holed from T2; a thick roof (overhead mountain) is never removed.</summary>
        public static bool HolesRoof(int tier, bool hasRoof, bool thick)
        {
            return tier >= T2 && hasRoof && !thick;
        }

        /// <summary>Rubble trail: every tiered pawn leaves a chance of filth per cell.</summary>
        public static bool LeavesFilth(int tier, bool rolledUnderChance)
        {
            return tier >= T1 && rolledUnderChance;
        }

        /// <summary>Units lost to one day of spoilage: a fixed fraction of what is left, always at least one while anything is left.</summary>
        public static int SpoilLoss(int remaining, float perDay)
        {
            if (remaining <= 0) return 0;
            int loss = (int)Math.Ceiling(remaining * perDay);
            return Math.Min(remaining, Math.Max(0, loss));
        }

        /// <summary>Units one work session pulls from the pool.</summary>
        public static int HarvestTake(int remaining, int perSession)
        {
            return Math.Max(0, Math.Min(remaining, perSession));
        }
    }
}
