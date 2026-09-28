using UnityEngine;
using Verse;
using RimMandrake.Utinni.RustCathedralHum;
using RimMandrake.Utinni.RustCathedralWalls;

namespace RimMandrake.RustCathedral
{
    // ════════════════════════════════════════════════════════════════════
    // RUSTCATHEDRAL_RM_MOD_BUILD_1 — Mod Settings for the Rust Cathedral.
    //
    // This mod ABSORBS three former standalone satellite kits
    // (mandrake.rut.rustcathedralhum, mandrake.rut.rustcathedralwalls, and
    // the two roach defs duplicated out of mandrake.rut.rustcathedralroaches)
    // plus the biome itself. Per the item's assembly-merge trade (§6,
    // option (b)): Hum and Walls keep their own DLLs/namespaces/settings
    // DATA classes unchanged (zero namespace churn, zero XML class-binding
    // edits) — only their standalone `Mod`-derived wrapper classes
    // (RustCathedralHumSettingsMod / RustCathedralWallsSettingsMod) are
    // retired, replaced by this ONE settings screen for the whole mod,
    // which calls GetSettings<T>() for both their data classes plus this
    // mod's own new master/roach/cross-biome section.
    //
    // Master toggle shape follows the sibling biome-worker mods
    // (RM_MiasmaSettings.biomeRarityFactor / RM_PoisonForestMod): 0 = never
    // generates on a new planet. Everything else is a per-mechanic toggle,
    // default = shipped behavior, all-off degrades gracefully.
    // ════════════════════════════════════════════════════════════════════
    public class RM_RustCathedralSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        public static float biomeRarityFactor = 1f;

        // RUSTCATHEDRAL_RM_MOD_BUILD_1 §6: the roaches (RM_CathedralRoach)
        // absorbed from mandrake.rut.rustcathedralroaches carried NO toggle
        // at all in their donor mod — this is the first one. Gated for real
        // via RM_ThinkNode_ConditionalRoachCleaningEnabled, wrapped around
        // RM_ThinkNode_EatCleanable in RM_ThinkTree_CathedralRoach.xml (the
        // RM_ copy only — the frozen RUT_ twin's own roach/tree are
        // untouched). Off: the roach still spawns and wanders, it just never
        // seeks out filth/wastepacks to eat.
        public static bool roachCleaningEnabled = true;

