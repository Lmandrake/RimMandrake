using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.WeatherSuite
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for WeatherSuite.
    //
    // Three independently-gateable mechanics, found by reading
    // WeatherSuiteHook.cs (this mod's entire C# surface) before writing this:
    //   1. Terminator Front — MapComponent_TerminatorBand.FinalizeInit starts
    //      a PERMANENT storm GameCondition on any newly-initialized map that
    //      sits in the terminator band. WORLDGEN-AFFECTING: only ever
    //      applied once, right when a map is generated — a map that already
    //      has (or lacks) the condition is never retroactively changed.
    //   2. Nightside Aurora — IncidentWorker_NightsideAurora gates vanilla's
    //      own Aurora incident to nightside-band maps only.
    //   3. Maximized aurora brightness — GameCondition_DarkAuroraMax's
    //      override of vanilla's hardcoded-private aurora colour/brightness.
    //
    // The forecaster instrument (CompForecaster) is a passive inspect-string
    // reader with no tunable number and nothing to turn off that isn't
    // already "don't build the building" — not duplicated here.
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    // ════════════════════════════════════════════════════════════════════
    public class WeatherSuiteSettings : ModSettings
    {
        public static bool terminatorFrontEnabled = true;
        public static bool nightsideAuroraEnabled = true;

        public static bool auroraMaxBrightnessEnabled = true;
        // Vanilla defaults, for reference: sky lerp 0.075, overlay lerp 0.025,
        // brightness range 0.73-1.0.
        public static float auroraSkySaturation = 0.35f;
        public static float auroraOverlaySaturation = 0.05f;
        public static float auroraSkyBrightness = 1.15f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref terminatorFrontEnabled, "terminatorFrontEnabled", true);
            Scribe_Values.Look(ref nightsideAuroraEnabled, "nightsideAuroraEnabled", true);
            Scribe_Values.Look(ref auroraMaxBrightnessEnabled, "auroraMaxBrightnessEnabled", true);
            Scribe_Values.Look(ref auroraSkySaturation, "auroraSkySaturation", 0.35f);
            Scribe_Values.Look(ref auroraOverlaySaturation, "auroraOverlaySaturation", 0.05f);
            Scribe_Values.Look(ref auroraSkyBrightness, "auroraSkyBrightness", 1.15f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(WeatherSuiteSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(WeatherSuiteSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

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
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // Scopes audited per read site (WeatherSuiteHook.cs): the terminator storm is started once when a new map initialises;
            // the aurora incident gate is read whenever the incident is rolled; the colours are read every frame the aurora is active.
            if (Group(list, "Terminator Front permanent storm (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "terminatorFrontEnabled" }))
            {
                list.CheckboxLabeled("Terminator Front permanent storm", ref terminatorFrontEnabled,
                    "A map generated inside the day/night terminator band gets a permanent storm-wall "
                  + "weather condition. Off: no new map ever gets it. A map that already has one keeps it "
                  + "either way - this never changes an existing map.");
                list.GapLine();
            }

            if (Group(list, "Nightside Aurora incident", RimMandrake.Shared.SettingScope.NextPulse, new[] { "nightsideAuroraEnabled" }))
            {
                list.CheckboxLabeled("Nightside Aurora incident", ref nightsideAuroraEnabled,
                    "Lets the aurora incident fire on colonies sitting in the planet's deep-night band. "
                  + "Off: this incident never fires (an ordinary map with no dark-side band is unaffected "
                  + "either way).");
                list.GapLine();
            }

            if (Group(list, "Maximized aurora colours", RimMandrake.Shared.SettingScope.Now, new[] { "auroraMaxBrightnessEnabled", "auroraSkySaturation", "auroraOverlaySaturation", "auroraSkyBrightness" }))
            {
                list.CheckboxLabeled("Maximized aurora colours", ref auroraMaxBrightnessEnabled,
                    "Makes an active aurora's sky colour bold and bright instead of vanilla's faint tint. "
                  + "Off: the aurora looks exactly like vanilla's.");
                list.Label("  Sky colour strength: " + auroraSkySaturation.ToString("0.00") + " (vanilla: 0.08)");
                auroraSkySaturation = list.Slider(auroraSkySaturation, 0.075f, 1f);
                list.Label("  Terrain overlay strength: " + auroraOverlaySaturation.ToString("0.00") + " (vanilla: 0.03)");
                auroraOverlaySaturation = list.Slider(auroraOverlaySaturation, 0.025f, 0.5f);
                list.Label("  Sky brightness: " + auroraSkyBrightness.ToString("0.00") + " (vanilla: 0.73-1.0)");
                auroraSkyBrightness = list.Slider(auroraSkyBrightness, 0.73f, 2f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class WeatherSuiteOptionsMod : Mod
    {
        public static WeatherSuiteSettings settings;

        public WeatherSuiteOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WeatherSuiteSettings>();
        }

        public override string SettingsCategory()
        {
            return "Weather Suite";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
