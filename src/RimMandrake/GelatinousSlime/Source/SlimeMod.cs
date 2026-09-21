using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — the ruled rarity slider and the two ruled flavor hooks.
    //
    // Spec §2, round 2: "worldgen 1-3 rare patches + rarity slider ... Engine:
    // the standard Mod + ModSettings classes — precedent already verified
    // in-repo: the decompiled GenepacksInjection mod's
    // GenepacksInjectionMod.Settings.UseEndogenes toggle."
    // Spec §10, ruled round 2: "BOTH flavor hooks SHIP as mod-settings
    // toggles — the 'Entry recorded' registry flavor and the read-mark scars
    // are options, ON BY DEFAULT [default state INVENTED]."
    //
    // 🔑 STATIC FIELDS, READ FROM EVERYWHERE, WRITTEN ONLY HERE. The biome
    // worker runs during worldgen when no Mod instance may be handy, so the
    // values have to be statics that survive a settings load — hence the
    // Scribe_Values pattern below rather than instance fields.
    // ════════════════════════════════════════════════════════════════════
    public class SlimeSettings : ModSettings
    {
        // 1.0 = the ruled default (1-3 rare patches on a default planet).
        // 0 = the biome never generates at all. 8 = common.
        public static float rarityFactor = 1f;

        // "Entry recorded" — the body acknowledges what it just read.
        public static bool flavorEntryRecorded = true;

        // Read-marks: the smear a slimified creature leaves where it walked.
        public static bool flavorReadMarks = true;


        // ── TITANOSLIME (TITANOSLIME_SLIME_BIOME_1, spec §5) ────────────
        // Project rule: every mod ships a real settings screen — on/off per
        // major feature, tuning where a number is the experience, defaults =
        // shipped behaviour, all-off degrades gracefully. All-off here leaves
        // a slow, big, slam-only predator that still works.

        // Rarity of the titanoslime in any biome that rosters it. Applied by
        // rewriting the LOADED BiomeDef's wildAnimals commonality — see
        // TitanoslimeSpawnTuning below.
        public static float titanoslimeSpawnFactor = 1f;

        // Off: the engulf tool always slams, and anything already held is
        // released on the next round.
        public static bool titanoslimeEngulfs = true;

        // Off: absorbedMass is frozen at its spawn value; the creature keeps
        // whatever stage it rolled and never moves off it.
        public static bool titanoslimeGrows = true;

        // Off: mass never decreases — starving, dry ground and wounds stop
        // taking it back. The owner's shipped default is ON (reversible):
        // nothing is ever permanently huge.
        public static bool titanoslimeReversible = true;

        // 1-5. Caps the ladder; at 2, absorbedMass 12 still reads as stage 2.
        public static int titanoslimeMaxStage = 5;

        // Off: a cut titanoslime stops leaking gelatids.
        public static bool titanoslimeSheds = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref rarityFactor, "rarityFactor", 1f, true);
            Scribe_Values.Look(ref flavorEntryRecorded, "flavorEntryRecorded", true, true);
            Scribe_Values.Look(ref flavorReadMarks, "flavorReadMarks", true, true);
            Scribe_Values.Look(ref titanoslimeSpawnFactor, "titanoslimeSpawnFactor", 1f, true);
            Scribe_Values.Look(ref titanoslimeEngulfs, "titanoslimeEngulfs", true, true);
            Scribe_Values.Look(ref titanoslimeGrows, "titanoslimeGrows", true, true);
            Scribe_Values.Look(ref titanoslimeReversible, "titanoslimeReversible", true, true);
            Scribe_Values.Look(ref titanoslimeMaxStage, "titanoslimeMaxStage", 5, true);
            Scribe_Values.Look(ref titanoslimeSheds, "titanoslimeSheds", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the gelatinous slime never generates on a new planet. "
                       + "The default places roughly one to three rare patches. "
                       + "Changing this affects planets generated afterwards, never "
                       + "one that already exists.");
            rarityFactor = list.Slider(rarityFactor, 0f, 8f);
            list.GapLine();

            list.CheckboxLabeled("\"Entry recorded\" messages", ref flavorEntryRecorded,
                "The body acknowledges each genome it finishes filing.");
            list.CheckboxLabeled("Read-marks", ref flavorReadMarks,
                "Slimified creatures leave a smear where they have walked.");
            list.GapLine();

            list.Label("THE TITANOSLIME");
            list.Label("A titanic green slime that swallows pawns whole and grows on what "
                       + "it absorbs. With every box below unticked it is still a large, "
                       + "slow predator that slams — nothing breaks, it just stops being "
                       + "the thing it was built to be.");

            list.CheckboxLabeled("Swallow pawns whole", ref titanoslimeEngulfs,
                "On: a titanoslime that hits with its engulfing mass takes the target "
                + "inside itself and digests it. Off: that attack is an ordinary slam, "
                + "and anything already held is released.");

            list.CheckboxLabeled("Grows as it eats", ref titanoslimeGrows,
                "On: absorbing prey, and ordinary eating, move it up a five-stage ladder "
                + "from body size 6 to 40. Off: it keeps the stage it spawned at.");

            list.CheckboxLabeled("Growth is reversible", ref titanoslimeReversible,
                "On: starving, standing off slime terrain and being wounded all take "
                + "mass back, so nothing is permanently huge. Off: the ladder only "
                + "climbs.");

            list.CheckboxLabeled("Sheds gelatids when cut", ref titanoslimeSheds,
                "On: a wounded titanoslime of stage 2 or better comes apart into wild "
                + "gelatids as you fight it, losing mass with each one.");

            list.Label("Largest stage it can reach: " + MaxStageLabel());
            titanoslimeMaxStage = Mathf.RoundToInt(list.Slider(titanoslimeMaxStage, 1f, 5f));

            list.Label("Titanoslime rarity: " + TitanoslimeRarityLabel());
            list.Label("Multiplies how often a titanoslime spawns in any biome that lists "
                       + "one. At 0 none ever spawns. Takes effect on the next map "
                       + "generated; a titanoslime already on a map is unaffected.");
            titanoslimeSpawnFactor = list.Slider(titanoslimeSpawnFactor, 0f, 3f);

            list.End();
        }

        private static string MaxStageLabel()
        {
            switch (titanoslimeMaxStage)
            {
                case 1: return "1 — young titanoslime (body size 6)";
                case 2: return "2 — titanoslime (body size 10)";
                case 3: return "3 — great titanoslime (body size 16)";
                case 4: return "4 — elder titanoslime (body size 24)";
                default: return "5 — titanoslime colossus (body size 40)";
            }
        }

        private static string TitanoslimeRarityLabel()
        {
            if (titanoslimeSpawnFactor <= 0.001f) return "never spawns";
            if (titanoslimeSpawnFactor < 0.6f) return "very rare ("
                + titanoslimeSpawnFactor.ToString("0.0") + "x)";
            if (titanoslimeSpawnFactor < 1.6f) return "default ("
                + titanoslimeSpawnFactor.ToString("0.0") + "x)";
            return "common (" + titanoslimeSpawnFactor.ToString("0.0") + "x)";
        }

        private static string RarityLabel()
        {
            if (rarityFactor <= 0.001f) return "never generates";
            if (rarityFactor < 0.6f) return "very rare (" + rarityFactor.ToString("0.0") + "x)";
            if (rarityFactor < 1.6f) return "default, 1-3 patches (" + rarityFactor.ToString("0.0") + "x)";
            if (rarityFactor < 4f) return "uncommon (" + rarityFactor.ToString("0.0") + "x)";
            return "common (" + rarityFactor.ToString("0.0") + "x)";
        }
    }

    public class SlimeMod : Mod
    {
        public static SlimeSettings settings;

        public SlimeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<SlimeSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Gelatinous Slime";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        // Settings close -> re-apply the titanoslime rarity to the loaded
        // BiomeDefs, so the slider does not need a game restart.
        public override void WriteSettings()
        {
            base.WriteSettings();
            TitanoslimeSpawnTuning.Apply();
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // DEFS THIS ASSEMBLY NAMES.
    //
    // 🔴 GetNamedSilentFail, NOT [DefOf], AND THAT IS DELIBERATE. A [DefOf]
    // field for a Biotech-gated def logs a hard error on every load of a game
    // without Biotech, and About.xml promises that game works unchanged. The
    // resolver below returns null instead, and every caller is written to
    // no-op on null.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class SlimeDefs
    {
        public const string SlimeTerrainTag = "RM_SlimeTerrain";

        public static readonly BiomeDef GelatinousSlime =
            DefDatabase<BiomeDef>.GetNamedSilentFail("RM_GelatinousSlime");

        public static readonly HediffDef Slimification =
            DefDatabase<HediffDef>.GetNamedSilentFail("RM_Slimification");

        public static readonly HediffDef SlimeMarked =
            DefDatabase<HediffDef>.GetNamedSilentFail("RM_SlimeMarked");

        public static readonly HediffDef XenogerminationComa =
            DefDatabase<HediffDef>.GetNamedSilentFail("XenogerminationComa");

        public static readonly ThingDef RawSlime =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_RawSlime");

        public static readonly ThingDef SlimeSmear =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_SlimeSmear");

        public static readonly ThingDef GeneSeekerLoaded =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_GeneSeeker_Loaded");

        public static readonly TerrainDef SlimeRich =
            DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Rich");

        public static readonly TerrainDef SlimeGrass =
            DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Grass");

        public static readonly TerrainDef SlimeLiquid =
            DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Liquid");
    }
}
