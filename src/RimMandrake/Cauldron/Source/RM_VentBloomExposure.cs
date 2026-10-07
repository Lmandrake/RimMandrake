using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    [DefOf]
    public static class RM_CauldronDefOf
    {
        public static WeatherDef RM_VentBloom;
        public static HediffDef RM_VentMetalLoad;
        public static ThingDef RM_CauldronVent;
        public static JobDef RM_VexxissDrinkVent;

        static RM_CauldronDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_CauldronDefOf));
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
    // Gated by RM_CauldronSettings.ventBloomExposureEnabled; off = the
    // bloom is weather only, no hediff ever applied.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_VentBloomExposure : MapComponent
    {
        private const int IntervalTicks = RM_YieldKernel.BloomIntervalTicks;          // vanilla toxic-weather cadence
        private const float BaseSeverityPerInterval = RM_YieldKernel.BaseSeverityPerInterval; // INVENTED: ~0.2/day fully exposed

        public RM_MapComponent_VentBloomExposure(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            WeatherManager wm = map.weatherManager;
            if (!RM_YieldKernel.BloomTicks(Find.TickManager.TicksGame, RM_CauldronSettings.ventBloomExposureEnabled,
                    wm != null && wm.curWeather == RM_CauldronDefOf.RM_VentBloom, wm != null && RM_VentKernel.ApproximatelyOne(wm.TransitionLerpFactor))) return;

            var pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!Eligible(p)) continue;
                // CAULDRON_VENT_ENRICHMENT_HOOKS_1: strongest beside a live vent; 1.0 on a map with no vents.
                float amount = RM_YieldKernel.Dose(RM_CauldronSettings.ventBloomExposureFactor, p.GetStatValue(StatDefOf.ToxicResistance),
                    p.GetStatValue(StatDefOf.ToxicEnvironmentResistance), RM_MapComponent_CauldronVents.ExposureWeight(map, p.Position));
                if (amount <= 0f) continue;
                HealthUtility.AdjustSeverity(p, RM_CauldronDefOf.RM_VentMetalLoad, amount);
            }
        }

        private bool Eligible(Pawn p)
        {
            if (p == null) return false;
            return RM_YieldKernel.Eligible(true, p.Dead, p.Spawned, p.kindDef != null && p.kindDef.immuneToGameConditionEffects,
                p.RaceProps != null && p.RaceProps.IsFlesh, p.Spawned && p.Position.Roofed(map),
                p.RaceProps != null && p.RaceProps.Animal,
                p.RaceProps != null && p.RaceProps.Animal && map.Biome != null && map.Biome.CommonalityOfAnimal(p.kindDef) > 0f);
        }
    }
}
