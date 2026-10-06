using UnityEngine;
using Verse;

namespace RimMandrake.OasisMaker
{
    // ════════════════════════════════════════════════════════════════════
    // OASIS_MAKER_BUILD_1 — Mod Settings.
    // MOD_OPTIONS_RETROFIT_1 doctrine: master on/off, every number the spec
    // named as a tuning knob, defaults = the spec's own shipped numbers,
    // all-off degrades gracefully (masterEnabled false: the comp never
    // leaves Dormant, the PlaceWorker still allows placing anywhere since a
    // disabled mechanic must not soft-lock a build the player already owns).
    // ════════════════════════════════════════════════════════════════════
    public class RM_OasisMakerSettings : ModSettings
    {
        public static bool masterEnabled = true;

        // §3 hard floor — refuse to place below this.
        public static int shadeScoreFloor = 8;
        public static int rockScoreFloor = 15;
        public static int scoringRadius = 8;

        // Quality ceilings: shadeScore/rockScore values that earn full 1.0
        // quality (1.5x speed, radius cap 9) once at or above the floor.
        // Tuning knobs, not spec-literal numbers — the spec leaves the
        // quality curve's shape as "a tuning knob."
        public static int shadeScoreExcellent = 30;
        public static int rockScoreExcellent = 45;

        // §2 states.
        public static int attuningDays = 2;

        // §2 growth model.
        public static float baseRingDays = 3f;
        public static float ringGrowthFactor = 1.5f;
        public static int minRadiusCap = 6;
        public static int maxRadiusCap = 9;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref shadeScoreFloor, "shadeScoreFloor", 8);
            Scribe_Values.Look(ref rockScoreFloor, "rockScoreFloor", 15);
            Scribe_Values.Look(ref scoringRadius, "scoringRadius", 8);
            Scribe_Values.Look(ref shadeScoreExcellent, "shadeScoreExcellent", 30);
            Scribe_Values.Look(ref rockScoreExcellent, "rockScoreExcellent", 45);
            Scribe_Values.Look(ref attuningDays, "attuningDays", 2);
            Scribe_Values.Look(ref baseRingDays, "baseRingDays", 3f);
            Scribe_Values.Look(ref ringGrowthFactor, "ringGrowthFactor", 1.5f);
            Scribe_Values.Look(ref minRadiusCap, "minRadiusCap", 6);
            Scribe_Values.Look(ref maxRadiusCap, "maxRadiusCap", 9);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

            list.CheckboxLabeled("Oasis-maker enabled", ref masterEnabled,
                "Master switch. Off: placed oasis-makers stay Dormant forever and grow "
              + "nothing, but placement itself is never blocked by the shade/rock floor.");

            if (masterEnabled)
            {
                list.Gap();
                list.Label("Shade score floor (of " + scoringRadius + "-cell radius): " + shadeScoreFloor);
                shadeScoreFloor = (int)list.Slider(shadeScoreFloor, 1, 60);
                list.Label("Rock score floor (of " + scoringRadius + "-cell radius): " + rockScoreFloor);
                rockScoreFloor = (int)list.Slider(rockScoreFloor, 1, 90);
                list.Label("Scoring radius: " + scoringRadius + " cells");
                scoringRadius = (int)list.Slider(scoringRadius, 4, 12);

                list.Gap();
                list.Label("Shade score for excellent (1.5x speed, radius 9) quality: " + shadeScoreExcellent);
                shadeScoreExcellent = Mathf.Max(shadeScoreFloor + 1, (int)list.Slider(shadeScoreExcellent, 5, 80));
                list.Label("Rock score for excellent quality: " + rockScoreExcellent);
                rockScoreExcellent = Mathf.Max(rockScoreFloor + 1, (int)list.Slider(rockScoreExcellent, 5, 120));

                list.Gap();
                list.Label("Attuning length: " + attuningDays + " days");
                attuningDays = (int)list.Slider(attuningDays, 1, 10);
                list.Label("Base ring time (first, innermost ring): " + baseRingDays.ToString("0.0") + " days");
                baseRingDays = list.Slider(baseRingDays, 0.5f, 15f);
                list.Label("Per-ring growth factor: " + ringGrowthFactor.ToString("0.00") + "x");
                ringGrowthFactor = list.Slider(ringGrowthFactor, 1.05f, 3f);

                list.Gap();
                list.Label("Radius cap, poor placement: " + minRadiusCap + " cells");
                minRadiusCap = (int)list.Slider(minRadiusCap, 3, 8);
                list.Label("Radius cap, excellent placement: " + maxRadiusCap + " cells");
                maxRadiusCap = Mathf.Max(minRadiusCap, (int)list.Slider(maxRadiusCap, minRadiusCap, 12));
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_OasisMakerMod : Mod
    {
        public static RM_OasisMakerSettings settings;

        public RM_OasisMakerMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_OasisMakerSettings>();
        }

        public override string SettingsCategory()
        {
            return "Oasis Maker";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
