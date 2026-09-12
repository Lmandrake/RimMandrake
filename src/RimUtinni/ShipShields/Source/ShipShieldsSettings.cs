using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ShipShields.
    //
    // Four live mechanisms this mod runs:
    //   1. CompShieldGenerator's collapse explosion, when a bubble field's
    //      hit points hit zero.
    //   2. CompShieldParticulateScreen's per-interval filth sweep.
    //   3. CompShieldThermalVeil's per-interval room temperature nudge.
    //   4. HarmonyPatches' slow-projectile pass-through (the "slow things
    //      press through any shield, crew included" canon rule).
    // Each gets its own toggle; the collapse explosion also gets a damage
    // multiplier over its def-configured amount.
    public class ShipShieldsSettings : ModSettings
    {
        public static bool collapseExplosionEnabled = true;
        public static float collapseExplosionDamageMultiplier = 1f;
        public static bool particulateScreenEnabled = true;
        public static bool thermalVeilEnabled = true;
        public static bool bubbleSlowPassThroughEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref collapseExplosionEnabled, "collapseExplosionEnabled", true);
            Scribe_Values.Look(ref collapseExplosionDamageMultiplier, "collapseExplosionDamageMultiplier", 1f);
            Scribe_Values.Look(ref particulateScreenEnabled, "particulateScreenEnabled", true);
            Scribe_Values.Look(ref thermalVeilEnabled, "thermalVeilEnabled", true);
            Scribe_Values.Look(ref bubbleSlowPassThroughEnabled, "bubbleSlowPassThroughEnabled", true);
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
            list.GapLine();

            list.CheckboxLabeled("Particulate screen filth sweep", ref particulateScreenEnabled,
                "The particulate field mode sweeps weather-deposited filth out of its radius.");
            list.CheckboxLabeled("Thermal veil temperature control", ref thermalVeilEnabled,
                "The thermal field mode nudges room temperature toward its comfort setpoint.");

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
