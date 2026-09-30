using RimWorld;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // CRACKEDLANDS_MECHANICS_BUILD_1 §5 — Peakstorm Light's only event
    // (Defs/WeatherDefs/RM_PeakstormLight.xml). Vanilla's
    // WeatherEvent_LightningFlash (RimSage, 2026-09-29) already is "a flash
    // plus Thunder_OffMap and nothing strikes"; the storm here is on the
    // peaks, far off, so the flash is dimmed to a skyline flicker. Nothing
    // else is overridden: no strike, no fire, no precipitation.
    public class RM_WeatherEvent_DistantFlicker : WeatherEvent_LightningFlash
    {
        private const float DistanceDim = 0.4f;

        public RM_WeatherEvent_DistantFlicker(Map map) : base(map)
        {
        }

        protected override float LightningBrightness => base.LightningBrightness * DistanceDim;
    }
}
