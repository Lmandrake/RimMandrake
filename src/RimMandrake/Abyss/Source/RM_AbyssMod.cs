using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: every mod ships a real
    // settings screen. No mechanics kit exists for this biome yet (the
    // Unveiling weather, darkbeast Dark-halo behaviour, gust-wind
    // variability are all unbuilt — biome_mod_architecture.md §5 step 1:
    // "a ModSettings class with the master toggle only, no kit mechanics
    // exist yet to gate"), so the only control is the standard worldgen-
    // rarity slider every sibling biome mod ships.
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AbyssSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // ABYSS_GHARREK_BUILD_1: the shared gust signal (off = no gusts, gharreks never open).
        public static bool gustsEnabled = true;
        // ABYSS_GHARREK_BUILD_1: gharreks lie dormant in the still and feed in gusts (off = ordinary animals).
        public static bool gharrekReflexEnabled = true;
        // ABYSS_DURRGAK_BUILD_1: cairn rings on Abyss maps and wild durrgaks laying them.
        public static bool durrgakSignsEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref gustsEnabled, "gustsEnabled", true, true);
            Scribe_Values.Look(ref gharrekReflexEnabled, "gharrekReflexEnabled", true, true);
            Scribe_Values.Look(ref durrgakSignsEnabled, "durrgakSignsEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Abyss never generates on a new planet. "
                       + "The default places a handful of rare, hilly, night-dark patches. "
                       + "Affects planets generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.GapLine();
            list.CheckboxLabeled("Gusts", ref gustsEnabled,
                "A shared wind pulse on Abyss maps. Off: no gusts, so gharreks never open.");
            list.CheckboxLabeled("Gharrek gust reflex", ref gharrekReflexEnabled,
                "Gharreks lie dormant in the still and open and feed in gusts. Off: ordinary animals.");
            list.CheckboxLabeled("Durrgak signs", ref durrgakSignsEnabled,
                "Cairn rings and a steel-lined cache on Abyss maps, and wild durrgaks laying rings. Off: none.");

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

    public class RM_AbyssMod : Mod
    {
        public static RM_AbyssSettings settings;

        public RM_AbyssMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_AbyssSettings>();
        }

        public override string SettingsCategory()
        {
            return "Abyss";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
