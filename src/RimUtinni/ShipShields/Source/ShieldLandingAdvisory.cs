using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // shd:no-hard-landing-gate (owner ruling, ship_shields_deep_design.md §6):
    // "The ship will know what's visibly dangerous and will advise course of
    // action, but no more than that." This is the diegetic-warning half of
    // that ruling: a single non-blocking letter on landing, never a refusal
    // and never a damage tick (the design doc's escalating-damage half is a
    // separate, larger mechanism -- it needs a per-tick hazard-application
    // system nothing in this build touches yet; not started, see item file).
    //
    // v1 slice: evaluates only the two hazards THIS build's shields cover
    // (thermal, particulate) against real vanilla signals, never a guessed
    // modded defName -- cryo/spore hazards aren't evaluated because those
    // shields don't exist. Fires from HarmonyPatches.cs's postfix on
    // Scenario.PostGravshipLanded, a hook confirmed live this session
    // (GIZKA_HOLD_HOOK_SPIKE_1).
    public static class ShieldLandingAdvisory
    {
        // Roughly the vanilla Heatstroke-adjacent register; LavaFlow/HeatWave
        // are checked directly too, so this only carries tiles neither
        // condition is flagging as a backstop.
        private const float ExtremeHeatThreshold = 58f;

        public static void Evaluate(Map map)
        {
            if (map == null || !ShipShieldsSettings.landingAdvisoryEnabled)
            {
                return;
            }

            ThingDef generatorDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_ShieldGenerator");
            List<Thing> generators = generatorDef != null
                ? map.listerThings.ThingsOfDef(generatorDef)
                : new List<Thing>();

            bool heatHazard = map.mapTemperature.OutdoorTemp >= ExtremeHeatThreshold
                || map.gameConditionManager.ConditionIsActive(GameConditionDefOf.HeatWave)
                || (ModsConfig.OdysseyActive && GameConditionDefOf.LavaFlow != null
                    && map.gameConditionManager.ConditionIsActive(GameConditionDefOf.LavaFlow));

            // sandRate is a real WeatherDef field (vanilla's own Sandstorm
            // sets it to 1.6) -- checking the field rather than any specific
            // defName also catches a modded dust/sand weather without
            // guessing its name.
            bool particulateHazard = map.gameConditionManager.ConditionIsActive(GameConditionDefOf.ToxicFallout)
                || map.weatherManager.curWeather.sandRate > 0f;

            List<string> warnings = new List<string>();
            if (heatHazard && !generators.Any(g => IsModeReadyAndPowered(g, ShieldFieldMode.Thermal)))
            {
                warnings.Add("Extreme heat detected outside the hull. No thermal veil is configured "
                    + "and powered -- exposed systems will accumulate thermal stress.");
            }

            if (particulateHazard && !generators.Any(g => IsModeReadyAndPowered(g, ShieldFieldMode.Particulate)))
            {
                warnings.Add("Airborne particulate or contamination detected. No particulate screen "
                    + "is configured and powered -- expect fouling and untreated exposure.");
            }

            if (warnings.Count == 0)
            {
                return;
            }

            string text = "The ship's sensors report hazards this hull is not currently configured for:\n\n"
                + string.Join("\n\n", warnings)
                + "\n\nThis is advisory only -- the hull will not stop you from staying.";

            Find.LetterStack.ReceiveLetter(
                "Landing advisory: unshielded hazard",
                text,
                LetterDefOf.NeutralEvent,
                new TargetInfo(map.Center, map));
        }

        private static bool IsModeReadyAndPowered(Thing generator, ShieldFieldMode mode)
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
