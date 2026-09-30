using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: every mod ships a real
    // settings screen. No mechanics kit exists for this biome yet (thin
    // biome per biome_mod_architecture.md — def + terrain + plants + fauna
    // partition only, no mechanic to gate beyond worldgen insertion), so the
    // only control is the standard worldgen-rarity slider every sibling
    // biome mod ships.
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CauldronSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // CAULDRON_TREE_METAL_YIELD_1: the metal second yield on the thornwood
        // and martyr tree. Off = they yield wood only. Factor scales the count.
        public static bool metalYieldEnabled = true;
        public static float metalYieldFactor = 1f;

        // CAULDRON_MECHANICS_BUILD_1 part 2: the vent bloom's stacking metal
        // load on pawns outdoors + unroofed. Off = the bloom is weather only.
        public static bool ventBloomExposureEnabled = true;
        public static float ventBloomExposureFactor = 1f;

        // CAULDRON_MECHANICS_BUILD_1 part 5: vexxiss behaviours.
        public static bool vexxissFireWardenEnabled = true;
        public static bool vexxissAttacksIgniter = true;
        public static bool vexxissPoisonsWater = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref metalYieldEnabled, "metalYieldEnabled", true, true);
            Scribe_Values.Look(ref metalYieldFactor, "metalYieldFactor", 1f, true);
            Scribe_Values.Look(ref ventBloomExposureEnabled, "ventBloomExposureEnabled", true, true);
            Scribe_Values.Look(ref ventBloomExposureFactor, "ventBloomExposureFactor", 1f, true);
            Scribe_Values.Look(ref vexxissFireWardenEnabled, "vexxissFireWardenEnabled", true, true);
            Scribe_Values.Look(ref vexxissAttacksIgniter, "vexxissAttacksIgniter", true, true);
            Scribe_Values.Look(ref vexxissPoisonsWater, "vexxissPoisonsWater", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Poison Forest never generates on a new planet. "
                       + "The default places a scattering of cold, permanently dim, "
                       + "toxin-laced forest patches. Affects planets generated "
                       + "afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.GapLine();
            list.CheckboxLabeled("Metal-infused trees yield metal",
                ref metalYieldEnabled,
                "Twisting thornwood and martyr trees drop steel beside their wood, "
                + "more from older growth. Off: wood only. Takes effect on the next harvest.");
            if (metalYieldEnabled)
            {
                list.Label("Metal yield: " + metalYieldFactor.ToString("0.0") + "x (default 1.0x)");
                metalYieldFactor = list.Slider(metalYieldFactor, 0.1f, 3f);
            }

            list.GapLine();
            list.CheckboxLabeled("Vent bloom builds a metal load",
                ref ventBloomExposureEnabled,
                "During a vent bloom, anyone outdoors under open sky slowly takes on a "
                + "metal-load condition. A roof or toxic-resistant gear keeps it off; native "
                + "animals are unaffected. Off: the bloom is weather only.");
            if (ventBloomExposureEnabled)
            {
                list.Label("Metal load build-up: " + ventBloomExposureFactor.ToString("0.0") + "x (default 1.0x)");
                ventBloomExposureFactor = list.Slider(ventBloomExposureFactor, 0.1f, 3f);
            }

            list.GapLine();
            list.CheckboxLabeled("Vexxiss puts out fires",
                ref vexxissFireWardenEnabled,
                "A vexxiss that notices a nearby fire walks to it and smothers it. Off: it ignores fire.");
            if (vexxissFireWardenEnabled)
            {
                list.CheckboxLabeled("  ...and attacks whoever started it",
                    ref vexxissAttacksIgniter,
                    "When the fire has a known starter still in reach, the vexxiss goes for them first. "
                    + "A tame vexxiss never attacks its own faction.");
            }
            list.CheckboxLabeled("Vexxiss poisons the water it wades through",
                ref vexxissPoisonsWater,
                "Water cells a vexxiss stands in, and the cells touching it, turn to toxic water. "
                + "Off: water is left alone.");

            list.End();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default, a handful of patches (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_CauldronMod : Mod
    {
        public static RM_CauldronSettings settings;

        public RM_CauldronMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_CauldronSettings>();
        }

        public override string SettingsCategory()
        {
            return "Poison Forest";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
