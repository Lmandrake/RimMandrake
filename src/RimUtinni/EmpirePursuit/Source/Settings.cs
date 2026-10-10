using System.Reflection;
/* Ported from Ruthless Faction Pursuit (workshop 3621784437) by Matathias, GPLv3.
 * See ../../LICENSE.txt and About.xml for the fork's credit and scope.
 * MODIFIED 2026-10-06 (EMPIRE_ESCALATION_LADDER_1): the escalation ladder's settings,
 * design doc §6. All on = the ladder as designed; ladder off = upstream's flat pursuit. */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Verse;

namespace RuthlessPursuingMechanoids
{
    public class RFPSettings : ModSettings
    {
        public static bool printDebug = false;

        /* EMPIRE_ESCALATION_LADDER_1 — defaults are the shipped behaviour (PROVISIONAL numbers). */
        public static bool ladderEnabled = true;
        public static bool probesOpen = true;
        public static float ladderPace = 1f;
        public static bool visibilityDrivesPace = true;
        public static bool rememberRungs = true;
        public static int rungDecayPerSeason = 1;
        public static bool cordonEnabled = true;
        public static float ionLockoutHours = 6f;
        public static float ionVolleyIntervalHours = 8f;
        public static bool bombardmentEnabled = true;
        public static bool endlessAfterTop = true;
        public static bool showSearchAlert = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref printDebug, "printDebug", false, true);
            Scribe_Values.Look(ref ladderEnabled, "ladderEnabled", true, true);
            Scribe_Values.Look(ref probesOpen, "probesOpen", true, true);
            Scribe_Values.Look(ref ladderPace, "ladderPace", 1f, true);
            Scribe_Values.Look(ref visibilityDrivesPace, "visibilityDrivesPace", true, true);
            Scribe_Values.Look(ref rememberRungs, "rememberRungs", true, true);
            Scribe_Values.Look(ref rungDecayPerSeason, "rungDecayPerSeason", 1, true);
            Scribe_Values.Look(ref cordonEnabled, "cordonEnabled", true, true);
            Scribe_Values.Look(ref ionLockoutHours, "ionLockoutHours", 6f, true);
            Scribe_Values.Look(ref ionVolleyIntervalHours, "ionVolleyIntervalHours", 8f, true);
            Scribe_Values.Look(ref bombardmentEnabled, "bombardmentEnabled", true, true);
            Scribe_Values.Look(ref endlessAfterTop, "endlessAfterTop", true, true);
            Scribe_Values.Look(ref showSearchAlert, "showSearchAlert", true, true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RFPSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RFPSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Debug", RimMandrake.Shared.SettingScope.Now, new[] { "printDebug" }))
            {
                list.CheckboxLabeled("printDebug".Translate(), ref printDebug);
                list.GapLine();
            }

            if (Group(list, "Escalation ladder", RimMandrake.Shared.SettingScope.Now, new[] { "ladderEnabled", "ladderPace", "visibilityDrivesPace", "endlessAfterTop", "showSearchAlert" }))
            {
                list.CheckboxLabeled("RUT_Ladder_Enabled".Translate(), ref ladderEnabled, "RUT_Ladder_EnabledDesc".Translate());
                list.Label("RUT_Ladder_Pace".Translate(ladderPace.ToString("0.00")));
                ladderPace = list.Slider(ladderPace, 0.25f, 4f);
                list.CheckboxLabeled("RUT_Ladder_VisibilityPace".Translate(), ref visibilityDrivesPace, "RUT_Ladder_VisibilityPaceDesc".Translate());
                list.CheckboxLabeled("RUT_Ladder_Endless".Translate(), ref endlessAfterTop);
                list.CheckboxLabeled("RUT_Ladder_Alert".Translate(), ref showSearchAlert);
                list.GapLine();
            }

            if (Group(list, "Which rungs fire", RimMandrake.Shared.SettingScope.NextPulse, new[] { "probesOpen", "cordonEnabled", "bombardmentEnabled" }))
            {
                list.CheckboxLabeled("RUT_Ladder_ProbesOpen".Translate(), ref probesOpen, "RUT_Ladder_ProbesOpenDesc".Translate());
                list.CheckboxLabeled("RUT_Ladder_Cordon".Translate(), ref cordonEnabled, "RUT_Ladder_CordonDesc".Translate());
                list.CheckboxLabeled("RUT_Ladder_Bombardment".Translate(), ref bombardmentEnabled, "RUT_Ladder_BombardmentDesc".Translate());
                list.GapLine();
            }

            if (Group(list, "Rung memory", RimMandrake.Shared.SettingScope.NextPulse, new[] { "rememberRungs", "rungDecayPerSeason" }))
            {
                list.CheckboxLabeled("RUT_Ladder_Remember".Translate(), ref rememberRungs, "RUT_Ladder_RememberDesc".Translate());
                list.Label("RUT_Ladder_Decay".Translate(rungDecayPerSeason));
                rungDecayPerSeason = Mathf.RoundToInt(list.Slider(rungDecayPerSeason, 0f, 3f));
                list.GapLine();
            }

            if (Group(list, "Ion cordon timing", RimMandrake.Shared.SettingScope.Now, new[] { "ionLockoutHours", "ionVolleyIntervalHours" }))
            {
                list.Label("RUT_Ladder_IonLockout".Translate(ionLockoutHours.ToString("0")));
                ionLockoutHours = Mathf.Round(list.Slider(ionLockoutHours, 1f, 23f));
                list.Label("RUT_Ladder_IonVolleyInterval".Translate(ionVolleyIntervalHours.ToString("0")));
                ionVolleyIntervalHours = Mathf.Round(list.Slider(ionVolleyIntervalHours, 1f, 24f));
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

    }
    public class RFPMod : Mod
    {
        public static RFPSettings settings = new RFPSettings();

        public RFPMod(ModContentPack content) : base(content)
        {
            Pack = content;
            settings = GetSettings<RFPSettings>();
        }

        public ModContentPack Pack { get; }

        public override string SettingsCategory() => Pack.Name;

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }
}
