using System.Collections.Generic;
using System.Reflection;
// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the restraining-bolt goodwill cap.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
//
// The one mechanism here (GoodwillSituationWorker_RestrainingBolts) computes
// maxGoodwill = 100 - penaltyPerBoltedDroid * N, floored at goodwillFloor. Both
// numbers were hardcoded (2.5 and -70); both are exposed below, plus a master
// off switch that returns the vanilla 100 ceiling unconditionally.
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RestrainingBolts
{
    public class RestrainingBoltsSettings : ModSettings
    {
        public static bool enabled = true;
        public static float penaltyPerBoltedDroid = 2.5f;
        public static float goodwillFloor = -70f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref penaltyPerBoltedDroid, "penaltyPerBoltedDroid", 2.5f);
            Scribe_Values.Look(ref goodwillFloor, "goodwillFloor", -70f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RestrainingBoltsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RestrainingBoltsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): GetMaxGoodwill and CeilingFor run on every goodwill recache and read all three settings each time, nothing at map or world generation, so everything is [now].</summary>
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
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

            if (Group(list, "Goodwill cap", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Cap Free Droid Enclaves goodwill by bolted droids", ref enabled,
                    "Off: your goodwill ceiling with the Free Droid Enclaves is always 100, "
                  + "same as any other faction. Requires Droid Depot to do anything either way.");
                list.GapLine();
            }

            if (Group(list, "Cap size", RimMandrake.Shared.SettingScope.Now, new[] { "penaltyPerBoltedDroid", "goodwillFloor" }))
            {
                list.Label("Goodwill penalty per bolted droid: " + penaltyPerBoltedDroid.ToString("0.0"));
                list.Label("Every droid you own carrying a restraining bolt right now lowers your "
                  + "possible goodwill ceiling with the Enclaves by this much.");
                penaltyPerBoltedDroid = list.Slider(penaltyPerBoltedDroid, 0f, 10f);
                list.Label("Goodwill floor: " + goodwillFloor.ToString("0"));
                list.Label("The ceiling never drops below this, however many droids you bolt "
                  + "(kept above the -75 hostility line by default, leaving margin).");
                goodwillFloor = list.Slider(goodwillFloor, -100f, 0f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RestrainingBoltsMod : Mod
    {
        public static RestrainingBoltsSettings settings;

        public RestrainingBoltsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RestrainingBoltsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Restraining Bolts";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
