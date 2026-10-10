using System.Reflection;
using System.Collections.Generic;
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
    //   9. ShieldHazardExposureTracker's per-map escalating hull damage for
    //      staying unshielded in a hazard (shd:no-hard-landing-gate's other
    //      half), plus its own escalated-warning letter.
    //   10. ShieldHazardExposureTracker's immediate lava-landing damage
    //      burst -- the ruling's named "worst case," unconditional on
    //      shield state.
    //   11. CompShieldCryoEnvelope's per-interval room temperature nudge
    //      plus its own constant interior heat drain (shd:cryo-envelope).
    // Each gets its own toggle; the collapse explosion, the escalating hull
    // damage and the lava burst also get a damage multiplier over their
    // def/const-configured amount.
    public class ShipShieldsSettings : ModSettings
    {
        public static bool collapseExplosionEnabled = true;
        public static float collapseExplosionDamageMultiplier = 1f;
        public static bool predictiveFailureAlertEnabled = true;
        public static bool particulateScreenEnabled = true;
        public static bool particulateAnimalRepulsionEnabled = true;
        public static bool particulateWeatherDamageNegationEnabled = true;
        public static bool thermalVeilEnabled = true;
        public static bool cryoEnvelopeEnabled = true;
        public static bool bubbleSlowPassThroughEnabled = true;
        public static bool landingAdvisoryEnabled = true;
        public static bool landingHazardExposureEnabled = true;
        public static bool lavaLandingBurstEnabled = true;
        public static float lavaLandingBurstDamageMultiplier = 1f;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref collapseExplosionEnabled, "collapseExplosionEnabled", true);
            Scribe_Values.Look(ref collapseExplosionDamageMultiplier, "collapseExplosionDamageMultiplier", 1f);
            Scribe_Values.Look(ref predictiveFailureAlertEnabled, "predictiveFailureAlertEnabled", true);
            Scribe_Values.Look(ref particulateScreenEnabled, "particulateScreenEnabled", true);
            Scribe_Values.Look(ref particulateAnimalRepulsionEnabled, "particulateAnimalRepulsionEnabled", true);
            Scribe_Values.Look(ref particulateWeatherDamageNegationEnabled, "particulateWeatherDamageNegationEnabled", true);
            Scribe_Values.Look(ref thermalVeilEnabled, "thermalVeilEnabled", true);
            Scribe_Values.Look(ref cryoEnvelopeEnabled, "cryoEnvelopeEnabled", true);
            Scribe_Values.Look(ref bubbleSlowPassThroughEnabled, "bubbleSlowPassThroughEnabled", true);
            Scribe_Values.Look(ref landingAdvisoryEnabled, "landingAdvisoryEnabled", true);
            Scribe_Values.Look(ref landingHazardExposureEnabled, "landingHazardExposureEnabled", true);
            Scribe_Values.Look(ref lavaLandingBurstEnabled, "lavaLandingBurstEnabled", true);
            Scribe_Values.Look(ref lavaLandingBurstDamageMultiplier, "lavaLandingBurstDamageMultiplier", 1f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(ShipShieldsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(ShipShieldsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Bubble shields", RimMandrake.Shared.SettingScope.Now, new[] { "collapseExplosionEnabled", "collapseExplosionDamageMultiplier", "bubbleSlowPassThroughEnabled", "predictiveFailureAlertEnabled" }))
            {
                list.CheckboxLabeled("Bubble shield collapse explosion", ref collapseExplosionEnabled,
                    "A bubble-field shield generator explodes when its hit points are driven to zero.");
                list.Label("Collapse explosion damage: " + collapseExplosionDamageMultiplier.ToString("0.00") + "x");
                collapseExplosionDamageMultiplier = list.Slider(collapseExplosionDamageMultiplier, 0.25f, 3f);
                list.CheckboxLabeled("Slow projectiles pass through shields", ref bubbleSlowPassThroughEnabled,
                    "Canon rule: anything slow enough (including a person) presses through a bubble "
                  + "field untouched. Off: a bubble field intercepts everything, same as a vanilla "
                  + "projectile interceptor.");
                list.CheckboxLabeled("Predictive shield-failure alert", ref predictiveFailureAlertEnabled,
                    "Warn when a shield's hit points are declining fast enough to predict collapse soon, "
                  + "so the crew has time to return to the hull and leave.");
                list.GapLine();
            }

            if (Group(list, "Field modes", RimMandrake.Shared.SettingScope.Now, new[] { "particulateScreenEnabled", "particulateAnimalRepulsionEnabled", "particulateWeatherDamageNegationEnabled", "thermalVeilEnabled", "cryoEnvelopeEnabled" }))
            {
                list.CheckboxLabeled("Particulate screen filth sweep", ref particulateScreenEnabled,
                    "The particulate field mode sweeps weather-deposited filth out of its radius.");
                list.CheckboxLabeled("Particulate screen repels small animals", ref particulateAnimalRepulsionEnabled,
                    "The particulate field mode makes small wild animals flee out of its radius.");
                list.CheckboxLabeled("Particulate screen blocks airborne toxic damage", ref particulateWeatherDamageNegationEnabled,
                    "Pawns and crops inside an active particulate field's radius are unaffected by "
                  + "airborne Toxic Fallout exposure.");
                list.CheckboxLabeled("Thermal veil temperature control", ref thermalVeilEnabled,
                    "The thermal field mode nudges room temperature toward its comfort setpoint.");
                list.CheckboxLabeled("Cryo envelope temperature control", ref cryoEnvelopeEnabled,
                    "The cryo field mode holds back severe outside cold, but continuously drains a small "
                  + "amount of interior heat while active as its own cost.");
                list.GapLine();
            }

            if (Group(list, "Unshielded hazard exposure", RimMandrake.Shared.SettingScope.Now, new[] { "landingHazardExposureEnabled" }))
            {
                list.CheckboxLabeled("Escalating unshielded hull damage", ref landingHazardExposureEnabled,
                    "The longer the ship sits in a hazard with no matching shield configured and powered, "
                  + "the more its own structures take periodic damage -- accelerating after a long stretch. "
                  + "Never a hard block, matching the advisory letter in \"On landing\".");
                list.GapLine();
            }

            if (Group(list, "On landing", RimMandrake.Shared.SettingScope.NextPulse, new[] { "landingAdvisoryEnabled", "lavaLandingBurstEnabled", "lavaLandingBurstDamageMultiplier" }))
            {
                list.CheckboxLabeled("Landing hazard advisory", ref landingAdvisoryEnabled,
                    "On landing the gravship, warn (once, non-blocking) if a hazard is present that no "
                  + "installed shield is currently configured and powered for.");
                list.CheckboxLabeled("Lava-landing damage burst", ref lavaLandingBurstEnabled,
                    "Landing on active lava (the design's named worst case) causes one immediate, severe "
                  + "damage burst -- no shield configuration prevents this specific one.");
                list.Label("Lava-landing burst damage: " + lavaLandingBurstDamageMultiplier.ToString("0.00") + "x");
                lavaLandingBurstDamageMultiplier = list.Slider(lavaLandingBurstDamageMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
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
