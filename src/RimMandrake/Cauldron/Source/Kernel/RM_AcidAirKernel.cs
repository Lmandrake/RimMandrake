using System;

namespace RimMandrake.Cauldron
{
    /// <summary>VEXXITH_USES_1: the Verse-free rules of ambient acid, compiled into the offline selftest.
    /// Numbers are PROVISIONAL, owed to DESIGN_MATERIALS_REVIEW_1.</summary>
    public static class RM_AcidAirKernel
    {
        public const int IntervalTicks = 2500;           // one in-game hour
        public const float PawnBurnChance = 0.25f;       // about six points a day under open sky, unsuited
        public const float PawnBurnDamage = 1f;
        public const int HullSamplesPerInterval = 12;    // a large ship is bitten here and there, not all at once
        public const float HullBurnDamage = 1f;
        public const int HullFloorPercent = 30;           // the air weakens a ship; it never takes it apart. Whole percent: 0.3f x 100 ceils to 31

        /// <summary>Chance of a burn this hour. A sealed suit scores by whichever sealing stat is better, so a vacsuit and
        /// helmet (VacuumResistance 1.01) are safe and a gas mask (ToxicEnvironmentResistance) is partial.</summary>
        public static float BurnChance(float factor, float vacuumResistance, float toxicEnvResistance)
        {
            float seal = Math.Max(0f, Math.Min(1f, Math.Max(vacuumResistance, toxicEnvResistance)));
            return Math.Max(0f, PawnBurnChance * factor * (1f - seal));
        }

        /// <summary>Roofed ground is out of the air. Native animals have lived in it all their lives.</summary>
        public static bool PawnExposed(bool dead, bool spawned, bool immuneToConditions, bool roofed, bool animal, bool nativeAnimal)
        {
            return !dead && spawned && !immuneToConditions && !roofed && !(animal && nativeAnimal);
        }

        /// <summary>Stops at the floor so an unattended ship is weak, never gone.</summary>
        public static bool HullBurns(bool enabled, bool lined, bool onShip, bool exposed, int hitPoints, int maxHitPoints)
        {
            return enabled && !lined && onShip && exposed && hitPoints * 100 > maxHitPoints * HullFloorPercent;
        }
    }
}
