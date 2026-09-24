using UnityEngine;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// Every shipped number in one place. BactaSettings' defaults are read from here, so
    /// "defaults = shipped behavior" is enforced by construction rather than by discipline.
    /// </summary>
    public static class BactaTuning
    {
        /// <summary>How often the mechanism runs. Never per-tick: one aggregate pass.</summary>
        public const int ImmersionIntervalTicks = 250;

        /// <summary>Ticks in a day, for the per-day rates below.</summary>
        public const int TicksPerDay = 60000;

        /// <summary>Ticks in an hour, for the revival window below.</summary>
        public const int TicksPerHour = TicksPerDay / 24;

        /// <summary>
        /// BACTA_REVIVAL_MECHANIC_1, owner ruling verbatim: "works on dead bodies IF retrieved
        /// within a few hours". Hours since death a corpse stays eligible for the tank.
        /// </summary>
        public const float RevivalWindowHours = 6f;

        /// <summary>
        /// Severity healed per day, per fresh injury. A hospital bed with good medicine
        /// closes an average wound over days; 30/day means a severity-12 gunshot is gone
        /// in about ten in-game hours.
        /// </summary>
        public const float WoundHealPerDay = 30f;

        /// <summary>
        /// Severity removed per day from a permanent/scarred injury. Deliberately an order
        /// of magnitude slower than fresh healing: erasing an old scar is days of floating,
        /// not hours.
        /// </summary>
        public const float ScarHealPerDay = 2.4f;

        /// <summary>
        /// Extra immunity gained per day, added on top of the pawn's normal immunity gain,
        /// for diseases medicine could treat. 0.30 turns most survivable infections into
        /// reliably survivable ones without making untendable ones matter less.
        /// </summary>
        public const float ImmunityGainPerDay = 0.30f;

        /// <summary>Bacta units consumed per day while a pawn is immersed and being healed.</summary>
        public const float FluidCostPerDay = 5f;

        /// <summary>
        /// Tend quality applied to fresh, tendable wounds so bleeding stops early. Below a
        /// glitterworld doctor with glitterworld medicine, above a nervous teenager with cloth.
        /// </summary>
        public const float TendQuality = 0.85f;

        /// <summary>The fluid's colour, for the fill quad drawn over the suspended pawn.</summary>
        public static readonly Color FluidColor = new Color32(123, 220, 255, 75);
    }
}
