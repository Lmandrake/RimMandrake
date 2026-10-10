using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // §12 Mod Settings: a toggle each for the gale, abrasion, carry, static, emergence
    // (plus per-row toggles) and dust devils; frequency sliders. Defaults are shipped
    // behaviour. All off: the biome keeps Odyssey's own sandstorm and nothing else.
    // ════════════════════════════════════════════════════════════════════
    public class RM_DuneGaleSettings : ModSettings
    {
        public static bool galeEnabled = true;
        public static float galeFrequency = 1f;
        public static bool abrasionEnabled = true;
        public static bool carryEnabled = true;
        public static bool staticEnabled = true;
        public static bool emergenceEnabled = true;
        public static bool seedingEnabled = true;
        public static bool dustDevilsEnabled = true;
        public static float dustDevilFrequency = 1f;
        private static Dictionary<string, bool> emergenceOff = new Dictionary<string, bool>();

        public static bool EmergenceAllowed(string key)
        {
            return key.NullOrEmpty() || !(emergenceOff.TryGetValue(key, out bool off) && off);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref galeEnabled, "galeEnabled", true);
            Scribe_Values.Look(ref galeFrequency, "galeFrequency", 1f);
            Scribe_Values.Look(ref abrasionEnabled, "abrasionEnabled", true);
            Scribe_Values.Look(ref carryEnabled, "carryEnabled", true);
            Scribe_Values.Look(ref staticEnabled, "staticEnabled", true);
            Scribe_Values.Look(ref emergenceEnabled, "emergenceEnabled", true);
            Scribe_Values.Look(ref seedingEnabled, "seedingEnabled", true);
            Scribe_Values.Look(ref dustDevilsEnabled, "dustDevilsEnabled", true);
            Scribe_Values.Look(ref dustDevilFrequency, "dustDevilFrequency", 1f);
            Scribe_Collections.Look(ref emergenceOff, "emergenceOff", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                emergenceOff = emergenceOff ?? new Dictionary<string, bool>();
            }
        }

        /// <summary>One checkbox per emergence row of every gale def, shown while emergence is on.</summary>
        private static void DrawEmergenceRows(Listing_Standard list)
        {
            IEnumerable<RM_GaleEmergence> rows = DefDatabase<GameConditionDef>.AllDefsListForReading
                .Select(d => d.GetModExtension<RM_DuneGaleExtension>())
                .Where(e => e != null)
                .SelectMany(e => e.emergences)
                .Where(r => !r.key.NullOrEmpty());
            foreach (RM_GaleEmergence r in rows)
            {
                bool on = EmergenceAllowed(r.key);
                list.CheckboxLabeled("    " + (r.letterLabel ?? r.key), ref on);
                emergenceOff[r.key] = !on;
            }
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_DuneGaleSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                if (n == "emergenceOff") { emergenceOff.Clear(); continue; }
                FieldInfo f = typeof(RM_DuneGaleSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the gale and dust-devil switches are read in TryExecute and their frequencies in BaseChanceThisGame (storyteller rolls, NextPulse); abrasion, carry and static are read on gale ticks and emergence and seeding at gale end (Now).</summary>
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
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "The dune gale", RimMandrake.Shared.SettingScope.NextPulse, new[] { "galeEnabled", "galeFrequency" }))
            {
                list.CheckboxLabeled("Dune gale", ref galeEnabled,
                    "The Stillsand's own storm: a herald, one to two days of gale, then one thing the wind uncovers. "
                    + "Off: it never fires; Odyssey's sandstorm is unaffected.");
                list.Label("Gale frequency: x" + galeFrequency.ToString("0.00"));
                galeFrequency = Mathf.Round(list.Slider(galeFrequency, 0f, 3f) * 20f) / 20f;
                list.GapLine();
            }

            if (Group(list, "Gale effects", RimMandrake.Shared.SettingScope.Now, new[] { "abrasionEnabled", "carryEnabled", "staticEnabled" }))
            {
                list.CheckboxLabeled("Abrasion", ref abrasionEnabled,
                    "Exposed pawns take slow scratches; light walls and thin roof edges wear.");
                list.CheckboxLabeled("Carry", ref carryEnabled,
                    "Light pawns and animals in the open on a crest can be dragged downwind. One carried off the "
                    + "edge gets a letter and always comes back, alive or not.");
                list.CheckboxLabeled("Gale static", ref staticEnabled,
                    "Charged dust: brief stuns on turrets and mechanoids, sparks on metal.");
                list.GapLine();
            }

            if (Group(list, "What the wind uncovers at gale end", RimMandrake.Shared.SettingScope.Now, new[] { "emergenceEnabled", "emergenceOff", "seedingEnabled" }))
            {
                list.CheckboxLabeled("Emergence", ref emergenceEnabled,
                    "At gale end the wind uncovers one thing near a fresh erosion face, with a letter.");
                if (emergenceEnabled)
                {
                    DrawEmergenceRows(list);
                }
                list.CheckboxLabeled("Seeding", ref seedingEnabled,
                    "Gale end wakes dormant dust husks nearby, lays glasscrust, and blooms hourbloom at any water.");
                list.GapLine();
            }

            if (Group(list, "Dust devils", RimMandrake.Shared.SettingScope.NextPulse, new[] { "dustDevilsEnabled", "dustDevilFrequency" }))
            {
                list.CheckboxLabeled("Dust devils", ref dustDevilsEnabled,
                    "A fair-weather column that wanders the flat, lifts light items and spooks animals. Never damages.");
                list.Label("Dust devil frequency: x" + dustDevilFrequency.ToString("0.00"));
                dustDevilFrequency = Mathf.Round(list.Slider(dustDevilFrequency, 0f, 3f) * 20f) / 20f;
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_DuneGaleMod : Mod
    {
        public static RM_DuneGaleSettings settings;

        public RM_DuneGaleMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_DuneGaleSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand: dune gale";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
