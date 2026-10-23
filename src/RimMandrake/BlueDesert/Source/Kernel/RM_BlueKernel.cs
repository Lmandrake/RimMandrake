// Verse-free kernel of the Blue Desert's small mechanics: the blue-ice heat sink, the thaw roll, the vhaulk's detonation gate and
// departure, the plant charge, the ablation timeline, and the weighted pick several of them share.
// SelfTest/BlueDesertFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.BlueDesert
{
    public static class RM_BlueKernel
    {
        public const int TicksPerDay = 60000;
        public const int TicksPerHour = 2500;

        // ── weighted pick (Verse's TryRandomElementByWeight): weights <= 0 are never chosen; false when nothing has weight ──
        public static int PickWeighted(float[] weights, int n, double roll01)
        {
            double total = 0;
            for (int i = 0; i < n; i++) total += Math.Max(0f, weights[i]);
            if (total <= 0) return -1;
            double r = roll01 * total;
            for (int i = 0; i < n; i++)
            {
                double w = Math.Max(0f, weights[i]);
                if (w <= 0) continue;
                if (r < w) return i;
                r -= w;
            }
            for (int i = n - 1; i >= 0; i--) if (weights[i] > 0f) return i;
            return -1;
        }

        // ── cold sink ──
        public static float ColdPerBlock(float coldPerBlock, float capacityFactor) { return Math.Max(1f, coldPerBlock * capacityFactor); }

        public static int ClarityStage(bool hasFuelComp, float fuelPercent)
        {
            if (!hasFuelComp) return 2;
            if (fuelPercent > 0.5f) return 0;
            return fuelPercent > 0.1f ? 1 : 2;
        }

        // The rack absorbs the heat the room would shed, but never more than the ice left holds. tempChange is the room's
        // (<= 0) cooling step; returns the possibly scaled step, the ice blocks used and whether the rack worked at all.
        public static bool Absorb(float tempChange, int cellCount, float fuel, float coldPerBlock, out float scaledChange, out float blocks)
        {
            scaledChange = 0f; blocks = 0f;
            if (tempChange >= 0f || Math.Abs(tempChange) < 1e-6f) return false;
            float absorbed = -tempChange * cellCount;
            float available = fuel * coldPerBlock;
            scaledChange = tempChange;
            if (absorbed > available)
            {
                scaledChange = tempChange * (available / absorbed);
                absorbed = available;
            }
            blocks = absorbed / coldPerBlock;
            return true;
        }

        // ── thaw roll ──
        public static bool ThawCounts(ref int blocksSinceRoll, int blocksPerRoll)
        {
            blocksSinceRoll++;
            if (blocksSinceRoll < Math.Max(1, blocksPerRoll)) return false;
            blocksSinceRoll = 0;
            return true;
        }
        public static int ThawStack(int rolled, int stackLimit) { return Math.Max(1, Math.Min(Math.Max(1, stackLimit), rolled)); }

        // ── detonation gate (the vhaulk cistern) ──
        public static bool IsHeatKill(bool hasDamage, bool damageIsHeat, bool hasCulprit, bool culpritIsHeat) { return (hasDamage && damageIsHeat) || (hasCulprit && culpritIsHeat); }
        public static bool Detonates(bool detonationsOn, bool empTriggered, bool heatGateOn, bool heatKill) { return detonationsOn && (empTriggered || !heatGateOn || heatKill); }
        public static bool EmpTrap(bool detonationsOn, bool trapOn, bool dead, bool destroyed, bool isEmp) { return detonationsOn && trapOn && !dead && !destroyed && isEmp; }
        public static bool IsEmp(bool listEmpty, bool defIsVanillaEmp, bool defInList) { return listEmpty ? defIsVanillaEmp : defInList; }
        public static bool PartKills(bool detonationsOn, bool alive, bool partMatches, bool partMissing) { return detonationsOn && alive && partMatches && partMissing; }

        // ── plant charge: two warm long-ticks in a row detonate it; 1 = crack cue, 2 = detonate ──
        public static int ChargeStep(ref int warmInARow, bool enabled, bool hasMap, bool warm)
        {
            if (!enabled) { warmInARow = 0; return 0; }
            if (!hasMap) return 0;
            if (warm)
            {
                warmInARow++;
                return warmInARow >= 2 ? 2 : 1;
            }
            warmInARow = 0;
            return 0;
        }
        public static float WeatherCommonality(bool on, float authored) { return on ? authored : 0f; }

        // ── vhaulk walk-off ──
        public static int DepartTick(int now, float stayDaysRoll, float factor) { return now + (int)Math.Round(stayDaysRoll * Math.Max(0.1f, factor) * TicksPerDay); }
        // 0 = nothing, 1 = reset the departing flag then try to leave, 2 = try to leave
        public static int DepartAction(bool departOn, int departTick, int now, bool hashDue, bool departing, bool jobExitsMap)
        {
            if (!(departOn && departTick >= 0 && now >= departTick && hashDue)) return 0;
            if (departing && !jobExitsMap) return 1;
            return departing ? 0 : 2;
        }

        // ── ablation emergence ──
        public static int SilhouetteTick(int now, float hoursRoll, float pace) { return now + (int)Math.Round(hoursRoll * TicksPerHour * Math.Max(0.1f, pace)); }
        public static int ExposureTick(int silhouetteTick, float hoursRoll, float pace) { return silhouetteTick + (int)Math.Round(hoursRoll * TicksPerHour * Math.Max(0.1f, pace)); }
        // One rare tick of the marker: returns the new stage (0 hidden, 1 silhouette, 2 exposed). Both steps may happen in one tick.
        public static int AblationStage(int stage, int now, int silhouetteTick, int exposureTick, out bool callScavengers, out bool expose)
        {
            callScavengers = false; expose = false;
            if (stage == 0 && now >= silhouetteTick) { stage = 1; callScavengers = true; }
            if (stage == 1 && now >= exposureTick) { stage = 2; expose = true; }
            return stage;
        }
    }
}
