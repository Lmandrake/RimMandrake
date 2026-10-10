using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;
using RimMandrake.RustCathedral.Hum;
using RimMandrake.RustCathedral.Walls;

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

        // RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 §6. borehulkEnabled is a MAP
        // GENERATION toggle (RM_GenStep_BorehulkPlacement): it affects maps
        // generated afterwards, never a borehulk already placed.
        // borehulkSpawnChance default 0.6 is the item's number;
        // borehulkGrindMtbHours default 4 is PROVISIONAL ("every so often").
        public static bool borehulkEnabled = true;
        public static float borehulkSpawnChance = 0.6f;
        public static bool borehulkGrindEnabled = true;
        public static float borehulkGrindMtbHours = 4f;

        // RUSTCATHEDRAL_BASE_FINISH_BUILD_1 parts 3 and 5. Both are MAP GENERATION toggles: they affect maps
        // generated afterwards. Counts are PROVISIONAL ("a handful" of strays; eels "at a low commonality").
        public static bool coolantEelsEnabled = true;
        public static int coolantEelCount = 4;
        public static bool straysEnabled = true;
        public static int strayCount = 5;

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
            Scribe_Values.Look(ref borehulkEnabled, "borehulkEnabled", true);
            Scribe_Values.Look(ref borehulkSpawnChance, "borehulkSpawnChance", 0.6f);
            Scribe_Values.Look(ref borehulkGrindEnabled, "borehulkGrindEnabled", true);
            Scribe_Values.Look(ref borehulkGrindMtbHours, "borehulkGrindMtbHours", 4f);
            Scribe_Values.Look(ref coolantEelsEnabled, "coolantEelsEnabled", true);
            Scribe_Values.Look(ref coolantEelCount, "coolantEelCount", 4);
            Scribe_Values.Look(ref straysEnabled, "straysEnabled", true);
            Scribe_Values.Look(ref strayCount, "strayCount", 5);
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
            Scribe_Values.Look(ref RustCathedralHumSettings.lineCycleEnabled, "hum_lineCycleEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.lineCycleMtbDays, "hum_lineCycleMtbDays", 8f);
            Scribe_Values.Look(ref RustCathedralHumSettings.lineCycleMinSeconds, "hum_lineCycleMinSeconds", 60f);
            Scribe_Values.Look(ref RustCathedralHumSettings.lineCycleMaxSeconds, "hum_lineCycleMaxSeconds", 120f);
            Scribe_Values.Look(ref RustCathedralHumSettings.humReadingEnabled, "hum_humReadingEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.humReaderThresholdDays, "hum_humReaderThresholdDays", 5f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltsEnabled, "hum_hullBoltsEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltBoardMin, "hum_hullBoltBoardMin", 1);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltBoardMax, "hum_hullBoltBoardMax", 3);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltNoneChance, "hum_hullBoltNoneChance", 0.15f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltEdgePull, "hum_hullBoltEdgePull", 0.35f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltWitnessEnabled, "hum_hullBoltWitnessEnabled", true);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltWeightScale, "hum_hullBoltWeightScale", 1f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltIrritationCap, "hum_hullBoltIrritationCap", 60f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltRealiseDays, "hum_hullBoltRealiseDays", 10f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltRevealDays, "hum_hullBoltRevealDays", 5f);
            Scribe_Values.Look(ref RustCathedralHumSettings.hullBoltPetMemoryEnabled, "hum_hullBoltPetMemoryEnabled", true);

            Scribe_Values.Look(ref RustCathedralWallsSettings.wallTiersEnabled, "walls_wallTiersEnabled", true);
            Scribe_Values.Look(ref RustCathedralWallsSettings.sacredWallsEnabled, "walls_sacredWallsEnabled", true);
            Scribe_Values.Look(ref RustCathedralWallsSettings.sacredWallChanceMultiplier, "walls_sacredWallChanceMultiplier", 1f);
            Scribe_Values.Look(ref RustCathedralWallsSettings.livePatternMetalGateEnabled, "walls_livePatternMetalGateEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_RustCathedralSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_RustCathedralSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string> { "Not wired yet (these change nothing)" };

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope the biome worker (GetScore) and three GenSteps (borehulk placement, canal eels, strays) run at world or map generation ([new maps only]); the roach think node, the borehulk drill comp's tick and its grind roll read live ([now]). The four cross-biome fields are read by nothing, so they sit in the collapsed change-nothing group (crossBiomeBiomeList is a string with no control and is kept only as a saved key).ED per setting against its read site (2026-10-10): the biome worker (GetScore) and three GenSteps (borehulk placement, canal eels, strays) run at world or map generation ([new maps only]); the roach think node, the borehulk drill comp's tick and its grind roll read live ([now]). The four cross-biome fields are read by nothing, so they sit in the collapsed change-nothing group (crossBiomeBiomeList is a string with no control and is kept only as a saved key).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Biome rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "biomeRarityFactor" }))
            {
                list.Label("Biome rarity: " + RustCathedralRarityLabel());
                biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Cathedral roaches", RimMandrake.Shared.SettingScope.Now, new[] { "roachCleaningEnabled" }))
            {
                list.CheckboxLabeled("Roaches clean filth and wastepacks", ref roachCleaningEnabled,
                    "Off: the cathedral roach still spawns and wanders, it just never seeks out filth or wastepacks to eat.");
                list.GapLine();
            }

            if (Group(list, "The borehulk on new maps (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "borehulkEnabled", "borehulkSpawnChance" }))
            {
                list.CheckboxLabeled("Map generation: may place a borehulk", ref borehulkEnabled,
                    "Map generation only: applies to maps generated afterwards. Off: no new map gets a borehulk; one already placed stays.");
                list.Label("Borehulk chance per map: " + borehulkSpawnChance.ToStringPercent());
                borehulkSpawnChance = list.Slider(borehulkSpawnChance, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "Borehulk grinding", RimMandrake.Shared.SettingScope.Now, new[] { "borehulkGrindEnabled", "borehulkGrindMtbHours" }))
            {
                list.CheckboxLabeled("Worn borehulk grinds its stub on the plate", ref borehulkGrindEnabled,
                    "Off: the worn borehulk never lowers its drill to scrape (no sound, no sparks).");
                list.Label("Grind roughly every " + borehulkGrindMtbHours.ToString("0.0") + " hours");
                borehulkGrindMtbHours = list.Slider(borehulkGrindMtbHours, 0.5f, 24f);
                list.GapLine();
            }

            if (Group(list, "Canal eels and dried-out dead on new maps (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "coolantEelsEnabled", "coolantEelCount", "straysEnabled", "strayCount" }))
            {
                list.CheckboxLabeled("Map generation: living coolant eels in the canals", ref coolantEelsEnabled,
                    "Map generation only: applies to maps generated afterwards. Off: no new map gets living eels; the canals stay fishable.");
                list.Label("Living eels per map: " + coolantEelCount);
                coolantEelCount = (int)list.Slider(coolantEelCount, 0f, 20f);
                list.CheckboxLabeled("Map generation: dried-out dead at the edges", ref straysEnabled,
                    "Map generation only: applies to maps generated afterwards. Off: no new map gets the desiccated animal dead at its edges.");
                list.Label("Dead per map: " + strayCount);
                strayCount = (int)list.Slider(strayCount, 0f, 20f);
                list.GapLine();
            }

            if (Group(list, "Not wired yet (these change nothing)", RimMandrake.Shared.SettingScope.Now, new[] { "crossBiomeEnabled", "crossBiomeEverywhere", "crossBiomeBiomeList", "crossBiomeCoverage" }))
            {
                list.CheckboxLabeled("Allow this mod's mechanics on other biomes", ref crossBiomeEnabled,
                    "Reserved for a future pass. No mechanic in this mod currently reads this switch (nor crossBiomeEverywhere, crossBiomeBiomeList or crossBiomeCoverage, which have no controls).");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string RustCathedralRarityLabel()
        {
            float v = biomeRarityFactor;
            if (v <= 0.001f) return "never generates";
            if (v < 0.6f) return "very rare (" + v.ToString("0.0") + "x)";
            if (v < 1.6f) return "default (" + v.ToString("0.0") + "x)";
            if (v < 4f) return "uncommon (" + v.ToString("0.0") + "x)";
            return "common (" + v.ToString("0.0") + "x)";
        }
    }

    public class RM_RustCathedralMod : Mod
    {
        public static RM_RustCathedralSettings settings;

        // The absorbed kits' settings DATA classes (all-static fields) still need ONE instance each to call the
        // non-static DoWindowContents() on. RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1: Verse.Mod tracks only ONE ModSettings
        // per Mod object, so plain `new` is correct; their static fields are scribed by RM_RustCathedralSettings.ExposeData().
        private readonly RustCathedralHumSettings humSettings = new RustCathedralHumSettings();
        private readonly RustCathedralWallsSettings wallsSettings = new RustCathedralWallsSettings();
        private static int tab;

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
            // Three screens (this mod, the Hum kit, the Walls kit), one tab each; each is a full SettingsKit screen
            // with its own search box and scroll view.
            string[] names = { "The Cathedral", "The hum", "Walls" };
            float w = inRect.width / names.Length;
            for (int i = 0; i < names.Length; i++)
            {
                if (Widgets.ButtonText(new Rect(inRect.x + i * w, inRect.y, w - 4f, 30f), (tab == i ? "[ " + names[i] + " ]" : names[i])))
                    tab = i;
            }
            Rect body = new Rect(inRect.x, inRect.y + 36f, inRect.width, inRect.height - 36f);
            if (tab == 1) humSettings.DoWindowContents(body);
            else if (tab == 2) wallsSettings.DoWindowContents(body);
            else settings.DoWindowContents(body);
        }
    }
}
