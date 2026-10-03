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

        // ABYSS_KRIZZAK_BUILD_1: wild krizzaks dim glow plants and lit lamps they settle on. Off = they just fly. Safe mid-game.
        public static bool krizzakLightEatingEnabled = true;

        // ABYSS_ETCHFALL_BUILD_1: grain erosion strength on unroofed rock and steel. 0 = off, 1 = shipped.
        public static float etchfallStrength = 1f;

        // ABYSS_DARK_BUILD_1: the Dark as real air. Master toggle, strength slider (0 = no effect, 1 = shipped), the Unveiling and the storm call.
        public static bool darkEnabled = true;
        public static float darkStrength = 1f;
        public static bool unveilingEnabled = true;
        public static bool stormCallEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref gustFeedersEnabled, "gustFeedersEnabled", true, true);
            Scribe_Values.Look(ref durrgakRingsEnabled, "durrgakRingsEnabled", true, true);
            Scribe_Values.Look(ref krizzakLightEatingEnabled, "krizzakLightEatingEnabled", true, true);
            Scribe_Values.Look(ref etchfallStrength, "etchfallStrength", 1f, true);
            Scribe_Values.Look(ref darkEnabled, "darkEnabled", true, true);
            Scribe_Values.Look(ref darkStrength, "darkStrength", 1f, true);
            Scribe_Values.Look(ref unveilingEnabled, "unveilingEnabled", true, true);
            Scribe_Values.Look(ref stormCallEnabled, "stormCallEnabled", true, true);
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

            list.CheckboxLabeled("Wild krizzaks eat light", ref krizzakLightEatingEnabled,
                "On: wild krizzaks settle on glow plants and lit lamps and shrink their light until they leave. Off: they only fly about. Light recovers on its own. Safe mid-game.");

            list.Label("Etchfall strength: " + (etchfallStrength <= 0.001f ? "off" : etchfallStrength.ToString("0.0") + "x"));
            etchfallStrength = list.Slider(etchfallStrength, 0f, 3f);
            list.Label("How fast falling grain erodes unroofed rock and steel into tholin dust. 0 = off; roofed cells are never touched. Safe mid-game; hollows already made stay.");

            list.CheckboxLabeled("The Dark blinds and swallows lamplight", ref darkEnabled,
                "On: in the Abyss the air is dark; pawns lose sight, aim and melee skill and lamps shrink, except where warmth thins it. Off: the Abyss weather is plain sky only. Safe mid-game.");
            list.Label("Dark strength: " + (darkStrength <= 0.001f ? "off" : darkStrength.ToString("0.0") + "x"));
            darkStrength = list.Slider(darkStrength, 0f, 2f);
            list.Label("How hard the Dark presses on sight, aim, melee and lamplight. 0 = no effect. Warm places stay clear at any strength.");

            list.CheckboxLabeled("The Unveiling may happen", ref unveilingEnabled,
                "On: rarely the Dark folds away for a few hours and the whole country shows. Off: it never lifts.");

            list.CheckboxLabeled("Storm giant calls in Witchfire storms", ref stormCallEnabled,
                "On: some thunder in Witchfire storms is a summ calling, a flash with no lightning, and one may come down and cross the map. Off: ordinary storms.");

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
