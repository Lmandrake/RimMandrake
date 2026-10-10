using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Watchers
{
    // WATCHER_CREATURES_MOD_1, design §6. Defaults = shipped behaviour. All off = the members are
    // ordinary small animals that never hide. The readable sign has no toggle: it is the "no animal
    // vanishes" rule, not a feature. Scroll view per the Webwork fix (cfdba9344): maxOneColumn is
    // load-bearing, or the overflow wraps into a hidden second column and the view never grows.
    public class RM_WatchersSettings : ModSettings
    {
        public static bool watchersEnabled = true;
        public static bool hideAndFlinch = true;
        public static bool turnToFace = true;
        public static bool stayOnMedium = true;
        public static bool geophone = true;
        public static bool alarmRipple = true;       // owner ruling 2026-10-08: the bounded alarm ripple has its own toggle
        public static float flinchRadiusScale = 1f;   // PROVISIONAL range 0.5-2 (design §6 gives 3-12 cells around 6)
        public static float emergeDelayScale = 1f;    // PROVISIONAL range 0.25-3 (design §6: "1-3 h, slider")
        public static int maxActivePerMap = 40;       // design §6 default; PROVISIONAL range 5-200
        // The optional non-body cues (owner ruling 2026-10-08, "Full set"): one toggle per kind; a member only reacts to the kinds it lists.
        public static bool cueGas = true;
        public static bool cueHeat = true;
        public static bool cueFire = true;
        public static bool cueSteam = true;
        public static bool cueShade = true;
        public static bool cueBuried = true;
        public static bool cueLight = true;
        // The Rust Cathedral Watcher's own section (pitch 5.6). Scribe keys equal the field names (they were always these keys).
        public static bool watcherStalkEnabled = true;       // off: the Watcher never raises its stalk
        public static bool watcherStalkAnimation = true;     // off: no rise/retract animation
        public static bool watcherStalkSmoothTracking = true; // off: the head snaps to eight directions

        public static bool HideActive => watchersEnabled && hideAndFlinch;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref watchersEnabled, "watchersEnabled", true);
            Scribe_Values.Look(ref hideAndFlinch, "hideAndFlinch", true);
            Scribe_Values.Look(ref turnToFace, "turnToFace", true);
            Scribe_Values.Look(ref stayOnMedium, "stayOnMedium", true);
            Scribe_Values.Look(ref geophone, "geophone", true);
            Scribe_Values.Look(ref alarmRipple, "alarmRipple", true);
            Scribe_Values.Look(ref watcherStalkEnabled, "watcherStalkEnabled", true);
            Scribe_Values.Look(ref watcherStalkAnimation, "watcherStalkAnimation", true);
            Scribe_Values.Look(ref watcherStalkSmoothTracking, "watcherStalkSmoothTracking", true);
            Scribe_Values.Look(ref flinchRadiusScale, "flinchRadiusScale", 1f);
            Scribe_Values.Look(ref emergeDelayScale, "emergeDelayScale", 1f);
            Scribe_Values.Look(ref maxActivePerMap, "maxActivePerMap", 40);
            Scribe_Values.Look(ref cueGas, "cueGas", true);
            Scribe_Values.Look(ref cueHeat, "cueHeat", true);
            Scribe_Values.Look(ref cueFire, "cueFire", true);
            Scribe_Values.Look(ref cueSteam, "cueSteam", true);
            Scribe_Values.Look(ref cueShade, "cueShade", true);
            Scribe_Values.Look(ref cueBuried, "cueBuried", true);
            Scribe_Values.Look(ref cueLight, "cueLight", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_WatchersSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_WatchersSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Mod switch", RimMandrake.Shared.SettingScope.Now, new[] { "watchersEnabled" }))
            {
                list.CheckboxLabeled("RM_Watchers_Setting_Enabled".Translate(), ref watchersEnabled,
                    "RM_Watchers_Setting_Enabled_Tip".Translate());
                list.GapLine();
            }

            if (Group(list, "Watcher behaviour", RimMandrake.Shared.SettingScope.Now, new[] { "hideAndFlinch", "turnToFace", "stayOnMedium", "geophone", "alarmRipple" }))
            {
                list.CheckboxLabeled("RM_Watchers_Setting_Hide".Translate(), ref hideAndFlinch,
                    "RM_Watchers_Setting_Hide_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Face".Translate(), ref turnToFace,
                    "RM_Watchers_Setting_Face_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Medium".Translate(), ref stayOnMedium,
                    "RM_Watchers_Setting_Medium_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Geophone".Translate(), ref geophone,
                    "RM_Watchers_Setting_Geophone_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_Alarm".Translate(), ref alarmRipple,
                    "RM_Watchers_Setting_Alarm_Tip".Translate());
                list.GapLine();
            }

            if (Group(list, "Other things they hide from", RimMandrake.Shared.SettingScope.Now, new[] { "cueGas", "cueHeat", "cueFire", "cueSteam", "cueShade", "cueBuried", "cueLight" }))
            {
                list.Label("RM_Watchers_Setting_CuesHeader".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueGas".Translate(), ref cueGas, "RM_Watchers_Setting_CueGas_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueHeat".Translate(), ref cueHeat, "RM_Watchers_Setting_CueHeat_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueFire".Translate(), ref cueFire, "RM_Watchers_Setting_CueFire_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueSteam".Translate(), ref cueSteam, "RM_Watchers_Setting_CueSteam_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueShade".Translate(), ref cueShade, "RM_Watchers_Setting_CueShade_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueBuried".Translate(), ref cueBuried, "RM_Watchers_Setting_CueBuried_Tip".Translate());
                list.CheckboxLabeled("RM_Watchers_Setting_CueLight".Translate(), ref cueLight, "RM_Watchers_Setting_CueLight_Tip".Translate());
                list.GapLine();
            }

            if (Group(list, "Flinch, hiding and crowd size", RimMandrake.Shared.SettingScope.Now, new[] { "flinchRadiusScale", "emergeDelayScale", "maxActivePerMap" }))
            {
                list.Label("RM_Watchers_Setting_FlinchRadius".Translate(flinchRadiusScale.ToStringPercent()));
                flinchRadiusScale = Mathf.Round(list.Slider(flinchRadiusScale, 0.5f, 2f) * 20f) / 20f;
                list.Label("RM_Watchers_Setting_EmergeDelay".Translate(emergeDelayScale.ToStringPercent()));
                emergeDelayScale = Mathf.Round(list.Slider(emergeDelayScale, 0.25f, 3f) * 20f) / 20f;
                list.Label("RM_Watchers_Setting_MaxActive".Translate(maxActivePerMap));
                maxActivePerMap = Mathf.RoundToInt(list.Slider(maxActivePerMap, 5f, 200f));
                list.GapLine();
            }

            if (Group(list, "The Watcher (Rust Cathedral)", RimMandrake.Shared.SettingScope.Now, new[] { "watcherStalkEnabled", "watcherStalkAnimation", "watcherStalkSmoothTracking" }))
            {
                list.CheckboxLabeled("RM_WatcherStalk_Setting_Enabled".Translate(), ref watcherStalkEnabled, "RM_WatcherStalk_Setting_Enabled_Tip".Translate());
                list.CheckboxLabeled("RM_WatcherStalk_Setting_Animation".Translate(), ref watcherStalkAnimation,
                    "RM_WatcherStalk_Setting_Animation_Tip".Translate());
                list.CheckboxLabeled("RM_WatcherStalk_Setting_Smooth".Translate(), ref watcherStalkSmoothTracking,
                    "RM_WatcherStalk_Setting_Smooth_Tip".Translate());
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_WatchersMod : Mod
    {
        public static RM_WatchersSettings settings;

        public RM_WatchersMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WatchersSettings>();
        }

        public override string SettingsCategory()
        {
            return "RM_Watchers_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
