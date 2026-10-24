# FlowWorks + GSS takeover plan, 2026-10-23

Owner 2026-10-23: "I asked Foundry to hand ALL FlowWorks items to you to complete them and own them from now on. No more Foundry work on FlowWorks." Owner card 07:41: GSS included. Everything below is BENCH-owned.

Method: open items classified by what their prose/notes name (FlowWorks/ or GimmeSomeSlack/ paths, FlowWorks types), not by title. "moved" = reassigned this sitting from FOUNDRY (66 FlowWorks + 5 GSS); "was BENCH" = already BENCH. States are ledger states: built/validated = code landed, live criteria owed.

## Wave plan (no two concurrent helpers on the same files)

- **Wave 1, offline, 5 parallel helpers** (disjoint file sets): **B** pits/superdeep (Source/Superdeep/**, RM_RaiderTrench*), **D** suspension/drawbridge (Pits/Suspension, Pits/Drawbridge; NOTE working tree already has uncommitted edits to RM_DrawbridgeArt.cs, Building_SuspensionDeck.cs, RM_DrawbridgeMath.cs, DrawbridgeChecks.cs, the SelfTest csproj, owner of those must commit or be the D helper), **H** hose/pipe/tank/pump art+C#, **A** liquids/levels/ledger (owns RM_MapComponent_Excavation.cs, RM_Liquid*.cs; B must not touch Excavation.cs, hand B's needs to A), **F** GSS (GimmeSomeSlack/** + CompAerialAnchor/RM_MapComponent_Aerial).
- **Wave 2, offline, 2 helpers**: **E** rivers/weirs/settings (RM_River*, settings kit; touches shared SettingsKit so not concurrent with A's settings rows), **P** proofs/selftests/northstar python (touches only northstar/*.py, validation*.py, SelfTest; start after Wave 1 so proofs target landed code).
- **Bridge batches**: one game session per wave, run by one driver holding the bridge. **Bridge run 1** after Wave 1 deploy (one DLL+defs deploy): all `needs=bridge` items of areas B/D/H/A/F in one pass; **Bridge run 2** after Wave 2 (rivers, settings, north-star GREEN-min, the 12 review scenes). The deployed-DLL staleness trap (PIPE_GIRTH_TUNE note: 8d5b94b0e1 never deployed) means deploy first and read the deployed DLL hash in each result.
- **Owner-needed** items (judge/look/decide) go in one owner sitting, listed below, not blocking helpers.
- csproj/SelfTest.csproj Compile lines: TANK_DEBUG (e609a50675 unpushed) owes Compile lines for FlowWorksTankDebug.cs, RM_TankDebugMath; helper H owns that csproj in Wave 1, D must not edit it (D's SelfTest csproj edit is the dirty one above, so D and H serialize on that file: H waits for D's commit).

## Items by area

### B: Pits / superdeep / trench / ladders / falls (Wave 1, 27 items)
Default files: FlowWorks/Source/Superdeep/** (RM_PitPathing, RM_SuperdeepTrap, RM_PocketGrid, Building_PitCover), RM_RaiderTrench*.cs

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED | ready | offline | code C# | (area default) | M | was BENCH |
| CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| EXCAVATION_LEGACY_MIGRATION_FLAG_1 | built | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| EXCAVATION_WALL_ART_1 | validated | bridge (live check owed; code built) | art | (area default) | L | moved |
| FALL_GUARDRAILS_BUILD_REAL_OBJECT | validated | bridge (live check owed; code built) | code C# | Building_PitCover.cs, RM_PitPathing.cs, RM_SuperdeepTrap.cs | S | moved |
| FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG | proposed | offline | code C# | (area default) | M | moved |
| FLOWWORKS_NORTHSTAR_SHIP_1 | proposed | offline | proof | (area default) | S | moved |
| FLOWWORKS_QUARRY_DIGGING_1 | validated | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| LADDER_EW_FIX_LEANS_THE_WRONG_WAY | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| LADDER_PARITY_BUILD_NO_KEYS_REQUIRED | built | bridge (live check owed; code built) | code C# | (area default) | L | was BENCH |
| PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS | built | bridge (live check owed; code built) | art | (area default) | S | was BENCH |
| PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS | validated | owner | code C# | (area default) | S | was BENCH |
| PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH | proposed | bridge | proof | (area default) | S | moved |
| PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS | built | bridge (live check owed; code built) | code C# | RM_DigDiscovery.cs | S | moved |
| PIT_LID_FIX_VICKY_PEEKS_THROUGH | validated | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| PIT_LIP_OCCLUDES_OUTSIDE_1 | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE | built | owner | code C# | (area default) | S | was BENCH |
| PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS | doing | deploy | art | (area default) | S | was BENCH |
| PIT_SUPERDEEP_COLLAPSE_1 | ready | bridge | code C# | CompPitFitting.cs, RM_ExcavationDepth.cs | L | moved |
| PIT_TEMPERATURE_SOFTENING_1 | validated | bridge (live check owed; code built) | code C# | (area default) | L | moved |
| PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS | proposed | owner | code C# | (area default) | M | was BENCH |
| PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT | proposed | offline | art | (area default) | S | was BENCH |
| RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP | validated | bridge (live check owed; code built) | code C# | RM_RaiderTrench.cs, RM_RaiderTrenchMath.cs | S | was BENCH |
| RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL | doing | deploy | art | (area default) | S | was BENCH |
| SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS | proposed | bridge | proof | (area default) | S | was BENCH |
| TITAN_TRENCHES_WIRE_MIND_THE_GAP | built | bridge (live check owed; code built) | code C# | (area default) | L | was BENCH |
| TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP | validated | bridge (live check owed; code built) | code C# | RM_RaiderTrench.cs | S | was BENCH |

### D: Suspension / drawbridge / railing (Wave 1, 11 items)
Default files: FlowWorks/Source/Pits/Suspension/**, Pits/Drawbridge/**, RM_DrawbridgeMath.cs, Building_SpanDeck.cs

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS | doing | offline | code C# | RM_PocketGrid.cs | M | was BENCH |
| DRAWBRIDGE_CABLES_FIX_STOP_SHORT | proposed | offline | code C# | (area default) | M | was BENCH |
| DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK | built | bridge (live check owed; code built) | art | (area default) | S | was BENCH |
| RAILING_MATERIAL_FIX_MADE_OF_NOTHING | built | bridge (live check owed; code built) | code C# | RM_MapComponent_SuspensionBridges.cs | S | moved |
| SUSPENSION_ART_RESKIN_HE_SEES_FIRST | validated | bridge (live check owed; code built) | art | (area default) | M | was BENCH |
| SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT | validated | bridge (live check owed; code built) | code C# | Building_PitCover.cs, RM_LiquidFire.cs, RM_Patch_SuperdeepShooting.cs | S | was BENCH |
| SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS | validated | bridge (live check owed; code built) | code C# | Designator.cs | M | was BENCH |
| SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP | validated | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD | validated | bridge (live check owed; code built) | code C# | RM_CliffMask.cs, RM_PocketGrid.cs | M | was BENCH |
| SUSPENSION_WATERS_BUILD_MAY_BACKTRACK | validated | bridge (live check owed; code built) | code C# | (area default) | M | was BENCH |

### H: Hose / pipe / joint / reel / tank / pump / coupler (C# + art) (Wave 1, 54 items)
Default files: FlowWorks/Source/Hose*, HoseMath.cs, RM_MapComponent_Hoses.cs, Joint*/selftests, art_source/{Hose,Pipe,Tank,Pump,UnderCouplers}

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| COUPLER_ART_INSTALL_DRESSED_UP_AT_LAST | built | bridge (live check owed; code built) | art | (area default) | S | was BENCH |
| FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| FOUNTAIN_ART_FINISH_WAITS_FOR_A_FAVOURITE | proposed | offline | art | (area default) | S | was BENCH |
| FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN | proposed | offline | code C# | RM_MapComponent_Sheet.cs, RM_Sprinkle.cs | L | was BENCH |
| FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART | proposed | offline | art | (area default) | S | was BENCH |
| GLOWTANK_DRINK_DIAGNOSE_DRY_BESIDE_THE_SEA | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| GLOW_TANK_LIQUID_FEED_1 | validated | bridge (live check owed; code built) | code C# | Building_GlowTank.cs | M | moved |
| HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| HOSE_END_REDRAW_STARES_AT_CAMERA | proposed | offline | art | (area default) | S | was BENCH |
| HOSE_GIRTH_TUNE_MUCH_THINNER | doing | game-up | art | (area default) | S | was BENCH |
| HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES | validated | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| HOSE_LAY_POLISH_CENTRE_VS_MOUTH | proposed | offline | code C# | HoseMath.cs, RM_MapComponent_Hoses.cs | M | was BENCH |
| HOSE_NOZZLE_DIAGNOSE_HUGS_WALL_ENDS | proposed | offline | proof | (area default) | S | was BENCH |
| HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| HOSE_REEL_FIX_TURNS_WITH_THE_SHIP | built | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS | validated | bridge (live check owed; code built) | code C# | HoseWallSeamChecks.cs | S | was BENCH |
| HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD | validated | bridge (live check owed; code built) | code C# | (area default) | M | was BENCH |
| HOSE_SIDEPORT_FIX_AIMS_AT_OLD_MIDPOINT | proposed | offline | code C# | (area default) | M | was BENCH |
| HOSE_SPLICE_BUILD_MATES_BY_SLOPE | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| INSITU_ART_JUDGE_SAVES_KEPT_WARM | proposed | owner | art | (area default) | S | was BENCH |
| JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX | built | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED | proposed | owner | proof | LiquidJoinRule.cs | S | was BENCH |
| MISSION_TANK_GOAL_REWIRE_TO_DEST | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL | proposed | offline | art | (area default) | S | was BENCH |
| MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY | proposed | offline | art | (area default) | S | was BENCH |
| MODERN_REEL_SHADOW_FIX_BOX_TOO_BIG | built | bridge (live check owed; code built) | art | (area default) | S | moved |
| PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE | proposed | offline | art | (area default) | S | was BENCH |
| PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE | built | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| PIPE_GIRTH_TUNE_HALF_AS_THICK | doing | game-up | art | (area default) | S | was BENCH |
| PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL | built | bridge (live check owed; code built) | code C# | RM_FlowKernel.cs, RM_MapComponent_Excavation.cs, RM_PumpMath.cs | M | was BENCH |
| PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY | proposed | offline | code C# | (area default) | M | was BENCH |
| PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| POND_PUMP_FIX_LAST_DROP_COUNTS | built | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| PROOF_REELS_FIX_STILL_STAGED_WEST | built | bridge (live check owed; code built) | proof | (area default) | S | was BENCH |
| PUMPSTATION_COUPLER_MATCH_FIX_STEEL | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| PUMP_ART_RESKIN_LESS_GARDEN_HOSE | built | bridge (live check owed; code built) | art | (area default) | S | was BENCH |
| PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES | built | bridge (live check owed; code built) | art | RM_PipePoleMath.cs | S | was BENCH |
| PUMP_STATION_REDRAW_PLUMBED_FOR_GIANTS | proposed | offline | art | (area default) | S | was BENCH |
| REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED | built | bridge (live check owed; code built) | art | (area default) | S | was BENCH |
| REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT | built | owner | code C# | (area default) | S | was BENCH |
| REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH | built | owner | code C# | (area default) | S | was BENCH |
| REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON | built | bridge (live check owed; code built) | art | (area default) | S | moved |
| SPRINKLER_HEADS_BUILD_PUMP_REQUIRED | doing | offline | code C# | (area default) | M | was BENCH |
| TANK_DEBUG_BUILD_FILL_AT_WILL | proposed | offline | code C# | (area default) | M | was BENCH |
| TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY | built | bridge (live check owed; code built) | art | (area default) | S | moved |
| TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR | built | bridge (live check owed; code built) | art | (area default) | S | moved |
| TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID | proposed | bridge | proof | (area default) | S | was BENCH |
| TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT | built | bridge (live check owed; code built) | art | (area default) | S | moved |
| UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK | proposed | offline | art | (area default) | S | moved |
| UNDER_COUPLER_DECIDE_CORNER_CROWDING | built | bridge (live check owed; code built) | design | (area default) | S | moved |

### A: Liquids / levels / heat / ledger / ponds / worldtags / thirst (Wave 1, 28 items)
Default files: FlowWorks/Source/Liquids/** (RM_Liquid*.cs, RM_FlowKernel.cs), RM_MapComponent_Excavation.cs, RM_WaterLadder.cs

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| ASH_FIELD_FIX_FORGETS_THE_WATER | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES | built | bridge (live check owed; code built) | art | RM_WaterLadder.cs | M | moved |
| CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES | proposed | bridge | art | (area default) | S | moved |
| DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| FLOWWORKS_CONTAINER_MATERIALS_1 | validated | bridge (live check owed; code built) | code C# | RM_ContainerMaterialMath.cs, RM_ContainerMaterials.cs | L | was BENCH |
| FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST | built | bridge (live check owed; code built) | code C# | CompLiquidConverter.cs | S | moved |
| FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT | built | bridge (live check owed; code built) | code C# | RM_LiquidReaction.cs | S | moved |
| FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO | validated | bridge (live check owed; code built) | art | RM_MapComponent_Excavation.cs | S | moved |
| HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE | validated | bridge (live check owed; code built) | code C# | RM_LiquidHeat.cs | S | moved |
| LAVA_LIQUID_BUILD_PROMISED_BY_CARD | validated | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS | built | bridge (live check owed; code built) | proof | (area default) | S | was BENCH |
| LIQUID_BOTTLE_LOOP_1 | built | bridge (live check owed; code built) | code C# | Building_LiquidTank.cs, LiquidDef.cs, RM_LiquidBottleUtility.cs | L | moved |
| LIQUID_LEDGER_BUILD_NO_UNIT_LOST | validated | bridge (live check owed; code built) | code C# | (area default) | L | was BENCH |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1 | built | bridge (live check owed; code built) | art | (area default) | S | moved |
| LIQUID_THIRST_CHAIN_1 | built | bridge (live check owed; code built) | code C# | (area default) | L | moved |
| NATURAL_HEAT_CACHE_PROVE_STALE_DAYS | validated | bridge (live check owed; code built) | proof | (area default) | S | moved |
| POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD | validated | bridge (live check owed; code built) | code C# | RM_MapComponent_Excavation.cs | S | was BENCH |
| SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| TAKEN_BY_LAND_SERVICE_1 | validated | bridge (live check owed; code built) | code C# | RM_RiverWorksProof.cs | S | moved |
| TAR_COOLING_GLASS_MEND_ENGINE_CELLS | validated | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY | doing | offline | code C# | (area default) | M | was BENCH |
| WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED | built | bridge (live check owed; code built) | art | (area default) | L | moved |
| WATER_DEPTH_RESKIN_HE_LOOKS_FIRST | proposed | offline | art | (area default) | S | moved |
| WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT | built | bridge (live check owed; code built) | art | (area default) | M | moved |
| WATER_SCENES_S5_JUDGE_THIRD_DRAFT | proposed | owner | art | (area default) | S | was BENCH |
| WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID | built | bridge (live check owed; code built) | art | (area default) | M | was BENCH |
| WORLDMAP_LIQUID_TAGS_1 | built | bridge (live check owed; code built) | code C# | RM_GenStep_LiquidShores.cs, RM_LiquidBodyDef.cs, RM_WorldComponent_LiquidTags.cs | S | moved |

### F: GSS / aerial cords (Wave 1, 12 items)
Default files: src/RimMandrake/GimmeSomeSlack/**; FlowWorks Aerial (CompAerialAnchor.cs, RM_MapComponent_Aerial.cs)

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| CORD_GRAPH_TOPOLOGY_REVISION_1 | built | bridge (live check owed; code built) | code C# | (area default) | S | GSS |
| CORD_LOOP_UNTANGLE_LASSOED_A_PIPE | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| FALLEN_WIRE_SHOCK_1 | validated | bridge (live check owed; code built) | code C# | RM_FallenWireShock.cs | M | GSS |
| GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 | validated | bridge (live check owed; code built) | code C# | (area default) | S | GSS |
| GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT | proposed | bridge | code C# | (area default) | M | was BENCH |
| GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED | proposed | bridge | art | (area default) | S | was BENCH |
| JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS | proposed | game-up | proof | RM_Swim.cs | M | GSS |
| MAST_PIPE_MEND_STOPS_SHY | proposed | offline | code C# | (area default) | M | was BENCH |
| PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE | validated | bridge (live check owed; code built) | code C# | (area default) | M | was BENCH |
| PIPE_POLE_REDRAW_NOT_A_POWER_LINE | proposed | offline | art | (area default) | S | was BENCH |
| PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES | built | bridge (live check owed; code built) | design | CompAerialAnchor.cs, RM_MapComponent_Aerial.cs, SectionLayer_RM_AerialGround.cs | M | GSS |

### E: Rivers / weirs / settings (Wave 2, 14 items)
Default files: FlowWorks/Source/Rivers/** (RM_River*.cs, RM_PlaceWorker_RiverWeir), Settings kit (_Shared/SettingsKit*, RM_*Settings.cs)

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| FLOWWORKS_CHECKOUT_SCOPE_1 | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING | built | game-up | code C# | (area default) | S | moved |
| FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM | built | bridge (live check owed; code built) | code C# | RM_RiverColors.cs | S | moved |
| RIVER_MUFFALO_FIX_SHOWS_ITS_REAR | built | bridge (live check owed; code built) | code C# | (area default) | S | was BENCH |
| RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS | proposed | bridge | art | (area default) | S | moved |
| RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED | built | bridge (live check owed; code built) | proof | (area default) | L | moved |
| RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS | proposed | offline | art | (area default) | S | was BENCH |
| SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST | built | bridge (live check owed; code built) | code C# | RM_HoseSettings.cs, RM_PyrelandsMod.cs | L | was BENCH |
| SETTINGS_SCREEN_KIT_1 | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND | built | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| SURFACE_RIVER_WEIRS_1 | validated | bridge (live check owed; code built) | code C# | (area default) | S | moved |
| TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS | built | bridge (live check owed; code built) | proof | (area default) | S | was BENCH |
| TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES | proposed | bridge | proof | (area default) | S | was BENCH |
| WEIR_CATCH_FIX_NO_FREE_FISH | built | bridge (live check owed; code built) | code C# | (area default) | M | was BENCH |

### P: Proofs / north star / test envs / selftests / review (Wave 2, 13 items)
Default files: FlowWorks/northstar/*.py, validation*.py, SelfTest/*.cs (python/selftest only)

| ID | state | needs | kind | named files | size | origin |
|---|---|---|---|---|---|---|
| FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING | proposed | owner | proof | (area default) | S | was BENCH |
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1 | built | bridge (live check owed; code built) | proof | (area default) | M | moved |
| FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1 | proposed | bridge | proof | (area default) | S | moved |
| FLOWWORKS_NORTHSTAR_TRIAL_1 | built | bridge (live check owed; code built) | proof | (area default) | L | moved |
| FLOWWORKS_PLAYTEST_CAMPAIGN_1 | proposed | offline | proof | (area default) | S | was BENCH |
| FLOWWORKS_REVIEW_LOOKS_ROUND_1 | proposed | offline | art | (area default) | M | was BENCH |
| FLOWWORKS_VISUAL_PRINCIPLES_1 | validated | bridge (live check owed; code built) | code C# | (area default) | M | moved |
| FW_SELFTESTS_MEND_TWO_RED_AFTER_PARITY | proposed | offline | code C# | DrawbridgeChecks.cs | M | moved |
| NORTH_STAR_WALK_AUTHORING_1 | ready | offline | proof | (area default) | M | was BENCH |
| SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY | built | bridge (live check owed; code built) | proof | (area default) | S | was BENCH |
| TESTENV_MEGAPEDE_HARDEN_GATECRASHER | built | bridge (live check owed; code built) | proof | (area default) | S | moved |
| TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME | built | bridge (live check owed; code built) | proof | (area default) | S | moved |

## Needs the owner (judge / look / decide)

- FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING (proposed)
- INSITU_ART_JUDGE_SAVES_KEPT_WARM (proposed)
- LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED (proposed)
- PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS (validated)
- PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE (built)
- PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS (proposed)
- REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT (built)
- REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH (built)
- WATER_SCENES_S5_JUDGE_THIRD_DRAFT (proposed)

## Candidates for the seat to close (DONE / dead, with the proof in the item notes)

| ID | proof |
|---|---|
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1 | Owner card 2026-10-21 (note 10-22): small test list suffices for final GREEN, full-list GREEN not required -> close/drop as not required |
| PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL | Owner 2026-10-21 note: "Owner keeps the built behaviour" -> close against built sha |
| SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS | Note 2026-10-15: "FIXED 17e90dc6ca" (HasJobOnCell/JobDriver refuse edificed cell); state still proposed -> close with that sha |
| PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT | Note 2026-10-23: "Live look DONE (redraw 8 deployed; C12 ...)" -> close |
| SUSPENSION_ART_RESKIN_HE_SEES_FIRST | Note 2026-10-19: title superseded by owner 10-18 ruling (new art accepted first time); installed; validated L2 -> close, leftovers refiled |
| NORTH_STAR_WALK_AUTHORING_1 | Note 2026-10-21: drafting DONE (91 walks, 653d9c7d3a); remaining is generic north-star work, not FlowWorks-owned -> close drafting part / re-scope |
| LIQUID_THIRST_CHAIN_1 | Note 2026-10-17: thirst + bottles built under THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (43266db9aa, 77ef5bfcc8) -> supersede by that item |
| CORD_GRAPH_TOPOLOGY_REVISION_1 | Note 2026-10-11: DrawMotion half built (2c5974430); topology half deliberately NOT built per FOUNDRY 10-09 -> drop remainder / close |
| SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY | Note 2026-10-22: fix published 35a8d1d8ae (harness only, no DLL change) -> close after one L5 rerun green (or close on that sha) |
| PROOF_REELS_FIX_STILL_STAGED_WEST | Re-check 2026-10-23: PORTS_CORNER_REFUSED PASS x2 fresh maps -> close candidate |
| LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS | Re-check 2026-10-23 round 3a: overflowDestroyedTotal/releaseLostDl stayed 0 over every watched call -> close candidate |
| WATER_DEPTH_RESKIN_HE_LOOKS_FIRST | CORRECTION note 2026-10-23: 5m/10m tints ARE built (a96dbf99f, a6d324164) -> likely done except owner look; seat to re-read |
| WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED | Triage note 2026-10-22: "nothing built"; sheet letter A = already-installed 0.5 m art -> likely dead/superseded by WATER_DEPTH_RESKIN; seat to confirm |
| HOSE_LAY_POLISH_CENTRE_VS_MOUTH | Re-checked 2026-10-18: F4 fixed 79902641c6, F5 not a bug; only F2 (visual, live check) remains -> shrink to F2 |

These are note-based, not re-measured here; close only after the seat re-reads each.

## FlowWorks items held by OWNER seat (not reassigned; they are his / mid-edit with a lease)

- SLIME_CROSSING_BUILD_SLIPPERY_SLOPE
- FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS
- FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES
- TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH
- REVIEW_SCENARIOS_BUILD_ALL_TWELVE_AT_ONCE
- PIT_LIP_FIX_BOAR_HANGS_OUT
- PIT_LADDER_REDRAW_HUNG_ON_THE_WALL
- FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS
- LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS
- HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY
- THIRST_RULES_BUILD_SALT_OFF_THE_MENU
- TAR_LOOK_TUNE_THICK_AND_SLOW
- GSS_CORD_SILENCE_PHANTOM_SPARK
- SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR

Seat to decide whether to reclaim these too (OWNER rows with leases, "doing offline"); they were left because their owner field is OWNER, not FOUNDRY.

## Judged NOT FlowWorks (stay FOUNDRY)
FOUNDRY items that merely depend on or mention FlowWorks: SWALE_CANAL_ART_REFERENCE_1, CRACKEDLANDS_MECHANICS_BUILD_1, WARSCAR_RAINBOW_POOLS_1, FORGE_CYCLE_MECHANICS_1, HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1, SUMP_TAR_NASTINESS_1, SUMP_WALKWAYS_1, SCALD_MECHANICS_1, VEXXITH_USES_1, AQUATIC_WATER_BREATHING_GENE_1, GLASS_TO_TRANSPARISTEEL_1, STILLSAND_SOLAR_STILL_1, HUTT_SLAVE_PIT_TEST_SITE_1, VAULT_DUNGEON_BUILD_1, COLD_LOAD_RUN_SHEET_4, WORLD_RIVERS_REPAIR_DOWNHILL_AT_LAST (dev world tiles), RIVER_STEAM_ANIMATION_1 (Pyrelands visual), LIQUID_INDUSTRY_SETPIECES_1 (WreckedMachines set-pieces), MESSYCONDUIT_CABLE_PILE_LOOK_1 (MessyConduit), TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT, NORTHSTAR_PROCESS_RETRO_1, DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN. Borderline, say if you want them moved.
