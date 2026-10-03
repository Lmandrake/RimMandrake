using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // Mod Settings (CLAUDE.md "Every mod ships superb Mod Settings"). Defaults are
    // the shipped behaviour the owner ruled 2026-10-02: riddles that flip to hints,
    // lore offered never pushed, small rewards OFF.
    public class AtlasSettings : ModSettings
    {
        // Detection
        public static bool detectionEnabled = true;
        public static int pollIntervalTicks = 250;

        // Spoilers
        public static bool hintsAllowed = true;      // off: cards stay riddles until found
        public static bool showTrueNameOnHint;       // off: a flipped hint never names the thing
        public static bool showUnavailable = true;   // show entries whose subject is absent from this world
        public static bool showCounters = true;

        // Presentation
        public static bool toastsEnabled = true;
        public static bool flipAnimation = true;
        public static bool lightsPulse = true;

        // Rewards (owner ruling Q5: optional, off by default, future discoveries only)
        public static bool rewardsEnabled;
        public static float rewardScale = 1f;

        // Per-category visibility and detection
        public static List<string> disabledCategories = new List<string>();

        public static bool CategoryEnabled(AtlasCategory c) => !disabledCategories.Contains(c.ToString());

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref detectionEnabled, "detectionEnabled", true);
            Scribe_Values.Look(ref pollIntervalTicks, "pollIntervalTicks", 250);
            Scribe_Values.Look(ref hintsAllowed, "hintsAllowed", true);
            Scribe_Values.Look(ref showTrueNameOnHint, "showTrueNameOnHint", false);
            Scribe_Values.Look(ref showUnavailable, "showUnavailable", true);
            Scribe_Values.Look(ref showCounters, "showCounters", true);
            Scribe_Values.Look(ref toastsEnabled, "toastsEnabled", true);
            Scribe_Values.Look(ref flipAnimation, "flipAnimation", true);
            Scribe_Values.Look(ref lightsPulse, "lightsPulse", true);
            Scribe_Values.Look(ref rewardsEnabled, "rewardsEnabled", false);
            Scribe_Values.Look(ref rewardScale, "rewardScale", 1f);
            Scribe_Collections.Look(ref disabledCategories, "disabledCategories", LookMode.Value);
            if (disabledCategories == null) disabledCategories = new List<string>();
        }

        private static Vector2 scroll;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, 760f);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard();
            list.Begin(view);

            list.Label("<b>Discovery</b>");
            list.CheckboxLabeled("Track discoveries", ref detectionEnabled,
                "Off: the Atlas stops lighting entries. Lights already lit stay lit. The Atlas tab still opens.");
            Rect pollLabel = list.Label("Check for discoveries every " + pollIntervalTicks + " ticks (" + (pollIntervalTicks / 60f).ToString("0.#") + " s at 1x)");
            TooltipHandler.TipRegion(pollLabel, "How often the Atlas looks for durable facts (a creature in view, a canal holding water). Terrain scans run ten times less often. Higher is cheaper, lower is quicker to notice.");
            pollIntervalTicks = Mathf.RoundToInt(list.Slider(pollIntervalTicks, 60f, 2500f) / 10f) * 10;

            list.GapLine();
            list.Label("<b>Spoilers</b>");
            list.CheckboxLabeled("Riddles flip over to hints", ref hintsAllowed,
                "On (default): click a riddle card to turn it over to a plainer hint. Off: undiscovered cards stay riddles.");
            list.CheckboxLabeled("Hints name the thing", ref showTrueNameOnHint,
                "Off (default): a flipped hint says where and how to look, never what the thing is called.");
            list.CheckboxLabeled("Show lights for things absent from this world", ref showUnavailable,
                "An entry whose subject's mod is not loaded is drawn as a dark, crossed-out lamp. Off: such lamps are not drawn.");
            list.CheckboxLabeled("Show counts (lights lit / total)", ref showCounters,
                "Counts tell you how much is left to find. Off for a purer mystery.");

            list.GapLine();
            list.Label("<b>Presentation</b>");
            list.CheckboxLabeled("Message when a light comes on", ref toastsEnabled,
                "A quiet message at the top of the screen. Off: discoveries are silent until you open the Atlas.");
            list.CheckboxLabeled("Animate card flips", ref flipAnimation);
            list.CheckboxLabeled("Lit lamps glow and pulse", ref lightsPulse);

            list.GapLine();
            list.Label("<b>Small rewards</b> (optional; off by default)");
            list.CheckboxLabeled("Grant a small material reward for each new discovery", ref rewardsEnabled,
                "Only discoveries made AFTER you switch this on pay out. Things you had already found never do. Rewards arrive by drop pod near your trade drop spot.");
            if (rewardsEnabled)
            {
                list.Label("Reward size: x" + rewardScale.ToString("0.0#"));
                rewardScale = Mathf.Round(list.Slider(rewardScale, 0.25f, 3f) * 4f) / 4f;
            }

            list.GapLine();
            list.Label("<b>Regions of the ship</b> (off hides the region and stops tracking it)");
            foreach (AtlasCategory c in Enum.GetValues(typeof(AtlasCategory)))
            {
                bool on = CategoryEnabled(c);
                bool was = on;
                list.CheckboxLabeled(("RUT_Atlas_Category_" + c).Translate() + " — " + ("RUT_Atlas_Region_" + c).Translate(), ref on);
                if (on != was)
                {
                    if (on) disabledCategories.Remove(c.ToString());
                    else if (!disabledCategories.Contains(c.ToString())) disabledCategories.Add(c.ToString());
                }
            }

            list.GapLine();
            if (list.ButtonText("Reset all Atlas settings to defaults"))
            {
                detectionEnabled = true; pollIntervalTicks = 250; hintsAllowed = true; showTrueNameOnHint = false;
                showUnavailable = true; showCounters = true; toastsEnabled = true; flipAnimation = true;
                lightsPulse = true; rewardsEnabled = false; rewardScale = 1f; disabledCategories.Clear();
            }

            list.End();
            Widgets.EndScrollView();
        }
    }

    public class AtlasMod : Mod
    {
        public static AtlasSettings settings;

        public AtlasMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<AtlasSettings>();
        }

        public override string SettingsCategory() => "Scavenger's Atlas";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
