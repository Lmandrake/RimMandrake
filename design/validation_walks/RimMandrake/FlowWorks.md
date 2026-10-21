# RimMandrake FlowWorks — validation walk
subject: src/RimMandrake/FlowWorks  (packageId `mandrake.rm.flowworks`)
feature: canal-flood-engine
deps: Ludeon.RimWorld.Odyssey (Flood is Odyssey-gated in the base game); none third-party
list: minimal+Odyssey     # official DLC, not a workshop mod; check it is in the active list
checkout: src/RimMandrake/FlowWorks/northstar/manifest.py  (the walk's manifest: the core live proof validation_v2.py's declared_rows() UNION the hose live proof northstar/proof_hose.py's; results: validation_v2_result_*.json and proof_hose_*.json at the current mod hash)
status-hint: dig a canal cell, let a fluid reservoir prime and then drip + re-flood adjacent terrain on two cadences — species/biome-agnostic engine, water is the one shipped fluid

The reservoir era (`CompFluidReservoir`, `RM_FluidSpring_Test`, `Flood_FluidCanal`) ended with ruling 24
(2026-09-16): a source is a SUPERDEEP cell or a natural body, not a building. Every step below is written against
the depth/fill primitive (`RM_ExcavationDepth` on `RM_MapComponent_Excavation`, stock in `RM_LiquidStock`, bodies in
`RM_LiquidBody`).

## must be true
- The river's washed-away colonists, and the dune gale's carried ones (Stillsand), go through ONE hold-and-return service: held as world pawns, a letter when taken and when back, a ground trace (`RM_Filth_DragMark`, toggle `takenByLandTraceEnabled`) at the spot, the return scheduled and decided by one kernel (lost, died, back alive, back to die). → taken_by_land.service_has_river_policy_and_trace_setting (FlowWorksRivers suite); kernel offline: `selftest_flowworks_stock.py` case `TAKEN_BY_LAND_SERVICE_1_kernel_decides_return_outcomes_and_schedules`; the live take and return: UNCOVERED beyond `swept.returns_home` (needs a pawn at the river edge)
- Thick liquids creep (THICK_LIQUID_CREEP_1): with `thickCreepEnabled` a tar or slime fill front advances one cell per moving pulse down a 40-cell channel, where with it off the front crosses the whole channel in one pulse; water is unaffected; the pulse ledger stays balanced and the kernel still equals the oracle (3000 scenes). → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` case `THICK_LIQUID_CREEP_1_front_speed_down_a_40_cell_channel` (control: creep off races, 40 of 40) and `selftest_flowworks_kernel_oracle.py`; the in-game front speed needs a tar channel on a bridge map
- A canal network bigger than the partition cap (`maxNetworkCells`, default 6000) still wets end to end (FLOW_ORDER_EXTERNAL_INPUT_1 part 2): with `networkSeamsMoveEnabled` the partition seams move each pulse and every partition reads one network-wide flow order, so a 200-cell channel at cap 50 wets 200 of 200 and settles, where with seams fixed it stops at 49 of 200; a network inside the cap is pulse-for-pulse identical either way. Moving seams are slower than one uncapped piece (136 vs 200 wet after 400 pulses). → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` case `FLOW_ORDER_EXTERNAL_INPUT_1_part2_oversized_network_exchanges_across_seams`; the in-game pulse cost on a >6000-cell network (which decides whether the default cap can rise) needs a bridge timing
- `RM_DigCanal` designation exists and `RM_DigCanalJob`/`RM_DigCanalWorkGiver` drive a colonist to actually dig it (`JobDriver_DigCanal`, `WorkGiver_DigCanal`). → core `E8_player_dig` (a designated cell dug by a colonist reads D=1, `RM_Channel_Empty`), `J_workgiver_selection` (the work giver offers `RM_DigCanalJob` on the designation and no job on an undesignated dug cell), `J_orders_accepted`
- A flooded cell's *underlying* terrain is recoverable — `TerrainGrid.TopTerrainAt` (what remains once the flood drains) must differ from the temporary flood terrain and must not itself be destroyed. `Flood_FlowWorks.SpreadOneTile` writes `SetTempTerrain` + `QueueRemoveTerrain` and the flood terrains deliberately carry no `tempTerrain.destroysFloors`; the one permanent write is by design: `CoolFrontToGlass` sets the front cells of a fluid with `coolsToGlassEdge` (tar) to that glass terrain with `SetTerrain`, never on an excavated cell (its base terrain is the depth engine's, `RM_StockMath.MayCoolToGlass`). → UNCOVERED live: no core row or chain spawns a `Flood_FlowWorks` release and reads the cell after it drains; `jawa/flowworks_spawn_flood` plus `jawa/canal_cell_report` (`underneath`, `tempTerrain`) are the tools such a chain would use
- A flood that is walled in before its volume runs out destroys itself at `ExpiryTick` = `spawnedTick + 2 * FloodingTicks` rather than ticking into every save. → UNCOVERED live: same gap, no chain walls in a release and waits past 2×FloodingTicks; `jawa/canal_cell_report` already reports the flood's `expiresAtTick`
- `RM_Channel_Empty` (the dug-channel terrain, Diggable/Walkable/Light affordances, not itself water) is what a D=1 dig sets a cell to (`JobDriver_DigCanal`, or `jawa/flowworks_excavation_drive` in tests; `jawa/canal_dig` is a stub that always fails); D=2/3/4 set `RM_Channel_Mid`/`_Deep`/`_Superdeep`. → core `S1_dig_ladder` (D 1..4 read back as the four channel terrains, excavated +4, superdeep +1), `S1n_superdeep_is_max` (phase S runs at the 2 m dig-cap setting; the shipped cap is 8 m, a Mod Setting 2 to 20 m, PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT); the colonist route: `E8_player_dig`; the affordance list is read by no row
- Spread IS channel-constrained: `Flood_FlowWorks.CanFloodInto` always gates on `RM_MapComponent_Excavation.CanLiquidEnter`; the `channelConfinementEnabled` setting was retired (FLOWWORKS_CONFINEMENT_TOGGLE_VESTIGIAL_1) and there is no leak-across-open-ground mode. → core `E2_dry_ring` (every non-channel cell round the four direction scenes stays undug, F=0, Soil after the flow phase), `E2_channels_fill_every_direction`

