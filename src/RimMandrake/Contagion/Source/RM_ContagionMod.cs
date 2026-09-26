using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: every mod ships a real
    // settings screen. CONTAGION_GENOME_ORGAN_GROWING_1 (2026-09-26) added the
    // mod's first real mechanic — the amoeba genome/organ-growing loop — so
    // this now also carries that feature's own on/off toggle, default =
    // shipped behaviour (on).
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_ContagionSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // CONTAGION_GENOME_ORGAN_GROWING_1: master toggle for the genome
        // sample extraction recipe and the amoeba-injection interaction.
        // Off degrades gracefully — the recipe refuses and the float-menu
        // option simply never appears.
        public static bool genomeOrganGrowingEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref genomeOrganGrowingEnabled, "genomeOrganGrowingEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Contagion never generates on a new planet. "
                       + "The default places a handful of rare, hot, storm-roofed peaks. "
                       + "Affects planets generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.Gap();
            list.CheckboxLabeled(
                "Amoeba genome/organ growing enabled",
                ref genomeOrganGrowingEnabled,
                "Lets a colonist extract a genome sample and inject it into a Contagion "
                + "amoeba (AA_RedGoo), which gestates a one-time batch of organs matched "
                + "to that colonist and dies producing it. Off removes the surgery recipe "
                + "and the injection option entirely.");

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

    public class RM_ContagionMod : Mod
    {
        public static RM_ContagionSettings settings;

        public RM_ContagionMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_ContagionSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Contagion";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
