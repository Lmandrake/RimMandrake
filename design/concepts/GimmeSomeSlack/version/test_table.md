# Gimme Some Slack 0.1.0: test-and-stage table

Generated 2026-11-16T07:39:13-08:00 from `test_table.json` (the record; this is its read view) by the throwaway `make_test_table.py`. Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Columns follow Explosive Knockback's table.

## Counts (measured)

- bars: 49
- with a deciding test runnable today (an offline test that ran, or an in-game scene whose entry exists): 49
- with every deciding test runnable today: 48
- with at least one test of any kind runnable today, supports included (proof rows whose code exists count): 49
- with an offline deciding test, all green today: 25
- decided offline only (no game needed): 2
- in-game scenes: 26 named in scenes.json plus 2 specified here; entry exists 28, absent 0
- older proof rows (supports): 170 mapped in proof_leaves.ROW_LEAVES (2 of them gravship_scene), code found for 170; last live run J20261113T075443Z-3da526 (SteveDesktop, 35aaf354ea, 2026-11-13): 156 rows, 154 PASS, FAIL M2c_no_sharp_bends and SC_no_two_cords_alike (ledger, BENCH shard); mapped rows and run rows not reconciled one to one
- offline tests: 25 built before Stage 3 (ran today: 24 PASS, 1 FAIL); 4 specified at the lock, built in Stage 3: T_SETTINGS_SWEEP_OFFLINE PASS, T_SHOCK_RULE_OFFLINE PASS, T_CORD_GEOMETRY_OFFLINE PASS, T_STATICS_CENSUS PASS

## Bars

