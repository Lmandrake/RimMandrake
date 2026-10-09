using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for FlowWorks.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // This screen covers excavation, flow and pits. The water-effects engine
    // came in with the 2026-09-16 merge and keeps its own screen beside this
    // one under the FlowWorks name (Source/ManyWaters/RiverSteamSettings.cs);
    // the old Pits screen retired 2026-10-02 (PIT_LEGACY_CODE_RETIRE_1) and its
    // four surviving settings live here.
    //
    // ⚠️ `canalFlowEnabled`, `flowRateMultiplier` and `floodVolumeMultiplier`
    // are GONE. They existed only to scale CompFluidReservoir's drip and
    // re-flood cadence, and ruling 24 (owner, 2026-09-16) deleted that comp
    // outright — a source is not a building. A slider that moves nothing is
    // worse than an absent one, so they are removed rather than left inert.
    // ════════════════════════════════════════════════════════════════════
    public class RimMandrakeFlowWorksSettings : ModSettings
    {
        // ── the depth engine (rulings 17-19, 21, 26) ──────────────────────
        //   4. depthEngineEnabled — master switch for the depth/fill grid and
        //      its pulse. Off: nothing pours, nothing overflows, and a dug
        //      channel is inert earthworks. Digging and the depth-derived
        //      movement cost are UNAFFECTED, because those are properties of
        //      terrain the player already paid labour for.
        //   5. pulseIntervalTicks — how often the sort-and-overflow runs.
        //      Never per tick; pillar 2 forbids a fluid simulation outright.
        //   6. flowPerPulse — how many fill levels one cell may take in from
        //      its neighbours per pulse. The viscosity dial, effectively.
        //   7. digToDepthEnabled — deepening. Off: one level only, the way
        //      the mod shipped before the four-depth ruling.
        public static bool depthEngineEnabled = true;
        public static float pulseIntervalTicks = 250f;
        public static float flowPerPulse = 1f;
        public static bool digToDepthEnabled = true;

        // ── UNPROVEN MECHANICS, OFF BY DEFAULT ───────────────────────────
        // The standing rule is "defaults = shipped behavior". These two came
        // in with the 2026-09-16 LiquidTypes merge, and LiquidTypes was never
        // in the live ModsConfig — so their shipped behavior is that they have
        // never run at all. LIQUID_TYPES_SPIKES_1 says it plainly of the
        // ignition prototype: "has never ticked inside a running game".
        // Faithful to that, both default OFF. Turning them ON is the owner's
        // call AFTER a live proof, not a default an agent quietly chose for
        // him — a merge must not smuggle unproven damage into a campaign.
        //
        // Gated at the top of each MapComponentTick rather than by dropping
        // the component: a MapComponent is scribed per map, and removing one
        // that a save already carries is a save-compat problem. Off means it
        // ticks and returns; the component still exists, still loads, and
        // flipping the toggle needs no new game.
        //   9. liquidCorrosionEnabled  — LiquidCorrosionMapComponent
        //  10. liquidIgnitionEnabled   — LiquidIgnitionMapComponent
        public static bool liquidCorrosionEnabled = false;
        public static bool liquidIgnitionEnabled = false;
        // FLOWWORKS_BUILD_PROGRAM_1 Phase 6 — fire on the depth/fill engine (RM_LiquidFire). Ruling 7's numbers are
        // the owner's (1 canal level/day, 1 source level/5 days); front speed and source reach are PROVISIONAL.
        public static bool canalFireEnabled = true;
        // LIQUID_HEAT_PUSH_1: hot/icy liquid warms or chills its room through vanilla heat (strength PROVISIONAL).
        public static bool liquidHeatPushEnabled = true;
        public static float liquidHeatStrength = 1f;
        public static float canalBurnDaysPerLevel = 1f;
        public static float sourceBurnDaysPerLevel = 5f;
        public static float fireFrontSpeedMultiplier = 1f;
        public static float sourceFireReach = 3f;
        public static bool explosionIgnitesLiquidEnabled = true;
        public static bool foamSmothersLiquidFireEnabled = true;
        public static bool rainDousesLiquidFireEnabled = true;
        public static int SourceFireReach => Mathf.Clamp(Mathf.RoundToInt(sourceFireReach), 0, 30);

        // ══════════════════════════════════════════════════════════════════
        // PHASE 4 — STOCK, DISPLACEMENT, RECESSION, REFILL, SINKS.
        //
        // ⚠️ DELIBERATELY ITS OWN SECTION, top to bottom: fields, ExposeData
        // lines and the screen block below all sit together and touch nothing
        // above them. A second lane was adding unrelated toggles to this file
        // in the same window; keeping Phase 4 in one contiguous run is what
        // makes both changes land without either rewriting the other's lines.
        //
        // Defaults = the behaviour this phase ships, per the standing rule
        // (owner, 2026-09-12). ALL-OFF degrades exactly to the pre-Phase-4
        // engine: dry digging, the sort-and-overflow pulse, limitless sources,
        // nothing receding, nothing refilling, nothing draining off-map.
        //  11. fillInEnabled              — the fill-in designator exists at all
        //  12. fillInDisplacementEnabled  — displaced liquid is credited back
        //  13. sourceBudgetEnabled        — the 5:1 budget; off = limitless all
        //  14. stickyLimitlessEnabled     — edge + size classification
        //  15. recessionEnabled           — a spent body gives up cells
        //  16. refillEnabled              — seepage, rain and season
        //  17. rainFillsExcavationsEnabled— ruling 25, roof grid consulted
        //  18. edgeSinksEnabled           — map-edge drainage
        public static bool fillInEnabled = true;
        public static bool fillInDisplacementEnabled = true;
        public static bool sourceBudgetEnabled = true;
        public static bool stickyLimitlessEnabled = true;
        public static bool recessionEnabled = true;
        // PROVISIONAL (auto-decided 2026-10-09, LIQUID_RECESSION_TOPOLOGY_1): a body with any stock keeps its last cell.
        public static bool recedeKeepsLastCell = true;
        public static bool refillEnabled = true;
        public static bool rainFillsExcavationsEnabled = true;
        public static bool edgeSinksEnabled = true;
        // EXCAVATION_LOAD_SANITY_REPAIR_1: clamp/repair the dig grids and compact the liquid list on map load.
        public static bool excavationLoadRepairEnabled = true;
        // PROVISIONAL (auto-decided 2026-10-09, EXCAVATION_LEGACY_MIGRATION_FLAG_1): unrecorded filled-in cells get neighbour terrain.
        public static bool legacyFillFallbackEnabled = true;
        // FLOOD_DRIVER_OWNERSHIP_CONTRACT_1: a legacy flood release on an excavated cell fills it through the engine.
        public static bool legacyFloodViaEngineEnabled = true;
        public static float sourceBudgetMultiplier = 1f;
        public static float minLimitlessBodyCells = 50f;
        public static float refillRateMultiplier = 1f;
        public static float rainFillPerPulse = 0.1f;

        // ══════════════════════════════════════════════════════════════════
        // PHASE 5 — CAPTURE, LADDERS, AND THE ONE SHOOTING RULE.
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as Phase 4 above:
        // fields, ExposeData lines and the screen block are each kept whole and
        // touch nothing around them, so a concurrent lane editing this file
        // does not have to rewrite these lines to land its own.
        //
        // Defaults = what this phase ships. All three OFF degrades to the
        // pre-Phase-5 engine: nothing captures, nothing is stranded, and every
        // verb's line of fire is vanilla's again.
        //  19. superdeepCaptureEnabled     — ruling 26, fall-in at D = 4
        //  20. superdeepCapturesOwnFaction — whether your own hole takes you too
        //  21. ladderRequiredToExitEnabled — the jailer mechanic
        //  22. superdeepShootingRuleEnabled— ruling 23, 8-way adjacency only
        //
        // 🔴 ONE DISCLOSED DEVIATION from "all-off = exactly as before". Before
        // this phase RM_Channel_Superdeep was <passability>Impassable</passability>,
        // a placeholder whose own def comment says "until fall-in capture and
        // ladders exist". They exist now, so it is passable, and passability is a
        // per-Def field that no runtime toggle can move. With capture off a
        // SUPERDEEP cell is therefore a very costly hole (pathCost 300) rather
        // than a wall. That is the placeholder retiring, not a mechanic hiding.
        public static bool superdeepCaptureEnabled = true;
        public static bool superdeepCapturesOwnFaction = false;
        public static bool ladderRequiredToExitEnabled = true;
        // LADDER_PRISON_DOOR_1 (owner Q1 2026-10-02): a ladder is a prison door. Off = any ladder lets anyone out.
        public static bool ladderPrisonDoorEnabled = true;
        // FLOWWORKS_LADDER_RAISE_LOWER_1 (owner 2026-10-06): the player raises and lowers each ladder. Off = no
        // gizmo and every ladder counts as lowered.
        public static bool ladderRaiseLowerEnabled = true;
        public static bool superdeepShootingRuleEnabled = true;
        // Owner 2026-10-06 (Q5/Q9): a damaging or fire blast breaks any pit cover it reaches.
        public static bool blastsBreakPitCovers = true;
        // SUPERDEEP_PRISON_ROOM_1 (LAW 2 exception [D]): an enclosed superdeep area is its own room;
        // capture down / convert down are done from the lip.
        public static bool superdeepRoomsEnabled = true;
        public static bool captureDownEnabled = true;
        public static bool wardenFromLipEnabled = true;
        // SUPERDEEP_HOLDER_RETIRE_1, owner Q4: the pit must be as wide as the creature.
        // Required width W = max(1, round(sqrt(BodySize x this))). 1 = the proposed bands.
        public static float pitWidthBodySizeMultiplier = 1f;
        // PIT_LEGACY_CODE_RETIRE_1: the four survivors of the retired PitsMod screen
        // (same field names and defaults, so nothing that reads them changes meaning).
        // The cover's mass trigger (PIT_COVER_FALL_REWIRE_1) and the fall on any descent
        // into a D=4 cell. Struggle/escape and pit-cell exposure died with their mechanics.
        public static bool trapTriggerEnabled = true;
        public static float trapSensitivityMultiplier = 1f;
        public static bool fallDamageEnabled = true;
        public static float fallDamageMultiplier = 1f;
        // PIT_TEMPERATURE_SOFTENING_1 (PROVISIONAL numbers): exposure on/off, temperature coupling, resistance loss rate.
        public static bool pitExposureEnabled = true;
        // PIT_FILL_EFFECTS_1 (PROVISIONAL rates): drowning at D=4 with any fill (non-swimmers), poison fluid toxin keyed to fill.
        public static bool pitDrowningEnabled = true;
        public static float pitDrowningRateMultiplier = 1f;
        public static bool poisonFillEnabled = true;
        public static float pitTemperatureCoupling = 3f;
        public static float pitResistanceLossMultiplier = 1f;
        // CANAL_BOTTOM_SPIKES_1: RM_Spikes on a D=4 floor stab whoever drops in (3 Sharp hits, 40 x BodySize total, PROPOSED).
        public static bool spikesEnabled = true;
        public static float spikeDamageMultiplier = 1f;
        // PIT_DEPTH_DRAW_OFFSET_1 (PROVISIONAL 0.3 cells/level: D=4 lip 1.2x a person's height): pawns drawn lower on dug cells.
        public static bool pitDepthDrawOffsetEnabled = true;
        public static float pitSinkPerLevel = 0.3f;
        // EXCAVATION_WALL_ART_1: wall faces drawn by SectionLayer_RMExcavationWalls (procedural until art lands).
        public static bool excavationWallFacesEnabled = true;
        // FLOWWORKS_VISUAL_PRINCIPLES_1 (owner principles 1-5, 2026-10-05). Each OFF falls back to the flat look.
        public static bool excavationWallMaterialEnabled = true;   // faces in the ground's own dirt/stone, lit like vanilla walls
        public static bool pitLipOcclusionEnabled = true;          // the near lip hides a sunk pawn's lower body
        public static bool pitSinkClampEnabled = false;            // OFF (owner 2026-10-07, try without): hold the sink so the drawn centre stays north of the near lip; on a south-row pit cell this caps every pawn at 0.5
        public static float pitLipOcclusion = 0.85f;               // how much it hides (1 = fully)
        public static bool pitLipOccupantCutEnabled = true;        // FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1: a window through the near bank so the occupant stays visible
        public static float pitLipOccupantCutWidth = 1f;           // PROVISIONAL: window width in cells (1 = the occupied cell)
        public static bool liquidSurfaceMotionEnabled = true;      // ripples / gloss / sheen on filled cuts
        public static bool liquidWakesEnabled = true;              // V wakes behind anything wading
        public static bool liquidLooksEnabled = true;              // per-liquid engine surface look (off: plain XML look)
        // FLOWWORKS_REVIEW_LOOKS_ROUND_1 (owner review, 2026-10-06). Each OFF degrades to the previous look/behaviour.
        public static bool liquidBubblesEnabled = true;            // acid, slime and boiling liquid bubble (item 7)
        public static float liquidBubbleDensity = 1f;              // x every liquid's own bubble rate
        public static bool liquidSeeThroughEnabled = true;         // a cut's floor/walls show through clear liquid (item 10)
        public static bool pitWalkNormalEnabled = true;            // walking along a pit floor is normal; only climbing is slow (item 9)
        // Liquids that may fill a cut (item 4): a FluidDef named here is refused by every fill (pump, drill, debug,
        // review map). Default empty = every liquid on. Labels come from the FluidDefs, so a new liquid appears itself.
        public static System.Collections.Generic.List<string> disabledFluids = new System.Collections.Generic.List<string>();

        public static bool FluidAllowed(FluidDef f)
        {
            return f == null || disabledFluids == null || !disabledFluids.Contains(f.defName);
        }
        public static bool pitScorchEnabled = true;                // a cut that burned dry reads scorched
        public static float pitScorchFadeDays = 20f;               // PROVISIONAL; 0 = never fades
        public static bool pitOutlineEnabled = true;               // closed dark outline, strong near (south) lining
        public static bool pitHidesShadowEnabled = true;           // no ground shadow under a pawn sunk in a cut
        // FLOWWORKS_DOOR_FAMILY_1: the sluice and security grate (two stuffable doors that pass liquid).
        public static bool flowDoorsSealedFromPitEnabled = true;
        public static bool sluiceLetsBigThroughEnabled = true;
        // FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 VISCOSITY (PROVISIONAL stride = ticksPerTile / 60): a viscous fluid's level
        // moves only every Nth pulse (tar 6, slime 8, oil 3), so its fill front lags water's.
        public static bool viscosityEnabled = true;
        // THICK_LIQUID_CREEP_1: a thick liquid's fill front moves one cell per moving pulse (a cell that just received it cannot
        // pass it on in the same pulse). Needs viscosityEnabled. PROVISIONAL: one cell per moving pulse.
        public static bool thickCreepEnabled = true;

        // ══════════════════════════════════════════════════════════════════
        // LIQUID_BOTTLE_LOOP_1 — FILL / USE / DIRTY / WASH.
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as Phases 4/5 above.
        //
        // Both default ON -- that is the shipped campaign behaviour (design
        // "Dirty-bottle stage is a Mod Settings toggle; default ON in the
        // campaign"). Off degrades gracefully at two different joints:
        //  23. bottleLoopEnabled       — the whole fill/wash WorkGiver pair.
        //      Off: RM_BottleEmpty/RM_BottleDirty just sit there like any
        //      other item; a colonist can still hand-carry and drink a
        //      filled bottle, only the automatic fill/wash labour stops.
        //  24. bottleDirtyStageEnabled — whether "use" leaves a dirty bottle
        //      to wash at all. Off: drinking a filled bottle returns a clean
        //      empty bottle directly and RM_BottleDirty is never minted —
        //      any dirty bottle a save already holds from before the switch
        //      is still washable, since WorkGiver_WashBottle does not gate
        //      on this toggle.
        public static bool bottleLoopEnabled = true;
        public static bool bottleDirtyStageEnabled = true;
        // LIQUID_BOTTLE_LOOP_1 revert timer: bottled boiling/icy water returns to fresh (row data).
        public static bool bottleRevertEnabled = true;

        // ══════════════════════════════════════════════════════════════════
        // LIQUID_BOTTLE_LOOP_1 — THE TANK (fill/empty at Building_LiquidTank).
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as the blocks above.
        //
        //  25. tankLoopEnabled        — the pour-in/draw-out WorkGiver pair.
        //      Off: a built tank still holds whatever it already has (no
        //      save-compat loss), a colonist can still hand-carry a
        //      container to it and use the gizmo-free interaction is simply
        //      absent -- only the automatic fetch labour stops, same as
        //      bottleLoopEnabled above.
        //  26. tankCapacityMultiplier — scales the 300-unit base stock every
        //      RM_LiquidTank ships with. 1x is the shipped size; this is the
        //      "tuning where a number is the experience" dial for it.
        public static bool tankLoopEnabled = true;
        public static float tankCapacityMultiplier = 1f;
        // FLOWWORKS_BUILD_PROGRAM_1 Phase 8: the universal pump (first slice, no hoses).
        public static bool liquidPumpEnabled = true;

        // ══════════════════════════════════════════════════════════════════
        // MANY_WATERS_DRILL_BUILDINGS_1 — THE DRILL/TAP FAMILY.
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as the blocks above.
        //
        //  27. liquidDrillingEnabled    — master switch for the whole route.
        //      Off: a built drill or tap sits there consuming nothing and
        //      producing nothing (RM_MapComponent_SubsurfaceLiquid still
        //      SURVEYS every map regardless — that fact does not depend on a
        //      slider — only spending the reserve does). Default ON: this is
        //      the shipped fourth acquisition route, not a hidden prototype.
        //  28. drillYieldChanceMultiplier — scales every biome's own
        //      chanceMapHasYield. 1x is what the biome extension authored;
        //      raise it to make "the right maps" common, lower it to make a
        //      drillable map a real find.
        //  29. drillUnitsPerCycle       — fill-units a drill may pull from
        //      the reserve per TickRare (250 ticks) once its outlet has
        //      room. The RM_LiquidDrillExtension.unitsPerCycleMultiplier on
        //      each ThingDef (drill vs. tap) scales this same number rather
        //      than duplicating it.
        public static bool liquidDrillingEnabled = true;
        public static float drillYieldChanceMultiplier = 1f;
        public static float drillUnitsPerCycle = 1f;

        // ══════════════════════════════════════════════════════════════════
        // WORLDMAP_LIQUID_TAGS_1 — TYPED WORLDMAP BODIES.
        //
        // ⚠️ ITS OWN CONTIGUOUS SECTION, same discipline as the blocks above.
        //
        //  30. typedLiquidShoresEnabled — the landing repaint. On (shipped):
        //      a colony landing on a tile belonging to a TYPED body of water
        //      finds that body's own liquid underfoot instead of generic
        //      water. Off: every map generates exactly as vanilla would,
        //      which is ALREADY what an untyped tile does — so this switch
        //      changes nothing at all on an untyped tile and is
        //      "worldgen-affecting" only in the sense that it decides what a
        //      NEWLY generated map looks like. An already-generated map keeps
        //      whatever terrain it has either way; nothing repaints
        //      retroactively and nothing un-repaints.
        public static bool typedLiquidShoresEnabled = true;

        // ══════════════════════════════════════════════════════════════════
        // CRACKEDLANDS_MECHANICS_BUILD_1 §1 — THE SWALE. Own contiguous section.
        //  31. swaleEnabled — a water-fed swale walks the ground around it up
        //      the fertility ladder (Source/Swale/RM_Swale.cs). Off: a built
        //      swale is an inert liner; terrain it already improved stays.
        //  swaleRateMultiplier — PROVISIONAL tuning on the one-rung-per-fed-day pace.
        // FLOWWORKS_QUARRY_DIGGING_1: canal-dig finds (all numbers PROVISIONAL).
        public static bool digFindsEnabled = true;
        public static bool digFindsLocalOnly = true;
        public static float digFindChanceMultiplier = 1f;
        public static float digFindBudgetPercent = 5f;
        public static bool digFindLetterEnabled = true;
        public static bool swaleEnabled = true;
        public static float swaleRateMultiplier = 1f;

        public static float SwaleRateMultiplier => Mathf.Clamp(swaleRateMultiplier, 0.1f, 10f);

        public static float DrillUnitsPerCycle => Mathf.Max(0.05f, drillUnitsPerCycle);

        public static int MinLimitlessBodyCells => Mathf.Max(1, Mathf.RoundToInt(minLimitlessBodyCells));

        public static int PulseIntervalTicks => Mathf.Max(60, Mathf.RoundToInt(pulseIntervalTicks));

        public static int FlowPerPulse => Mathf.Clamp(Mathf.RoundToInt(flowPerPulse), 1, 4);

        public override void ExposeData()
        {
            // HARMONY_PATCH_RESILIENCE_1: a feature switched off by a failed patch is saved with the player's own value.
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref depthEngineEnabled, "depthEngineEnabled", true);
            Scribe_Values.Look(ref pulseIntervalTicks, "pulseIntervalTicks", 250f);
            Scribe_Values.Look(ref flowPerPulse, "flowPerPulse", 1f);
            Scribe_Values.Look(ref digToDepthEnabled, "digToDepthEnabled", true);
            Scribe_Values.Look(ref liquidCorrosionEnabled, "liquidCorrosionEnabled", false);
            Scribe_Values.Look(ref liquidIgnitionEnabled, "liquidIgnitionEnabled", false);
            Scribe_Values.Look(ref canalFireEnabled, "canalFireEnabled", true);
            Scribe_Values.Look(ref liquidHeatPushEnabled, "liquidHeatPushEnabled", true);
            Scribe_Values.Look(ref liquidHeatStrength, "liquidHeatStrength", 1f);
            Scribe_Values.Look(ref canalBurnDaysPerLevel, "canalBurnDaysPerLevel", 1f);
            Scribe_Values.Look(ref sourceBurnDaysPerLevel, "sourceBurnDaysPerLevel", 5f);
            Scribe_Values.Look(ref fireFrontSpeedMultiplier, "fireFrontSpeedMultiplier", 1f);
            Scribe_Values.Look(ref sourceFireReach, "sourceFireReach", 3f);
            Scribe_Values.Look(ref explosionIgnitesLiquidEnabled, "explosionIgnitesLiquidEnabled", true);
            Scribe_Values.Look(ref foamSmothersLiquidFireEnabled, "foamSmothersLiquidFireEnabled", true);
            Scribe_Values.Look(ref rainDousesLiquidFireEnabled, "rainDousesLiquidFireEnabled", true);
            // ── Phase 4 (see the block above; kept contiguous on purpose) ──
            Scribe_Values.Look(ref fillInEnabled, "fillInEnabled", true);
            Scribe_Values.Look(ref fillInDisplacementEnabled, "fillInDisplacementEnabled", true);
            Scribe_Values.Look(ref sourceBudgetEnabled, "sourceBudgetEnabled", true);
            Scribe_Values.Look(ref stickyLimitlessEnabled, "stickyLimitlessEnabled", true);
            Scribe_Values.Look(ref recessionEnabled, "recessionEnabled", true);
            Scribe_Values.Look(ref recedeKeepsLastCell, "recedeKeepsLastCell", true);
            Scribe_Values.Look(ref refillEnabled, "refillEnabled", true);
            Scribe_Values.Look(ref rainFillsExcavationsEnabled, "rainFillsExcavationsEnabled", true);
            Scribe_Values.Look(ref edgeSinksEnabled, "edgeSinksEnabled", true);
            Scribe_Values.Look(ref excavationLoadRepairEnabled, "excavationLoadRepairEnabled", true);
            Scribe_Values.Look(ref legacyFillFallbackEnabled, "legacyFillFallbackEnabled", true);
            Scribe_Values.Look(ref legacyFloodViaEngineEnabled, "legacyFloodViaEngineEnabled", true);
            Scribe_Values.Look(ref sourceBudgetMultiplier, "sourceBudgetMultiplier", 1f);
            Scribe_Values.Look(ref minLimitlessBodyCells, "minLimitlessBodyCells", 50f);
            Scribe_Values.Look(ref refillRateMultiplier, "refillRateMultiplier", 1f);
            Scribe_Values.Look(ref rainFillPerPulse, "rainFillPerPulse", 0.1f);
            // ── Phase 5 (see the block above; kept contiguous on purpose) ──
            Scribe_Values.Look(ref superdeepCaptureEnabled, "superdeepCaptureEnabled", true);
            Scribe_Values.Look(ref blastsBreakPitCovers, "blastsBreakPitCovers", true);
            Scribe_Values.Look(ref superdeepCapturesOwnFaction, "superdeepCapturesOwnFaction", false);
            Scribe_Values.Look(ref ladderRequiredToExitEnabled, "ladderRequiredToExitEnabled", true);
            Scribe_Values.Look(ref ladderPrisonDoorEnabled, "ladderPrisonDoorEnabled", true);
            Scribe_Values.Look(ref ladderRaiseLowerEnabled, "ladderRaiseLowerEnabled", true);
            Scribe_Values.Look(ref superdeepShootingRuleEnabled, "superdeepShootingRuleEnabled", true);
            Scribe_Values.Look(ref superdeepRoomsEnabled, "superdeepRoomsEnabled", true);
            Scribe_Values.Look(ref captureDownEnabled, "captureDownEnabled", true);
            Scribe_Values.Look(ref wardenFromLipEnabled, "wardenFromLipEnabled", true);
            Scribe_Values.Look(ref pitWidthBodySizeMultiplier, "pitWidthBodySizeMultiplier", 1f);
            Scribe_Values.Look(ref trapTriggerEnabled, "trapTriggerEnabled", true);
            Scribe_Values.Look(ref trapSensitivityMultiplier, "trapSensitivityMultiplier", 1f);
            Scribe_Values.Look(ref fallDamageEnabled, "fallDamageEnabled", true);
            Scribe_Values.Look(ref fallDamageMultiplier, "fallDamageMultiplier", 1f);
            Scribe_Values.Look(ref pitExposureEnabled, "pitExposureEnabled", true);
            Scribe_Values.Look(ref pitDrowningEnabled, "pitDrowningEnabled", true);
            Scribe_Values.Look(ref pitDrowningRateMultiplier, "pitDrowningRateMultiplier", 1f);
            Scribe_Values.Look(ref poisonFillEnabled, "poisonFillEnabled", true);
            Scribe_Values.Look(ref pitTemperatureCoupling, "pitTemperatureCoupling", 3f);
            Scribe_Values.Look(ref pitResistanceLossMultiplier, "pitResistanceLossMultiplier", 1f);
            Scribe_Values.Look(ref spikesEnabled, "spikesEnabled", true);
            Scribe_Values.Look(ref spikeDamageMultiplier, "spikeDamageMultiplier", 1f);
            Scribe_Values.Look(ref pitDepthDrawOffsetEnabled, "pitDepthDrawOffsetEnabled", true);
            Scribe_Values.Look(ref pitSinkPerLevel, "pitSinkPerLevel", 0.3f);
            Scribe_Values.Look(ref excavationWallFacesEnabled, "excavationWallFacesEnabled", true);
            Scribe_Values.Look(ref excavationWallMaterialEnabled, "excavationWallMaterialEnabled", true);
            Scribe_Values.Look(ref pitLipOcclusionEnabled, "pitLipOcclusionEnabled", true);
            Scribe_Values.Look(ref pitSinkClampEnabled, "pitSinkClampEnabled", false);
            Scribe_Values.Look(ref pitLipOcclusion, "pitLipOcclusion", 0.85f);
            Scribe_Values.Look(ref pitLipOccupantCutEnabled, "pitLipOccupantCutEnabled", true);
            Scribe_Values.Look(ref pitLipOccupantCutWidth, "pitLipOccupantCutWidth", 1f);
            Scribe_Values.Look(ref liquidSurfaceMotionEnabled, "liquidSurfaceMotionEnabled", true);
            Scribe_Values.Look(ref liquidWakesEnabled, "liquidWakesEnabled", true);
            Scribe_Values.Look(ref liquidLooksEnabled, "liquidLooksEnabled", true);
            Scribe_Values.Look(ref liquidBubblesEnabled, "liquidBubblesEnabled", true);
            Scribe_Values.Look(ref liquidBubbleDensity, "liquidBubbleDensity", 1f);
            Scribe_Values.Look(ref liquidSeeThroughEnabled, "liquidSeeThroughEnabled", true);
            Scribe_Values.Look(ref pitWalkNormalEnabled, "pitWalkNormalEnabled", true);
            Scribe_Collections.Look(ref disabledFluids, "disabledFluids", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && disabledFluids == null)
            {
                disabledFluids = new System.Collections.Generic.List<string>();
            }
            Scribe_Values.Look(ref pitOutlineEnabled, "pitOutlineEnabled", true);
            Scribe_Values.Look(ref pitHidesShadowEnabled, "pitHidesShadowEnabled", true);
            Scribe_Values.Look(ref pitScorchEnabled, "pitScorchEnabled", true);
            Scribe_Values.Look(ref pitScorchFadeDays, "pitScorchFadeDays", 20f);
            Scribe_Values.Look(ref flowDoorsSealedFromPitEnabled, "flowDoorsSealedFromPitEnabled", true);
            Scribe_Values.Look(ref sluiceLetsBigThroughEnabled, "sluiceLetsBigThroughEnabled", true);
            Scribe_Values.Look(ref viscosityEnabled, "viscosityEnabled", true);
            Scribe_Values.Look(ref thickCreepEnabled, "thickCreepEnabled", true);
            // ── LIQUID_BOTTLE_LOOP_1 (see the block above; kept contiguous) ─
            Scribe_Values.Look(ref bottleLoopEnabled, "bottleLoopEnabled", true);
            Scribe_Values.Look(ref bottleDirtyStageEnabled, "bottleDirtyStageEnabled", true);
            Scribe_Values.Look(ref bottleRevertEnabled, "bottleRevertEnabled", true);
            // ── LIQUID_BOTTLE_LOOP_1 tank (see the block above; contiguous) ─
            Scribe_Values.Look(ref tankLoopEnabled, "tankLoopEnabled", true);
            Scribe_Values.Look(ref tankCapacityMultiplier, "tankCapacityMultiplier", 1f);
            Scribe_Values.Look(ref liquidPumpEnabled, "liquidPumpEnabled", true);
            // ── MANY_WATERS_DRILL_BUILDINGS_1 (see the block above; contiguous) ─
            Scribe_Values.Look(ref liquidDrillingEnabled, "liquidDrillingEnabled", true);
            Scribe_Values.Look(ref drillYieldChanceMultiplier, "drillYieldChanceMultiplier", 1f);
            Scribe_Values.Look(ref drillUnitsPerCycle, "drillUnitsPerCycle", 1f);
            // ── WORLDMAP_LIQUID_TAGS_1 (see the block above; contiguous) ───
            Scribe_Values.Look(ref typedLiquidShoresEnabled, "typedLiquidShoresEnabled", true);
            // ── CRACKEDLANDS_MECHANICS_BUILD_1 §1 swale (contiguous) ───────
            Scribe_Values.Look(ref digFindsEnabled, "digFindsEnabled", true);
            Scribe_Values.Look(ref digFindsLocalOnly, "digFindsLocalOnly", true);
            Scribe_Values.Look(ref digFindChanceMultiplier, "digFindChanceMultiplier", 1f);
            Scribe_Values.Look(ref digFindBudgetPercent, "digFindBudgetPercent", 5f);
            Scribe_Values.Look(ref digFindLetterEnabled, "digFindLetterEnabled", true);
            Scribe_Values.Look(ref swaleEnabled, "swaleEnabled", true);
            Scribe_Values.Look(ref swaleRateMultiplier, "swaleRateMultiplier", 1f);
            // ── Rivers (River Works, merged 2026-10-05): one settings file, unique keys ──
            Rivers.RM_RiversSettings.ExposeData();
            Machinery.RM_MachinerySettings.ExposeData();
            // Builder Y sections (2026-10-05): tanker, sluice gates, bottled blood, quarry. One line each.
            Machinery.Logistics.RM_TankerSettings.ExposeData();
            Machinery.Logistics.RM_SluiceGateSettings.ExposeData();
            Machinery.Logistics.RM_BloodDrawSettings.ExposeData();
            Machinery.Kits.RM_KitSettings.ExposeData();
            Quarry.RM_QuarrySettings.ExposeData();
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static Vector2 scrollPosition = Vector2.zero;

        // FLOWWORKS_SETTINGS_SCOPE_RESET_1 (FL-5): defaults are snapshotted when the type initialises, which is
        // before any save is read, so "reset" restores the shipped value even after ExposeData has overwritten it.
        private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = CaptureDefaults();

        private static System.Collections.Generic.Dictionary<string, object> CaptureDefaults()
        {
            var d = new System.Collections.Generic.Dictionary<string, object>();
            foreach (System.Reflection.FieldInfo f in typeof(RimMandrakeFlowWorksSettings).GetFields(
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
            {
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float))
                {
                    d[f.Name] = f.GetValue(null);
                }
            }
            return d;
        }

        /// <summary>Resets the named fields to their shipped values.</summary>
        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                object v;
                System.Reflection.FieldInfo f = typeof(RimMandrakeFlowWorksSettings).GetField(n);
                if (f != null && shippedDefaults.TryGetValue(n, out v))
                {
                    f.SetValue(null, v);
                }
            }
        }

        private static void DrawSectionReset(Listing_Standard list, string[] names)
        {
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
        }

        public void DoWindowContents(Rect inRect)
        {
            // Raised from 900 when the unproven-mechanics section landed, and
            // from 1400 when Phase 4's stock section did, and from 3000 when
            // Phase 5's capture/ladder/shooting section did: this is a FIXED view
            // height, so content taller than it is clipped rather than scrolled
            // to. Anyone adding a block here raises this number in the same
            // edit or their block is invisible. (+2000 for the Rivers section; +2400 for the
            // tanker / sluice-gate / blood / quarry sections, 2026-10-05; +500 for liquid looks / pit outline /
            // pit shadow; +150 for hot and icy liquid, 2026-10-08; +400 for per-section reset buttons.)
            Rect view = new Rect(0f, 0f, inRect.width - 24f, 11500f);
            Widgets.BeginScrollView(inRect, ref scrollPosition, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);

            Text.Font = GameFont.Medium;
            list.Label("Excavation and flow");
            DrawSectionReset(list, new[] { "depthEngineEnabled", "digToDepthEnabled", "pulseIntervalTicks", "flowPerPulse" });
            Text.Font = GameFont.Small;

            list.CheckboxLabeled("Depth engine", ref depthEngineEnabled,
                "The depth/fill engine: liquid pours into the deepest excavated cells first "
              + "and overflows from a full cell into any neighbour with room. Off: nothing "
              + "pours and a dug channel is inert earthworks. Digging still works, and a "
              + "channel still costs what it costs to cross.");

            list.CheckboxLabeled("Dig deeper", ref digToDepthEnabled,
                "Digging a channel that is already dug cuts it one level further down — "
              + "shallow, mid, deep, then SUPERDEEP. Each level costs more labour than the "
              + "last. Off: channels are one level only.");

            list.Gap();
            list.Label("Flow pulse: every " + PulseIntervalTicks + " ticks");
            pulseIntervalTicks = list.Slider(pulseIntervalTicks, 60f, 2500f);
            list.Label("How often liquid levels itself out. There is no per-tick fluid "
                     + "simulation here and there will not be one — flow happens on this "
                     + "pulse and nowhere else. A shorter pulse means livelier water and "
                     + "more work per second.");

            list.Gap();
            list.Label("Flow per pulse: " + FlowPerPulse + " level(s) per cell");
            flowPerPulse = list.Slider(flowPerPulse, 1f, 4f);
            list.Label("How many fill levels one cell can take in from its neighbours each "
                     + "pulse. Low reads as thick and slow; high reads as water.");

            list.GapLine();
            list.Label("A channel holds three visible levels of liquid, and depth decides "
                     + "how much a cell can hold. Those levels are also the unit burning "
                     + "consumes, so anything that changes the depth ladder changes how "
                     + "long a burning channel lasts. They are one number wearing two hats, "
                     + "on purpose.");
            list.GapLine();
            list.Label("Sources are terrain, not buildings: a natural liquid body is itself "
                     + "the source — a superdeep cell that is already full, which is why it "
                     + "spills into any shallower channel dug at its edge. There is nothing "
                     + "to place and nothing to tune.");

            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Unproven mechanics — OFF by default");
            DrawSectionReset(list, new[] { "liquidCorrosionEnabled", "liquidIgnitionEnabled" });
            Text.Font = GameFont.Small;
            list.Label("These came in with the liquid-types merge and have never run inside a "
                     + "live game. They are off because that is what has actually shipped, not "
                     + "because they are broken. Turn one on when you want to test it, and "
                     + "expect it to be rough.");

            list.CheckboxLabeled("Liquid corrosion", ref liquidCorrosionEnabled,
                "Standing in an acidic or caustic liquid damages a pawn and eats the apparel "
              + "it is wearing, per that liquid's registry row. UNTESTED in a running game: "
              + "it can destroy worn gear, and it acts on colonists exactly as it acts on "
              + "raiders. Off: the rule is inert and liquids are just terrain.");

            list.CheckboxLabeled("Liquid ignition", ref liquidIgnitionEnabled,
                "A flammable liquid catches fire when something hot or electrical touches it — "
              + "never spontaneously. UNTESTED in a running game, and it is a prototype rather "
              + "than the finished burn model FlowWorks owes. Off: flammable liquids sit there.");

            // ══════════════════════════════════════════════════════════════
            // PHASE 4 SECTION — kept whole and kept last, see the field block.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Stock, recession and drainage");
            DrawSectionReset(list, new[] { "fillInEnabled", "fillInDisplacementEnabled", "sourceBudgetEnabled", "sourceBudgetMultiplier", "stickyLimitlessEnabled", "minLimitlessBodyCells", "recessionEnabled", "recedeKeepsLastCell", "refillEnabled", "refillRateMultiplier", "rainFillsExcavationsEnabled", "rainFillPerPulse", "excavationLoadRepairEnabled", "legacyFillFallbackEnabled", "legacyFloodViaEngineEnabled", "edgeSinksEnabled" });
            Text.Font = GameFont.Small;
            list.Label("How much liquid a natural body actually has, what happens when a canal "
                     + "drinks it dry, and where liquid goes when you fill a channel back in. "
                     + "Everything here is on by default; turn it all off and sources are "
                     + "bottomless, nothing recedes and nothing drains, which is how the mod "
                     + "behaved before this.");

            list.CheckboxLabeled("Fill in channels", ref fillInEnabled,
                "Adds the 'fill in canal' order — the opposite of digging. Each application "
              + "raises a cell one level; taking it all the way back to the surface restores "
              + "the terrain that was there before you dug. Off: the order refuses and the "
              + "tool is inert.");

            list.CheckboxLabeled("Filling in displaces liquid", ref fillInDisplacementEnabled,
                "Liquid pushed out of a cell you are filling flows into the rest of the "
              + "channel and back into the body it came from, so the rest of the canal gets "
              + "deeper. Only what finds no room anywhere is lost, and you are told when that "
              + "happens. Off: displaced liquid is simply lost — still reported, never silent.");

            list.CheckboxLabeled("Sources have a stock", ref sourceBudgetEnabled,
                "A natural body supplies a limited amount: each of its cells is worth a few "
              + "canal cells and no more, however big the pond looks. Run it down and the "
              + "canal stops filling. Off: every source is bottomless.");

            list.Gap();
            list.Label("Source budget: " + (5f * sourceBudgetMultiplier).ToString("F1")
                     + " canal cells per source cell");
            sourceBudgetMultiplier = list.Slider(sourceBudgetMultiplier, 0.2f, 5f);
            list.Label("The trade the whole stock model turns on. Lower makes water precious and "
                     + "a canal a real commitment; higher makes ponds generous. Applies to ponds the map "
                     + "finds from now on (new ponds only): a pond already tracked keeps its stock.");

            list.CheckboxLabeled("Big bodies are limitless", ref stickyLimitlessEnabled,
                "A body that touches the map edge and is large enough is treated as fed from "
              + "off-map: it never runs down and never recedes. This is decided ONCE, the first "
              + "time you draw from it, and never revisited — so a lake cannot flicker between "
              + "limitless and limited. Off: every body is limited, including the ocean.");

            list.Gap();
            list.Label("Smallest limitless body: " + MinLimitlessBodyCells + " cells");
            minLimitlessBodyCells = list.Slider(minLimitlessBodyCells, 1f, 400f);
            list.Label("A body must touch the map edge AND be at least this big to count as "
                     + "limitless. Raise it to make even edge-clipping ponds exhaustible.");

            list.CheckboxLabeled("Bodies recede when drawn down", ref recessionEnabled,
                "A limited body that has been spent gives up cells from its outer edge inward, "
              + "so you can see it shrinking. The original terrain of every cell it gives up is "
              + "recorded and handed back when the water returns — a receding pond never "
              + "permanently changes your map. Off: the stock runs down invisibly.");

            list.CheckboxLabeled("A body keeps its last cell", ref recedeKeepsLastCell,
                "While a receding body still holds any liquid at all, its last cell stays wet, so "
              + "the final dregs can still be drawn instead of sitting invisible until it refills. "
              + "Off: a body gives up a cell whenever it cannot pay for it in full, down to nothing.");

            list.CheckboxLabeled("Bodies refill", ref refillEnabled,
                "Seepage, rain and the season slowly put liquid back into a limited body, and "
              + "its cells come back in the order it gave them up. A very small seep takes "
              + "multiple seasons. Off: what you spend is gone for good.");

            list.Gap();
            list.Label("Refill speed: " + refillRateMultiplier.ToString("F2") + "x");
            refillRateMultiplier = list.Slider(refillRateMultiplier, 0.1f, 5f);
            list.Label("Slow and certain is the intent, not random. At 1x a one-cell seep needs "
                     + "the better part of a year to refill what it can support.");

            list.CheckboxLabeled("Rain fills open excavations", ref rainFillsExcavationsEnabled,
                "Rain falls into any excavated cell that is NOT roofed. Roof a pit and it stays "
              + "dry in a downpour — that is the point, and it makes roofing a real decision. "
              + "Off: weather never touches a channel.");

            list.Gap();
            list.Label("Rain fill speed: " + rainFillPerPulse.ToString("F2") + " level(s) per pulse");
            rainFillPerPulse = list.Slider(rainFillPerPulse, 0.01f, 1f);
            list.Label("How fast heavy rain fills an open trench. At the default a downpour takes "
                     + "roughly an in-game hour to add one level.");

            list.CheckboxLabeled("Repair dig data on load", ref excavationLoadRepairEnabled,
                "When a map loads, depth is held to 0-4, liquid never exceeds depth, and liquids "
              + "no cell uses are dropped from the map's list (one log line says what changed). "
              + "Takes effect the next time a map loads. Off: saves load exactly as stored.");

            list.CheckboxLabeled("Old channels fill back to nearby ground", ref legacyFillFallbackEnabled,
                "A channel dug before FlowWorks recorded what was under it has nothing to restore when "
              + "you fill it in. It gets the commonest ground around it (soil if there is none) instead "
              + "of staying an empty trench. Off: such a cell keeps the trench terrain.");

            list.CheckboxLabeled("Spilled liquid fills channels properly", ref legacyFloodViaEngineEnabled,
                "A spill or release that runs into a dug channel fills it the same way a pump does, so the "
              + "channel owns that liquid and it flows on with the rest. Off: the spill lies on top as a "
              + "temporary puddle that dries on its own timer, and can clash with the channel's own liquid.");

            list.CheckboxLabeled("Map-edge sinks drain", ref edgeSinksEnabled,
                "A channel dug into the strip along the map edge is a drain: liquid reaching it "
              + "leaves the map. It is not destroyed — it goes where an edge-touching lake's "
              + "water comes from. This also lets you dig in that strip at all, which the game "
              + "normally refuses. Off: the edge strip is undiggable again and nothing drains.");

            // ── LIQUID_HEAT_PUSH_1: hot and icy liquid ──────────────────────
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Hot and icy liquid");
            DrawSectionReset(list, new[] { "liquidHeatPushEnabled", "liquidHeatStrength" });
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("Boiling and icy liquid warm or chill the room they are in", ref liquidHeatPushEnabled,
                "Boiling water (and any hot liquid) warms the room it stands in, the same way a heater does; icy water "
              + "chills it. A roofed hut over a boiling pool is warm, and a closed pit flooded with a hot liquid becomes "
              + "a heat trap. Outdoors nothing changes: like a heater, the open air takes no heat. A room levels off at "
              + "50 C (hot) or 0 C (icy). Takes effect within a few seconds. Off: liquid never changes the air.");
            if (liquidHeatPushEnabled)
            {
                list.Label("Heat strength: x" + liquidHeatStrength.ToString("F2") + " (PROVISIONAL; applies now)");
                liquidHeatStrength = list.Slider(liquidHeatStrength, 0.25f, 3f);
            }

            // ── PHASE 6: fire ───────────────────────────────────────────────
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Burning liquid");
            DrawSectionReset(list, new[] { "canalFireEnabled", "canalBurnDaysPerLevel", "sourceBurnDaysPerLevel", "fireFrontSpeedMultiplier", "sourceFireReach", "explosionIgnitesLiquidEnabled", "foamSmothersLiquidFireEnabled", "rainDousesLiquidFireEnabled" });
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("Flammable liquid in channels and ponds can be lit", ref canalFireEnabled,
                "Any fire touching tar (or another burnable liquid) lights it. The fire creeps along the liquid, "
              + "back into the pond or lake that feeds it, and burns for days. Anyone standing in it catches "
              + "fire; anyone trapped in a superdeep pit always does. Off: liquid never burns.");
            if (canalFireEnabled)
            {
                list.Label("Channel burn: one fill level every " + canalBurnDaysPerLevel.ToString("F1") + " day(s)");
                canalBurnDaysPerLevel = list.Slider(canalBurnDaysPerLevel, 0.1f, 5f);
                list.Label("Source burn: one level every " + sourceBurnDaysPerLevel.ToString("F1") + " day(s)");
                sourceBurnDaysPerLevel = list.Slider(sourceBurnDaysPerLevel, 0.5f, 25f);
                list.Label("A channel three levels full burns about three times the first number. These are rates "
                  + "on the fill ladder, so changing how many levels a channel holds changes how long it burns. "
                  + "A small moat fed from a bigger unburning source can burn indefinitely; a limitless source "
                  + "burns forever.");
                list.Label("Fire front speed: x" + fireFrontSpeedMultiplier.ToString("F2"));
                fireFrontSpeedMultiplier = list.Slider(fireFrontSpeedMultiplier, 0.25f, 4f);
                list.Label("How far fire walks into a pond from where it enters: " + SourceFireReach + " cell(s)");
                sourceFireReach = list.Slider(sourceFireReach, 0f, 30f);
                list.CheckboxLabeled("Explosions light burnable liquid", ref explosionIgnitesLiquidEnabled,
                    "A flame or bomb blast lights tar, oil and the like in every cell it reaches, even where no fire "
                  + "is left burning. Off: only an actual fire lights liquid.");
                list.CheckboxLabeled("Firefoam smothers burning liquid", ref foamSmothersLiquidFireEnabled,
                    "Firefoam on a burning cell puts it out, and the cell cannot relight while the foam lies there. "
                  + "Off: foam does nothing to burning liquid.");
                list.CheckboxLabeled("Rain slowly douses burning liquid", ref rainDousesLiquidFireEnabled,
                    "Rain on an open burning cell has a small chance to put it out every second; a downpour clears an "
                  + "open channel in about half an hour, though a cell still burning beside it can relight it. "
                  + "Roofed cells are untouched. Off: rain does nothing to burning liquid.");
            }

            // ══════════════════════════════════════════════════════════════
            // PHASE 5 SECTION — kept whole and kept last, see the field block.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Pits, ladders and shooting");
            DrawSectionReset(list, new[] { "superdeepCaptureEnabled", "blastsBreakPitCovers", "superdeepCapturesOwnFaction", "ladderRequiredToExitEnabled", "ladderPrisonDoorEnabled", "ladderRaiseLowerEnabled", "pitWidthBodySizeMultiplier", "superdeepRoomsEnabled", "captureDownEnabled", "wardenFromLipEnabled", "pitDrowningEnabled", "pitDrowningRateMultiplier", "poisonFillEnabled", "pitExposureEnabled", "pitTemperatureCoupling", "pitResistanceLossMultiplier", "pitWalkNormalEnabled", "fallDamageEnabled", "fallDamageMultiplier", "spikesEnabled", "spikeDamageMultiplier", "pitDepthDrawOffsetEnabled", "pitSinkPerLevel", "excavationWallFacesEnabled", "excavationWallMaterialEnabled", "pitOutlineEnabled", "pitScorchEnabled", "pitScorchFadeDays", "pitLipOcclusionEnabled", "pitSinkClampEnabled", "pitHidesShadowEnabled", "pitLipOcclusion", "pitLipOccupantCutEnabled", "pitLipOccupantCutWidth", "liquidSurfaceMotionEnabled", "liquidWakesEnabled", "liquidLooksEnabled", "liquidBubblesEnabled", "liquidBubbleDensity", "liquidSeeThroughEnabled", "flowDoorsSealedFromPitEnabled", "sluiceLetsBigThroughEnabled", "viscosityEnabled", "thickCreepEnabled", "trapTriggerEnabled", "trapSensitivityMultiplier", "superdeepShootingRuleEnabled" });
            Text.Font = GameFont.Small;
            list.Label("A pit is any canal cell dug to superdeep, nothing more: there is no pit building. "
                     + "Everything shallower is wadeable however full it is: a brimming deep canal is "
                     + "a tax on crossing it, never a barrier, so stopping power comes from superdeep "
                     + "cells and nothing else.");

            list.CheckboxLabeled("Superdeep cells trap", ref superdeepCaptureEnabled,
                "Anyone who walks, is pushed or jumps into a superdeep cell takes a fall and, if the "
              + "pit is wide enough for them, cannot climb back out. They stay on the map, standing "
              + "on the pit floor. Off: a superdeep cell is just a very slow hole to cross.");

            list.CheckboxLabeled("Blasts break pit covers", ref blastsBreakPitCovers,
                "A bomb, grenade, mortar or fire blast that reaches a pit cover breaks the whole cover, and anyone on it "
              + "falls in. EMP, smoke and stun blasts do not. Off: only weight springs a cover.");

            list.CheckboxLabeled("Your own pit takes your own people", ref superdeepCapturesOwnFaction,
                "Off (the default), a superdeep cell ignores your own colonists unless they jump in, "
              + "otherwise nobody could ever get down there to build the ladder. On, the ground does "
              + "not care whose side you are on.");

            list.CheckboxLabeled("A ladder is needed to get out", ref ladderRequiredToExitEnabled,
                "On, a pit holds whoever is in it until a ladder stands in their cell: pull the "
              + "ladder and they are stranded. Off: a pit still costs the fall, but anyone can walk "
              + "back out.");

            list.CheckboxLabeled("A ladder works like a prison door", ref ladderPrisonDoorEnabled,
                "On, a lowered ladder lets your people and friendly visitors climb out but not trapped "
              + "enemies or wild animals, and prisoners only during a prison break. Off: any lowered ladder "
              + "lets anyone climb out.");

            list.CheckboxLabeled("Ladders can be raised and lowered", ref ladderRaiseLowerEnabled,
                "On, each ladder has a Ladder up / Ladder down button. Lowered, people can climb down into the pit "
              + "and back up it, and haulers fetch what lies on the pit floor. Raised, nobody climbs it either way. "
              + "Colonists never move a ladder themselves. Off: every ladder stays lowered and has no button.");

            list.Label("How wide a pit must be to hold a creature (body size multiplier): "
                     + pitWidthBodySizeMultiplier.ToString("F2"), tooltip:
                "A creature is held only if a square of superdeep cells as wide as it is contains its "
              + "cell. Width = round(square root of body size x this). At 1.00 a one-cell pit holds "
              + "anything under body size 2.25 (a human), a 2x2 pit anything under 6.25, a 3x3 pit "
              + "anything under 12.25. A creature too big for its pit walks out.");
            pitWidthBodySizeMultiplier = list.Slider(pitWidthBodySizeMultiplier, 0.25f, 4f);

            bool roomsWas = superdeepRoomsEnabled;
            list.CheckboxLabeled("An enclosed pit is its own room", ref superdeepRoomsEnabled,
                "A superdeep area with ordinary ground all round it counts as a room of its own, separate "
              + "from the ground above, so it has its own temperature and can hold prisoners. Bare, it holds "
              + "trapped enemies; put a prisoner bed in it and it is a prison cell. Shallower cuts never "
              + "make rooms. Off: a pit is part of whatever room surrounds it (rooms are rebuilt at once).");
            if (roomsWas != superdeepRoomsEnabled)
            {
                RM_PitRooms.RebuildAllMaps();
            }
            if (superdeepRoomsEnabled)
            {
                list.CheckboxLabeled("Capture down from the lip", ref captureDownEnabled,
                    "Right-click a trapped person in a pit that has a prisoner bed: a colonist walks to the edge "
                  + "and takes them prisoner from above, without climbing in. Only someone the pit actually holds "
                  + "(a creature too wide for it is not trapped). Off: no capture-down order.");
            }
            list.CheckboxLabeled("Wardens and doctors work from the lip", ref wardenFromLipEnabled,
                "Recruiting, converting, enslaving, wearing down, interrogating, tending and bringing food to "
              + "someone in a pit is done from the edge: food is dropped down onto its spot, talk happens "
              + "within speaking distance, tending from a cell touching them. Only if no edge cell will do "
              + "does the colonist climb down as usual. Off: they always climb down.");

            list.CheckboxLabeled("A flooded pit drowns whoever cannot swim", ref pitDrowningEnabled,
                "Any liquid in a superdeep cell drowns a trapped non-swimmer, faster the fuller it is "
              + "(about an hour when brimming). Swimming creatures tread water. Off: liquid in a pit is harmless.");
            if (pitDrowningEnabled)
            {
                list.Label("Drowning speed: x" + pitDrowningRateMultiplier.ToString("F2"));
                pitDrowningRateMultiplier = list.Slider(pitDrowningRateMultiplier, 0.1f, 5f);
            }
            list.CheckboxLabeled("Poisonous liquid poisons whoever stands in it", ref poisonFillEnabled,
                "A poison liquid builds up toxins in anyone standing in it, more the fuller the cell. "
              + "Toxic resistance helps. Off: poison is just another liquid.");
            list.CheckboxLabeled("An open pit wears down whoever is left in it", ref pitExposureEnabled,
                "An unroofed pit room tracks outdoor temperature faster, and a prisoner left in it gains pit "
              + "exposure and loses recruitment resistance. Off: a pit room behaves like any room.");
            if (pitExposureEnabled)
            {
                list.Label("Pit temperature coupling: x" + pitTemperatureCoupling.ToString("F1"));
                pitTemperatureCoupling = list.Slider(pitTemperatureCoupling, 1f, 6f);
                list.Label("Resistance loss rate: x" + pitResistanceLossMultiplier.ToString("F2"));
                pitResistanceLossMultiplier = list.Slider(pitResistanceLossMultiplier, 0f, 4f);
            }

            list.CheckboxLabeled("Walking along a pit floor is normal speed", ref pitWalkNormalEnabled,
                "Only climbing into or out of a cut is slow (the deeper, the slower; a ladder too); walking around "
              + "inside one, at one depth, is ordinary walking, and dropping into a superdeep pit is instant. "
              + "Off: every step on dug ground costs its depth, as before.");
            list.CheckboxLabeled("Falling into a pit deals damage", ref fallDamageEnabled,
                "Anyone who walks, is pushed or jumps into a superdeep cell takes blunt damage scaled "
              + "by their mass. Off: the fall is harmless.");
            if (fallDamageEnabled)
            {
                list.Label("Fall damage multiplier: " + fallDamageMultiplier.ToString("F2"));
                fallDamageMultiplier = list.Slider(fallDamageMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Spikes on a pit floor stab whoever drops in", ref spikesEnabled,
                "Spikes built on the floor of a superdeep pit stab anyone who falls, is pushed or jumps "
              + "into that cell: three Sharp hits through armour, bigger for bigger creatures. Never on "
              + "walking up to the edge or moving along the pit floor. Off: spikes are harmless.");
            if (spikesEnabled)
            {
                list.Label("Spike damage multiplier: " + spikeDamageMultiplier.ToString("F2"));
                spikeDamageMultiplier = list.Slider(spikeDamageMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Pawns sink into dug channels and rise out of them", ref pitDepthDrawOffsetEnabled,
                "A pawn standing in a dug cell is drawn lower the deeper the cell, and rises smoothly as it "
              + "walks out, so every depth reads at a glance. Drawing only: it changes nothing about "
              + "movement, sight or shooting. Off: pawns are drawn at ground level everywhere.");
            if (pitDepthDrawOffsetEnabled)
            {
                list.Label("Sink per depth level (cells): " + pitSinkPerLevel.ToString("F2")
                  + "  (superdeep: " + (pitSinkPerLevel * 4f).ToString("F2") + ")");
                pitSinkPerLevel = list.Slider(pitSinkPerLevel, 0.05f, 0.5f);
            }

            bool wallsWas = excavationWallFacesEnabled;
            list.CheckboxLabeled("Dug cells show their walls", ref excavationWallFacesEnabled,
                "Every cut draws the faces of its banks the way you would see them from above and to the south: the far "
              + "(north) bank's face is a band that grows taller and darker the deeper the cut, and the side banks show "
              + "as narrow faces. Liquid standing in a cut covers the foot of its walls. Drawing only. Off: a dug cell "
              + "shows only its ground.");
            bool matWas = excavationWallMaterialEnabled;
            if (excavationWallFacesEnabled)
            {
                list.CheckboxLabeled("  Walls look like the ground they are cut through", ref excavationWallMaterialEnabled,
                    "A cut's walls are drawn the way the game draws its own walls from above: a lit face with a dark rim, "
                  + "made of the ground beside it, earth beside soil and that rock's stone beside rock. A cut deep enough "
                  + "to hold a person shows a wall-height face, the deepest cut a taller one. Drawing only. Off: the plain "
                  + "earth-coloured band.");
            }
            bool outlineWas = pitOutlineEnabled;
            if (excavationWallFacesEnabled)
            {
                list.CheckboxLabeled("  Cuts are outlined, darkest along the near edge", ref pitOutlineEnabled,
                    "Every cut gets a closed dark outline so you can see where it is: a thin line on the far and side "
                  + "banks and a heavy dark lining on the near (south) edge that grows with depth. Shows even when "
                  + "liquid fills the cut. Drawing only.");
            }
            bool scorchWas = pitScorchEnabled;
            list.CheckboxLabeled("A cut that burned dry looks scorched", ref pitScorchEnabled,
                "After a liquid fire burns a cut dry, it stays an empty pit with charred walls, an ash floor and a scorch "
              + "ring round the rim, until it is refilled or filled in, or the scorch fades. Drawing only. Off: a burned "
              + "cut looks like any other.");
            if (pitScorchEnabled)
            {
                list.Label("Scorch fades after (days, 0 = never): " + pitScorchFadeDays.ToString("F0") + "  (rain on it: three times as fast)");
                pitScorchFadeDays = Mathf.Round(list.Slider(pitScorchFadeDays, 0f, 60f));
            }
            if (wallsWas != excavationWallFacesEnabled || matWas != excavationWallMaterialEnabled || scorchWas != pitScorchEnabled
                || outlineWas != pitOutlineEnabled)
            {
                SectionLayer_RMExcavationWalls.RedrawAll();
            }
            if (pitDepthDrawOffsetEnabled)
            {
                list.CheckboxLabeled("The near edge of a cut hides whoever stands deep in it", ref pitLipOcclusionEnabled,
                    "Seen from above and to the south, the near bank is in front of a pawn standing deep in a cut, so the "
                  + "part of them below its edge is hidden behind it. Drawing only.");
                list.CheckboxLabeled("Hold a deep pawn inside the cut's near edge", ref pitSinkClampEnabled,
                    "Stops a big sprite from drawing outside the cut on the south side, but also caps how far everyone sinks on that row. Off by default. Drawing only.");
                list.CheckboxLabeled("No ground shadow under someone down in a cut", ref pitHidesShadowEnabled,
                    "A person or animal standing in a cut has no shadow drawn on the ground under them, so it cannot "
                  + "show through the near bank. Drawing only. Off: the game's usual shadow.");
                if (pitLipOcclusionEnabled)
                {
                    list.Label("How much it hides: " + pitLipOcclusion.ToStringPercent() + "  (100% = completely; less leaves a faint outline)");
                    pitLipOcclusion = list.Slider(pitLipOcclusion, 0.5f, 1f);
                    list.CheckboxLabeled("Keep whoever is in the cut visible", ref pitLipOccupantCutEnabled,
                        "Cuts a window through the near edge's cover where someone stands, at every depth, so they can always be found. "
                      + "The cover still hides their sides. Drawing only. Off: the cover hides them as above.");
                    if (pitLipOccupantCutEnabled)
                    {
                        list.Label("Window width: " + pitLipOccupantCutWidth.ToString("0.0") + " cells");
                        pitLipOccupantCutWidth = list.Slider(pitLipOccupantCutWidth, 0.5f, 2.5f);
                    }
                }
            }
            list.CheckboxLabeled("Extra sheen on liquids that have one", ref liquidSurfaceMotionEnabled,
                "A drifting film drawn over the few liquids whose look asks for one (oil's rainbow sheen). "
              + "Drawing only. Off: no film.");
            list.CheckboxLabeled("Wakes behind anything wading", ref liquidWakesEnabled,
                "Anything walking through a liquid in a cut leaves a V-shaped wake, strong in water and faint in thick "
              + "liquids. Drawing only.");
            bool looksWas = liquidLooksEnabled;
            list.CheckboxLabeled("Each liquid has its own surface", ref liquidLooksEnabled,
                "Water looks and moves like the game's own shallow water (tinted for brine, toxic or acid water, "
              + "steaming when boiling); tar, oil and slime are thick dark liquids that slowly creep and shine. "
              + "Each liquid's look is part of its definition. Drawing only. Off: every liquid is a flat tinted water.");
            if (looksWas != liquidLooksEnabled)
            {
                if (liquidLooksEnabled) RM_LiquidLooks.ApplyAll(); else RM_LiquidLooks.RevertAll();
            }
            list.CheckboxLabeled("Acid, slime and boiling liquid bubble", ref liquidBubblesEnabled,
                "Bubbles rise and pop on the liquids that have them: lightly on slime, steadily on acid, hard on "
              + "boiling water. Drawing only. Off: no bubbles.");
            if (liquidBubblesEnabled)
            {
                list.Label("How many bubbles: x" + liquidBubbleDensity.ToString("F1"));
                liquidBubbleDensity = Mathf.Round(list.Slider(liquidBubbleDensity, 0.2f, 3f) * 10f) / 10f;
            }
            bool seeWas = liquidSeeThroughEnabled;
            list.CheckboxLabeled("See the floor and walls of a cut through clear liquid", ref liquidSeeThroughEnabled,
                "Water and other clear liquids standing in a cut let its floor and drowned walls show through, "
              + "fainter the deeper it is. Tar, oil, slime and blood stay opaque. Drawing only. Off: the liquid "
              + "surface hides the cut below it.");
            if (seeWas != liquidSeeThroughEnabled)
            {
                SectionLayer_RMExcavationWalls.RedrawAll();
            }
            list.Gap(6f);
            list.Label("Liquids that can fill a cut (off: nothing pours that liquid into a cut — pump, drill or any "
                     + "other source; what already stands in one stays):");
            foreach (FluidDef fd in DefDatabase<FluidDef>.AllDefsListForReading)
            {
                bool on = FluidAllowed(fd);
                bool was = on;
                list.CheckboxLabeled("  " + fd.LabelCap, ref on, "Lets " + fd.label + " stand in a dug cut.");
                if (on != was)
                {
                    if (on) disabledFluids.Remove(fd.defName); else if (!disabledFluids.Contains(fd.defName)) disabledFluids.Add(fd.defName);
                }
            }

            list.CheckboxLabeled("Sluices and grates cannot be opened from inside a pit", ref flowDoorsSealedFromPitEnabled,
                "A pawn held in a superdeep pit cannot open a sluice or a security grate, even one it "
              + "could open from outside. Off: they open like ordinary doors for anyone allowed through.");
            list.CheckboxLabeled("A sluice only holds small creatures", ref sluiceLetsBigThroughEnabled,
                "A sluice is a cheap gate: people (prisoners and raiders included) and any creature too big "
              + "for a one-wide pit force their way through it. Use a security grate to hold a real "
              + "prisoner. Both pass liquid while closed either way. Off: a sluice holds like an ordinary door.");
            list.CheckboxLabeled("Thick liquids flow slower than water", ref viscosityEnabled,
                "Tar, slime and oil creep along a channel: each level waits several pulses before it moves "
              + "on (oil 3, tar 6, slime 8 pulses to water's 1), so a tar channel fills far behind a water "
              + "one dug beside it. Off: every liquid flows at water's pace.");
            list.CheckboxLabeled("Thick liquids creep one cell at a time", ref thickCreepEnabled,
                "Needs 'Thick liquids flow slower'. On: tar, slime and blood advance one cell each time they move, "
              + "so a long channel fills at its stated speed instead of all at once on one pulse. Water is not "
              + "affected. Off: a thick liquid that reaches a cell can pass on to the next in the same pulse.");

            list.CheckboxLabeled("Pit covers give way under enough weight", ref trapTriggerEnabled,
                "An armed cover over a pit drops whoever stands on it once their combined mass passes "
              + "the cover's rating. Off: covers never give way on their own.");
            if (trapTriggerEnabled)
            {
                list.Label("Cover sensitivity multiplier: " + trapSensitivityMultiplier.ToString("F2"));
                trapSensitivityMultiplier = list.Slider(trapSensitivityMultiplier, 0.25f, 3f);
            }

            list.CheckboxLabeled("Superdeep limits who can shoot whom", ref superdeepShootingRuleEnabled,
                "Someone standing in a superdeep hole can only trade fire with whoever is in one "
              + "of the eight cells touching theirs, and that cuts both ways: a turret cannot "
              + "shoot into the hole unless it is right at the lip, and whoever is down there can "
              + "still shoot anyone who comes to the edge. It is a restriction only — nothing here "
              + "changes accuracy, cover or sight. Off: depth never affects shooting at all.");

            // ══════════════════════════════════════════════════════════════
            // LIQUID_BOTTLE_LOOP_1 SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Bottles, buckets, barrels: fill, use, wash");
            DrawSectionReset(list, new[] { "bottleLoopEnabled", "bottleDirtyStageEnabled", "bottleRevertEnabled" });
            Text.Font = GameFont.Small;
            list.Label("An empty container filled at a matching liquid's shore becomes a filled one; "
                     + "drinking or otherwise using one leaves a container behind to deal with. Buckets "
                     + "hold five bottles' worth, barrels twenty-five — same chain, same labour. "
                     + "Containers are loot, not free.");

            list.CheckboxLabeled("Container fill/wash labour", ref bottleLoopEnabled,
                "Colonists automatically carry an empty bottle, bucket or barrel to a matching liquid's "
              + "edge to fill it, and a dirty one to fresh water to wash it — no order needed, the same "
              + "way an empty fuel tank is a standing invitation to refuel. Off: containers still fill "
              + "and empty by hand if you carry and drink them yourself, but nothing does the fetching "
              + "for you.");

            list.CheckboxLabeled("Using a container leaves it dirty", ref bottleDirtyStageEnabled,
                "Drinking a filled bottle or bucket leaves a dirty one that needs washing before it can "
              + "be filled again — the shipped campaign behaviour. Off: drinking returns a clean empty "
              + "container directly and no dirty ones are minted; any a save already holds are still "
              + "washable. Barrels are the bulk trade good and are never drunk from directly.");

            list.CheckboxLabeled("Bottled boiling or icy water returns to normal", ref bottleRevertEnabled,
                "A bottle, bucket or barrel filled with boiling water cools to fresh water, and one filled with "
              + "icy water warms to it, after a while (each liquid's own timer — about an hour for boiling, two for "
              + "icy). Off: bottled liquid keeps the state it was filled in.");

            // ══════════════════════════════════════════════════════════════
            // LIQUID_BOTTLE_LOOP_1 TANK SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("The liquid tank");
            DrawSectionReset(list, new[] { "tankLoopEnabled", "tankCapacityMultiplier", "liquidPumpEnabled" });
            Text.Font = GameFont.Small;
            list.Label("A patched-together scavenger tank: a big fixed store of ONE liquid at a "
                     + "time, filled by pouring a container in and drained by filling a container "
                     + "from it. The same fetch-labour pattern as the fill/wash loop above.");

            list.CheckboxLabeled("Tank pour/draw labour", ref tankLoopEnabled,
                "Colonists automatically carry a filled container to a tank that can take its "
              + "contents, and an empty container to a tank holding enough to fill it — no order "
              + "needed. Off: a tank already built keeps whatever it holds and can still be worked "
              + "by hand-carrying, but nothing fetches for you.");

            list.Gap();
            list.Label("Tank capacity: " + Mathf.RoundToInt(300f * tankCapacityMultiplier) + " units");
            tankCapacityMultiplier = list.Slider(tankCapacityMultiplier, 0.2f, 5f);
            list.Label("Every RM_LiquidTank ships holding this many units at 1x. Raise it for a "
                     + "colony that wants to stockpile; lower it to keep a tank a modest buffer "
                     + "rather than a warehouse.");

            list.CheckboxLabeled("Liquid pumps run", ref liquidPumpEnabled,
                "A powered pump set beside a liquid tank either draws liquid from the pond, lake or dug channel beside "
              + "it into the tank, or pours the tank into a dug channel beside it — one channel level (five tank "
              + "units) every few seconds. A pond it draws from runs down like any other use. Off: pumps sit idle "
              + "and draw no power.");

            // ══════════════════════════════════════════════════════════════
            // MANY_WATERS_DRILL_BUILDINGS_1 SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Drilling and tapping");
            DrawSectionReset(list, new[] { "liquidDrillingEnabled", "drillYieldChanceMultiplier", "drillUnitsPerCycle" });
            Text.Font = GameFont.Small;
            list.Label("The fourth acquisition route: some maps sit on a liquid you never see "
                     + "the surface of. A drill (powered) or a tap (hand-worked, smaller) pours "
                     + "whatever a subsurface survey found into a dug channel at its outlet, "
                     + "drawing down a fixed reserve that never refills. Every map is surveyed "
                     + "once, quietly, whether or not you ever build one.");

            list.CheckboxLabeled("Drilling and tapping", ref liquidDrillingEnabled,
                "Master switch for the whole route. Off: a built drill or tap sits there inert, "
              + "consuming no power and producing nothing — the underlying survey still runs so "
              + "flipping this back on does not need a new game.");

            list.Gap();
            list.Label("How often a map has anything down there: " + drillYieldChanceMultiplier.ToString("F2") + "x");
            drillYieldChanceMultiplier = list.Slider(drillYieldChanceMultiplier, 0.1f, 3f);
            list.Label("Scales every biome's own odds of yielding a drillable liquid at all. "
                     + "1x is what the biome was authored with; raise it to make 'the right "
                     + "maps' common, lower it to make a real find rare. Rolled once when a map is "
                     + "first surveyed (new maps only); a map you already have keeps its answer.");

            list.Gap();
            list.Label("Extraction rate: " + DrillUnitsPerCycle.ToString("F2") + " fill-unit(s) per cycle");
            drillUnitsPerCycle = list.Slider(drillUnitsPerCycle, 0.1f, 6f);
            list.Label("How much a drill (or a slower tap, scaled down per building) can pull "
                     + "from the ground every 250 ticks once its outlet has room to take it. "
                     + "The reserve it draws from is finite and never comes back.");

            // ══════════════════════════════════════════════════════════════
            // WORLDMAP_LIQUID_TAGS_1 SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Typed bodies of water");
            DrawSectionReset(list, new[] { "typedLiquidShoresEnabled" });
            Text.Font = GameFont.Small;
            list.Label("Some named seas and lakes on the planet are made of something other "
                     + "than plain water — brine, boiling water, liquid propane. Landing on "
                     + "one finds that liquid underfoot instead of generic blue water. Water "
                     + "that has not been given a type is untouched, and always was.");

            list.CheckboxLabeled("Landing repaints typed water  (affects newly generated maps)",
                ref typedLiquidShoresEnabled,
                "On: a map generated on a tile belonging to a typed body has its lake and sea "
              + "water repainted to that body's own liquid. Rivers are never repainted — a "
              + "river feeding a brine sea is still fresh — and neither is shore sand. Off: "
              + "every map generates exactly as it would without this mod. Either way, a map "
              + "you have already generated keeps the terrain it was generated with.");

            // ── FLOWWORKS_QUARRY_DIGGING_1 — what a canal cut turns up ────
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Finds while digging");
            DrawSectionReset(list, new[] { "digFindsEnabled", "digFindsLocalOnly", "digFindChanceMultiplier", "digFindBudgetPercent", "digFindLetterEnabled" });
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("Digging a canal can turn up minerals", ref digFindsEnabled,
                "Each time a cell is cut a level deeper there is a small chance of a lump of something the land holds, "
              + "thrown up onto the bank. Deep and superdeep cuts can reach what a deep drill would find under that cell. "
              + "Where the land holds nothing, you get chunks of the local rock. Filling a cell in and digging it again "
              + "pays nothing twice. Off: digging only digs.");
            if (digFindsEnabled)
            {
                list.CheckboxLabeled("Finds come only from this map's own rock", ref digFindsLocalOnly,
                    "On: a find is one of the ores actually in this map's rock (or under the cell, for a deep cut). "
                  + "Off: any ore the game knows can turn up. Components and plasteel never come out of a hole either way.");
                list.Label("Find chance: x" + digFindChanceMultiplier.ToString("F2") + "  (1x = 1.5% per cut; first-guess number)");
                digFindChanceMultiplier = list.Slider(digFindChanceMultiplier, 0f, 10f);
                list.Label("Loose-find ceiling: " + digFindBudgetPercent.ToString("F1") + "% of the ore in this map's rock");
                digFindBudgetPercent = list.Slider(digFindBudgetPercent, 0f, 50f);
                list.Label("Once a map's share is dug out, cuts only turn up rock. Set when the map first finds something.");
                list.CheckboxLabeled("A letter on the first find of each material", ref digFindLetterEnabled,
                    "The first time a material turns up on a map you get a letter saying the land holds it; later finds "
                  + "are a short message. Off: messages only.");
            }

            // ── CRACKEDLANDS_MECHANICS_BUILD_1 §1 — the swale ─────────────
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Swales");
            DrawSectionReset(list, new[] { "swaleEnabled", "swaleRateMultiplier" });
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("A watered swale enriches the ground around it", ref swaleEnabled,
                "On: a swale laid in a dug channel, while its own cell carries water (a fill, a flood "
              + "or a natural source), slowly turns the ground within two cells one step richer — "
              + "sand to soil to rich soil, never past rich soil, never while dry. Off: a built "
              + "swale does nothing; ground it already improved stays improved.");
            list.Label("Swale pace: " + SwaleRateMultiplier.ToString("F2") + "x  (1x = one step per fed day; first-guess number)");
            swaleRateMultiplier = list.Slider(swaleRateMultiplier, 0.1f, 10f);

            // ── Rivers (River Works, merged 2026-10-05) ───────────────────
            Rivers.RM_RiversSettingsWindow.DoSettingsSection(list);
            Machinery.RM_MachinerySettings.DoSettingsSection(list);
            Machinery.Logistics.RM_TankerSettings.DoSettingsSection(list);
            Machinery.Logistics.RM_SluiceGateSettings.DoSettingsSection(list);
            Machinery.Logistics.RM_BloodDrawSettings.DoSettingsSection(list);
            Machinery.Kits.RM_KitSettings.DoSettingsSection(list);
            Quarry.RM_QuarrySettings.DoSettingsSection(list);

            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RimMandrakeFlowWorksMod : Mod
    {
        public static RimMandrakeFlowWorksSettings settings;

        public RimMandrakeFlowWorksMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RimMandrakeFlowWorksSettings>();
        }

        public override string SettingsCategory()
        {
            // Grouped by origin: three Mod classes ship in this one assembly
            // (RimWorld instantiates every Mod subclass it finds, one screen
            // each — LoadedModManager.CreateModClasses), so they are named to
            // sort together in the settings list.
            return "FlowWorks: Excavation & Flow";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
            RimMandrake.Shared.PatchApplier.ReforceOff();
        }
    }
}
