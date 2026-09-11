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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref rarityFactor, "rarityFactor", 1f, true);
            Scribe_Values.Look(ref flavorEntryRecorded, "flavorEntryRecorded", true, true);
            Scribe_Values.Look(ref flavorReadMarks, "flavorReadMarks", true, true);
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

            list.End();
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
