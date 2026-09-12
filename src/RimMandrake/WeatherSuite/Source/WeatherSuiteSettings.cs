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

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Terminator Front permanent storm (affects new maps only)", ref terminatorFrontEnabled,
                "A map generated inside the day/night terminator band gets a permanent storm-wall "
              + "weather condition. Off: no new map ever gets it. A map that already has one keeps it "
              + "either way — this never changes an existing map.");
            list.GapLine();

            list.CheckboxLabeled("Nightside Aurora incident", ref nightsideAuroraEnabled,
                "Lets the aurora incident fire on colonies sitting in the planet's deep-night band. "
              + "Off: this incident never fires (an ordinary map with no dark-side band is unaffected "
              + "either way).");
            list.GapLine();

            list.CheckboxLabeled("Maximized aurora colours", ref auroraMaxBrightnessEnabled,
                "Makes an active aurora's sky colour bold and bright instead of vanilla's faint tint. "
              + "Off: the aurora looks exactly like vanilla's.");
            if (auroraMaxBrightnessEnabled)
            {
                list.Label("  Sky colour strength: " + auroraSkySaturation.ToString("0.00") + " (vanilla: 0.08)");
                auroraSkySaturation = list.Slider(auroraSkySaturation, 0.075f, 1f);
                list.Label("  Terrain overlay strength: " + auroraOverlaySaturation.ToString("0.00") + " (vanilla: 0.03)");
                auroraOverlaySaturation = list.Slider(auroraOverlaySaturation, 0.025f, 0.5f);
                list.Label("  Sky brightness: " + auroraSkyBrightness.ToString("0.00") + " (vanilla: 0.73-1.0)");
                auroraSkyBrightness = list.Slider(auroraSkyBrightness, 0.73f, 2f);
            }

            list.End();
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
