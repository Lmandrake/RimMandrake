using System;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The choking smoke weather's effect (owner 2026-11-13: "the choking smoke that sometimes come as its own weather"; bar
    /// pyre_smoke_weather_chokes). Every SmokeCheckIntervalTicks, while the map's sky holds any RM_FE_Weather_Smoke (the weather
    /// manager's blend: curWeather at the transition lerp, lastWeather at 1 - lerp), each spawned pawn that breathes (flesh, and a
    /// kind not immune to weather effects, the test vanilla's ToxicUtility uses for airborne toxins) standing on an unroofed cell
    /// gains RM_FE_SmokeChoke by RM_FireEcoKernel.SmokeSeverityGain. Under a roof (built, thin rock or overhead mountain) it gains
    /// none and the hediff's own -2.4 a day wears it off. It keys on the map's weather, never on the biome: a smoke forced by the
    /// bridge or Royalty's weather controller chokes the same way on any map. Off with the mod's master switch or the smoke
    /// setting. Nothing is saved here: the hediff saves itself.
    /// </summary>
    public class MapComponent_RM_SmokeWeather : MapComponent
    {
        private static WeatherDef smoke;
        private static HediffDef choke;
        private static bool looked;

        public MapComponent_RM_SmokeWeather(Map map) : base(map)
        {
        }

        private static bool Resolve()
        {
            if (!looked)
            {
                smoke = DefDatabase<WeatherDef>.GetNamedSilentFail(RM_FireEcoKernel.SmokeWeatherDefName);
                choke = DefDatabase<HediffDef>.GetNamedSilentFail(RM_FireEcoKernel.SmokeChokeHediffDefName);
                looked = true;
            }
            return smoke != null && choke != null;
        }

        /// <summary>How much of the map's current sky is smoke, 0..1 (also the harness read).</summary>
        public static float SmokeShare(Map map)
        {
            WeatherManager wm = map?.weatherManager;
            if (wm == null || !Resolve()) return 0f;
            return RM_FireEcoKernel.BlackRainShare(wm.curWeather == smoke, wm.lastWeather == smoke, wm.TransitionLerpFactor);
        }

        /// <summary>Does this pawn breathe the open air, for the smoke's purpose.</summary>
        public static bool Breathes(Pawn pawn)
        {
            return pawn != null && !pawn.Dead && pawn.RaceProps != null && pawn.RaceProps.IsFlesh
                   && (pawn.kindDef == null || !pawn.kindDef.immuneToGameConditionEffects);
        }

        public override void MapComponentTick()
        {
            if ((Find.TickManager.TicksGame + map.uniqueID) % RM_FireEcoKernel.SmokeCheckIntervalTicks != 0) return;
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.smokeWeatherEnabled) return;
            try
            {
                float share = SmokeShare(map);
                if (share <= 0f) return;
                var pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = pawns.Count - 1; i >= 0; i--)
                {
                    Pawn p = pawns[i];
                    bool breathes = Breathes(p);
                    bool roofed = breathes && p.Position.Roofed(map);
                    float res = breathes && !roofed ? p.GetStatValue(StatDefOf.ToxicEnvironmentResistance) : 0f;
                    float gain = RM_FireEcoKernel.SmokeSeverityGain(PyrelandsMechanicsGate.On, RM_PyrelandsSettings.smokeWeatherEnabled,
                        share, breathes, roofed, res);
                    if (gain > 0f) HealthUtility.AdjustSeverity(p, choke, gain);
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] smoke weather: " + e.Message, 0x46E31);
            }
        }
    }
}