| bar | from | proves at | decides | supports (not proof rows) | proof rows | runnable today |
|---|---|---|---|---|---|---|
| `invisible_conduit` | record | 6 | sc_conduit_invisible | - | 7 | all |
| `cord_slack_lay` | record | 6 | T_CORE, T_CORD_GEOMETRY_OFFLINE, sc_cords_slack | T_END_HEAP, T_MATRIX | 20 | all |
| `junction_strips` | record | 6 | T_CORE, sc_junction_strips, sc_dense_tangle | T_JUNCTION_ART, T_STRIP_ART | 11 | all |
| `connectivity_truth` | record | 6 | T_CORE, sc_true_to_grid | T_MATRIX | 54 | all |
| `break_ends_live_dead` | record | 6 | T_CORE, sc_cut_ends | - | 20 | all |
| `rebuild_cost` | record | 6 | sc_rewire_cost | T_CORE | 7 | all |
| `overhead_spans` | record | 6 | sc_spans | T_CORE | 11 | all |
| `downed_spans` | record | 6 | sc_fallen_span | T_CORE | 12 | all |
| `fallen_wire_shock` | record | 6 | sc_shock, sc_shock_reach | T_SHOCK_OUTLIVES, T_SHOCK_OUTLIVES_BINDING, T_SHOCK_BITES_BINDING, T_SHOCK_RULE_OFFLINE | 8 | all |
| `wire_down_alert` | record | 6 | sc_restring | - | 7 | all |
| `restring_job` | record | 6 | sc_restring | - | 7 | all |
| `power_theft` | record | 6 | T_CORE, sc_tap_theft, sc_statics_new_game | - | 4 | all |
| `four_styles` | record | 6 | T_CORE, sc_four_looks | T_GATE, T_JUNCTION_ART | 24 | all |
| `mod_settings` | record | 6 | T_SETTINGS_SWEEP_OFFLINE, sc_settings, sc_owner_change, sc_gravship | T_CORE, T_GATE | 37 | all |
| `pipe_pole_switch` | record | 6 | T_CORE, sc_settings | - | 33 | all |
| `gravship_connectivity` | record | 6 | sc_gravship | - | 6 | all |
| `owner_change_cut` | record | 6 | sc_owner_change | - | 3 | all |
| `game_statics_reset` | record | 6 | sc_statics_new_game | T_STATICS_CENSUS | 1 | all |
| `uninstall_clean` | record | 6 | sc_removal_consequence | - | 0 | all |
| `no_hose` | record | 4-5 | T_NO_HOSE | - | 0 | all |
| `floor_end_shock` | record | 6 | T_SHOCK_RULE_OFFLINE, sc_floor_end_shock, sc_fuel_ignition, sc_shock_reach | - | 12 | all |
| `shock_reach_setting` | both | 6 | T_SHOCK_RULE_OFFLINE, sc_shock_reach | - | 3 | all |
| `cords_draw_under_things` | record | 6 | T_CORE, sc_cords_under_items, sc_cords_under_items | T_FW_PIT_DRAW_CENSUS, LOOK_STAGE8 | 54 | all |
| `cords_join_stubs_on_position_and_slope` | record | 6 | T_STUB_JOINS, T_STUB_ART_CENSUS, sc_stub_joins | - | 0 | all |
| `conduit_invisible` | tree | 6 | sc_conduit_invisible | T_GATE | 7 | all |
| `cords_lie_slack` | tree | 6 | T_CORE, T_CORD_GEOMETRY_OFFLINE, sc_cords_slack | T_MATRIX, T_END_HEAP | 20 | all |
| `no_unforced_sharp_turn` | tree | 6 | T_CORD_GEOMETRY_OFFLINE, sc_no_sharp_turn | - | 2 | all |
| `cords_meet_walls_at_face` | tree | 6 | sc_walls | T_CORE, T_END_HEAP | 6 | all |
| `strip_at_every_junction` | tree | 6 | T_CORE, sc_junction_strips | T_JUNCTION_ART, T_STRIP_ART | 3 | all |
| `dense_block_tangle` | tree | 6 | T_CORE, sc_dense_tangle | T_MATRIX | 8 | all |
| `cord_shape_variation_probe` | tree | 6 | T_CORE, sc_no_repeat | - | 1 | all |
| `cords_never_repeat` | tree | 6 | T_CORE, sc_no_repeat | T_H_NO_TWO_ALIKE_SHORT | 1 | all |
| `drawing_true_to_grid` | tree | 6 | T_CORE, sc_true_to_grid, sc_cords_under_items | T_MATRIX | 54 | all |
| `cut_live_and_dead_ends` | tree | 6 | T_CORE, sc_cut_ends | - | 20 | all |
| `floor_end_shocks_crossers` | tree | 6 | T_SHOCK_RULE_OFFLINE, sc_floor_end_shock | - | 7 | all |
| `no_stall_on_rewire` | tree | 6 | sc_rewire_cost | T_CORE | 7 | all |
| `spans_above_everything` | tree | 6 | sc_spans | T_CORE, T_FW_PIT_DRAW_CENSUS, T_H_KINETIC_SWAY | 11 | all |
| `fallen_span_on_ground` | tree | 6 | sc_fallen_span | T_CORE, T_H_EXPLODE_PARSE | 12 | all |
| `fallen_wire_shocks_crossers` | tree | 6 | sc_shock | T_SHOCK_OUTLIVES, T_SHOCK_OUTLIVES_BINDING, T_SHOCK_BITES_BINDING, T_SHOCK_RULE_OFFLINE | 5 | all |
| `restring_cut_span` | tree | 6 | sc_restring | T_H_RESTRING_PROOF | 7 | all |
| `live_wire_lights_fuel` | tree | 6 | sc_fuel_ignition | - | 2 | all |
| `tap_steals_and_costs_goodwill` | tree | 6 | T_CORE, sc_tap_theft | - | 3 | all |
| `four_looks_one_run` | tree | 6 | T_CORE, sc_four_looks | T_GATE, T_JUNCTION_ART | 24 | all |
| `settings_switch_cleanly` | tree | 6 | T_SETTINGS_SWEEP_OFFLINE, sc_settings | T_CORE, T_GATE, T_H_AERIAL_PROBE_BATCH | 33 | all |
| `gravship_keeps_connections` | tree | 6 | sc_gravship | - | 6 | all |
| `owner_change_coils_wires` | tree | 6 | sc_owner_change | - | 3 | all |
| `statics_clear_between_games` | tree | 6 | sc_statics_new_game | T_STATICS_CENSUS | 1 | all |
| `no_hose_in_gss` | tree | 4-5 | T_NO_HOSE | - | 0 | all |
| `walk_scavenger_base` | tree | 8 | sc_walk, LOOK_STAGE8 | T_H_PLAYTEST_RUNNER, sc_cords_under_items | 6 | some |

## Tests (offline and scenes; the 170 proof rows are in the JSON)

