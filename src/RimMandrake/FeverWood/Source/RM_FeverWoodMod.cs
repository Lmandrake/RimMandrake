using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FeverWood
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Fever Wood.
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // Deliberately thin, and that is a finding, not a shortcut: this build
    // (FEVERWOOD_RM_MOD_BUILD_1 steps 1-4) ships only the BiomeDef itself
    // plus its own workerClass. The F1/F2/F3/F5/F6/F7 hazard mechanics
    // (mirror pools, boughway network, the trunk, the mirror-list item, the
    // mirror-break incident) still live in mandrake.rm.environmentalhazards/
    // UtinniPatches, not in this mod — packaging them here is an explicitly
    // unmade call in the item file. A per-mechanic toggle for content this
    // mod does not ship would be a settings screen that lies (a checkbox
    // wired to nothing), so it is not built until that content actually
    // lands here. Only the one thing this mod controls gets a toggle.
    // ════════════════════════════════════════════════════════════════════
    public class RM_FeverWoodSettings : ModSettings
    {
        /// <summary>Master switch for this mod's own biome-worker scoring
        /// (RM_BiomeWorker_FeverWood). Off: the class still exists (the def
        /// still loads), it just always returns 0 so RM_FeverWood never wins
        /// natural placement on someone else's generated world. Default ON —
        /// matches shipped behavior. Irrelevant on the frozen campaign world,
        /// which places this biome by hand, never by score.</summary>
        public static bool naturalPlacementEnabled = true;

        /// <summary>FEVERWOOD_TENTACLE_BESTIARY_1 master toggle. Off: no
        /// ambient tentacle limbs spawn at registered pools at all (the
        /// mirror pools, mirror-break and mirror-list mechanics from
        /// mandrake.rm.environmentalhazards are unaffected — this only
        /// gates the six Sekkulaath limb-types and the drive-off ladder).
        /// Default ON — matches shipped behavior.</summary>
        public static bool tentacleBestiaryEnabled = true;

        /// <summary>Mean ticks-to-event unit (hours) for an ordinary "1-2
        /// limbs emerge" ambient sighting, while no pool is on cooldown.
        /// INVENTED default: 6 — the design sheet rules the ladder's shape
        /// but names no ambient frequency; exposed here rather than
        /// hardcoded so a play-test can retune it without a rebuild.</summary>
        public static float tentacleAmbientMtbHours = 6f;

        /// <summary>FEVERWOOD_TENTACLE_SETPIECE_TUNING_1 master toggle for
        /// the distinct "Great Emergence" set-piece (§2b row 3 — a large
        /// pool, many limbs, and the eye together, replacing the eye's
        /// prior placeholder involvement in the ordinary roll). Off: Bloom
        /// never spawns at all on this map — no lone-eye fallback, since
        /// the ordinary roll no longer carries it either. Default ON.</summary>
        public static bool tentacleGreatEmergenceEnabled = true;

        /// <summary>"Large pool" half of the detection threshold: minimum
        /// registered pool-cell count on the map. INVENTED default: 24 —
        /// no number is given in the design sheet; exposed for retuning
        /// against the map's real pool sizes without a rebuild.</summary>
        public static int tentacleGreatEmergencePoolSizeThreshold = 24;

        /// <summary>"Many limbs" half of the detection threshold: ordinary
        /// ambient encounters that must accumulate on this map (§6d:
        /// "every ordinary encounter... is a deposit toward its big one")
        /// before the Great Emergence becomes eligible at all. Resets to 0
        /// once a Great Emergence fires. INVENTED default: 6.</summary>
        public static int tentacleGreatEmergencePressureThreshold = 6;

        /// <summary>Chance, once eligible, that a successful ordinary roll
        /// escalates into the Great Emergence instead. Owner ruling
        /// 2026-09-29: "roughly the current odds, ~1/50" — default 0.02,
        /// matching the retired placeholder's ~1.9% (2-of-105) Bloom
        /// weight in magnitude.</summary>
        public static float tentacleGreatEmergenceChance = 0.02f;

        /// <summary>How many ordinary limbs spawn together with the eye
        /// when the Great Emergence fires ("many tentacles," owner
        /// verbatim). INVENTED default: 3-5.</summary>
        public static int tentacleGreatEmergenceMinLimbs = 3;
        public static int tentacleGreatEmergenceMaxLimbs = 5;

        /// <summary>FEVERWOOD_TENTACLE_SETPIECE_TUNING_1 §6f master toggle
        /// for the free-tier Uranium suppression route (RM_RadioactiveSuppressant,
        /// crafted from vanilla Uranium). Off: the item and its recipe still
        /// exist, but using one at a registered pool does nothing — the
        /// same "inert, not a working feature" posture as this mod's other
        /// toggles. Default ON.</summary>
        public static bool tentacleUraniumSuppressionEnabled = true;

        /// <summary>How many RM_RadioactiveSuppressant charges one "foul
        /// the pool" job consumes. INVENTED default: 5.</summary>
        public static int tentacleUraniumSuppressantAmountPerUse = 5;

        /// <summary>Suppression duration once a pool is fouled — "several
        /// days" per §6f, unset exactly. INVENTED default: 5 days. Also
        /// dampens the treasure trickle (RM_Corvath via the Porter), since
        /// both ride the same blockedUntilTick gate — see
        /// RM_MapComponent_TentacleWatch.SuppressPoolWithRadioactiveMaterial's
        /// own header for why that is the chosen (not incidental) shape.</summary>
        public static float tentacleUraniumSuppressionDurationDays = 5f;

        /// <summary>FEVERWOOD_DIANOGA_PRISON_1 master toggle. Off: the
        /// prison tank still exists as a plain inert building (buildable,
        /// deconstructible) but its RM_CompCapturedSpecimen never produces,
        /// never teaches, and never escapes — the safest "all-off degrades
        /// gracefully" reading, since silently disabling the BUILDING would
        /// strand a colony's already-placed tank. Default ON.</summary>
        public static bool sekkulaathTankEnabled = true;

        /// <summary>Global multiplier on both escape triggers (neglect MTB
        /// and damage-threshold per-hit chance) — lower is MORE escape-prone.
        /// Exposed because every one of those numbers is this build's own
        /// INVENTED placeholder (see FEVERWOOD_DIANOGA_TANK_TUNING_1), and a
        /// play-test should be able to retune risk without a rebuild.
        /// Default 1.0 — matches shipped behavior.</summary>
        public static float sekkulaathEscapeRiskMultiplier = 1f;

        /// <summary>FEVERWOOD_ANT_HIVE_DUNGEON_1 master toggle. Off: the
        /// procedural ant hive never generates on any Fever Wood map — a
        /// WORLDGEN-AFFECTING switch, since it changes what a freshly
        /// generated map can contain. Default ON — matches shipped
        /// behavior. The hive's reaction (notice/alarm/rally) is
        /// CreatureBehaviors' own reaction switches, not this one.</summary>
        public static bool antHiveDungeonEnabled = true;

        /// <summary>Chamber 1 of 3, the farm. Off: a new hive carries no
        /// thornbug herd (WORLDGEN-AFFECTING), and an existing herd stops
        /// being herded back to its room. Default ON.</summary>
        public static bool antHiveFarmChamberEnabled = true;

        /// <summary>FEVERWOOD_HIVE_SEALED_PASSAGES_1. Off: a hive alarm never
        /// plugs the corridor behind the intruder. Default ON.</summary>
        public static bool antHiveSealingEnabled = true;

        /// <summary>FEVERWOOD_HIVE_PARASITE_CHAMBER_1. Off: a new hive carries
        /// no glomvar (WORLDGEN-AFFECTING), and an existing glomvar stops
        /// hunting the hive (it lives on as an ordinary animal). Default ON.</summary>
        public static bool antHiveParasiteChamberEnabled = true;

        /// <summary>Multiplies RM_AntHiveBiomeExtension.hiveChance. INVENTED
        /// default 1.0 (matches shipped behavior); exposed because the base
        /// chance itself is an invented placeholder a play-test should be
        /// able to retune without a rebuild.</summary>
        public static float antHiveChanceMultiplier = 1f;

        /// <summary>FEVERWOOD_TWO_FRONT_LURE_1 master toggle. Off: the lure
        /// stake can still be built and a pawn can still be staked to it
        /// (the designator/WorkGiver chain is unaffected), but
        /// RM_MapComponent_TwoFrontLure never rolls an arrival for any
        /// staked lure on this map — an inert prop, not a working feature,
        /// same "all-off degrades gracefully" posture as this mod's other
        /// toggles. Default ON.</summary>
        public static bool twoFrontLureEnabled = true;

        /// <summary>Mean hours between first-wave rolls while at least one
        /// RM_LureStake on the map carries live bait (Rand.MTBEventOccurs
        /// unit: days, converted in RM_MapComponent_TwoFrontLure). INVENTED
        /// default: 6 — no number is given in the design sheet for how long
        /// a staked lure takes to be found.</summary>
        public static float twoFrontLureRaidMtbHours = 6f;

        /// <summary>Chance, once a first wave has arrived, that a second
        /// wave also comes. INVENTED default: 0.5 — the design sheet's own
        /// "if only ONE arrives, that is bad" (§5) rules out both 0 and 1;
        /// a coin flip is the simplest number that keeps both outcomes real.</summary>
        public static float twoFrontLureSecondWaveChance = 0.5f;

        /// <summary>Delay range (hours) from the first wave's arrival to the
        /// second wave's, so the two can never land on the same tick —
        /// "Shouldn't both come precisely at the same time... maybe the
        /// other arrives too" (owner, §5). INVENTED default: 2-8 hours.</summary>
        public static float twoFrontLureSecondWaveMinHours = 2f;
        public static float twoFrontLureSecondWaveMaxHours = 8f;

        /// <summary>FEVERWOOD_TWO_FRONT_LURE_TUNING_1 point 3: the raid's
        /// threat-points formula (`Mathf.Max(minThreatPoints,
        /// DefaultThreatPointsNow(map) * multiplier)`) was hardcoded and
        /// invented — "check it against a real colony's threat points once
        /// one exists to stake a lure with." Exposed here instead of
        /// re-guessed, so that check can happen live, in Mod Settings,
        /// without a rebuild. INVENTED defaults unchanged from the original
        /// hardcoded values: multiplier 0.6, floor 80.</summary>
        public static float twoFrontLureThreatPointsMultiplier = 0.6f;
        public static float twoFrontLureMinThreatPoints = 80f;

        /// <summary>FEVERWOOD_TWO_FRONT_LURE_TUNING_1 point 5: v1 let a
        /// staked pawn be released at any time, including after a raid is
        /// already inbound — a real, if minor, deviation from the design
        /// sheet's "you are hoping the second column shows up" framing,
        /// which reads as a commitment. Whether that should be blocked is
        /// "worth an owner check", not a guess this pass makes for him — so
        /// it ships here as an opt-in toggle, default OFF (matches shipped
        /// v1 behavior: release always allowed). Turning it on blocks
        /// "Release lure" once this specific stake has drawn a raid.</summary>
        public static bool twoFrontLureLockOnceTriggered = false;

        /// <summary>FEVERWOOD_ANT_THEFT_RAIDBACK_1: a kurreth raid stuns thornbugs and tamed sap-suckers and
        /// carries them off alive (letter + slime trail). Off: the lure's kurreth wave is a plain assault.</summary>
        public static bool antTheftEnabled = true;

        /// <summary>FEVERWOOD_KURRETH_COLUMN_RAIDBACK_1: the raid-back quest after a theft (camp site, then the hive).</summary>
        public static bool kurrethColumnEnabled = true;
        public static float kurrethColumnDays = 4f;
        public static float kurrethHiveHoldDays = 15f;

        /// <summary>FEVERWOOD_OIL_BOIL_WEATHER_1: hot still days boil the seep oil into a flammable haze.</summary>
        public static bool oilBoilEnabled = true;
        public static float oilBoilMinTempC = 35f;
        public static float oilBoilCommonalityMultiplier = 1f;
        public static float oilBoilYieldMultiplier = 2f;
        public static float oilBoilFlashRadius = 8f;
        public static bool oilBoilWakesDeep = true;

        /// <summary>FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1 toggle. On: a
        /// failed taming attempt on a vaulm, drommath or ollareth triggers
        /// its refusal (seal / swell / scream) exactly as taking damage does.
        /// Off: only damage triggers it. Default ON — matches shipped
        /// behavior.</summary>
        public static bool sapSuckerMishandleRefusalEnabled = true;

        /// <summary>FEVERWOOD_RM_CAST_COMPLETION_1: the silloch's bark wait-ambush
        /// (RM_CompSillochAmbush). Off: it is an ordinary wandering animal that
        /// never strikes unprovoked. Default ON.</summary>
        public static bool sillochAmbushEnabled = true;

        /// <summary>FEVERWOOD_RM_CAST_COMPLETION_1: the brathek eats living trees
        /// (its wood-pulp diet; RM_BrathekBoring). It never damages walls,
        /// buildings or boughways in this build. Off: it grazes like any other
        /// animal. Default ON.</summary>
        public static bool brathekBoresWood = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref naturalPlacementEnabled, "naturalPlacementEnabled", true);
            Scribe_Values.Look(ref tentacleBestiaryEnabled, "tentacleBestiaryEnabled", true);
            Scribe_Values.Look(ref tentacleAmbientMtbHours, "tentacleAmbientMtbHours", 6f);
            Scribe_Values.Look(ref tentacleGreatEmergenceEnabled, "tentacleGreatEmergenceEnabled", true);
            Scribe_Values.Look(ref tentacleGreatEmergencePoolSizeThreshold, "tentacleGreatEmergencePoolSizeThreshold", 24);
            Scribe_Values.Look(ref tentacleGreatEmergencePressureThreshold, "tentacleGreatEmergencePressureThreshold", 6);
            Scribe_Values.Look(ref tentacleGreatEmergenceChance, "tentacleGreatEmergenceChance", 0.02f);
            Scribe_Values.Look(ref tentacleGreatEmergenceMinLimbs, "tentacleGreatEmergenceMinLimbs", 3);
            Scribe_Values.Look(ref tentacleGreatEmergenceMaxLimbs, "tentacleGreatEmergenceMaxLimbs", 5);
            Scribe_Values.Look(ref tentacleUraniumSuppressionEnabled, "tentacleUraniumSuppressionEnabled", true);
            Scribe_Values.Look(ref tentacleUraniumSuppressantAmountPerUse, "tentacleUraniumSuppressantAmountPerUse", 5);
            Scribe_Values.Look(ref tentacleUraniumSuppressionDurationDays, "tentacleUraniumSuppressionDurationDays", 5f);
            Scribe_Values.Look(ref sekkulaathTankEnabled, "sekkulaathTankEnabled", true);
            Scribe_Values.Look(ref sekkulaathEscapeRiskMultiplier, "sekkulaathEscapeRiskMultiplier", 1f);
            Scribe_Values.Look(ref antHiveDungeonEnabled, "antHiveDungeonEnabled", true);
            Scribe_Values.Look(ref antHiveChanceMultiplier, "antHiveChanceMultiplier", 1f);
            Scribe_Values.Look(ref antHiveFarmChamberEnabled, "antHiveFarmChamberEnabled", true);
            Scribe_Values.Look(ref antHiveSealingEnabled, "antHiveSealingEnabled", true);
            Scribe_Values.Look(ref antHiveParasiteChamberEnabled, "antHiveParasiteChamberEnabled", true);
            Scribe_Values.Look(ref twoFrontLureEnabled, "twoFrontLureEnabled", true);
            Scribe_Values.Look(ref twoFrontLureRaidMtbHours, "twoFrontLureRaidMtbHours", 6f);
            Scribe_Values.Look(ref twoFrontLureSecondWaveChance, "twoFrontLureSecondWaveChance", 0.5f);
            Scribe_Values.Look(ref twoFrontLureSecondWaveMinHours, "twoFrontLureSecondWaveMinHours", 2f);
            Scribe_Values.Look(ref twoFrontLureSecondWaveMaxHours, "twoFrontLureSecondWaveMaxHours", 8f);
            Scribe_Values.Look(ref twoFrontLureThreatPointsMultiplier, "twoFrontLureThreatPointsMultiplier", 0.6f);
            Scribe_Values.Look(ref twoFrontLureMinThreatPoints, "twoFrontLureMinThreatPoints", 80f);
            Scribe_Values.Look(ref twoFrontLureLockOnceTriggered, "twoFrontLureLockOnceTriggered", false);
            Scribe_Values.Look(ref sapSuckerMishandleRefusalEnabled, "sapSuckerMishandleRefusalEnabled", true);
            Scribe_Values.Look(ref sillochAmbushEnabled, "sillochAmbushEnabled", true);
            Scribe_Values.Look(ref brathekBoresWood, "brathekBoresWood", true);
            Scribe_Values.Look(ref antTheftEnabled, "antTheftEnabled", true);
            Scribe_Values.Look(ref kurrethColumnEnabled, "kurrethColumnEnabled", true);
            Scribe_Values.Look(ref kurrethColumnDays, "kurrethColumnDays", 4f);
            Scribe_Values.Look(ref kurrethHiveHoldDays, "kurrethHiveHoldDays", 15f);
            Scribe_Values.Look(ref oilBoilEnabled, "oilBoilEnabled", true);
            Scribe_Values.Look(ref oilBoilMinTempC, "oilBoilMinTempC", 35f);
            Scribe_Values.Look(ref oilBoilCommonalityMultiplier, "oilBoilCommonalityMultiplier", 1f);
            Scribe_Values.Look(ref oilBoilYieldMultiplier, "oilBoilYieldMultiplier", 2f);
            Scribe_Values.Look(ref oilBoilFlashRadius, "oilBoilFlashRadius", 8f);
            Scribe_Values.Look(ref oilBoilWakesDeep, "oilBoilWakesDeep", true);
        }

        private static Vector2 scroll;
        private static float viewHeight = 2000f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, viewHeight);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.Label("Fever Wood");
            list.CheckboxLabeled("Compete for natural placement on generated worlds", ref naturalPlacementEnabled,
                "RM_FeverWood is placed by hand on the frozen campaign world and does not need this. "
              + "On a freshly generated world, this lets it compete for hot, low, humid tiles the way "
              + "any other biome does. Off: the biome never wins natural placement, but still loads "
              + "and can be assigned to a tile directly.");
            list.GapLine();
            list.Label("The biome's hazard mechanics (mirror pools, boughway network, the living trunk) "
              + "are not settings-gated yet — they ship from mandrake.rm.environmentalhazards, which has "
              + "no per-Fever-Wood toggle of its own.");
            list.GapLine();
            list.CheckboxLabeled("Sekkulaath tentacle bestiary", ref tentacleBestiaryEnabled,
                "Six pseudo-species tentacle limbs (feeler, snare, lash, porter, sentinel, bloom) "
              + "emerge ambiently at registered mirror pools and can be driven off, severed for a "
              + "harvestable body, or — rarely — permanently cleared from a map. Off: no limbs ever "
              + "spawn; a map already carrying spawned limbs is unaffected until they next retreat.");
            list.Label("Ambient sighting frequency (mean hours, lower = more often): "
                + tentacleAmbientMtbHours.ToString("0.0"));
            tentacleAmbientMtbHours = list.Slider(tentacleAmbientMtbHours, 1f, 24f);
            list.GapLine();
            list.CheckboxLabeled("The Great Emergence (rare set-piece)", ref tentacleGreatEmergenceEnabled,
                "A large pool under real pressure can, rarely, erupt into a distinct and much bigger "
              + "attack: several limbs rising together with the eye itself. Driving off or killing the "
              + "eye ends the whole attack. There is no protection against this beyond seeing it coming "
              + "— no maturity gate, no wealth floor. Off: the eye never spawns on this map at all.");
            list.Label("Pool must register at least this many water cells: " + tentacleGreatEmergencePoolSizeThreshold);
            tentacleGreatEmergencePoolSizeThreshold = (int)list.Slider(tentacleGreatEmergencePoolSizeThreshold, 4f, 80f);
            list.Label("Ordinary encounters that must accumulate at a qualifying pool first: " + tentacleGreatEmergencePressureThreshold);
            tentacleGreatEmergencePressureThreshold = (int)list.Slider(tentacleGreatEmergencePressureThreshold, 0f, 30f);
            list.Label("Chance per roll, once eligible, that it fires (roughly 1/50 by default): "
                + tentacleGreatEmergenceChance.ToString("0.000"));
            tentacleGreatEmergenceChance = list.Slider(tentacleGreatEmergenceChance, 0f, 0.25f);
            list.Label("Limbs that rise alongside the eye: " + tentacleGreatEmergenceMinLimbs + " - " + tentacleGreatEmergenceMaxLimbs);
            tentacleGreatEmergenceMinLimbs = (int)list.Slider(tentacleGreatEmergenceMinLimbs, 1f, 10f);
            tentacleGreatEmergenceMaxLimbs = (int)list.Slider(tentacleGreatEmergenceMaxLimbs, 1f, 10f);
            list.GapLine();
            list.CheckboxLabeled("Uranium suppression (free-tier route)", ref tentacleUraniumSuppressionEnabled,
                "A colonist can craft a radioactive suppressant charge from vanilla Uranium and use it to "
              + "foul a registered pool, driving whatever lives beneath it down for several days — no "
              + "hostile encounters and no treasure trickle from that pool while it lasts. Off: the item "
              + "and recipe still exist, but using one does nothing.");
            list.Label("Charges consumed per use: " + tentacleUraniumSuppressantAmountPerUse);
            tentacleUraniumSuppressantAmountPerUse = (int)list.Slider(tentacleUraniumSuppressantAmountPerUse, 1f, 20f);
            list.Label("Suppression duration (days): " + tentacleUraniumSuppressionDurationDays.ToString("0.0"));
            tentacleUraniumSuppressionDurationDays = list.Slider(tentacleUraniumSuppressionDurationDays, 0.5f, 30f);
            list.GapLine();
            list.CheckboxLabeled("Sekkulaath prison tank", ref sekkulaathTankEnabled,
                "A buildable containment cell that teaches, produces, and can get out. Off: the "
              + "tank can still be built, but it never produces, never teaches, and its occupant "
              + "never escapes — an inert box, not a working feature.");
            list.Label("Escape risk multiplier (lower = more escape-prone): "
                + sekkulaathEscapeRiskMultiplier.ToString("0.00"));
            sekkulaathEscapeRiskMultiplier = list.Slider(sekkulaathEscapeRiskMultiplier, 0.25f, 4f);
            list.GapLine();
            list.CheckboxLabeled("Ant hive dungeons", ref antHiveDungeonEnabled,
                "A rare, procedurally-laid-out chain of dug tunnels and rooms, populated with kurreth "
              + "workers and a queen in the deepest room. The hive notices you, raises the alarm and "
              + "rallies after you (Creature Behaviors' reaction settings govern that). Off: no hive ever "
              + "generates on a new map; an already-generated one is unaffected.");
            list.Label("Hive frequency multiplier (lower = rarer): " + antHiveChanceMultiplier.ToString("0.00"));
            antHiveChanceMultiplier = list.Slider(antHiveChanceMultiplier, 0f, 3f);
            list.CheckboxLabeled("Ant hive farm chamber (worldgen)", ref antHiveFarmChamberEnabled,
                "The shallowest hive room keeps a herd of thornbugs the kurreth tend and herd back when "
              + "they stray: the hive is a farm. Off: new hives carry no herd and an existing herd is no "
              + "longer herded.");
            list.CheckboxLabeled("Ant hive seals passages", ref antHiveSealingEnabled,
                "When the hive raises its alarm it plugs the tunnel behind the intruder with resin "
              + "(one tunnel per alarm; the plugs crumble after a few hours or can be broken). Off: "
              + "the way out stays open.");
            list.CheckboxLabeled("Ant hive parasite chamber (worldgen)", ref antHiveParasiteChamberEnabled,
                "A mid-depth hive room hides a glomvar, a pale thing the kurreth cannot perceive that "
              + "eats them one a day, and falls on them in a frenzy while they are busy fighting you. "
              + "Off: new hives carry none and an existing one stops hunting the hive.");
            list.GapLine();
            list.CheckboxLabeled("Two-front lure raids", ref twoFrontLureEnabled,
                "A buildable stake for staking a tamed animal or prisoner as living bait. While bait is "
              + "staked, the Fever Wood's two raiders (the kurreth swarm, and — with the Star Wars "
              + "animal collection installed — the feralisk/Wyyyschokk brood) may converge on it one "
              + "after the other, never both at once. Off: the stake and staking still work, but no "
              + "raid is ever rolled.");
            list.Label("Mean hours until a first wave answers a staked lure: " + twoFrontLureRaidMtbHours.ToString("0.0"));
            twoFrontLureRaidMtbHours = list.Slider(twoFrontLureRaidMtbHours, 1f, 24f);
            list.Label("Chance a second wave follows the first: " + twoFrontLureSecondWaveChance.ToString("0.00"));
            twoFrontLureSecondWaveChance = list.Slider(twoFrontLureSecondWaveChance, 0f, 1f);
            list.Label("Second-wave delay range (hours): " + twoFrontLureSecondWaveMinHours.ToString("0.0")
                + " - " + twoFrontLureSecondWaveMaxHours.ToString("0.0"));
            twoFrontLureSecondWaveMinHours = list.Slider(twoFrontLureSecondWaveMinHours, 0.5f, 12f);
            twoFrontLureSecondWaveMaxHours = list.Slider(twoFrontLureSecondWaveMaxHours, 0.5f, 24f);
            list.Label("Raid strength: max(" + twoFrontLureMinThreatPoints.ToString("0") + ", colony threat points x "
                + twoFrontLureThreatPointsMultiplier.ToString("0.00") + ")");
            twoFrontLureMinThreatPoints = list.Slider(twoFrontLureMinThreatPoints, 20f, 300f);
            twoFrontLureThreatPointsMultiplier = list.Slider(twoFrontLureThreatPointsMultiplier, 0.1f, 2f);
            list.CheckboxLabeled("Lock the wager in once a raid is drawn", ref twoFrontLureLockOnceTriggered,
                "Off (shipped default): a staked pawn can be released at any time, even after a raid is "
              + "already inbound. On: once THIS stake has drawn a raid, 'Release lure' is disabled until "
              + "the bait dies, is rescued by the raid's own fallout, or the stake is rebuilt — matching "
              + "the design sheet's 'you are hoping the second column shows up' framing more literally.");
            list.GapLine();
            list.CheckboxLabeled("Sap-suckers refuse a failed taming attempt", ref sapSuckerMishandleRefusalEnabled,
                "On: a failed attempt to tame a vaulm, drommath or ollareth sets off its refusal — the vaulm "
              + "seals itself, the drommath swells, the ollareth screams — just as being hurt does. Off: only "
              + "being hurt sets it off.");
            list.CheckboxLabeled("Silloch ambush from the bark", ref sillochAmbushEnabled,
                "On: a silloch presses itself against a tree trunk and waits, and strikes any small creature (or "
              + "person) that steps right beside it. It never chases: once the victim gets a few steps clear, it lets "
              + "go. Off: it wanders like an ordinary animal and never strikes unprovoked.");
            list.CheckboxLabeled("Brathek bores into living wood", ref brathekBoresWood,
                "On: a brathek eats living trees as well as ground cover, so a grove with brathek in it slowly thins. "
              + "It never digs through walls, buildings or boughways. Off: it grazes like any other animal.");
            list.GapLine();
            list.CheckboxLabeled("Kurreth carry animals off alive", ref antTheftEnabled,
                "On: a kurreth raid fights as before, but up to a third of the column pins a thornbug (then any "
              + "tamed vaulm, ollareth or drommath) down without killing it and carries it off the map alive; once "
              + "nothing is left to take, the rest leave. A letter names every animal taken and the way the column "
              + "went, and a slime trail leads off the edge there. Off: the kurreth wave is a plain assault.");
            list.CheckboxLabeled("Stolen animals can be taken back", ref kurrethColumnEnabled,
                "On: after a theft the column makes camp a few tiles away with the animals bound alive; a colonist who "
              + "reaches one while no kurreth stands guard close by cuts it free. Not reached in time, the column goes "
              + "on to its hive: if a hive lies under the map they were taken from, they are carried bound into its "
              + "deepest chamber for a while, then lost. Off: a stolen animal is simply gone with the column.");
            list.Label("Days before the column reaches its hive: " + kurrethColumnDays.ToString("0.0"));
            kurrethColumnDays = list.Slider(kurrethColumnDays, 1f, 15f);
            list.Label("Days the animals last bound in the hive: " + kurrethHiveHoldDays.ToString("0.0"));
            kurrethHiveHoldDays = list.Slider(kurrethHiveHoldDays, 2f, 60f);

            list.GapLine();
            list.CheckboxLabeled("Oil boil weather", ref oilBoilEnabled,
                "On hot, still days the seep oil boils off the ground into a low haze. While it lasts seepril yield "
              + "more seep oil, and the haze is fuel: a shot fired from or landing in it, a fire or a burning creature in "
              + "it, or a dry-lightning strike flashes fire along the haze, which then burns off. The crown (boughway, "
              + "bough-soil, stilt platforms) and roofed ground stay clear. Melee never sparks it. Off: the weather never comes.");
            list.Label("Only at or above this outdoor temperature: " + oilBoilMinTempC.ToString("0") + " C");
            oilBoilMinTempC = list.Slider(oilBoilMinTempC, 20f, 60f);
            list.Label("How often, against the biome's other weather: " + oilBoilCommonalityMultiplier.ToString("0.0") + "x");
            oilBoilCommonalityMultiplier = list.Slider(oilBoilCommonalityMultiplier, 0f, 5f);
            list.Label("Seepril yield while boiling: " + oilBoilYieldMultiplier.ToString("0.0") + "x");
            oilBoilYieldMultiplier = list.Slider(oilBoilYieldMultiplier, 1f, 4f);
            list.Label("How far a flash runs along the haze: " + oilBoilFlashRadius.ToString("0") + " cells");
            oilBoilFlashRadius = list.Slider(oilBoilFlashRadius, 2f, 20f);
            list.CheckboxLabeled("A flash at a pool's edge wakes the deep", ref oilBoilWakesDeep,
                "On: if the fire reaches a cell beside a pool, tentacles rise there (an ordinary emergence, never the "
              + "Great Emergence). Off: the fire burns and the deep sleeps on.");

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_FeverWoodMod : Mod
    {
        public static RM_FeverWoodSettings settings;

        public RM_FeverWoodMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_FeverWoodSettings>();
            // FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1 — this mod's only Harmony
            // patch so far (RM_Patch_SapSuckerMishandle).
            new HarmonyLib.Harmony("mandrake.rm.feverwood").PatchAll(typeof(RM_FeverWoodMod).Assembly);
            // FEVERWOOD_HIVE_SEALED_PASSAGES_1: the hive answers its own alarms.
            RimMandrake.CreatureBehaviors.RM_ReactionEvents.AlarmAnnounced += RM_HiveSealing.OnAlarm;
            // FEVERWOOD_HIVE_PARASITE_CHAMBER_1: an alarm sends the glomvar into a feeding frenzy.
            RimMandrake.CreatureBehaviors.RM_ReactionEvents.AlarmAnnounced += RM_CompHiveParasite.OnAlarm;
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_OilBoil.ApplySettings();
            RM_BrathekBoring.ApplySettings();
        }

        public override string SettingsCategory()
        {
            return "Fever Wood";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
