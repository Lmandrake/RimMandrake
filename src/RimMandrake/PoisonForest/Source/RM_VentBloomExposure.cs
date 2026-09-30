using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.PoisonForest
{
    [DefOf]
    public static class RM_PoisonForestDefOf
    {
        public static WeatherDef RM_VentBloom;
        public static HediffDef RM_VentMetalLoad;

        static RM_PoisonForestDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_PoisonForestDefOf));
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_MECHANICS_BUILD_1 part 2 — the vent bloom's metal load.
    //
    // While RM_VentBloom is the map's current weather, every flesh pawn standing
    // outdoors under open sky gains RM_VentMetalLoad. Interval and resistance
    // math copy vanilla's own airborne toxic tick (WeatherWorker.WeatherTick +
    // ToxicUtility.DoPawnToxicDamage): every 3451 ticks, only once the weather
    // transition has finished, scaled by (1 - ToxicResistance) x
    // (1 - ToxicEnvironmentResistance) — so the same sealed gear that stops
    // toxic buildup stops this.
    //
    // The bloom WeatherDef leaves doToxicBuildup false, so this is the only
    // tax the bloom levies (no double-tax with vanilla toxic buildup).
    //
    // Native fauna are exempt: an animal whose kind is on the map biome's own
    // wildAnimals list (CommonalityOfAnimal > 0) has lived in this breath all
    // its life. Pawns vanilla marks immuneToGameConditionEffects are exempt
    // the same way vanilla exempts them from toxic weather.
    //
    // Gated by RM_PoisonForestSettings.ventBloomExposureEnabled; off = the
    // bloom is weather only, no hediff ever applied.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_VentBloomExposure : MapComponent
    {
        private const int IntervalTicks = 3451;          // vanilla toxic-weather cadence
        private const float BaseSeverityPerInterval = 0.012f; // INVENTED: ~0.2/day fully exposed

        public RM_MapComponent_VentBloomExposure(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % IntervalTicks != 0) return;
            if (!RM_PoisonForestSettings.ventBloomExposureEnabled) return;
            WeatherManager wm = map.weatherManager;
            if (wm == null || wm.curWeather != RM_PoisonForestDefOf.RM_VentBloom) return;
            if (!Mathf.Approximately(wm.TransitionLerpFactor, 1f)) return;

            var pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!Eligible(p)) continue;
                float amount = BaseSeverityPerInterval * RM_PoisonForestSettings.ventBloomExposureFactor;
                amount *= Mathf.Max(1f - p.GetStatValue(StatDefOf.ToxicResistance), 0f);
                amount *= Mathf.Max(1f - p.GetStatValue(StatDefOf.ToxicEnvironmentResistance), 0f);
                if (amount <= 0f) continue;
                HealthUtility.AdjustSeverity(p, RM_PoisonForestDefOf.RM_VentMetalLoad, amount);
            }
        }

        private bool Eligible(Pawn p)
        {
            if (p == null || p.Dead || !p.Spawned) return false;
            if (p.kindDef != null && p.kindDef.immuneToGameConditionEffects) return false;
            if (p.RaceProps == null || !p.RaceProps.IsFlesh) return false;
            if (p.Position.Roofed(map)) return false;
            if (p.RaceProps.Animal && map.Biome != null && map.Biome.CommonalityOfAnimal(p.kindDef) > 0f)
                return false;
            return true;
        }
    }
}
