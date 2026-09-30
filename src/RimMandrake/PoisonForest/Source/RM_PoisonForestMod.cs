using UnityEngine;
using Verse;

namespace RimMandrake.PoisonForest
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
    public class RM_PoisonForestSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // CAULDRON_TREE_METAL_YIELD_1: the metal second yield on the thornwood
        // and martyr tree. Off = they yield wood only. Factor scales the count.
        public static bool metalYieldEnabled = true;
        public static float metalYieldFactor = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref metalYieldEnabled, "metalYieldEnabled", true, true);
            Scribe_Values.Look(ref metalYieldFactor, "metalYieldFactor", 1f, true);
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

    public class RM_PoisonForestMod : Mod
    {
        public static RM_PoisonForestSettings settings;

        public RM_PoisonForestMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_PoisonForestSettings>();
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
