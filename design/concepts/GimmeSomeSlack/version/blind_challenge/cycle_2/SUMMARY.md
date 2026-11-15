# GimmeSomeSlack 0.1.0 — blind challenge, cycle 2 (visit 2)

Resumed 2026-11-15 20:21Z by a second run after the first was killed (lane 1 committed by it at 922dfcddb3, kept as recorded).
Lane 2 ended 22:26Z [measured]. Spend of the resumed run about $7.5 of $20 [measured, the session budget line]; the killed run's spend is not visible here.

Judge: detached helper, item RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_TWO_TESTS_FIRST (seat BENCH).

## Start time
2026-11-15T18:33:52Z (UTC), before any input was opened.

## Changed files to bars
`git diff --name-only f5e310809f origin/main -- <the brief's paths> | grep -v /blind_challenge/`: 34 files (the brief's list).
Mapped by what each file is, before reading why it changed:

| changed file(s) | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_FallenWireShock.cs` | floor_end_shocks_crossers, floor_end_shock, fallen_wire_shocks_crossers, fallen_wire_shock, shock_reach_setting, live_wire_lights_fuel |
| `src/RimMandrake/GimmeSomeSlack/Source/Core/CordBuilder.cs`, `Core/CordSlacken.cs` | cords_lie_slack, cord_slack_lay, no_unforced_sharp_turn, cords_meet_walls_at_face, strip_at_every_junction, junction_strips, dense_block_tangle, cords_never_repeat, drawing_true_to_grid, connectivity_truth, cut_live_and_dead_ends, cords_draw_under_things, no_stall_on_rewire |
| `Assemblies/RimMandrakeGimmeSomeSlack.dll` (+ `.srchash`) | every game-side bar; and no_hose / no_hose_in_gss (the DLL ships, its type names are scanned) |
| `northstar/selftest_gss_no_hose.py` | no_hose, no_hose_in_gss (the offline decider) |
| `northstar/selftest_gss_cords_under_items.py` | cords_draw_under_things |
| `selftest_gss_dropped_cords_ignore_aerial_master.py` | shock_reach_setting, floor_end_shock, fallen_wire_shock |
| `Source/SelfTest/{CordGeometryChecks,Program,SliceGateChecks}.cs`, `Utils/selftest_gimmesomeslack.py`, `validation.py` | the cord-geometry bars above; no_stall_on_rewire, rebuild_cost (slice gate) |
| `scenes.json` (locked): one new scene `sc_cords_under_items` | cords_draw_under_things |
| `tree.json` (locked): only the `coverage` signature block; no leaf line changed | none |
| `version/*` (VERSION.json, bars.md, locked_bars.json, test_table.*, preflight*, stage_record.json, run_spend.jsonl, make_test_table.py), `record.json`, `stage.json`, `exam.json`, `coverage_verdict.json`, `journal.md`, `park_summary.md`, `result.bench-gss-owed-exam-st*.json` | records of the stage, not bar inputs; test_table.* is the decider map (read in lane 2) |

Lane-1 scope: the two offline bars (no_hose, no_hose_in_gss) in full; then the AerialMath kernel's stage-6 bars (spans,
downed spans, shock, re-string, theft, gravship, the pipe-pole switch); the cord-lay and shock-reach bars the changed
files touch are game-side (`not_kernel` rows) and go to lane 2's code read.

## Lane 1
Recorded at 2026-11-15T18:43Z, before anything sealed was opened. `lane1/run_lane1.py` (kernel tests `lane1/BlindLane1.cs`
compiled with `src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs`, plus `lane1/blind_no_hose.py`), rows in
`lane1/lane1_rows.jsonl`: **48 rows: 30 PASS, 2 FAIL, 2 INFO, 14 UNSETTLED** [measured].

- Offline bars: `L1_NOHOSE_LIVE_SCAN` PASS: no def, texture, type or texture-path literal for a hose or reel in what
  ships (About, Defs, Patches, Textures, Assemblies, and every C# file the csproj compiles, `_Shared` included). 11 controls
  PASS: each planted kind (def, patch-added def, thingClass, texture file, texture folder alone, C# class, C# texture path,
  a stale DLL holding a hose type) is caught, decoys (whose/choose/Wheel) are not, 40 of 40 seeded random plants caught.
- INFO `L1_NOHOSE_HOSE_NAMED_MEMBERS`: the DLL carries hose-named MEMBERS from the shared geometry it compiles in
  (`_Shared/SlackGeometry/DrawOrder.cs` LayerHose/HoseQueue/..., `CordLayer.cs` `CordKind.Hose`, `LayParams.Hose()`) and a
  settings-migration name `FireHosesMod`; `L1_NOHOSE_GSS_NEVER_SELECTS_HOSE_LAY` PASS: GSS's own code never selects them.
- INFO `L1_NOHOSE_PIPE_WORDS`: the sheet line says "No hose, reel or pipe is drawn by this mod", but the kernel carries
  `AerialLineKind.Pipe` (FlowWorks pipe poles: one stiff strand, sag 0.02, span 12). Whether GSS draws a pipe is a
  game-side read: lane 2.
- FAIL `L1_DOWNED_LAY_ON_GROUND_RANDOM` (seed 4202): 13 of 1500 fallen wires lie on the ground over 2x their cable + 2
  cells, e.g. a 5.66-cell cable grounded over 14.27 cells (2.52x) falling up-left; shrunk: still over at a 5.16-cell span.
- FAIL `L1_RESTRING_TICKS_SWEEP`: `RestringTicks(NaN)` returns int.MinValue (300 at speed 1, monotone, >= 1 elsewhere).
- 14 UNSETTLED `not_kernel` rows: game-side bars owed to Stage 6 (none names an offline bar).

## Lane 2 reruns
`lane2/rerun_offline.py` (every `kind: offline` test of `version/test_table.json`, recorded 2026-11-14): **27 rerun, 22 match, 23
same verdict, 23 PASS** [measured] (`lane2/reruns.jsonl`). The decider of both offline bars, `T_NO_HOSE`, PASS and matching.
- `T_STATICS_CENSUS` FAIL (recorded PASS): `Core/CordBuilder.cs::StepTrace`, a static delegate added 2026-11-15, neither reset nor listed.
- `T_CORE` (and `T_SHOCK_RULE_OFFLINE`, its `via`) FAIL 4509/4510: the graph-worker fault check; red 3 of 3 full runs, green 2 of 2
  `--perdig-only` runs. `T_GATE` FAIL only through its O3 (= `T_CORE`).
- `T_CORD_GEOMETRY_OFFLINE` PASS (the brief listed it red or unrun; it passed 4524/4524) with a longer last line than recorded.
After the fixes (`lane2/reruns_after_fix.jsonl`, at 349f9aa86b): `T_NO_HOSE`, `T_STATICS_CENSUS`, `T_CORE`, `T_SHOCK_RULE_OFFLINE`,
`T_GATE`, `T_CORD_GEOMETRY_OFFLINE` **6 of 6 PASS**; four differ from the recorded last line only by check counts the builder added
after 2026-11-14 (4508 -> 4510, 4515 -> 4520).

## Planted
`lane2/planted_faults.json` (made by `lane2/make_planted_faults.py`), run by `lane2/plant_faults.py` with
`WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c2_mut`: **36 planted, 19 caught; 20 with the pipe
plant re-run after its fix** (`lane2/planted_after_fix.jsonl`) [measured]. Baseline row first, `tree_clean_after: true` last
(`git diff --quiet` 0). A later row for the same fault (a wider `--suites` run) replaces the earlier one.
- Offline bars' kernel (what ships, and the scan): 6 planted (hose def, reel texture folder, hose class, pipe def, two scan
  blindings); 5 caught; the pipe def MISSED -> Problem (below), caught after the fix.
- Game-side callers and patches: 10 (RM_FallenWireShock x4, GssSessionReset x2, the pipe switch default, pipe kind under the power
  master, pipe strand cap, re-string speed floor): 7 caught. MISSED: `PIPE_SWITCH_DEFAULT_OFF` (Verse-side default before
  FlowWorks registers: game-side, Stage 6), `AM_RESTRING_SPEED_FLOOR` (no decider claims re-string speed; lane 1's sweep checks
  monotone and >= 1 only), and `AM_PIPE_TWO_STRANDS` missed by lane 1 and binding but caught by `T_CORE`.
- FW_STALE_SPAN_BITES keeps the source text `kind == LineKind.DownedSpan && !AerialSettings.enabled` and changes behaviour: the
  source-reading `selftest_gss_dropped_cords_ignore_aerial_master.py` and validation's C2 shape both stay green on it; the compiled
  binding tests (`T_SHOCK_*_BINDING`) catch it. Not a Problem: a behaviour decider catches it.
- Changed files, two each: CordBuilder x3, CordSlacken x3, CordGeometryChecks x2, Program x2, SliceGateChecks x2, the wrapper
  `selftest_gimmesomeslack.py` x2, validation x2, cords_under_items x2, no_hose x2 (above), dropped_cords x2, RM_FallenWireShock (above).
  Records and JSON files (`*.json`, `journal.md`, `version/*`) and the DLL are not code: no plant.
- MISSED and not Problems: ten pure test weakenings with no self-control (CGC_PLANT_CONTROL_SKIPPED, VAL_C2_SHAPE_BLIND,
  CU_ONE_ENTRY_UNCHECKED, CU_CONTRACT_SKIPPED, DC_C4_ALWAYS_TRUE, SGC_CALLER_REDUCE_UNCHECKED, SGC_HANDOFF_BUDGET_x100,
  PROG_FUZZ_SKIPPED, WRAP_RC_SWALLOWED, and the two geometry skips, Polish below); three cord-lay guards (CB_TAUT_FAULT_HALVED,
  CB_BEND_ALLOWANCE, CS_FLAT_LONG_EDGE) MISSED by the full `--geometry` run. A firing probe (`--geometry-only`, temporary prints,
  restored): the taut guard never fires in the band the plant changes (0 times); the bend guard 20 times and the flat guard 71
  times while the outputs still read 0 unforced bends and 0 flat long edges, so the bar holds [measured]; that a later stage
  masks them is [guess ~65%]. Polish, below.

## Faults
`lane2/faults.json`, 9 refusal records [measured]: **3 Problems (all FIXED red first), 6 Polish (2 NOTED_FOR_CONDUCTOR, 4 PENDING);
miss_of 1: 4** (the no-hose pipe scan, the pipe wording, re-string NaN, fallen-wire length).
- Problem `RIMMANDRAKE_RESET_GSS_STEPTRACE_STATIC_CENSUS_CAUGHT_IT` (statics_clear_between_games): FIXED 164931fd94. miss_of 0.
- Problem `RIMMANDRAKE_WIDEN_GSS_FAULT_GUARD_LAY_NEEDED_SIXTY_THREE` (T_CORE): FIXED 164931fd94. miss_of 0: with the cap
  lifted the Builds end bit-identical at 63; the 2026-11-15 cord-builder work grew the live scene's async lay past a loop guard of 60.
- Problem `RIMMANDRAKE_WIDEN_GSS_NO_HOSE_SCAN_PIPE_PLANT_PASSED` (no_hose, no_hose_in_gss): FIXED 349f9aa86b. miss_of 1 (the
  scan's word list is unchanged since 2026-11-12).
- Polish NOTED `RIMMANDRAKE_REWORD_GSS_NO_PIPE_BAR_POLES_ON_PURPOSE`: the leaf says "No hose, reel or pipe is drawn by this mod",
  while GSS's line engine draws FlowWorks' pipe-pole spans by design (pipe_pole_switch). For the neutral fixer.
- Polish NOTED `RIMMANDRAKE_REPIN_GSS_ASYNC_FAULT_CAP_FIFTY_SEVEN_USED`: SliceGateChecks (5) asserts `builds5 < 60` while the
  async lay takes about 57 Builds; an assertion bound only the steward may re-pin.
- Polish `RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME` (lane-1 row L1_RESTRING_TICKS_SWEEP), Polish
  `RIMMANDRAKE_TRIM_GSS_FALLEN_WIRE_COILS_OUTGROW_CABLE` (lane-1 row L1_DOWNED_LAY_ON_GROUND_RANDOM), Polish
  `RIMMANDRAKE_PROVE_GSS_GEOMETRY_RAN_COUNT_IS_ONLY_TELL`, Polish `RIMMANDRAKE_EXERCISE_GSS_CORD_GUARDS_THREE_PLANTS_SURVIVE`.
Every fault is a rimflow item (seat BENCH); the three Problems are closed at their shas.

## Fixes
`lane2/fixes.jsonl`, red first, each red run for real at the fix's parent (a `git archive` of it) and on 8d03656883:
- 164931fd94: `GssSessionReset` clears `Core.CordBuilder.StepTrace`; census RESET row; GraphWorker (2) guard 60 -> 600 Builds,
  120 s bound and the assertion kept; DLL rebuilt (`winbuild.py`, private root). Red rc 1 / rc 1, green rc 0 / rc 0.
- 349f9aa86b: `T_NO_HOSE` scans `hose|reel|pipe`, mutant M7. Red: `lane2/check_pipe_plant.py 851090817` rc 1 (0 of 3 pipe
  plants); green: the same at 349f9aa86b rc 0 (3 of 3) and `T_NO_HOSE` rc 0.
Lane 1 rerun after the fixes: `lane2/lane1_rows_after_fix.jsonl`, 30 PASS, 2 FAIL, 2 INFO, 14 UNSETTLED [measured]: the two FAIL
rows are the two Polish faults that name them (Polish is not part of passing). The edited files read DIRTY on
`code_review_status.py` (all three were DIRTY before this cycle); no full-file review was done, none was marked clean.

## Steward's decisions enacted
None written for this cycle; the standing default was followed: every bar judged as locked, Problems fixed in place red first,
the two wrong criteria written up as NOTED_FOR_CONDUCTOR. No `--per-ruling` event was needed.

## Tests edited
`tests_edited.json`: `selftest_gss_statics_census.py` (a RESET row added), `Source/SelfTest/SliceGateChecks.cs` (a loop guard,
not an assertion), `northstar/selftest_gss_no_hose.py` (pipe added, mutant M7). No assertion weakened, skipped or deleted.

## Unsettled
- 14 lane-1 `not_kernel` rows, every one naming stage-6 bars only: owed to Stage 6.
- Whether the bend and flat cord guards are redundant or only unexercised [guess ~65% redundant]; a digest comparison would settle it.
- `PIPE_SWITCH_DEFAULT_OFF`: the pipe switch's default before FlowWorks registers is a Verse-side read (Stage 6).
- The no-hose bar's word "pipe" (NOTED): the code's verdict stands on what GSS ships, not on what its engine draws for FlowWorks.

## Exit
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 0
exit_met: true

## Owed
- `maturation.py next GimmeSomeSlack` (2026-11-15 22:30Z) passes every file check above and reads the exit as not met for one
  reason: "a new blind judge is owed: 3 Problem(s) were FIXED in this cycle ... a fixed mod goes back to a new blind judgement
  pass (advance --to blind_challenge opens cycle 3)". The block above follows the brief's definition (a Problem FIXED red first is
  closed); the road back is the Conductor's call. This judge ran one cycle and did not advance.
- Conductor: the two NOTED Polish items (pipe wording for the neutral fixer; the `builds5 < 60` bound to re-pin).
- The four PENDING Polish items, on the mod's Polish list, each with its acceptance test in its item or record.
- The DLL at 164931fd94 is built, committed with its `.srchash`, and not deployed (offline stage).
- A full-file review of the three edited files before any is marked clean.