        // RUSTCATHEDRAL_RM_MOD_BUILD_1 §6a / MOD_OPTIONS_RETROFIT_1: reserved
        // fields for letting this biome's mechanics run on OTHER biomes too.
        // Persisted and exposed here honestly as NOT YET WIRED to any
        // mechanic — no code in this mod or its absorbed kits reads them.
        // A future pass that actually threads a mechanic onto a foreign
        // biome via these fields does the real work; shipping the toggle
        // early without the wiring would be the settings-screen-that-lies
        // NightsideIce/Miasma precedent warns against, so the label says so.
        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref roachCleaningEnabled, "roachCleaningEnabled", true);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);

            // RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1: Verse.Mod caches ONE
            // ModSettings instance per Mod object (keyed by nothing — a second
            // GetSettings<T>() call for a different T just logs an error and
            // returns null). RM_RustCathedralMod's constructor used to call
            // GetSettings<>() three times for three different types, so
            // humSettings/wallsSettings were always null and their fields never
            // persisted. Fix: this is the ONLY ModSettings this mod registers;
            // the absorbed kits' static fields are scribed here directly.
            Scribe_Values.Look(ref RustCathedralHumSettings.humMechanicEnabled, "hum_humMechanicEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.commentaryEnabled, "hum_commentaryEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.goodwillDrainEnabled, "hum_goodwillDrainEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.irritationDecayRateMultiplier, "hum_irritationDecayRateMultiplier", 1f);
            Scribe_Values.Look(ref RustCathedralHumSettings.boltDanceEnabled, "hum_boltDanceEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.boltShedEnabled, "hum_boltShedEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.boltWatchedPricingEnabled, "hum_boltWatchedPricingEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.fishingPricingEnabled, "hum_fishingPricingEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.drillResponseEnabled, "hum_drillResponseEnabled", true);

            Scribe_Values.Look(ref RustCathedralWallsSettings.wallTiersEnabled, "walls_wallTiersEnabled", true);
            Scribe_Values.Look(ref RustCathedralWallsSettings.sacredWallsEnabled, "walls_sacredWallsEnabled", true);
            Scribe_Values.Look(ref RustCathedralWallsSettings.sacredWallChanceMultiplier, "walls_sacredWallChanceMultiplier", 1f);
            Scribe_Values.Look(ref RustCathedralWallsSettings.livePatternMetalGateEnabled, "walls_livePatternMetalGateEnabled", true);
        }

    }

    public class RM_RustCathedralMod : Mod
    {
        public static RM_RustCathedralSettings settings;

        // Absorbed kits' settings DATA classes (all-static fields, unchanged
        // from their satellite-mod days) still need ONE instance each to call
        // the non-static DoWindowContents() on. RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1:
        // Verse.Mod tracks only ONE ModSettings instance per Mod object, so a
        // second/third GetSettings<T>() call here for a different T returned
        // null instead of loading anything — plain `new` is correct: these
        // instances exist only to host the DoWindowContents() method, their
        // static fields are scribed by RM_RustCathedralSettings.ExposeData()
        // above, not by these instances' own (never-invoked-by-Scribe) ExposeData().
        private readonly RustCathedralHumSettings humSettings = new RustCathedralHumSettings();
        private readonly RustCathedralWallsSettings wallsSettings = new RustCathedralWallsSettings();

        public RM_RustCathedralMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_RustCathedralSettings>();
        }

        public override string SettingsCategory()
        {
            return "the Rust Cathedral";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            // Three independent sections stacked top to bottom: this mod's
            // own master/roach/cross-biome block, then the absorbed Hum
            // block, then the absorbed Walls block — each a full
            // Listing_Standard pass over its own vertical slice of inRect,
            // since RustCathedralHumSettings/RustCathedralWallsSettings'
            // DoWindowContents() (unchanged from their satellite-mod days)
            // each call Begin/End on the Rect they are handed.
            float thirdHeight = inRect.height / 3f;
            Rect ownRect = new Rect(inRect.x, inRect.y, inRect.width, thirdHeight);
            Rect humRect = new Rect(inRect.x, inRect.y + thirdHeight, inRect.width, thirdHeight);
            Rect wallsRect = new Rect(inRect.x, inRect.y + thirdHeight * 2f, inRect.width, thirdHeight);

            DoOwnSection(ownRect);
            humSettings.DoWindowContents(humRect);
            wallsSettings.DoWindowContents(wallsRect);
        }

        private static void DoOwnSection(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Worldgen — applies to planets generated afterwards, never one that already exists.");
            list.Label("Biome rarity: " + RustCathedralRarityLabel());
            RM_RustCathedralSettings.biomeRarityFactor = list.Slider(RM_RustCathedralSettings.biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.Label("Cathedral roaches (absorbed from the former mandrake.rut.rustcathedralroaches)");
            bool roachCleaningEnabled = RM_RustCathedralSettings.roachCleaningEnabled;
            list.CheckboxLabeled("Roaches clean filth and wastepacks", ref roachCleaningEnabled,
                "Off: the cathedral roach still spawns and wanders, it just never seeks out filth or wastepacks to eat.");
            RM_RustCathedralSettings.roachCleaningEnabled = roachCleaningEnabled;
            list.GapLine();

            list.Label("Cross-biome (reserved — not yet wired to any mechanic in this build)");
            bool crossBiomeEnabled = RM_RustCathedralSettings.crossBiomeEnabled;
            list.CheckboxLabeled("Allow this mod's mechanics on other biomes", ref crossBiomeEnabled,
                "Reserved for a future pass. No mechanic in this mod currently reads this switch.");
            RM_RustCathedralSettings.crossBiomeEnabled = crossBiomeEnabled;

            list.End();
        }

        private static string RustCathedralRarityLabel()
        {
            float v = RM_RustCathedralSettings.biomeRarityFactor;
            if (v <= 0.001f) return "never generates";
            if (v < 0.6f) return "very rare (" + v.ToString("0.0") + "x)";
            if (v < 1.6f) return "default (" + v.ToString("0.0") + "x)";
            if (v < 4f) return "uncommon (" + v.ToString("0.0") + "x)";
            return "common (" + v.ToString("0.0") + "x)";
        }
    }
}
