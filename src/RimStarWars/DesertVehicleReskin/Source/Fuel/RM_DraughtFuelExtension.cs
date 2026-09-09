using Verse;

namespace RimMandrake.DesertVehicleReskin
{
    /// <summary>
    /// Marker attached (via XML patch, see DraughtFuel_Marker.xml) to the
    /// specific Alpha Vehicles - Neolithic VehicleDefs this mod's fuel-widening
    /// Harmony patches are actually about (Chariot / WarChariot / OxCart /
    /// CoveredCarriage / DogSled). Everything else on the Vehicle Framework
    /// load falls through to vanilla fuel behaviour instead of being widened
    /// (VEHICLE_FUEL_PATCH_UNFILTERED_1 -- the widening silently applied to
    /// every VF vehicle on the load, e.g. VVE trucks accepting potatoes).
    /// </summary>
    public class RM_DraughtFuelExtension : DefModExtension
    {
    }
}
