using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1 (owner card 2026-10-08): a WeatherDef has no mote-direction field, so
    // Peakstorm Light carries this custom sky overlay. It drifts a dust sheet one way and, at the end of every
    // RM_DustKernel.PeriodTicks, swings it round and back for ReverseTicks ("cool, wet-clay air pushes through the slots").
    // Vanilla's fog sheet stands in for the dust art (MatLoader reads only Unity Resources/, see
    // RM_WeatherOverlay_GreentideRoil); it is tinted by the weather's own <overlay> sky colour. The pan is reimplemented
    // here because WeatherOverlayDualPanner keeps its accumulated pan private.
    //
    // VERIFY BY STATE READ, never a screenshot: RM_PeakstormDustProof.ProofState reports the live direction factor.
    [StaticConstructorOnStartup]
    public class RM_WeatherOverlay_PeakstormDust : WeatherOverlayDualPanner
    {
        private static readonly Material DustOverlayWorld = MatLoader.LoadMat("Weather/FogOverlayWorld");
        private static readonly int MainTex = Shader.PropertyToID("_MainTex");
        private static readonly int MainTex2 = Shader.PropertyToID("_MainTex2");

        // Last state this overlay ticked, for the proof hook. Static: the overlay instance lives on the WeatherDef.
        public static float LastFactor = 1f;
        public static long LastTick = -1;
        public static int ReversalsSeen;
        private static bool wasReversed;

        private Vector2 pan1 = Vector2.zero;
        private Vector2 pan2 = Vector2.zero;

        public RM_WeatherOverlay_PeakstormDust()
        {
            worldOverlayMat = DustOverlayWorld;
            // Drift toward +x/+y; INVENTED, faster than the Roil, slower than a storm's fog.
            worldOverlayPanSpeed1 = 0.0006f;
            worldOverlayPanSpeed2 = 0.0004f;
            worldPanDir1 = new Vector2(1f, 0.15f);
            worldPanDir2 = new Vector2(0.8f, -0.1f);
        }

        public override void TickOverlay(Map map, float lerpFactor)
        {
            if (worldOverlayMat == null)
            {
                return;
            }
            long tick = Find.TickManager.TicksGame;
            float f = RM_DustKernel.Factor(tick, RM_FloodedCanyonSettings.peakstormDustReversalEnabled);
            LastFactor = f;
            LastTick = tick;
            bool rev = RM_DustKernel.Reversed(f);
            if (rev && !wasReversed)
            {
                ReversalsSeen++;
            }
            wasReversed = rev;
            float rate = Find.TickManager.TickRateMultiplier * f;
            pan1 -= worldPanDir1 * (worldOverlayPanSpeed1 * worldOverlayMat.GetTextureScale(MainTex).x * rate);
            worldOverlayMat.SetTextureOffset(MainTex, pan1);
            if (worldOverlayMat.HasProperty(MainTex2))
            {
                pan2 -= worldPanDir2 * (worldOverlayPanSpeed2 * worldOverlayMat.GetTextureScale(MainTex2).x * rate);
                worldOverlayMat.SetTextureOffset(MainTex2, pan2);
            }
        }

        public override void Reset()
        {
            pan1 = Vector2.zero;
            pan2 = Vector2.zero;
            base.Reset();
        }
    }

    // jawa/static_call proof hook (validation.py, peakstorm_dust_reversal). Pure state read.
    public static class RM_PeakstormDustProof
    {
        public static string ProofState(string unused)
        {
            Map map = Find.CurrentMap;
            string weather = map?.weatherManager?.curWeather?.defName ?? "none";
            return "weather=" + weather
                + " enabled=" + RM_FloodedCanyonSettings.peakstormDustReversalEnabled
                + " factor=" + RM_WeatherOverlay_PeakstormDust.LastFactor.ToString("0.00")
                + " reversed=" + RM_DustKernel.Reversed(RM_WeatherOverlay_PeakstormDust.LastFactor)
                + " reversalsSeen=" + RM_WeatherOverlay_PeakstormDust.ReversalsSeen
                + " lastTick=" + RM_WeatherOverlay_PeakstormDust.LastTick;
        }
    }
}
