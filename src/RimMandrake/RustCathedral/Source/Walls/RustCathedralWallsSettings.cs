using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.RustCathedral.Walls
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RustCathedralWalls.
    //
    // Three mechanisms this mod runs, each gated here:
    //   1. GenStep_ScatterCathedralWallTiers (Tiers 1-2) — worldgen-affecting.
    //   2. GenStep_ScatterSacredWalls (Tier 3, faction-owned wall) — worldgen-
    //      affecting, plus the per-map chance it already carries as a field.
    //   3. HarmonyPatch_GateLivePatternMetal (Tier 4, deep-scan biome gate) —
    //      runs live, whenever a deep scanner picks a resource.
    //
    // 🔑 STATIC FIELDS, READ FROM EVERYWHERE. Class name avoids
    // "RustCathedralWallsMod", already taken by the static Harmony-init class
    // in HarmonyPatch_GateLivePatternMetal.cs.
    public class RustCathedralWallsSettings : ModSettings
    {
        public static bool wallTiersEnabled = true;
        public static bool sacredWallsEnabled = true;
        public static float sacredWallChanceMultiplier = 1f;
        public static bool livePatternMetalGateEnabled = true;

        // NOT CALLED AT RUNTIME (the class is never registered). Kept only as the Scribe inventory that
        // Utils/selftest_settings_screens.py audits this screen against; it must NOT call PatchApplier (the hooks below do).
        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wallTiersEnabled, "wallTiersEnabled", true);
            Scribe_Values.Look(ref sacredWallsEnabled, "sacredWallsEnabled", true);
            Scribe_Values.Look(ref sacredWallChanceMultiplier, "sacredWallChanceMultiplier", 1f);
            Scribe_Values.Look(ref livePatternMetalGateEnabled, "livePatternMetalGateEnabled", true);
        }

        // CATHEDRAL_FORCEDOFF_FIX_SAVED_AS_CHOICE: never registered with Verse; RM_RustCathedralSettings.ExposeData scribes these
        // statics as "walls_*" and calls these hooks, because PatchApplier is internal and this DLL holds its own copy of it.
        public static void PatchBeforeExpose() { RimMandrake.Shared.PatchApplier.BeforeExpose(); }
        public static void PatchAfterExpose() { RimMandrake.Shared.PatchApplier.AfterExpose(); }
        public static void PatchReforceOff() { RimMandrake.Shared.PatchApplier.ReforceOff(); }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RustCathedralWallsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RustCathedralWallsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string> { "unused" };

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope is tagged per group against its read site: wall tiers and sacred walls are read when a map
        /// generates ([new maps only]); the Live Pattern Metal deep-scan gate is read live ([now]).</summary>
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
            RimMandrake.Shared.PatchApplier.DrawNotice(list);

            if (Group(list, "Wall tiers and sacred walls (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "wallTiersEnabled", "sacredWallsEnabled", "sacredWallChanceMultiplier" }))
            {
                list.CheckboxLabeled("Cathedral wall tiers (Tiers 1-2)", ref wallTiersEnabled,
                    "Scatters the low-tier rust cathedral wall fragments on Rust Cathedral maps. Applies to maps generated afterwards.");
                list.CheckboxLabeled("Sacred wall (Tier 3)", ref sacredWallsEnabled,
                    "A rare, faction-owned sacred wall segment placed on Rust Cathedral maps. Applies to maps generated afterwards.");
                list.Label("Sacred wall chance: " + (sacredWallChanceMultiplier * 100f).ToString("0") + "% of the base rate");
                sacredWallChanceMultiplier = list.Slider(sacredWallChanceMultiplier, 0f, 2f);
                list.GapLine();
            }

            if (Group(list, "Live Pattern Metal", RimMandrake.Shared.SettingScope.Now, new[] { "livePatternMetalGateEnabled" }))
            {
                list.CheckboxLabeled("Restrict Live Pattern Metal to the Rust Cathedral", ref livePatternMetalGateEnabled,
                    "Off: deep scanners anywhere may find Live Pattern Metal, same as an unpatched game.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    // RUSTCATHEDRAL_RM_MOD_BUILD_1: the standalone RustCathedralWallsSettingsMod
    // wrapper (one Mod-derived class per satellite kit) is RETIRED now that
    // Hum/Walls/Roaches/the biome all ship in one mod, mandrake.rm.rustcathedral.
    // This settings DATA class is still read from everywhere it always was and
    // is drawn on the single RimMandrake.RustCathedral.RM_RustCathedralMod
    // settings screen. It is NEVER registered with Verse (no GetSettings call;
    // RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1): RM_RustCathedralSettings.ExposeData
    // scribes its static fields directly under "walls_*" keys.
}
