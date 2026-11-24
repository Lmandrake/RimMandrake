# FlowWorks: Polish list

Polish improves play but is not part of passing 0.1.0. Each entry here is moved only with his confirmation, marked in the decision (owner, by card 2026-11-13).

*Empty at entry on 2026-11-13: no open judge gap sorted as Polish.*

## From blind challenge cycle 4 (run judge-1795134433), moved here by the Conductor's instruction of 2026-11-19

Source rows: `blind_challenge/cycle_4/lane2/faults.json` (class Polish, status NOTED_FOR_CONDUCTOR). Nobody fixes these for 0.1.0.

- `RIMMANDRAKE_NOTE_FLOWWORKS_OVERSPILL_SHIPS_SWITCHED_OFF` (inv_overflow_sheet): `RM_SheetSettings.sheetOverflowEnabled` ships false ("off until the live walk signs it off"); flip the default after his walk signs the overspill off.
- `RIMMANDRAKE_NOTE_FLOWWORKS_CONVERTER_PARTIAL_MOVE_UNCHARGED` (inv_converters): in `CompLiquidConverter.CompTickRare` a part-made move (0 < moved < n batches) leaves the batches it made uncharged (budget, totals, fuel, rotation).
- `RIMMANDRAKE_NOTE_FLOWWORKS_SPRINKLER_PICKS_BEFORE_RESERVE` (inv_sprinklers): `RM_Sprinkle.MostHeld` picks the liquid by raw stock, then pays from the reserve-reduced stock, so a net whose most-held liquid is all reserved reads Dry while another sprayable liquid is spendable.
- `RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH` (inv_flow_level): the kernel fuzz's volume law does not see an unreported sink drain on `RM_FlowKernel.cs:851` (planted `CHANGED_FUZZ_SINK_UNREPORTED`, rc 0).
- `RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED` (inv_looks): `selftest_glow_tank_live.py` does not pin the scene room's size (planted `CHANGED_GLOW_ROOM_SHORT`, rc 0).

- Pawn shadows reach outside a pit (his walk 2026-11-20: "Nice to have if easy, don't go crazy trying for it."): the pawn ground shadow is already skipped for a pawn drawn sunk in a cut (`RM_Patch_PitHidesShadow`, `Source/Superdeep/RM_PitDepthDraw.cs:417-436`); which shadow he saw is unread; no cheap fix found offline. No ticket.

- Pit relief corner pieces (RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN): under clear water only the dry part of a north corner piece is drawn; its drowned part shows the floor under the sheet (the far wall and side strips have drowned redraws, the corner has none). A scorched corner piece carries no soot. The old flat-look fallback (`excavationWallMaterialEnabled` off) draws no floor shade, corner or face foot.

- Removed row `body_cover_is_a_look` from `PIT_LOOK_1114_LIVE` (RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE): it was `None` by construction, so the scene read UNMEASURED every visit; it decides no bar (the scene only supports inv_pits, inv_pit_access, inv_looks, ways_in_and_out). The drowned-body cover is a picture and his walk decides it (LOOK_STAGE8: FAIL on 2026-11-20, fix owned by RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES).

- A Gimme Some Slack power switch drowned in a cut keeps its lamp (lens and halo) above the water: SwitchLightDraw draws every frame outside the realtime gate (pit draw census, LISTED gap, 2026-11-21). The bottom distortion the water judge saw in BLEND is not built: the only moving-texture engine shader paints lava colours (water_by_depth_target.json effects.bottom_distortion).

- Frozen-pond crust ice (RIMMANDRAKE_FIX_FLOWWORKS_FROZEN_POND_CUT_LEAVES_NO_CRUSHED_ICE, 2026-11-21): a pond dug in ICE ground, frozen (ThinIce), cut by a machine at superdeep where the deep stone resolves, leaves no crushed ice (CrustYield skips ice ground, IceCut yields to the deep stone); a colonist's 2 m cap never reaches it. The crust's ice melts to a notch of water the pond does not pay for; bounded by the rolled-depth guard (one per depth per square). `FrozenCrustTerrains` names only vanilla ThinIce.

