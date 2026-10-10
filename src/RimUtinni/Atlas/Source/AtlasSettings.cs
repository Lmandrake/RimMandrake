using System.Reflection;
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

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(AtlasSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                if (n == "disabledCategories") { disabledCategories.Clear(); continue; }
                FieldInfo f = typeof(AtlasSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

        // Local bool for the checkbox's ref; kept out of DoWindowContents so the screen check sees only the persisted fields.
        private static void DrawCategory(Listing_Standard list, AtlasCategory c)
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

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Discovery", RimMandrake.Shared.SettingScope.Now, new[] { "detectionEnabled", "pollIntervalTicks" }))
            {
                list.CheckboxLabeled("Track discoveries", ref detectionEnabled,
                    "Off: the Atlas stops lighting entries. Lights already lit stay lit. The Atlas tab still opens.");
                Rect pollLabel = list.Label("Check for discoveries every " + pollIntervalTicks + " ticks (" + (pollIntervalTicks / 60f).ToString("0.#") + " s at 1x)");
                TooltipHandler.TipRegion(pollLabel, "How often the Atlas looks for durable facts (a creature in view, a canal holding water). Terrain scans run ten times less often. Higher is cheaper, lower is quicker to notice.");
                pollIntervalTicks = Mathf.RoundToInt(list.Slider(pollIntervalTicks, 60f, 2500f) / 10f) * 10;
                list.GapLine();
            }

            if (Group(list, "Spoilers", RimMandrake.Shared.SettingScope.Now, new[] { "hintsAllowed", "showTrueNameOnHint", "showUnavailable", "showCounters" }))
            {
                list.CheckboxLabeled("Riddles flip over to hints", ref hintsAllowed,
                    "On (default): click a riddle card to turn it over to a plainer hint. Off: undiscovered cards stay riddles.");
                list.CheckboxLabeled("Hints name the thing", ref showTrueNameOnHint,
                    "Off (default): a flipped hint says where and how to look, never what the thing is called.");
                list.CheckboxLabeled("Show lights for things absent from this world", ref showUnavailable,
                    "An entry whose subject's mod is not loaded is drawn as a dark, crossed-out lamp. Off: such lamps are not drawn.");
                list.CheckboxLabeled("Show counts (lights lit / total)", ref showCounters,
                    "Counts tell you how much is left to find. Off for a purer mystery.");
                list.GapLine();
            }

            if (Group(list, "Presentation", RimMandrake.Shared.SettingScope.Now, new[] { "flipAnimation", "lightsPulse" }))
            {
                list.CheckboxLabeled("Animate card flips", ref flipAnimation);
                list.CheckboxLabeled("Lit lamps glow and pulse", ref lightsPulse);
                list.GapLine();
            }

            if (Group(list, "On a new discovery: message and small rewards", RimMandrake.Shared.SettingScope.NextPulse, new[] { "toastsEnabled", "rewardsEnabled", "rewardScale" }))
            {
                list.CheckboxLabeled("Message when a light comes on", ref toastsEnabled,
                    "A quiet message at the top of the screen. Off: discoveries are silent until you open the Atlas.");
                list.CheckboxLabeled("Grant a small material reward for each new discovery", ref rewardsEnabled,
                    "Only discoveries made AFTER you switch this on pay out. Things you had already found never do. Rewards arrive by drop pod near your trade drop spot. Optional; off by default.");
                list.Label("Reward size: x" + rewardScale.ToString("0.0#"));
                rewardScale = Mathf.Round(list.Slider(rewardScale, 0.25f, 3f) * 4f) / 4f;
                list.GapLine();
            }

            if (Group(list, "Regions of the ship", RimMandrake.Shared.SettingScope.Now, new[] { "disabledCategories" }))
            {
                list.Label("Off hides the region and stops tracking it.");
                foreach (AtlasCategory c in Enum.GetValues(typeof(AtlasCategory))) DrawCategory(list, c);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
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
