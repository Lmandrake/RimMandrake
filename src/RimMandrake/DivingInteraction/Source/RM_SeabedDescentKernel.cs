// SEABED_DESCENT_ASCENT_1. Verse-free kernel of the depth fuel a gravship pays to cross between the surface and the
// sea-floor layer (RM_SeabedLayer). The vanilla pilot console prices a cross-layer flight as the layer connection's
// fuelCost plus distance on the destination layer (GravshipUtility.TryGetPathFuelCost); our surface<->floor
// connection costs 0 because one number cannot know the depth. This kernel is the per-depth part, and it is the
// SAME both ways: descending to a floor tile and climbing back from it pay for the water column over that floor.
// SelfTest/DivingFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.DivingInteraction
{
    public static class RM_SeabedDescentKernel
    {
        public const float DefaultFuelPerMeter = 0.2f;
        public const float MinFuelPerMeter = 0f;
        public const float MaxFuelPerMeter = 2f;

        /// <summary>Clamp a fuel-per-metre setting into its slider range; NaN reads as the shipped default.</summary>
        public static float FuelPerMeter(float v)
        {
            if (float.IsNaN(v)) return DefaultFuelPerMeter;
            return Math.Max(MinFuelPerMeter, Math.Min(MaxFuelPerMeter, v));
        }

        /// <summary>Depth in metres of the water over a floor tile whose elevation is given (elevation &lt;= 0 is
        /// under water). Land, NaN and infinities have no water column: 0.</summary>
        public static float Depth(float floorElevation)
        {
            if (float.IsNaN(floorElevation) || float.IsInfinity(floorElevation)) return 0f;
            return floorElevation < 0f ? -floorElevation : 0f;
        }

        /// <summary>Extra fuel for one flight. Exactly one end on the floor layer and the other on the surface pays
        /// depth x fuelPerMeter, where the depth is the floor end's; same-layer flights, and flights to or from any
        /// third layer (orbit), pay nothing here.</summary>
        public static float ExtraFuel(bool fromFloor, bool fromSurface, bool toFloor, bool toSurface,
            float floorEndElevation, float fuelPerMeter)
        {
            bool crossing = (fromFloor && toSurface) || (fromSurface && toFloor);
            if (!crossing) return 0f;
            return Depth(floorEndElevation) * FuelPerMeter(fuelPerMeter);
        }
    }
}
