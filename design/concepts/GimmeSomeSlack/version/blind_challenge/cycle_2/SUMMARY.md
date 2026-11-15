# GimmeSomeSlack 0.1.0 — blind challenge, cycle 2 (visit 2)

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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