| test | stage | kind | file :: entry | runs today | observes |
|---|---|---|---|---|---|
| `T_CORE` | 4-5 | offline | `src/RimMandrake/Utils/selftest_gimmesomeslack.py` | PASS rc=0 188.79s | the C# SelfTest on the production core and aerial halves against the Python oracle: graph reduction, planner, slack laying, shape no-two-alike, junction strips, |
| `T_STUB_JOINS` | 4-5 | offline | `src/RimMandrake/Utils/selftest_gimmesomeslack.py` | FAIL rc=1 9.81s | Core/StubJoinAudit over 524 generated scenes (four looks x boxes, switches with 1-4 cords, wall/rock faces through and dead-ending, his stations 12 and 25): eac |
| `T_STUB_ART_CENSUS` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py` | PASS rc=0 0.02s | every texture under Textures/ is classed in StubArt.Census (stubbed, position only, loose end, cord); a planted unknown texture goes red |
| `T_GATE` | 2 | offline | `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` | PASS rc=0 202.97s | the offline tier O1-O8: mod files, csproj and DLL, the 26 shipped setting defaults, style art sanity with planted faults, review-round art, GPT fix shapes, lamp |
| `T_MATRIX` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/northstar_matrix/selftest.py` | PASS rc=0 13.65s | the scene matrix generator, oracle, placer and fake game: 57 checks, 17 negative controls |
| `T_NO_HOSE` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` | PASS rc=0 1.83s | the mod ships no hose, reel or pipe def, texture or class; a planted hose goes red |
| `T_SHOCK_OUTLIVES` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_shock_outlives_wire.py` | PASS rc=0 0.06s | a fallen wire's shock cells die with the wire (GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE) |
| `T_SHOCK_OUTLIVES_BINDING` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_shock_outlives_wire_binding.py` | PASS rc=0 8.03s | the live binding of the shock-outlives fix, compiled offline |
| `T_SHOCK_BITES_BINDING` | 4-5 | offline | `src/RimMandrake/Utils/selftest_gss_shock_still_bites_binding.py` | PASS rc=0 0.41s | a live fallen wire still shocks after the outlives fix (binding, offline) |
| `T_END_HEAP` | 4-5 | offline | `src/RimMandrake/Utils/selftest_gss_end_heap_budget.py` | PASS rc=0 0.02s | long-run end heaps stay inside the loop budget |
| `T_JUNCTION_ART` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_junction_necks.py` | PASS rc=0 0.14s | the Modern and Futuristic T/X junction PNGs: body wider than the cord, necks meet the cord |
| `T_STRIP_ART` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_strip_art.py` | PASS rc=0 0.05s | the Modern power-strip PNGs have no black fringe (his 2026-11-08 sitting) |
| `T_FW_PIT_DRAW_CENSUS` | 4-5 | offline | `src/RimMandrake/FlowWorks/selftest_flowworks_pit_draw_census.py` | PASS rc=0 0.17s | everything drawn outside the map-mesh print against FlowWorks' under-liquid law; GSS floor cords on a pit floor are faded by FloorSeen (CordUnderLiquid), overhe |
| `T_PROOF_LEAVES` | 2 | offline | `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_proof_leaves.py` | PASS rc=0 0.08s | every proof row cites a leaf of tree.json and every leaf has a row or a live item owing it |
| `T_H_RESTRING_PROOF` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_restring_proof.py` | PASS rc=0 0.15s | harness: the M15f re-string proof path's instruments |
| `T_H_KINETIC_SWAY` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_kinetic_sway.py` | PASS rc=0 0.42s | harness: the M22 kinetic-sway proof rows, probe transport, launcher |
| `T_H_AERIAL_PROBE_BATCH` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_aerial_probe_batch.py` | PASS rc=0 0.61s | harness: the aerial mod-settings probe batch |
| `T_H_EXPLODE_PARSE` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_explode_parse.py` | PASS rc=0 1.33s | harness: the explode probe's parsing against production AerialMath |
| `T_H_NO_TWO_ALIKE_SHORT` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_two_alike_short.py` | PASS rc=0 0.02s | harness: SC_no_two_cords_alike exempts cords under 3 cells |
| `T_H_PLAYTEST_RUNNER` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_playtest_runner.py` | PASS rc=0 0.02s | harness: the walk launcher's recipe expansion |
| `T_H_PROOF_DRIVERS` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_proof_drivers.py` | PASS rc=0 0.18s | harness: the proof drivers' false-pass fixes |
| `T_H_REVIEW_LEFTOVERS` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_review_leftovers.py` | PASS rc=0 0.26s | harness: post-approval proof-harness findings |
| `T_H_WEAKCLOSE_GUARDS` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_weakclose_guards.py` | PASS rc=0 0.01s | harness: source-shape guards for Verse-bound findings |
| `T_H_HUMAN_REVIEW` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_human_review.py` | PASS rc=0 0.04s | harness: the review map layout |
| `T_H_PROOF_ALL` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/northstar/selftest_proof_all.py` | PASS rc=0 12.81s | harness: proof_all's durability on a fake bridge |
| `T_SETTINGS_SWEEP_OFFLINE` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_settings_sweep.py` | PASS rc=0 2.31s | the settings sweep, moved out of the game: for each key of the shipped floor table (validation.SHIPPED, 26) and each AerialSettings field, either an offline fli |
| `T_SHOCK_RULE_OFFLINE` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/ShockRuleChecks.cs` | PASS rc=0 182.09s | the who-is-shocked rule as a pure table: line kind (floor end, downed span, FlowWorks deck cord) x live by power path at the last poll x setting (None, Only dow |
| `T_CORD_GEOMETRY_OFFLINE` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/CordGeometryChecks.cs` | PASS rc=0 190.03s | on the oracle scenes and on the M2c junction-battery site as a lab world: every edge's drawn length is at least 1.4 times its chord, every edge over four cells  |
| `T_STATICS_CENSUS` | 4-5 | offline | `src/RimMandrake/GimmeSomeSlack/selftest_gss_statics_census.py` | PASS rc=0 0.11s | every mutable static field in Source (outside SelfTest) is cleared in GssSessionReset.cs or listed immutable with a reason; planted: a new static collection not |
| `sc_conduit_invisible` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_conduit_invisible | entry exists | no pipe drawn on any PowerConduit or WaterproofConduit cell, a cord per edge on both runs, overlay connector lines present; the HiddenConduit run owns no cord |
| `sc_cords_slack` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_cords_slack | entry exists | every edge at least 1.4 times its chord, no bend tighter than the minimum radius, an excursion off the conduit line on edges over four cells |
| `sc_no_sharp_turn` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_no_sharp_turn | entry exists | strands read greater than zero in every look (the instrument sees cords); unforced == 0 in every look, at plug and junction ends as well as mid-cord; every forc |
| `sc_walls` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_walls | entry exists | no sampled point on an impassable cell except wall-face stubs; a stub on both faces of each crossing; two plates on the pocket's dive |
| `sc_junction_strips` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_junction_strips | entry exists | one piece of the look's family per junction, every arm end in its socket, Modern pieces the PowerStrip art, Industrial the Junction_T/X box |
| `sc_dense_tangle` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_dense_tangle | entry exists | tangle-pile pieces over the block, crossings per cell above the sparse room's, the judge reads a tangle |
| `sc_no_repeat` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_no_repeat | entry exists | every pair above the minimum shape distance; the judge sees no repeated stamp |
| `sc_true_to_grid` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_true_to_grid | entry exists | every cord's ends on one net, one cord end per power connection, no second cable at the pump, no plug on a pipe slot; the cord reaching the dual-port device ent |
| `sc_cords_under_items` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_cords_under_items | entry exists | a floor cord under a battery, a shelf of items and furniture, dry and in a FlowWorks pit: the cord's draw altitude and queue read below the thing's, the junctio |
| `sc_cut_ends` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_cut_ends | entry exists | no edge across either gap; run one: the generator side live, the far side dead, and after switch-off both dead within one poll; run two: both ends live after th |
| `sc_rewire_cost` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_rewire_cost | entry exists | max slice under 20 ms and no frame over the bar for each lone and burst action; the touched edge's drawing current after |
| `sc_spans` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_spans | entry exists | the span's draw altitude reads above both the Pawn and Building altitude layers, sag above zero; the lamp mast's span joins the same PowerNet and its lamp reads |
| `sc_fallen_span` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_fallen_span | entry exists | each fallen wire draws cells on the ground between its anchors, at ground layer below pawns; live end sparking and dead end limp per net; the unpowered span's w |
| `sc_shock` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_shock | entry exists | hauler, visitor and the other span's re-stringer shocked; this wire's re-stringer not |
| `sc_floor_end_shock` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_floor_end_shock | entry exists | hauler 1, hauler 4, the visitor and constructor B shocked; hauler 1 shocked again with the aerial master off; with maxSparkingEnds 1 both live-end haulers shock |
| `sc_shock_reach` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_shock_reach | entry exists | the default reads All; All: all three haulers shocked; Only downed lines: the fallen-wire and deck-cord haulers shocked, the floor-end hauler not; None: none sh |
| `sc_restring` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_restring | entry exists | alert lists both the cut anchor and the grounded one; each jump centres the camera on the listed anchor's cell; the job runs at the cut anchor; after it the spa |
| `sc_tap_theft` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_tap_theft | entry exists | power flows from their net into ours only; their goodwill falls each day after sighting and stops after removal; every other faction's goodwill unchanged |
| `sc_four_looks` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_four_looks | entry exists | each run's members report one style, and the four runs' cord texture paths and junction defs all differ; a judge agent given the four captures in grayscale (art |
| `sc_settings` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_settings | entry exists | each feature's observable state changes with its switch and returns on flip-back, no restart: drip loops drawn or not at a mast; slideUnder off makes the dual-p |
| `sc_gravship` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_gravship | entry exists | switch on: the aboard span is still linked after landing and the true-to-grid read passes; switch off: the aboard span is down after landing (no link between th |
| `sc_walk` | 6 | live_full | `src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py` :: scene_walk | entry exists | after reload the true-to-grid and live/dead reads match before save; repeat and second order pass the same reads; each rewire's frame time under the 20 ms bar;  |
| `sc_shock_restring` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_shock_restring | entry exists | the hauler is shocked crossing the sparking end; the re-stringer is not; after the re-string power flows and no one is shocked |
| `sc_owner_change` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_owner_change | entry exists | switch on: no link from the middle mast to either mast of ours, the sweep's cut count equals the two links cut, the message shown, the middle mast unpowered by  |
| `sc_fuel_ignition` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_fuel_ignition | entry exists | live and switch on: fire on the fallen wire's puddle cell and none on the floor end's puddle cell; switch off: no fire; wire dead: no fire |
| `sc_statics_new_game` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_statics_new_game | entry exists | game 1 lists the tap and both picks, holds printed-section keys and strand names, and prices the fallen wire's cells under its map id; the new quicktest starts  |
| `sc_removal_consequence` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/validation.py` :: scene_removal_consequence | entry exists | the consequence is written down: which defs drop and what errors log |
| `sc_stub_joins` | 6 | live_minimal | `src/RimMandrake/GimmeSomeSlack/northstar/live_stub_joins.py` :: main | entry exists | on his review map (save GSS_OWNER_LOOK_20261116) the probe joins: runs Core/StubJoinAudit on the live pieces of every station: stubs off line or slope, bare stu |
| `LOOK_STAGE8` | 8 | look | `None` | entry ABSENT | his walk of a scavenger base on his full list, with a mid-way reload |

## Held look statements placed

- `design/RimMandrake/validation_holding/owner_look_defects_2026-11-12.md` row 34, "Here is a screenshot of a GSS connector unfortunately showing up through the battery it should be beneath in a pit." -> bars cords_draw_under_things; test T_CORE (slideunder: under) + T_FW_PIT_DRAW_CENSUS + sc_cords_under_items (in scenes.json since 2026-11-14) (stage 4-5 then 6, defect; offline checks (run today) + in-game draw-order read (owed); bar added by his card 2026-11-14)
- `design/RimMandrake/validation_holding/owner_look_defects_2026-11-12.md` row 36, "The wires are also above the items and furniture otherwise, likely all the same problem." -> bars cords_draw_under_things; test T_CORE (slideunder: under) + sc_cords_under_items (in scenes.json since 2026-11-14) (stage 4-5 then 6, as row 34)
- `design/RimMandrake/validation_holding/owner_look_defects_2026-11-13.md` row 16, "[Image #8] Also, the GSS cables are now correctly below the items." -> bars cords_draw_under_things; test sc_cords_under_items (in scenes.json since 2026-11-14) keeps it so (stage 6, approval: the regression the in-game read guards; bar added by his card 2026-11-14)

## The five judge corrections (rm-coverage-judge-1794599377), checked against the current text

- g1 (sc_floor_end_shock): text present True; applied 910f69411e (Designer run rm-role-designer-1794600246); no judge has read it since
- g2 (sc_floor_end_shock|sc_fuel_ignition|sc_shock_reach): text present True; applied 910f69411e (Designer run rm-role-designer-1794600246); no judge has read it since
- g3 (sc_no_sharp_turn): text present True; applied 910f69411e (Designer run rm-role-designer-1794600246); no judge has read it since
- g4 (sc_owner_change): text present True; applied 910f69411e (Designer run rm-role-designer-1794600246); no judge has read it since
- g5 (sc_statics_new_game): text present True; applied 910f69411e (Designer run rm-role-designer-1794600246); no judge has read it since

## The settings sweep, moved offline

settings_switch_cleanly and mod_settings: the flip-and-return of every switch and the patch-to-switch map are decided offline by T_SETTINGS_SWEEP_OFFLINE (specified); T_CORE already flips the aerial switches and the pipe-pole kind rule offline (SwitchFlipChecks). sc_settings keeps only what needs the renderer and the live Harmony instance: master off and on restoring vanilla conduit and lamp art without a restart, and the applied-patch list read at runtime. The leaf's text is not edited.
