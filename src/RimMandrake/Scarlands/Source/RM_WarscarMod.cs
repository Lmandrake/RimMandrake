using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // SCARLANDS_STANDALONE_MOD_1 — Mod Settings for Warscar.
    //
    // This biome ships no bespoke mechanic of its own: its two duplicated
    // flora defs (RM_Glower/RM_ScorchedStars) are plain harvestable plants
    // with no comp yet (the frozen twin's own radiation-dose harvest loop is
    // still owed to SCARLANDS_MECHANICS_2), and the frozen twin's own
    // scaria-mark/pre-sprung-dressing mechanics deliberately did NOT move
    // into this mod (this item's own `## spec`: "don't invent extra scope").
    // So this screen ships only the standard worldgen-rarity slider every
    // biome-worker mod ships, plus the honestly-disclosed reserved
    // cross-biome section (MOD_OPTIONS_RETROFIT_1 doctrine), same shape as
    // RM_Miasma/RM_RustCathedral's own screens.
    //
    // STATIC FIELD, read from worldgen with no Mod instance handy.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WarscarSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        public static float biomeRarityFactor = 1f;

        // MOD_OPTIONS_RETROFIT_1: reserved fields for letting this biome's
        // (currently nonexistent) mechanics run on other biomes too.
        // Persisted and exposed here honestly as NOT YET WIRED to any
        // mechanic — there is no mechanic in this mod for it to gate yet.
        // WARSCAR_TURRETS_TRACK_1 toggles.
        public static bool turretTrackingEnabled = true;   // broken turrets' barrels follow movers
        public static bool turretRefitEnabled = true;      // wreck -> RM_OldLineTurret gizmo
        public static float oldLineDamageFactor = 1f;      // applied at game start
        public static float oldLineCooldownFactor = 1f;    // applied at game start

        // WARSCAR_TOTCHAK_WAKES_1 toggles.
        public static bool totchakEnabled = true;           // totchak spawns dormant in walls and wakes
        public static bool totchakEatsPlayerWalls = true;   // ruled default on
        public static float totchakWakeRadius = 12f;        // demolition wake radius (cells)
        public static float totchakBiteScale = 1f;          // wall-eating damage scale
        public static float totchakGrazeDays = 8f;          // awake days before it lies down again

        // WARSCAR_OLD_TONGUE_1 toggles.
        public static bool oldTongueEnabled = true;          // inscribed panels generate on new maps
        public static float oldTonguePanelsPerMap = 3f;      // panel placement attempts per map
        public static float oldTongueRevealChance = 0.8f;    // chance each attempt actually places a panel
        public static int oldTongueSkillGate = 8;            // Intellectual needed to transcribe (0 = none)

        // WARSCAR_HOSPICE_DESERTERS_1 toggles.
        public static bool hospiceEnabled = true;            // rings, cradle jobs and walk-ins
        public static int hospiceIntactPerMap = 2;           // max intact chassis rolled per map (0-3)
        public static float hospiceStageDays = 1.5f;         // days per cradle stage (five stages)
        public static float hospiceFailureChance = 0.08f;    // per risky stage
        public static bool hospiceLashOut = true;            // limbs stage may hit an adjacent pawn once
        public static bool hospiceWalkInEnabled = true;      // deserter walk-in incident
        public static float hospiceWalkInFrequency = 1f;     // chance the incident proceeds when it rolls

        // WARSCAR_RAINBOW_POOLS_1 toggles.
        public static bool poolsEnabled = true;              // pools generate on new maps; taps work
        public static float poolsPerMap = 3f;                // up to this many pools (1-3), new maps
        public static float poolCycleHours = 24f;            // one full four-phase cycle
        public static float bloomDanger = 1f;                // scales the burn and toxic buildup of drawing the bloom
        public static bool catalystEnabled = true;           // glower crust holds a phase

        // WARSCAR_CHOTRIX_BUILD_1 toggles.
        public static bool chotrixEnabled = true;            // chotrix spawns on new maps and hunts
        public static float chotrixPerMap = 2f;              // up to this many per map (0-2), new maps
        public static float chotrixRevealSeconds = 4f;       // seconds visible after it strikes
        public static bool lacquerCloakEnabled = true;       // lacquered cloaks grant still-and-unseen invisibility
        public static float lacquerSeenRadius = 15f;         // a hostile with sight within this many cells "sees" the wearer

        // WARSCAR_FREE_TIER_BODY_1 toggles. Species rows apply at startup (restart needed).
        public static bool enableChatrak = true;
        public static bool enableTetchik = true;
        public static bool enablePallbearer = true;
        public static bool enableScarRoach = true;
        public static bool enableWreckLichenSeeder = true;
        public static bool enableInterimDonors = true;

        // WARSCAR_SETTLING_WEATHER_1 toggles.
        public static bool settlingEnabled = true;           // calm starts the Settling at all
        public static float settlingCalmThreshold = 0.35f;   // wind speed below this is calm
        public static float settlingCalmHours = 4f;          // hours of calm before it starts
        public static float settlingEndWind = 0.8f;          // wind speed above this ends it
        public static float settlingEndHours = 1f;           // hours of strong wind before it ends
        public static float settlingToxicStrength = 1f;      // scales the airborne toxic buildup (0 = harmless)
        public static bool liftFrontEnabled = true;          // the visible front with brief toxic exposure
        public static bool warDustEnabled = true;            // film can be swept up for war dust
        public static bool warDustBlightCureEnabled = true;  // growers dust blighted plants with war dust (insecticide)
        public static float ordnancePerMap = 3f;             // buried shells per new map (0-8)

        // WARSCAR_GEIGER_CHOIR_1 toggles.
        public static bool choirEnabled = true;              // the whole choir (ticks, wind, hum, boil, jar sound)
        public static float choirVolume = 1f;                // one global volume
        public static float choirTickVolumeCeiling = 1f;     // cap on how loud the tick gets
        public static float choirTickDensity = 1f;           // tick tempo scale
        public static bool choirWindEnabled = true;          // wind-on-metal layer
        public static bool choirReducedRepetition = false;   // fewer, jittered clicks
        public static bool choirJarWarnings = true;          // caravan message before a polluted tile

        // WARSCAR_MARK_TRADE_BUILD_1 -- the mark made a trade
        public static bool markEnabled = true;               // hourly accrual on a Warscar map
        public static float markAccrualPerDay = 0.3f;        // gross per day on the map (fade is -0.1/day)
        public static bool markFloorEnabled = true;          // past 0.5 it never fades below 0.25
        public static bool markTradeBonusesEnabled = true;   // hacking / mech butchery / smelting offsets (restart)

        // WARSCAR_CHATRAK_SNAP_BUILD_1 -- the chatrak's snap
        public static bool snapEnabled = true;               // scaria chatrak are armed and eventually snap
        public static float snapArmingHours = 24f;           // hours between arming sweeps on a Warscar map
        public static float snapStageSpeed = 1f;             // scales the incubation climb (restart)

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref turretTrackingEnabled, "turretTrackingEnabled", true);
            Scribe_Values.Look(ref turretRefitEnabled, "turretRefitEnabled", true);
            Scribe_Values.Look(ref oldLineDamageFactor, "oldLineDamageFactor", 1f);
            Scribe_Values.Look(ref oldLineCooldownFactor, "oldLineCooldownFactor", 1f);
            Scribe_Values.Look(ref totchakEnabled, "totchakEnabled", true);
            Scribe_Values.Look(ref totchakEatsPlayerWalls, "totchakEatsPlayerWalls", true);
            Scribe_Values.Look(ref totchakWakeRadius, "totchakWakeRadius", 12f);
            Scribe_Values.Look(ref totchakBiteScale, "totchakBiteScale", 1f);
            Scribe_Values.Look(ref totchakGrazeDays, "totchakGrazeDays", 8f);
            Scribe_Values.Look(ref oldTongueEnabled, "oldTongueEnabled", true);
            Scribe_Values.Look(ref oldTonguePanelsPerMap, "oldTonguePanelsPerMap", 3f);
            Scribe_Values.Look(ref oldTongueRevealChance, "oldTongueRevealChance", 0.8f);
            Scribe_Values.Look(ref oldTongueSkillGate, "oldTongueSkillGate", 8);
            Scribe_Values.Look(ref hospiceEnabled, "hospiceEnabled", true);
            Scribe_Values.Look(ref hospiceIntactPerMap, "hospiceIntactPerMap", 2);
            Scribe_Values.Look(ref hospiceStageDays, "hospiceStageDays", 1.5f);
            Scribe_Values.Look(ref hospiceFailureChance, "hospiceFailureChance", 0.08f);
            Scribe_Values.Look(ref hospiceLashOut, "hospiceLashOut", true);
            Scribe_Values.Look(ref hospiceWalkInEnabled, "hospiceWalkInEnabled", true);
            Scribe_Values.Look(ref hospiceWalkInFrequency, "hospiceWalkInFrequency", 1f);
            Scribe_Values.Look(ref poolsEnabled, "poolsEnabled", true);
            Scribe_Values.Look(ref poolsPerMap, "poolsPerMap", 3f);
            Scribe_Values.Look(ref poolCycleHours, "poolCycleHours", 24f);
            Scribe_Values.Look(ref bloomDanger, "bloomDanger", 1f);
            Scribe_Values.Look(ref catalystEnabled, "catalystEnabled", true);
            Scribe_Values.Look(ref chotrixEnabled, "chotrixEnabled", true);
            Scribe_Values.Look(ref chotrixPerMap, "chotrixPerMap", 2f);
            Scribe_Values.Look(ref chotrixRevealSeconds, "chotrixRevealSeconds", 4f);
            Scribe_Values.Look(ref lacquerCloakEnabled, "lacquerCloakEnabled", true);
            Scribe_Values.Look(ref lacquerSeenRadius, "lacquerSeenRadius", 15f);
            Scribe_Values.Look(ref enableChatrak, "enableChatrak", true);
            Scribe_Values.Look(ref enableTetchik, "enableTetchik", true);
            Scribe_Values.Look(ref enablePallbearer, "enablePallbearer", true);
            Scribe_Values.Look(ref enableScarRoach, "enableScarRoach", true);
            Scribe_Values.Look(ref enableWreckLichenSeeder, "enableWreckLichenSeeder", true);
            Scribe_Values.Look(ref enableInterimDonors, "enableInterimDonors", true);
            Scribe_Values.Look(ref settlingEnabled, "settlingEnabled", true);
            Scribe_Values.Look(ref settlingCalmThreshold, "settlingCalmThreshold", 0.35f);
            Scribe_Values.Look(ref settlingCalmHours, "settlingCalmHours", 4f);
            Scribe_Values.Look(ref settlingEndWind, "settlingEndWind", 0.8f);
            Scribe_Values.Look(ref settlingEndHours, "settlingEndHours", 1f);
            Scribe_Values.Look(ref settlingToxicStrength, "settlingToxicStrength", 1f);
            Scribe_Values.Look(ref liftFrontEnabled, "liftFrontEnabled", true);
            Scribe_Values.Look(ref warDustEnabled, "warDustEnabled", true);
            Scribe_Values.Look(ref warDustBlightCureEnabled, "warDustBlightCureEnabled", true);
            Scribe_Values.Look(ref ordnancePerMap, "ordnancePerMap", 3f);
            Scribe_Values.Look(ref choirEnabled, "choirEnabled", true);
            Scribe_Values.Look(ref choirVolume, "choirVolume", 1f);
            Scribe_Values.Look(ref choirTickVolumeCeiling, "choirTickVolumeCeiling", 1f);
            Scribe_Values.Look(ref choirTickDensity, "choirTickDensity", 1f);
            Scribe_Values.Look(ref choirWindEnabled, "choirWindEnabled", true);
            Scribe_Values.Look(ref choirReducedRepetition, "choirReducedRepetition", false);
            Scribe_Values.Look(ref choirJarWarnings, "choirJarWarnings", true);
            Scribe_Values.Look(ref markEnabled, "markEnabled", true);
            Scribe_Values.Look(ref markAccrualPerDay, "markAccrualPerDay", 0.3f);
            Scribe_Values.Look(ref markFloorEnabled, "markFloorEnabled", true);
            Scribe_Values.Look(ref markTradeBonusesEnabled, "markTradeBonusesEnabled", true);
            Scribe_Values.Look(ref snapEnabled, "snapEnabled", true);
            Scribe_Values.Look(ref snapArmingHours, "snapArmingHours", 24f);
            Scribe_Values.Look(ref snapStageSpeed, "snapStageSpeed", 1f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        private static Vector2 scroll;
        private static float viewHeight = 2400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, viewHeight);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 Warscar never generates on a new planet. Affects planets "
                       + "generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.CheckboxLabeled("Broken turrets track movement", ref turretTrackingEnabled,
                "The barrel of a broken ancient turret turns to follow the nearest moving pawn. It never fires.");
            list.CheckboxLabeled("Allow refitting broken turrets", ref turretRefitEnabled,
                "Adds a Refit button to broken turrets that converts them into an old-line turret.");
            list.Label("Old-line turret damage: x" + oldLineDamageFactor.ToString("0.00") + " (applies after restart)");
            oldLineDamageFactor = list.Slider(oldLineDamageFactor, 0.25f, 3f);
            list.Label("Old-line turret cooldown: x" + oldLineCooldownFactor.ToString("0.00") + " (applies after restart)");
            oldLineCooldownFactor = list.Slider(oldLineCooldownFactor, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Totchak (wall colossus)", ref totchakEnabled,
                "A totchak sleeps in a run of ruin wall, wakes to demolition, eats walls, and lies down again. Affects new maps.");
            list.CheckboxLabeled("Totchak eats player walls", ref totchakEatsPlayerWalls,
                "When no ruin wall is in reach, a woken totchak eats your walls.");
            list.Label("Totchak wake radius: " + totchakWakeRadius.ToString("0") + " cells");
            totchakWakeRadius = list.Slider(totchakWakeRadius, 4f, 30f);
            list.Label("Totchak wall-eating damage: x" + totchakBiteScale.ToString("0.00"));
            totchakBiteScale = list.Slider(totchakBiteScale, 0.25f, 4f);
            list.Label("Totchak grazing days before it lies down: " + totchakGrazeDays.ToString("0.0"));
            totchakGrazeDays = list.Slider(totchakGrazeDays, 1f, 30f);
            list.GapLine();

            list.CheckboxLabeled("Inscribed panels (old tongue)", ref oldTongueEnabled,
                "Panels of an old script stand against ruin walls; reading a full set unlocks research. Affects new maps.");
            list.Label("Panels per map: " + oldTonguePanelsPerMap.ToString("0"));
            oldTonguePanelsPerMap = list.Slider(oldTonguePanelsPerMap, 1f, 8f);
            list.Label("Panel reveal chance: " + oldTongueRevealChance.ToString("0%"));
            oldTongueRevealChance = list.Slider(oldTongueRevealChance, 0.1f, 1f);
            list.Label("Intellectual needed to read a panel: " + oldTongueSkillGate + (oldTongueSkillGate == 0 ? " (no gate)" : ""));
            oldTongueSkillGate = Mathf.RoundToInt(list.Slider(oldTongueSkillGate, 0f, 20f));
            list.GapLine();

            list.CheckboxLabeled("Hospice (kneeling chassis and cradle)", ref hospiceEnabled,
                "Rings of kneeling chassis in ruins; an intact one can be hauled to a hospice cradle and woken over days. Ring placement affects new maps.");
            list.Label("Intact chassis per map: up to " + hospiceIntactPerMap + " (new maps)");
            hospiceIntactPerMap = Mathf.RoundToInt(list.Slider(hospiceIntactPerMap, 0f, 3f));
            list.Label("Cradle stage length: " + hospiceStageDays.ToString("0.0") + " days (five stages)");
            hospiceStageDays = list.Slider(hospiceStageDays, 0.1f, 5f);
            list.Label("Cradle failure chance per risky stage: " + hospiceFailureChance.ToString("0%"));
            hospiceFailureChance = list.Slider(hospiceFailureChance, 0f, 0.6f);
            list.CheckboxLabeled("Limbs stage may lash out", ref hospiceLashOut,
                "At the twitching-limbs stage the machine may hit one adjacent pawn, once.");
            list.CheckboxLabeled("Deserter walks in", ref hospiceWalkInEnabled,
                "Rarely, a damaged machine walks onto the map toward your cradle. Only while a cradle stands.");
            list.Label("Walk-in frequency: " + hospiceWalkInFrequency.ToString("0%") + " of rolls proceed");
            hospiceWalkInFrequency = list.Slider(hospiceWalkInFrequency, 0f, 1f);
            list.GapLine();

            list.CheckboxLabeled("Rainbow pools", ref poolsEnabled,
                "Reaction-liquor pools cycle through four phases a day; a tap at the rim draws each phase's reagent. Pool placement affects new maps and needs FlowWorks.");
            list.Label("Pools per map: up to " + Mathf.RoundToInt(poolsPerMap) + " (new maps)");
            poolsPerMap = Mathf.Round(list.Slider(poolsPerMap, 1f, 3f));
            list.Label("Cycle length: " + poolCycleHours.ToString("0") + " hours (four phases)");
            poolCycleHours = list.Slider(poolCycleHours, 4f, 96f);
            list.Label("Bloom danger: x" + bloomDanger.ToString("0.00") + (bloomDanger <= 0f ? " (drawing the bloom is harmless)" : ""));
            bloomDanger = list.Slider(bloomDanger, 0f, 3f);
            list.CheckboxLabeled("Glower crust catalyst", ref catalystEnabled,
                "Glower crust loaded into a tap holds the pool's phase (6 hours per crust) and doubles each draw.");
            list.GapLine();

            list.CheckboxLabeled("Chotrix (invisible hunter)", ref chotrixEnabled,
                "A lean cloaked scavenger hunts lone small animals, and lone pawns at night. It shows when it strikes. Spawning affects new maps.");
            list.Label("Chotrix per map: up to " + Mathf.RoundToInt(chotrixPerMap) + " (new maps)");
            chotrixPerMap = Mathf.Round(list.Slider(chotrixPerMap, 0f, 2f));
            list.Label("Chotrix visible after a strike: " + chotrixRevealSeconds.ToString("0.0") + " seconds");
            chotrixRevealSeconds = list.Slider(chotrixRevealSeconds, 1f, 15f);
            list.CheckboxLabeled("Lacquered cloaks hide the wearer", ref lacquerCloakEnabled,
                "A cloak made with cloak lacquer makes the wearer invisible while standing still and unseen. Permanent; never expires.");
            list.Label("Lacquer: seen within " + lacquerSeenRadius.ToString("0") + " cells by a hostile with line of sight");
            lacquerSeenRadius = list.Slider(lacquerSeenRadius, 3f, 40f);
            list.GapLine();

            list.CheckboxLabeled("The Settling (calm-triggered war fallout)", ref settlingEnabled,
                "When the wind stays calm the old war's dust settles: toxic to anything unroofed, and a film that keeps every footprint until the wind returns. Off: it never starts and ends at once if running.");
            list.Label("Calm means wind below: " + settlingCalmThreshold.ToString("0.00"));
            settlingCalmThreshold = list.Slider(settlingCalmThreshold, 0.05f, 0.8f);
            list.Label("Calm hours before it starts: " + settlingCalmHours.ToString("0.0"));
            settlingCalmHours = list.Slider(settlingCalmHours, 0.5f, 24f);
            list.Label("Strong wind that ends it: above " + settlingEndWind.ToString("0.00"));
            settlingEndWind = list.Slider(settlingEndWind, 0.4f, 1.5f);
            list.Label("Hours of strong wind before it ends: " + settlingEndHours.ToString("0.0"));
            settlingEndHours = list.Slider(settlingEndHours, 0.25f, 12f);
            list.Label("Toxic strength: x" + settlingToxicStrength.ToString("0.00") + (settlingToxicStrength <= 0f ? " (harmless)" : ""));
            settlingToxicStrength = list.Slider(settlingToxicStrength, 0f, 3f);
            list.CheckboxLabeled("Lift front", ref liftFrontEnabled,
                "When the wind returns the film lifts as a grey front crossing the map downwind, with brief airborne toxic exposure as it passes.");
            list.CheckboxLabeled("War dust", ref warDustEnabled,
                "Colonists may sweep the film into war dust (thickest in crater bowls), a toxic powder for tox shells, an insecticide and a dye filler.");
            list.CheckboxLabeled("War dust cures blight", ref warDustBlightCureEnabled,
                "Growers carry one war dust to each blighted plant and dust it: the blight dies and the plant lives. Off: blight is cut as in vanilla.");
            list.Label("Buried shells per map: up to " + Mathf.RoundToInt(ordnancePerMap) + " (new maps)");
            ordnancePerMap = Mathf.Round(list.Slider(ordnancePerMap, 0f, 8f));
            list.GapLine();

            list.CheckboxLabeled("Geiger choir (Warscar soundscape)", ref choirEnabled,
                "Tetchik tick over glower and beetles, wind on ancient metal (silent during the Settling), the projector hum, the pool boil, and the tetchik jar's sound.");
            list.Label("Choir volume: " + choirVolume.ToString("0.00"));
            choirVolume = list.Slider(choirVolume, 0f, 1f);
            list.Label("Tick volume ceiling: " + choirTickVolumeCeiling.ToString("0.00"));
            choirTickVolumeCeiling = list.Slider(choirTickVolumeCeiling, 0.1f, 1f);
            list.Label("Tick density: x" + choirTickDensity.ToString("0.00"));
            choirTickDensity = list.Slider(choirTickDensity, 0.25f, 3f);
            list.CheckboxLabeled("Wind-on-metal layer", ref choirWindEnabled);
            list.CheckboxLabeled("Reduced-repetition mode", ref choirReducedRepetition,
                "Far fewer clicks, each with a slightly different pitch.");
            list.CheckboxLabeled("Tetchik jar warnings", ref choirJarWarnings,
                "A caravan carrying a tetchik jar gets a message before it enters a polluted tile.");
            list.GapLine();

            list.Label("The Warscar mark");
            list.CheckboxLabeled("Walking the Warscar marks people", ref markEnabled,
                "Every hour on a Warscar map, roofed or not, deepens a mark on each person there: a mood hit, "
              + "sad wandering at the deeper stages, and a trade in return. Off: no new mark accrues.");
            if (markEnabled)
            {
                list.Label("Mark accrual: " + markAccrualPerDay.ToString("0.00") + " per day on the map (it fades 0.10 per day)");
                markAccrualPerDay = list.Slider(markAccrualPerDay, 0f, 1f);
            }
            list.CheckboxLabeled("A deep mark never fully fades", ref markFloorEnabled,
                "Once a mark has passed halfway it never fades below a mild mark, on or off the Warscar.");
            list.CheckboxLabeled("The mark pays a trade (restart to apply)", ref markTradeBonusesEnabled,
                "Marked people hack faster, butcher mechanoids faster and, from a deepening mark, smelt faster. "
              + "Off: the mark only costs.");
            list.GapLine();

            list.Label("The chatrak's snap");
            list.CheckboxLabeled("Scaria chatrak snap in the end", ref snapEnabled,
                "A wild chatrak carrying scaria on a Warscar map starts to turn: its plates lift, it stops eating, "
              + "it circles, and then it goes for anyone. Off: no chatrak is armed, and one already turning never snaps.");
            if (snapEnabled)
            {
                list.Label("Arming sweep every " + snapArmingHours.ToString("0") + " hours");
                snapArmingHours = list.Slider(snapArmingHours, 1f, 120f);
                list.Label("Turning speed (restart to apply): x" + snapStageSpeed.ToString("0.00")
                    + " (default: about one to two weeks from armed to snap)");
                snapStageSpeed = list.Slider(snapStageSpeed, 0.25f, 4f);
            }
            list.GapLine();

            list.Label("Species (restart required; affects maps generated afterwards)");
            list.CheckboxLabeled("Chatrak (plated grazer)", ref enableChatrak);
            list.CheckboxLabeled("Tetchik (glower beetle)", ref enableTetchik);
            list.CheckboxLabeled("Pallbearer (carrion eater)", ref enablePallbearer);
            list.CheckboxLabeled("Scar roach (cleaner)", ref enableScarRoach);
            list.CheckboxLabeled("Interim donor animals (spined gow, rimclaw, helixien)", ref enableInterimDonors);
            list.CheckboxLabeled("Wreck-lichen grows beside ruins and wreck", ref enableWreckLichenSeeder,
                "Places wreck-lichen on open cells next to ruins and wreck. Worldgen-affecting.");
            list.GapLine();

            list.Label("Cross-biome (reserved — not yet wired to any mechanic in this build)");
            bool crossBiomeEnabledLocal = crossBiomeEnabled;
            list.CheckboxLabeled("Allow this mod's mechanics on other biomes", ref crossBiomeEnabledLocal,
                "Reserved for a future pass. No mechanic in this mod currently reads this switch.");
            crossBiomeEnabled = crossBiomeEnabledLocal;

            viewHeight = list.CurHeight + 24f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_WarscarMod : Mod
    {
        public static RM_WarscarSettings settings;

        public RM_WarscarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarscarSettings>();
        }

        public override string SettingsCategory()
        {
            return "Warscar";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}

