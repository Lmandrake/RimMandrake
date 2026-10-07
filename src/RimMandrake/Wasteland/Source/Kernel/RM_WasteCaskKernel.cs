// Verse-free kernel of the waste cask and the sealed cask bay (RM_WasteCaskBay.cs): breach, leak gating and pacing,
// the bay's seal charge / internal heat step, launch safety and the ship check. The comps call these with the same
// expressions; SelfTest/WastelandFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Wasteland
{
    public enum LaunchVerdict { Safe = 0, NoPower = 1, LowIntegrity = 2, TooHot = 3 }

    public enum ShipVerdict { Safe = 0, UnsafeBay = 1, LooseCask = 2 }

    public static class RM_WasteCaskKernel
    {
        // Unity's Mathf.RoundToInt is (int)Math.Round(f): banker's rounding.
        public static int RoundToInt(float f) { return (int)Math.Round(f); }
        public static float Lerp(float a, float b, float t) { t = t < 0f ? 0f : (t > 1f ? 1f : t); return a + (b - a) * t; }

        // ---- the cask ------------------------------------------------------------------------
        public static float StoredDose(float storedDose) { return Math.Max(0f, storedDose); }

        // Below the leak fraction of max hit points, with dose left.
        public static bool Breached(bool useHitPoints, int hitPoints, int maxHitPoints, float leakHpFraction, float storedDose)
        {
            return useHitPoints && hitPoints < maxHitPoints * leakHpFraction && StoredDose(storedDose) > 0f;
        }

        // A breached cask leaks unless a CONTAINED bay holds it.
        public static bool CaskLeaking(bool spawned, bool breached, bool wastelandOn, bool leaksOn, bool inBay, bool bayContained)
        {
            if (!spawned || !breached || !wastelandOn || !leaksOn) return false;
            return !inBay || !bayContained;
        }

        public static bool LeakDue(int nextLeakTick, int now) { return nextLeakTick < 0 || now >= nextLeakTick; }

        public static float DoseAfterLeak(float storedDose, float dosePerLeak) { return Math.Max(0f, StoredDose(storedDose) - dosePerLeak); }

        public static int PollutionCells(int leakPollutionCells, float severity) { return Math.Max(1, RoundToInt(leakPollutionCells * severity)); }
        public static int GasAmount(int leakGasAmount, float severity) { return RoundToInt(leakGasAmount * severity); }

        // A destroyed cask with dose left bursts: 4x pollution (at least 4 cells) and 3x gas.
        public static bool BurstsOnKill(bool killed, bool hadMap, float storedDose, bool wastelandOn, bool leaksOn)
        {
            return killed && hadMap && StoredDose(storedDose) > 0f && wastelandOn && leaksOn;
        }
        public static int BurstCells(int leakPollutionCells, float severity) { return Math.Max(4, RoundToInt(leakPollutionCells * 4 * severity)); }
        public static int BurstGas(int leakGasAmount, float severity) { return RoundToInt(leakGasAmount * 3 * severity); }

        // Reburial needs diggable ground with no building on it.
        public static bool CanRebury(bool terrainKnown, bool diggable, bool hasEdifice) { return terrainKnown && diggable && !hasEdifice; }

        // ---- the bay -------------------------------------------------------------------------
        public static float HpFraction(int hitPoints, int maxHitPoints) { return maxHitPoints > 0 ? hitPoints / (float)maxHitPoints : 1f; }
        public static float SealIntegrity(float sealCharge, float hpFraction) { return Math.Min(sealCharge, hpFraction); }
        public static bool Contained(float sealIntegrity, float leakThreshold) { return sealIntegrity >= leakThreshold; }

        // Powered: regenerate (cap 1). Unpowered: drain (floor 0).
        public static float NextCharge(float sealCharge, bool powered, float regenPerRare, float drainPerRare)
        {
            return powered ? Math.Min(1f, sealCharge + regenPerRare) : Math.Max(0f, sealCharge - drainPerRare);
        }

        // Heat the casks would reach, cooled while powered.
        public static float HeatTarget(float rawTarget, bool powered, float poweredHeatFactor) { return powered ? rawTarget * poweredHeatFactor : rawTarget; }
        public static float NextHeat(float internalHeat, float heatTarget) { return Lerp(internalHeat, heatTarget, 0.1f); }
        public static bool PushesHeat(float internalHeat) { return internalHeat > 1f; }
        public static float HeatPushed(float internalHeat) { return internalHeat * 0.5f; }

        public static bool BayLeaking(bool wastelandOn, bool leaksOn, int caskCount, float totalDose, bool contained)
        {
            return wastelandOn && leaksOn && caskCount > 0 && totalDose > 0f && !contained;
        }

        // Processing: progress per rare tick; completes (and resets) at 1.
        public static float ProcessProgress(float progress, float perDay, int tickRareInterval, int ticksPerDay)
        {
            return progress + perDay * tickRareInterval / (float)ticksPerDay;
        }
        public static bool ProcessDone(float progress) { return progress >= 1f; }
        public static int ProcessedAmount(float milkAmount, float outputFactor, int stackLimit)
        {
            int amount = Math.Max(1, RoundToInt(milkAmount * outputFactor));
            return Math.Min(amount, stackLimit);
        }

        public static int Capacity(int sizeX, int sizeZ, int maxItemsInCell) { return sizeX * sizeZ * Math.Max(1, maxItemsInCell); }
        public static int PerCell(int setting) { return Math.Max(1, Math.Min(6, setting)); }

        // ---- launch safety --------------------------------------------------------------------
        public static LaunchVerdict LaunchSafety(int caskCount, bool powered, float sealIntegrity, float launchIntegrity,
                                                 float internalHeat, float launchHeatLimit)
        {
            if (caskCount == 0) return LaunchVerdict.Safe;
            if (!powered) return LaunchVerdict.NoPower;
            if (sealIntegrity < launchIntegrity) return LaunchVerdict.LowIntegrity;
            if (internalHeat > launchHeatLimit) return LaunchVerdict.TooHot;
            return LaunchVerdict.Safe;
        }

        // The ship check: any aboard bay that is unsafe, else any aboard cask outside a bay.
        public static ShipVerdict CheckShip(IEnumerable<LaunchVerdict> aboardBays, int looseCasksAboard, out LaunchVerdict firstBad)
        {
            firstBad = LaunchVerdict.Safe;
            foreach (LaunchVerdict v in aboardBays)
            {
                if (v != LaunchVerdict.Safe) { firstBad = v; return ShipVerdict.UnsafeBay; }
            }
            return looseCasksAboard > 0 ? ShipVerdict.LooseCask : ShipVerdict.Safe;
        }
    }
}
