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

        // CONTAGION_UNFINISHED_SPAWNER_1: master toggle for AA_RedGoo's
        // CompSpawnerUnfinished. Off degrades gracefully — the comp's CompTick
        // simply never spawns; any Unfinished already on the map keep living
        // out their (short) lives normally.
        public static bool unfinishedSpawnerEnabled = true;

        // CONTAGION_MECHANICS_BUILD_1 Part 1 — the Burn and the Bloom. Only
        // ever acts on a map whose biome carries RM_ContagionSkyExtension.
        // Off: no Burn is ever scheduled; the Bloom weather still rolls from
        // the biome's commonalities (it is plain weather).
        public static bool burnEnabled = true;
        public static bool burnTellsEnabled = true;
        // Multiplier on how often Burns come (1 = shipped: one every ~3 days).
        public static float burnFrequency = 1f;
        // Multiplier on the Burn's damage to natives and dose to visitors.
        public static float burnDamageFactor = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref genomeOrganGrowingEnabled, "genomeOrganGrowingEnabled", true, true);
            Scribe_Values.Look(ref unfinishedSpawnerEnabled, "unfinishedSpawnerEnabled", true, true);
            Scribe_Values.Look(ref burnEnabled, "burnEnabled", true, true);
            Scribe_Values.Look(ref burnTellsEnabled, "burnTellsEnabled", true, true);
            Scribe_Values.Look(ref burnFrequency, "burnFrequency", 1f, true);
            Scribe_Values.Look(ref burnDamageFactor, "burnDamageFactor", 1f, true);
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

            list.Gap();
            list.CheckboxLabeled(
                "The Unfinished spawner enabled",
                ref unfinishedSpawnerEnabled,
                "Lets the Contagion's red goo (AA_RedGoo) periodically bud a short-lived "
                + "Unfinished chimera nearby — random-limb, days-long-lived, dissolving to "
                + "goo on death. Off stops new ones from budding; any already alive keep "
                + "living out their (short) lives normally.");

            list.GapLine();
            list.CheckboxLabeled(
                "The Burn enabled",
                ref burnEnabled,
                "Rare tears in the Contagion's storm: the red fog lifts, ranged fire works, "
                + "and raw UV scorches everything under open sky — natives burn and dive for "
                + "roof, canopy or water; visitors take a sunscald dose. Only ever happens on a "
                + "Contagion map. Off: the storm never tears.");
            list.CheckboxLabeled(
                "Burn tells enabled",
                ref burnTellsEnabled,
                "Shortly before a Burn the gawpsacks stop and settle, puffing, as one — "
                + "the only forecast the valley gives. Off: Burns arrive unannounced.");
            list.Label("Burn frequency: " + burnFrequency.ToString("0.00") + "x (1 = one every ~3 days)");
            burnFrequency = list.Slider(burnFrequency, 0.1f, 4f);
            list.Label("Burn damage: " + burnDamageFactor.ToString("0.00") + "x (0 = weather only, no harm)");
            burnDamageFactor = list.Slider(burnDamageFactor, 0f, 3f);

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
