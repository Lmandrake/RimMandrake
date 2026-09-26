using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // SCARLANDS_STANDALONE_MOD_1 — Mod Settings for Warscar.
    //
    // This biome ships no bespoke mechanic of its own: its two duplicated
    // flora defs (RM_Glower/RM_ScorchedStars) are plain harvestable plants
    // with no comp yet (the frozen twin's own radiation-dose harvest loop is
    // still owed to SCARLANDS_MECHANICS_2), and the frozen twin's own
    // scaria-mark/pre-sprung-dressing mechanics deliberately did NOT move
    // into this mod (this item's own `## spec`: "don't invent extra scope").
    // So this screen ships only the standard worldgen-rarity slider every
    // biome-worker mod ships, plus the honestly-disclosed reserved
    // cross-biome section (MOD_OPTIONS_RETROFIT_1 doctrine), same shape as
    // RM_Miasma/RM_RustCathedral's own screens.
    //
    // STATIC FIELD, read from worldgen with no Mod instance handy.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WarscarSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        public static float biomeRarityFactor = 1f;

        // MOD_OPTIONS_RETROFIT_1: reserved fields for letting this biome's
        // (currently nonexistent) mechanics run on other biomes too.
        // Persisted and exposed here honestly as NOT YET WIRED to any
        // mechanic — there is no mechanic in this mod for it to gate yet.
        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 Warscar never generates on a new planet. Affects planets "
                       + "generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.Label("Cross-biome (reserved — not yet wired to any mechanic in this build)");
            bool crossBiomeEnabledLocal = crossBiomeEnabled;
            list.CheckboxLabeled("Allow this mod's mechanics on other biomes", ref crossBiomeEnabledLocal,
                "Reserved for a future pass. No mechanic in this mod currently reads this switch.");
            crossBiomeEnabled = crossBiomeEnabledLocal;

            list.End();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_WarscarMod : Mod
    {
        public static RM_WarscarSettings settings;

        public RM_WarscarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarscarSettings>();
        }

        public override string SettingsCategory()
        {
            return "Warscar";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
