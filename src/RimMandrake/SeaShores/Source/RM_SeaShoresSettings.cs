using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.SeaShores
{
    // MOD_OPTIONS_RETROFIT_1. Four switches, one per mechanic, defaults = shipped
    // behaviour. Fields are INSTANCE fields reached through Cur, not public
    // statics: the bridge's rimworld/update_mod_settings reflects over instance
    // fields on the ModSettings object and refuses a static one outright
    // (found live 2026-09-12 on the Pits pilot).
    public class RM_SeaShoresSettings : ModSettings
    {
        public bool seasCountAsCoast = true;
        public bool generateSeaShores = true;
        public bool seaCatchTables = true;
        public bool healFrozenWorldOnLoad = true;

        private static readonly RM_SeaShoresSettings Defaults = new RM_SeaShoresSettings();

        // Every read goes through here so the patches are safe before (or
        // without) the Mod class being constructed — a null settings object
        // degrades to shipped defaults rather than an NRE inside a Harmony
        // patch, which would be unrecoverable at worldgen time.
        public static RM_SeaShoresSettings Cur => RM_SeaShoresMod.settings ?? Defaults;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seasCountAsCoast, "seasCountAsCoast", true);
            Scribe_Values.Look(ref generateSeaShores, "generateSeaShores", true);
            Scribe_Values.Look(ref seaCatchTables, "seaCatchTables", true);
            Scribe_Values.Look(ref healFrozenWorldOnLoad, "healFrozenWorldOnLoad", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public instance bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();  // instance settings: read from a fresh instance

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var fresh = new RM_SeaShoresSettings();
            foreach (FieldInfo f in typeof(RM_SeaShoresSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(fresh);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_SeaShoresSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
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

            // Scopes audited per read site (2026-10-10): coast direction is a Harmony postfix answered on every query (now);
            // shore generation is read by the sea-coast tile mutator while a map generates; the catch-table swap is read on each fishing
            // lookup; the heal runs once in the world component's FinalizeInit when a save loads.
            if (Group(list, "Modded seas count as coastline", RimMandrake.Shared.SettingScope.Now, new[] { "seasCountAsCoast" }))
            {
                list.CheckboxLabeled("Modded seas count as coastline", ref seasCountAsCoast,
                    "A land tile bordering a modded sea reads as coastal: coastal animals spawn there, "
                  + "attackers can emerge from the water, and river deltas can form. "
                  + "Off: only the vanilla ocean makes a tile coastal.");
                list.GapLine();
            }

            if (Group(list, "Shores beside a modded sea (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "generateSeaShores" }))
            {
                list.CheckboxLabeled("Generate shores on maps beside a modded sea", ref generateSeaShores,
                    "Maps on those tiles get a real shore - the sea's own deep and shallow water, "
                  + "then the land's beach. Off: the tile may still read as coastal, but the map "
                  + "generates with no water at its edge.\n\nAffects world and map generation.");
                list.GapLine();
            }

            if (Group(list, "Fishing", RimMandrake.Shared.SettingScope.Now, new[] { "seaCatchTables" }))
            {
                list.CheckboxLabeled("Fish the sea's catch table, not the land's", ref seaCatchTables,
                    "Fishing a shore made of a modded sea's water pulls that sea's own fish, including "
                  + "its rare catches. Off: the land biome's fish are used, as in vanilla.");
                list.GapLine();
            }

            if (Group(list, "Repair existing worlds", RimMandrake.Shared.SettingScope.Now, new[] { "healFrozenWorldOnLoad" }, "[next game start]"))
            {
                list.CheckboxLabeled("Repair existing worlds on load", ref healFrozenWorldOnLoad,
                    "Tile mutators are saved with the world, so a planet created before this mod was "
                  + "installed has no shores beside its modded seas and will never regenerate. This "
                  + "adds them on load, once, to tiles that have no coastline of any kind yet. Harmless "
                  + "to run repeatedly.\n\nAffects an existing saved world.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }
}
