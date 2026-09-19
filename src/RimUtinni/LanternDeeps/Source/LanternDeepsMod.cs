using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Lantern Deeps.
    //
    // The mod's runtime mechanisms are GenStep_ScatterCavePortal and
    // GenStep_ScatterMineshaftPortal, both WORLDGEN-AFFECTING steps (new maps
    // only): each scatters its own entrance onto a qualifying ≤ -40°C biome
    // at a flat per-map chance (LANTERN_DEEPS_INJECTION_1's own comment:
    // "FOUNDRY's placeholder pick pending the owner's actual density call").
    // Exposed here as a master toggle plus a multiplier per entrance type,
    // default 1x = shipped rate. MapComponent_LanternDeepDarkness (spec item
    // 6, the darkness mechanic) runs only inside an already-generated Deep,
    // so it gets its own toggle rather than sharing either entrance's.
    public class LanternDeepsSettings : ModSettings
    {
        public static bool emergenceEnabled = true;
        public static float emergenceChanceMultiplier = 1f;
        public static bool mineshaftEnabled = true;
        public static float mineshaftChanceMultiplier = 1f;
        public static bool darknessMechanicEnabled = true;
        public static float darknessThresholdMultiplier = 1f;

        // CAVERNS_PARITY_BUILD_1 — the two features the mod now OWNS rather than
        // borrows from Biomes! Caverns, each gated per the standing rule
        // (every mod ships real Mod Settings; defaults = shipped behavior;
        // all-off degrades gracefully).
        //
        // Both are WORLDGEN-AFFECTING in the same sense the entrance scatters
        // are: they are read while a Deep's pocket map is being generated, so a
        // change applies to the NEXT Deep entered, never to one already made.
        // The Deeps remain persistent maps (sheet hard ban 5) either way.
        //
        // All-off behaviour: a Deep with formations off and flora off is still a
        // complete, enterable, mineable cavern — gravel, lanternstone shelves,
        // lanternstone walls in extraRockTypes, the darkness mechanic, and both
        // the pyrinth and kyber scatters. It loses its crystal field and its
        // fungal pasture, not its floor.
        public static bool lanternstoneFormationsEnabled = true;
        public static float lanternstoneDensityMultiplier = 1f;
        public static bool deepFloraEnabled = true;

        // DEEP_ENTRANCE_BIOMES_SETTING_1 — owner, 2026-09-18: "The mod itself
        // will be (3) but for the Utinni scenario it's definitely (1)". The
        // biomes an entrance may scatter onto are a Mod Setting (any biome
        // selectable); the DEFAULT is exactly the three the Utinni campaign
        // ruled ≤ -40°C (the_lantern_deeps.md "Injection rule"), which is what
        // both GenSteps hardcoded before this setting existed. WORLDGEN-AFFECTING:
        // read once per map generation, so a change applies to new maps only.
        // A name that resolves to no loaded BiomeDef is simply never matched.
        public static readonly string[] UtinniDefaultEntranceBiomes =
        {
            "BiomeGRimond",
            "RUT_NightsideIce",
            "RUT_PropaneLake",
        };

        public static List<string> entranceBiomes = new List<string>(UtinniDefaultEntranceBiomes);

        // Lazy lookup set. Invalidated explicitly by every UI edit and by
        // ResetEntranceBiomes(); ALSO rebuilt whenever the backing list's
        // reference or count differs from what the set was built from, because
        // the bridge's jawa/mod_settings_field writes the static field directly
        // and never calls a setter (BRIDGE_STATIC_SETTINGS_FIELDS_1).
        private static HashSet<string> entranceBiomeSet;
        private static List<string> entranceBiomeSetSource;
        private static int entranceBiomeSetCount = -1;

        public static bool IsEntranceBiome(BiomeDef biome)
        {
            if (biome == null)
            {
                return false;
            }
            List<string> list = entranceBiomes;
            if (list == null)
            {
                return false;
            }
            if (entranceBiomeSet == null
                || !ReferenceEquals(entranceBiomeSetSource, list)
                || entranceBiomeSetCount != list.Count)
            {
                entranceBiomeSet = new HashSet<string>(list);
                entranceBiomeSetSource = list;
                entranceBiomeSetCount = list.Count;
            }
            return entranceBiomeSet.Contains(biome.defName);
        }

        public static void InvalidateEntranceBiomeSet()
        {
            entranceBiomeSet = null;
            entranceBiomeSetSource = null;
            entranceBiomeSetCount = -1;
        }

        public static void ResetEntranceBiomes()
        {
            entranceBiomes = new List<string>(UtinniDefaultEntranceBiomes);
            InvalidateEntranceBiomeSet();
        }

        public static bool EntranceBiomesAreUtinniDefault()
        {
            List<string> list = entranceBiomes;
            return list != null
                && list.Count == UtinniDefaultEntranceBiomes.Length
                && UtinniDefaultEntranceBiomes.All(list.Contains);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref entranceBiomes, "entranceBiomes", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // ReadModSettings loads through Scribe_Deep.Look, which registers
                // this object for the PostLoadInit pass, so this branch does run.
                // Null = a settings file written before this key existed; empty =
                // nothing useful to keep. Either way: the Utinni defaults.
                if (entranceBiomes == null || entranceBiomes.Count == 0)
                {
                    ResetEntranceBiomes();
                }
                else
                {
                    InvalidateEntranceBiomeSet();
                }
            }
            Scribe_Values.Look(ref emergenceEnabled, "emergenceEnabled", true);
            Scribe_Values.Look(ref emergenceChanceMultiplier, "emergenceChanceMultiplier", 1f);
            Scribe_Values.Look(ref mineshaftEnabled, "mineshaftEnabled", true);
            Scribe_Values.Look(ref mineshaftChanceMultiplier, "mineshaftChanceMultiplier", 1f);
            Scribe_Values.Look(ref darknessMechanicEnabled, "darknessMechanicEnabled", true);
            Scribe_Values.Look(ref darknessThresholdMultiplier, "darknessThresholdMultiplier", 1f);
            Scribe_Values.Look(ref lanternstoneFormationsEnabled, "lanternstoneFormationsEnabled", true);
            Scribe_Values.Look(ref lanternstoneDensityMultiplier, "lanternstoneDensityMultiplier", 1f);
            Scribe_Values.Look(ref deepFloraEnabled, "deepFloraEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Lantern Deep emergence (affects new maps only)");
            list.CheckboxLabeled("Natural cave-mouth portal can emerge", ref emergenceEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a lanternstone-geode mouth. "
              + "A map that already exists is never retroactively changed.");
            if (emergenceEnabled)
            {
                list.Label("Emergence chance: " + emergenceChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 8% of qualifying maps)");
                emergenceChanceMultiplier = list.Slider(emergenceChanceMultiplier, 0f, 3f);
            }

            list.Gap();
            list.Label("Ruined mineshaft entrance (affects new maps only)");
            list.CheckboxLabeled("Ruined-mineshaft portal can appear", ref mineshaftEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a ruined-mineshaft mouth. "
              + "A map that already exists is never retroactively changed.");
            if (mineshaftEnabled)
            {
                list.Label("Mineshaft chance: " + mineshaftChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 4% of qualifying maps)");
                mineshaftChanceMultiplier = list.Slider(mineshaftChanceMultiplier, 0f, 3f);
            }

            list.Gap();
            list.Label("Darkness (inside an already-generated Deep)");
            list.CheckboxLabeled("Bright light draws cave predators", ref darknessMechanicEnabled,
                "Off: colonists inside a Lantern Deep can light the place up freely with no consequence. "
              + "On (default): sustained bright light near colonists eventually draws a resident predator "
              + "into a manhunter attack. Working in the dark, or moving on before light lingers, avoids it.");
            if (darknessMechanicEnabled)
            {
                list.Label("Trigger threshold: " + darknessThresholdMultiplier.ToString("0.00")
                    + "x the base sensitivity (higher = more light tolerated before something notices)");
                darknessThresholdMultiplier = list.Slider(darknessThresholdMultiplier, 0.25f, 4f);
            }

            list.Gap();
            list.Label("Inside a Lantern Deep (affects newly generated Deeps only)");
            list.CheckboxLabeled("Lanternstone formations grow in the Deeps", ref lanternstoneFormationsEnabled,
                "Off: a newly entered Deep has bare gravel and lanternstone shelves but no standing crystal "
              + "formations to mine, light the place, or go off when shot. The cavern is still complete and "
              + "still has its lanternstone walls.");
            if (lanternstoneFormationsEnabled)
            {
                list.Label("Lanternstone density: " + lanternstoneDensityMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 15-30 clusters per 10,000 cells)");
                lanternstoneDensityMultiplier = list.Slider(lanternstoneDensityMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Cave flora grows in the Deeps", ref deepFloraEnabled,
                "Off: a newly entered Deep has no mycelium carpet, no mushroom trees and no glow-fungi — "
              + "no forageable food and no cloth or wood from below. Bare rock and crystal.");

            // DEEP_ENTRANCE_BIOMES_SETTING_1 — worldgen-affecting biome checklist.
            list.Gap();
            list.Label("World generation: entrance biomes (affects new maps only)");
            Text.Font = GameFont.Tiny;
            list.Label("Both entrance types can only appear on a new map whose biome is ticked below. "
                + "Shipped default: the three Utinni deep-cold biomes. A ticked biome that is not loaded "
                + "is ignored. Ticking none is restored to the defaults on next load; use the toggles "
                + "above to turn entrances off.");
            Text.Font = GameFont.Small;

            List<string> selected = entranceBiomes ?? (entranceBiomes = new List<string>());
            List<BiomeDef> biomes = AllBiomesSorted;
            int loadedSelected = 0;
            for (int i = 0; i < biomes.Count; i++)
            {
                if (selected.Contains(biomes[i].defName))
                {
                    loadedSelected++;
                }
            }
            list.Label(loadedSelected + " of " + biomes.Count + " loaded biomes selected"
                + (EntranceBiomesAreUtinniDefault() ? " (Utinni defaults)" : ""));

            Rect buttonRow = list.GetRect(30f);
            float buttonWidth = (buttonRow.width - 2f * 8f) / 3f;
            if (Widgets.ButtonText(new Rect(buttonRow.x, buttonRow.y, buttonWidth, buttonRow.height),
                "Reset to Utinni defaults"))
            {
                ResetEntranceBiomes();
            }
            if (Widgets.ButtonText(new Rect(buttonRow.x + buttonWidth + 8f, buttonRow.y, buttonWidth, buttonRow.height),
                "Select all"))
            {
                entranceBiomes = biomes.Select(b => b.defName).ToList();
                InvalidateEntranceBiomeSet();
            }
            if (Widgets.ButtonText(new Rect(buttonRow.x + 2f * (buttonWidth + 8f), buttonRow.y, buttonWidth, buttonRow.height),
                "Select none"))
            {
                entranceBiomes = new List<string>();
                InvalidateEntranceBiomeSet();
            }
            list.Gap(4f);

            float usedHeight = list.CurHeight;
            list.End();

            Rect outRect = new Rect(inRect.x, inRect.y + usedHeight, inRect.width,
                Mathf.Max(inRect.height - usedHeight, 120f));
            DrawBiomeChecklist(outRect);
        }

        private static Vector2 biomeScrollPosition = Vector2.zero;
        private static List<BiomeDef> allBiomesSortedCached;

        // DefDatabase is fixed after load, so one sorted snapshot is enough.
        private static List<BiomeDef> AllBiomesSorted =>
            allBiomesSortedCached ?? (allBiomesSortedCached = DefDatabase<BiomeDef>.AllDefsListForReading
                .OrderBy(b => b.LabelCap.ToString())
                .ThenBy(b => b.defName)
                .ToList());

        private const float BiomeRowHeight = 24f;

        private static void DrawBiomeChecklist(Rect outRect)
        {
            List<BiomeDef> biomes = AllBiomesSorted;
            List<string> selected = entranceBiomes;
            Rect viewRect = new Rect(0f, 0f, outRect.width - 16f, biomes.Count * BiomeRowHeight);
            Widgets.BeginScrollView(outRect, ref biomeScrollPosition, viewRect);
            float y = 0f;
            for (int i = 0; i < biomes.Count; i++)
            {
                BiomeDef biome = biomes[i];
                Rect row = new Rect(0f, y, viewRect.width, BiomeRowHeight);
                bool was = selected.Contains(biome.defName);
                bool now = was;
                Widgets.CheckboxLabeled(row, biome.LabelCap + " (" + biome.defName + ")", ref now);
                if (now != was)
                {
                    if (now)
                    {
                        selected.Add(biome.defName);
                    }
                    else
                    {
                        selected.RemoveAll(n => n == biome.defName);
                    }
                    InvalidateEntranceBiomeSet();
                }
                y += BiomeRowHeight;
            }
            Widgets.EndScrollView();
        }
    }

    public class LanternDeepsMod : Mod
    {
        public static LanternDeepsSettings settings;

        public LanternDeepsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LanternDeepsSettings>();
        }

        public override string SettingsCategory() => "Lantern Deeps";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
