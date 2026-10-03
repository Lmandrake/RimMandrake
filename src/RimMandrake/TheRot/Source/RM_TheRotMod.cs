using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
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
    // ROT_MOD_SETTINGS_WIRING_1: every control on this screen is wired, or hidden until the item that
    // wires it lands. This screen is the per-biome FRONT for mechanics living in mandrake.rm.environmentalhazards:
    // RM_TheRotFront (below) registers into RM_KitFronts at startup, and the shared mechanics ask it before
    // running on a map. The shared screen's own gate still applies first. A map that is neither The Rot nor an
    // opted-in cross-biome map is never affected by this screen.
    //   theRotEnabled             master: off = every gated mechanic reads off on Rot / cross-biome maps
    //   sheenExposure             sheenExposure          acceleratedRot(+Rate)   acceleratedRot
    //   livingProduceHeat(+PerUnit) livingProduceHeat    warmMat(+Warmth)        warmGround
    //   livePreparations / ...StrictViability            livePrepStrict (both must be on for strict)
    //   sporeCloudIncidentWeight  sporeCloud: 0 = never fires, otherwise scales the incident's chance
    //   guardianGroves, paleTreeSpawn: the wild-spawn rows leave RM_TheRot's wildPlants at startup (restart)
    //   crossBiome*: opt-in donor (RM_TheRot's extensions) for non-Rot maps; Coverage scales their intensity
    //   healthSharing: the field is kept and saved, but the checkbox is hidden until ROT_WOUND_SHARING_WIRING_1
    //                  gives it a reader (a control that moves and does nothing is the defect)
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
            list.CheckboxLabeled("Guardian groves (new maps, restart to apply)", ref guardianGroves,
                "Defended tea-source mushrooms wild-spawn with the false-fruit lure ring. WORLDGEN-AFFECTING: "
              + "applies to maps generated after the next launch.");
            list.CheckboxLabeled("Pale tree spawn (new maps, restart to apply)", ref paleTreeSpawn,
                "The rare pale tree (a door-ajar oddity) wild-spawns. Royalty-gated regardless of this toggle. "
              + "WORLDGEN-AFFECTING: applies to maps generated after the next launch.");
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
                list.Label("  Intensity on those maps: " + (crossBiomeCoverage * 100f).ToString("0") + "%");
                crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
            }

            list.End();
        }
    }

    /// <summary>ROT_MOD_SETTINGS_WIRING_1: registers this screen as the front for the shared Rot mechanics.</summary>
    [StaticConstructorOnStartup]
    public static class RM_TheRotFront
    {
        public static bool IsRotBiome(BiomeDef biome)
        {
            return biome != null && (biome.defName == "RM_TheRot" || biome.defName == "RUT_TheRot");
        }

        /// <summary>True when this screen governs a map of this biome (the Rot itself, or an opted-in cross-biome map).</summary>
        public static bool Governs(BiomeDef biome)
        {
            return IsRotBiome(biome) || RM_TheRotSettings.AppliesToBiome(biome);
        }

        public static bool Enabled(string key, BiomeDef biome)
        {
            if (!Governs(biome))
            {
                return true;
            }
            if (!RM_TheRotSettings.theRotEnabled)
            {
                return false;
            }
            switch (key)
            {
                case "sheenExposure": return RM_TheRotSettings.sheenExposure;
                case "acceleratedRot": return RM_TheRotSettings.acceleratedRot;
                case "livingProduceHeat": return RM_TheRotSettings.livingProduceHeat;
                case "warmGround": return RM_TheRotSettings.warmMat;
                case "livePrepStrict": return RM_TheRotSettings.livePreparations && RM_TheRotSettings.livePreparationsStrictViability;
                case "sporeCloud": return RM_TheRotSettings.sporeCloudIncidentWeight > 0f;
                default: return true;
            }
        }

        public static float Factor(string key, BiomeDef biome)
        {
            if (!Governs(biome))
            {
                return 1f;
            }
            float f;
            switch (key)
            {
                case "acceleratedRot": f = RM_TheRotSettings.acceleratedRotRate; break;
                case "livingProduceHeat": f = RM_TheRotSettings.livingProduceHeatPerUnit; break;
                case "warmGround": f = RM_TheRotSettings.warmMatWarmth; break;
                case "sporeCloud": f = RM_TheRotSettings.sporeCloudIncidentWeight; break;
                default: return 1f;
            }
            return IsRotBiome(biome) ? f : f * RM_TheRotSettings.crossBiomeCoverage;
        }

        static RM_TheRotFront()
        {
            RM_KitFronts.enabled = Enabled;
            RM_KitFronts.factor = Factor;
            RM_KitFronts.extensionDonor = biome =>
                !IsRotBiome(biome) && RM_TheRotSettings.theRotEnabled && RM_TheRotSettings.AppliesToBiome(biome)
                    ? DefDatabase<BiomeDef>.GetNamedSilentFail("RM_TheRot")
                    : null;

            // Wild-spawn gates take effect on the next launch (the roster is read at map generation).
            BiomeDef rot = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_TheRot");
            if (rot == null || rot.wildPlants == null)
            {
                return;
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.paleTreeSpawn)
            {
                rot.wildPlants.RemoveAll(r => r.plant != null && r.plant.defName == "RM_PaleTree");
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.guardianGroves)
            {
                rot.wildPlants.RemoveAll(r => r.plant != null && System.Array.IndexOf(GuardianGroveRows, r.plant.defName) >= 0);
            }
        }

        private static readonly string[] GuardianGroveRows = { "RM_AgelessCap", "RM_RegenerantVeil", "RM_EuphoricCrown", "RM_FalseFruit" };
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
