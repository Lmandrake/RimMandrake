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

        // ABYSS_GHARREK_BUILD_1: gharreks go dormant in the still and open at gusts. Off = they are
        // ordinary always-active animals. Safe mid-game.
        public static bool gustFeedersEnabled = true;

        // ABYSS_DURRGAK_BUILD_1: wild durrgaks place obsidian-shard rings. Off = none are placed (existing rings stay).
        public static bool durrgakRingsEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref gustFeedersEnabled, "gustFeedersEnabled", true, true);
            Scribe_Values.Look(ref durrgakRingsEnabled, "durrgakRingsEnabled", true, true);
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

            list.CheckboxLabeled("Gharreks sleep in the still and feed at gusts", ref gustFeedersEnabled,
                "On: gharreks lie dormant until a gust, then open and feed together. Off: they behave as ordinary animals.");

            list.CheckboxLabeled("Wild durrgaks set rings of shards", ref durrgakRingsEnabled,
                "On: wild durrgaks slowly arrange obsidian-shard rings on the ground they roam. Off: none are placed; rings already standing stay. Safe mid-game.");

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
