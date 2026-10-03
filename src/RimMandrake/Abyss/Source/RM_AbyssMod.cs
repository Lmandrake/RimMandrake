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
        // ABYSS_DURRGAK_BUILD_1: a new Abyss map gets a stocked den, a row of rings, sometimes a salvage cache. Off = none on maps generated afterwards.
        public static bool durrgakMapSignsEnabled = true;

        // ABYSS_KRIZZAK_BUILD_1: wild krizzaks dim glow plants and lit lamps they settle on. Off = they just fly. Safe mid-game.
        public static bool krizzakLightEatingEnabled = true;

        // ABYSS_DONOR_BEASTS_FREED_1: the summ regenerates and burns in daylight; the drokattak hackles before it lunges.
        public static bool summRegenerates = true;
        public static bool summUVSensitive = true;
        public static bool drokattakHackleEnabled = true;

        // ABYSS_ETCHFALL_BUILD_1: grain erosion strength on unroofed rock and steel. 0 = off, 1 = shipped.
        public static float etchfallStrength = 1f;

        // ABYSS_DARK_BUILD_1: the Dark as real air. Master toggle, strength slider (0 = no effect, 1 = shipped), the Unveiling and the storm call.
        public static bool darkEnabled = true;
        public static float darkStrength = 1f;
        public static bool unveilingEnabled = true;
        public static bool stormCallEnabled = true;

        // ABYSS_HIDDEN_SHIP_PROBES_1: a landed gravship slowly hides; probes still come. Safe mid-game.
        public static bool shipCoverEnabled = true;
        public static bool probesEnabled = true;

        // ABYSS_INVENTED_CREATURES_TO_RM_1: the skarnix flees firelight and heated space. Off = it ignores light. Safe mid-game.
        public static bool lightAversionEnabled = true;
        public static float fleeRadiusMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lightAversionEnabled, "lightAversionEnabled", true, true);
            Scribe_Values.Look(ref fleeRadiusMultiplier, "fleeRadiusMultiplier", 1f, true);
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref gustFeedersEnabled, "gustFeedersEnabled", true, true);
            Scribe_Values.Look(ref durrgakRingsEnabled, "durrgakRingsEnabled", true, true);
            Scribe_Values.Look(ref durrgakMapSignsEnabled, "durrgakMapSignsEnabled", true, true);
            Scribe_Values.Look(ref krizzakLightEatingEnabled, "krizzakLightEatingEnabled", true, true);
            Scribe_Values.Look(ref summRegenerates, "summRegenerates", true, true);
            Scribe_Values.Look(ref summUVSensitive, "summUVSensitive", true, true);
            Scribe_Values.Look(ref drokattakHackleEnabled, "drokattakHackleEnabled", true, true);
            Scribe_Values.Look(ref etchfallStrength, "etchfallStrength", 1f, true);
            Scribe_Values.Look(ref darkEnabled, "darkEnabled", true, true);
            Scribe_Values.Look(ref darkStrength, "darkStrength", 1f, true);
            Scribe_Values.Look(ref unveilingEnabled, "unveilingEnabled", true, true);
            Scribe_Values.Look(ref stormCallEnabled, "stormCallEnabled", true, true);
            Scribe_Values.Look(ref shipCoverEnabled, "shipCoverEnabled", true, true);
            Scribe_Values.Look(ref probesEnabled, "probesEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // the screen outgrew one page: scroll it (view height measured from the last draw)
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(inRect.height, lastHeight));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Abyss never generates on a new planet. "
                       + "The default places a handful of rare, hilly, night-dark patches. "
                       + "Affects planets generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.CheckboxLabeled("Gharreks sleep in the still and feed at gusts", ref gustFeedersEnabled,
                "On: gharreks lie dormant until a gust, then open and feed together. Off: they behave as ordinary animals.");

            list.CheckboxLabeled("Wild durrgaks set rings of shards", ref durrgakRingsEnabled,
                "On: wild durrgaks slowly arrange obsidian-shard rings on the ground they roam. Off: none are placed; rings already standing stay. Safe mid-game.");
            list.CheckboxLabeled("New maps carry a durrgak den and rings", ref durrgakMapSignsEnabled,
                "On: each new Abyss map has a tidy den lined with scrap steel, a row of shard rings, and sometimes a salvage cache. Off: none. Affects maps generated afterwards (map generation).");

            list.CheckboxLabeled("Wild krizzaks eat light", ref krizzakLightEatingEnabled,
                "On: wild krizzaks settle on glow plants and lit lamps and shrink their light until they leave. Off: they only fly about. Light recovers on its own. Safe mid-game.");

            list.CheckboxLabeled("Summs regenerate", ref summRegenerates,
                "On: a summ slowly heals its wounds on its own. Off: it heals like any animal. Safe mid-game.");
            list.CheckboxLabeled("Summs burn in daylight", ref summUVSensitive,
                "On: a summ under an open daylit sky takes a daylight burn (pain, slowness) that fades in shade or darkness. Off: daylight does nothing to it. Safe mid-game.");
            list.CheckboxLabeled("Drokattaks rattle their quills before they lunge", ref drokattakHackleEnabled,
                "On: a drokattak that starts a hunt or an attack stops for a moment and rattles its quills, a warning. Off: it lunges at once. Safe mid-game.");

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

            list.CheckboxLabeled("Skarnixes flee light", ref lightAversionEnabled,
                "On: a skarnix standing in light breaks off what it is doing and slinks toward the nearest dark cell, so a lit camp neutralises it. Off: it ignores light entirely. Safe mid-game.");
            if (lightAversionEnabled)
            {
                list.Label("  Flee search radius: " + fleeRadiusMultiplier.ToString("0.00") + "x (default searches 10 cells out)");
                fleeRadiusMultiplier = list.Slider(fleeRadiusMultiplier, 0.5f, 2f);
            }

            list.CheckboxLabeled("A landed gravship slowly hides", ref shipCoverEnabled,
                "On: a gravship kept quiet (few lit lamps) in the Abyss slowly drops out of sight; the cover lapses after a while, resets when the engine leaves, and collapses if a probe reports. Off: no cover. Safe mid-game.");
            list.CheckboxLabeled("Probes hunt the hidden ship", ref probesEnabled,
                "On: while the ship is hidden, probes come now and then. A probe that keeps a moving colonist or lit lamp in sight reports and the cover collapses. Off: the cover is never tested.");

            lastHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scroll;
        private static float lastHeight = 1200f;

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
