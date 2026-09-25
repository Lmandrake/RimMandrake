using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheRot
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 / §6a of THEROT_RM_MOD_BUILD_1 — Mod Settings for
    // The Rot. Pattern copied from RM_GreentideSettings
    // (src/RimMandrake/Greentide/Source/RM_GreentideMod.cs): static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass. Defaults = shipped behavior throughout.
    //
    // ⚠️ NOT YET WIRED to mandrake.rm.environmentalhazards' own settings
    // screen, which already gates several of these same mechanics
    // (RM_MapComponent_AcceleratedRot, RM_MapComponent_WarmGround,
    // RM_MapComponent_LivingProduce, etc. read that assembly's own
    // RM_EnvironmentalHazardsSettings fields, not these). This screen is the
    // per-biome front described in the item's §6a spec; consolidating the two
    // — or moving the gates — is OWED, not done here (see the build's own
    // REMAINS note). Toggling a switch below therefore does not yet change
    // whether the shared mechanic runs; it is scaffolding for that
    // consolidation, not a behavior change today.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TheRotSettings : ModSettings
    {
        public static bool theRotEnabled = true;

        public static bool sheenExposure = true;
        public static bool acceleratedRot = true;
        public static float acceleratedRotRate = 1f;
        public static bool livingProduceHeat = true;
        public static float livingProduceHeatPerUnit = 1f;
        public static bool warmMat = true;
        public static float warmMatWarmth = 1f;
        public static bool livePreparations = true;
        public static bool livePreparationsStrictViability = true;
        public static bool guardianGroves = true;
        public static bool healthSharing = true;
        public static bool paleTreeSpawn = true;
        public static float sporeCloudIncidentWeight = 1f;

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        private string biomeListBuffer;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref theRotEnabled, "theRotEnabled", true);
            Scribe_Values.Look(ref sheenExposure, "sheenExposure", true);
            Scribe_Values.Look(ref acceleratedRot, "acceleratedRot", true);
            Scribe_Values.Look(ref acceleratedRotRate, "acceleratedRotRate", 1f);
            Scribe_Values.Look(ref livingProduceHeat, "livingProduceHeat", true);
            Scribe_Values.Look(ref livingProduceHeatPerUnit, "livingProduceHeatPerUnit", 1f);
            Scribe_Values.Look(ref warmMat, "warmMat", true);
            Scribe_Values.Look(ref warmMatWarmth, "warmMatWarmth", 1f);
            Scribe_Values.Look(ref livePreparations, "livePreparations", true);
            Scribe_Values.Look(ref livePreparationsStrictViability, "livePreparationsStrictViability", true);
            Scribe_Values.Look(ref guardianGroves, "guardianGroves", true);
            Scribe_Values.Look(ref healthSharing, "healthSharing", true);
            Scribe_Values.Look(ref paleTreeSpawn, "paleTreeSpawn", true);
            Scribe_Values.Look(ref sporeCloudIncidentWeight, "sporeCloudIncidentWeight", 1f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        /// <summary>True if the cross-biome opt-in currently applies to this biome (never to The Rot's own — that is native, not "cross").</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            if (!crossBiomeEnabled || biome == null || biome.defName == "RM_TheRot")
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

            list.CheckboxLabeled("The Rot enabled", ref theRotEnabled,
                "Master switch. Off: the biome and its defs still load (nothing here is worldgen-affecting "
              + "except the cross-biome section below), but every per-feature toggle is ignored as off.");
            list.GapLine();

            list.CheckboxLabeled("Sheen exposure ladder", ref sheenExposure,
                "The Sheen weather rotation bootstraps a spore-coating hediff on unprotected pawns.");
            list.CheckboxLabeled("Accelerated rot/decay", ref acceleratedRot,
                "Items and corpses decay faster on this biome's living ground.");
            list.Label("  Rate: " + acceleratedRotRate.ToString("0.00") + "x");
            acceleratedRotRate = list.Slider(acceleratedRotRate, 0.25f, 3f);
            list.CheckboxLabeled("Living produce heat", ref livingProduceHeat,
                "Live food preparations radiate warmth proportional to stored mass.");
            list.Label("  Heat per unit: " + livingProduceHeatPerUnit.ToString("0.00") + "x");
            livingProduceHeatPerUnit = list.Slider(livingProduceHeatPerUnit, 0.25f, 3f);
            list.CheckboxLabeled("Warm living ground", ref warmMat,
                "The biome's natural terrain and living mycelium floors radiate ambient warmth.");
            list.Label("  Warmth: " + warmMatWarmth.ToString("0.00") + "x");
            warmMatWarmth = list.Slider(warmMatWarmth, 0.25f, 3f);
            list.CheckboxLabeled("Live preparations", ref livePreparations,
                "Food/ingredient preparations stay biologically \"alive\" until used.");
            list.CheckboxLabeled("  Strict viability", ref livePreparationsStrictViability,
                "Strict: viability lapses on any mishandling. Lenient: more forgiving window.");
            list.CheckboxLabeled("Guardian groves", ref guardianGroves,
                "Defended tea-source mushrooms wild-spawn with the false-fruit lure ring.");
            list.CheckboxLabeled("Health sharing", ref healthSharing,
                "Kin-linked pawns share a portion of wound healing.");
            list.CheckboxLabeled("Pale tree spawn", ref paleTreeSpawn,
                "The rare pale tree (a door-ajar oddity) wild-spawns. Royalty-gated regardless of this toggle.");
            list.Label("Spore cloud incident weight: " + sporeCloudIncidentWeight.ToString("0.00") + "x");
            sporeCloudIncidentWeight = list.Slider(sporeCloudIncidentWeight, 0f, 3f);
            list.GapLine();

            list.Label("Cross-biome opt-in (WORLDGEN-AFFECTING — new maps only)");
            list.Label("Lets Rot mechanics generate on a NON-Rot biome's map, without adding the whole "
              + "biome. Applies once, right after a map generates; an existing map is never retroactively "
              + "changed.");
            list.CheckboxLabeled("Enable outside The Rot biome", ref crossBiomeEnabled,
                "Master switch for the section below.");
            if (crossBiomeEnabled)
            {
                list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere,
                    "Apply to any non-Rot biome. Off: only the biomes named below.");
                if (!crossBiomeEverywhere)
                {
                    list.Label("  Biome defNames, comma-separated (e.g. TropicalRainforest, AridShrubland):");
                    biomeListBuffer = list.TextEntry(biomeListBuffer);
                    crossBiomeBiomeList = biomeListBuffer;
                }
                list.Label("  Coverage: " + (crossBiomeCoverage * 100f).ToString("0") + "%");
                crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
            }

            list.End();
        }
    }

    public class RM_TheRotMod : Mod
    {
        public static RM_TheRotSettings settings;

        public RM_TheRotMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TheRotSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Rot";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
