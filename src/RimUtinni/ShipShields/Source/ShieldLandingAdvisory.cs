using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // shd:no-hard-landing-gate (owner ruling, ship_shields_deep_design.md §6):
    // "The ship will know what's visibly dangerous and will advise course of
    // action, but no more than that." This is the diegetic-warning half of
    // that ruling: a single non-blocking letter on landing, never a refusal
    // and never a damage tick. The design doc's escalating-damage half
    // (ShieldHazardExposureTracker) and the lava-landing immediate-burst
    // carve-out (ShieldHazardExposureTracker.OnGravshipLanded) are separate,
    // additive systems built 2026-09-18 -- see the item file. Hazard
    // detection and the module-ready-and-powered check now live in
    // ShieldHazardUtility (moved, not duplicated, 2026-09-18) so this letter
    // and that tracker read identical signals.
    //
    // v1 slice: evaluates only the two hazards THIS build's shields cover
    // (thermal, particulate) against real vanilla signals, never a guessed
    // modded defName -- cryo/spore hazards aren't evaluated because those
    // shields don't exist. Fires from HarmonyPatches.cs's postfix on
    // Scenario.PostGravshipLanded, a hook confirmed live this session
    // (GIZKA_HOLD_HOOK_SPIKE_1).
    public static class ShieldLandingAdvisory
    {
        public static void Evaluate(Map map)
        {
            if (map == null || !ShipShieldsSettings.landingAdvisoryEnabled)
            {
                return;
            }

            bool heatHazard = ShieldHazardUtility.HasHeatHazard(map);
            bool particulateHazard = ShieldHazardUtility.HasParticulateHazard(map);

            List<string> warnings = new List<string>();
            if (heatHazard && !ShieldHazardUtility.IsHazardShielded(map, ShieldFieldMode.Thermal))
            {
                warnings.Add("Extreme heat detected outside the hull. No thermal veil is configured "
                    + "and powered -- exposed systems will accumulate thermal stress.");
            }

            if (particulateHazard && !ShieldHazardUtility.IsHazardShielded(map, ShieldFieldMode.Particulate))
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
    }
}
