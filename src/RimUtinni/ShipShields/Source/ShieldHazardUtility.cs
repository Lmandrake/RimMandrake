using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // shd:no-hard-landing-gate. Shared hazard-detection + shield-coverage
    // logic, extracted from ShieldLandingAdvisory (2026-09-12's one-time
    // landing letter) so it and ShieldHazardExposureTracker's ongoing
    // per-tick system (2026-09-18) read the exact same signals -- two
    // independent readings of "is this map hazardous and unshielded right
    // now" would drift the moment either file changed alone. Behavior is
    // unchanged from the original ShieldLandingAdvisory logic, only moved.
    public static class ShieldHazardUtility
    {
        // Roughly the vanilla Heatstroke-adjacent register; LavaFlow/HeatWave
        // are checked directly too, so this only carries tiles neither
        // condition is flagging as a backstop.
        public const float ExtremeHeatThreshold = 58f;

        // Symmetric backstop for cold, same role as ExtremeHeatThreshold: a
        // standing nightside biome has no ColdSnap GameCondition active (that
        // condition is a temporary weather event, confirmed via rimsage
        // GameConditionDefOf.ColdSnap), so a fixed-ambient-temperature
        // backstop is the PRIMARY signal for "permanently past the
        // terminator," not just a rare fallback the way it is for heat.
        public const float ExtremeColdThreshold = -40f;

        public static bool HasHeatHazard(Map map)
        {
            return map.mapTemperature.OutdoorTemp >= ExtremeHeatThreshold
                || map.gameConditionManager.ConditionIsActive(GameConditionDefOf.HeatWave)
                || (ModsConfig.OdysseyActive && GameConditionDefOf.LavaFlow != null
                    && map.gameConditionManager.ConditionIsActive(GameConditionDefOf.LavaFlow));
        }

        // shd:cryo-envelope gates the nightside and the propane sea (R-H6/
        // R-H10) -- a standing biome condition, not a passing storm, so the
        // ambient-temperature backstop is doing most of the real work here.
        // ColdSnap is checked too for a temporary severe-cold event on an
        // otherwise-survivable map.
        public static bool HasColdHazard(Map map)
        {
            return map.mapTemperature.OutdoorTemp <= ExtremeColdThreshold
                || map.gameConditionManager.ConditionIsActive(GameConditionDefOf.ColdSnap);
        }

        // sandRate is a real WeatherDef field (vanilla's own Sandstorm sets
        // it to 1.6) -- checking the field rather than any specific defName
        // also catches a modded dust/sand weather without guessing its name.
        public static bool HasParticulateHazard(Map map)
        {
            return map.gameConditionManager.ConditionIsActive(GameConditionDefOf.ToxicFallout)
                || map.weatherManager.curWeather.sandRate > 0f;
        }

        // shd:no-hard-landing-gate's carved-out exception ("Landing on lava
        // should be the worst case causing immediate severe damage"),
        // checked at the instant of landing only
        // (ShieldHazardExposureTracker.OnGravshipLanded). LavaDeep/
        // LavaShallow can be permanent map terrain from a LavaLake/
        // LavaCrater tile mutator with no GameCondition_LavaFlow ever
        // registered (confirmed via rimsage: TileMutatorWorker_LavaLake
        // writes TerrainDefOf.LavaDeep directly at map generation, no
        // condition involved), so the condition check alone would miss a
        // hand-placed lava lake. A full-map terrain scan is cheap done once,
        // at landing -- it is deliberately never run from the per-tick
        // monitor.
        public static bool HasLavaAtLanding(Map map)
        {
            if (ModsConfig.OdysseyActive && GameConditionDefOf.LavaFlow != null
                && map.gameConditionManager.ConditionIsActive(GameConditionDefOf.LavaFlow))
            {
                return true;
            }

            if (!ModsConfig.OdysseyActive)
            {
                return false;
            }

            foreach (IntVec3 cell in map.AllCells)
            {
                TerrainDef terrain = cell.GetTerrain(map);
                if (terrain == TerrainDefOf.LavaDeep || terrain == TerrainDefOf.LavaShallow)
                {
                    return true;
                }
            }

            return false;
        }

        public static List<Thing> Generators(Map map)
        {
            ThingDef generatorDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_ShieldGenerator");
            return generatorDef != null ? map.listerThings.ThingsOfDef(generatorDef) : new List<Thing>();
        }

        public static bool IsHazardShielded(Map map, ShieldFieldMode mode)
        {
            return Generators(map).Any(g => IsModeReadyAndPowered(g, mode));
        }

        public static bool IsModeReadyAndPowered(Thing generator, ShieldFieldMode mode)
        {
            ThingWithComps thing = generator as ThingWithComps;
            CompShieldModuleSwitch moduleSwitch = thing?.GetComp<CompShieldModuleSwitch>();
            if (moduleSwitch == null || moduleSwitch.CurrentMode != mode || !moduleSwitch.IsUnlocked(mode))
            {
                return false;
            }

            CompPowerTrader power = thing.GetComp<CompPowerTrader>();
            return power == null || power.PowerOn;
        }
    }
}
