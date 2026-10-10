using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ScarlandsLadder
{
    // MOD_OPTIONS_RETROFIT_1 settings for the Scarlands ladder (moved out of PilgrimCamps.cs so the screen check reads one file).
    public class ScarlandsLadderSettings : ModSettings
    {
        public static bool campsEnabled = true;             // camps generate on new RUT_Scarlands maps
        public static float campsPerMap = 1f;               // 0-3, new maps
        public static bool journalsAdvanceLadder = true;    // reading a journal moves the Scarlands ladder

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref campsEnabled, "campsEnabled", true);
            Scribe_Values.Look(ref campsPerMap, "campsPerMap", 1f);
            Scribe_Values.Look(ref journalsAdvanceLadder, "journalsAdvanceLadder", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(ScarlandsLadderSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(ScarlandsLadderSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Pilgrim camps (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "campsEnabled", "campsPerMap" }))
            {
                list.CheckboxLabeled("Pilgrim camps on Scarlands maps", ref campsEnabled,
                    "A cold fire, a bedroll, the pilgrim who never left, and a journal. Placed while a Scarlands map is generated; existing maps keep theirs.");
                list.Label((TaggedString)("Camps per map (up to): " + Mathf.RoundToInt(campsPerMap).ToString()), -1f, "Rounded to a whole number when a map is generated.");
                campsPerMap = list.Slider(campsPerMap, 0f, 3f);
                list.GapLine();
            }

            if (Group(list, "Reading the journals", RimMandrake.Shared.SettingScope.Now, new[] { "journalsAdvanceLadder" }))
            {
                list.CheckboxLabeled("Reading a pilgrim's journal teaches the Scarlands", ref journalsAdvanceLadder,
                    "Each journal read moves the Scarlands' description one stage further. Off: the journals can still be read, but teach nothing. Read at the moment of reading.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class ScarlandsLadderMod : Mod
    {
        public static ScarlandsLadderSettings settings;

        public ScarlandsLadderMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ScarlandsLadderSettings>();
        }

        public override string SettingsCategory()
        {
            return "Scarlands Ladder";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
