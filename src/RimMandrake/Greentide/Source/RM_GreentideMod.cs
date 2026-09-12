using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Greentide.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs (static
    // fields read from everywhere, Scribe_Values in ExposeData, a
    // DoWindowContents helper called from the Mod subclass).
    //
    // Three things this exposes, per the item's own spec:
    //   1. Master on/off per mechanic (mire hazard, buried caches) — default
    //      ON, matching shipped GREENTIDE_STANDALONE_MOD_1 behavior.
    //   2. A tuning number (mire severity multiplier) — default 1.0x.
    //   3. The named trigger case: per-feature biome opt-in so the churnmud/
    //      mire hazard can run on a NON-Greentide biome's maps without
    //      importing the whole Greentide biome. WORLDGEN-AFFECTING — labeled
    //      as such in the UI and only ever applied once, to a freshly
    //      generated map (RM_MapComponent_CrossBiomeChurnmud).
    //
    // Buried caches (RM_MapComponent_MudSwallow) need no separate cross-biome
    // toggle: it already fires off the terrain extension alone, wherever
    // RM_Churnmud exists, native map or opted-in map alike. The Greatbole
    // does not exist yet (About.xml: gated on ALPHA_MECHANICS_KIT_1 /
    // EXPLOSIVE_PLANT_GROWTH_1) — nothing to gate.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GreentideSettings : ModSettings
    {
        public static bool mireEnabled = true;
        public static bool buriedCacheEnabled = true;
        public static float mireSeverityMultiplier = 1f;

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        private string biomeListBuffer;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref mireEnabled, "mireEnabled", true);
            Scribe_Values.Look(ref buriedCacheEnabled, "buriedCacheEnabled", true);
            Scribe_Values.Look(ref mireSeverityMultiplier, "mireSeverityMultiplier", 1f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        /// <summary>True if the cross-biome opt-in currently applies to this biome (never to Greentide's own — that is native, not "cross").</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            if (!crossBiomeEnabled || biome == null || biome.defName == "RM_Greentide")
            {
                return false;
            }
            if (crossBiomeEverywhere)
            {
                return true;
            }
            return ParseBiomeList().Contains(biome.defName);
        }

        private static List<string> ParseBiomeList()
        {
            var result = new List<string>();
            if (crossBiomeBiomeList.NullOrEmpty())
            {
                return result;
            }
            string[] parts = crossBiomeBiomeList.Split(',', ';');
            for (int i = 0; i < parts.Length; i++)
            {
                string trimmed = parts[i].Trim();
                if (trimmed.Length > 0)
                {
                    result.Add(trimmed);
                }
            }
            return result;
        }

        public void DoWindowContents(Rect inRect)
        {
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Churnmud / mire hazard");
            list.CheckboxLabeled("Mire hazard enabled", ref mireEnabled,
                "Standing on churnmud escalates the RM_Mired hediff (slowed, then stuck). "
              + "Off: churnmud is inert underfoot — no NREs, the terrain just does nothing.");
            list.Label("Mire severity: " + mireSeverityMultiplier.ToString("0.00") + "x");
            mireSeverityMultiplier = list.Slider(mireSeverityMultiplier, 0.25f, 3f);
            list.Gap();
            list.CheckboxLabeled("Buried caches enabled", ref buriedCacheEnabled,
                "Loose items left on churnmud long enough get buried (dig them back out, nothing "
              + "is destroyed). Off: items just sit there like any other terrain.");
            list.GapLine();

            list.Label("Cross-biome opt-in (WORLDGEN-AFFECTING — new maps only)");
            list.Label("Lets churnmud/mire generate on a NON-Greentide biome's map, without "
              + "adding the whole Greentide biome. Applies once, right after a map generates; "
              + "a map that already exists is never retroactively changed.");
            list.CheckboxLabeled("Enable outside the Greentide biome", ref crossBiomeEnabled,
                "Master switch for the section below.");
            if (crossBiomeEnabled)
            {
                list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere,
                    "Apply to any non-Greentide biome. Off: only the biomes named below.");
                if (!crossBiomeEverywhere)
                {
                    list.Label("  Biome defNames, comma-separated (e.g. TropicalRainforest, AridShrubland):");
                    biomeListBuffer = list.TextEntry(biomeListBuffer);
                    crossBiomeBiomeList = biomeListBuffer;
                }
                list.Label("  Coverage: " + (crossBiomeCoverage * 100f).ToString("0") + "% of that map's ordinary Mud terrain becomes churnmud");
                crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
            }

            list.End();
        }
    }

    public class RM_GreentideMod : Mod
    {
        public static RM_GreentideSettings settings;

        public RM_GreentideMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_GreentideSettings>();
        }

        public override string SettingsCategory()
        {
            return "Greentide";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
