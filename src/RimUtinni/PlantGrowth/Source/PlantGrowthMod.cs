using System.Collections.Generic;
using System.Reflection;
// MOD_OPTIONS_RETROFIT_1 — Mod Settings for Jawa Plant Growth.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs (static fields
// read from everywhere, Scribe_Values in ExposeData, DoWindowContents helper
// called from the Mod subclass).
//
// PRECEDENCE CHANGE, DOCUMENTED HERE AND IN PlantGrowthConfig.Rebuild(): before
// this pass, the four numeric bands (defaultMultiplier, treeMultiplier,
// terminatorMultiplier, minGrowDaysToBoost) were read from
// Defs/JawaPlantGrowthSettings.xml. They are now owned by THIS in-game Mod
// Settings screen instead — the XML def's own numeric fields are kept only for
// anyone hand-editing the file for reference, but Rebuild() no longer reads
// them. The terminator biome roster and exempt-plant list stay XML-configured
// (a list has no sensible slider). Every default below matches the shipped
// def's numbers exactly, so this changes nothing about day-one behavior.
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PlantGrowth
{
    public class PlantGrowthSettings : ModSettings
    {
        // Master switch. Off: Patch_Plant_GrowthRate's postfix no-ops and every
        // plant grows at vanilla speed.
        public static bool growthEnabled = true;

        public static float defaultMultiplier = PlantGrowthConfig.DEFAULT_MULTIPLIER;
        public static float treeMultiplier = PlantGrowthConfig.TREE_MULTIPLIER;
        public static float terminatorMultiplier = PlantGrowthConfig.TERMINATOR_MULTIPLIER;
        public static float minGrowDaysToBoost = PlantGrowthConfig.MIN_GROW_DAYS_TO_BOOST;
        public static float wetAmbientMultiplier = PlantGrowthConfig.WET_AMBIENT_MULTIPLIER;
        public static float wetAmbientTreeMultiplier = PlantGrowthConfig.WET_AMBIENT_TREE_MULTIPLIER;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref growthEnabled, "growthEnabled", true);
            Scribe_Values.Look(ref defaultMultiplier, "defaultMultiplier", PlantGrowthConfig.DEFAULT_MULTIPLIER);
            Scribe_Values.Look(ref treeMultiplier, "treeMultiplier", PlantGrowthConfig.TREE_MULTIPLIER);
            Scribe_Values.Look(ref terminatorMultiplier, "terminatorMultiplier", PlantGrowthConfig.TERMINATOR_MULTIPLIER);
            Scribe_Values.Look(ref minGrowDaysToBoost, "minGrowDaysToBoost", PlantGrowthConfig.MIN_GROW_DAYS_TO_BOOST);
            Scribe_Values.Look(ref wetAmbientMultiplier, "wetAmbientMultiplier", PlantGrowthConfig.WET_AMBIENT_MULTIPLIER);
            Scribe_Values.Look(ref wetAmbientTreeMultiplier, "wetAmbientTreeMultiplier", PlantGrowthConfig.WET_AMBIENT_TREE_MULTIPLIER);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(PlantGrowthSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(PlantGrowthSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Planetary fast growth", RimMandrake.Shared.SettingScope.Now, new[] { "growthEnabled" }))
            {
                list.CheckboxLabeled("Planetary fast growth enabled", ref growthEnabled,
                    "Off: every plant grows at vanilla speed, everywhere. On by default.");
                list.GapLine();
            }

            if (Group(list, "Growth multipliers", RimMandrake.Shared.SettingScope.Now, new[] { "defaultMultiplier", "treeMultiplier", "terminatorMultiplier", "wetAmbientMultiplier", "wetAmbientTreeMultiplier" }))
            {
                list.Label("Wild plants & crops: " + defaultMultiplier.ToString("0.0") + "x growth");
                defaultMultiplier = list.Slider(defaultMultiplier, 1f, 8f);
                list.Label("Trees: " + treeMultiplier.ToString("0.0") + "x growth");
                list.Label("Kept lower than crops on purpose - wood stays a decision.");
                treeMultiplier = list.Slider(treeMultiplier, 1f, 8f);
                list.Label("Terminator / poison-forest biomes: " + terminatorMultiplier.ToString("0.00") + "x growth");
                list.Label("The one place on this world where growth has stalled - kept below "
                  + "1.0x by default. This is the multiplier, not a bonus: 1.0 means vanilla "
                  + "speed in that biome, not vanilla plus a bonus.");
                terminatorMultiplier = list.Slider(terminatorMultiplier, 0.1f, 2f);
                list.Label("Wet biomes (Greentide, Miasma, Fever Wood): " + wetAmbientMultiplier.ToString("0.0") + "x growth");
                list.Label("The always-on groaning, swelling growth of the wet jungles. Replaces the "
                  + "wild-plants band on those biomes (it does not stack on it).");
                wetAmbientMultiplier = list.Slider(wetAmbientMultiplier, 1f, 20f);
                list.Label("Wet-biome trees: " + wetAmbientTreeMultiplier.ToString("0.00") + "x growth");
                wetAmbientTreeMultiplier = list.Slider(wetAmbientTreeMultiplier, 1f, 20f);
                list.GapLine();
            }

            if (Group(list, "Plants left alone", RimMandrake.Shared.SettingScope.Now, new[] { "minGrowDaysToBoost" }))
            {
                list.Label("Skip plants already faster than: " + minGrowDaysToBoost.ToString("0.0") + " grow-days");
                list.Label("A plant already this fast gains nothing from multiplying and can "
                  + "produce silly per-tick values, so it is left untouched. Plants are "
                  + "re-classified when you close the settings window.");
                minGrowDaysToBoost = list.Slider(minGrowDaysToBoost, 0.1f, 5f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class PlantGrowthMod : Mod
    {
        public static PlantGrowthSettings settings;

        public PlantGrowthMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PlantGrowthSettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Plant Growth";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        // Re-runs the classification pass so the sliders take effect immediately
        // rather than only after a restart, same as the def-driven path already
        // did (Rebuild() has always been safe to call more than once).
        public override void WriteSettings()
        {
            base.WriteSettings();
            PlantGrowthConfig.Rebuild();
        }
    }
}