- Flexible hoses (moved from Gimme Some Slack M11/M12 at the hose port, 2026-10-11; reel `RM_HoseReel`, pipe networks tab since ruling #4 2026-10-11): a hose lays as a thick, stiff hose round a wall, plumps within its transition when flow is on, never flickers on a fast toggle, collapses only after the release window, re-lays on a stiffness change; it solves a maze and re-routes or retracts with a reason when walled; relay reels chain past one hose's reach without a ring. A colonist carries a hose end: the trail follows his walk, drafting drops it with the order kept, the work giver resumes it to the target, a retract winds it in, the instant lay/reel-in gizmos exist only in dev mode; a dropped and a carrying reel survive a save, the carrying one resumes after the load. Each reel keeps its picked look (Scrapper/Industrial/Modern/Futuristic) through blueprint, frame, copy, reinstall and save; an unstyled reel draws FlowWorks' default look. → `FlowWorks/validation_hose.py` (H1b-H11, maze M1-M5/P1-P2, relay RL2-RL9, carry CR1-CR7), `FlowWorks/validation_style_hose.py` (R0-R7), offline `FlowWorks/validation_hose_offline.py` (HO5-HO8) and the "hose:" suites of `selftest_flowworks_stock.py`; the one-session live driver is `FlowWorks/northstar/proof_hose.py` (hose port step 8)

- The rigid universal pipe (`RM_UniversalPipe`; owner rulings 2026-10-11 #1/#8, `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`) is built in one of the wires' four looks (Scrapper/Industrial/Modern/Futuristic) picked on its build button through the shared `StylePickerCore` (`Source/Machinery/PipeLook.cs`), each look a Basic-linked atlas (`Defs/Machinery/RM_UniversalPipeStyles.xml`); an unstyled (older) pipe draws in the `pipeDefaultLook` setting; a selected pipe offers "Choose style" for itself or its whole run. The pipe, both tanks, the hose reel and the pipe adapters sit in the `VCHE_PipeNetworks` ("pipe networks") tab the Vanilla Expanded pipe mods share (ruling #4); pumps and stills stay in Production. No stored liquid ever solidifies (ruling #6, "Pitch stays pitch."). → pipe_looks.selftest_cases (offline: `selftest_flowworks_stock.py` cases `PipeStyles_*`, `BuildMenu_pipes_and_tanks_in_the_pipe_networks_tab`, `Pitch_never_solidifies_in_bulk`); live (menu opens, look survives blueprint → frame → building → save, atlas joins): UNCOVERED: needs a bridge session (FOUNDRY holds the bridge 2026-10-11); flow semantics of the pipe wait for the owner's liquid-network design pass (2026-10-11)
- Liquid moves conserve (liquid networks L1, `design/RimMandrake/liquid_network_semantics_design_2026-10-11.md` §4): every tank, world and VE-boundary mutation of the pump (draw from a channel, from a body, pour), converter, reactor, bath, pipe adapter and tank settle goes through `RM_LiquidTransfer.Move`, which validates both legs, runs the reversible (tank) leg first and the world leg last, and puts the units back on a refusal, so a refusal on either leg at either stage leaves every total unchanged and credits no hose; a converter's item output that finds no room stays pending (saved) instead of vanishing; the adapter reads the VE storage back after each call, puts a short accept back into the tank and carries the fractional remainder (saved), failing closed on a non-finite reading. → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` cases `Transfer_Move_refusal_on_either_leg_changes_nothing`, `Transfer_Move_composite_legs_are_all_or_nothing`, `Transfer_Adapter_boundary_conserves_with_carry`, `Transfer_site_*` (one per site, refusal injected on each leg, then the production site read) and `Transfer_caller_coverage` (FINAL's 11 credit sites + the tank settle, each inside a committed-Move block; no tank mutation outside the service but the listed bottle/ruin/probe paths); a live refusal needs a full tank or a foreign cell staged by the bridge
- The liquid network is components (liquid networks L2, rev 2 §3.1): pipe cells, relay reels and live hoses conduct; tanks and machines attach to every component they touch and never conduct, so a tank between two pipe runs is in both and the runs stay apart, and a tank–hose–tank pair is one component (each tank's store holds the other); a hose free end with a role is a port of its hose's component; a member's store does not depend on who asked first; components are built once per topology revision (a pipe/tank/machine spawn or despawn, any hose link change, the pipes or hoses switch), never per tick; a component over 3000 conductors and members is refused whole and its machines read "network too large". → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` cases `Net_tank_between_two_runs_is_in_both_runs_do_not_merge`, `Net_tank_hose_tank_is_one_component_of_one_conductor`, `Net_machines_do_not_conduct`, `Net_free_end_ports_attach_to_their_hose_component`, `Net_store_is_origin_independent_and_route_from_the_tree`, `Net_over_size_component_is_refused_never_partly_operated`, `Net_revision_bumps_on_each_listed_event`, and the hose suites `HoseNetChecks`/`HoseNetCacheChecks` (perf: 20 reels, 4 pumps, 10 tanks ≤ 0.05 ms/tick mean, ≤ 1 ms worst tick); the probe verb `net:` reports `componentBuilds`/`revisionBumps`/`tooLarge` for a live row
- Where liquid goes and comes from depends only on stock and tank id (liquid networks L3, rev 2 §3.2-3.3): a pump level, a converter's or reactor's output and an adapter's intake fill the fullest tank already holding that liquid, then empty tanks, lowest id on ties, and a level may split across tanks (3 + 2 units of room take a 5-unit level, where one tank used to have to take all 5); machine inputs, a bath and an adapter's send draw the emptiest tank holding the liquid first; two machines consuming one liquid take turns instead of the first-ticking one taking everything. → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` cases `Plan_three_plus_two_room_takes_a_level`, `Plan_fill_order_fullest_holder_then_empty_by_id`, `Plan_draw_order_emptiest_holder_first`, `Plan_two_origins_get_the_same_plan`, `Plan_consumer_rotation_two_machines_take_turns`, `Plan_callers_use_plans_and_rotation`; a live row needs two near-full tanks on one pump
- Tank jobs (liquid networks L4, rev 2 §3.2; owner ruling #9 "a tank would pass liquid on to a hose screwed into it, without a pump needed"): each player tank has a job button, Store (default; old saves load as Store) / Fill / Empty / Dump, saved as `rmTankMode`; once per pump cycle every component with a Fill or Empty tank settles: Empty tanks send to Fill then Store tanks, Fill tanks pull from Empty then Store tanks, at most `tankLitresPerCycle` (2,000 L) per tank, only from stock present at the start, never into another liquid; two Fill (or two Empty) tanks move nothing between them; Dump tanks never trade with tanks; pumps and machines never fill an Empty tank nor draw from a Dump tank; with `tankModesEnabled` off every tank is Store and nothing moves tank to tank (the old equalising hose feed is gone; the old `hose_tanksFeedHoses` value is read once). → `hose_switch_flips.flip_tankModesEnabled` (offline); also `selftest_flowworks_stock.py` cases `Settle_ship_Fill_loads_from_base`, `Settle_ship_Empty_unloads_to_base`, `Settle_two_Fill_tanks_never_take_from_each_other`, `Settle_Empty_Fill_Dump_on_one_component`, `Settle_moves_only_stock_present_at_the_start`, `Settle_empty_Fill_tank_rotates_liquids_by_cycle`, `Settle_production_tick_and_jobs`; live (ship tank on Fill loads from the base over a hose): UNCOVERED: needs a bridge session with a laid hose between two tanks
- Hose free ends have a role (liquid networks L5, rev 2 §3.4): a reel's "Free end:" button cycles Capped (default; old saves load Capped) / Intake / Outflow, saved as `rmFreeEndRole`; the role belongs to the end where it lies, so carrying the reel never flips it; an Intake or Outflow end lying free is a port of its hose's network, a coupled end is a plain connection whatever its role, and a role change bumps the network's revision; the cosmetic fitting button is now labelled "Fitting:"; with `freeEndRolesEnabled` off every free end is Capped and the button is hidden. → `hose_switch_flips.flip_freeEndRolesEnabled` (offline); also `selftest_flowworks_stock.py` case `Net_free_end_ports_attach_to_their_hose_component`; what an Intake or Outflow end does is L6/L7
- The pump is the only mover out of the world (liquid networks L6, rev 2 §3.3): it draws from water in its own reach and then from the water under or beside every Intake hose end on its network (never a dry end cell), and sends each level first to the network's Outflow ends (rotated, at most one level per end per cycle, only into a cell that can take that liquid, checked before the source level is taken; a refused pour puts the level back) and then into its tanks, so lake → pump → disconnected canal needs no tank; a blocked outflow falls through to the tanks and the pump says so; `levelsPerCycle` is the whole budget however many intakes; a pump on Pour (kept, Q3 "Keep it as faster draining") drains only tanks set to Dump, into its reach or out of Outflow ends, and a pour-mode pump with no Dump tank idles with one message per map; a drawing pump warns when another pump on its network pours. → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` cases `Pump_lake_to_canal_with_no_tank`, `Pump_blocked_outflow_falls_to_tanks`, `Pump_budget_is_shared_across_intakes_and_outflows`, `Pump_world_to_world_refusal_puts_the_take_back`, `Pump_pond_round_trip_conserves`, `Pump_production_world_mover`; live bars `NS_canal_from_lake_no_tank` and `NS_intake_needs_pump` are owed to a bridge session
- Outflow ends and the slow drain (liquid networks L7, rev 2 §3.5/§3.7): an Outflow end puts liquid into an excavated cell at or within 1.5 cells of it that can take that liquid (deepest, emptiest), or onto dry open ground as a cleanable spill (`LiquidDef.spillFilth`, tar's `RM_Filth_Tar`, else `RM_Filth_LiquidSpill`; one patch per `litresPerFilth` litres (400 L), so colonists clean it in the home area); a full or foreign channel, a wall or water is blocked and moves nothing; a tank set to Dump drains with no pump, `dumpLitresPerCycle` (1,000 L) per settle, out of the Outflow ends on its network (a whole level into a channel, any amount onto ground), and a Dump tank with no Outflow end waits; a pump's outflow and a pouring pump use the same outlet (a liquid with no channel form still leaves as a spill); an Intake end with no working pump, and an Outflow end with neither a pump nor a Dump tank, say so on the reel. → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` cases `Outflow_dump_drain_takes_levels_into_channels_any_units_onto_ground`, `Outflow_dump_drain_conserves_without_a_pump`, `Outflow_spill_filth_count`, `Outflow_production_outlet_spill_and_drain`; live bars `NS_dump_tank_drains_without_pump`, `NS_canal_from_lake_no_tank`, `NS_intake_needs_pump` are owed to a bridge session
- A hose holds liquid and spills it when it stops (liquid networks L8, rev 2 §3.7; owner Q2 ruled real: "you have to have colonists "clean it up" if it's in a cleanable area"): a hose a committed move crossed fills to ceil(length × `hoseLitresPerCell`) (5 L: 150 L for 30 cells), taken out of that move's own tank (or, pump world-to-world, the first levels go into the hoses), one liquid at a time (another liquid flushes the held one out of the far end first); saved as `rmHoseHeldLiquid`/`rmHoseHeldUnits` (an unknown liquid is cleared with one warning); when it stops carrying (holding switched off, wound, dropped, decoupled, capped, its lease run out, packed up or destroyed) it empties out of its free end, else at the reel: whole levels into a channel that takes them, the rest as a cleanable spill, never back into a tank; nothing is created or lost. → `hose_switch_flips.flip_hoseHoldsLiquid` (offline); also `selftest_flowworks_stock.py` cases `HoseHold_capacity_is_cells_times_units_per_cell`, `HoseHold_conserves_across_fill_change_of_liquid_and_stop`, `HoseHold_change_of_liquid_flushes_first`, `HoseHold_production_fill_flush_drain_and_save`; live (a spill in the home area gets a colonist Clean job): UNCOVERED: needs a bridge session
- Liquid theft, priced like power theft (liquid networks L9, rev 2 §3.4; owner card Q4 "allowed as theft"; ruling #7: 2 goodwill a day, 12-cell notice): another faction's tank or machine joins a hose or pipe network like the player's own (an unowned ruin always does); once per pump cycle each foreign tank whose stock changed (liquid taken out or put in, by any mover) counts as theft; the first time one of theirs (humanlike, awake, not downed, not our prisoner) within `liquidTheftSightRange` with line of sight sees it, a letter names them, and from then on every whole day of cycles with taking costs `liquidTheftGoodwillPerDay` goodwill (reason "liquid theft"); an idle tank accrues nothing; a faction at -100 or permanently hostile is skipped; with `liquidTheftEnabled` off a foreign tank never joins. The rule is a copy of Gimme Some Slack's (FlowWorks never references it). → `hose_switch_flips.flip_liquidTheftEnabled` (offline); also `selftest_flowworks_stock.py` cases `Theft_spotting_matches_power_theft`, `Theft_accrues_per_day_of_taking_and_idle_accrues_nothing`, `Theft_production_tick_join_and_switch`; live (a visitor sees a hose draining their tank, the letter, a day's charge): UNCOVERED: needs a bridge session
- A pipe adapter has three modes (liquid networks L10, rev 2 §3.10-3.11): Send into the VE pipe net, Take from it, or Shut (moves nothing); a newly built adapter starts Shut so two adapters never churn a loop through a VE net by accident, while an older save's adapter keeps its mode (`RM_adapterFeedNet` true = Send, false = Take; `RM_adapterShut` false on such a load); across the boundary the VE storage is read back after each call, a short accept goes back into the tanks and the fraction is carried (saved); a reflection failure or a non-finite reading shuts the adapter itself with one red line. → UNCOVERED live: proven offline by `selftest_flowworks_stock.py` cases `Adapter_save_keys_map_to_modes`, `Adapter_short_accept_puts_units_back`, `Adapter_production_modes`, `Transfer_Adapter_boundary_conserves_with_carry`; a live row needs VE PipeSystem, which is on no test list
- Liquid-network settings and cost (liquid networks L11, rev 2 §4): every switch and number of the network is a Mod Setting with the shipped default (`tankModesEnabled`, `tankLitresPerCycle` 2,000, `freeEndRolesEnabled`, `dumpLitresPerCycle` 1,000, `hoseHoldsLiquid`, `hoseLitresPerCell` 5 in the hose section; `litresPerFilth` 400, `liquidTheftEnabled`, `liquidTheftGoodwillPerDay` 2, `liquidTheftSightRange` 12 in machinery), each a typed registry row (`northstar/site_spec.py`); the network costs ≤ 0.05 ms per tick mean and ≤ 1 ms worst tick, rebuilds included, on the fixture of 20 reels, 4 pumps (1 pouring), 10 tanks (3 with jobs), 2 Intake and 2 Outflow ends; the probe verb `net:` reports builds, bumps, settles, dumped, spilled and drained units, moves, put-backs and theft. → `northstar/selftest_settings_registry.py` and validation_v2 O2 (offline registry equality); `selftest_flowworks_stock.py` hose suite `HoseNetCacheChecks` (rev 2 net perf); live worst tick on a real map: UNCOVERED: needs a bridge session (probe `net:`)

- Sprinkler heads (SPRINKLER_HEADS_BUILD_PUMP_REQUIRED, `design/RimMandrake/sprinklers_design_2026-10-16.md`, OQ-S1..S7 ruled by card 2026-10-16): `RM_SprinklerHead` stands on a universal pipe, needs no power but a working pump on its network ("No pressure: no pump on this network" otherwise, drawing nothing), and once an hour draws cells x 0.5 L from its net all-or-nothing, keeping its covered cells sprinkled until the next pulse plus 250 ticks; walls stop the spray; tar clogs it; acid/boiling spray hurts pawns in it and fuel leaves its spill filth; the VFE Farming sprinkler is adapted the same way and its waterless boost is skipped only in our biomes. → `sprinklers` (offline rows S0-S12 run off SprinklerChecks.cs; live rows `sprinkler.draws_and_wets`, `sprinkler.dries_when_starved`, `sprinkler.no_pressure`, `sprinkler.thick_clogs`, `sprinkler.liquid_key`, `sprinkler.acid_hurts_fuel_puddles`, `sprinkler.walls_stop_spray`, `sprinkler_switch_flips.flip_sprinklersEnabled`, `sprinkler.vfe_boost_skipped`, `sprinkler.vfe_valve` written, UNMEASURED, owed a bridge session)

- Ponds shallow out before they turn to mud (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, `design/RimMandrake/pond_depth_design_2026-10-16.md`, D1-D4 ruled 2026-10-16; owner D2: *"It should slosh around until it levels, pond or canal or otherwise."*): a LIMITED still-water pond keeps one flat surface s levels below its brim (its stock and bed record, nothing new per square); every square deeper than s shows bed - s (deep, then `RM_WaterChestDeepStill`, `WaterShallow`, `RM_WaterThin`), the last part-level is one connected patch, a square at or above the surface is mud for `pondMudDays` (2) and then cracked lakebed; refill raises the surface everywhere, and a dry square with a pawn or building waits; a pond feeds a ditch only while its surface stands above the ditch's water, and a canal two or more above a pond's surface runs back into it (mouth-paced, through the return leg); limitless bodies, moving water and other liquids keep full-or-empty squares; `pondDepthEnabled` off re-lays every touched pond back to its own water and the old shed rule; `pondHeadRuleEnabled` off is today's draw-to-empty. → `liquid_checks.L8_pond_shallows_before_mud` (OWED: written, never run live; needs a deployed DLL and `--l8-pond x,z` on a pumped station pond); offline `selftest_flowworks_stock.py` cases `PondDepth_S1`..`S8` and `selftest_flowworks_kernel_oracle.py` mode `pond` (head rule, kernel == PulseOracle); UNCOVERED: the mud-to-lakebed timer, the occupant wait and the toggle round trip in game (state reads owed to the same L8 session), and the canyon-flood exclusion (S6, not built)

- Dug ground gives cover (TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT, `design/RimMandrake/canal_cover_design_2026-10-17.md`, Q1-Q8 ruled 2026-10-18; owner Q1: *"This updates/replaces the old ruling that digging does not change shooting."*): a pawn standing in a dug hole, wet or dry, is covered by each neighbour whose ground is higher than its floor, read like a vanilla sandbag (angle and distance falloff): block 0.75 x clamp(h/H) x `trenchCoverStrength`, so 0.22 / 0.44 / 0.66 for a person at 0.5 / 1 / 1.5 m; a shot along the trench gets none, a shooter on the lip none, one back a third; an intact pit cover and natural water read 0; trench plus vanilla cover stack, capped by `trenchCoverCap` (0.9); the hit-chance tooltip shows "Trench wall: blocks N%"; a trench "miss" goes wild (never at a cover Thing); no blast cover; raiders read it through vanilla cover and, with `trenchAiAvoidsCages`, never pick a cast square in a pocket they could not climb out of; `trenchCoverEnabled` off = vanilla cover exactly. → offline: `python3 src/RimMandrake/Utils/selftest_flowworks_trench_cover.py`; live: `python.exe src/RimMandrake/FlowWorks/northstar/trench_cover_proof.py` (square-on 0.44, enfilade 0, lip 0, one back 0.147, wet = dry, hit falls by the block); raid cast squares, the cage guard live, grenade damage and the cast-search cost: UNCOVERED (owed rows in that script)

## the walk
Densified 2026-10-05 (`design/RimMandrake/northstar_densification_lessons.md`): ONE core live proof, then the feature chains. Steps 2 and 4 are BOTH the basic checkout (FLOWWORKS_CHECKOUT_SCOPE_1, 2026-10-11): every chain step 4 runs is ordinary Utinni play, and `debug_process.md` §6b keeps "extended" for mod-mod compatibility, declared incompatibilities and removal, which live in `## extended` below. A green step 2 alone says nothing about the step-4 features.
1. [O] `python3 src/RimMandrake/FlowWorks/northstar/validation_v2.py` — offline tier O1-O10 (defs incl. the four channel path costs, shipped settings, UNBUILT register, geometry, pulse oracle, scene predictions, lint, shared source, pit width), O-NEG (each offline check mutated red) and O-LIVE-NEG (a clean `--mock` live tier is green and every MockBridge fault turns its row red); `python3 src/RimMandrake/FlowWorks/northstar/selftest_extensions.py` (core/extension split and bar/toggle coverage); `python3 src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py offline`
2. [B] `python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply`, launch via Steam, then `python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map` from the repo root: one fresh 250x250 quicktest map, folded preflight rows (L1 fresh map, L2 tier live incl. Player.log + DLL identity + shipped settings, L3 live channel-def path costs, L4 site ready), S state (dig ladder to superdeep, clamp, classification, sink band, sticky, dig-to-depth gate), 0-tick flow phases A/B/C/R against the oracle (G_every_cell_vs_oracle), J pawn jobs (the only ticks: dig, fill-in displacement, engine off/on, cadence clamp, rain toggle), rain, P pit capture/ladder/carve-out, X pawn height, viscosity, fluid identity, cover, liquid fire (X10: lit, persists, burns out to ash), the fluid-switch refusal and ONE log budget (E9); one result JSON `northstar/validation_v2_result_*.json`
3. [B] record: `python3 -m modcheck.cli record FlowWorks --result <northstar/validation_v2_result_*.json> --tier flowworks`
4. [B] (every checkout, after step 2; basic per §6b, not extended) feature chains (still named "extensions" in the code): `prep_site.py` + `preflight_flowworks.py live` build and check the golden trial site, then `python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live [--chains ...]` runs the visual-trial plots (judge screenshots) and the optional-feature chains (fire reaching a reservoir, fire put out by explosion/foam/rain toggles, doors, spikes, ladders OFF, the superdeep prison room + capture down + lip service, the pump, bottle revert, wall faces, dig finds, bottles/tanks/drilling, shores, river steam, swale ...). Record both results together: `modcheck record FlowWorks --result <validation_v2_result> --extensions <extension_result>` -- a step-4 FAIL makes the checkout RED, and a missing or partial step-4 result leaves it REFUSED/UNMEASURED, never green
X. [S] (human pass) the look and the build state: `python3 src/RimMandrake/FlowWorks/human_review.py` writes the capability sheet `src/RimMandrake/FlowWorks/northstar/review/FlowWorks_review.html` (status per intended capability, derived from disk + the newest core result + the ledger); never a pass bar

## extended
Not run in a basic checkout and never blocks one; run only when requested (design/RimMandrake/debug_process.md §6b).
- E1. Removal: a save made with FlowWorks loads without it -> UNBUILT (no removal check yet)
- E2. Mod-mod compatibility: the third-party mods `About.xml` loads after (`sarg.alphabiomes`, `Dubwise.DubsBadHygiene.Lite`) running alongside FlowWorks -> UNBUILT (no tier or check yet)
- E3. Declared incompatibilities: `About.xml` names every mod known to clash and why; an older Gimme Some Slack that still carries the hose reel defs is the one known case (loadAfter + one red log line) -> UNBUILT (no check yet)

## north star
state: DRAFT
validated-hash: 

The `state:` line above is authoritative;
`design/RimMandrake/north_star_validation_spec.md` defines what each state means, and a
checklist binds only while that line reads VALIDATED. The recorded hash covers this whole
section, so any edit reverts it to DRAFT until he re-validates. Every bar is one observable
claim a player can check by looking, or, where the bar itself says so, read from the game's
state; where each came from is in the provenance table at the
end of this section, never in the bar text, because the bar text is the question the judge
is asked.

🔑 **A bar for a feature that is not built yet fails until it is built.** That is the bar
doing its job, not a reason to park it. Every bar below stays bound whatever the state of
the code or the art.

### the experience  (OWNER'S WORDS — verbatim)

The canal, bench session 2026-09-16:

> *"This mod allows the user to dig canals in the ground from an ambient source of liquid
> (fresh water, salt water, tar, propane, colored water, slime, etc from Many Waters if
> present or just water if not). at the liquid's viscosity (water is essentially zero)
> liquid then flows into the canal to fill it, extending the source. This brings the
> concept of a limited vs limitless source. Any source that touches the map edge is
> determined to be limitless. If it is fully encompassed by the map edge, then it is
> limited. Each source's square can supply up to five canal squares with liquid before it
> stops providing. This also brings with it a reduced graphic for the parent water source
> to show that it is strained. This same graphic can be reused should the player start to
> PUMP the water into tanks. One full tank can reduce a source of liquid (equivalent to 5
> filled canal squares). Incompletely filled canals spread the water throughout themselves
> using a graphic showing partial fill, and the parent body of water reduces itself in
> proportion as well. Pumping water out of a source or canal has the same effect. An
> unfilled pit slows movement as per other established dug barriers, while filled pits
> reduce as per that terrain cost. Some materials are flammable and thus the canals can be
> lit and burn for a very long time. They will also light their source at that time. Slime
> has the particular properly of being so slippery that it is nearly impossible to cross,
> and escape from the pit takes a great deal of time. The mod is intended to allow natural
> irrigation of crops (all plants nearby the canal react to the presence of the water as
> though watered)."*

His ranking the same session: **defense first, then irrigation, then industry, and finally
terraforming.** His scarcity ruling: **every source is stock**, refilling *"slowly, from rain
and season and ground liquids oozing in… it can take quite a while to fill up from a very
small natural source."*

2026-09-17, retiring the source object (ruling 34):

> *"Strained isn't a thing anymore. We replaced 'sources' with just placed deep liquid
> reservoirs just like a player would normally place on the map. Filled very deep tiles.
> Everything follows from that."*

The pit, 2026-09-13 and 2026-09-15, on seeing the shipped trap:

> *"Looks like it was working. But we need to think now about very deeply what it looks
> like. It can't just be a simple trap graphic you get stuck on. So we need a big dark
> pit."*

> *"A simple little trap that just Snares a pawn to stand there staring at the camera, stuck
> in a trap with "Pit" written on it. Not at all "falling in a pit" but I understand what
> happened."*

2026-09-17, collapsing the pit onto the canal (`PIT_SUPERDEEP_COLLAPSE_1`):

> *"I'm not really sure a pit is any different than a deep canal."* · *"If you're in a
> superdeep pit, you can't climb out. Period. Welcome to your pit."*

2026-09-17, the depth ruling, verbatim:

> *"All depths must be visually legible and differentiable graphically. The pawn should
> visibly rise up and lower down as they move over the depths. They should be low enough
> that it is visually clear how they could not possibly climb out (the walls are higher
> than their head by 20%)"*

2026-09-17, on spikes and the camera:

> *"The spikes will barely be able to be tall enough to be visible most likely, but there
> should still be something showing their presence. make sure the viewing angle of the pit
> is such that SOME amount of spike is possible"*

🔑 The through-line: **a canal is the reservoir, moved, and a pit is a canal dug all the way
down.** Every cell carries a depth and a fill; the reservoir, the channel and the pit are the
same thing at different depths, and the screen must show which depth and which fill a cell
holds.

### must show

**The channel itself**
- [ ] `canal_reads_as_dug_channel` — a dug channel has a visibly recessed bed and cut earthen
      walls, not the look of a path or a floor.
- [ ] `canal_dry_reads_as_obstacle` — an unfilled channel is legible as something that
      impedes crossing, without a tooltip.
- [ ] `filled_excavation_reads_as_obstacle` — a filled channel reads as harder to cross than
      the ordinary ground beside it.

**Fill**
- [ ] `canal_partial_fill_distinct` — a partly filled canal is distinguishable at a glance
      from a full one.
- [ ] `fill_tier_legible` — dry, water under a quarter of a metre deep, and water about 0.5 m,
      1 m, 1.5 m, and 2 m or more deep, are six looks distinguishable from each other by
      looking, whatever the depth of the hole holding them.
- [ ] `canal_fill_spreads_along_itself` — an incompletely filled channel shows one
      continuous wet reach extending away from its inlet, not an isolated puddle at the inlet.
- [ ] `canal_fill_front_watchable` (change) — the boundary between wet and dry is visibly
      farther along the same channel in the AFTER frame than in the BEFORE frame.
- [ ] `tar_fill_front_lags_water` (change) — from matching dry starts, water has visibly
      reached farther along its channel than tar has along an identical one after the same
      time.
- [ ] `canal_holds_only_the_channel` — the liquid surface ends at the channel's walls and does
      not spread onto the ground beside it.
- [ ] `canal_reads_as_same_liquid_as_reservoir` — a filled canal reads as the same substance
      as the body it came from.
- [ ] `fill_fluid_distinct` — excavations holding different fluids are distinguishable from
      each other by looking.
- [ ] `depth_and_fill_jointly_legible` — in one view, 1 m of water standing in holes 1 m, 2 m
      and 4 m deep (told apart by their walls and by how low a pawn sits), and holes 4 m deep
      holding 0.5 m, 1 m and 2 m of water (told apart by the water's look), are all
      distinguishable from each other.
- [ ] `still_water_one_surface_height` — every square of one connected body of still water (a
      pond, lake, canal or pit, joined below its surface) stands at the same surface height, to
      within 1 cm, read from the game's state, not from the picture.

**The reservoir paying for it**
- [ ] `reservoir_fill_visibly_drops` (change) — after supplying a canal, an enclosed
      reservoir's visible liquid level is lower in the AFTER frame than in the BEFORE frame.
- [ ] `reservoir_shoreline_recedes` (change) — after supplying a canal, the far shoreline of
      a small enclosed pond has visibly receded.
- [ ] `empty_reservoir_stops_flow` (change) — once its enclosed reservoir is visibly empty, a
      canal's wet front stays where it was between two frames taken apart in time.
- [ ] `reservoir_recharge_progress_visible` (change) — a drawn-down reservoir left alone has
      visibly regained some liquid in the AFTER frame while still short of full.

**Defense**
- [ ] `canal_burning_reads_as_burning_liquid` — a lit flammable canal reads as the liquid
      surface itself alight, not as ordinary fire standing on ground.
- [ ] `canal_fire_reaches_reservoir` (change) — a connected flammable reservoir is unlit in
      the BEFORE frame and visibly alight in the AFTER frame, while the channel fire is still
      visible.
- [ ] `canal_fire_persists` (change) — the same liquid is still visibly alight in two frames
      labelled at least one in-game day apart.
- [ ] `canal_spent_after_burn` — a burned-out channel is visibly distinguishable from an
      unburned dry channel by scorching, reading as burned and empty rather than merely dry.
- [ ] `slime_reads_as_viscous_not_water` — slime shows a thick, opaque surface, never the look
      of recoloured water.
- [ ] `slime_occupant_below_surface` — a pawn caught in a slime canal is drawn sunk into the
      slime, not standing on its surface.

**Depth**
- [ ] `pit_depth_ladder_legible` — undug ground and dry holes 0.5 m, 1 m, 1.5 m, 2 m, 4 m and
      8 m deep, side by side, are each distinguishable from the others by looking, without a
      tooltip.
- [ ] `pawn_height_ladder_legible` — a colonist sits lower in each deeper hole, from undug ground down through dry
      holes 0.5 m, 1 m, 1.5 m, 2 m and 4 m deep, and sits no lower in any hole deeper than 4 m.
- [ ] `pawn_lowers_on_deeper_cell` (change) — the same pawn is drawn visibly lower relative to
      the rim in the AFTER frame, after moving onto a deeper cell.
- [ ] `pawn_rises_on_shallower_cell` (change) — the same pawn is drawn visibly higher in the
      AFTER frame, after moving onto a shallower cell.

**The pit — a superdeep excavation, empty**
- [ ] `pit_reads_as_hole` — a superdeep cell reads as a big dark hole at play zoom with labels
      hidden.
- [ ] `pit_walls_have_visible_depth` — an empty superdeep excavation shows wall faces
      descending from rim to floor, not a flat dark tile.
- [ ] `pit_not_vanilla_trap` — a superdeep excavation is visually distinct from vanilla's
      spike trap.
- [ ] `pit_reads_at_size` — a multi-cell superdeep area reads as one excavated place, not as
      a grid of identical tiles.

**The pit, occupied**
- [ ] `pit_occupant_below_floor` — an occupant of a superdeep cell reads as being down in
      the hole, not standing on top of it.
- [ ] `pit_occupied_distinguishable` — occupied and empty superdeep cells are
      distinguishable at a glance, with no tooltip and no click.
- [ ] `pit_trapped_reads_as_trapped` — the walls around a superdeep occupant rise visibly
      above the top of their head, by about a fifth of their height, so climbing out reads
      as impossible.

**The cover**
- [ ] `pit_covered_invisible` (change) — the same patch of ground looks the same at play zoom
      in the BEFORE frame (undug) and the AFTER frame (a covered superdeep excavation).
- [ ] `pit_covered_seam_at_max_zoom` — a covered superdeep excavation shows a slight seam or
      discoloration at maximum zoom, so the player who placed it can find it.

**The built half — ladders, sluice gates, spikes**
- [ ] `ladder_state_legible` — a raised ladder beside the rim is visibly distinguishable from
      the same ladder lowered into the excavation.
- [ ] `sluice_gate_state_legible` — a sluice gate open versus shut is visible without
      selecting it.
- [ ] `spikes_read_distinct` — at play zoom some part of the spikes is visibly projecting in a
      spiked cell, distinguishing it from a bare one before anything falls in.

⛔ **Irrigation has NO visual line, by ruling 36 (2026-09-17).** He was told the consequence is
a player who may irrigate for hours without perceiving that it works, and ruled the yield is
enough. **A future pass must not re-add an irrigation line as an oversight.**

**Flexible hoses** (moved from Gimme Some Slack's walk at the hose port, 2026-10-11)
- [ ] `hose_thicker_stiffer_than_cord` — a laid hose is visibly several times thicker than a power cord and turns
      in wide curves, never in tight loops.
- [ ] `hose_plump_when_flowing_flat_when_not` — a hose carrying flow is drawn round and full, and the same kind of
      hose with no flow is drawn flat.
- [ ] `hose_plumps_only_from_powered_pump` (change) — a hose coupled to a pump is flat in the BEFORE frame with the
      pump unpowered and round in the AFTER frame with the pump powered and liquid flowing.
- [ ] `hose_joiner_reads_brass_screwed_together` — where one hose length meets the next, the joint reads as two
      brass couplings screwed together, with no gap between them.
- [ ] `reel_hose_leaves_brass_outlet_nozzle` — a laid hose leaves its reel from the reel's brass outlet nozzle,
      with a coupling on it, not from under the drum.
- [ ] `reel_laid_and_wound_look_differ` — a reel with its hose laid out looks different from the same reel with
      its hose wound in, and the laid hose visibly runs into the reel.
- [ ] `relay_chain_reads_connected` — a hose that ends on the next reel of a relay chain reads as coupled to it,
      not as two loose hoses lying side by side.

- [ ] `reel_offers_choose_style` — a selected hose reel shows a "Choose style" button.
- [ ] `four_reel_looks_distinguishable` — Scrapper, Industrial, Modern and Futuristic reels and their hoses are
      distinguishable from each other by looking.
- [ ] `hose_drawn_under_overhead_span` — a laid hose under an overhead span (Gimme Some Slack's power lines) is drawn
      beneath the span, never over it.
- [ ] `hose_carries_real_units` — liquid a powered pump moves through a hose arrives in the tank at the hose's far end,
      a pump level at a time.
- [ ] `hose_tint_is_carried_liquid` — a charged hose shows the colour of the liquid moving through it.
- [ ] `hose_dropped_carries_nothing` — a hose dropped on the ground (not set down at its end) carries no liquid.
- [ ] `hose_follows_port_changes` — when the tank at a hose's end is removed the flow stops, and when a tank is built
      there again the flow resumes by the pump's next cycle.
- [ ] `hose_far_end_pump_reaches_reel_tank` — a pump at a hose's far end fills the tank at the reel's end.
- [ ] `relay_chain_carries_liquid` — liquid passes down a chain of relay reels to the tank at its end, every hose
      in the chain plump.
- [ ] `pipe_and_hose_one_net` — a pump, a universal-pipe run, a reel on that run and its hose make one line: the tank at
      the hose's end fills.
- [ ] `tank_feeds_hose_without_pump` — a tank with a hose screwed into it passes its liquid on through the hose with no
      pump (owner ruling 2026-10-11).

**Limitless bodies** (the narrowed `limited_vs_limitless_legible`)
- [ ] `limitless_body_marked` — the depth readout over a body of water that never runs dry (the sea, a river, a lake
      fed from off the map) reads "Endless"; the readout over a pond, canal, pit or any lake that can be drawn down
      carries no such mark.

**The water ladder and swimming**
- [ ] `half_metre_water_reads_as_silt` — water about 0.5 m deep reads as grey-brown silty water; 1 m is the first
      depth that reads blue.
- [ ] `deep_water_pawn_swims` — a pawn in water 2 m or deeper is drawn swimming at the surface, head and shoulders
      above it, never walking on the floor beneath it nor standing on top of it.

**Trench cover**
- [ ] `trench_wall_cover_shown` — a shooter's hit chance on a pawn standing in a dug hole shows a "trench wall" cover
      line, and the figure is larger for a pawn chest-deep below the lip than for one waist-deep.
- [ ] `raiders_never_shelter_in_a_cage` — raiders seeking cover take trench squares they can climb out of and never
      step down into a sheer pocket they could not leave, read from the game's state.

**Pit access — ladders, gear, jumps**
- [ ] `wall_ladder_rides_on_rails` — the permanent pit ladder is drawn on rails fixed to the wall it serves, on each
      of the four sides of a pit; it can be raised from below or from above, but lowered only from above.
- [ ] `portable_ladder_leans_on_its_wall` — a portable ladder set in a pit leans diagonally against the wall it
      serves; one set against a wall too tall for it lies flat and gives no way out.
- [ ] `climbing_gear_reads_as_kit` — climbing gear reads as one belt-or-backpack kit of ropes, small grappling hooks
      and climbing claws, on the ground and worn.
- [ ] `geared_pawn_climbs_out` (change) — a colonist wearing climbing gear is on the floor of a sheer pit with no
      ladder in the BEFORE frame and on the ground beside it in the AFTER frame.
- [ ] `jump_into_pit_lands_unhurt` — a pawn who jumps (jump pack) or skips into a pit arrives on its floor with no
      fall injury, read from the game's state; flying creatures fly in and out, jumping creatures jump in or out, and
      floating creatures float in and out.

**Wall scaling**
- [ ] `geared_pawn_scales_built_wall` (change) — a pawn wearing climbing gear is on one side of an unroofed built wall
      in the BEFORE frame and on the other side in the AFTER frame, with no door in the wall; the same pawn without
      the gear cannot.

**Suspension bridges and pit covers**
- [ ] `suspension_bridge_reads_hung` — a suspension bridge reads as a deck hung between anchors at its two ends over a
      dug hole, not as a floor tile or the game's own bridge.
- [ ] `pawn_walks_under_deck` (change) — a pawn on the floor of a hole is on one side of a suspension deck overhead in
      the BEFORE frame and on the other side in the AFTER frame, having walked beneath it.
- [ ] `pit_cover_unlike_bridge` — a pit cover never looks like a suspension bridge: the cover passes for ground (the
      bars `pit_covered_invisible` and `pit_covered_seam_at_max_zoom` judge it), the bridge reads as a built crossing.

**Pipes, ports and hoses**
- [ ] `pipe_meets_building_centre` — a pipe or hose that meets a tank, pump, tap or sprinkler reads as running on
      beneath it to its centre: seen through its see-through margins, hidden by its solid body, never stopping short
      at its edge.
- [ ] `pump_port_takes_pipe_or_hose` — a pump shows one clear port on each of its four sides, and each port takes
      either a pipe or a hose, never both; a pipe or a hose joined to a port meets it with a visible coupling.

### cannot show

- [ ] `never_liquid_on_open_ground` — liquid standing on undug ground outside both the
      reservoir and the channel.
- [ ] `never_gravel_path` — a channel that reads as a gravel road.
- [ ] `never_full_reservoir_after_heavy_draw` (change) — an enclosed reservoir whose fill looks
      untouched after filling a long canal.
- [ ] `never_snared_standing` — a pawn snared upright on a labelled tile, staring at the
      camera.
- [ ] `never_hose_across_impassable` — a hose drawn across a wall, rock or other impassable cell.
- [ ] `never_tank_bridges_pipe_runs` — two universal-pipe runs that both touch one tank becoming one line through it.
- [ ] `never_external_pipe_carries` — another mod's pipe (Vanilla Expanded, Dubs) between two FlowWorks runs joining
      them: those couple a hose for the look only.
- [ ] `never_reads_as_building` — the bare excavation itself, apart from any ladder, gate or
      spikes in it, reads as a placed building sitting on the floor.

### candidate lines

**Empty by decision.** Resolved with him and not to be re-added:

- `limited_vs_limitless_legible` — **cut** by ruling 35 (2026-09-17); **narrowed 2026-10-17**: limitless bodies are
  marked in the readout, limited ones are not. A narrowed bar is offered as a proposal, outside this section.
- `source_exhausted_distinct_from_strained` — **cut.** Incoherent after ruling 34, which
  removed the source object and the strained state.
- `irrigated_ground_visibly_differs` — **cut** by ruling 36, above.
- `digsite_stage_legible` — **cut** with the staged dig-site chain the pit collapse retires.

### provenance

| bar | his words it distils |
|---|---|
| `canal_reads_as_dug_channel` | *"dig canals in the ground"* |
| `canal_dry_reads_as_obstacle` | *"an unfilled pit slows movement as per other established dug barriers"* |
| `filled_excavation_reads_as_obstacle` | *"filled pits reduce as per that terrain cost"*; *"all other flooded canal depths just slow you down more"* |
| `canal_partial_fill_distinct` | *"a graphic showing partial fill"* |
| `fill_tier_legible` | pit card round 3, 2026-09-17 — approved; strengthens `canal_partial_fill_distinct` (many states vs two), sits beside it because ids are frozen; re-stated in metres by the 2026-10-17 depth rebuild (one water ladder by metres; a new look under 25 cm) |
| `canal_fill_spreads_along_itself` | *"spread the water throughout themselves"* |
| `canal_fill_front_watchable` | *"at the liquid's viscosity (water is essentially zero)"*; promoted from candidate 2026-09-17 |
| `tar_fill_front_lags_water` | *"water is essentially zero"* viscosity against tar; split from `canal_fill_front_watchable` on GPT review |
| `canal_holds_only_the_channel` | *"flows into the canal to fill it"* |
| `canal_reads_as_same_liquid_as_reservoir` | *"extending the source"* |
| `fill_fluid_distinct` | pit card round 3 — approved; generalises `slime_reads_as_viscous_not_water`; half of the old Pits `fitting_reads_distinct` |
| `depth_and_fill_jointly_legible` | the depth ruling (*"All depths must be visually legible"*) held together with the water ladder; re-stated in metres by the 2026-10-17 depth rebuild |
| `still_water_one_surface_height` | 2026-10-17: *"Yes, north star should check for level surfaces"*, on *"We need VERY smooth water. That's water's one primary characteristic: a level surface."*; rivers and the sea stay the game's own water and are not still bodies |
| `reservoir_fill_visibly_drops` | *"the parent body of water reduces itself in proportion as well"*; ruling 34 makes it partial fill on a deeper cell |
| `reservoir_shoreline_recedes` | *"a small pond visibly shrinks at its far edge"*, split out of `reservoir_fill_visibly_drops` |
| `empty_reservoir_stops_flow` | *"Each source's square can supply up to five canal squares with liquid before it stops providing"* |
| `reservoir_recharge_progress_visible` | *"refilling slowly, from rain and season and ground liquids oozing in"* |
| `canal_burning_reads_as_burning_liquid` | *"the canals can be lit and burn for a very long time"* |
| `canal_fire_reaches_reservoir` | *"They will also light their source at that time"* |
| `canal_fire_persists` | *"burn for a very long time"* |
| `canal_spent_after_burn` | promoted from candidate 2026-09-17 so the defense use leaves a visible mark |
| `slime_reads_as_viscous_not_water` | *"so slippery that it is nearly impossible to cross"* |
| `slime_occupant_below_surface` | *"escape from the pit takes a great deal of time"*; his rejection of a pawn *"staring at the camera"* |
| `pit_depth_ladder_legible` | the depth ruling: *"All depths must be visually legible and differentiable graphically."*; re-stated in metres when colonist digs went past 2 m (2026-10-17, by card: default deepest dig 8 m) |
| `pawn_height_ladder_legible` | the depth ruling: *"They should be low enough that it is visually clear how they could not possibly climb out"*; the pawn keeps sinking down to 4 m and no lower beyond (card 2026-10-20, "Keep sinking to 4 m"; it stopped at 2 m in the 2026-10-17 depth rebuild) |
| `pawn_lowers_on_deeper_cell` | the depth ruling: *"The pawn should visibly rise up and lower down as they move over the depths."* |
| `pawn_rises_on_shallower_cell` | the same sentence, the other direction |
| `pit_reads_as_hole` | *"we need a big dark pit"*; ruling 33 *"walls with depth, not a flat tile"* |
| `pit_walls_have_visible_depth` | ruling 33 *"walls with depth, not a flat tile"*, split out of `pit_reads_as_hole` |
| `pit_not_vanilla_trap` | *"stuck in a trap with "Pit" written on it"* — reworded from the Pits walk to drop the building's texture path |
| `pit_reads_at_size` | Pits walk bar, strengthened from "fills its own footprint" to "one excavated place" |
| `pit_occupant_below_floor` | Pits walk bar; absorbs the Pits walk's `pitcell_occupant_visible` (same claim) |
| `pit_occupied_distinguishable` | Pits walk bar, "sprung pits" re-subjected to superdeep cells |
| `pit_trapped_reads_as_trapped` | pit card round 3, worded against the walls by his choice; the depth ruling's *"the walls are higher than their head by 20%"* |
| `pit_covered_invisible` | `design/Jawa/covered_pit_traps_spec.md` §3, 2026-08-30 |
| `pit_covered_seam_at_max_zoom` | *"a slight seam/discoloration at high zoom for the player's own eye"* |
| `ladder_state_legible` | *"A ladder nearby can be pulled up or lowered"*; half of the Pits walk's `pitcell_gate_state_legible` |
| `sluice_gate_state_legible` | *"A sluice gate also acts just like a door"*; the other half of `pitcell_gate_state_legible` |
| `spikes_read_distinct` | *"there should still be something showing their presence"*; half of the Pits walk's `fitting_reads_distinct` |
| `never_liquid_on_open_ground` | *"flows into the canal to fill it"* |
| `never_gravel_path` | the dug channel must not read as a road |
| `never_full_reservoir_after_heavy_draw` | conservation of mass made visible; his stock ruling |
| `never_snared_standing` | the defect that prompted the north-star system, kept verbatim from the Pits walk |
| `never_reads_as_building` | pit card round 3 — approved; the general form of `pit_not_vanilla_trap` |
| `hose_thicker_stiffer_than_cord` | *"much thicker and stiffer than the wires, much like the fire hoses they use"* |
| `hose_plump_when_flowing_flat_when_not` | *"they SHOULD "plump up" when water is flowing through them and "collapse down" when it's not"* |
| `hose_plumps_only_from_powered_pump` | 2026-10-05 review, relayed (deflated unless liquid + somewhere to flow + powered pump); fails until FlowWorks ships a pump |
| `hose_joiner_reads_brass_screwed_together` | 2026-10-05 review, relayed (joiners look like brass screwed together) |
| `reel_hose_leaves_brass_outlet_nozzle` | 2026-10-05 review, relayed (2x2 reel's hose attaches to its brass outlet nozzle) |
| `reel_laid_and_wound_look_differ` | style-per-build brief: a reel that looks different when its hose is laid out, the hose running into the reel (paraphrased in that design's own text) |
| `relay_chain_reads_connected` | *"Maybe they place another reel out there to connect to?"* |
| `reel_offers_choose_style` | *"reels don't have a choose style option"* |
| `four_reel_looks_distinguishable` | *"select between these four art styles for the poles, hose reels, hoses, and cables"* (hose half, moved with the hose) |
| `hose_drawn_under_overhead_span` | *"firehose is shown as going OVER the hanging power lines (oops!)"* |
| `never_hose_across_impassable` | the hose half of Gimme Some Slack's `never_cord_across_impassable` (moved with the hose) |
| `hose_carries_real_units` | owner, typed 2026-10-10: "move the GimmeSomeSlack hose code/functionality over to FlowWorks. That's the right home" (the hose joins FlowWorks' liquid net; design FINAL §3.6) |
| `hose_tint_is_carried_liquid` | the hose tints by what it carries (GSS design 3.4), now the carried LiquidDef's own colour |
| `hose_dropped_carries_nothing` | design FINAL §3.1: only a Laid hose carries (G1.6) |
| `hose_follows_port_changes` | design FINAL §3.1/§3.6 (G1.4, G6.4) |
| `hose_far_end_pump_reaches_reel_tank` | design v2 M2 (far-end seeding) |
| `relay_chain_carries_liquid` | *"Maybe they place another reel out there to connect to?"* -- the liquid half of the relay bar |
| `pipe_and_hose_one_net` | owner 2026-10-04: the reel must connect to *"standard static piping and other pipe-friendly buildings (like tanks)"* |
| `tank_feeds_hose_without_pump` | owner, typed 2026-10-11: *"Yes, a tank would pass liquid on to a hose screwed into it, without a pump needed."* |
| `never_tank_bridges_pipe_runs` | FlowWorks' net rule: a tank is an endpoint, two runs never merge through it (RM_LiquidNet) |
| `never_external_pipe_carries` | design FINAL §3.1 (G1.7): VE/DBH couplings stay visual |
| `limitless_body_marked` | R13, owner said 2026-10-17: "Any natural body of water that is supposed to be 'clearly limitless' should be so marked, so players aren't shocked."; wording, he typed 2026-10-20: *"it should simply say Endless, for simplicity"* |
| `half_metre_water_reads_as_silt` | card 2026-10-18, "How should 0.5 m water look → Keep grey silt"; accepted at the 2026-10-20 sitting |
| `deep_water_pawn_swims` | R12 (pawns may swim in water 2 m or deeper); accepted at the 2026-10-20 sitting |
| `trench_wall_cover_shown` | owner 2026-10-18, "This updates/replaces the old ruling that digging does not change shooting"; card "Any dug hole with a wall"; accepted at the 2026-10-20 sitting |
| `raiders_never_shelter_in_a_cage` | canal cover design Q5 (raiders use trenches, with the cage check); accepted at the 2026-10-20 sitting |
| `wall_ladder_rides_on_rails` | owner 2026-10-18, "one permanent that you install on a wall that raises and lowers to open and close access"; he typed 2026-10-20: *"It can be raised from either below or above. But it can only be lowered from above."* |
| `portable_ladder_leans_on_its_wall` | owner 2026-10-18, "a personally carriable ladder placed into the pit (if not too deep)"; his look at the diagonal art; accepted at the 2026-10-20 sitting |
| `climbing_gear_reads_as_kit` | owner 2026-10-18 by card (the gear is one item of all of these); accepted at the 2026-10-20 sitting |
| `geared_pawn_climbs_out` | "Climbing gear a pawn has that allows them to scale"; accepted at the 2026-10-20 sitting |
| `jump_into_pit_lands_unhurt` | "jump packs and other leaping abilities allow entrance/exit immediately"; he typed 2026-10-20: *"plus flying creatures can simply fly in/out, jumping creatures jump in or out, floating creatures float in/out"* |
| `geared_pawn_scales_built_wall` | owner 2026-10-18 by card: built walls too, colonists and raiders, slowly, both ways; accepted at the 2026-10-20 sitting |
| `suspension_bridge_reads_hung` | owner 2026-10-17, "These are not 'Bridges' in the sense Rimworld normally uses … Something that shows they're not pier/pyle-type bridges over water."; accepted at the 2026-10-20 sitting |
| `pawn_walks_under_deck` | R8 amendment, "only for these new bridges uniquely, NOT actual tunnels."; accepted at the 2026-10-20 sitting |
| `pit_cover_unlike_bridge` | the bridges design: covers are the hidden trap tier of the same span base, with their own look (Q8); accepted at the 2026-10-20 sitting |
| `pipe_meets_building_centre` | owner 2026-10-18, "draw pipes as though they are connected into the centers of all pipe-receiving items"; accepted at the 2026-10-20 sitting |
| `pump_port_takes_pipe_or_hose` | owner 2026-10-18, "a more squarish device with a clear place for pumps to join … connectable from any angle"; card 2026-10-20, "One port per side, either kind" (each side takes a pipe or a hose, not both). Renamed from `pump_port_takes_pipe_and_hose`, which read as both at once |

## proposed bars (NOT hash-bound — proposals for his sitting)

⚠️ **Everything under this heading is a PROPOSAL by an agent, not a bar.** It sits outside `## north star`, so the
validated-hash does not cover it and `modcheck` does not read it. A proposal becomes a bar only when he accepts it at a
sitting (`FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`); it then moves, with a `- [ ]` checkbox and a provenance row, into
`## north star`, and that move is itself an edit he re-validates. Sitting sheet:
`design/RimMandrake/flowworks_bars_sitting_2026-10-18.md`; his answers:
`design/RimMandrake/flowworks_bars_answers_2026-10-20.md`. Proposals 6-21 were accepted at the 2026-10-20 sitting and
moved into the north star; one remains.

**Pipes, ports and hoses**
- `hose_and_pipe_girth_sensible` — side by side at a pump, a tank, a tap and a sprinkler, with a colonist beside them, a hose and a solid pipe look sized for each other, for the port they enter and for the colonist. *Source: owner 2026-10-18, "we need to do a live game walk of the hoses vs pipes to make sure the diameters are sensible." His numbers for what "sensible" is are owed at the sitting.* **Not accepted — 2026-10-20 he typed:** *"Both pipe and hose art need a better
  definition of width. Colonists don't have arms. Need an in-game look"*. A width spec is owed, and the bar is judged at
  an in-game look: `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`.

## anti-guessing notes
- ✅ **The DRAFT banner that used to open `## north star` was false and is deleted** (2026-09-17).
  It said the checklist "has never bound" while `state: VALIDATED` sat three lines above it, and
  a note here instructed the reader ⛔ *not* to tidy it, because correcting it would revert his
  validation by hash mismatch. **Owner ruled that trade away the same day** — verbatim: *"Change
  no code — you just re-validate when prose is corrected."* So the banner was replaced with
  state-independent prose and he re-validated in the same sitting; `NORTHSTAR_HASH_SCOPE_1` is
  dropped, declined not deferred. 🔑 The general rule this leaves: **never leave false text
  standing inside a hashed section to protect a hash** — correct it and re-validate. And write
  only state-independent prose in there, so a state change cannot make the prose wrong.
- The live dig/fill/read surface is `jawa/flowworks_excavation_drive` (Deepen/TrySetDriverFill), `jawa/flowworks_excavation_report` (D/F, source/sink, map counters) and `jawa/flowworks_spawn_flood` in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksTools.cs`, plus the `jawa/static_call` read surfaces in the mod (`RM_PromotionProofs`, `RM_NorthstarProofs`, `RM_LiquidFireProof`, `RM_DigDiscoveryProof`, `RM_FluidIdentityProof`). `jawa/canal_dig` is a STUB since ruling 24 that always fails — never call it.
- 🔴 This walk USED TO CLAIM "No [S] line: nothing here is a visual-only concern". That claim was false and is deleted. MEASURED 2026-09-16: the mod ships **zero bespoke textures** — the dug channel borrows `Terrain/Surfaces/Gravel`, the test source borrows the drop-beacon sprite — so every state assertion above can pass while the player looks at gravel. That is exactly the defect class the north star system exists to catch (`design/RimMandrake/north_star_validation_spec.md`), and this walk was one of the 7 that dismissed the visual pass in writing.
- ✅ **The rename is complete and this walk carries the new name.** MEASURED 2026-09-17: file is `FlowWorks.md`, `subject:` reads `src/RimMandrake/FlowWorks`, `About.xml` declares `mandrake.rm.flowworks`, C# namespaces are `RimMandrake.FlowWorks.*`, def files are `FlowWorks_*.xml`. The six remaining "fluidcanal" strings in `src/` are the live defName `RM_FluidCanalFlood` (its ThingDef and DefOf agree, so it functions), three history comments, and a compiled DLL — none is owed work. A prior note here claimed this file was still `FluidCanals.md`; that was false and is deleted.
