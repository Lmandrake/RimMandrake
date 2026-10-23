# BENCH night live batch 2026-10-23 (save RM_fw_walkthrough_20261022d)

| item | check | verdict | evidence |
|---|---|---|---|
| HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS | skipped: FOUNDRY sweep validated | SKIP | - |
| HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES | skipped: FOUNDRY sweep validated | SKIP | - |
| HOSE_TANK_LAY_FIX_ENDS_ON_LID | map C: reelin + lay:104,z,116,z for the 4 Modern tanks (z 202/208/214/220) | PASS | every free end lands on (115,z), 'coupled to <tank>'; joint_check map C: 0 reel-joint gaps (only 2 pipe_stub FAILs, unrelated). joint_check_C_after_tanklay.json |
| HOSE_WORLD_SNAPSHOT_FIX_STALE_WHILE_PAUSED | PAUSED tick 130096: build_batch 5 walls x=110 z206-210 across reel 104,208's route, reelin + lay without a tick | PASS | lay ok at tick 130096 (unchanged); route bbox z>=205.15 goes round the wall's south end, wallCross 0, fellBack false; same route after a 2-tick control. snapshot_wall_route.png. Note: census centreCells read z=207 through x=110 (wall) while the drawn pose dips to z~205.5 -> filed |
| JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN | joint_check.py --all-maps on save d | FAIL | lists ends + the D11 crossing (map R 1864471x1864472 at 116,43, expected), but 5 of 7 pipe_stub FAILs are false: ends fed by a bleed well (C 25,130) or ending sprinkler lines (R 134,47/53/59/65) -- net:x,z answers 'no liquid machine' for RM_LiquidTap/RM_SprinklerHead -> filed JOINT_CHECK_FIX_TAPS_LOOK_LIKE_NOTHING. 2 real tails (C 131,41; R 142,45) -> WALK_PIPES_PRUNE_TWO_TAILS_TO_NOWHERE. joint_check_all.json, jc_*.png |
| C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE | | pending | |
| PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO | zoo census maps C/R around proof_hose --no-fresh-map --only walls, realflow, relay | PASS | 9 non-colonists on C, 1 on R before and after each block (zoo_before/after_walls/after_realflow/after_relay.json); walls HW1 PASS 19 laid |
| PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN | validation_v2 --live --current-map; liquid_checks --only L2 on map C | FAIL | v2 refuses a non-pristine map at L1 (abort, zoo kept 9). liquid_checks: sweep_at_start kept 9, but quiet_site 'hostiles_removed' vanished both pirate PRISONERS (zoo 9->7, zoo_after_liquid.json) -> QUIET_SITE_FIX_JAILBREAK_BY_VANISHING. raid_trench/water_scenes_walk/prep_site not run (hostiles/long) |
| PROOF_REELS_FIX_STILL_STAGED_WEST | fresh map: proof_hose realflow, lines_proof, walk_gaps_proof (ports, ponds), pipe_levelling_perf_proof --rehearsal | FAIL | realflow 13/13 NS rows PASS (NS_relay_chain PASS on fresh map; its save-d FAIL was SITE), lines_proof 11/11 PASS, ponds 2/2 PASS. walk_gaps PORTS_ONE_HOSE_PER_SIDE + PORTS_CORNER_REFUSED UNMEASURED/SITE: reel 92,39 now faces N toward the pump 4 cells away -> 'no room for the straight lead-out from the nozzle' (HARNESS, reel_toward on a short lay). pipe_levelling rehearsal: layFailures 360, 'no hose reel at (100,0,4)', rows UNMEASURED; that map also logged 100 conservation exceptions (200 levels destroyed). walk_gaps_ports_ponds.json, pipe_levelling_rehearsal.json |
| VALIDATION_HOSE_REELS_FIX_STILL_WEST | fresh map: proof_hose --only relay (validation_hose) | FAIL | reels face per RELAY_TARGET; RL2,3,5,6,7,8,9 PASS. RL4 FAIL: C faces West, hose meets its brass inlet (capture relay_C_west_inlet_fresh.png looks right) but drawnEnd x 76.353 sits inside C's edge and west_inlet wants dst[0]-tol < x < dst[0] -> presumed HARNESS (stale window), unproven. Save-d relay run: RL4/5/6/8 SITE (deep channel at 75,100) -> RELAY_PROOF_FIX_SITE_WIPES_THE_REVIEW |
| X8C_WALKER_FIX_FELL_THROUGH_THE_FLOOR | validation_v2 --live (calm site save) | FAIL | v2 62 PASS / 1 UNMEASURED: X8c UNMEASURED/SITE -- 'RM_PitCover_PlankLattice lid gave way under the walker': covered=False beneath=False sink 1.2 drawDz -1.035 at 141,70. The criterion bars UNMEASURED. v2_calm.json |
| MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS | capture C3 north | pending | |
| TANK_FLANGE_FIX_HOVERS_MID_PIPE | capture C3 north | pending | |
| TANK_STUB_HUNT_POINTS_AT_NOTHING | capture C3 north | pending | |
| C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING | capture R C1 cord | pending | |
| CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE | capture R C11 R1/R2 | pending | |
| FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE | capture R2 ford | pending | |
| PUMPSTATION_SOUTH_PORT_REDRAW_ALMOST_THERE | capture Kludged+Repaired south port | pending | |

## log
