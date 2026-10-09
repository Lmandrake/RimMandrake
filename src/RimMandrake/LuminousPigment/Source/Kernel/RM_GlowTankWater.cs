// DESIGN_PASS LP-2 (GLOW_TANK_LIQUID_FEED_1). Verse-free kernel of the GlowTank's ocean-water reserve: the tank keeps
// a small reserve measured in ticks of growth, drains it while it runs, and draws one unit of salt or boiling water
// from a FlowWorks liquid net whenever the reserve falls to its refill mark. SelfTest/LuminousPigmentFuzz.cs compiles
// this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.LuminousPigment
{
    public static class RM_GlowTankWater
    {
        public const string SaltWater = "RM_Liquid_SaltWater";
        public const string BoilingWater = "RM_Liquid_BoilingWater";

        // Spec §2.5 Q5 (2026-09-25): salt or boiling only; brine and fresh water do not count.
        public static bool IsOceanLiquid(string defName) { return defName == SaltWater || defName == BoilingWater; }

        // The gate applies only with the setting on AND FlowWorks loaded (card ruling: none needed without it).
        public static bool GateActive(bool settingOn, bool flowWorksPresent) { return settingOn && flowWorksPresent; }

        // Ticks of running one unit buys. unitsPerDay <= 0 = the tank drinks nothing (never parched).
        public static int TicksPerUnit(float unitsPerDay)
        {
            if (unitsPerDay <= 0f) return 0;
            double t = Math.Round(60000.0 / unitsPerDay);
            return t < 1 ? 1 : t >= int.MaxValue ? int.MaxValue : (int)t;
        }

        public static int Drain(int reserve, int elapsed) { return Math.Max(0, reserve - Math.Max(0, elapsed)); }

        // Draw when the reserve has fallen to half a unit, so a tank on a working net never runs dry between checks.
        public static bool WantsDraw(int reserve, int ticksPerUnit) { return ticksPerUnit > 0 && reserve <= ticksPerUnit / 2; }

        // Holds at most two units' worth; saturates instead of wrapping.
        public static int Refill(int reserve, int ticksPerUnit)
        {
            if (ticksPerUnit <= 0) return reserve;
            long cap = 2L * ticksPerUnit, r = (long)Math.Max(0, reserve) + ticksPerUnit;
            if (r > cap) r = cap;
            return r > int.MaxValue ? int.MaxValue : (int)r;
        }

        public static bool Parched(bool gateActive, int ticksPerUnit, int reserve) { return gateActive && ticksPerUnit > 0 && reserve <= 0; }
    }
}
