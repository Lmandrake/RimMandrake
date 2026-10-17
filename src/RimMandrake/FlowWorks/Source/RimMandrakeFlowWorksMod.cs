using UnityEngine;
using Verse;

// The JawaBench bridge companion (bridgetools/JawaBench.BridgeTools) drives this mod's internal cord geometry types
// (_Shared/SlackGeometry is internal in each assembly since the hose port).
[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("JawaBench.BridgeTools")]

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

        // ── UNPROVEN MECHANICS, ON BY DEFAULT (owner decision 2026-10-15) ─
        // These two came in with the 2026-09-16 LiquidTypes merge and had
        // never run in a live game (LIQUID_TYPES_SPIKES_1 of the ignition
        // prototype: "has never ticked inside a running game"). They shipped
        // OFF until the owner turned them ON for release (b5c8547e8b); the
        // settings screen still labels them unproven.
        //
        // Gated at the top of each MapComponentTick rather than by dropping
        // the component: a MapComponent is scribed per map, and removing one
        // that a save already carries is a save-compat problem. Off means it
        // ticks and returns; the component still exists, still loads, and
        // flipping the toggle needs no new game.
        //   9. liquidCorrosionEnabled  — LiquidCorrosionMapComponent
        //  10. liquidIgnitionEnabled   — LiquidIgnitionMapComponent
        public static bool liquidCorrosionEnabled = true;
        public static bool liquidIgnitionEnabled = true;
        // FLOWWORKS_BUILD_PROGRAM_1 Phase 6 — fire on the depth/fill engine (RM_LiquidFire). Ruling 7: burning is a RATE.
        // LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §5.6, D3 defaulted, veto-able): ONE rate for every burning
        // square, canal or pond, 0.5 m a day; front speed and source reach are PROVISIONAL.
        public static bool canalFireEnabled = true;
        // LIQUID_HEAT_PUSH_1: hot/icy liquid warms or chills its room through vanilla heat (strength PROVISIONAL).
        public static bool liquidHeatPushEnabled = true;
        // FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW: fixes a vanilla water-body count bug when water changes type.
        public static bool waterBodyTypeFlipFixEnabled = true;
        public static float liquidHeatStrength = 1f;
        public static float burnDaysPerNotch = 1f;
        public static float fireFrontSpeedMultiplier = 1f;
        public static float sourceFireReach = 3f;
        public static bool explosionIgnitesLiquidEnabled = true;
        public static bool foamSmothersLiquidFireEnabled = true;
        public static bool rainDousesLiquidFireEnabled = true;
        // CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15): chemfuel burns as a moat of gasoline, astrofuel
        // detonates as one chained blast. Both on by default; dials PROVISIONAL (RM_FuelFireMath holds the numbers).
        public static bool chemfuelInfernoEnabled = true;
        public static float chemfuelIntensity = 1f;
        public static float chemfuelSpreadSpeed = 1f;
        public static float chemfuelBurnRate = 1f;
        public static bool astrofuelDetonationEnabled = true;
        public static float astrofuelBlastScale = 1f;
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
        //  13. sourceBudgetEnabled        — a pond holds what its floor holds; off = limitless all
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
        // PROVISIONAL (auto-decided 2026-10-09, POND_RECESSION_STRANDS_CHANNEL_1): cells feeding a dug channel recede last.
        public static bool recedeSparesOutflow = true;
        public static bool refillEnabled = true;
        // POND_RETURN_LEG_BUILD_WATER_GOES_HOME (owner rulings 5/6, 2026-10-12): pumps and outflows refill natural ponds;
        // refill waits for pawns and buildings (items wash ashore); a dug dry bed square leaves its pond, filled back in it returns.
        public static bool pondReturnLegEnabled = true;
        public static bool refillWaitsForOccupants = true;
        public static bool dugBedLeavesPondEnabled = true;
        // POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2 (owner rulings 2-4, look (b) by card 2026-10-13): a drained pond square is a
        // hollow at its bed depth (2 shallow, 4 deep), laid as cracked lakebed; a canal above a bed's floor runs back into the pond.
        public static bool pondBedHollowEnabled = true;
        /// <summary>LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (owner by card 2026-10-16): the bottom-left cell readout shows the
        /// liquid standing in the square, metres deep and litres (RM_Patch_MouseoverDepth). Off: vanilla's line only.</summary>
        public static bool mouseoverDepthEnabled = true;
        // POND_ELEVATION_BUILD_LAKES_RUN_DEEP (owner by card 2026-10-15, "Build it today"; design §9): a lake's deep middle runs
        // deeper than 4 (one level per deepBedCellsPerLevel squares past the shore band, capped at deepBedMaxDepth), it drains
        // off its shallow rim first and refills to its exact shape; an inland lake up to drainableLakeMaxCells squares is
        // drainable (4000 = the old ocean cap). Each applies to lakes the map finds from now on; a tracked pond keeps its bed.
        public static bool deepBedsEnabled = true;
        // POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (design/RimMandrake/pond_depth_design_2026-10-16.md §9; owner by card 2026-10-16,
        // "Yes, ponds shallow out"; D2 his words "It should slosh around until it levels, pond or canal or otherwise."): a still
        // water pond keeps one flat surface and shallows all over (deep → chest-deep → shallow → thin → mud → lakebed); a pond
        // feeds a ditch only while its surface stands above the ditch's water, and a canal above a pond's surface runs back in.
        public static bool pondDepthEnabled = true;
        public static float pondMudDays = 2f;
        public static float pondStageWritesPerPulse = 400f;
        public static bool pondHeadRuleEnabled = true;
        // LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (absorbed LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES; owner D2 2026-10-17): the deepest natural
        // floor, in NOTCHES (0.5 m), shown in metres, settable up to 250 = 125 m. The floor SHAPE per lake and biome is
        // LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (R11); 20 (10 m) stays the default until that lands.
        public static float deepBedMaxDepth = 20f;
        public static float deepBedCellsPerLevel = 4f;
        public static float drainableLakeMaxCells = 40000f;
        public static bool rainFillsExcavationsEnabled = true;
        public static bool edgeSinksEnabled = true;
        // EXCAVATION_LOAD_SANITY_REPAIR_1: clamp/repair the dig grids and compact the liquid list on map load.
        public static bool excavationLoadRepairEnabled = true;
        // PROVISIONAL (auto-decided 2026-10-09, EXCAVATION_LEGACY_MIGRATION_FLAG_1): unrecorded filled-in cells get neighbour terrain.
        public static bool legacyFillFallbackEnabled = true;
        // FLOOD_DRIVER_OWNERSHIP_CONTRACT_1: a legacy flood release on an excavated cell fills it through the engine.
        public static bool legacyFloodViaEngineEnabled = true;
        // FLOW_ORDER_EXTERNAL_INPUT_1: a pump/drill-fed channel with no natural source spreads away from its input.
        public static bool pumpFedSpreadEnabled = true;
        // FLOW_ORDER_EXTERNAL_INPUT_1 part 2: a network over the partition cap moves its seams each pulse.
        public static bool networkSeamsMoveEnabled = true;
        // The partition cap. 6000 is the shipped value; raising the default waits on one in-game timing.
        public static float maxNetworkCells = 6000f;
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
        // PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP (owner 2026-10-12: "it should be relative height ... so that gradual slopes never
        // trap anyone"): a pit holds a creature when no chain of steps it can climb reaches the surface. Off = the old absolute
        // rule (any D=4 cell holds). The multiplier scales creature height for the climb bands (PROVISIONAL, design §8.2).
        public static bool pitRelativeClimbEnabled = true;
        public static float pitClimbAbilityMultiplier = 1f;
        // PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS (design §8.2, PROVISIONAL): a step of exactly K >= 2 costs this many normal climbs.
        public static float pitSlowClimbFactor = 2f;
        // PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS (design §8.4, owner 2026-10-12 Q3): a 1-square ramp spans up to 3 levels at walking speed;
        // a ladder spans any depth, this many normal climbs per level (PROVISIONAL).
        public static bool pitRampsEnabled = true;
        public static int pitRampMaxSpan = 3;
        public static float pitLadderSlowness = 2f;
        // PIT_LEGACY_CODE_RETIRE_1: the four survivors of the retired PitsMod screen
        // (same field names and defaults, so nothing that reads them changes meaning).
        // The cover's mass trigger (PIT_COVER_FALL_REWIRE_1) and the fall on any descent
        // into a D=4 cell. Struggle/escape and pit-cell exposure died with their mechanics.
        public static bool trapTriggerEnabled = true;
        public static float trapSensitivityMultiplier = 1f;
        public static bool fallDamageEnabled = true;
        public static float fallDamageMultiplier = 1f;
        // PIT_TEMPERATURE_SOFTENING_1 (redesigned 2026-10-11): exposure on/off, comfort narrowing (owner Q1: 8 C), temperature
        // coupling (kept until a live check), resistance loss rate (owner Q2: only while the elements hurt).
        public static bool pitExposureEnabled = true;
        public static float pitExposureNarrowing = 8f;   // = RM_PitExposureMath.DefaultNarrowing (a literal: the northstar settings registry parses it)
        // PIT_FILL_EFFECTS_1 (PROVISIONAL rates): drowning at D=4 with any fill (non-swimmers), poison fluid toxin keyed to fill.
        public static bool pitDrowningEnabled = true;
        public static float pitDrowningRateMultiplier = 1f;
        public static bool poisonFillEnabled = true;
        // SLIME_CROSSING_BUILD_SLIPPERY_SLOPE (PROVISIONAL): walking in slippery liquid (slime) slips, stuns and, on the climb
        // out, slides back (RM_SlimeSlip / RM_SlimeMath; defaults = RM_SlimeMath.Default*, literals for the settings registry).
        public static bool slimeSlipEnabled = true;
        public static float slimeSlipChanceMultiplier = 1f;
        public static float slimeSlipStunSeconds = 2f;
        public static float slimeClimbOutSlipFactor = 2f;
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
        public static bool pitSinkClampEnabled = true;             // ON (owner by card 2026-10-15; was off 2026-10-07): hold the sink so the drawn centre stays north of the near lip; on a south-row pit cell this caps every pawn at 0.5
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
        /// <summary>Test/script hook (jawa/static_call): switch one liquid on or off exactly as the settings checkbox does.
        /// Returns the new allowed state. Added 2026-10-09 for FLUID_DISABLE_ALL_INPUTS_1's live check: the bridge's settings
        /// tools cannot write a static List.</summary>
        public static bool SetFluidAllowed(string defName, bool on)
        {
            if (disabledFluids == null) disabledFluids = new System.Collections.Generic.List<string>();
            if (on) disabledFluids.Remove(defName); else if (!disabledFluids.Contains(defName)) disabledFluids.Add(defName);
            return !disabledFluids.Contains(defName);
        }
        public static bool pitScorchEnabled = true;                // a cut that burned dry reads scorched
        public static float pitScorchFadeDays = 20f;               // PROVISIONAL; 0 = never fades
        public static bool pitOutlineEnabled = true;               // closed dark outline, strong near (south) lining
        public static bool pitHidesShadowEnabled = true;           // no ground shadow under a pawn sunk in a cut
        // FLOWWORKS_DOOR_FAMILY_1: the sluice and security grate (two stuffable doors; a shut sluice seals, the grate passes liquid).
        public static bool flowDoorsSealedFromPitEnabled = true;
        public static bool sluiceLetsBigThroughEnabled = true;
        // FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 VISCOSITY (PROVISIONAL stride = ticksPerTile / 60): a viscous fluid's level
        // moves only every Nth pulse (tar 6, slime 8, oil 3), so its fill front lags water's.
        public static bool viscosityEnabled = true;
        // THICK_LIQUID_CREEP_1: a thick liquid's fill front moves one cell per moving pulse (a cell that just received it cannot
        // pass it on in the same pulse). Needs viscosityEnabled. PROVISIONAL: one cell per moving pulse.
        public static bool thickCreepEnabled = true;
        // CANAL_FRONT_FIX_WRONG_END_WETS_FIRST (owner 2026-10-12): water's fill front also advances one cell per pulse from the
        // mouth, like a flood front, instead of racing the whole run in one pulse. Off = the old instant race.
        public static bool waterFrontCreepEnabled = true;
        // WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND (owner 2026-10-16, by card "Level by water surface"): water moves from a
        // higher water SURFACE to a lower one whatever each square's dug depth, so a run levels out and drains to empty.
        // Off = the old rule (only into a deeper bed, or out of a brim-full square), which left deep puddles behind.
        public static bool levelBySurfaceEnabled = true;
        // WATER_LEVELSET_SOLVE (owner 2026-10-16, review station 1: "levelset down to a smooth 0 or 1 across a too-wide
        // field like this, not 0, deep, 0"). Needs levelBySurfaceEnabled. On: each wet region is solved to its flat level
        // (RM_FlowKernel.LevelSetWetRegions). Off: the one-unit-at-a-time levelling, which stripes wide fields 0,1,0,1.
        public static bool levelSetEnabled = true;
        // WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17: "We need VERY smooth water. That's water's one primary
        // characteristic: a level surface."; ruled exactly level by card). On: every dug square holds its water in decilitres
        // and each connected body (canal, pit, pond, or joined) stands at ONE surface (RM_FlowKernel.ResolveExact,
        // RM_LevelSolve); looks follow the true metres of water. Off: whole half-metre notches (the engines above).
        public static bool levelExactEnabled = true;

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
        //  26. tankCapacityMultiplier — scales every tank's footprint size (one square = one deep notch,
        //      RM_Volume.UnitsPerSquare; tall tanks twice). 1x is the shipped size; this is the
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
        // DIG_ROCK_TUNE_STONE_FIGHTS_BACK (owner 2026-10-16): digging through rock ground. PROVISIONAL numbers.
        public static bool digRockGroundEnabled = true;
        public static float digRockWorkMultiplier = 4f;
        public static bool digRockChunksEnabled = true;
        public static float digRockChunkMultiplier = 1f;
        public static float digSoilChunkPercent = 0.5f;
        public static bool swaleEnabled = true;
        public static float swaleRateMultiplier = 1f;

        public static float SwaleRateMultiplier => Mathf.Clamp(swaleRateMultiplier, 0.1f, 10f);

        public static float DrillUnitsPerCycle => Mathf.Max(0.05f, drillUnitsPerCycle);

        public static int MinLimitlessBodyCells => Mathf.Max(1, Mathf.RoundToInt(minLimitlessBodyCells));

        /// <summary>POND_DEPTH: ticks an exposed pond square stays mud before it cracks to lakebed.</summary>
        public static int PondMudTicks => Mathf.RoundToInt(Mathf.Clamp(pondMudDays, 0f, 30f) * 60000f);
        /// <summary>POND_DEPTH: terrain restages per pulse (the §8 cost guard), at least one.</summary>
        public static int PondStageWritesPerPulse => Mathf.Clamp(Mathf.RoundToInt(pondStageWritesPerPulse), 1, 5000);
        public static int DeepBedMaxDepth => Mathf.Clamp(Mathf.RoundToInt(deepBedMaxDepth), RM_Volume.LevelsPerSquare, RM_BedMath.MaxBedCeiling);
        public static int DeepBedCellsPerLevel => Mathf.Clamp(Mathf.RoundToInt(deepBedCellsPerLevel), 1, 12);
        public static int DrainableLakeMaxCells => Mathf.Clamp(Mathf.RoundToInt(drainableLakeMaxCells / 1000f) * 1000, RM_BedMath.OceanWalkCells, 62500);

        public static int PulseIntervalTicks => Mathf.Max(RM_FireMath.MinFlowPulseTicks, Mathf.RoundToInt(pulseIntervalTicks));

        public static int FlowPerPulse => Mathf.Clamp(Mathf.RoundToInt(flowPerPulse), 1, 4);
        public static int MaxNetworkCells => Mathf.Clamp(Mathf.RoundToInt(maxNetworkCells / 500f) * 500, 1000, 50000);

        public override void ExposeData()
        {
            // HARMONY_PATCH_RESILIENCE_1: a feature switched off by a failed patch is saved with the player's own value.
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref depthEngineEnabled, "depthEngineEnabled", true);
            Scribe_Values.Look(ref pulseIntervalTicks, "pulseIntervalTicks", 250f);
            Scribe_Values.Look(ref flowPerPulse, "flowPerPulse", 1f);
            Scribe_Values.Look(ref digToDepthEnabled, "digToDepthEnabled", true);
            Scribe_Values.Look(ref liquidCorrosionEnabled, "liquidCorrosionEnabled", true);
            Scribe_Values.Look(ref liquidIgnitionEnabled, "liquidIgnitionEnabled", true);
            Scribe_Values.Look(ref canalFireEnabled, "canalFireEnabled", true);
            Scribe_Values.Look(ref liquidHeatPushEnabled, "liquidHeatPushEnabled", true);
            Scribe_Values.Look(ref waterBodyTypeFlipFixEnabled, "waterBodyTypeFlipFixEnabled", true);
            Scribe_Values.Look(ref liquidHeatStrength, "liquidHeatStrength", 1f);
            // LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: one burn rate. A settings file from before it has no "burnDaysPerNotch": the old
            // canal rate (the owner's ruling-7 day) is read once under its old name; the 5-day pond rate is dropped (D3).
            Scribe_Values.Look(ref burnDaysPerNotch, "burnDaysPerNotch", -1f);
            if (Scribe.mode == LoadSaveMode.LoadingVars && burnDaysPerNotch < 0f)
            {
                burnDaysPerNotch = Scribe.loader.curXmlParent?["canalBurnDaysPerLevel"] is System.Xml.XmlNode oldCanal
                    && float.TryParse(oldCanal.InnerText, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float days)
                    ? days : 1f;
            }
            Scribe_Values.Look(ref fireFrontSpeedMultiplier, "fireFrontSpeedMultiplier", 1f);
            Scribe_Values.Look(ref sourceFireReach, "sourceFireReach", 3f);
            Scribe_Values.Look(ref explosionIgnitesLiquidEnabled, "explosionIgnitesLiquidEnabled", true);
            Scribe_Values.Look(ref foamSmothersLiquidFireEnabled, "foamSmothersLiquidFireEnabled", true);
            Scribe_Values.Look(ref rainDousesLiquidFireEnabled, "rainDousesLiquidFireEnabled", true);
            Scribe_Values.Look(ref chemfuelInfernoEnabled, "chemfuelInfernoEnabled", true);
            Scribe_Values.Look(ref chemfuelIntensity, "chemfuelIntensity", 1f);
            Scribe_Values.Look(ref chemfuelSpreadSpeed, "chemfuelSpreadSpeed", 1f);
            Scribe_Values.Look(ref chemfuelBurnRate, "chemfuelBurnRate", 1f);
            Scribe_Values.Look(ref astrofuelDetonationEnabled, "astrofuelDetonationEnabled", true);
            Scribe_Values.Look(ref astrofuelBlastScale, "astrofuelBlastScale", 1f);
            // ── Phase 4 (see the block above; kept contiguous on purpose) ──
            Scribe_Values.Look(ref fillInEnabled, "fillInEnabled", true);
            Scribe_Values.Look(ref fillInDisplacementEnabled, "fillInDisplacementEnabled", true);
            Scribe_Values.Look(ref sourceBudgetEnabled, "sourceBudgetEnabled", true);
            Scribe_Values.Look(ref stickyLimitlessEnabled, "stickyLimitlessEnabled", true);
            Scribe_Values.Look(ref recessionEnabled, "recessionEnabled", true);
            Scribe_Values.Look(ref recedeKeepsLastCell, "recedeKeepsLastCell", true);
            Scribe_Values.Look(ref recedeSparesOutflow, "recedeSparesOutflow", true);
            Scribe_Values.Look(ref refillEnabled, "refillEnabled", true);
            Scribe_Values.Look(ref pondReturnLegEnabled, "pondReturnLegEnabled", true);
            Scribe_Values.Look(ref refillWaitsForOccupants, "refillWaitsForOccupants", true);
            Scribe_Values.Look(ref dugBedLeavesPondEnabled, "dugBedLeavesPondEnabled", true);
            Scribe_Values.Look(ref pondBedHollowEnabled, "pondBedHollowEnabled", true);
            Scribe_Values.Look(ref mouseoverDepthEnabled, "mouseoverDepthEnabled", true);
            Scribe_Values.Look(ref deepBedsEnabled, "deepBedsEnabled", true);
            Scribe_Values.Look(ref pondDepthEnabled, "pondDepthEnabled", true);
            Scribe_Values.Look(ref pondMudDays, "pondMudDays", 2f);
            Scribe_Values.Look(ref pondStageWritesPerPulse, "pondStageWritesPerPulse", 400f);
            Scribe_Values.Look(ref pondHeadRuleEnabled, "pondHeadRuleEnabled", true);
            Scribe_Values.Look(ref deepBedMaxDepth, "deepBedMaxDepth", 20f);
            Scribe_Values.Look(ref deepBedCellsPerLevel, "deepBedCellsPerLevel", 4f);
            Scribe_Values.Look(ref drainableLakeMaxCells, "drainableLakeMaxCells", 40000f);
            Scribe_Values.Look(ref rainFillsExcavationsEnabled, "rainFillsExcavationsEnabled", true);
            Scribe_Values.Look(ref edgeSinksEnabled, "edgeSinksEnabled", true);
            Scribe_Values.Look(ref excavationLoadRepairEnabled, "excavationLoadRepairEnabled", true);
            Scribe_Values.Look(ref legacyFillFallbackEnabled, "legacyFillFallbackEnabled", true);
            Scribe_Values.Look(ref legacyFloodViaEngineEnabled, "legacyFloodViaEngineEnabled", true);
            Scribe_Values.Look(ref pumpFedSpreadEnabled, "pumpFedSpreadEnabled", true);
            Scribe_Values.Look(ref networkSeamsMoveEnabled, "networkSeamsMoveEnabled", true);
            Scribe_Values.Look(ref maxNetworkCells, "maxNetworkCells", 6000f);
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
            Scribe_Values.Look(ref pitRelativeClimbEnabled, "pitRelativeClimbEnabled", true);
            Scribe_Values.Look(ref pitClimbAbilityMultiplier, "pitClimbAbilityMultiplier", 1f);
            Scribe_Values.Look(ref pitSlowClimbFactor, "pitSlowClimbFactor", 2f);
            Scribe_Values.Look(ref pitRampsEnabled, "pitRampsEnabled", true);
            Scribe_Values.Look(ref pitRampMaxSpan, "pitRampMaxSpan", 3);
            Scribe_Values.Look(ref pitLadderSlowness, "pitLadderSlowness", 2f);
            Scribe_Values.Look(ref trapTriggerEnabled, "trapTriggerEnabled", true);
            Scribe_Values.Look(ref trapSensitivityMultiplier, "trapSensitivityMultiplier", 1f);
            Scribe_Values.Look(ref fallDamageEnabled, "fallDamageEnabled", true);
            Scribe_Values.Look(ref fallDamageMultiplier, "fallDamageMultiplier", 1f);
            Scribe_Values.Look(ref pitExposureEnabled, "pitExposureEnabled", true);
            Scribe_Values.Look(ref pitExposureNarrowing, "pitExposureNarrowing", RM_PitExposureMath.DefaultNarrowing);
            Scribe_Values.Look(ref pitDrowningEnabled, "pitDrowningEnabled", true);
            Scribe_Values.Look(ref pitDrowningRateMultiplier, "pitDrowningRateMultiplier", 1f);
            Scribe_Values.Look(ref poisonFillEnabled, "poisonFillEnabled", true);
            Scribe_Values.Look(ref slimeSlipEnabled, "slimeSlipEnabled", true);
            Scribe_Values.Look(ref slimeSlipChanceMultiplier, "slimeSlipChanceMultiplier", 1f);
            Scribe_Values.Look(ref slimeSlipStunSeconds, "slimeSlipStunSeconds", 2f);
            Scribe_Values.Look(ref slimeClimbOutSlipFactor, "slimeClimbOutSlipFactor", 2f);
            Scribe_Values.Look(ref pitTemperatureCoupling, "pitTemperatureCoupling", 3f);
            Scribe_Values.Look(ref pitResistanceLossMultiplier, "pitResistanceLossMultiplier", 1f);
            Scribe_Values.Look(ref spikesEnabled, "spikesEnabled", true);
            Scribe_Values.Look(ref spikeDamageMultiplier, "spikeDamageMultiplier", 1f);
            Scribe_Values.Look(ref pitDepthDrawOffsetEnabled, "pitDepthDrawOffsetEnabled", true);
            Scribe_Values.Look(ref pitSinkPerLevel, "pitSinkPerLevel", 0.3f);
            Scribe_Values.Look(ref excavationWallFacesEnabled, "excavationWallFacesEnabled", true);
            Scribe_Values.Look(ref excavationWallMaterialEnabled, "excavationWallMaterialEnabled", true);
            Scribe_Values.Look(ref pitLipOcclusionEnabled, "pitLipOcclusionEnabled", true);
            Scribe_Values.Look(ref pitSinkClampEnabled, "pitSinkClampEnabled", true);
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
            Scribe_Values.Look(ref waterFrontCreepEnabled, "waterFrontCreepEnabled", true);
            Scribe_Values.Look(ref levelBySurfaceEnabled, "levelBySurfaceEnabled", true);
            Scribe_Values.Look(ref levelSetEnabled, "levelSetEnabled", true);
            Scribe_Values.Look(ref levelExactEnabled, "levelExactEnabled", true);
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
            Scribe_Values.Look(ref digRockGroundEnabled, "digRockGroundEnabled", true);
            Scribe_Values.Look(ref digRockWorkMultiplier, "digRockWorkMultiplier", 4f);
            Scribe_Values.Look(ref digRockChunksEnabled, "digRockChunksEnabled", true);
            Scribe_Values.Look(ref digRockChunkMultiplier, "digRockChunkMultiplier", 1f);
            Scribe_Values.Look(ref digSoilChunkPercent, "digSoilChunkPercent", 0.5f);
            Scribe_Values.Look(ref swaleEnabled, "swaleEnabled", true);
            Scribe_Values.Look(ref swaleRateMultiplier, "swaleRateMultiplier", 1f);
            // ── Rivers (River Works, merged 2026-10-05): one settings file, unique keys ──
            Rivers.RM_RiversSettings.ExposeData();
            RiverColors.RM_RiverColorsSettings.ExposeData();   // River Colors merged 2026-10-16 (was mandrake.rut.rivercolors)
            Machinery.RM_MachinerySettings.ExposeData();
            // Builder Y sections (2026-10-05): sluice gates, quarry. One line each. (The empty tanker and bottled-blood stubs were
            // deleted 2026-10-11: neither feature is built; its settings arrive with it.)
            Machinery.Logistics.RM_SluiceGateSettings.ExposeData();
            MapControls.RM_MapControlSettings.ExposeData();   // FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS
            Machinery.Kits.RM_KitSettings.ExposeData();
            Quarry.RM_QuarrySettings.ExposeData();
            Hose.RM_HoseSettings.ExposeData();
            Thirst.RM_ThirstSettings.ExposeData();   // THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (design §6)
            Sprinklers.RM_SprinklerSettings.ExposeData();   // SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design §5)
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static Vector2 scrollPosition = Vector2.zero;

        // SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST: which switch is the master of which control on this screen. Each pair was
        // checked at its read site (2026-10-14): a dependent is declared only where the code that reads it is unreachable with the
        // master off. Left Independent on purpose: pulseIntervalTicks (the depth engine's own off-burn timer still uses it),
        // digToDepthEnabled (digging works with the engine off), drillYieldChanceMultiplier (the survey runs whatever the drill
        // switch says), wardenFromLipEnabled. The controls stay visible and greyed with their values kept; they replace the old
        // "hide when off" blocks.
        internal static readonly RimMandrake.Shared.SettingDependencies Masters = new RimMandrake.Shared.SettingDependencies()
            .Declare("depthEngineEnabled", "flowPerPulse", "maxNetworkCells", "networkSeamsMoveEnabled")
            .Declare("refillEnabled", "refillRateMultiplier")
            .Declare("deepBedsEnabled", "deepBedMaxDepth", "deepBedCellsPerLevel")
            .Declare("pondDepthEnabled", "pondMudDays", "pondStageWritesPerPulse")
            .Declare("rainFillsExcavationsEnabled", "rainFillPerPulse")
            .Declare("viscosityEnabled", "thickCreepEnabled")
            .Declare("liquidHeatPushEnabled", "liquidHeatStrength")
            .Declare("canalFireEnabled", "burnDaysPerNotch", "fireFrontSpeedMultiplier", "sourceFireReach",
                     "explosionIgnitesLiquidEnabled", "foamSmothersLiquidFireEnabled", "rainDousesLiquidFireEnabled",
                     "chemfuelInfernoEnabled", "astrofuelDetonationEnabled")
            .Declare("chemfuelInfernoEnabled", "chemfuelIntensity", "chemfuelSpreadSpeed", "chemfuelBurnRate")
            .Declare("astrofuelDetonationEnabled", "astrofuelBlastScale")
            .Declare("pitDrowningEnabled", "pitDrowningRateMultiplier")
            .Declare("slimeSlipEnabled", "slimeSlipChanceMultiplier", "slimeSlipStunSeconds", "slimeClimbOutSlipFactor")
            .Declare("pitExposureEnabled", "pitExposureNarrowing", "pitTemperatureCoupling", "pitResistanceLossMultiplier")
            .Declare("fallDamageEnabled", "fallDamageMultiplier")
            .Declare("spikesEnabled", "spikeDamageMultiplier")
            .Declare("pitDepthDrawOffsetEnabled", "pitSinkPerLevel", "pitLipOcclusionEnabled", "pitSinkClampEnabled", "pitHidesShadowEnabled")
            .Declare("pitLipOcclusionEnabled", "pitLipOcclusion", "pitLipOccupantCutEnabled")
            .Declare("pitLipOccupantCutEnabled", "pitLipOccupantCutWidth")
            .Declare("excavationWallFacesEnabled", "excavationWallMaterialEnabled", "pitOutlineEnabled")
            .Declare("pitScorchEnabled", "pitScorchFadeDays")
            .Declare("liquidBubblesEnabled", "liquidBubbleDensity")
            .Declare("trapTriggerEnabled", "trapSensitivityMultiplier")
            .Declare("superdeepRoomsEnabled", "captureDownEnabled")
            .Declare("digFindsEnabled", "digFindsLocalOnly", "digFindChanceMultiplier", "digFindBudgetPercent", "digFindLetterEnabled")
            .Declare("digRockGroundEnabled", "digRockWorkMultiplier")
            .Declare("digRockChunksEnabled", "digRockChunkMultiplier", "digSoilChunkPercent")
            .Declare("liquidDrillingEnabled", "drillUnitsPerCycle")
            .Declare("swaleEnabled", "swaleRateMultiplier")
            .Independent("pulseIntervalTicks", "digToDepthEnabled", "drillYieldChanceMultiplier", "wardenFromLipEnabled", "waterBodyTypeFlipFixEnabled")
            .Name("depthEngineEnabled", "Depth engine")
            .Name("pondDepthEnabled", "Ponds shallow out before they turn to mud")
                        .Name("refillEnabled", "Bodies refill").Name("rainFillsExcavationsEnabled", "Rain fills open excavations")
            .Name("viscosityEnabled", "Thick liquids flow slower than water")
            .Name("liquidHeatPushEnabled", "Boiling and icy liquid warm or chill the room they are in")
            .Name("waterBodyTypeFlipFixEnabled", "Water changing type keeps the game's water-body counts right")
            .Name("canalFireEnabled", "Flammable liquid in channels and ponds can be lit")
            .Name("chemfuelInfernoEnabled", "Chemfuel burns like gasoline").Name("astrofuelDetonationEnabled", "Astrofuel detonates")
            .Name("pitDrowningEnabled", "A flooded pit drowns whoever cannot swim")
            .Name("slimeSlipEnabled", "Slime is so slippery it is nearly impossible to cross")
            .Name("pitExposureEnabled", "An open pit leaves whoever is in it exposed to the elements")
            .Name("fallDamageEnabled", "Falling into a pit deals damage").Name("spikesEnabled", "Spikes on a pit floor stab whoever drops in")
            .Name("pitDepthDrawOffsetEnabled", "Pawns sink into dug channels and rise out of them")
            .Name("pitLipOcclusionEnabled", "The near edge of a cut hides whoever stands deep in it")
            .Name("pitLipOccupantCutEnabled", "Keep whoever is in the cut visible")
            .Name("excavationWallFacesEnabled", "Dug cells show their walls").Name("pitScorchEnabled", "A cut that burned dry looks scorched")
            .Name("liquidBubblesEnabled", "Acid, slime and boiling liquid bubble")
            .Name("trapTriggerEnabled", "Pit covers give way under enough weight")
            .Name("superdeepRoomsEnabled", "An enclosed pit is its own room")
            .Name("digFindsEnabled", "Digging a canal can turn up minerals")
            .Name("digRockGroundEnabled", "Canals can be dug through rock ground").Name("digRockChunksEnabled", "Digging can turn up rock chunks").Name("liquidDrillingEnabled", "Drilling and tapping")
            .Name("swaleEnabled", "A watered swale enriches the ground around it");

        private static object GetField(string n)
        {
            object v = typeof(RimMandrakeFlowWorksSettings).GetField(n, System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)?.GetValue(null);
            return v is System.Collections.Generic.List<string> l ? new System.Collections.Generic.List<string>(l) : v;
        }
        private static void SetField(string n, object v) =>
            typeof(RimMandrakeFlowWorksSettings).GetField(n, System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)?.SetValue(null, v);

        private static System.IDisposable Dependent(Listing_Standard list, params string[] keys) =>
            RimMandrake.Shared.SettingsKitMastersDrawer.Dependent(list, Masters, GetField, SetField, keys);

        /// <summary>The Reset-all button (after the confirmation): every setting on this window's excavation, flow, pit and look
        /// sections back to its shipped value. The hose section has its own Reset-all (RM_HoseSettings); the sub-screens with no
        /// reset of their own (rivers, machinery, sluice gates, kits, quarry) are not touched.</summary>
        public static void ResetAllFields()
        {
            var names = new System.Collections.Generic.List<string>(shippedDefaults.Keys) { nameof(disabledFluids) };
            ResetFields(names.ToArray());
        }

        // FLOWWORKS_SETTINGS_SCOPE_RESET_1 (FL-5): defaults are snapshotted when the type initialises, which is
        // before any save is read, so "reset" restores the shipped value even after ExposeData has overwritten it.
        private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = CaptureDefaults();

        private static System.Collections.Generic.Dictionary<string, object> CaptureDefaults()
        {
            var d = new System.Collections.Generic.Dictionary<string, object>();
            foreach (System.Reflection.FieldInfo f in typeof(RimMandrakeFlowWorksSettings).GetFields(
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
            {
                // int too: pitRampMaxSpan is one, and a section reset that skips it leaves the ramp span where the player set it.
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                {
                    d[f.Name] = f.GetValue(null);
                }
            }
            return d;
        }

        /// <summary>Resets the named fields to their shipped values. "disabledFluids" (a list, not snapshotted) resets
        /// to its shipped value, empty: every liquid may fill a cut.</summary>
        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                if (n == nameof(disabledFluids))
                {
                    disabledFluids?.Clear();
                    continue;
                }
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

        // SETTINGS_SCREEN_KIT_1: search + collapsible sections, via the shared kit. State is per game session.
        private static string searchQuery = "";
        private static readonly System.Collections.Generic.HashSet<string> collapsedSections = new System.Collections.Generic.HashSet<string>();
        private static float lastListHeight;

        /// <summary>
        /// Draws a section header (click to collapse), its reset button, and returns whether the body should draw.
        /// A search hits when the query matches the section title or any of its setting names (case-insensitive);
        /// non-matching sections vanish, and a search opens every matching section.
        /// </summary>
        private static bool Section(Listing_Standard list, string title, string[] names)
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
            if (open) DrawSectionReset(list, names);
            return open;
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
            // pit shadow; +150 for hot and icy liquid, 2026-10-08; +400 for per-section reset buttons; +100 recedeSparesOutflow.)
            // Collapsing/searching shrinks the content, so after the first frame the height is what the listing measured.
            // Before drawing: a confirmed Reset-all (its dialog runs after this window's frame) is picked up here.
            ApplyChangedSettings();
            Rect view = new Rect(0f, 0f, inRect.width - 24f, lastListHeight > 0f ? lastListHeight + 40f : 11600f);
            Widgets.BeginScrollView(inRect, ref scrollPosition, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);
            RimMandrake.Shared.SettingsKitMastersDrawer.ResetAllButton(list, "Flow Works excavation, flow and pit", ResetAllFields);

            if (Section(list, "Excavation and flow", new[] { "depthEngineEnabled", "digToDepthEnabled", "pulseIntervalTicks", "flowPerPulse", "maxNetworkCells", "networkSeamsMoveEnabled", "mouseoverDepthEnabled" }))
            {

            list.CheckboxLabeled("Show liquid depth and litres under the mouse", ref mouseoverDepthEnabled,
                "The cell readout in the bottom-left corner adds the liquid standing in the square: how deep it is in metres "
              + "(a level is half a metre) and how many litres it holds (a level is 1,000 litres, a deep square 4,000). Dug "
              + "channels and pits show their fill; ponds and lakes show their bed, scaled by how full the pond is. Off: "
              + "vanilla's line only.");

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
            using (Dependent(list, "flowPerPulse", "maxNetworkCells", "networkSeamsMoveEnabled"))
            {
                list.Label("Flow per pulse: " + FlowPerPulse + " level(s) per cell");
                flowPerPulse = list.Slider(flowPerPulse, 1f, 4f);
                list.Label("How many fill levels one cell can take in from its neighbours each "
                         + "pulse. Low reads as thick and slow; high reads as water.");

                list.Gap();
                list.Label("Largest network worked as one piece: " + MaxNetworkCells + " cells");
                maxNetworkCells = list.Slider(maxNetworkCells, 1000f, 50000f);
                list.Label("A connected canal network bigger than this is worked in pieces of this size each "
                         + "pulse. Higher costs more work in one pulse on a very large network; it changes "
                         + "nothing for a network smaller than it. Takes effect on the next pulse.");

                list.CheckboxLabeled("Liquid crosses between the pieces of a huge network", ref networkSeamsMoveEnabled,
                    "Where a network is too big to work as one piece, the borders between its pieces move each "
                  + "pulse, so liquid reaches every part of it. Off: the borders stay put and liquid never "
                  + "crosses them, so the far parts of a huge network stay dry. Takes effect on the next pulse.");
            }

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

            }

            list.GapLine();
            if (Section(list, "Unproven mechanics — ON by default", new[] { "liquidCorrosionEnabled", "liquidIgnitionEnabled" }))
            {
            list.Label("These came in with the liquid-types merge and have never run inside a "
                     + "live game. They ship on (owner decision 2026-10-15), but they have not had long play, not "
                     + "because they are broken. Turn one off if it misbehaves, and "
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
            }

            list.GapLine();
            if (Section(list, "Stock, recession and drainage", new[] { "fillInEnabled", "fillInDisplacementEnabled", "sourceBudgetEnabled", "stickyLimitlessEnabled", "minLimitlessBodyCells", "recessionEnabled", "recedeKeepsLastCell", "recedeSparesOutflow", "refillEnabled", "pondReturnLegEnabled", "refillWaitsForOccupants", "dugBedLeavesPondEnabled", "pondBedHollowEnabled", "deepBedsEnabled", "deepBedMaxDepth", "deepBedCellsPerLevel", "drainableLakeMaxCells", "pondDepthEnabled", "pondMudDays", "pondStageWritesPerPulse", "pondHeadRuleEnabled", "refillRateMultiplier", "rainFillsExcavationsEnabled", "rainFillPerPulse", "excavationLoadRepairEnabled", "legacyFillFallbackEnabled", "legacyFloodViaEngineEnabled", "pumpFedSpreadEnabled", "edgeSinksEnabled" }))
            {
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
                "A natural pond or lake holds the water its floor holds and no more: a square 2 m deep holds "
              + RM_Volume.FormatLitres(RM_Volume.LevelsPerSquare * RM_Volume.LitresPerNotch) + ", a 1 m shore square half that, "
              + "however big the pond looks. Run it down and the canal stops filling. Seas and rivers at the map's edge "
              + "never run dry. Off: every source is bottomless.");

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

            list.CheckboxLabeled("A body keeps the cells that feed a channel", ref recedeSparesOutflow,
                "A receding body gives up the cells touching a dug channel, pump cut or pit last, so a "
              + "canal dug off a pond keeps draining it instead of being cut off with most of the "
              + "water stranded behind the dried inlet. Off: the inlet recedes like any other edge cell.");

            list.CheckboxLabeled("Bodies refill", ref refillEnabled,
                "Seepage, rain and the season slowly put liquid back into a limited body, and "
              + "its cells come back in the order it gave them up. A very small seep takes "
              + "multiple seasons. Off: what you spend is gone for good.");

            list.CheckboxLabeled("Pumps and outflows can refill natural ponds", ref pondReturnLegEnabled,
                "A pump pouring, or a hose outflow end, next to a pond or its dried bed puts the water back into that "
              + "pond, one whole level at a time and never past what it held at the start. Off: only dug cells take "
              + "poured water; an outflow over a dried bed spills.");
            list.CheckboxLabeled("Returning water waits for people and buildings", ref refillWaitsForOccupants,
                "A dried pond square does not refill while a pawn stands on it or something is built on it; items "
              + "lying there wash to the nearest dry shore. Off: water comes back regardless.");
            list.CheckboxLabeled("Digging a dried bed takes the square out of its pond", ref dugBedLeavesPondEnabled,
                "A dried pond square you dig becomes yours, and the pond shrinks by what it held. Filling it back in to "
              + "ground level returns it to the pond as dry bed. Off: the old behaviour (a filled-in square came back "
              + "as unpaid pond water and flickered).");
            list.CheckboxLabeled("A drained pond leaves a hollow", ref pondBedHollowEnabled,
                "A pond square that dries out becomes cracked lakebed sunk to the depth the water had: two levels where it "
              + "was shallow, four where it was deep. A pond with a shallow rim is walked out of; a sheer deep drop holds what "
              + "falls in. A canal whose water stands above the bed's floor runs back into the pond. Refilling re-wets the "
              + "squares in the reverse order they dried, to the exact old shape. Off: a dried square is flat ground. "
              + "Climbing changes at once; squares already dry can keep their current look until they refill.");

            list.CheckboxLabeled("Lakes run deep", ref deepBedsEnabled,
                "The middle of a big lake goes deeper than 2 m: past a shore band its floor drops 0.5 m every few "
              + "squares, so a drained lake is a gentle bowl you can walk out of, darker toward its deepest floor. It holds that "
              + "much more water, drains off its shallow rim first and refills to its exact old shape. Applies to lakes the map "
              + "finds from now on. Off: every deep square is 2 m, and a pond dries by its average square, as before.");
            using (Dependent(list, "deepBedMaxDepth", "deepBedCellsPerLevel"))
            {
                list.Label("Deepest lake floor: " + RM_Volume.FormatMetres(DeepBedMaxDepth) + " (2 m to "
                    + RM_Volume.FormatMetres(RM_BedMath.MaxBedCeiling) + ")");
                deepBedMaxDepth = list.Slider(deepBedMaxDepth, RM_Volume.LevelsPerSquare, RM_BedMath.MaxBedCeiling);
                list.Label("Lake floor slope: 0.5 m deeper every " + DeepBedCellsPerLevel + " squares from the shore");
                deepBedCellsPerLevel = list.Slider(deepBedCellsPerLevel, 1f, 12f);
            }
            list.CheckboxLabeled("Ponds shallow out before they turn to mud", ref pondDepthEnabled,
                "A drawn-down pond keeps one flat surface and gets shallower all over: deep water, then chest-deep, then "
              + "shallow, then a thin sheet with the bed showing, then mud by the water's edge, and only after the mud time "
              + "cracked lakebed. Refilling raises the surface everywhere at once. Off: each pond square is full or dry, and "
              + "a pond shrinks from its edges, as before. Takes effect next pulse (ponds already touched are re-laid once).");
            using (Dependent(list, "pondMudDays", "pondStageWritesPerPulse"))
            {
                list.Label("Mud time: " + pondMudDays.ToString("F1") + " day(s) before an exposed pond square cracks");
                pondMudDays = list.Slider(pondMudDays, 0f, 10f);
                list.Label("Pond restages per pulse: " + PondStageWritesPerPulse);
                pondStageWritesPerPulse = list.Slider(pondStageWritesPerPulse, 50f, 2000f);
                list.Label("A cost guard: how many pond squares may change their look in one pulse. A big lake crossing a level "
                         + "catches up over a few pulses; the water itself never lags.");
            }
            list.CheckboxLabeled("Connected water levels to one surface", ref pondHeadRuleEnabled,
                "Water sloshes until it levels, pond or canal: a pond feeds a ditch only while its surface stands above the "
              + "ditch's water, so a shallow ditch stops drawing once the pond has dropped below its floor (dig deeper to keep "
              + "drawing), and a canal standing above a pond's surface runs back into it. Off: a pond feeds any ditch until "
              + "it is empty, as before.");

            list.Label("Largest drainable lake: " + DrainableLakeMaxCells + " squares");
            drainableLakeMaxCells = list.Slider(drainableLakeMaxCells, RM_BedMath.OceanWalkCells, 62500f);
            list.Label("A lake that does not touch the map edge and is no bigger than this has a real stock and can be "
                     + "pumped dry. Bigger, or touching the edge past the size above, it is limitless. "
                     + RM_BedMath.OceanWalkCells + " is the old limit. Applies to lakes the map finds from now on.");

            list.Gap();
            using (Dependent(list, "refillRateMultiplier"))
            {
                list.Label("Refill speed: " + refillRateMultiplier.ToString("F2") + "x");
                refillRateMultiplier = list.Slider(refillRateMultiplier, 0.1f, 5f);
                list.Label("Slow and certain is the intent, not random. At 1x a one-cell seep needs "
                         + "the better part of a year to refill what it can support.");
            }

            list.CheckboxLabeled("Rain fills open excavations", ref rainFillsExcavationsEnabled,
                "Rain falls into any excavated cell that is NOT roofed. Roof a pit and it stays "
              + "dry in a downpour — that is the point, and it makes roofing a real decision. "
              + "Off: weather never touches a channel.");

            list.Gap();
            using (Dependent(list, "rainFillPerPulse"))
            {
                list.Label("Rain fill speed: " + rainFillPerPulse.ToString("F2") + " level(s) per pulse");
                rainFillPerPulse = list.Slider(rainFillPerPulse, 0.01f, 1f);
                list.Label("How fast heavy rain fills an open trench. At the default a downpour takes "
                         + "roughly an in-game hour to add one level.");
            }

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
              + "channel owns that liquid and it flows on with the rest. Off: a spill never enters a dug "
              + "channel. Spills only ever spread through dug channels (or over standing liquid that is not "
              + "water), so with this off most spills place nothing at all.");

            list.CheckboxLabeled("Pumped liquid spreads along the channel", ref pumpFedSpreadEnabled,
                "Liquid a pump or drill puts into a channel spreads outward from where it enters, even when no "
              + "pond or river feeds that channel. Off: in a flat channel with no natural source, pumped liquid "
              + "piles up beside the pump.");

            list.CheckboxLabeled("Map-edge sinks drain", ref edgeSinksEnabled,
                "A channel dug into the strip along the map edge is a drain: liquid reaching it "
              + "leaves the map. It is not destroyed — it goes where an edge-touching lake's "
              + "water comes from. This also lets you dig in that strip at all, which the game "
              + "normally refuses. Off: the edge strip is undiggable again and nothing drains.");

            // ── LIQUID_HEAT_PUSH_1: hot and icy liquid ──────────────────────
            }

            list.GapLine();
            if (Section(list, "Hot and icy liquid", new[] { "liquidHeatPushEnabled", "liquidHeatStrength", "waterBodyTypeFlipFixEnabled" }))
            {
            list.CheckboxLabeled("Boiling and icy liquid warm or chill the room they are in", ref liquidHeatPushEnabled,
                "Boiling water (and any hot liquid) warms the room it stands in, the same way a heater does; icy water "
              + "chills it. A roofed hut over a boiling pool is warm, and a closed pit flooded with a hot liquid becomes "
              + "a heat trap. Outdoors nothing changes: like a heater, the open air takes no heat. A room levels off at "
              + "50 C (hot) or 0 C (icy). Takes effect within a few seconds. Off: liquid never changes the air.");
            using (Dependent(list, "liquidHeatStrength"))
            {
                list.Label("Heat strength: x" + liquidHeatStrength.ToString("F2") + " (PROVISIONAL; applies now)");
                liquidHeatStrength = list.Slider(liquidHeatStrength, 0.25f, 3f);
            }
            list.CheckboxLabeled("Water changing type keeps the game's water-body counts right", ref waterBodyTypeFlipFixEnabled,
                "A fix for a base-game bug. When a water cell turns into a different kind of water (fresh to salt, or "
              + "water to one of our liquids), the game keeps counting it in its old pond. Filling in the rest of that "
              + "pond later throws an error and the ground is not changed. On: the cell leaves its old pond first. "
              + "Off: the base game's behaviour. Takes effect at once.");

            // ── PHASE 6: fire ───────────────────────────────────────────────
            }

            list.GapLine();
            if (Section(list, "Burning liquid", new[] { "canalFireEnabled", "burnDaysPerNotch", "fireFrontSpeedMultiplier", "sourceFireReach", "explosionIgnitesLiquidEnabled", "foamSmothersLiquidFireEnabled", "rainDousesLiquidFireEnabled", "chemfuelInfernoEnabled", "chemfuelIntensity", "chemfuelSpreadSpeed", "chemfuelBurnRate", "astrofuelDetonationEnabled", "astrofuelBlastScale" }))
            {
            list.CheckboxLabeled("Flammable liquid in channels and ponds can be lit", ref canalFireEnabled,
                "Any fire touching tar (or another burnable liquid) lights it. The fire creeps along the liquid, "
              + "back into the pond or lake that feeds it, and burns for days. Anyone standing in it catches "
              + "fire; anyone trapped in a superdeep pit always does. Off: liquid never burns.");
            using (Dependent(list, "burnDaysPerNotch", "fireFrontSpeedMultiplier", "sourceFireReach", "explosionIgnitesLiquidEnabled", "foamSmothersLiquidFireEnabled", "rainDousesLiquidFireEnabled", "chemfuelInfernoEnabled", "astrofuelDetonationEnabled"))
            {
                list.Label("Burning liquid goes down " + RM_Volume.FormatMetres(1) + " every " + burnDaysPerNotch.ToString("F1")
                    + " day(s), in a canal or a pond alike");
                burnDaysPerNotch = list.Slider(burnDaysPerNotch, 0.1f, 5f);
                list.Label("A rate, not a timer: 1.5 m of burning liquid lasts about three times this, and a thin sheet "
                  + "burns away in a fraction of it. A pond still outlasts a canal, because the squares that are not "
                  + "burning keep sharing their water with the ones that are; a moat fed from a bigger unburning source "
                  + "can burn indefinitely, and a limitless source burns forever.");
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
                list.CheckboxLabeled("Chemfuel burns like gasoline", ref chemfuelInfernoEnabled,
                    "Lit chemfuel in a channel goes up like a moat of gasoline: the fire races along it in seconds, the "
                  + "flames stand tall, the heat is fierce, anything that can burn within a few cells of it catches, and "
                  + "the chemfuel burns away within a minute. Off: chemfuel creeps and smoulders for days like oil.");
                using (Dependent(list, "chemfuelIntensity", "chemfuelSpreadSpeed", "chemfuelBurnRate"))
                {
                    list.Label("Chemfuel fire intensity (heat, reach, size of the fires it starts): x" + chemfuelIntensity.ToString("F2"));
                    chemfuelIntensity = list.Slider(chemfuelIntensity, 0.25f, 3f);
                    list.Label("Chemfuel fire spread speed: x" + chemfuelSpreadSpeed.ToString("F2"));
                    chemfuelSpreadSpeed = list.Slider(chemfuelSpreadSpeed, 0.25f, 4f);
                    list.Label("Chemfuel burn-down: a fill level every " + (RM_FuelFireMath.InfernoTicksPerLevelAt(chemfuelBurnRate) / 60f).ToString("F1") + " s");
                    chemfuelBurnRate = list.Slider(chemfuelBurnRate, 0.25f, 4f);
                }
                list.CheckboxLabeled("Astrofuel detonates", ref astrofuelDetonationEnabled,
                    "Lighting astrofuel anywhere sets off the whole connected body at once: a rippling chain of explosions "
                  + "runs through every cell in a second or two, throwing back and staggering whoever is near, with a "
                  + "wave of heat, and every drop of it is gone. Off: astrofuel burns like chemfuel instead.");
                using (Dependent(list, "astrofuelBlastScale"))
                {
                    list.Label("Astrofuel blast damage and radius: x" + astrofuelBlastScale.ToString("F2"));
                    astrofuelBlastScale = list.Slider(astrofuelBlastScale, 0.25f, 3f);
                }
            }

            // ══════════════════════════════════════════════════════════════
            // PHASE 5 SECTION — kept whole and kept last, see the field block.
            // ══════════════════════════════════════════════════════════════
            }

            list.GapLine();
            if (Section(list, "Pits, ladders and shooting", new[] { "superdeepCaptureEnabled", "blastsBreakPitCovers", "superdeepCapturesOwnFaction", "ladderRequiredToExitEnabled", "ladderPrisonDoorEnabled", "ladderRaiseLowerEnabled", "pitWidthBodySizeMultiplier", "pitRelativeClimbEnabled", "pitClimbAbilityMultiplier", "pitSlowClimbFactor", "pitRampsEnabled", "pitRampMaxSpan", "pitLadderSlowness", "superdeepRoomsEnabled", "captureDownEnabled", "wardenFromLipEnabled", "pitDrowningEnabled", "pitDrowningRateMultiplier", "poisonFillEnabled", "slimeSlipEnabled", "slimeSlipChanceMultiplier", "slimeSlipStunSeconds", "slimeClimbOutSlipFactor", "pitExposureEnabled", "pitExposureNarrowing", "pitTemperatureCoupling", "pitResistanceLossMultiplier", "pitWalkNormalEnabled", "fallDamageEnabled", "fallDamageMultiplier", "spikesEnabled", "spikeDamageMultiplier", "pitDepthDrawOffsetEnabled", "pitSinkPerLevel", "excavationWallFacesEnabled", "excavationWallMaterialEnabled", "pitOutlineEnabled", "pitScorchEnabled", "pitScorchFadeDays", "pitLipOcclusionEnabled", "pitSinkClampEnabled", "pitHidesShadowEnabled", "pitLipOcclusion", "pitLipOccupantCutEnabled", "pitLipOccupantCutWidth", "liquidSurfaceMotionEnabled", "liquidWakesEnabled", "liquidLooksEnabled", "liquidBubblesEnabled", "liquidBubbleDensity", "liquidSeeThroughEnabled", "flowDoorsSealedFromPitEnabled", "sluiceLetsBigThroughEnabled", "viscosityEnabled", "thickCreepEnabled", "waterFrontCreepEnabled", "levelBySurfaceEnabled", "levelSetEnabled", "levelExactEnabled", "trapTriggerEnabled", "trapSensitivityMultiplier", "superdeepShootingRuleEnabled", "disabledFluids" }))
            {
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

            list.CheckboxLabeled("Pits trap by relative height", ref pitRelativeClimbEnabled,
                "On, what traps a creature is the height of the step it must climb, compared with each square's north, "
              + "south, east and west neighbours: a slope it can climb a step at a time never traps it, however deep it "
              + "goes, so a drained pond is walked out of. How tall a step a creature climbs depends on its size: "
              + RM_PocketGrid.BandText() + " Off: the old rule, any superdeep square holds whoever the pit captures.");
            list.Label("Climb ability (scales creature height): " + pitClimbAbilityMultiplier.ToString("F2"), tooltip:
                "1.00 = the table above. Higher, every creature climbs as if it were taller; lower, shorter.");
            pitClimbAbilityMultiplier = list.Slider(pitClimbAbilityMultiplier, 0.5f, 2f);
            list.Label("Slow climb factor: " + pitSlowClimbFactor.ToString("F1"), tooltip:
                "A creature climbs a step as tall as the most it can manage (two levels for a person) this many times slower "
              + "than a smaller step. 1 = no slower. Walking along one depth, or on a ramp, is never slowed.");
            pitSlowClimbFactor = list.Slider(pitSlowClimbFactor, 1f, 4f);
            list.CheckboxLabeled("Ramps", ref pitRampsEnabled,
                "On, a ramp can be built on a dug square, pointing uphill at a neighbour up to the span below shallower. "
              + "Everyone walks it both ways at normal walking speed, enemies and animals too: a ramp makes a pit escapable. "
              + "Off: ramps are inert and a pit is only left by climbing or a ladder.");
            list.Label("Levels a ramp spans: " + pitRampMaxSpan, tooltip:
                "How much shallower the square a ramp faces may be (1 to 3). A deeper drop takes a second ramp, or a ramp then "
              + "a step the creature can climb.");
            pitRampMaxSpan = Mathf.RoundToInt(list.Slider(pitRampMaxSpan, 1f, 3f));
            list.Label("Ladder slowness: " + pitLadderSlowness.ToString("F1"), tooltip:
                "A ladder joins its square to the wall it hangs on (a shallower neighbour), however deep, but each level climbed on it costs this "
              + "many normal climbs, so a ramp is always faster.");
            pitLadderSlowness = list.Slider(pitLadderSlowness, 1f, 4f);

            list.CheckboxLabeled("An enclosed pit is its own room", ref superdeepRoomsEnabled,
                "A superdeep area with ordinary ground all round it counts as a room of its own, separate "
              + "from the ground above, so it has its own temperature and can hold prisoners. Bare, it holds "
              + "trapped enemies; put a prisoner bed in it and it is a prison cell. Shallower cuts never "
              + "make rooms. Off: a pit is part of whatever room surrounds it (rooms are rebuilt at once).");
            using (Dependent(list, "captureDownEnabled"))
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
            using (Dependent(list, "pitDrowningRateMultiplier"))
            {
                list.Label("Drowning speed: x" + pitDrowningRateMultiplier.ToString("F2"));
                pitDrowningRateMultiplier = list.Slider(pitDrowningRateMultiplier, 0.1f, 5f);
            }
            list.CheckboxLabeled("Poisonous liquid poisons whoever stands in it", ref poisonFillEnabled,
                "A poison liquid builds up toxins in anyone standing in it, more the fuller the cell. "
              + "Toxic resistance helps. Off: poison is just another liquid.");
            list.CheckboxLabeled("Slime is so slippery it is nearly impossible to cross", ref slimeSlipEnabled,
                "Anyone walking through slime in a canal or pit keeps slipping: each slip stops them for a moment and "
              + "says so over their head, and a slip while climbing out slides them back to the start of the climb, so "
              + "getting out takes a long time. Colonists plan routes around slime. Off: slime is just a thick liquid.");
            using (Dependent(list, "slimeSlipChanceMultiplier", "slimeSlipStunSeconds", "slimeClimbOutSlipFactor"))
            {
                list.Label("How often people slip: x" + slimeSlipChanceMultiplier.ToString("F2"));
                slimeSlipChanceMultiplier = list.Slider(slimeSlipChanceMultiplier, 0.1f, 2.5f);
                list.Label("How long a slip stops them: " + slimeSlipStunSeconds.ToString("F1") + " s");
                slimeSlipStunSeconds = list.Slider(slimeSlipStunSeconds, 0.5f, 6f);
                list.Label("Slipping while climbing out: x" + slimeClimbOutSlipFactor.ToString("F1") + " as often");
                slimeClimbOutSlipFactor = list.Slider(slimeClimbOutSlipFactor, 1f, 4f);
            }
            list.CheckboxLabeled("An open pit leaves whoever is in it exposed to the elements", ref pitExposureEnabled,
                "Nobody in an open pit (no roof, no cover) can find shade, shelter or a windbreak: their comfortable "
              + "temperature range narrows, so the game's own heatstroke and hypothermia start sooner. Mild weather does "
              + "nothing. A prisoner loses recruitment resistance only while the heat or cold is actually hurting them, and "
              + "an unroofed pit room tracks outdoor temperature faster. Off: a pit is like open ground.");
            using (Dependent(list, "pitExposureNarrowing", "pitTemperatureCoupling", "pitResistanceLossMultiplier"))
            {
                list.Label("Exposure narrows the comfortable range by " + pitExposureNarrowing.ToString("F0") + " °C each way (owner's pick: 8)");
                pitExposureNarrowing = Mathf.Round(list.Slider(pitExposureNarrowing, 0f, 15f));
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
            using (Dependent(list, "fallDamageMultiplier"))
            {
                list.Label("Fall damage multiplier: " + fallDamageMultiplier.ToString("F2"));
                fallDamageMultiplier = list.Slider(fallDamageMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Spikes on a pit floor stab whoever drops in", ref spikesEnabled,
                "Spikes built on the floor of a superdeep pit stab anyone who falls, is pushed or jumps "
              + "into that cell: three Sharp hits through armour, bigger for bigger creatures. Never on "
              + "walking up to the edge or moving along the pit floor. Off: spikes are harmless.");
            using (Dependent(list, "spikeDamageMultiplier"))
            {
                list.Label("Spike damage multiplier: " + spikeDamageMultiplier.ToString("F2"));
                spikeDamageMultiplier = list.Slider(spikeDamageMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Pawns sink into dug channels and rise out of them", ref pitDepthDrawOffsetEnabled,
                "A pawn standing in a dug cell is drawn lower the deeper the cell, and rises smoothly as it "
              + "walks out, so every depth reads at a glance. Drawing only: it changes nothing about "
              + "movement, sight or shooting. Off: pawns are drawn at ground level everywhere.");
            using (Dependent(list, "pitSinkPerLevel"))
            {
                list.Label("Sink per depth level (cells): " + pitSinkPerLevel.ToString("F2")
                  + "  (superdeep: " + (pitSinkPerLevel * 4f).ToString("F2") + ")");
                pitSinkPerLevel = list.Slider(pitSinkPerLevel, 0.05f, 0.5f);
            }

            list.CheckboxLabeled("Dug cells show their walls", ref excavationWallFacesEnabled,
                "Every cut draws the faces of its banks the way you would see them from above and to the south: the far "
              + "(north) bank's face is a band that grows taller and darker the deeper the cut, and the side banks show "
              + "as narrow faces. Liquid standing in a cut covers the foot of its walls. Drawing only. Off: a dug cell "
              + "shows only its ground.");
            using (Dependent(list, "excavationWallMaterialEnabled"))
            {
                list.CheckboxLabeled("  Walls look like the ground they are cut through", ref excavationWallMaterialEnabled,
                    "A cut's walls are drawn the way the game draws its own walls from above: a lit face with a dark rim, "
                  + "made of the ground beside it, earth beside soil and that rock's stone beside rock. A cut deep enough "
                  + "to hold a person shows a wall-height face, the deepest cut a taller one. Drawing only. Off: the plain "
                  + "earth-coloured band.");
            }
            using (Dependent(list, "pitOutlineEnabled"))
            {
                list.CheckboxLabeled("  Cuts are outlined, darkest along the near edge", ref pitOutlineEnabled,
                    "Every cut gets a closed dark outline so you can see where it is: a thin line on the far and side "
                  + "banks and a heavy dark lining on the near (south) edge that grows with depth. Shows even when "
                  + "liquid fills the cut. Drawing only.");
            }
            list.CheckboxLabeled("A cut that burned dry looks scorched", ref pitScorchEnabled,
                "After a liquid fire burns a cut dry, it stays an empty pit with charred walls, an ash floor and a scorch "
              + "ring round the rim, until it is refilled or filled in, or the scorch fades. Drawing only. Off: a burned "
              + "cut looks like any other.");
            using (Dependent(list, "pitScorchFadeDays"))
            {
                list.Label("Scorch fades after (days, 0 = never): " + pitScorchFadeDays.ToString("F0") + "  (rain on it: three times as fast)");
                pitScorchFadeDays = Mathf.Round(list.Slider(pitScorchFadeDays, 0f, 60f));
            }
            using (Dependent(list, "pitLipOcclusionEnabled", "pitSinkClampEnabled", "pitHidesShadowEnabled"))
            {
                list.CheckboxLabeled("The near edge of a cut hides whoever stands deep in it", ref pitLipOcclusionEnabled,
                    "Seen from above and to the south, the near bank is in front of a pawn standing deep in a cut, so the "
                  + "part of them below its edge is hidden behind it. Drawing only.");
                list.CheckboxLabeled("Hold a deep pawn inside the cut's near edge", ref pitSinkClampEnabled,
                    "Stops a big sprite from drawing outside the cut on the south side, but also caps how far everyone sinks on that row. On by default. Drawing only.");
                list.CheckboxLabeled("No ground shadow under someone down in a cut", ref pitHidesShadowEnabled,
                    "A person or animal standing in a cut has no shadow drawn on the ground under them, so it cannot "
                  + "show through the near bank. Drawing only. Off: the game's usual shadow.");
                using (Dependent(list, "pitLipOcclusion", "pitLipOccupantCutEnabled"))
                {
                    list.Label("How much it hides: " + pitLipOcclusion.ToStringPercent() + "  (100% = completely; less leaves a faint outline)");
                    pitLipOcclusion = list.Slider(pitLipOcclusion, 0.5f, 1f);
                    list.CheckboxLabeled("Keep whoever is in the cut visible", ref pitLipOccupantCutEnabled,
                        "Cuts a window through the near edge's cover where someone stands, at every depth, so they can always be found. "
                      + "The cover still hides their sides. Drawing only. Off: the cover hides them as above.");
                    using (Dependent(list, "pitLipOccupantCutWidth"))
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
                "A V of ripples behind anything walking through a liquid in a cut, as strong as the liquid is thin: "
              + "water ripples clearly, slime and blood less, tar and oil barely stir. Drawing only.");
            list.CheckboxLabeled("Each liquid has its own surface", ref liquidLooksEnabled,
                "Water looks and moves like the game's own shallow water (tinted for brine, toxic or acid water, "
              + "steaming when boiling); tar, oil and slime are thick dark liquids that slowly creep and shine. "
              + "Each liquid's look is part of its definition. Drawing only. Off: every liquid is a flat tinted water.");
            list.CheckboxLabeled("Acid, slime and boiling liquid bubble", ref liquidBubblesEnabled,
                "Bubbles rise and pop on the liquids that have them: lightly on slime, steadily on acid, hard on "
              + "boiling water. Drawing only. Off: no bubbles.");
            using (Dependent(list, "liquidBubbleDensity"))
            {
                list.Label("How many bubbles: x" + liquidBubbleDensity.ToString("F1"));
                liquidBubbleDensity = Mathf.Round(list.Slider(liquidBubbleDensity, 0.2f, 3f) * 10f) / 10f;
            }
            list.CheckboxLabeled("See the floor and walls of a cut through clear liquid", ref liquidSeeThroughEnabled,
                "Water and other clear liquids standing in a cut let its floor and drowned walls show through, "
              + "fainter the deeper it is. Tar, oil, slime and blood stay opaque. Drawing only. Off: the liquid "
              + "surface hides the cut below it.");
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
              + "prisoner. A shut sluice holds liquid back; the grate passes liquid open or shut. Off: a sluice holds like an ordinary door.");
            list.CheckboxLabeled("Thick liquids flow slower than water", ref viscosityEnabled,
                "Tar, slime, oil and blood creep along a channel: each level waits several pulses before it moves "
              + "on (blood 2, oil 3, tar 6, slime 8 pulses to water's 1), so a tar channel fills far behind a water "
              + "one dug beside it. Off: every liquid flows at water's pace.");
            using (Dependent(list, "thickCreepEnabled"))
            {
                list.CheckboxLabeled("Thick liquids creep one cell at a time", ref thickCreepEnabled,
                    "Needs 'Thick liquids flow slower'. On: tar, slime, oil and blood advance one cell each time they move, "
                  + "so a long channel fills at its stated speed instead of all at once on one pulse. Water is not "
                  + "affected. Off: a thick liquid that reaches a cell can pass on to the next in the same pulse.");
            }
            list.CheckboxLabeled("Water fills a channel from the mouth outward", ref waterFrontCreepEnabled,
                "On: water advances one cell each pulse, so a dug channel wets from the end nearest the water and the wet "
              + "front visibly travels along it like a flood. Off: a level can be passed the whole run in one pulse, "
              + "which fills a dead-end channel from its far end first.");
            list.CheckboxLabeled("Water levels out by its surface", ref levelBySurfaceEnabled,
                "On: each square holds levels of water (half a metre, 1,000 litres each) and they spread toward the lowest water surface, whatever depth "
              + "each square was dug to, so a channel settles to within one level everywhere and a draining channel "
              + "empties instead of leaving deep puddles. Off: water only runs into a deeper square or out of a "
              + "brim-full one, so partly filled squares of equal depth never even out.");
            list.CheckboxLabeled("Water stands exactly level", ref levelExactEnabled,
                "On: water is kept to the litre, and every connected body of water - a canal, a pit, a pond, or all of them "
              + "joined - stands at one flat surface, so a little water spreads as a thin sheet (24 cm in every square of a "
              + "canal) instead of whole half-metre steps. Its look follows how deep the water really is. Off: water moves in "
              + "half-metre steps (the two settings below).");
            if (levelBySurfaceEnabled)
            {
                list.CheckboxLabeled("  Water settles to one flat level", ref levelSetEnabled,
                    "On: each connected body of water is laid out at the flat level it would settle to, so a wide field ends "
                  + "as an even sheet, or, with too little water to cover it, one patch of the shallowest depth (one level) "
                  + "and the rest dry. Water never climbs over a dry sill to reach another hole. Off: water moves one level "
                  + "at a time between neighbours, which can leave a wide field striped wet, dry, wet.");
            }

            list.CheckboxLabeled("Pit covers give way under enough weight", ref trapTriggerEnabled,
                "An armed cover over a pit drops whoever stands on it once their combined mass passes "
              + "the cover's rating. Off: covers never give way on their own.");
            using (Dependent(list, "trapSensitivityMultiplier"))
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
            }

            list.GapLine();
            if (Section(list, "Bottles, buckets, barrels: fill, use, wash", new[] { "bottleLoopEnabled", "bottleDirtyStageEnabled", "bottleRevertEnabled" }))
            {
            list.Label("An empty container filled at a matching liquid's shore becomes a filled one; "
                     + "drinking or otherwise using one leaves a container behind to deal with. Buckets "
                     + "hold " + RM_Volume.FormatLitres(15) + " (ten bottles), barrels " + RM_Volume.FormatLitres(208) + " — same chain, same labour. "
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
            }

            list.GapLine();
            if (Section(list, "The liquid tank", new[] { "tankLoopEnabled", "tankCapacityMultiplier", "liquidPumpEnabled" }))
            {
            list.Label("A patched-together scavenger tank: a big fixed store of ONE liquid at a "
                     + "time, filled by pouring a container in and drained by filling a container "
                     + "from it. The same fetch-labour pattern as the fill/wash loop above.");

            list.CheckboxLabeled("Tank pour/draw labour", ref tankLoopEnabled,
                "Colonists automatically carry a filled container to a tank set to Fill, and an empty "
              + "container to a Store, Empty or Dump tank holding enough to fill it — no order needed. "
              + "To pour bottles into an ordinary Store tank, order it (right-click a bottle). A bottle is "
              + "never filled from a Fill tank, so nothing is poured in and drawn straight back out. Off: a tank already built keeps whatever it holds and can still be worked "
              + "by hand-carrying, but nothing fetches for you.");

            list.Gap();
            list.Label("Tank capacity: x" + tankCapacityMultiplier.ToString("F2") + "  (one tank square "
                     + RM_Volume.FormatUnits(RM_Volume.TankCapacity(1, false, tankCapacityMultiplier)) + ", a tall square twice that, an extra-tall four times)");
            tankCapacityMultiplier = list.Slider(tankCapacityMultiplier, 0.2f, 5f);
            list.Label("Scales every tank's capacity (at 1x a tank square holds one deep canal square, "
                     + RM_Volume.FormatUnits(RM_Volume.UnitsPerSquare) + ": the 2x2 liquid tank 16 kL, the tall tank and cargo tank 32 kL, the extra-tall cargo tank 64 kL). Any value but 1x "
                     + "breaks one tank square = one canal square. Raise it for a colony that wants to stockpile.");

            list.CheckboxLabeled("Liquid pumps run", ref liquidPumpEnabled,
                "A powered pump either draws liquid from the pond, lake or dug channel it reaches into a tank on its "
              + "line (touching it or on a hose run to it), or pours that tank into a dug channel it reaches — one channel level (1,000 litres, "
              + "a cubic metre) every few seconds. A pond it draws from runs down like any other use. Off: pumps sit idle "
              + "and draw no power.");

            // ══════════════════════════════════════════════════════════════
            // MANY_WATERS_DRILL_BUILDINGS_1 SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            }

            list.GapLine();
            if (Section(list, "Drilling and tapping", new[] { "liquidDrillingEnabled", "drillYieldChanceMultiplier", "drillUnitsPerCycle" }))
            {
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
            using (Dependent(list, "drillUnitsPerCycle"))
            {
                list.Label("Extraction rate: " + DrillUnitsPerCycle.ToString("F2") + " fill-unit(s) per cycle");
                drillUnitsPerCycle = list.Slider(drillUnitsPerCycle, 0.1f, 6f);
                list.Label("How much a drill (or a slower tap, scaled down per building) can pull "
                         + "from the ground every 250 ticks once its outlet has room to take it. "
                         + "The reserve it draws from is finite and never comes back.");
            }

            // ══════════════════════════════════════════════════════════════
            // WORLDMAP_LIQUID_TAGS_1 SECTION — kept whole and kept last.
            // ══════════════════════════════════════════════════════════════
            }

            list.GapLine();
            if (Section(list, "Typed bodies of water", new[] { "typedLiquidShoresEnabled" }))
            {
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
            }

            list.GapLine();
            if (Section(list, "Finds while digging", new[] { "digFindsEnabled", "digFindsLocalOnly", "digFindChanceMultiplier", "digFindBudgetPercent", "digFindLetterEnabled", "digRockGroundEnabled", "digRockWorkMultiplier", "digRockChunksEnabled", "digRockChunkMultiplier", "digSoilChunkPercent" }))
            {
            list.CheckboxLabeled("Digging a canal can turn up minerals", ref digFindsEnabled,
                "Each time a cell is cut a level deeper there is a small chance of a lump of something the land holds, "
              + "thrown up onto the bank. Deep and superdeep cuts can reach what a deep drill would find under that cell. "
              + "Where the land holds nothing, you get chunks of the local rock. Filling a cell in and digging it again "
              + "pays nothing twice. Off: digging only digs.");
            using (Dependent(list, "digFindsLocalOnly", "digFindChanceMultiplier", "digFindBudgetPercent", "digFindLetterEnabled"))
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

            list.CheckboxLabeled("Canals can be dug through rock ground", ref digRockGroundEnabled,
                "On: bare stone floor (rough, rough-hewn or smoothed natural rock) can be marked to dig, and is much slower work "
              + "than soft ground. Off: only soil can be dug, as before.");
            using (Dependent(list, "digRockWorkMultiplier"))
            {
                list.Label("Rock digging takes x" + digRockWorkMultiplier.ToString("F1") + " the work of soft ground  (a rock wall mines in ~700 ticks; a soil cut is 3200)");
                digRockWorkMultiplier = list.Slider(digRockWorkMultiplier, 1f, 10f);
            }
            list.CheckboxLabeled("Digging can turn up rock chunks", ref digRockChunksEnabled,
                "Each cut a level deeper through rock ground has the same chance of a chunk of that rock as mining a standing rock wall "
              + "(25% in the base game). Through anything else (soil, sand, gravel) a chunk is very rare. Shares the guard of mineral finds: "
              + "filling in and re-digging pays nothing twice.");
            using (Dependent(list, "digRockChunkMultiplier", "digSoilChunkPercent"))
            {
                list.Label("Rock chunk chance in rock: x" + digRockChunkMultiplier.ToString("F2") + " of the wall-mining rate");
                digRockChunkMultiplier = list.Slider(digRockChunkMultiplier, 0f, 4f);
                list.Label("Rock chunk chance in non-rock ground: " + digSoilChunkPercent.ToString("F1") + "% per cut");
                digSoilChunkPercent = list.Slider(digSoilChunkPercent, 0f, 5f);
            }

            // ── CRACKEDLANDS_MECHANICS_BUILD_1 §1 — the swale ─────────────
            }

            list.GapLine();
            if (Section(list, "Swales", new[] { "swaleEnabled", "swaleRateMultiplier" }))
            {
            list.CheckboxLabeled("A watered swale enriches the ground around it", ref swaleEnabled,
                "On: a swale laid in a dug channel, while its own cell carries water (a fill, a flood "
              + "or a natural source), slowly turns the ground within two cells one step richer — "
              + "sand to soil to rich soil, never past rich soil, never while dry. Off: a built "
              + "swale does nothing; ground it already improved stays improved.");
            using (Dependent(list, "swaleRateMultiplier"))
            {
                list.Label("Swale pace: " + SwaleRateMultiplier.ToString("F2") + "x  (1x = one step per fed day; first-guess number)");
                swaleRateMultiplier = list.Slider(swaleRateMultiplier, 0.1f, 10f);
            }

            }

            // ── Rivers (River Works, merged 2026-10-05) ───────────────────
            Rivers.RM_RiversSettingsWindow.DoSettingsSection(list);
            RiverColors.RM_RiverColorsSettings.DoSettingsSection(list);
            Machinery.RM_MachinerySettings.DoSettingsSection(list);
            Machinery.Logistics.RM_SluiceGateSettings.DoSettingsSection(list);
            MapControls.RM_MapControlSettings.DoSettingsSection(list);
            Machinery.Kits.RM_KitSettings.DoSettingsSection(list);
            Quarry.RM_QuarrySettings.DoSettingsSection(list);
            Hose.RM_HoseSettings.DoSettingsSection(list);
            Thirst.RM_ThirstSettings.DoSettingsSection(list);
            Sprinklers.RM_SprinklerSettings.DoSettingsSection(list);

            lastListHeight = list.CurHeight;
            list.End();
            Widgets.EndScrollView();
            // After drawing: a checkbox, slider or section reset changed in this frame.
            ApplyChangedSettings();
        }

        // Settings whose change must rebuild or redraw something, as last applied. Compared against the live fields at the
        // start and end of every frame of this window, so EVERY route that changes one is caught: its own control, a section
        // reset, the confirmed Reset-all (whose dialog callback runs outside this window's frame, which per-frame snapshots
        // taken around Section() missed: review 2026-10-14), PatchApplier.ReforceOff, or a bridge settings write. Session-wide
        // on purpose: these mirror the session-wide settings themselves, not any game's state.
        private static bool appliedKnown;
        private static bool appliedHollow, appliedClimb, appliedRamps, appliedRooms, appliedWalls, appliedMat, appliedOutline,
            appliedScorch, appliedLooks, appliedSee;
        private static float appliedClimbMul;
        private static int appliedRampSpan;

        private static void ApplyChangedSettings()
        {
            if (appliedKnown)
            {
                bool hollow = appliedHollow != pondBedHollowEnabled;
                if (hollow || appliedClimb != pitRelativeClimbEnabled || appliedClimbMul != pitClimbAbilityMultiplier
                    || appliedRamps != pitRampsEnabled || appliedRampSpan != pitRampMaxSpan)
                {
                    RM_PocketGrid.SettingsChanged();
                }
                if (hollow && Current.Game != null)
                {
                    // the climb depth changed under every dry bed: redraw the wall faces and sinks too
                    foreach (Map m in Find.Maps)
                    {
                        m.mapDrawer.WholeMapChanged(RimWorld.MapMeshFlagDefOf.Terrain);
                    }
                }
                if (appliedRooms != superdeepRoomsEnabled)
                {
                    RM_PitRooms.RebuildAllMaps();
                }
                if (appliedWalls != excavationWallFacesEnabled || appliedMat != excavationWallMaterialEnabled
                    || appliedScorch != pitScorchEnabled || appliedOutline != pitOutlineEnabled || appliedSee != liquidSeeThroughEnabled)
                {
                    SectionLayer_RMExcavationWalls.RedrawAll();
                }
                if (appliedLooks != liquidLooksEnabled)
                {
                    if (liquidLooksEnabled) RM_LiquidLooks.ApplyAll(); else RM_LiquidLooks.RevertAll();
                }
            }
            appliedKnown = true;
            appliedHollow = pondBedHollowEnabled;
            appliedClimb = pitRelativeClimbEnabled;
            appliedClimbMul = pitClimbAbilityMultiplier;
            appliedRamps = pitRampsEnabled;
            appliedRampSpan = pitRampMaxSpan;
            appliedRooms = superdeepRoomsEnabled;
            appliedWalls = excavationWallFacesEnabled;
            appliedMat = excavationWallMaterialEnabled;
            appliedOutline = pitOutlineEnabled;
            appliedScorch = pitScorchEnabled;
            appliedLooks = liquidLooksEnabled;
            appliedSee = liquidSeeThroughEnabled;
        }
    }

    public class RimMandrakeFlowWorksMod : Mod
    {
        public static RimMandrakeFlowWorksSettings settings;

        public RimMandrakeFlowWorksMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RimMandrakeFlowWorksSettings>();
            // hose port step 2: the hose's essential patches (save-skip, type alias) outside PatchApplier, the one-time
            // import of Gimme Some Slack's hose settings and look, and the mixed-version warning
            Hose.RM_HoseEssentials.Apply();
            if (Hose.RM_HoseLegacy.ImportOnce()) settings.Write();
            Hose.RM_HoseLegacy.DetectOldGss();
        }

        public override string SettingsCategory()
        {
            // Grouped by origin: two Mod classes ship in this one assembly
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

        public override void WriteSettings()
        {
            base.WriteSettings();
            // C6-F3: the river avoidance cost lives on the TerrainDefs; a mid-game switch re-applies it, no restart
            Rivers.RM_RiverPathCost.Reapply();
            // THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY: thirst on/off or animals on/off adds or removes RM_Thirst on live pawns
            Thirst.RM_ThirstProvider.Reapply();
        }
    }
}