- Flow-sink film (RIMMANDRAKE_FIX_FLOWWORKS_SINK_STOPS_ON_LAST_DECILITRE_FILM, 2026-11-21, fresh reader of 2083f92acb): an edge sink alone still orders the remainder by plain BFS hops, so a shallow edge sink nearer than a deep one would hold a deep body's last dL the way the flow sink did (same class, never seen to fail; left to keep level_water.py's sinkHops twin exact). Also: a filtered sink still names squares of a liquid it never takes (harmless reorder); DeepestSinkHops allocates its key lambda each call and costs n log n on a partition (tens of ms at a 50k-cell cap, default 6000).

- Review-site geyser (RIMMANDRAKE_JUDGE_FLOWWORKS_PALE_BLOCKS_IN_TWO_METRE_PIT, 2026-11-21): `jawa/destroy_batch` skips `destroyable=false` things, so a vanilla SteamGeyser inside the owner review site rect (visit 3: (59,141), 5 cells north of station 21) stays and puffs steam over the shallows row. The pale squares in station 21 were not FlowWorks: they were TheForge's vapour-column haze round that geyser. That haze is removed on every map (RIMMANDRAKE_REMOVE_FORGE_GEYSER_PALE_MASK_KEEP_THE_SWIRLING_STEAM, 2026-11-21). The geyser and its puffs are vanilla and leave the water readable; not worth a stager change.

- Solid-deck fire per exposure (RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN, 2026-11-22, fresh reader): `SolidDeckRolls` is checked only by source regex, so dropping its record write (`deckExposedTick[p.thingIDNumber] = now`) would pass the selftest while every check rolls again; a fire that ends and restarts within 120 ticks is the same exposure (fits the ruling); `DeckExposureExpired` is a second name for `DeckExposureRolls`; the case's `"0.000"` float format is locale-dependent.

- UND_crush harm read (RIMMANDRAKE_CONFIRM_FLOWWORKS_VISIT_SEVEN_EXIT_MET, 2026-11-22, steward): `new_harm()` in `suspension_bridge_proof.py` counts any severity rise as harm, so a BloodLoss that grows from an earlier wound also reads as harm. The row also needs the mod's crushed counter to rise, so no false PASS is known.

## From the FlowWorks ticket sweep of 2026-11-22 (RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE)

Each ticket below was dropped as `not worth the touch` (test 1 of standing_rulings.md §Touching code has a cost: no broken promise in ordinary play, no failure that happened, no red test). One line each, as the record. Nobody fixes these for 0.1.0.

