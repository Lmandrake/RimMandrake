# BELT: FlowWorks Northstar v2 — 2026-10-02

Progress log (appended per step).

## Step 0 — read
- read plan/draft/tools/C#. Draft --offline: O1-O6 PASS. Game up: tick 1 quicktest 250x250 ExtremeDesert, 86 excavated cells from earlier helpers (not pristine).
- preflight offline: P-O4 FAIL (owner's pre-swap list carries dangling mandrake.rm.pits; FULL.LATEST dropped it at f6a81fb5d; Pits NOT installed - no About.xml in Mods), P-O5 FAIL (no TrialSite_v1 sidecar).
- DECISIONS: live tier = direct python.exe runner (modcheck run would swap ModsConfig = forbidden; northstar_driver run does not record_run). Flow scenes use jawa/flowworks_pulse (0 ticks). Site = FRESH quicktest map (pristine, L5 enforceable) with v2 bodies painted, not the v1 TrialSite (prep_site builds the OLD plot layout, not W1..W7). Pit mechanics: smoke only (S1 holder at D=4 via pit_report). E1 cadence merged into the E7/E8 job ticks (0 extra ticks). Rain (E6) is map-wide (ApplyRain loops all excavated cells) -> runs LAST.

## Step 1 — offline tier
- step 2a: P-O4 fixed (PITS-only diff accepted in either direction iff no installed mod carries mandrake.rm.pits; FAIL if installed; UNMEASURED if roots unreadable) + 3 selftest fixtures; selftest_flowworks_northstar PASS 0 failures; live P-O4 now PASS (611 mods).
- step 2b: prove_flowworks_pulse P2 now paints a 1-cell WaterShallow source, classifies it, asserts per-pulse vectors == PulseOracle (recession modelled) and stock 4 / recededCount 1 read from pulse bodies[] by id. Needs oracle recession support (added in v2).
- P-O5 (no TrialSite_v1 sidecar): NOT fixed by building -- v2 does not use that site (decision above).
- step 1 RESULT: validation_v2_DRAFT.py --offline: O1-O8 PASS + O-NEG (9 in-memory mutations all red) + O-LIVE-NEG (clean mock run green, 67 rows; 16 mock faults each turn their named live row red). 0 game ticks.
  - learned offline: at shipped rainFillPerPulse 0.1 the rain-toggle-OFF negative was VACUOUS (mock fault rain_toggle_ignored stayed PASS) -> pinned 1.0 during the job window + a would-add>=1.5 sanity gate.
  - learned from source: a 1-cell pond at shipped recession supplies exactly ONE level (floor(4/5)=0 supported cells -> recedes next pulse); oracle now models recession (PrefersCandidate order) and rain (map-wide).
  - E4 OFF window must straddle the scheduled tick (nextPulseTick 251 at tick 1), else an engine ignoring the toggle passes.

## Step 3 — live
- step 2b LIVE: prove_flowworks_pulse first rerun: P2 vector/stock FAIL -> live [1,0,0,0], stock 3. Cause (oracle reproduced it EXACTLY): a previous run's D=4 cell sat west of the new source; its component was seeded first and CLAIMED the source cell (pulseVisited is shared across components), so the strip's component had no source -> no flow order -> stalled at the inlet. SITE defect of the strip search (fixed: 9x3 dry block). It also exposed a MOD defect: two channels off ONE source cell -> the second-dug stalls at its inlet forever, even off a limitless body (oracle) = FLOWWORKS_SHARED_SOURCE_STALL_1 (new; v2 row E2s_shared_source_both_fill, expected RED). Oracle now seeds in dig order (C# HashSet insertion order).
- step 2b LIVE rerun: prove_flowworks_pulse ALL PASS (P2 [0,0,0,1] x3 == oracle, stock 4, recededCount 1). 0 ticks.
- offline after changes: O1-O8, O-NEG, O-LIVE-NEG PASS (mock: 16 faults red; E2s known MOD red).
- fresh quicktest map: {'success': False, 'wall_s': 280.0}
    L0_fresh_map           FAIL       SITE     {'success': False, 'message': 'Timed out waiting for RimWorld entry scene readiness.', 'state': {'programState': 'Playing', 'inEntryScene': False, 'hasCurrentGame': True, 'currentMapId': 'Map_0', 'currentMapIndex': 0, 'mapCount': 1, 'longEventPending': False, 'paused': True, 'timeSpeed': 'Paused', '
    L0_loaded_paused       PASS                programState Playing, ticksGame 1 -> 1 over 1 s
    L0_map_250             PASS                map 250x250 biome ExtremeDesert
    L1_log_clean           PASS                no FlowWorks error in 14 warn+ entries (base seq 17)
    L2_assembly_identity   PASS                loaded C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll sha 0fc9651256ec mvidMatchesFile True; repo sha 0fc9651256ec
    L3_defs_live           PASS                live pathCost {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300} (want {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300})
    L4_settings_default    PASS                43 settings read, all shipped defaults
    L5_site_pristine       FAIL       SITE     excavated 96 bodies 5 superdeep 3 activeFluidRaw RM_Fluid_Water
- step L_preflight: ticks 0 (planned 0), wall 19.1s, 53 calls ERROR Abort: site not pristine -- start a fresh quicktest map (--fresh-map)
    ABORT                  FAIL       SITE     site not pristine -- start a fresh quicktest map (--fresh-map)
    Z_settings_restored    PASS                0 touched settings back to shipped defaults
- live run 1: start_debug_game_ready from inside a colony timed out (280 s wall, 0 ticks) -> L5 refused (96 excavated). Fix: go_to_main_menu first + poll programState.
- fresh quicktest map: {'menu': True, 'start': True, 'programState': 'Playing', 'wall_s': 8.4}
    L0_loaded_paused       PASS                programState Playing, ticksGame 1 -> 1 over 1 s
    L0_map_250             PASS                map 250x250 biome Tundra
    L1_log_clean           PASS                no FlowWorks error in 14 warn+ entries (base seq 17)
    L2_assembly_identity   PASS                loaded C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll sha 0fc9651256ec mvidMatchesFile True; repo sha 0fc9651256ec
    L3_defs_live           PASS                live pathCost {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300} (want {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300})
    L4_settings_default    PASS                43 settings read, all shipped defaults
    L5_site_pristine       PASS                excavated 0 bodies 0 superdeep 0 activeFluidRaw None
    E1a_cadence_shipped    PASS                pulseIntervalTicks 250, nextPulseTick 251 at tick 1
    L5_dry_weather         PASS                weather Clear rainRate 0.0
- step L_preflight: ticks 0 (planned 0), wall 18.9s, 54 calls
    SITE0_no_pawn_in_plots PASS                22 pawns, none in 36 plot rects
    SITE1_painted_readback PASS                36 rects cleared+Soil, 9 bodies painted, every scene cell fresh Soil, every body exactly its sources
- step SITE_paint: ticks 0 (planned 0), wall 0.6s, 76 calls
    S1_dig_ladder          PASS                D [1, 2, 3, 4] terrain ['RM_Channel_Empty', 'RM_Channel_Mid', 'RM_Channel_Deep', 'RM_Channel_Superdeep'] excavated +4 superdeep +1
    S1n_superdeep_is_max   PASS                deepen D=4 once more -> 4
    S1p_holder_at_D4_only  PASS                D4 holder True (occupants 0); D3 holder False  [pit smoke only: pit model under redesign]
    S2_fill_clamp          PASS                setFill 9 on D=2 -> F=2; setFill 1 on undug -> fillSet=False F=0
    S3_classification      PASS                W1, W8 limitless; W2/W2R 5, W3 10, W4 (edge,40) 200, W5 (interior,64) 320 all LIMITED
    S4_sink_band           PASS                isSink at edge distance 9: True; at 11: False
    S5_sticky_limitless    PASS                W6 (sticky OFF) limitless=False; twin W7 (ON) limitless=True
    S6_digToDepth_gate     UNCOVERED           jawa/designate_batch adds Designations directly, bypassing Designator_DigCanal.CanDesignateCell; the WorkGiver gate needs a HasJobOnCell probe tool (owed)
    S7_S9_capture_ladder   SKIP                pit model (pit = depth-4 cell, no holder building) is being redesigned by other helpers; only the S1p holder smoke runs
    U_fill_fluid_distinct  UNBUILT             UNBUILT: one activeFluid field per map component
    U_ladder_state_legible UNBUILT             UNBUILT: RM_Ladder has no raised/lowered state (thingClass Building)
    U_pawn_height_ladder_legible UNBUILT             UNBUILT: no pawn draw offset by depth
    U_pawn_lowers_on_deeper_cell UNBUILT             UNBUILT: same
    U_pawn_rises_on_shallower_cell UNBUILT             UNBUILT: same
    U_pit_covered_invisible UNBUILT             UNBUILT: no superdeep cover (only legacy Building_TerrainMimicCover)
    U_pit_covered_seam_at_max_zoom UNBUILT             UNBUILT: same as pit_covered_invisible
    U_pit_trapped_reads_as_trapped UNBUILT             UNBUILT: same (walls above head need the offset)
    U_slime_occupant_below_surface UNBUILT             UNBUILT: same
    U_sluice_gate_state_legible UNBUILT             UNBUILT: no Sluice def
    U_spikes_read_distinct UNBUILT             UNBUILT: no per-cell spike def on excavations (RM_OpenPit_Spiked / RM_PitDigSite_*_Spiked are the legacy building pit)
    U_tar_fill_front_lags_water UNBUILT             UNBUILT: FlowPerPulse is global; viscosity not read by the engine
- step S_state: ticks 0 (planned 0), wall 2.9s, 31 calls
    A0_sanity_probe        PASS                rect read of the prefilled E5_sink run: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] (must see a known F=1)
    pulse[A] x8: 67 cells, 0 mismatching scenes []
    A_pulse_contract       PASS                8 pulses, 0 ticks, scheduler untouched, paused
    E2_east_A              PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_east_B              PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_north               PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_south               PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_west                PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_twins_identical     PASS                A [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] / B [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_channels_fill_every_direction PASS                first-full pulse by direction {'E2_east_A': 4, 'E2_north': 4, 'E2_south': 4, 'E2_west': 4} (bound n*D = 4; FLOWWORKS_CHANNEL_OSCILLATION_1 regression guard)
    E2_dry_ring            PASS                every non-channel, non-body ring cell undug, F=0, Soil
    E3b_recession_shipped  PASS                final [0, 0, 0, 1], W2R {'stock': 4.001896, 'recededCount': 1, 'activeCellCount': 0}
    E5_sink_drains         PASS                band run drained per oracle: sinkTransferredTotal +10.0 (oracle +10); final [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    E5_inner_holds         PASS                interior prefilled twin final [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    E2s_shared_source_oracle PASS                both pairs == oracle (first-dug claims the source): {'E2s_shared_E7': [1, 1, 1, 1], 'E2s_shared_N7': [1, 0, 0, 0], 'E2s_shared_N8': [1, 1, 1, 1], 'E2s_shared_E8': [1, 0, 0, 0]}
    E2s_shared_source_both_fill FAIL       MOD      two channels off ONE source cell after 8 pulses: {'E2s_shared_E7': [1, 1, 1, 1], 'E2s_shared_N7': [1, 0, 0, 0], 'E2s_shared_N8': [1, 1, 1, 1], 'E2s_shared_E8': [1, 0, 0, 0]} -- the second-dug channel stalls at its inlet (FLOWWORKS_SHARED_SOURCE_STALL_1)
    A_global_vs_oracle     PASS                every excavated cell == oracle at every pulse
- step A_flow_defaults: ticks 0 (planned 0), wall 0.5s, 90 calls
    pulse[B] x7: 75 cells, 0 mismatching scenes []
    E3_budget_exhaustion   PASS                cap-5 pond delivered exactly 5 ([0, 0, 0, 1, 1, 1, 1, 1]), then rested; stock 0.00162504055
    pulse[B-off] x2: 75 cells, 0 mismatching scenes []
    E3n_budget_off_supplies PASS                budget OFF: a spent pond supplies again ([0, 0, 0, 1, 1, 1, 1, 1] -> [0, 1, 1, 1, 1, 1, 1, 1])
    B_global_vs_oracle     PASS                all cells == oracle
- step B_budget: ticks 0 (planned 0), wall 3.3s, 20 calls
    pulse[C-off] x2: 85 cells, 0 mismatching scenes []
    E5n_sinks_off          PASS                sinks OFF: run [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], total 10.0->10.0, isSink any=False
    pulse[C-on] x3: 85 cells, 0 mismatching scenes []
    E5_sinks_back_on       PASS                sinks ON again: [1, 1, 0, 0, 0, 1, 0, 0, 0, 0], total +7.0 (oracle +7)
    C_global_vs_oracle     PASS                all cells == oracle
- step C_sink_toggle: ticks 0 (planned 0), wall 1.9s, 33 calls
    pulse[R] x8: 89 cells, 0 mismatching scenes []
    E2_rerun_determinism   PASS                E2_east_A (phase A) [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] vs E2_rerun (dug later, other body) [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    R_global_vs_oracle     PASS                all cells == oracle
- step R_determinism_rerun: ticks 0 (planned 0), wall 0.2s, 7 calls
    E4_engine_off          PASS                OFF for 310 ticks, past the due tick 251: nextPulseTick 251->251, cells moved []
    E1b_pulse_clamp        PASS                pulseIntervalTicks set 30 -> engine reads 60 (clamp floor 60)
    E1c_cadence_real_scheduler PASS                59 chunks of 60 ticks: nextPulseTick advances [60], lead [1]
    E4_engine_on_scheduled PASS                after 59 real scheduled pulses every oracle cell == oracle; E4 channel [1, 1, 1, 1]
    E6n_rain_toggle_off    PASS                rain fell (rate now 0.963) with rainFillsExcavations OFF over 59 pulses: no cell gained
    E7a_fillin_displaces   PASS                sum F 2 -> 2 (conserved), middle D=0 terrain Soil, vector [1, 0, 1]
    E7b_overflow_sanctioned PASS                no room: sum F 3 -> 2, overflowDestroyedTotal +1.0 (want +1)
    E8_player_dig          PASS                designated cell dug by a colonist: D=1 terrain RM_Channel_Empty after 3540 ticks (cap 4000, MiningSpeed 0.10)
- step J_jobs_scheduler: ticks 3850 (planned <= 4000 (job cap)), wall 16.6s, 297 calls
    E6_roof_readback       PASS                roofed excavated cells [(182, 60)]
    pulse[rain] x2: 100 cells, 0 mismatching scenes []
    E6_rain_fills_unroofed PASS                rate 0.963 x 2 pulses: unroofed F=1, roofed twin F=0, every excavated cell == oracle
- step E6_rain: ticks 0 (planned 0), wall 1.9s, 11 calls
    T0n_fluid_switch_refused PASS                set_active_fluid Tar after classification+fill: success=False, activeFluidRaw RM_Fluid_Water
    E9_log_budget          PASS                0 FlowWorks errors, 0 ledger imbalances, exactly 1 sanctioned conservation exception; 1 other error lines [('error', 'Attempted to calculate value for disabled stat MiningSpeed; this is meant as a consistency check, either set the stat to')]
- step T0_E9_tail: ticks 0 (planned 0), wall 0.0s, 5 calls
    Z_settings_restored    PASS                8 touched settings back to shipped defaults
- live run 2 RESULT (fresh Tundra quicktest): 54 PASS, 1 FAIL = E2s_shared_source_both_fill (MOD, FLOWWORKS_SHARED_SOURCE_STALL_1, live == oracle), UNCOVERED 1, UNBUILT 12, SKIP 1. 3850 ticks, 62 s wall, 649 calls. Ticks dominated by E8 job: a mining-INCAPABLE colonist (speed 0.10, our pawn_stats call logged a red 'disabled stat' error) -> cap 4000, done at 3540. Fix: re-roll incapable colonists. Rerunning (run 3) = determinism across runs.
- fresh quicktest map: {'menu': True, 'start': True, 'programState': 'Playing', 'wall_s': 13.3}
    L0_loaded_paused       PASS                programState Playing, ticksGame 1 -> 1 over 1 s
    L0_map_250             PASS                map 250x250 biome TemperateForest
    L1_log_clean           PASS                no FlowWorks error in 16 warn+ entries (base seq 40)
    L2_assembly_identity   PASS                loaded C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll sha 0fc9651256ec mvidMatchesFile True; repo sha 0fc9651256ec
    L3_defs_live           PASS                live pathCost {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300} (want {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300})
    L4_settings_default    PASS                43 settings read, all shipped defaults
    L5_site_pristine       PASS                excavated 0 bodies 0 superdeep 0 activeFluidRaw None
    E1a_cadence_shipped    PASS                pulseIntervalTicks 250, nextPulseTick 251 at tick 1
    L5_dry_weather         PASS                weather Clear rainRate 0.0
- step L_preflight: ticks 0 (planned 0), wall 19.7s, 54 calls
    SITE0_no_pawn_in_plots PASS                55 pawns, none in 36 plot rects
    SITE1_painted_readback PASS                36 rects cleared+Soil, 9 bodies painted, every scene cell fresh Soil, every body exactly its sources
- step SITE_paint: ticks 0 (planned 0), wall 1.1s, 76 calls
    S1_dig_ladder          PASS                D [1, 2, 3, 4] terrain ['RM_Channel_Empty', 'RM_Channel_Mid', 'RM_Channel_Deep', 'RM_Channel_Superdeep'] excavated +4 superdeep +1
    S1n_superdeep_is_max   PASS                deepen D=4 once more -> 4
    S1p_holder_at_D4_only  PASS                D4 holder True (occupants 0); D3 holder False  [pit smoke only: pit model under redesign]
    S2_fill_clamp          PASS                setFill 9 on D=2 -> F=2; setFill 1 on undug -> fillSet=False F=0
    S3_classification      PASS                W1, W8 limitless; W2/W2R 5, W3 10, W4 (edge,40) 200, W5 (interior,64) 320 all LIMITED
    S4_sink_band           PASS                isSink at edge distance 9: True; at 11: False
    S5_sticky_limitless    PASS                W6 (sticky OFF) limitless=False; twin W7 (ON) limitless=True
    S6_digToDepth_gate     UNCOVERED           jawa/designate_batch adds Designations directly, bypassing Designator_DigCanal.CanDesignateCell; the WorkGiver gate needs a HasJobOnCell probe tool (owed)
    S7_S9_capture_ladder   SKIP                pit model (pit = depth-4 cell, no holder building) is being redesigned by other helpers; only the S1p holder smoke runs
    U_fill_fluid_distinct  UNBUILT             UNBUILT: one activeFluid field per map component
    U_ladder_state_legible UNBUILT             UNBUILT: RM_Ladder has no raised/lowered state (thingClass Building)
    U_pawn_height_ladder_legible UNBUILT             UNBUILT: no pawn draw offset by depth
    U_pawn_lowers_on_deeper_cell UNBUILT             UNBUILT: same
    U_pawn_rises_on_shallower_cell UNBUILT             UNBUILT: same
    U_pit_covered_invisible UNBUILT             UNBUILT: no superdeep cover (only legacy Building_TerrainMimicCover)
    U_pit_covered_seam_at_max_zoom UNBUILT             UNBUILT: same as pit_covered_invisible
    U_pit_trapped_reads_as_trapped UNBUILT             UNBUILT: same (walls above head need the offset)
    U_slime_occupant_below_surface UNBUILT             UNBUILT: same
    U_sluice_gate_state_legible UNBUILT             UNBUILT: no Sluice def
    U_spikes_read_distinct UNBUILT             UNBUILT: no per-cell spike def on excavations (RM_OpenPit_Spiked / RM_PitDigSite_*_Spiked are the legacy building pit)
    U_tar_fill_front_lags_water UNBUILT             UNBUILT: FlowPerPulse is global; viscosity not read by the engine
- step S_state: ticks 0 (planned 0), wall 2.8s, 31 calls
    A0_sanity_probe        PASS                rect read of the prefilled E5_sink run: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] (must see a known F=1)
    pulse[A] x8: 67 cells, 0 mismatching scenes []
    A_pulse_contract       PASS                8 pulses, 0 ticks, scheduler untouched, paused
    E2_east_A              PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_east_B              PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_north               PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_south               PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_west                PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_twins_identical     PASS                A [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] / B [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_channels_fill_every_direction PASS                first-full pulse by direction {'E2_east_A': 4, 'E2_north': 4, 'E2_south': 4, 'E2_west': 4} (bound n*D = 4; FLOWWORKS_CHANNEL_OSCILLATION_1 regression guard)
    E2_dry_ring            PASS                every non-channel, non-body ring cell undug, F=0, Soil
    E3b_recession_shipped  PASS                final [0, 0, 0, 1], W2R {'stock': 4.00473976, 'recededCount': 1, 'activeCellCount': 0}
    E5_sink_drains         PASS                band run drained per oracle: sinkTransferredTotal +10.0 (oracle +10); final [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    E5_inner_holds         PASS                interior prefilled twin final [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    E2s_shared_source_oracle PASS                both pairs == oracle (first-dug claims the source): {'E2s_shared_E7': [1, 1, 1, 1], 'E2s_shared_N7': [1, 0, 0, 0], 'E2s_shared_N8': [1, 1, 1, 1], 'E2s_shared_E8': [1, 0, 0, 0]}
    E2s_shared_source_both_fill FAIL       MOD      two channels off ONE source cell after 8 pulses: {'E2s_shared_E7': [1, 1, 1, 1], 'E2s_shared_N7': [1, 0, 0, 0], 'E2s_shared_N8': [1, 1, 1, 1], 'E2s_shared_E8': [1, 0, 0, 0]} -- the second-dug channel stalls at its inlet (FLOWWORKS_SHARED_SOURCE_STALL_1)
    A_global_vs_oracle     PASS                every excavated cell == oracle at every pulse
- step A_flow_defaults: ticks 0 (planned 0), wall 0.8s, 90 calls
    pulse[B] x7: 75 cells, 0 mismatching scenes []
    E3_budget_exhaustion   PASS                cap-5 pond delivered exactly 5 ([0, 0, 0, 1, 1, 1, 1, 1]), then rested; stock 0.004062602
    pulse[B-off] x2: 75 cells, 0 mismatching scenes []
    E3n_budget_off_supplies PASS                budget OFF: a spent pond supplies again ([0, 0, 0, 1, 1, 1, 1, 1] -> [0, 1, 1, 1, 1, 1, 1, 1])
    B_global_vs_oracle     PASS                all cells == oracle
- step B_budget: ticks 0 (planned 0), wall 3.6s, 20 calls
    pulse[C-off] x2: 85 cells, 0 mismatching scenes []
    E5n_sinks_off          PASS                sinks OFF: run [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], total 10.0->10.0, isSink any=False
    pulse[C-on] x3: 85 cells, 0 mismatching scenes []
    E5_sinks_back_on       PASS                sinks ON again: [1, 1, 0, 0, 0, 1, 0, 0, 0, 0], total +7.0 (oracle +7)
    C_global_vs_oracle     PASS                all cells == oracle
- step C_sink_toggle: ticks 0 (planned 0), wall 1.9s, 33 calls
    pulse[R] x8: 89 cells, 0 mismatching scenes []
    E2_rerun_determinism   PASS                E2_east_A (phase A) [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] vs E2_rerun (dug later, other body) [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    R_global_vs_oracle     PASS                all cells == oracle
- step R_determinism_rerun: ticks 0 (planned 0), wall 0.1s, 7 calls
    job pawns {'E7a_fillin': ('Human38025', 2.44), 'E7b_overflow': ('Human38028', 2.44), 'E8_dig': ('Human38031', 2.44)} (rejected, mining disabled: [])
    E4_engine_off          PASS                OFF for 310 ticks, past the due tick 251: nextPulseTick 251->251, cells moved []
    E1b_pulse_clamp        PASS                pulseIntervalTicks set 30 -> engine reads 60 (clamp floor 60)
    E1c_cadence_real_scheduler PASS                33 chunks of 60 ticks: nextPulseTick advances [60], lead [1]
    E4_engine_on_scheduled PASS                after 33 real scheduled pulses every oracle cell == oracle; E4 channel [1, 1, 1, 1]
    E6n_rain_toggle_off    PASS                rain fell (rate now 0.573) with rainFillsExcavations OFF over 33 pulses: no cell gained
    E7a_fillin_displaces   UNMEASURED UNRESOLVED job not done in 1980 ticks (cap 1945): {'E7a_fillin': {'position': {'x': 149, 'z': 92}, 'curJob': None, 'job': None, 'jobDef': None, 'drafted': None, 'downed': None}, 'E7b_overflow': {'position': {'x': 154, 'z': 88}, 'curJob': None, 'job': None, 'jobDef': None, 'drafted': None, 'downed': None}, 'E8_
    E7b_overflow_sanctioned UNMEASURED UNRESOLVED job not done ({'E7a_fillin': {'position': {'x': 149, 'z': 92}, 'curJob': None, 'job': None, 'jobDef': None, 'drafted': None, 'downed': None}, 'E7b_overflow': {'position': {'x': 154, 'z': 88}, 'curJob': None, 'job': None, 'jobDef': None, 'drafted': None, 'downed': None}, 'E8_dig': {'position': {'x': 
    E8_player_dig          UNMEASURED UNRESOLVED job not done in 1980 ticks: {'E7a_fillin': {'position': {'x': 149, 'z': 92}, 'curJob': None, 'job': None, 'jobDef': None, 'drafted': None, 'downed': None}, 'E7b_overflow': {'position': {'x': 154, 'z': 88}, 'curJob': None, 'job': None, 'jobDef': None, 'drafted': None, 'downed': None}, 'E8_dig': {'pos
- step J_jobs_scheduler: ticks 2290 (planned <= 1945 (job cap)), wall 14.5s, 221 calls
    E6_roof_readback       PASS                roofed excavated cells [(182, 60)]
    pulse[rain] x2: 101 cells, 0 mismatching scenes []
    E6_rain_fills_unroofed PASS                rate 0.573 x 2 pulses: unroofed F=1, roofed twin F=0, every excavated cell == oracle
- step E6_rain: ticks 0 (planned 0), wall 1.8s, 11 calls
    T0n_fluid_switch_refused PASS                set_active_fluid Tar after classification+fill: success=False, activeFluidRaw RM_Fluid_Water
    E9_log_budget          UNMEASURED HARNESS  sanity probe: E7b's expected 'conservation exception' warning not seen (0 warn+ lines since base)
- step T0_E9_tail: ticks 0 (planned 0), wall 0.0s, 5 calls
    Z_settings_restored    PASS                8 touched settings back to shipped defaults
- live run 3: pawns re-rolled OK but all three walked ~60 cells away (Tundra) and never took the WorkGiver jobs within cap 1945 -> E7a/E7b/E8 UNMEASURED (UNRESOLVED, pawn AI = SITE noise), E9 sanity UNMEASURED (no overflow happened). 2290 ticks. Fix: jawa/ordered_job with the WorkGiver's exact JobDef; WorkGiver selection -> UNCOVERED row.
- fresh quicktest map: {'menu': True, 'start': True, 'programState': 'Playing', 'wall_s': 10.8}
    L0_loaded_paused       PASS                programState Playing, ticksGame 1 -> 1 over 1 s
    L0_map_250             PASS                map 250x250 biome TemperateForest
    L1_log_clean           PASS                no FlowWorks error in 16 warn+ entries (base seq 40)
    L2_assembly_identity   PASS                loaded C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll sha 0fc9651256ec mvidMatchesFile True; repo sha 0fc9651256ec
    L3_defs_live           PASS                live pathCost {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300} (want {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300})
    L4_settings_default    PASS                43 settings read, all shipped defaults
    L5_site_pristine       PASS                excavated 0 bodies 0 superdeep 0 activeFluidRaw None
    E1a_cadence_shipped    PASS                pulseIntervalTicks 250, nextPulseTick 251 at tick 1
    L5_dry_weather         PASS                weather Clear rainRate 0.0
- step L_preflight: ticks 0 (planned 0), wall 20.2s, 54 calls
    SITE0_no_pawn_in_plots FAIL       SITE     [('Hare48216', (201, 5))]
- step SITE_paint: ticks 0 (planned 0), wall 0.1s, 4 calls ERROR Abort: a pawn stands in a plot rect
    ABORT                  FAIL       SITE     a pawn stands in a plot rect
    Z_settings_restored    PASS                0 touched settings back to shipped defaults
- live run 4: SITE abort at 0 ticks (wild hare in a plot rect). Fix: destroy_bulk nonColonists before SITE0 (plan recipe).
- fresh quicktest map: {'menu': True, 'start': True, 'programState': 'Playing', 'wall_s': 10.9}
    L0_loaded_paused       PASS                programState Playing, ticksGame 1 -> 1 over 1 s
    L0_map_250             PASS                map 250x250 biome TropicalRainforest
    L1_log_clean           PASS                no FlowWorks error in 16 warn+ entries (base seq 40)
    L2_assembly_identity   PASS                loaded C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll sha 0fc9651256ec mvidMatchesFile True; repo sha 0fc9651256ec
    L3_defs_live           PASS                live pathCost {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300} (want {'RM_Channel_Empty': 30, 'RM_Channel_Mid': 45, 'RM_Channel_Deep': 80, 'RM_Channel_Superdeep': 300})
    L4_settings_default    PASS                43 settings read, all shipped defaults
    L5_site_pristine       PASS                excavated 0 bodies 0 superdeep 0 activeFluidRaw None
    E1a_cadence_shipped    PASS                pulseIntervalTicks 250, nextPulseTick 251 at tick 1
    L5_dry_weather         PASS                weather Clear rainRate 0.0
- step L_preflight: ticks 0 (planned 0), wall 20.3s, 54 calls
    destroy_bulk nonColonists: 58
    SITE0_no_pawn_in_plots PASS                3 pawns, none in 36 plot rects
    SITE1_painted_readback PASS                36 rects cleared+Soil, 9 bodies painted, every scene cell fresh Soil, every body exactly its sources
- step SITE_paint: ticks 0 (planned 0), wall 1.3s, 77 calls
    S1_dig_ladder          PASS                D [1, 2, 3, 4] terrain ['RM_Channel_Empty', 'RM_Channel_Mid', 'RM_Channel_Deep', 'RM_Channel_Superdeep'] excavated +4 superdeep +1
    S1n_superdeep_is_max   PASS                deepen D=4 once more -> 4
    S1p_holder_at_D4_only  PASS                D4 holder True (occupants 0); D3 holder False  [pit smoke only: pit model under redesign]
    S2_fill_clamp          PASS                setFill 9 on D=2 -> F=2; setFill 1 on undug -> fillSet=False F=0
    S3_classification      PASS                W1, W8 limitless; W2/W2R 5, W3 10, W4 (edge,40) 200, W5 (interior,64) 320 all LIMITED
    S4_sink_band           PASS                isSink at edge distance 9: True; at 11: False
    S5_sticky_limitless    PASS                W6 (sticky OFF) limitless=False; twin W7 (ON) limitless=True
    S6_digToDepth_gate     UNCOVERED           jawa/designate_batch adds Designations directly, bypassing Designator_DigCanal.CanDesignateCell; the WorkGiver gate needs a HasJobOnCell probe tool (owed)
    S7_S9_capture_ladder   SKIP                pit model (pit = depth-4 cell, no holder building) is being redesigned by other helpers; only the S1p holder smoke runs
    U_fill_fluid_distinct  UNBUILT             UNBUILT: one activeFluid field per map component
    U_ladder_state_legible UNBUILT             UNBUILT: RM_Ladder has no raised/lowered state (thingClass Building)
    U_pawn_height_ladder_legible UNBUILT             UNBUILT: no pawn draw offset by depth
    U_pawn_lowers_on_deeper_cell UNBUILT             UNBUILT: same
    U_pawn_rises_on_shallower_cell UNBUILT             UNBUILT: same
    U_pit_covered_invisible UNBUILT             UNBUILT: no superdeep cover (only legacy Building_TerrainMimicCover)
    U_pit_covered_seam_at_max_zoom UNBUILT             UNBUILT: same as pit_covered_invisible
    U_pit_trapped_reads_as_trapped UNBUILT             UNBUILT: same (walls above head need the offset)
    U_slime_occupant_below_surface UNBUILT             UNBUILT: same
    U_sluice_gate_state_legible UNBUILT             UNBUILT: no Sluice def
    U_spikes_read_distinct UNBUILT             UNBUILT: no per-cell spike def on excavations (RM_OpenPit_Spiked / RM_PitDigSite_*_Spiked are the legacy building pit)
    U_tar_fill_front_lags_water UNBUILT             UNBUILT: FlowPerPulse is global; viscosity not read by the engine
- step S_state: ticks 0 (planned 0), wall 2.9s, 31 calls
    A0_sanity_probe        PASS                rect read of the prefilled E5_sink run: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] (must see a known F=1)
    pulse[A] x8: 67 cells, 0 mismatching scenes []
    A_pulse_contract       PASS                8 pulses, 0 ticks, scheduler untouched, paused
    E2_east_A              PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_east_B              PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_north               PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_south               PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_west                PASS                8/8 pulse vectors == oracle; [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_twins_identical     PASS                A [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] / B [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    E2_channels_fill_every_direction PASS                first-full pulse by direction {'E2_east_A': 4, 'E2_north': 4, 'E2_south': 4, 'E2_west': 4} (bound n*D = 4; FLOWWORKS_CHANNEL_OSCILLATION_1 regression guard)
    E2_dry_ring            PASS                every non-channel, non-body ring cell undug, F=0, Soil
    E3b_recession_shipped  PASS                final [0, 0, 0, 1], W2R {'stock': 4.001896, 'recededCount': 1, 'activeCellCount': 0}
    E5_sink_drains         PASS                band run drained per oracle: sinkTransferredTotal +10.0 (oracle +10); final [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    E5_inner_holds         PASS                interior prefilled twin final [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    E2s_shared_source_oracle PASS                both pairs == oracle (first-dug claims the source): {'E2s_shared_E7': [1, 1, 1, 1], 'E2s_shared_N7': [1, 0, 0, 0], 'E2s_shared_N8': [1, 1, 1, 1], 'E2s_shared_E8': [1, 0, 0, 0]}
    E2s_shared_source_both_fill FAIL       MOD      two channels off ONE source cell after 8 pulses: {'E2s_shared_E7': [1, 1, 1, 1], 'E2s_shared_N7': [1, 0, 0, 0], 'E2s_shared_N8': [1, 1, 1, 1], 'E2s_shared_E8': [1, 0, 0, 0]} -- the second-dug channel stalls at its inlet (FLOWWORKS_SHARED_SOURCE_STALL_1)
    A_global_vs_oracle     PASS                every excavated cell == oracle at every pulse
- step A_flow_defaults: ticks 0 (planned 0), wall 0.6s, 90 calls
    pulse[B] x7: 75 cells, 0 mismatching scenes []
    E3_budget_exhaustion   PASS                cap-5 pond delivered exactly 5 ([0, 0, 0, 1, 1, 1, 1, 1]), then rested; stock 0.00162504055
    pulse[B-off] x2: 75 cells, 0 mismatching scenes []
    E3n_budget_off_supplies PASS                budget OFF: a spent pond supplies again ([0, 0, 0, 1, 1, 1, 1, 1] -> [0, 1, 1, 1, 1, 1, 1, 1])
    B_global_vs_oracle     PASS                all cells == oracle
- step B_budget: ticks 0 (planned 0), wall 3.3s, 20 calls
    pulse[C-off] x2: 85 cells, 0 mismatching scenes []
    E5n_sinks_off          PASS                sinks OFF: run [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], total 10.0->10.0, isSink any=False
    pulse[C-on] x3: 85 cells, 0 mismatching scenes []
    E5_sinks_back_on       PASS                sinks ON again: [1, 1, 0, 0, 0, 1, 0, 0, 0, 0], total +7.0 (oracle +7)
    C_global_vs_oracle     PASS                all cells == oracle
- step C_sink_toggle: ticks 0 (planned 0), wall 1.8s, 33 calls
    pulse[R] x8: 89 cells, 0 mismatching scenes []
    E2_rerun_determinism   PASS                E2_east_A (phase A) [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] vs E2_rerun (dug later, other body) [[0, 0, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]]
    R_global_vs_oracle     PASS                all cells == oracle
- step R_determinism_rerun: ticks 0 (planned 0), wall 0.1s, 7 calls
    job pawns {'E7a_fillin': ('Human44272', 2.44), 'E7b_overflow': ('Human44275', 2.2204), 'E8_dig': ('Human44278', 1.52255988)} (rejected, mining disabled: [])
    J_orders_accepted      PASS                [('E8_dig', True, None), ('E7a_fillin', True, None), ('E7b_overflow', True, None)]
    J_workgiver_selection  UNCOVERED           WorkGiver_DigCanal/FillInCanal choosing the designation unprompted is not timed here (pawn AI noise; run 3 never chose it) -- owed HasJobOnCell probe tool
    E4_engine_off          PASS                OFF for 310 ticks, past the due tick 251: nextPulseTick 251->251, cells moved []
    E1b_pulse_clamp        PASS                pulseIntervalTicks set 30 -> engine reads 60 (clamp floor 60)
    E1c_cadence_real_scheduler PASS                16 chunks of 60 ticks: nextPulseTick advances [60], lead [1]
    E4_engine_on_scheduled PASS                after 16 real scheduled pulses every oracle cell == oracle; E4 channel [1, 1, 1, 1]
    E6n_rain_toggle_off    PASS                rain fell (rate now 0.318) with rainFillsExcavations OFF over 16 pulses: no cell gained
    E7a_fillin_displaces   PASS                sum F 2 -> 2 (conserved), middle D=0 terrain Soil, vector [1, 0, 1]
    E7b_overflow_sanctioned PASS                no room: sum F 3 -> 2, overflowDestroyedTotal +1.0 (want +1)
    E8_player_dig          PASS                designated cell dug by a colonist: D=1 terrain RM_Channel_Empty after 960 ticks (cap 2973, MiningSpeed 1.52)
- step J_jobs_scheduler: ticks 1270 (planned <= 2973 (job cap)), wall 8.9s, 171 calls
    E6_roof_readback       PASS                roofed excavated cells [(182, 60)]
    pulse[rain] x4: 100 cells, 0 mismatching scenes []
    E6_rain_fills_unroofed PASS                rate 0.318 x 4 pulses: unroofed F=1, roofed twin F=0, every excavated cell == oracle
- step E6_rain: ticks 0 (planned 0), wall 1.8s, 11 calls
    T0n_fluid_switch_refused PASS                set_active_fluid Tar after classification+fill: success=False, activeFluidRaw RM_Fluid_Water
    E9_log_budget          PASS                0 FlowWorks errors, 0 ledger imbalances, exactly 1 sanctioned conservation exception; 0 other error lines []
- step T0_E9_tail: ticks 0 (planned 0), wall 0.0s, 5 calls
    Z_settings_restored    PASS                8 touched settings back to shipped defaults
- live run 5 RESULT (fresh map, ordered jobs): 55 PASS, 1 FAIL = E2s_shared_source_both_fill (MOD, FLOWWORKS_SHARED_SOURCE_STALL_1; live == oracle), UNCOVERED 2 (S6 designator gate, J WorkGiver selection), UNBUILT 12, SKIP 1 (pit capture/ladder: redesign). 1,270 ticks, 58.6 s wall, 525 calls.
  tick budget per step: L 0 (20.3 s) | SITE 0 (1.3 s) | S 0 (2.9 s) | A 0 (0.6 s) | B 0 (3.3 s) | C 0 (1.8 s) | R 0 (0.05 s) | J 1270 (8.9 s; 310 engine-OFF window + 960 jobs) | rain 0 (1.8 s) | tail 0. Plan target 1,000-2,000; old suite 112,921.
- determinism: --compare run2 (074022) vs run5 (074420), two different fresh maps: 31 zero-tick rows, 0 differ (negative control: a mutated copy -> DIFFER, rc 1).
- step 4: learned items + RULED OUT notes written into the script docstring; checks E2s_*, E3b, prove P2 oracle, O-LIVE-NEG faults carry them. Promoted to validation_v2.py (DRAFT removed); plan line 6 + prove script path updated.
- step 5: not recorded through modcheck (modcheck run swaps ModsConfig = forbidden; northstar_driver run has no record_run). Result JSONs beside the script: validation_v2_result_20261002T074420.json (green-but-known-MOD-red), 074022 (run 2), 074157 (run 3, jobs UNRESOLVED).
- GAME LEFT UP: fresh Tundra quicktest from run 5, paused at tick 1271, test plots on map, all FlowWorks settings at shipped defaults, weather Clear (forced-weather lock expires next tick), flowworks tier unchanged.
