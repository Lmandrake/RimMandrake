using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    public class CompProperties_ShieldThermalVeil : CompProperties
    {
        // shd:thermal-veil: "reflect all external heat outward... but also
        // reflect all internal heat inward, so the temperature slowly
        // climbs anyway... but not nearly as badly." A fraction (not all)
        // of the ideal correction toward comfortTemperature is applied each
        // interval -- the room still drifts, just far more slowly.
        public float rejectionFactor = 0.45f;
        public float comfortTemperature = 21f;
        public int intervalTicks = 250;

        public CompProperties_ShieldThermalVeil()
        {
            compClass = typeof(CompShieldThermalVeil);
        }
    }
}