namespace RimMandrake.Scarlands
{
    // Removes the wildAnimals rows of species the player switched off.
    // BiomeDef.wildAnimals is private and its commonality cache is lazy, so
    // this runs once at startup, before any map asks for a commonality.
    [StaticConstructorOnStartup]
    public static class RM_WarscarStartup
    {
        static RM_WarscarStartup()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Warscar");
            if (biome == null) return;

            HashSet<string> off = new HashSet<string>();
            if (!RM_WarscarSettings.enableChatrak) off.Add("RM_Chatrak");
            if (!RM_WarscarSettings.enableTetchik) off.Add("RM_Tetchik");
            if (!RM_WarscarSettings.enablePallbearer) off.Add("RM_Pallbearer");
            if (!RM_WarscarSettings.enableScarRoach) off.Add("RM_ScarRoach");
            if (!RM_WarscarSettings.enableInterimDonors)
            {
                off.Add("AA_SpinedGow");
                off.Add("RG_Rimclaw");
                off.Add("AA_Helixien");
            }
            if (off.Count == 0) return;

            FieldInfo wild = AccessTools.Field(typeof(BiomeDef), "wildAnimals");
            FieldInfo cache = AccessTools.Field(typeof(BiomeDef), "cachedAnimalCommonalities");
            if (wild == null || cache == null)
            {
                Log.Warning("[RM_Warscar] BiomeDef.wildAnimals/cachedAnimalCommonalities not found; species toggles not applied.");
                return;
            }
            List<BiomeAnimalRecord> rows = (List<BiomeAnimalRecord>)wild.GetValue(biome);
            rows.RemoveAll(r => r.animal != null && off.Contains(r.animal.defName));
            cache.SetValue(biome, null);
        }
    }
}
