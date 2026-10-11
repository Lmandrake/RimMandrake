# GSS proof_all re-run 2026-10-10

## Deploy check

deploy_custom_mods.py --mod GimmeSomeSlack dry run: "Everything in sync" (172 files, 139 held-by-design evidence JSONs). PASS.

## Offline gate

--offline-gate: rc=0, red=[] (O1-O7 PASS incl. O7 23 fix shapes, O3 836/836, matrix selftest 58/58, human_review 33/33). PASS.

## Live run

`python.exe .../proof_all.py --live --no-shots` (full run, one call; 850.7 s wall, exceeded the 600 s call limit and finished in the background). Result: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T175536.json`. Rows 151: PASS 136, FAIL 15, SKIP 0. Shots were off (state-only), unlike nothing else changed in the harness.

## Diff vs 2026-10-05

Block: 10-05 -> 10-10
- preflight 3P -> 3P
- matrix 39P -> 39P
- core 31P -> 31P + 2F (B3, B4d)
- aerial 16P -> 20P + 1F (R2)
- hose 6P -> 6P
- maze 7P 1S -> 3P + 5F
- relay 8P -> 5P + 3F
- carry 8P -> 8P
- style 12P -> 11P + 1F (S9d)
- style_hose 6P -> 6P
- session (Z) 3P -> 2P + 1F
- save_load 4P -> 2P + 2F
Totals 143 PASS -> 136 PASS / 15 FAIL. Of the 15, 12 were PASS on 10-05, 1 (P1_reel_couples_to_tank) was SKIP, 1 (B4d) is new, 1 (Z) was PASS.

## Failures

Likely common cause for the lay failures (hypothesis, not diagnosed): M1/M2/M3b/M5/RL3/RL8 all show layOk=false, pathLen=null; M3b reports retractReason "no room for the straight lead-out from the nozzle". Pointer: hose lay/lead-out change in the 10-06 or 10-09 fix waves, or the maze/relay sites being blocked. RL6 fails downstream (relayCouplings 0) of RL3. SL3/SL4 are after-load census differences in hose (same cell, different hash) and reel styles.

- B3_whip_live_ends: whipDraws_on 1, liveFloorEnds 1 vs deadFloorEnds 3 (live-end counting changed).
- B4d_spark_budget_shared_visible_first (new row): scene liveEndsOnScreen 0, sparkSetOnScreen 0 vs stub 1/1 (visible-first spark budget not met in the scene).
- R2_spans_and_heads_drawn: spanDraws 2, topDraws 2, spanMeshes 2, groundVerts 50 (draw counts differ from expectation; no detail on expected).
- M1_open_maze_short_route, M2_gap_walled_reroutes, M5_walls_removed_recovers: hose never laid (layOk false).
- M3b_laid_hose_over_cap_retracts: not laid; retract reason "no room for the straight lead-out from the nozzle", 8 retracts.
- P1_reel_couples_to_tank: feedDraws 0 against RM_LiquidTank (was SKIP before, now runs).
- RL3_hose_onto_relay_B: layOk false, onEdge false, endPoint (51.731,100.94).
- RL6_flow_passes_through: B signal false, fedBy [], relayCouplings 0.
- RL8_chain_beyond_one_hose: pathA null, pathB 31.711 for span 64 / maxLength 40.
- S9d_restyle_and_materials: restyle ok (7 changed) but unprintedStrands [Strand, Strand_CoiledBlack, Strand_Orange] flagged.
- SL3_after_load_census_equal: hoses(H10) hash differs after load (f3b0... vs 487e...); reelStyles(R4) missing entries.
- SL4_carry_states_survive: before/after for CR4a and CR4b shown equal in the captured excerpt; the failing key is beyond the excerpt (see JSON, resumedAfterLoad...).
- Z_log_budget: NullReferenceException from a long event (twice), plus unrelated donor noise (RimFridge ResearchProjectDef, forgetTimers dictionary).
