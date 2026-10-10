using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Antiquities
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Antiquities.
    //
    // Gates the two real runtime mechanics found in this mod's Source:
    //   1. WorkGiver_ExamineAntiquity offering the reading job at all
    //      (master on/off, degrades gracefully — pawns simply never pick
    //      the job up; nothing is destroyed, nothing NREs).
    //   2. JobDriver_ExamineAntiquity's read duration and "key text" bonus
    //      chance (design doc section 4.2's yield curve) — both were flat
    //      hardcoded numbers, now sliders with the shipped values as
    //      defaults.
    public class AntiquitiesSettings : ModSettings
    {
        public static bool readingEnabled = true;
        public static float durationMultiplier = 1f;
        public static bool keyTextBonusEnabled = true;
        public static float keyTextChanceScale = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref readingEnabled, "readingEnabled", true);
            Scribe_Values.Look(ref durationMultiplier, "durationMultiplier", 1f);
            Scribe_Values.Look(ref keyTextBonusEnabled, "keyTextBonusEnabled", true);
            Scribe_Values.Look(ref keyTextChanceScale, "keyTextChanceScale", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(AntiquitiesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(AntiquitiesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Reading the antiquities", RimMandrake.Shared.SettingScope.Now, new[] { "readingEnabled", "durationMultiplier" }))
            {
                list.CheckboxLabeled("Antiquity reading enabled", ref readingEnabled,
                    "Off: pawns never take the antiquity-reading job. Already-catalogued antiquities "
                  + "and research progress already made are unaffected.");
                list.Label("Reading time: " + durationMultiplier.ToString("0.00") + "x");
                list.Label("Scales how long a pawn spends reading an antiquity at the station "
                         + "(the pawn's own Intellectual/Artistic skill still matters on top of this).");
                durationMultiplier = list.Slider(durationMultiplier, 0.5f, 2f);
                list.GapLine();
            }

            if (Group(list, "Key text bonus", RimMandrake.Shared.SettingScope.Now, new[] { "keyTextBonusEnabled", "keyTextChanceScale" }))
            {
                list.CheckboxLabeled("\"Key text\" bonus reads", ref keyTextBonusEnabled,
                    "Once the LANGUAGE stage is finished, a read has a chance to double its research "
                  + "progress and print a special letter.");
                list.Label("Key text chance: " + keyTextChanceScale.ToString("0.00") + "x the base rate");
                keyTextChanceScale = list.Slider(keyTextChanceScale, 0f, 2f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class AntiquitiesMod : Mod
    {
        public static AntiquitiesSettings settings;

        public AntiquitiesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<AntiquitiesSettings>();
        }

        public override string SettingsCategory() => "Antiquities";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
