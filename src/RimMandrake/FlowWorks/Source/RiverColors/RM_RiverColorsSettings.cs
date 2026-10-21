using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.RiverColors
{
    /// <summary>
    /// The "River colours" section of FlowWorks' Mod Settings. River Colors was its own mod (mandrake.rut.rivercolors,
    /// its own ModSettings + Mod subclass) until RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW (owner 2026-10-16: "Add river
    /// colors into flowworks as part of adding liquids to the world."). Same shape as the Rivers and Hose sections: not a
    /// ModSettings of its own; RimMandrakeFlowWorksSettings.ExposeData scribes these fields into FlowWorks' one settings
    /// file under a `riverColors_` key prefix (keys unique across that file; selftest_flowworks_river_colors.py checks),
    /// and its window draws DoSettingsSection.
    ///
    /// The one mechanism (Patch_WorldDrawLayer_Paths_GeneratePaths) substitutes a per-tile water colour (by biome) for the
    /// planet-view river mesh. The water colours are RGB sliders with a live swatch; the switch reverts to the
    /// game's single flat river colour. Defaults = shipped behaviour (on, the 2026-10-20 water palette). Nothing here touches
    /// worldgen: the colours are read when the planet's river layer is generated, which happens when the world is drawn
    /// afresh (a load), so every setting is labelled [next game start]. The player's values from the old standalone
    /// mod's settings file are not imported (as with the River Works merge): a player who tuned them sees the shipped
    /// palette once.
    /// </summary>
    public static class RM_RiverColorsSettings
    {
        public static bool riverColorsEnabled = true;

        // RIVER_WATER_BY_BIOME (2026-10-20): water everywhere, a story tint inside four biomes (RM_RiverColors.cs).
        // Supersedes the 2026-09-06 headwater/jungle/terminus gradient and its 2026-10-20 darkening; new scribe keys, so a
        // player's old gradient values are not read.
        public static Color waterColor = new Color(0.08f, 0.16f, 0.30f);          // cool blue-grey
        public static Color contagionColor = new Color(0.36f, 0.03f, 0.04f);      // blood red
        public static Color miasmaColor = new Color(0.16f, 0.14f, 0.04f);         // brackish olive-brown
        public static Color wastelandColor = new Color(0.14f, 0.24f, 0.06f);      // toxic green
        public static Color rustCathedralColor = new Color(0.04f, 0.20f, 0.16f);  // verdigris coolant

        /// <summary>Called from RimMandrakeFlowWorksSettings.ExposeData, inside its PatchApplier Before/AfterExpose pair.</summary>
        public static void ExposeData()
        {
            Scribe_Values.Look(ref riverColorsEnabled, "riverColors_enabled", true);
            Scribe_Values.Look(ref waterColor, "riverColors_waterColor", new Color(0.08f, 0.16f, 0.30f));
            Scribe_Values.Look(ref contagionColor, "riverColors_contagionColor", new Color(0.36f, 0.03f, 0.04f));
            Scribe_Values.Look(ref miasmaColor, "riverColors_miasmaColor", new Color(0.16f, 0.14f, 0.04f));
            Scribe_Values.Look(ref wastelandColor, "riverColors_wastelandColor", new Color(0.14f, 0.24f, 0.06f));
            Scribe_Values.Look(ref rustCathedralColor, "riverColors_rustCathedralColor", new Color(0.04f, 0.20f, 0.16f));
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/Color setting, read from the field initialisers.
        // MUST stay below every public setting field (C# runs static initialisers in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_RiverColorsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(Color))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_RiverColorsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), the [next game start] tag line, and a per-section reset. Scope AUDITED
        /// per setting against its read site (2026-10-10, unchanged by the merge): the mesh colours are read when the
        /// planet-view river layer is generated (GeneratePaths prefix), not when a setting changes.</summary>
        private static bool Group(Listing_Standard list, string title, string[] names)
        {
            bool open = !collapsedSections.Contains(title);
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            if (!open) return false;
            list.Label("[next game start] changes take effect the next time the game starts or loads");
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        /// <summary>The "River colours" part of FlowWorks' settings window (planet-map rivers).</summary>
        public static void DoSettingsSection(Listing_Standard list)
        {
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("River colours (planet map)");
            Text.Font = GameFont.Small;

            if (Group(list, "River colouring", new[] { "riverColorsEnabled" }))
            {
                list.CheckboxLabeled("Colour rivers by biome", ref riverColorsEnabled,
                    "On (default): planet-map rivers draw as blue-grey water, tinted only inside the biomes whose water "
                  + "is not clean: blood red in the Contagion, brackish in the Miasma, toxic green in the Wasteland, "
                  + "verdigris in the Rust Cathedral. Off: rivers draw with the game's own single flat colour. The "
                  + "planet's river layer is rebuilt when the world is drawn afresh (a load), not the moment a setting "
                  + "changes. Never changes the world itself, only how its rivers are painted.");
            }

            if (Group(list, "Water colours", new[] { "waterColor", "contagionColor", "miasmaColor", "wastelandColor", "rustCathedralColor" }))
            {
                ColorSection(list, "River water (everywhere else)", ref waterColor);
                ColorSection(list, "Contagion (blood red)", ref contagionColor);
                ColorSection(list, "Miasma (brackish)", ref miasmaColor);
                ColorSection(list, "Wasteland (toxic)", ref wastelandColor);
                ColorSection(list, "Rust Cathedral (verdigris coolant)", ref rustCathedralColor);
            }
        }

        private static void ColorSection(Listing_Standard list, string label, ref Color color)
        {
            list.Label(label);

            Rect row = list.GetRect(24f);
            Rect swatch = row.LeftPart(0.12f);
            Widgets.DrawBoxSolid(swatch, color);
            Widgets.DrawBox(swatch);

            float r = color.r, g = color.g, b = color.b;
            r = list.Slider(r, 0f, 1f);
            g = list.Slider(g, 0f, 1f);
            b = list.Slider(b, 0f, 1f);
            color = new Color(r, g, b);
            list.Gap();
        }
    }
}
