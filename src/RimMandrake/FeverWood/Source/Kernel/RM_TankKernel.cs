// Verse-free kernel of the Sekkulaath prison tank and the display tank (FEVERWOOD_DIANOGA_PRISON_1 /
// FEVERWOOD_BROOD_RANSOM_1 s5): the check gate, neglect clock, the two escape rolls' probabilities, the occupied
// flag's transitions and the routing of a breach. RM_CompCapturedSpecimen calls these; SelfTest/FeverWoodFuzz.cs
// compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.FeverWood
{
    public static class RM_TankKernel
    {
        public const int CheckIntervalTicks = 2500; // 1 in-game hour
        public const float TicksPerDay = 60000f;
        public const float MinRiskMultiplier = 0.01f;

        // CompTick: inert while the master toggle is off, once emptied, or while a town's display tank (the town feeds it);
        // otherwise it acts once an hour.
        public static bool RunsThisTick(bool tankEnabled, bool occupied, bool foreignDisplay, int ticksGame)
        {
            if (!tankEnabled || !occupied || foreignDisplay) return false;
            return ticksGame % CheckIntervalTicks == 0;
        }

        // The unfed clock. Fed resets it; the first unfed hour starts it. Returns true when the neglect MTB roll is due:
        // the tank has been unfed for at least thresholdDays.
        public static bool NeglectStep(ref int unfedSinceTick, bool fed, int now, float thresholdDays)
        {
            if (fed)
            {
                unfedSinceTick = -1;
                return false;
            }
            if (unfedSinceTick < 0)
            {
                unfedSinceTick = now;
                return false;
            }
            float daysUnfed = (now - unfedSinceTick) / TicksPerDay;
            return !(daysUnfed < thresholdDays);
        }

        public static float RiskMultiplier(float setting) { return Math.Max(MinRiskMultiplier, setting); }

        // Lower multiplier = shorter MTB = more escape-prone.
        public static float NeglectMtbDays(float baseMtbDays, float riskSetting) { return baseMtbDays * RiskMultiplier(riskSetting); }

        // Lower multiplier = higher per-hit chance.
        public static float DamageEscapeChance(float chancePerHit, float riskSetting)
        {
            float c = chancePerHit / RiskMultiplier(riskSetting);
            return c < 0f ? 0f : c > 1f ? 1f : c;
        }

        public static float LostFraction(int hitPoints, int maxHitPoints)
        {
            float maxHp = maxHitPoints > 0 ? maxHitPoints : 1;
            return 1f - (float)hitPoints / maxHp;
        }

        // A hit only risks an escape past the damage threshold, while enabled and occupied.
        public static bool DamageArmed(bool tankEnabled, bool occupied, int hitPoints, int maxHitPoints, float thresholdFraction)
        {
            if (!tankEnabled || !occupied) return false;
            return !(LostFraction(hitPoints, maxHitPoints) < thresholdFraction);
        }

        // Window handed to the production MTB roll: a full hour, or the time since last produced if less.
        public static int ProductionWindow(int now, int lastProduced)
        {
            int elapsed = now - lastProduced;
            return elapsed >= CheckIntervalTicks ? CheckIntervalTicks : elapsed;
        }

        // ---- occupied ---------------------------------------------------------------------------------
        // Freeing a display tank's young is idempotent: an empty tank (or no map) does nothing.
        public static bool TryFreeDisplay(ref bool occupied, bool hasMap)
        {
            if (!occupied || !hasMap) return false;
            occupied = false;
            return true;
        }

        // "Return to the deep" needs an occupied, spawned tank.
        public static bool TryRelease(ref bool occupied, bool spawned)
        {
            if (!occupied || !spawned) return false;
            occupied = false;
            return true;
        }

        public static bool CountsInTally(bool occupied) { return occupied; }

        public static int GiftRolls(int rolls) { return Math.Max(1, rolls); }

        // Escape: a foreign display tank under the brood ransom breaks open and frees its young (no hostile escapee).
        public static bool EscapeFreesDisplayYoung(bool foreignDisplay, bool ransomOn) { return foreignDisplay && ransomOn; }

        // A tank broken outright (no escape roll got there first) still lets a display tank's young out.
        public static bool DestroyFreesDisplayYoung(bool killFinalize, bool occupied, bool displayProps, bool hasPreviousMap,
            bool hasOwner, bool ownerIsPlayer, bool ransomOn, bool tankOn)
        {
            return killFinalize && occupied && displayProps && hasPreviousMap && hasOwner && !ownerIsPlayer && ransomOn && tankOn;
        }

        public static bool IsForeignDisplay(bool displayProps, bool hasOwner, bool ownerIsPlayer) { return displayProps && hasOwner && !ownerIsPlayer; }
    }
}
