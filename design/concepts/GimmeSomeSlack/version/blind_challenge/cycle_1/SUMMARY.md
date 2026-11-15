# Gimme Some Slack 0.1.0 — blind challenge (Stages 4 and 5), cycle 1

## Start time
2026-11-15T08:35:06Z (00:35 PST), recorded before any GSS input was opened.

## Lane 1
Lane 1 committed before any builder test, journal, evidence, gap list or test table was opened (the commit sha is the proof).
Inputs: tree.json, sheet.md, plan.md, version/VERSION.json, version/bars.md; the kernels under Source/Core, Aerial/AerialMath.cs,
ShockRule.cs, TapWindow.cs and _Shared/SlackGeometry; GimmeSomeSlackMod.cs and AerialSettings.cs (defaults, sliders); the patch XML.
CordShapeAudit.cs was read too, because the no_unforced_sharp_turn oracle names it as its instrument.

Rows: 59 [measured]: PASS 33, FAIL 6, INFO 6, UNSETTLED 14 (all 14 UNSETTLED are not_kernel rows).
Run: `python3 lane1/run_lane1.py` (about 35 s), rows in `lane1/lane1_rows.jsonl`.

FAIL rows (the kernel against the bar's own oracle; whether each is a Problem or Polish is decided in lane 2):
- L1_NO_REPEAT (cords_never_repeat): two 4-cell runs side by side draw the same cord (mean point gap 0.01 cell, shrunk to 2 runs,
  build seed 6). The kernel's own CordShape.Table agrees: 31 of 672 pairs are under its own TooAlikeBelow 0.3, all at run length 4.
  Lengths 6, 9 and 12 are fine (smallest gap 0.46).
- L1_CORD_BENDS_TALLY (no_unforced_sharp_turn): the bar's named instrument, CordShapeAudit.BendTally, run offline over 80 random
  scenes: 82 unforced bends in 728 strands (1381 bends). L1_CORD_SHARP_TURN, my own coarser measure, agrees.
- L1_CORD_SLACK_RATIO (cords_lie_slack): 4 of 434 strands are under 1.4x their chord (worst 1.206), all on cut-routed leads with a
  live whip tail (L1_CORD_SLACK_RATE).
- L1_CORD_EXCURSION (cords_lie_slack): 5 of 139 edges over four cells never leave their conduit line by a cell (lowest 0.56)
  (L1_CORD_EXCURSION_RATE).
- L1_FALLEN_LAY_GROUND (fallen_span_on_ground): a fallen wire that is not Blocked lays a grounded point 0.044 cell inside a wall
  cell (seed 97531 trial 117, 1 of 1500).

Passing and offline-relevant: L1_NO_HOSE_SCAN (no_hose, no_hose_in_gss; SelfTest/ and northstar/ skipped while blind),
the shock table, the fixer's scope, the shock default (All), theft conservation and goodwill, link refusals, MST, removal and
gravship plans, net truth, one lead per device, cuts live and dead, the far-side battery, the junction pieces, the dense tangle,
determinism, the cache after a change, reach soundness, the rebuild gate, the slice window, the snapshot pool and the settings sweep.


## Lane 2 reruns
All 27 `kind: offline` tests of `version/test_table.json` rerun with their recorded commands (`lane2/rerun_offline.py`,
rows in `lane2/reruns.jsonl`) [measured]:
- Same verdict: 26 of 27. Exact match (verdict and last line): 23 of 27.
- T_CORE, T_SHOCK_RULE_OFFLINE and T_CORD_GEOMETRY_OFFLINE: PASS as recorded; their check counts grew since `runs_today`
  (4508 to 4510, 4515 to 4513 [measured]: tests were added or moved after the table was written), so the last line differs.
- T_GATE: rc 1 on the first rerun (`validation:O3_core_selftest` red), rc 0 on a second run minutes later with O3 4510/4510.
  The first red was not explained (RIMMANDRAKE_STEADY_GSS_GATE_RED_ONCE_THEN_GREEN).
- The offline bars' decider T_NO_HOSE: PASS before and after the fix (`lane2/reruns_after_fix.jsonl`, 6 of 6 match).

## Planted
31 faults first (`lane2/planted_faults.json`, results `lane2/planted_results.jsonl`, baseline row first, `tree_clean_after: true`
last). 21 in kernels (every kernel the brief names has at least one), 6 in game-side callers, a setting and a patch, and 4 hose
plants for the two offline bars [measured]:
- Caught (a NEW failing row against the baseline): 25 of 31. The core suite caught 20, lane 1 caught 15.
- Missed: PF_GAME_FLOOR_DEAD_ENDS_BITE, PF_GAME_ANY_BUILDER_EXEMPT, PF_PATCH_SWITCH_NOT_STYLED, PF_MOTION_LIVE_END_LIMP (no offline
  test reaches them; their deciders are Stage 6 scenes), and **PF_HOSE_TEXTURE_FOLDER and PF_HOSE_COMP_CLASS_ATTR**.
- **T_NO_HOSE was the only thing between a hose leak and green on both offline bars, and two of its four hose plants passed it**
  (a texture in a `Hose/` folder, a comp named only by its `Class` attribute). My own lane-1 hose scan missed the same two.
  It caught the planted defName and texPath. Fixed (below).
- After the fixes (`lane2/planted_after_fix.jsonl`): both hose plants and the old master gate, put back, are caught; tree clean.

## Faults
`lane2/faults.json`, ten refusal records, each filed as a rimflow item [measured]:

| id | class | bar | status |
|---|---|---|---|
| RIMMANDRAKE_WIDEN_GSS_HOSE_SCAN_ONE_TEST_TWO_BARS | Problem | no_hose_in_gss, no_hose | FIXED 6d2aeb9c3f |
| RIMMANDRAKE_UNGATE_GSS_DROPPED_CORDS_FROM_OVERHEAD_MASTER | Problem | shock_reach_setting, settings_switch_cleanly | FIXED 6d2aeb9c3f |
| RIMMANDRAKE_VARY_GSS_SHORT_CORDS_TWINS_AT_FOUR_CELLS | Problem | cords_never_repeat | PENDING |
| RIMMANDRAKE_UNBEND_GSS_RANDOM_BASES_SEVEN_SCENES_HID_IT | Problem | no_unforced_sharp_turn | PENDING |
| RIMMANDRAKE_SLACKEN_GSS_CUT_END_LEADS_WHIP_STEALS_SLACK | Problem | cords_lie_slack | PENDING |
| RIMMANDRAKE_STRAY_GSS_CORDS_A_CELL_OFF_THEIR_LINE | Problem | cords_lie_slack | PENDING |
| RIMMANDRAKE_LIFT_GSS_FALLEN_WIRE_OFF_WALL_CORNER | Polish | fallen_span_on_ground | PENDING |
| RIMMANDRAKE_STEADY_GSS_GATE_RED_ONCE_THEN_GREEN | Polish | (instrument) T_GATE | PENDING |
| RIMMANDRAKE_REWORD_GSS_NO_HOSE_BAR_POLES_DRAW_PIPES | Polish | no_hose_in_gss (bar words) | NOTED_FOR_CONDUCTOR |
| RIMMANDRAKE_COVER_GSS_CALLERS_FOUR_PLANTS_WALKED_PAST | Polish | callers' offline coverage | PENDING |

The four PENDING Problems are kernel geometry. Lane 1 saw them first, on random bases. The builder's geometry check passes
because it reads only the 7 oracle scenes. Their bars prove at Stage 6, but each one fails its own oracle offline. I did not fix them in place: each is a planner change in
CordBuilder/CordPlanner whose smallest fix I could not name with confidence within this bound. Each item carries an acceptance
test (a lane-1 row) watched failing.

On the NOTED one: the sheet says "No hose, reel or pipe is drawn by this mod", but GSS draws FlowWorks pipe-pole spans by
design. The oracle (hose, reel) is sound and is what the verdict below rests on. The word "pipe" gets no verdict and goes to
the neutral fixer.

## Fixes
Both red first (`lane2/fixes.jsonl`). Parent 67ddc758e5 (replayed onto origin as 3105e794f7); fix commit **6d2aeb9c3f**:
- The no-hose scan now reads texture paths and `Class` attributes. New mutants M5 and M6 went rc 1 against the old scanner and
  rc 0 after.
- `RM_FallenWireShock`: the overhead-lines master gates only GSS's own fallen spans. FlowWorks' dropped deck cords now bite and
  light fuel with it off. New test `selftest_gss_dropped_cords_ignore_aerial_master.py`: rc 1 on the parent, rc 0 on the fix.
  It is a source binding, because the code is Verse-bound. The live proof (sc_shock_reach with overhead lines off) is
  **UNRUN**; command: the scene `scene_shock_reach` in `src/RimMandrake/GimmeSomeSlack/validation.py`.
- The DLL was rebuilt (`winbuild.py GimmeSomeSlack`, 0 errors) and committed with its `.srchash`. It was not deployed.
- The touched tests plus the shock bindings and the settings sweep: `run_selftests.py --only` 6/6 GREEN.
- `code_review_status.py check`: all three changed files read DIRTY. They need a full-file review, which this run did not do.

## Tests edited
`tests_edited.json`: `northstar/selftest_gss_no_hose.py` was extended, not weakened. Every earlier check and mutant is
kept; it now also scans folders and Class attributes. `selftest_gss_dropped_cords_ignore_aerial_master.py` is new. No assertion
was removed, skipped or loosened. No bar, criterion, locked file or `test_table.json` field was edited.

## Unsettled
- 14 lane-1 rows are `not_kernel`, with reasons in the rows. Those bars live in game code and are owed to Stage 6.
- Whether FloorEndShock can drop a live end when two end tips share one cell (its contact map is keyed by cell) is a guess
  [guess ~20% that it happens]. It was not measured and not filed.
- The second fix has no live run.

## Exit
```
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 1
exit_met: false
```
Read from the files at ffe1a381b8 (gss_last, 2026-11-15): both offline bars green (T_NO_HOSE PASS on the rerun after the fixes, `lane2/reruns_after_fix.jsonl`).
Of the eight Problems in `lane2/faults.json`, seven are FIXED, each red then green in `lane2/fixes.jsonl`. One is open:
RIMMANDRAKE_SWEEP_GSS_WALLED_RESIDUE_TWO_THOUSAND_SCENES. Over 2000 seeded scenes the bars' own oracles still read 115 unforced bends,
7 strands under 1.4, 7 edges with no full-cell stray and 6 twin pairs, and none of these is shown forced. Lane 1 after the fixes
(`lane2/lane1_rows_after_fix.jsonl`) has two FAIL rows, each owned by a Polish fault: L1_FALLEN_LAY_GROUND
(RIMMANDRAKE_LIFT_GSS_FALLEN_WIRE_OFF_WALL_CORNER) and L1_CORD_SHARP_TURN (RIMMANDRAKE_ALIGN_GSS_SHARP_ROW_READS_CUT_END_CELL, for
the Conductor). The exit is not met.

## Owed
- The four PENDING Problems (items above, each with its acceptance test).
- A full-file review of the three changed files, so they can be marked CLEAN.
- The live run of sc_shock_reach with the overhead-lines master off.
- The two kernels I did not read in full (CordBuilder 4427 lines, CordShape 1719) were reached only through their outputs.

Spend at the record: about $11.5 of the $20 bound [measured, the session's budget line]. Lane 1 landed ce294c48e1 (00:51 PST).

## Lane 2 follow-up (gss_four, 2026-11-15)
Judge the judge (`lane2/judge_the_judge/`): the four criteria are sound (feasibility_sweep.py: 2704 of 2704 chord x heading cells have one cord meeting slack,
stray and bends at once). Two lane-1 checks were wrong and were repaired (refusals.json): L1_CORD_EXCURSION read other nodes' cells as the conduit line,
L1_NO_REPEAT could never pass. Fix 0416599c69 (parent 0725d4522a), red then green in `lane2/fixes.jsonl`: slack, stray and repeat FIXED; bends 82 -> 4 on the
judge's 80 scenes, still open. Over 2000 seeded scenes, base -> fix: slack 243 -> 5 of 16740 strands, stray 31 -> 6 of 6070 edges, unforced bends
1580 -> 92, twins (3-6 cells) 468 -> 1 of 11200 pairs. T_CORE 4510/4510. Lane 1 after the fix: `lane2/lane1_rows_after_fix.jsonl` (FAIL: bends, the judge's
sharp-turn row, the fallen wire Polish).

## Lane 2 follow-up (gss_last, 2026-11-15)
- **Bends, the last 4.** Geometry first: `lane2/judge_the_judge/cut_end_sweep.py` (`cut_end_step30.txt`) tested every cut-lead cell, chord 1-12 x kept-run
  heading (the whole circle) x fitting heading x live/dead (both curl sides) x fitted/plug end. 5040 of 5040 cells meet bends, fold (past the kept run),
  slack, stray and two distinct shapes at once, so the criteria do not conflict. Ported as `CordBuilder.BlendCutRun` (6f8bfb47c4): the join where a cut end's
  kept run meets its faired cord is laid again as a Dubins path (R 0.66-1.0) leaving the kept run's own heading; the whole cord is relaid only on a lead of
  3 cells or less, which keeps equal runs apart. Unforced bends on lane 1's 80 scenes: 4 -> 0 (L1_CORD_BENDS_TALLY rc 1 at 7a9444f717, rc 0 at 6f8bfb47c4).
  Over 2000 scenes: 174 -> 115. The builder's ratchet is now 0. T_CORE 4510/4510, --geometry 4517/4517.
- **Two loop definitions.** The bar's words define no loop. Its oracle names CordShapeAudit.Bends, which counts a turn of 300+ degrees one way at a mean
  radius of 0.45+ as a loop, so that reading is the bar's. Lane 1's row also required the 1-cell window's own rate, and it now asks the instrument
  (28b3041500, refusal record CHECK_REPAIRED). The local reading was measured, not adopted: 55 unforced on the 80 scenes (1573 over 2000) with
  shaping unchanged. Making the shaping cut those loops cost slack (7 -> 22 strands under) and twins (6 -> 23). The row still fails on two other
  definition gaps (a cut end's first cell, a window of 21 samples), filed for the Conductor.
- **Walled residue.** Not fixed, and not proven forced. No exemption was written without a proof (Problem above).
- **Lay cost.** New `--lay-profile`: HopWhole no longer reads bends on a draw costlier than the best so far. The same draw still wins. A cold live-scene
  build went from 733 to about 690 ms. The cold build still plans over 71-78 Builds (the count is wall-clock, so it is noisy; the base was 57). The floor:
  bundle strands now hop and re-slacken (the S-hook fix), about 250 of the 690 ms. Getting back to 57 would undo that fix.
- **T_GATE.** The slice flake was not GC: a collection ran in about 42 of 75 Builds, and a 36.8 ms Build had none. The slice bound now has to hold on
  one of up to 3 fresh cold builds, the graph worker's own rule (`--slice-repeat`: old form 2 of 20 over 30 ms, new form 0 of 20). The gate was also
  red on every run from 6d2aeb9c3f on: O7 had pinned the shape that the UNGATE fix replaced. It is re-pinned (ffe1a381b8), and T_GATE now reads rc 0.
- The DLL was rebuilt at landing (8f1338a19a, with its .srchash) and not deployed. Live checks are UNRUN; the commands are the scenes in
  `src/RimMandrake/GimmeSomeSlack/validation.py` (Stage 6).

