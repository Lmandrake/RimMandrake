using System;

namespace RimMandrake.LanternDeeps
{
    /// <summary>
    /// The Sippers' and the aurora's share of a light, with no Verse type in it so the offline fuzz compiles THIS file.
    /// Both reach the light through the shared light ledger (LIGHT_LEDGER_ONE_1, design/RimMandrake/light_ledger_design.md):
    /// the aurora as the "ld.aurora" multiplier, the sippers as the "ld.sipper" multiplier. The ledger composes them with
    /// every other effect, so this no longer guesses whether somebody else wrote the radius since (the old SipperLedger did,
    /// by tolerance).
    /// </summary>
    public static class SipperKernel
    {
        /// <summary>Sippers never drink a light below this fraction of its scaled radius.</summary>
        public const float Floor = 0.25f;

        /// <summary>Cells of radius <paramref name="sippers"/> take from a light whose radius before any subtraction is <paramref name="scaled"/>.</summary>
        public static float Take(float scaled, int sippers, float cellsPerSipper)
        {
            if (sippers <= 0 || scaled <= 0f) return 0f;
            return Math.Min(scaled * (1f - Floor), sippers * Math.Max(0f, cellsPerSipper));
        }

        /// <summary>
        /// The sippers' share as a MULTIPLIER on the light ("mul:ld.sipper"): <see cref="Take"/> as a fraction of the radius
        /// it was taken from. A proportion, not a fixed number of cells, so when something else shrinks the light between
        /// passes (the aurora ending) the floor still holds and the light never goes out (the fuzz caught a subtraction
        /// sized against the storm's radius blacking a lamp out for up to a pass).
        /// </summary>
        public static float Factor(float scaled, int sippers, float cellsPerSipper)
        {
            if (scaled <= 0f) return 1f;
            return 1f - Take(scaled, sippers, cellsPerSipper) / scaled;
        }

        /// <summary>The aurora's multiplier: its glowMultiplier while it storms, nothing otherwise.</summary>
        public static float AuroraFactor(bool on, float multiplier)
        {
            return on ? multiplier : 1f;
        }
    }
}
