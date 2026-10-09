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

        // DEEPFIRE_WORLD_LIGHT_1 (owner card 2026-10-08, typed: "Deliberately cannot"): the Dark never shrinks deepfire
        // light — the one light it cannot take, and the reason to haul pigment down. Off = deepfire dims like any lamp.
        public static bool darkSparesDeepfire = true;

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

        // ABYSS_LAMP_CROPS_BUILD_1: the wickwood lights crops (overlight) and grows wild in the Abyss. Off = a plain glowing tree, struck from the wild. Restart.
        public static bool lampCropsEnabled = true;

        // ABYSS_FOLD_LAMP_BUILD_1: a lit fold-lamp holds a lane of clear air open; heat-folding is learned by watching. Off = plain heater-lamp / plain bench research.
        public static bool foldLaneEnabled = true;
        public static bool foldDiscoveryByWatching = true;

        // ABYSS_SOUNDSCAPE_BUILD_1: silence by default, sound comes in gusts; the Dark muffles those sounds. Soundscape off = the vanilla fog wind (restart).
        public static bool gustSoundscapeEnabled = true;
        public static bool darkMuffleEnabled = true;
        // ABYSS_DARK_MUFFLE_ALL_SOUNDS_1: the Dark also muffles every map sound (gunshots, footsteps, calls), via one Harmony postfix on Sample.Update. Needs darkMuffleEnabled too. Safe mid-game.
        public static bool darkMuffleAllSounds = true;
        // ABYSS_FREE_CRYPTID_1 (RM_AbyssCryptid.cs): rumor-sites, the exchange, the clear pocket around nothing, the whisper, the dream.
        public static bool cryptidSignsEnabled = true;

        // ABYSS_LIGHTFALL_BROOD_WRECK_1 (RM_BroodLair.cs, RM_BroodEgg.cs, RM_ShipWreck.cs): the brood lair, the wreck in
        // its wall, the egg's storms, the bonded beast's bane and hunger, and how deeply she sleeps.
        public static bool broodLairEnabled = true;
        public static bool wreckEnabled = true;
        public static bool eggStormsEnabled = true;
        public static bool baneEnabled = true;
        public static float beastHunger = 1f;
        public static float broodSleepDepth = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref broodLairEnabled, "broodLairEnabled", true, true);
            Scribe_Values.Look(ref wreckEnabled, "wreckEnabled", true, true);
            Scribe_Values.Look(ref eggStormsEnabled, "eggStormsEnabled", true, true);
            Scribe_Values.Look(ref baneEnabled, "baneEnabled", true, true);
            Scribe_Values.Look(ref beastHunger, "beastHunger", 1f, true);
            Scribe_Values.Look(ref broodSleepDepth, "broodSleepDepth", 1f, true);
            Scribe_Values.Look(ref lightAversionEnabled, "lightAversionEnabled", true, true);
            Scribe_Values.Look(ref fleeRadiusMultiplier, "fleeRadiusMultiplier", 1f, true);
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref gustFeedersEnabled, "gustFeedersEnabled", true, true);
            Scribe_Values.Look(ref durrgakRingsEnabled, "durrgakRingsEnabled", true, true);
            Scribe_Values.Look(ref durrgakMapSignsEnabled, "durrgakMapSignsEnabled", true, true);
            Scribe_Values.Look(ref krizzakLightEatingEnabled, "krizzakLightEatingEnabled", true, true);
            Scribe_Values.Look(ref darkSparesDeepfire, "darkSparesDeepfire", true, true);
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
            Scribe_Values.Look(ref lampCropsEnabled, "lampCropsEnabled", true, true);
            Scribe_Values.Look(ref foldLaneEnabled, "foldLaneEnabled", true, true);
            Scribe_Values.Look(ref foldDiscoveryByWatching, "foldDiscoveryByWatching", true, true);
            Scribe_Values.Look(ref gustSoundscapeEnabled, "gustSoundscapeEnabled", true, true);
            Scribe_Values.Look(ref darkMuffleEnabled, "darkMuffleEnabled", true, true);
            Scribe_Values.Look(ref darkMuffleAllSounds, "darkMuffleAllSounds", true, true);
            Scribe_Values.Look(ref cryptidSignsEnabled, "cryptidSignsEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // the screen outgrew one page: scroll it (view height measured from the last draw)
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(inRect.height, lastHeight));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Abyss never generates on a new planet. "
                       + "The default places a handful of rare, hilly, night-dark patches. "
                       + "Affects planets generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.CheckboxLabeled("Gharreks sleep in the still and feed at gusts", ref gustFeedersEnabled,
                "On: gharreks lie dormant until a gust, then open and feed together. Off: they behave as ordinary animals.");

            list.CheckboxLabeled("Wild sorters set rings of shards", ref durrgakRingsEnabled,
                "On: wild sorters slowly arrange obsidian-shard rings on the ground they roam. Off: none are placed; rings already standing stay. Safe mid-game.");
            list.CheckboxLabeled("New maps carry a sorter den and rings", ref durrgakMapSignsEnabled,
                "On: each new Abyss map has a tidy den lined with scrap steel, a row of shard rings, and sometimes a salvage cache. Off: none. Affects maps generated afterwards (map generation).");

            list.CheckboxLabeled("Wild krizzaks eat light", ref krizzakLightEatingEnabled,
                "On: wild krizzaks settle on glow plants and lit lamps and shrink their light until they leave. Off: they only fly about. Light recovers on its own. Safe mid-game.");
            list.CheckboxLabeled("The Dark cannot swallow deepfire", ref darkSparesDeepfire,
                "On: deepfire light (painted floors, glowing pawns, the glow tank) keeps its full reach in the Dark while every other lamp shrinks. Off: the Dark shrinks deepfire like any lamp. Needs Luminous Pigment. Safe mid-game.");

            list.CheckboxLabeled("Summs regenerate", ref summRegenerates,
                "On: a summ slowly heals its wounds on its own. Off: it heals like any animal. Safe mid-game.");
            list.CheckboxLabeled("Summs burn in daylight", ref summUVSensitive,
                "On: a summ under an open daylit sky takes a daylight burn (pain, slowness) that fades in shade or darkness. Off: daylight does nothing to it. Safe mid-game.");
            list.CheckboxLabeled("Ombrathias rattle their quills before they lunge", ref drokattakHackleEnabled,
                "On: an ombrathia that starts a hunt or an attack stops for a moment and rattles its quills, a warning. Off: it lunges at once. Safe mid-game.");

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

            list.CheckboxLabeled("Ishvariths flee light", ref lightAversionEnabled,
                "On: an ishvarith standing in light breaks off what it is doing and slinks toward the nearest dark cell, so a lit camp neutralises it. Off: it ignores light entirely. Safe mid-game.");
            if (lightAversionEnabled)
            {
                list.Label("  Flee search radius: " + fleeRadiusMultiplier.ToString("0.00") + "x (default searches 10 cells out)");
                fleeRadiusMultiplier = list.Slider(fleeRadiusMultiplier, 0.5f, 2f);
            }

            list.CheckboxLabeled("A landed gravship slowly hides", ref shipCoverEnabled,
                "On: a gravship kept quiet (few lit lamps) in the Abyss slowly drops out of sight; the cover lapses after a while, resets when the engine leaves, and collapses if a probe reports. Off: no cover. Safe mid-game.");
            list.CheckboxLabeled("Probes hunt the hidden ship", ref probesEnabled,
                "On: while the ship is hidden, probes come now and then. A probe that keeps a moving colonist or lit lamp in sight reports and the cover collapses. Off: the cover is never tested.");

            list.CheckboxLabeled("Wickwoods are lamp crops", ref lampCropsEnabled,
                "On: the wickwood, the Abyss's glowing tree, grows wild there and lights the ground beneath it brightly enough to grow crops; extract and replant it to light a farm. The Dark never swallows its light. Off: it is a plain glowing tree that does not farm and no longer grows wild. Takes effect after a restart.");

            list.CheckboxLabeled("Fold-lamps hold a lane of clear air", ref foldLaneEnabled,
                "On: a lit fold-lamp clears the Dark in a lane ahead of its throat, toward the way it faces. Off: it is a plain fuelled heater-lamp. Safe mid-game.");
            list.CheckboxLabeled("Heat-folding is learned by watching the Dark", ref foldDiscoveryByWatching,
                "On: heat-folding opens only after a colonist has stood in a warm clear pocket beside a fire or heater while the Dark lies all around (a letter says so). Off: it is an ordinary research project from the start.");

            list.CheckboxLabeled("Sound comes in gusts", ref gustSoundscapeEnabled,
                "On: the Dark is silent; each gust lands as an impact, gharrek gill-fans rustle after it, falling grain ticks on stone, and a lamp a krizzak is eating clatters. Off: the ordinary fog wind (after a restart) and none of these.");
            list.CheckboxLabeled("The Dark swallows those sounds", ref darkMuffleEnabled,
                "On: the gust sounds come through muffled while the camera looks into the Dark and sharp over a warm clear pocket. Off: always sharp. Safe mid-game.");
            list.CheckboxLabeled("The Dark swallows EVERY map sound", ref darkMuffleAllSounds,
                "On: gunshots, footsteps, animal calls and every other sound placed on an Abyss map are muffled by the Dark at the camera, not only the Abyss's own. Needs the setting above. Off: only the Abyss's own sounds. Safe mid-game.");

            list.CheckboxLabeled("Abyss: cryptid signs", ref cryptidSignsEnabled,
                "On: people whisper of visitors who come for the Dark, and are never seen. New maps may carry extra rings and "
                + "caches; an item left unwatched on a ring of shards in the Dark is sometimes swapped for goods of about its "
                + "value; a clear pocket rarely opens over nothing; colonists whisper, and after a long stay one may dream of not "
                + "needing the light. Off: none of it; the biome is whole without it. Rumor-sites affect maps generated afterwards.");

            list.CheckboxLabeled("A brood lair at the bottom of the deepest chasm", ref broodLairEnabled,
                "On: where a map is marked for it, a summ brood-mother the size of the land sleeps round her eggs among a field of great bones. "
                + "Light, salvage cutting and taking an egg stir her; she shows it before she wakes, and awake she cannot be fought. "
                + "Off: no lair on maps generated afterwards, and an existing lair's meter stops moving (map generation).");
            list.Label("How deeply she sleeps: " + broodSleepDepth.ToString("0.0") + "x");
            broodSleepDepth = list.Slider(broodSleepDepth, 0.5f, 2f);
            list.Label("Higher lets you take more before she wakes. Fixed for a lair when its map is made.");
            list.CheckboxLabeled("A wrecked rescue ship in the lair wall", ref wreckEnabled,
                "On: the lair holds a wrecked rescue gravship to cut fittings from. Your own ship takes only some of them, to restore what has worn; "
                + "the rest is loot. Off: no wreck on lairs generated afterwards (map generation).");
            list.CheckboxLabeled("A stolen egg brings Witchfire storms home", ref eggStormsEnabled,
                "On: while a stolen summ egg is kept on your home map, Witchfire storms gather there every several days and a summ comes looking. Off: the egg is quiet. Safe mid-game.");
            list.CheckboxLabeled("A bonded summ kills what it finds", ref baneEnabled,
                "On: a summ that imprinted on you hunts wild animals on its own, semi-randomly, and now and then turns on a tame one. Off: it behaves like any tame animal. Safe mid-game.");
            list.Label("Bonded summ hunger: " + beastHunger.ToString("0.0") + "x");
            beastHunger = list.Slider(beastHunger, 0.5f, 3f);
            list.Label("How ruinous its appetite is on top of its size. 1 = shipped.");

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
            new HarmonyLib.Harmony("mandrake.rm.abyss").PatchAll();
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
