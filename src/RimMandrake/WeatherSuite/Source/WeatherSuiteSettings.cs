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
    //   4. Perpetual aurora (AURORAL_UMBRA) - a permanent aurora on marked biomes; its light comes from
    //      two Harmony postfixes (AuroraLight.cs, AURORA_LIGHT 2026-10-20).
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

        // AURORAL_UMBRA (owner 2026-10-19: "totally dark except for the utterly beautiful and wildly active aurora"): the perpetual aurora on
        // biomes carrying PerpetualAuroraExtension; its light is AuroraLight.cs (AURORA_LIGHT 2026-10-20). ALL NUMBERS PROVISIONAL (first
        // guesses, to be judged by eye in game): ground glow 0.22 (under vanilla's 0.30 "Lit" line: lit but still a dark place), sky light 0.30
        // (aurora hue added to the night sky colour), night darkness 0.50 (the ordinary night sky dimmed by half), activity 8 (colour change
        // every ~470 ticks, shimmer and curtain drift 8x), curtains on at strength 0.35.
        public static bool perpetualAuroraEnabled = true;
        public static float perpetualAuroraGroundGlow = 0.22f;
        public static float perpetualAuroraSkyLight = 0.30f;
        public static float perpetualAuroraNightDarkness = 0.50f;
        public static int perpetualAuroraActivity = 8;
        public static bool perpetualAuroraCurtains = true;
        public static float perpetualAuroraCurtainStrength = 0.35f;

        public override void ExposeData()
        {
            base.ExposeData();
            RimMandrake.Shared.PatchApplier.BeforeExpose(typeof(WeatherSuiteSettings));
            Scribe_Values.Look(ref terminatorFrontEnabled, "terminatorFrontEnabled", true);
            Scribe_Values.Look(ref nightsideAuroraEnabled, "nightsideAuroraEnabled", true);
            Scribe_Values.Look(ref auroraMaxBrightnessEnabled, "auroraMaxBrightnessEnabled", true);
            Scribe_Values.Look(ref auroraSkySaturation, "auroraSkySaturation", 0.35f);
            Scribe_Values.Look(ref auroraOverlaySaturation, "auroraOverlaySaturation", 0.05f);
            Scribe_Values.Look(ref auroraSkyBrightness, "auroraSkyBrightness", 1.15f);
            Scribe_Values.Look(ref perpetualAuroraEnabled, "perpetualAuroraEnabled", true);
            Scribe_Values.Look(ref perpetualAuroraGroundGlow, "perpetualAuroraGroundGlow", 0.22f);
            Scribe_Values.Look(ref perpetualAuroraSkyLight, "perpetualAuroraSkyLight", 0.30f);
            Scribe_Values.Look(ref perpetualAuroraNightDarkness, "perpetualAuroraNightDarkness", 0.50f);
            Scribe_Values.Look(ref perpetualAuroraActivity, "perpetualAuroraActivity", 8);
            Scribe_Values.Look(ref perpetualAuroraCurtains, "perpetualAuroraCurtains", true);
            Scribe_Values.Look(ref perpetualAuroraCurtainStrength, "perpetualAuroraCurtainStrength", 0.35f);
            RimMandrake.Shared.PatchApplier.AfterExpose(typeof(WeatherSuiteSettings));
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

            if (Group(list, "Perpetual aurora (biomes that never lose it)", RimMandrake.Shared.SettingScope.Now, new[] { "perpetualAuroraEnabled", "perpetualAuroraGroundGlow", "perpetualAuroraSkyLight", "perpetualAuroraNightDarkness", "perpetualAuroraActivity", "perpetualAuroraCurtains", "perpetualAuroraCurtainStrength" }))
            {
                list.CheckboxLabeled("Perpetual aurora", ref perpetualAuroraEnabled,
                    "A biome marked for it (on Ash'karr: the Auroral Umbra) keeps an aurora in its sky at all times, "
                  + "colouring the night sky, faintly lighting open ground and lifting moods. Off: the aurora is removed from those maps "
                  + "within an hour of game time; only the ordinary, occasional aurora event remains.");
                list.Label("  Light on open ground: " + perpetualAuroraGroundGlow.ToString("0.00") + " (below 0.30 the ground still counts as dark; full daylight: 1.00)");
                perpetualAuroraGroundGlow = list.Slider(perpetualAuroraGroundGlow, 0f, RimMandrake.StarWars.WeatherSuite.RM_WeatherKernel.MaxGroundGlow);
                list.Label("  Aurora colour in the sky: " + perpetualAuroraSkyLight.ToString("0.00") + " (how strongly its light tints the whole map)");
                perpetualAuroraSkyLight = list.Slider(perpetualAuroraSkyLight, 0f, 0.8f);
                list.Label("  Darkness of the night around it: " + perpetualAuroraNightDarkness.ToString("0.00") + " (0 = an ordinary night; 1 = black but for the aurora)");
                perpetualAuroraNightDarkness = list.Slider(perpetualAuroraNightDarkness, 0f, 1f);
                list.Label("  Activity (how fast it sweeps, shimmers and drifts): " + perpetualAuroraActivity + "x (1x = vanilla's slow permanent drift)");
                perpetualAuroraActivity = Mathf.RoundToInt(list.Slider(perpetualAuroraActivity, 1f, 30f));
                list.CheckboxLabeled("  Moving curtains of light", ref perpetualAuroraCurtains,
                    "Draws drifting ribbons of aurora light over the map at night. Off: only the sky colour and ground light remain.");
                list.Label("  Curtain brightness: " + perpetualAuroraCurtainStrength.ToString("0.00"));
                perpetualAuroraCurtainStrength = list.Slider(perpetualAuroraCurtainStrength, 0f, 1f);
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
            // AURORA_LIGHT: the perpetual aurora's two light postfixes (AuroraLight.cs). One broken patch switches its feature off, not the mod.
            RimMandrake.Shared.PatchApplier.Apply(new HarmonyLib.Harmony("mandrake.rm.weathersuite"), typeof(WeatherSuiteOptionsMod).Assembly, "RimMandrake.StarWars.WeatherSuite");
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
