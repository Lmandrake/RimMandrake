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
        /// behavior. Only the v1 hive (layout + plain hostile workers/queen)
        /// is gated here; the reactive alarm/rally mechanism and the three
        /// symbiotic chambers are follow-on work, not yet built (see
        /// RM_AntHiveBiomeExtension's header).</summary>
        public static bool antHiveDungeonEnabled = true;

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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref naturalPlacementEnabled, "naturalPlacementEnabled", true);
            Scribe_Values.Look(ref tentacleBestiaryEnabled, "tentacleBestiaryEnabled", true);
            Scribe_Values.Look(ref tentacleAmbientMtbHours, "tentacleAmbientMtbHours", 6f);
            Scribe_Values.Look(ref sekkulaathTankEnabled, "sekkulaathTankEnabled", true);
            Scribe_Values.Look(ref sekkulaathEscapeRiskMultiplier, "sekkulaathEscapeRiskMultiplier", 1f);
            Scribe_Values.Look(ref antHiveDungeonEnabled, "antHiveDungeonEnabled", true);
            Scribe_Values.Look(ref antHiveChanceMultiplier, "antHiveChanceMultiplier", 1f);
            Scribe_Values.Look(ref twoFrontLureEnabled, "twoFrontLureEnabled", true);
            Scribe_Values.Look(ref twoFrontLureRaidMtbHours, "twoFrontLureRaidMtbHours", 6f);
            Scribe_Values.Look(ref twoFrontLureSecondWaveChance, "twoFrontLureSecondWaveChance", 0.5f);
            Scribe_Values.Look(ref twoFrontLureSecondWaveMinHours, "twoFrontLureSecondWaveMinHours", 2f);
            Scribe_Values.Look(ref twoFrontLureSecondWaveMaxHours, "twoFrontLureSecondWaveMaxHours", 8f);
            Scribe_Values.Look(ref twoFrontLureThreatPointsMultiplier, "twoFrontLureThreatPointsMultiplier", 0.6f);
            Scribe_Values.Look(ref twoFrontLureMinThreatPoints, "twoFrontLureMinThreatPoints", 80f);
            Scribe_Values.Look(ref twoFrontLureLockOnceTriggered, "twoFrontLureLockOnceTriggered", false);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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
              + "workers and a queen in the deepest room. Off: no hive ever generates on a new map; an "
              + "already-generated one is unaffected. The reactive alarm/rally behaviour and the farm/"
              + "parasite/guard chambers are not built yet — this toggle only covers the v1 layout and "
              + "its plain hostile defenders.");
            list.Label("Hive frequency multiplier (lower = rarer): " + antHiveChanceMultiplier.ToString("0.00"));
            antHiveChanceMultiplier = list.Slider(antHiveChanceMultiplier, 0f, 3f);
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

            list.End();
        }
    }

    public class RM_FeverWoodMod : Mod
    {
        public static RM_FeverWoodSettings settings;

        public RM_FeverWoodMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_FeverWoodSettings>();
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
