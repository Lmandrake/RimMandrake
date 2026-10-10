using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SKELETONS_TRACKS_1 §9 — Mod Settings for the skeletons and
    // the horizon. Its own Mod class (as RM_StillsandEventsMod), so the
    // biome's settings file stays out of this item's diff. Defaults are the
    // shipped behaviour; all off leaves the biome whole (no skeletons are
    // placed, corpses stay corpses, raids arrive unannounced as in vanilla).
    //
    // Track persistence is NOT here: the tracks ride FOOTPRINT_TRACK_GRID_1,
    // whose own settings carry the on/off switch (it is not built yet).
    // ════════════════════════════════════════════════════════════════════
    public class RM_SkeletonSettings : ModSettings
    {
        public static bool skeletonPlacementEnabled = true;
        public static int maxSkeletonsPerMap = 2;
        public static bool corpseToSkeletonEnabled = true;
        public static float corpseToSkeletonDays = 15f;
        public static bool boneHarpEnabled = true;
        public static bool horizonWarningsEnabled = true;
        public static float horizonWarningHours = 3f;
        public static bool horizonPassersEnabled = true;
        public static bool dustSettledLetterEnabled = true;
        public static bool duneBurialEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref skeletonPlacementEnabled, "skeletonPlacementEnabled", true);
            Scribe_Values.Look(ref maxSkeletonsPerMap, "maxSkeletonsPerMap", 2);
            Scribe_Values.Look(ref corpseToSkeletonEnabled, "corpseToSkeletonEnabled", true);
            Scribe_Values.Look(ref corpseToSkeletonDays, "corpseToSkeletonDays", 15f);
            Scribe_Values.Look(ref boneHarpEnabled, "boneHarpEnabled", true);
            Scribe_Values.Look(ref horizonWarningsEnabled, "horizonWarningsEnabled", true);
            Scribe_Values.Look(ref horizonWarningHours, "horizonWarningHours", 3f);
            Scribe_Values.Look(ref horizonPassersEnabled, "horizonPassersEnabled", true);
            Scribe_Values.Look(ref dustSettledLetterEnabled, "dustSettledLetterEnabled", true);
            Scribe_Values.Look(ref duneBurialEnabled, "duneBurialEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_SkeletonSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_SkeletonSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): skeleton placement is a GenStep (NewMapsOnly); the horizon warning and passer gates and the warning hours are read as each incident is fired (NextPulse); corpse scan, harp, dune burial and the settled letter are read per tick (Now).</summary>
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

            list.Label("The giants' bones, and the empty horizon.");
            list.GapLine();

            if (Group(list, "Giant skeletons on new maps (fixed at map generation)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "skeletonPlacementEnabled", "maxSkeletonsPerMap" }))
            {
                list.CheckboxLabeled("Giant skeletons on new maps (map generation)", ref skeletonPlacementEnabled,
                    "Each new Stillsand map carries a few giant skeletons: ribs that throw striped shade, a skull "
                    + "you can shelter in, often an ollim growing among them. Affects map generation only.");
                if (skeletonPlacementEnabled)
                {
                    list.Label("Most skeletons per map: " + maxSkeletonsPerMap);
                    maxSkeletonsPerMap = (int)list.Slider(maxSkeletonsPerMap, 0, 2);
                }
                list.GapLine();
            }

            if (Group(list, "Giant corpses become skeletons", RimMandrake.Shared.SettingScope.Now, new[] { "corpseToSkeletonEnabled", "corpseToSkeletonDays" }))
            {
                list.CheckboxLabeled("Giant corpses become skeletons", ref corpseToSkeletonEnabled,
                    "A giant that dies on the open sand dries out and, after a while, stands where it fell as "
                    + "its skeleton. Off: its corpse stays a corpse.");
                if (corpseToSkeletonEnabled)
                {
                    list.Label("Days until a corpse is a skeleton: " + corpseToSkeletonDays.ToString("0"));
                    corpseToSkeletonDays = Mathf.Round(list.Slider(corpseToSkeletonDays, 1f, 60f));
                }
                list.GapLine();
            }

            if (Group(list, "Bone harps and dune burial", RimMandrake.Shared.SettingScope.Now, new[] { "boneHarpEnabled", "duneBurialEnabled" }))
            {
                list.CheckboxLabeled("Bone harps", ref boneHarpEnabled,
                    "Wind across a skeleton's ribs makes a low moan that rises with the wind, so you can find "
                    + "one by ear. Off: skeletons are silent.");
                list.CheckboxLabeled("Dunes bury and strip skeletons", ref duneBurialEnabled,
                    "Where the moving dunes pile drift over a skeleton it is buried to its top arcs: drawn sand-coloured, "
                    + "its harp silent. When the sand moves on it is stripped clean again, with a message each time. "
                    + "Off: skeletons stay clean whatever the sand does. Safe mid-game.");
                list.GapLine();
            }

            if (Group(list, "Dust on the horizon", RimMandrake.Shared.SettingScope.NextPulse, new[] { "horizonWarningsEnabled", "horizonWarningHours", "horizonPassersEnabled" }))
            {
                list.CheckboxLabeled("Dust on the horizon", ref horizonWarningsEnabled,
                    "On open sand nothing hides: raids and caravans are seen hours before they arrive, as a dust "
                    + "plume at the map edge and a letter giving the bearing. Off: they arrive as in vanilla.");
                if (horizonWarningsEnabled)
                {
                    list.Label("Hours of warning: " + horizonWarningHours.ToString("0.0"));
                    horizonWarningHours = Mathf.Round(list.Slider(horizonWarningHours, 0.5f, 8f) * 2f) / 2f;
                    list.CheckboxLabeled("  ...and wandering giants", ref horizonPassersEnabled,
                        "Herd migrations and passing giants (thrumbo-style passes) are seen coming too: the same letter, "
                        + "plume and bearing, and they really enter from that bearing. Off: they arrive unannounced.");
                }
                list.GapLine();
            }

            if (Group(list, "Dust-settled letter", RimMandrake.Shared.SettingScope.Now, new[] { "dustSettledLetterEnabled" }))
            {
                list.CheckboxLabeled("Tell me when the dust settles", ref dustSettledLetterEnabled,
                    "If a group announced by dust on the horizon never arrives, a short letter says the dust settled and "
                    + "they turned back. The plume stays up until the group really arrives or the wait runs out. Off: the "
                    + "plume just fades.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_SkeletonMod : Mod
    {
        public static RM_SkeletonSettings settings;

        public RM_SkeletonMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SkeletonSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand: skeletons and horizon";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
