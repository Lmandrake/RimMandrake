using System;

namespace RimMandrake.DivingInteraction
{
    public enum RM_GardenOffenseKind
    {
        Harvest,
        Kill,
        HeatDamage,
        DrillAgitation,
    }

    /// <summary>
    /// The Chill garden-defense scoring and cooldown arithmetic, with no Verse or UnityEngine type in it so the offline fuzz
    /// (Source/SelfTest/DivingFuzz.cs, `python3 src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py`) compiles THIS
    /// file and drives the code the game runs. RM_MapComponent_ChillGardenDefense calls it and then plays the effect it
    /// names; nothing here is a copy. A `using Verse;` landing in this file breaks the selftest build.
    /// </summary>
    public static class RM_GardenDefenseKernel
    {
        public const float HarvestWeight = 0.5f;
        public const float KillWeight = 4f;
        public const float HeatWeight = 4f;
        public const float DrillAgitationWeight = 1f;

        public const float Tier1Threshold = 4f;
        public const float Tier2Threshold = 16f;
        public const float AgitationTier1Threshold = 4f;
        public const float TrailThresholdDiscount = 0.35f;

        public const int Tier1CooldownTicks = 2500;
        public const int Tier2CooldownTicks = 60000;
        public const int AgitationCooldownTicks = 2500;

        public enum Outcome { None, Tier1Arc, Tier2Wake }

        /// <summary>The scalar state RM_MapComponent_ChillGardenDefense Scribes (names unchanged there).</summary>
        public struct State
        {
            public float offenseScore;
            public float agitationScore;
            public int tier1CooldownUntilTick;
            public int tier2CooldownUntilTick;
            public int agitationCooldownUntilTick;

            public static State Fresh()
            {
                return new State { tier1CooldownUntilTick = -1, tier2CooldownUntilTick = -1, agitationCooldownUntilTick = -1 };
            }
        }

        public static float WeightFor(RM_GardenOffenseKind kind)
        {
            switch (kind)
            {
                case RM_GardenOffenseKind.Harvest:
                    return HarvestWeight;
                case RM_GardenOffenseKind.Kill:
                    return KillWeight;
                case RM_GardenOffenseKind.HeatDamage:
                    return HeatWeight;
                default:
                    return 0f;
            }
        }

        public static float AdjustedThreshold(float baseThreshold, float trailDensity)
        {
            return baseThreshold * (1f - TrailThresholdDiscount * trailDensity);
        }

        /// <summary>One offense (Harvest/Kill/HeatDamage). Updates the score and cooldowns and names the effect to play.</summary>
        public static Outcome Offense(ref State s, RM_GardenOffenseKind kind, int now, float trailDensity)
        {
            s.offenseScore += WeightFor(kind);

            if (s.offenseScore >= AdjustedThreshold(Tier2Threshold, trailDensity) && now >= s.tier2CooldownUntilTick)
            {
                s.tier2CooldownUntilTick = now + Tier2CooldownTicks;
                s.tier1CooldownUntilTick = now + Tier1CooldownTicks; // the wake already IS the warning; don't also arc on the same breach
                s.offenseScore = 0f;
                return Outcome.Tier2Wake;
            }
            if (s.offenseScore >= AdjustedThreshold(Tier1Threshold, trailDensity) && now >= s.tier1CooldownUntilTick)
            {
                s.tier1CooldownUntilTick = now + Tier1CooldownTicks;
                s.offenseScore = 0f;
                return Outcome.Tier1Arc;
            }
            return Outcome.None;
        }

        /// <summary>One drill agitation. Its own pool and cooldown.</summary>
        public static bool Agitation(ref State s, int now, float trailDensity)
        {
            s.agitationScore += DrillAgitationWeight;
            if (s.agitationScore >= AdjustedThreshold(AgitationTier1Threshold, trailDensity) && now >= s.agitationCooldownUntilTick)
            {
                s.agitationCooldownUntilTick = now + AgitationCooldownTicks;
                s.agitationScore = 0f;
                return true;
            }
            return false;
        }
    }
}
