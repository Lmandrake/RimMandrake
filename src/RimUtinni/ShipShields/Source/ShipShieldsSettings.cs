using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ShipShields.
    //
    // Live mechanisms this mod runs:
    //   1. CompShieldGenerator's collapse explosion, when a bubble field's
    //      hit points hit zero.
    //   2. CompShieldGenerator's predictive-failure alert (shd:shield-
    //      collapse-evacuate's evacuation-warning half).
    //   3. CompShieldParticulateScreen's per-interval filth sweep.
    //   4. CompShieldParticulateScreen's small-animal repulsion.
    //   5. HarmonyPatches' toxic-fallout weather-damage negation under an
    //      active particulate screen.
    //   6. CompShieldThermalVeil's per-interval room temperature nudge.
    //   7. HarmonyPatches' slow-projectile pass-through (the "slow things
    //      press through any shield, crew included" canon rule).
    //   8. ShieldLandingAdvisory's one-time diegetic warning letter on
    //      gravship landing (shd:no-hard-landing-gate).
    // Each gets its own toggle; the collapse explosion also gets a damage
    // multiplier over its def-configured amount.
    public class ShipShieldsSettings : ModSettings
    {
        public static bool collapseExplosionEnabled = true;
        public static float collapseExplosionDamageMultiplier = 1f;
        public static bool predictiveFailureAlertEnabled = true;
        public static bool particulateScreenEnabled = true;
        public static bool particulateAnimalRepulsionEnabled = true;
        public static bool particulateWeatherDamageNegationEnabled = true;
        public static bool thermalVeilEnabled = true;
        public static bool bubbleSlowPassThroughEnabled = true;
        public static bool landingAdvisoryEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref collapseExplosionEnabled, "collapseExplosionEnabled", true);
            Scribe_Values.Look(ref collapseExplosionDamageMultiplier, "collapseExplosionDamageMultiplier", 1f);
            Scribe_Values.Look(ref predictiveFailureAlertEnabled, "predictiveFailureAlertEnabled", true);
            Scribe_Values.Look(ref particulateScreenEnabled, "particulateScreenEnabled", true);
            Scribe_Values.Look(ref particulateAnimalRepulsionEnabled, "particulateAnimalRepulsionEnabled", true);
            Scribe_Values.Look(ref particulateWeatherDamageNegationEnabled, "particulateWeatherDamageNegationEnabled", true);
            Scribe_Values.Look(ref thermalVeilEnabled, "thermalVeilEnabled", true);
            Scribe_Values.Look(ref bubbleSlowPassThroughEnabled, "bubbleSlowPassThroughEnabled", true);
            Scribe_Values.Look(ref landingAdvisoryEnabled, "landingAdvisoryEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Bubble shield collapse explosion", ref collapseExplosionEnabled,
                "A bubble-field shield generator explodes when its hit points are driven to zero.");
            list.Label("Collapse explosion damage: " + collapseExplosionDamageMultiplier.ToString("0.00") + "x");
            collapseExplosionDamageMultiplier = list.Slider(collapseExplosionDamageMultiplier, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Slow projectiles pass through shields", ref bubbleSlowPassThroughEnabled,
                "Canon rule: anything slow enough (including a person) presses through a bubble "
              + "field untouched. Off: a bubble field intercepts everything, same as a vanilla "
              + "projectile interceptor.");
            list.CheckboxLabeled("Predictive shield-failure alert", ref predictiveFailureAlertEnabled,
                "Warn when a shield's hit points are declining fast enough to predict collapse soon, "
              + "so the crew has time to return to the hull and leave.");
            list.GapLine();

            list.CheckboxLabeled("Particulate screen filth sweep", ref particulateScreenEnabled,
                "The particulate field mode sweeps weather-deposited filth out of its radius.");
            list.CheckboxLabeled("Particulate screen repels small animals", ref particulateAnimalRepulsionEnabled,
                "The particulate field mode makes small wild animals flee out of its radius.");
            list.CheckboxLabeled("Particulate screen blocks airborne toxic damage", ref particulateWeatherDamageNegationEnabled,
                "Pawns and crops inside an active particulate field's radius are unaffected by "
              + "airborne Toxic Fallout exposure.");
            list.CheckboxLabeled("Thermal veil temperature control", ref thermalVeilEnabled,
                "The thermal field mode nudges room temperature toward its comfort setpoint.");
            list.GapLine();

            list.CheckboxLabeled("Landing hazard advisory", ref landingAdvisoryEnabled,
                "On landing the gravship, warn (once, non-blocking) if a hazard is present that no "
              + "installed shield is currently configured and powered for.");

            list.End();
        }
    }

    public class ShipShieldsSettingsMod : Mod
    {
        public static ShipShieldsSettings settings;

        public ShipShieldsSettingsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ShipShieldsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Ship Shields";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
