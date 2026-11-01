using System;
using System.Collections.Generic;

namespace RimMandrake.RustCathedral
{
    // RUSTCATHEDRAL_WORN_BIT_ARC_1. The arc's arithmetic and gates, with no game reference, so the offline fuzz
    // (Source/SelfTest/WornBitFuzz.cs) runs the same code the game does.
    public enum RM_WornBitStage
    {
        None,
        AwaitingHead,
        Refurbishing,
        ReadyForCollection,
        Collected,
        Finished,
        Failed
    }

    public enum RM_WornBitChoice
    {
        None,
        Keep,
        Free,
        LeaveUnfinished
    }

    public static class RM_WornBitKernel
    {
        public const int CalmBandMax = 1;
        public const int MinUnbitWorkers = 2;

        // A colonist's vanilla rate on natural rock: JobDriver_Mine deals 80 damage per 100 ticks at MiningSpeed 1.
        public const float ColonistDigPerTick = 0.8f;

        public static bool CalmEnough(int band) { return band >= 0 && band <= CalmBandMax; }

        /// <summary>One worker's share of one tick. A lone worker, a moving hulk or a hum past the calm bands adds nothing.</summary>
        public static float UnbitDelta(int workersAtIt, float workerSpeed, int band, bool hulkMoving)
        {
            if (workersAtIt < MinUnbitWorkers || hulkMoving || !CalmEnough(band))
            {
                return 0f;
            }
            return workerSpeed / workersAtIt;
        }

        public static int ScaledFee(int baseFee, float wealthFactor)
        {
            float f = wealthFactor < 0.75f ? 0.75f : (wealthFactor > 2f ? 2f : wealthFactor);
            return (int)Math.Round(baseFee * f, MidpointRounding.AwayFromZero);
        }

        public static float WealthFactor(float playerWealth) { return playerWealth / 100000f; }

        /// <summary>Chance of a good haggle from the best Social skill: 0.2 at Social 0, 0.8 at 15 and up.</summary>
        public static float HaggleChance(int socialSkill)
        {
            int s = socialSkill < 0 ? 0 : (socialSkill > 15 ? 15 : socialSkill);
            return 0.2f + 0.04f * s;
        }

        /// <summary>A good haggle takes a quarter off, a failed one puts a quarter on.</summary>
        public static int HaggledFee(int fee, bool success)
        {
            return (int)Math.Round(fee * (success ? 0.75 : 1.25), MidpointRounding.AwayFromZero);
        }

        public static int Scaled(int delta, float multiplier)
        {
            return (int)Math.Round(delta * multiplier, MidpointRounding.AwayFromZero);
        }

        public static float ScaledF(float delta, float multiplier) { return delta * multiplier; }

        /// <summary>Index of the first item short of its count, or -1 when everything is there.</summary>
        public static int FirstShort(IList<int> need, IList<int> have)
        {
            for (int i = 0; i < need.Count; i++)
            {
                if (have[i] < need[i])
                {
                    return i;
                }
            }
            return -1;
        }

        public static float MaintenanceLeft(int nowTick, int lastServiceTick, int intervalTicks)
        {
            if (intervalTicks <= 0)
            {
                return 1f;
            }
            float left = 1f - (float)(nowTick - lastServiceTick) / intervalTicks;
            return left < 0f ? 0f : (left > 1f ? 1f : left);
        }

        public static bool KeptMayDig(bool maintenanceOn, int nowTick, int lastServiceTick, int intervalTicks)
        {
            return !maintenanceOn || MaintenanceLeft(nowTick, lastServiceTick, intervalTicks) > 0f;
        }

        public static bool FavourReady(int nowTick, int lastFavourTick, int cooldownTicks)
        {
            return lastFavourTick < 0 || nowTick - lastFavourTick >= cooldownTicks;
        }

        public static bool SelfBoreDue(int nowTick, int lastBoreTick, int intervalTicks)
        {
            return nowTick - lastBoreTick >= intervalTicks;
        }

        /// <summary>The half-way stop: the first tick the work crosses half with no choice taken holds there.</summary>
        public static bool ChoiceDue(float progress, float total, RM_WornBitChoice choice)
        {
            return choice == RM_WornBitChoice.None && progress >= total * 0.5f;
        }
    }
}
