using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LanternDeeps
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Lantern Deeps.
    //
    // The mod's runtime mechanisms are GenStep_ScatterCavePortal and
    // GenStep_ScatterMineshaftPortal, both WORLDGEN-AFFECTING steps (new maps
    // only): each scatters its own entrance onto a qualifying ≤ -40°C biome
    // at a flat per-map chance (LANTERN_DEEPS_INJECTION_1's own comment:
    // "FOUNDRY's placeholder pick pending the owner's actual density call").
    // Exposed here as a master toggle plus a multiplier per entrance type,
    // default 1x = shipped rate. MapComponent_LanternDeepDarkness (spec item
    // 6, the darkness mechanic) runs only inside an already-generated Deep,
    // so it gets its own toggle rather than sharing either entrance's.
    public class LanternDeepsSettings : ModSettings
    {
        // LANTERNDEEPS_RM_MOD_BUILD_1 (2026-09-25) — the §6a master toggle this
        // mod was missing: off, both entrance GenSteps (cave-mouth emergence
        // and ruined mineshaft) no-op unconditionally, checked before either's
        // own per-mechanic toggle and before the biome allowlist, same
        // "checked first" escape the per-mechanic toggles already use. A Deep
        // that already exists (already entered) is untouched — this only
        // gates whether a NEW map ever grows an entrance to one.
        public static bool lanternDeepsEnabled = true;

        public static bool emergenceEnabled = true;
        public static float emergenceChanceMultiplier = 1f;
        public static bool mineshaftEnabled = true;
        public static float mineshaftChanceMultiplier = 1f;
        public static bool darknessMechanicEnabled = true;
        public static float darknessThresholdMultiplier = 1f;
        // LANTERNDEEPS_LANTERN_LIGHT_BUILD_1: light from Lanterns alone does not count toward the darkness mechanic.
        public static bool safeLanternEnabled = true;

        // CAVERNS_PARITY_BUILD_1 — the two features the mod now OWNS rather than
        // borrows from Biomes! Caverns, each gated per the standing rule
        // (every mod ships real Mod Settings; defaults = shipped behavior;
        // all-off degrades gracefully).
        //
        // Both are WORLDGEN-AFFECTING in the same sense the entrance scatters
        // are: they are read while a Deep's pocket map is being generated, so a
        // change applies to the NEXT Deep entered, never to one already made.
        // The Deeps remain persistent maps (sheet hard ban 5) either way.
        //
        // All-off behaviour: a Deep with formations off and flora off is still a
        // complete, enterable, mineable cavern — gravel, lanternstone shelves,
        // lanternstone walls in extraRockTypes, the darkness mechanic, and both
        // the pyrinth and kyber scatters. It loses its crystal field and its
        // fungal pasture, not its floor.
        public static bool lanternstoneFormationsEnabled = true;
        public static float lanternstoneDensityMultiplier = 1f;
        public static bool deepFloraEnabled = true;
        // MINERAL_BIOME_LEAKS_1: on = a deep-scanner strike off the Deeps never returns lanternstone (steel instead).
        public static bool lanternstoneDeepGateEnabled = true;
        // LANTERNDEEPS_WORKING_DEAD_BUILD_1
        public static bool wellProvisionedDeadEnabled = true;   // new Deeps: remains, gear, dead chassis
        public static bool shardMindsEnabled = true;            // new Deeps: Shard-minds grow
        public static bool workingDeadAnimateEnabled = true;    // live: chassis near a Shard-mind stand and work
        public static bool shardMindDroidPullEnabled = true;    // live: colony droids near one stop and listen
        // LANTERNDEEPS_ORUN_GHAL_BUILD_1
        public static bool orunGhalEnabled = true;              // new Deeps: one Orun-Ghal; live: it walks its rounds
        public static bool orunGhalStudyEnabled = true;         // live: colonists study and befriend it
        // LANTERNDEEPS_HYDROCARBON_WAVE1_BUILD_1
        public static bool hydrocarbonIgnitionEnabled = true;   // live: drifter/galuush detonate when killed hot
        public static bool galuushEnabled = true;               // new Deeps: a galuush may hang in the biggest chamber
        // LANTERNDEEPS_CREEP_CLEAVERS_BUILD_1
        public static bool creepEnabled = true;                 // new Deeps: a Creep may be seeded; live: it grows
        public static float creepGrowthMultiplier = 1f;         // cells precipitated per hour while stalking
        public static bool cleavingEnabled = true;              // live: a Cleaver struck hard splits
        public static int cleaverMapCap = 24;                   // no cleave past this many Cleavers on one map
        // LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1
        public static bool auroraEnabled = true;                // live: the aurora storm overhead reaches the Deep
        public static float auroraMtbDays = 8f;                 // mean days between storms when none is mirrored
        public static bool collapseWarningsEnabled = true;      // live: dust, sand and the grumble before a roof falls
        public static int collapseWarningTicks = 900;           // the warning window
        public static bool galuushRoofFallEnabled = true;       // live: a galuush killed hot brings its roof down
        // LANTERNDEEPS_HYDROCARBON_WAVE2_BUILD_1
        public static bool slickTrailEnabled = true;            // live: slicks leave burning-fuse fuel trails
        public static bool blinkerFlashEnabled = true;          // live: a hurt blinker flashes and dazzles
        public static bool knockerAlarmEnabled = true;          // live: knockers drum at a failing roof
        public static float knockerWarningFactor = 2f;          // a tame knocker lengthens collapse warnings
        // LANTERNDEEPS_HYDROCARBON_WAVE3_BUILD_1
        public static bool hushHidingEnabled = true;            // new Deeps: 1-2 hush; live: unseen on unlit ground, lunge at 2
        public static bool sipperDrinkingEnabled = true;        // live: sippers seek the brightest light and drink its radius
        public static float sipperCellsPerSipper = 0.1f;        // glow radius lost per sipper sitting on a light
        public static bool tapperEnabled = true;                // live: wild tappers drain batteries; tame ones store aurora charge
        public static bool poolerSmotherEnabled = true;         // live: poolers smother fires, heaters and warm bodies

        // DEEP_ENTRANCE_BIOMES_SETTING_1 — owner, 2026-09-18: "The mod itself
        // will be (3) but for the Utinni scenario it's definitely (1)". The
        // biomes an entrance may scatter onto are a Mod Setting (any biome
        // selectable); the DEFAULT is exactly the three the Utinni campaign
        // ruled ≤ -40°C (the_lantern_deeps.md "Injection rule"), which is what
        // both GenSteps hardcoded before this setting existed. WORLDGEN-AFFECTING:
        // read once per map generation, so a change applies to new maps only.
        // A name that resolves to no loaded BiomeDef is simply never matched.
        //
        // FIX 2026-09-25 (TERMINALBIOMES_RM_MOD_BUILD_1, correcting
        // LANTERNDEEPS_RM_MOD_BUILD_1 the same day): the RUT_ names were
        // dropped here on the belief that "both host biomes completed their
        // RM_ tier moves" made them stale. False — per
        // BIOME_PAINT_ONCE_AT_THE_END_1 the planet is painted ONCE, at the
        // end; RUT_NightsideIce/RUT_PropaneLake are FROZEN, not deleted, and
        // still carry every tile on the live Ash'karr world today (their
        // RM_ twins sit at 0 tiles, mid-migration — see
        // infrastructure/state/facts/biome_paint_list.md). Dropping the
        // RUT_ names is what silently stops every entrance from scattering
        // on the actual campaign world; both names must ride together until
        // the terminal repaint retires the RUT_ twins.
        public static readonly string[] UtinniDefaultEntranceBiomes =
        {
            "BiomeGRimond",
            "RUT_NightsideIce",
            "RM_NightsideIce",
            "RUT_PropaneLake",
            "RM_TheChill",
        };

        public static List<string> entranceBiomes = new List<string>(UtinniDefaultEntranceBiomes);

        // Lazy lookup set. Invalidated explicitly by every UI edit and by
        // ResetEntranceBiomes(); ALSO rebuilt whenever the backing list's
        // reference or count differs from what the set was built from, because
        // the bridge's jawa/mod_settings_field writes the static field directly
        // and never calls a setter (BRIDGE_STATIC_SETTINGS_FIELDS_1).
        private static HashSet<string> entranceBiomeSet;
        private static List<string> entranceBiomeSetSource;
        private static int entranceBiomeSetCount = -1;

        public static bool IsEntranceBiome(BiomeDef biome)
        {
            if (biome == null)
            {
                return false;
            }
            List<string> list = entranceBiomes;
            if (list == null)
            {
                return false;
            }
            if (entranceBiomeSet == null
                || !ReferenceEquals(entranceBiomeSetSource, list)
                || entranceBiomeSetCount != list.Count)
            {
                entranceBiomeSet = new HashSet<string>(list);
                entranceBiomeSetSource = list;
                entranceBiomeSetCount = list.Count;
            }
            return entranceBiomeSet.Contains(biome.defName);
        }

        public static void InvalidateEntranceBiomeSet()
        {
            entranceBiomeSet = null;
            entranceBiomeSetSource = null;
            entranceBiomeSetCount = -1;
        }

        public static void ResetEntranceBiomes()
        {
            entranceBiomes = new List<string>(UtinniDefaultEntranceBiomes);
            InvalidateEntranceBiomeSet();
        }

        public static bool EntranceBiomesAreUtinniDefault()
        {
            List<string> list = entranceBiomes;
            return list != null
                && list.Count == UtinniDefaultEntranceBiomes.Length
                && UtinniDefaultEntranceBiomes.All(list.Contains);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref entranceBiomes, "entranceBiomes", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // ReadModSettings loads through Scribe_Deep.Look, which registers
                // this object for the PostLoadInit pass, so this branch does run.
                // Null = a settings file written before this key existed; empty =
                // nothing useful to keep. Either way: the Utinni defaults.
                if (entranceBiomes == null || entranceBiomes.Count == 0)
                {
                    ResetEntranceBiomes();
                }
                else
                {
                    InvalidateEntranceBiomeSet();
                }
            }
            Scribe_Values.Look(ref lanternDeepsEnabled, "lanternDeepsEnabled", true);
            Scribe_Values.Look(ref emergenceEnabled, "emergenceEnabled", true);
            Scribe_Values.Look(ref emergenceChanceMultiplier, "emergenceChanceMultiplier", 1f);
            Scribe_Values.Look(ref mineshaftEnabled, "mineshaftEnabled", true);
            Scribe_Values.Look(ref mineshaftChanceMultiplier, "mineshaftChanceMultiplier", 1f);
            Scribe_Values.Look(ref darknessMechanicEnabled, "darknessMechanicEnabled", true);
            Scribe_Values.Look(ref darknessThresholdMultiplier, "darknessThresholdMultiplier", 1f);
            Scribe_Values.Look(ref safeLanternEnabled, "safeLanternEnabled", true);
            Scribe_Values.Look(ref lanternstoneFormationsEnabled, "lanternstoneFormationsEnabled", true);
            Scribe_Values.Look(ref lanternstoneDensityMultiplier, "lanternstoneDensityMultiplier", 1f);
            Scribe_Values.Look(ref deepFloraEnabled, "deepFloraEnabled", true);
            Scribe_Values.Look(ref lanternstoneDeepGateEnabled, "lanternstoneDeepGateEnabled", true);
            Scribe_Values.Look(ref wellProvisionedDeadEnabled, "wellProvisionedDeadEnabled", true);
            Scribe_Values.Look(ref shardMindsEnabled, "shardMindsEnabled", true);
            Scribe_Values.Look(ref workingDeadAnimateEnabled, "workingDeadAnimateEnabled", true);
            Scribe_Values.Look(ref shardMindDroidPullEnabled, "shardMindDroidPullEnabled", true);
            Scribe_Values.Look(ref orunGhalEnabled, "orunGhalEnabled", true);
            Scribe_Values.Look(ref orunGhalStudyEnabled, "orunGhalStudyEnabled", true);
            Scribe_Values.Look(ref hydrocarbonIgnitionEnabled, "hydrocarbonIgnitionEnabled", true);
            Scribe_Values.Look(ref galuushEnabled, "galuushEnabled", true);
            Scribe_Values.Look(ref creepEnabled, "creepEnabled", true);
            Scribe_Values.Look(ref creepGrowthMultiplier, "creepGrowthMultiplier", 1f);
            Scribe_Values.Look(ref cleavingEnabled, "cleavingEnabled", true);
            Scribe_Values.Look(ref cleaverMapCap, "cleaverMapCap", 24);
            Scribe_Values.Look(ref auroraEnabled, "auroraEnabled", true);
            Scribe_Values.Look(ref auroraMtbDays, "auroraMtbDays", 8f);
            Scribe_Values.Look(ref collapseWarningsEnabled, "collapseWarningsEnabled", true);
            Scribe_Values.Look(ref collapseWarningTicks, "collapseWarningTicks", 900);
            Scribe_Values.Look(ref galuushRoofFallEnabled, "galuushRoofFallEnabled", true);
            Scribe_Values.Look(ref slickTrailEnabled, "slickTrailEnabled", true);
            Scribe_Values.Look(ref blinkerFlashEnabled, "blinkerFlashEnabled", true);
            Scribe_Values.Look(ref knockerAlarmEnabled, "knockerAlarmEnabled", true);
            Scribe_Values.Look(ref knockerWarningFactor, "knockerWarningFactor", 2f);
            Scribe_Values.Look(ref hushHidingEnabled, "hushHidingEnabled", true);
            Scribe_Values.Look(ref sipperDrinkingEnabled, "sipperDrinkingEnabled", true);
            Scribe_Values.Look(ref sipperCellsPerSipper, "sipperCellsPerSipper", 0.1f);
            Scribe_Values.Look(ref tapperEnabled, "tapperEnabled", true);
            Scribe_Values.Look(ref poolerSmotherEnabled, "poolerSmotherEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // the screen outgrew one page: the whole of it scrolls, the biome checklist keeps its own box
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(inRect.height, outerHeight));
            Widgets.BeginScrollView(inRect, ref outerScroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.CheckboxLabeled("Lantern Deeps enabled", ref lanternDeepsEnabled,
                "Off: neither entrance (cave-mouth emergence or ruined mineshaft) can ever appear on "
              + "a new map, regardless of the toggles below. A Deep already entered is untouched.");
            list.GapLine();

            list.Label("Lantern Deep emergence (affects new maps only)");
            list.CheckboxLabeled("Natural cave-mouth portal can emerge", ref emergenceEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a lanternstone-geode mouth. "
              + "A map that already exists is never retroactively changed.");
            if (emergenceEnabled)
            {
                list.Label("Emergence chance: " + emergenceChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 8% of qualifying maps)");
                emergenceChanceMultiplier = list.Slider(emergenceChanceMultiplier, 0f, 3f);
            }

            list.Gap();
            list.Label("Ruined mineshaft entrance (affects new maps only)");
            list.CheckboxLabeled("Ruined-mineshaft portal can appear", ref mineshaftEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a ruined-mineshaft mouth. "
              + "A map that already exists is never retroactively changed.");
            if (mineshaftEnabled)
            {
                list.Label("Mineshaft chance: " + mineshaftChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 4% of qualifying maps)");
                mineshaftChanceMultiplier = list.Slider(mineshaftChanceMultiplier, 0f, 3f);
            }

            list.Gap();
            list.Label("Darkness (inside an already-generated Deep)");
            list.CheckboxLabeled("Bright light draws cave predators", ref darknessMechanicEnabled,
                "Off: colonists inside a Lantern Deep can light the place up freely with no consequence. "
              + "On (default): sustained bright light near colonists eventually draws a resident predator "
              + "into a manhunter attack. Working in the dark, or moving on before light lingers, avoids it.");
            if (darknessMechanicEnabled)
            {
                list.Label("Trigger threshold: " + darknessThresholdMultiplier.ToString("0.00")
                    + "x the base sensitivity (higher = more light tolerated before something notices)");
                darknessThresholdMultiplier = list.Slider(darknessThresholdMultiplier, 0.25f, 4f);
                list.CheckboxLabeled("Lantern light is safe", ref safeLanternEnabled,
                    "On (default): the glow of a Lantern, where no other light reaches, is not counted toward drawing predators. "
                  + "Off: a Lantern lights the place like any lamp (it is still buildable and still shines).");
            }

            list.Gap();
            list.Label("Inside a Lantern Deep (affects newly generated Deeps only)");
            list.CheckboxLabeled("Lanternstone formations grow in the Deeps", ref lanternstoneFormationsEnabled,
                "Off: a newly entered Deep has bare gravel and lanternstone shelves but no standing crystal "
              + "formations to mine, light the place, or go off when shot. The cavern is still complete and "
              + "still has its lanternstone walls.");
            if (lanternstoneFormationsEnabled)
            {
                list.Label("Lanternstone density: " + lanternstoneDensityMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 15-30 clusters per 10,000 cells)");
                lanternstoneDensityMultiplier = list.Slider(lanternstoneDensityMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Cave flora grows in the Deeps", ref deepFloraEnabled,
                "Off: a newly entered Deep has no mycelium carpet, no mushroom trees and no glow-fungi — "
              + "no forageable food and no cloth or wood from below. Bare rock and crystal.");

            list.CheckboxLabeled("Lanternstone deep deposits only in the Deeps", ref lanternstoneDeepGateEnabled,
                "On: a ground-penetrating scanner on any other map finds steel where it would have found lanternstone. "
              + "Off: vanilla's global deep-resource table, lanternstone anywhere. Applies at scan time.");

            list.CheckboxLabeled("The well-provisioned dead lie in the Deeps", ref wellProvisionedDeadEnabled,
                "On: a newly generated Deep holds old remains in good gear along its galleries and at the shaft bottom, "
              + "with salvage and dead droid chassis beside them. Off: none. Affects newly generated Deeps only.");
            list.CheckboxLabeled("Shard-minds grow in the Deeps", ref shardMindsEnabled,
                "On: a newly generated Deep has one or two aware crystals with dead chassis around them. "
              + "Off: none. Affects newly generated Deeps only.");
            list.CheckboxLabeled("Dead chassis near a Shard-mind stand and work", ref workingDeadAnimateEnabled,
                "On: a dead chassis near a Shard-mind stands up, works at the rock (it never digs) and turns toward light. "
              + "Off: every chassis lies slumped. Safe mid-game.");
            list.CheckboxLabeled("Colony droids near a Shard-mind stop to listen", ref shardMindDroidPullEnabled,
                "On: now and then a droid of yours near a Shard-mind stops what it is doing and stands facing it for a while "
              + "(drafting breaks it). Off: droids ignore it. Safe mid-game.");
            list.CheckboxLabeled("Orun-Ghal lives in the Deeps", ref orunGhalEnabled,
                "On: a newly generated Deep holds Orun-Ghal, a huge dead mining suit worn and walked by the Shard-minds, its miner's "
              + "skeleton still inside. It never mines and never attacks; it walks its rounds between the Shard-minds and any lit "
              + "Lantern. Off: none in new Deeps, and one already there only wanders like an animal.");
            list.CheckboxLabeled("Orun-Ghal can be studied and befriended", ref orunGhalStudyEnabled,
                "On: a colonist doing research work visits it once a day and studies it (it stands still for the visit). Study "
              + "reveals what the crystals are and want; each visit on a new day raises its standing, and as it comes to know "
              + "you it walks over to your people. Off: no study work. Safe mid-game.");
            list.CheckboxLabeled("Methane bodies ignite when killed hot", ref hydrocarbonIgnitionEnabled,
                "On: a drifter or a galuush killed by fire, a burn, a bullet or a blast detonates (the galuush fills its chamber); "
              + "killed by a blade or a blow it collapses harmlessly. Off: they never detonate. Safe mid-game.");
            list.CheckboxLabeled("A galuush may hang in a Deep", ref galuushEnabled,
                "On: about half of newly generated Deeps have one galuush, a living sun hung in the biggest chamber. "
              + "Off: none. Affects newly generated Deeps only.");
            list.CheckboxLabeled("The Creep grows in the Deeps", ref creepEnabled,
                "On: about half of newly generated Deeps hold a Creep, a crystal crust that drifts across the cavern over days "
              + "and grows toward anything asleep or down within reach, engulfing it (a letter names it; break the crust to free it). "
              + "Off: no new Creep, and an existing crust stops growing.");
            if (creepEnabled)
            {
                list.Label("Creep growth: " + creepGrowthMultiplier.ToString("0.00") + "x (shipped: one cell an hour toward a sleeper)");
                creepGrowthMultiplier = list.Slider(creepGrowthMultiplier, 0.25f, 3f);
            }
            list.CheckboxLabeled("Cleavers split when struck", ref cleavingEnabled,
                "On: a Cleaver hit hard may fracture, and the shard walks away as a new Cleaver. Off: they only take damage. Safe mid-game.");
            if (cleavingEnabled)
            {
                list.Label("Most Cleavers on one map before splitting stops: " + cleaverMapCap);
                cleaverMapCap = (int)list.Slider(cleaverMapCap, 4f, 60f);
            }
            list.CheckboxLabeled("The aurora storm reaches the Deep", ref auroraEnabled,
                "On: now and then (and whenever a reconnection storm rages on the surface) the Deep has its feast day: lanternstone "
              + "glows wider, the Chorus rises, Cleavers quicken. Off: never. Safe mid-game.");
            if (auroraEnabled)
            {
                list.Label("Mean days between storms: " + auroraMtbDays.ToString("0.0"));
                auroraMtbDays = list.Slider(auroraMtbDays, 2f, 30f);
            }
            list.CheckboxLabeled("A failing roof warns before it falls", ref collapseWarningsEnabled,
                "On: in a Deep, an unsupported roof grumbles, trails dust and piles sand for a while before it falls; prop it in time "
              + "and it holds. Off: vanilla, it falls at once. Safe mid-game.");
            if (collapseWarningsEnabled)
            {
                list.Label("Warning time: " + (collapseWarningTicks / 60f).ToString("0") + " seconds at normal speed");
                collapseWarningTicks = (int)list.Slider(collapseWarningTicks, 300f, 3600f);
            }
            list.CheckboxLabeled("A galuush killed hot brings its roof down", ref galuushRoofFallEnabled,
                "On: the galuush's blast brings down the roof over its chamber (after the warning, propped or not). Off: blast and fire only.");
            list.CheckboxLabeled("Slicks leave fuel trails", ref slickTrailEnabled,
                "On: every cell a slick crosses is left wet with fuel that does not evaporate in the cold; one spark runs the corridor "
              + "like a fuse. Off: no trail. Safe mid-game.");
            list.CheckboxLabeled("A hurt blinker flashes", ref blinkerFlashEnabled,
                "On: a blinker that is hurt flashes: everything that can see it is dazzled for a few seconds and the chamber is lit "
              + "for a breath, which draws what light draws. Off: no flash. Safe mid-game.");
            list.CheckboxLabeled("Knockers drum at a failing roof", ref knockerAlarmEnabled,
                "On: a knocker that hears a roof failing (during the collapse warning) drums and runs; a tame one names the danger "
              + "cells and lengthens every warning on its map. Off: they ignore it. Safe mid-game.");
            if (knockerAlarmEnabled)
            {
                list.Label("Warning length with a tame knocker: " + knockerWarningFactor.ToString("0.0") + "x");
                knockerWarningFactor = list.Slider(knockerWarningFactor, 1f, 4f);
            }
            list.CheckboxLabeled("The hush is unseen in the dark", ref hushHidingEnabled,
                "On: one or two hush lie on the unlit floor of each new Deep; on an unlit cell a hush cannot be seen or targeted, and "
              + "anything that walks within two cells is struck. Light it and it is a plain black slab. Off: no new hush are placed and "
              + "any that exist stay visible. Safe mid-game.");
            list.CheckboxLabeled("Sippers drink light", ref sipperDrinkingEnabled,
                "On: sippers hop toward the brightest light near them and sit on it; every sipper on a light shrinks its glow "
              + "(never below a quarter), and the light comes back as they leave. Off: they wander. Safe mid-game.");
            if (sipperDrinkingEnabled)
            {
                list.Label("Glow lost per sipper: " + sipperCellsPerSipper.ToString("0.00") + " cells");
                sipperCellsPerSipper = list.Slider(sipperCellsPerSipper, 0.02f, 0.5f);
            }
            list.CheckboxLabeled("Tappers eat electricity", ref tapperEnabled,
                "On: wild tappers walk to your charged batteries and drain them while they sit beside them; a tame tapper never drains, "
              + "stores charge while the aurora storms and pours it into any battery it stands beside. Off: neither. Safe mid-game.");
            list.CheckboxLabeled("Poolers smother warmth", ref poolerSmotherEnabled,
                "On: a wild pooler seeks the warmest thing near it: it puts out fires, drowns a fuelled heater flat, holds a powered "
              + "heater off while it sits on it, and chills a warm body fast; a tame one only hunts fires. Fire never hurts it. Off: "
              + "it wanders and any heater it held comes back on. Safe mid-game.");

            // DEEP_ENTRANCE_BIOMES_SETTING_1 — worldgen-affecting biome checklist.
            list.Gap();
            list.Label("World generation: entrance biomes (affects new maps only)");
            Text.Font = GameFont.Tiny;
            list.Label("Both entrance types can only appear on a new map whose biome is ticked below. "
                + "Shipped default: the three Utinni deep-cold biomes. A ticked biome that is not loaded "
                + "is ignored. Ticking none is restored to the defaults on next load; use the toggles "
                + "above to turn entrances off.");
            Text.Font = GameFont.Small;

            List<string> selected = entranceBiomes ?? (entranceBiomes = new List<string>());
            List<BiomeDef> biomes = AllBiomesSorted;
            int loadedSelected = 0;
            for (int i = 0; i < biomes.Count; i++)
            {
                if (selected.Contains(biomes[i].defName))
                {
                    loadedSelected++;
                }
            }
            list.Label(loadedSelected + " of " + biomes.Count + " loaded biomes selected"
                + (EntranceBiomesAreUtinniDefault() ? " (Utinni defaults)" : ""));

            Rect buttonRow = list.GetRect(30f);
            float buttonWidth = (buttonRow.width - 2f * 8f) / 3f;
            if (Widgets.ButtonText(new Rect(buttonRow.x, buttonRow.y, buttonWidth, buttonRow.height),
                "Reset to Utinni defaults"))
            {
                ResetEntranceBiomes();
            }
            if (Widgets.ButtonText(new Rect(buttonRow.x + buttonWidth + 8f, buttonRow.y, buttonWidth, buttonRow.height),
                "Select all"))
            {
                entranceBiomes = biomes.Select(b => b.defName).ToList();
                InvalidateEntranceBiomeSet();
            }
            if (Widgets.ButtonText(new Rect(buttonRow.x + 2f * (buttonWidth + 8f), buttonRow.y, buttonWidth, buttonRow.height),
                "Select none"))
            {
                entranceBiomes = new List<string>();
                InvalidateEntranceBiomeSet();
            }
            list.Gap(4f);

            Rect outRect = list.GetRect(260f);
            outerHeight = list.CurHeight + 12f;
            list.End();
            DrawBiomeChecklist(outRect);
            Widgets.EndScrollView();
        }

        private static Vector2 outerScroll = Vector2.zero;
        private static float outerHeight = 1400f;

        private static Vector2 biomeScrollPosition = Vector2.zero;
        private static List<BiomeDef> allBiomesSortedCached;

        // DefDatabase is fixed after load, so one sorted snapshot is enough.
        private static List<BiomeDef> AllBiomesSorted =>
            allBiomesSortedCached ?? (allBiomesSortedCached = DefDatabase<BiomeDef>.AllDefsListForReading
                .OrderBy(b => b.LabelCap.ToString())
                .ThenBy(b => b.defName)
                .ToList());

        private const float BiomeRowHeight = 24f;

        private static void DrawBiomeChecklist(Rect outRect)
        {
            List<BiomeDef> biomes = AllBiomesSorted;
            List<string> selected = entranceBiomes;
            Rect viewRect = new Rect(0f, 0f, outRect.width - 16f, biomes.Count * BiomeRowHeight);
            Widgets.BeginScrollView(outRect, ref biomeScrollPosition, viewRect);
            float y = 0f;
            for (int i = 0; i < biomes.Count; i++)
            {
                BiomeDef biome = biomes[i];
                Rect row = new Rect(0f, y, viewRect.width, BiomeRowHeight);
                bool was = selected.Contains(biome.defName);
                bool now = was;
                Widgets.CheckboxLabeled(row, biome.LabelCap + " (" + biome.defName + ")", ref now);
                if (now != was)
                {
                    if (now)
                    {
                        selected.Add(biome.defName);
                    }
                    else
                    {
                        selected.RemoveAll(n => n == biome.defName);
                    }
                    InvalidateEntranceBiomeSet();
                }
                y += BiomeRowHeight;
            }
            Widgets.EndScrollView();
        }
    }

    public class LanternDeepsMod : Mod
    {
        public static LanternDeepsSettings settings;

        public LanternDeepsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LanternDeepsSettings>();
        }

        public override string SettingsCategory() => "Lantern Deeps";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