- `ALL_OFF_FIX_DEPTH_ENGINE_STAYS_ON`: all_off() leaves the reload-latched depth engine on; use the _setting() path if an all-off row ever reads a false MOD fail.
- `AUTO_SPLICE_FIX_SKIPS_OBSTACLE_CHECK`: Automatic hose splice shaping skips the obstacle and hose-length checks, so a spliced hose can draw past its reel's length (GPT review FB_hose_gss_1.7).
- `CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS`: CordPlanner/HoseMath.CheckReplan have no A* node-expansion counter for the hose replay harness to ceiling.
- `COVER_BLAST_FIX_DECK_LEFT_INTACT`: A blast that destroys a pit cover's first cell can leave the rest of the deck standing (GPT review FC_pits_superdeep_1.8).
- `DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL`: deep_stone_live: superdeep-cut row stayed UNMEASURED on a spore map (SITE); rerun on a spore-free tile.
- `DEEP_STONE_PROOF_FIX_RERUN_LETTER_FAILS`: deep_stone_live.py fails a correct rerun on the same map because it demands a second first-find letter; use --fresh-map.
- `FIRE_RAIN_DIAGNOSE_BRIDGE_NAPS_MID_DOUSE`: testq fire_rain: a bridge 30 s timeout reads as FAIL instead of a harness cause (2026-11-04, once).
- `FLOWWORKS_PROOF_POKES_RESTORE_PRIOR`: Seven C# proof probes (HoseProbe, RM_SuspensionProofs, RM_WaterLookProofs) leave DevMode/godMode/water-look toggles set if they throw (proof_restore_check BASELINE).
- `FLOWWORKS_TOGGLES_BUILD_SIX_PREDICATES_OWED`: FlowWorks: liquid_drilling and typed_shores toggle chains still read 'owed, no predicate yet' (EXTENSION_TOGGLES_OWED); 4 of the 6 were written 2026-11-12.
- `FUEL_FIRE_SELFTEST_FIX_SQUARE_COVERAGE`: Fuel-fire detonation selftest checks a square, not BlastRadiusFor's real radius (GPT review FE_cs_selftests_1.2).
- `GLOW_TANK_PROOF_FIX_BLIND_READ_PASSES`: glow_tank_live.py setting-off row reads PASS when the final inspect returns nothing; should read UNMEASURED.
- `HARNESS_REPAIR_CAUSE_13905C1C`: one native mono crash in a FlowWorks testq load 2026-11-15; refile if the signature repeats.
- `HARNESS_REPAIR_CAUSE_BE6F3534`: one load_hang on stevedesktop 2026-11-21 (J20261121T205538Z-b4095c); later jobs loaded; reopen only if seen again.
- `HOSE_LAY_POLISH_CENTRE_VS_MOUTH`: Hose: a feeder reel whose lay is refused still counts as feeding its receiver, so the receiver's lead-out is suppressed (visual, rare).
- `HOSE_LOOK_DIAGNOSE_INDUSTRIAL_NEVER_BUILT`: validation_hose.py style_hose: the Industrial reel at (117,120) never became a building in one Steve run; re-check on the next hose proof before suspecting the mod.
- `HOSE_PLUMP_FIX_SAME_LENGTH_AS_FLAT`: Hose H6: a filled (plump) hose keeps the flat hose's pose length; the row expects it shorter. Decide the row or the pose; nobody sees it.
- `HOSE_REPLAY_BUILD_LIVE_RECORDER`: Hose replay: a live RMREPLAY trace recorder would let hose_replay.py replay a real colony, not only the generated corpus.
- `HOSE_SCHEDULE_UNIFY_REPLAY_AND_GAME`: hose replay and game schedules are two copies; unify only if they drift.
- `JOBPROBE_FIX_CANREACH_FALSE_WHILE_REACHED`: jawa/flowworks_job_probe reports canReach=False for a mid-channel fill cell colonists do reach (PathEndMode mismatch, line 122).
- `JOINED_WEIR_BREACH_FIX_CATCH_UNTOUCHED`: joined weir: a breach away from the run head leaves the head's held catch on the bank (RM_Weir.cs:432 washes own HeldCatch, not RunHead's).
- `LADDER_CLIMBERS_PRUNE_GHOST_GERMS`: FlowWorks_LadderClimbers.xml still names IronScruff_Hydrazoa/Jellybird/Tardigrade of the retired Primordial Geysers; drop them next time the file is touched.
- `LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS`: pipe_levelling_perf_proof --rehearsal stages its basins over walk_gaps_proof's ponds when both run on one map; run them on separate maps.
- `OUTFLOW_REGRESSION_FIX_HARDCODED_CAP`: fw_pond_outflow_regression CAP=30 is stale (beds are notches x volumePerTile) and never asserts channel fills; northstar-only, no current gate.
- `PERF_SCENE_REMEASURE_BASINS_OFF_EDGE`: Pipe-levelling perf scene digs its basins inside the 10-square edge band, so with edge sinks on it times drain churn rather than levelling; re-stage basins 10+ squares in if levelling cost is ever re-measured.
- `PIT_RAIN_FIX_FRACTIONAL_HEADROOM_FULL`: Rain on a pit square with less than one notch of room runs over the lip instead of topping it up (RoomNotches whole-notch).
- `PLACER_SELFCHECK_FIX_LEAVES_MERGED_ORE`: placer selfcheck cleanup tracks only new Thing ids, so ore merged into a nearby stack stays (RM_PlacerWorks.cs:719).
- `POCKET_TRAP_FIX_LADDER_TO_SEALED_POCKET`: RM_PocketGrid.TrappedIn treats a ladder into a second sealed pocket as an escape (one-hop check); walk the ladder graph if nested pockets ever matter.
- `PROOF_TIERS_WIDEN_FOUR_FULL_LIST_HOLDOUTS`: preflight_flowworks P-O4 and three other harness defaults still assume the full mod list (small-lists-first).
- `REVIEW_STAGE_FIX_SMALL_MAPS_HELD_GATES`: owner_review_stage.py:484 cuts gate_open's report to 60 chars and does not re-read the gate state, so a held-open gate can log as shut.
- `RIMMANDRAKE_ADD_OVERLAY_PROOF_HOOK_LAW_CANNOT_SEE_ICONS`: FlowWorks proof: ProofOverlays reads the law's decisions, not the alpha drawn last; the battery bar and GenDraw lines stay unseen (676c5cd131 partial).
- `RIMMANDRAKE_BATCH_PIT_REPORT_READS_IN_PIT_EXPOSURE`: pit_exposure_live spends ~25 s of a 64 s run on 450-500 single pit_report calls; batch one report per sample hour.
- `RIMMANDRAKE_COVER_REALTIME_MINIFIED_UNDER_LIQUID`: A realtime-drawn minified thing (MinifiedThingRealtimeDraw) in a liquid pit may still draw whole; unconfirmed, not in the pit draw census.
- `RIMMANDRAKE_FADE_LAID_HOSE_ON_PIT_FLOOR_LIKE_CORDS`: Hoses, pipe joins and under-couplers laid on a flooded pit floor draw crisp instead of faded under the liquid.
- `RIMMANDRAKE_NOTE_FLOWWORKS_SHEET_TOOLTIP_TWO_CM`: Crops-drown tooltip says 'at least 2 cm'; the kernel's standing tier starts at 3 cm rising (2 cm falling).
- `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_TIER_EDGE_LANE_ONE_ONLY`: T_SHEET does not pin the 3 cm sheet-tier boundary (lane 1 only).
- `RIMMANDRAKE_PIN_FLOWWORKS_SPRINKLER_RADIUS_DEFAULT_UNWATCHED`: No test pins the sprinkler radius default or its 25-square label.
- `RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER`: ProofSubmerge reports no shadow draw order, so whether a floor shadow draws over the liquid sheet is judged by his walk. The check's row OL_no_surface_shadow_under_sheet, always BLOCKED and deciding no bar, was removed 2026-11-23 (RIMMANDRAKE_SETTLE_FLOWWORKS_MOAT_MELEE_AND_DROP_BLOCKED_LOOK_ROW).
- `RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER`: pump_outflow_live.py and tank_theft_live.py reset liquidPumpEnabled to True rather than its prior value (waived at the setter, 9d3e4c2725).
- `RIMMANDRAKE_RETIRE_SPIKE_SUBMERGED_ALPHA`: RM_SpikeDrawMath.SubmergedAlpha is test-only dead code since RM_UnderLiquid; retire it with the next golden regeneration.
- `RIMMANDRAKE_SPLIT_GEYSER_PROOF_COUNTERS_EVERY_VENT_SHARES_ONE`: RM_GeyserPit plumeBubbles/dryPuffs counters are global, so a geyser proof cannot attribute a bubble to one vent.
- `SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD`: Steve chain test sites let colonists take ToxicBuildup, go down or die during the hold, so some runs end with no verdict.
- `SLIME_SELFTEST_FIX_SKIPS_MISSING_COST`: SlimeChecks pathCost regex skips a slime terrain that lacks <pathCost> or reads the next def's (bound the match to one TerrainDef).
- `STAGER_RESTORE_HARDEN_TWO_PATHS_UNCHECKED`: stage_proof_site.py: a make_map or tile-export failure sits outside the restore block, so an earlier maxLength 80 survives it, and the failure-path restore reply is unchecked.
- `SUNKEN_DRAWBRIDGE_FIX_REJECTS_HINGE_BANK`: Raising a sunken drawbridge rejects its own hinge bank as a landing, so every rider becomes overflow (GPT review FC_pits_superdeep_1.3).
- `SWIM_WARNING_FIX_ANY_PAWN_MESSAGE`: depth_rebuild_proofs SWIM_armour_warned_before_under takes '<=' and any pawn's message, so a drowning notice passes as advance warning; no current bar reads it.
- `TAR_LAG_FIX_NO_WATER_CONTROL`: The tar viscosity check (extensions.py:746-753) has no water control, so a water-speed tar front would also pass.
- `THIRST_CHAIN_UNSTICK_STILL_SIPPING`: testq thirst chain hung twice on SteveDesktop 2026-10-27 (harness: selftest stall, pawn_need timeout); not seen since.
- `VALIDATION_UNPOISON_AUDIT_STATEFUL_CHAINS`: validation.py chain-latch resets after an UNMEASURED row in 19 mods can make a later stateful row FAIL on an unbuilt fixture; audit per mod (Bacta fixed).
- `VV_MATRIX_FIX_SURFACE_FAILURES_UNDERCOUNT`: VV ShippedMatrixProbe surface 'failures' is max(settle,conservation,...) not the union count; rename to failures_lower_bound or count distinct scenes.
- `WALKS3_OUTFLOW_FIX_HOSE_WONT_JUMP_DITCH`: water_scenes_walk S3 lays its outflow hose onto a dug square; move the end to the bank (as sitting_gaps_proof does) if S3 is run again.
- `WALLREACH_READCHECK_HARDEN_SIM_LINGERS`: WallReachReadChecks.cs re-implements TickOwned's sliced read/cover/due policy instead of calling the shipped code.
- `WINSTAGE_CULL_THREE_GIGS_PER_KERNEL`: selftest_winstage.windows_project_path rsyncs the whole 3 GB src with --checksum for 13 callers (whole_src=True default).
- `WORKS_RUINS_BUILD_PREDICATE_TWO_FRESH_MAPS`: Ruined liquid works / ruin stock toggles (fresh-map only) and pipeAdaptersEnabled (needs VE PipeSystem) have no automated check.
- `RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN` (stations 61-64): the four steel-bridge looks share one suspension silhouette (twin posts, sagging main cable, hangers); the GPT art judge failed "the four looks read differently". He picked Scrapper C, Industrial A, Modern A and Futuristic A knowing this (2026-11-22). A different structure for the Modern (and perhaps Futuristic) bridge is a Designer question.
- `WINBUILD_STAGED_DEFS_STALE_TAR_CHECK_READS_OLD_COPY`: SelfTest `Submerge_defs_tar_dark_gates_shadowless` reads `../Defs/...` from the winbuild mirror (`D:\ClaudeWork\rimmandrake\build\FlowWorks`), which winbuild does not re-stage, so it fails on a stale RM_LiquidDefRegistry.xml while the repo's copy holds the dark tint (measured 2026-11-22).
- `RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON`: the cut edge of a pawn in an opaque liquid is a hard straight line; a ring at the line (design section 7, Polish) is not built. A held weapon is drawn outside the render tree and is not cut.
- `RIMMANDRAKE_CUT_FLOWWORKS_CORPSE_WOUNDS_FLOAT_ON_TAR`: the red splotches over tar in visit 8's big-pit shots are vanilla BloodSplash hit flecks (0.15 s of game ticks) of the scene's own killing blow, held by the pause; the corpses' real wounds are hidden under tar and tinted under water. `big_pit_scene.py` ticks no time after the kills, so a shot of it can show them; no bar reads it.
- 2026-11-23 liquid pump: a HOSE coupled on the pump's south still ends under the drawn cap (hoses draw below the building; read from code, not seen live); only a pipe is drawn over it (PumpSouthSocket). Recommended: next version.
