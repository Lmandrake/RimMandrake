# GimmeSomeSlack 0.1.0 — blind challenge, cycle 3

## Start time
2026-11-15T22:39:41Z (UTC), before any input was opened.

## Changed files to bars
`git diff --name-only 7dc9069b89 origin/main` over the brief's paths, `/blind_challenge/` excluded: 11 files [measured]. Mapped by
file name and role only (lane 1 did not read the diffs):

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/GimmeSomeSlack/Source/Core/CordBuilder.cs` | the floor-cord leaves: cords_lie_slack, no_unforced_sharp_turn, cords_meet_walls_at_face, strip_at_every_junction, dense_block_tangle, cords_never_repeat, drawing_true_to_grid, cut_live_and_dead_ends, floor_end_shocks_crossers (live end cells), no_stall_on_rewire; rows cord_slack_lay, junction_strips, connectivity_truth, break_ends_live_dead, floor_end_shock, rebuild_cost |
| `src/RimMandrake/GimmeSomeSlack/Source/GssSessionReset.cs` | statics_clear_between_games, game_statics_reset |
| `src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll` (+ `.srchash`) | every C#-decided bar; for the offline bars, the shipped DLL scan (no_hose, no_hose_in_gss) |
| `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/CordGeometryChecks.cs` | test of the CordBuilder leaves (T_CORD_GEOMETRY_OFFLINE, read in lane 2) |
| `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/SliceGateChecks.cs` | no_stall_on_rewire, rebuild_cost (a test) |
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` | **no_hose, no_hose_in_gss: the decider of both offline bars** |
| `src/RimMandrake/GimmeSomeSlack/selftest_gss_statics_census.py` | statics_clear_between_games, game_statics_reset (a test) |
| `design/concepts/GimmeSomeSlack/journal.md`, `version/run_spend.jsonl`, `version/stage_record.json` | records, no bar (journal opened only in lane 2) |

No locked file (`tree.json`, `sheet.md`, `scenes.json`) changed [measured: absent from the list]. Lane-1 scope: both offline bars
(their decider changed), and the aerial kernel's stage-6 bars (unchanged kernel, read once per "all once" since this judge is new).

## Lane 1
Landed before anything sealed was opened. Inputs: `tree.json`, `sheet.md`, `plan.md`, `version/VERSION.json`, `version/bars.md`,
the `record.json` rows `no_hose` and `pipe_pole_switch`, `AerialSettings.cs` (defaults, slider ranges), the kernel
`Source/Aerial/AerialMath.cs`, file names under `Defs/` `Patches/` `Textures/` `Source/`. Files: `lane1/BlindLane1.cs`
(kernel rows, plus a metadata dump of the shipped DLL), `lane1/BlindNoHose.py` (the offline-bar scan), `lane1/run_lane1.py`
(one command; `--kernel`, `--root`, `--dll` for planted faults).

**62 rows: 28 PASS, 3 FAIL, 4 INFO, 27 UNSETTLED** [measured, `lane1/lane1_rows.jsonl`].

- Offline bars `no_hose` / `no_hose_in_gss`: 9 decided rows, all PASS: defs (every element and value, not only defName),
  patches, texture files and folders, shipped C# type names and texture literals, the shipped DLL's 489 type names and 1697
  user strings, and a sanity probe proving the scan goes red on a planted hose def, a `Hoses/` texture folder, a
  `HoseReelDrawer` class and a pipe texture literal. Two INFO rows: the mast description's "scrap pipe" is prose; and the
  kernel has `AerialLineKind.Pipe`, so GSS lays FlowWorks pipe-pole spans: whether GSS *draws* a pipe is a lane-2 read.
- Kernel rows (aerial lines, theft, blasts, strands, sway, removal plans): links, auto-link, spanning links, sag depth,
  drip switch, strands, sway, removal-plan conservation, watchdog, shock table, knockback, blast kinds and falloff, tap
  conservation over 1-4 taps, sighting, goodwill drain conservation, the pipe pole's own switch, clamps, re-string time: PASS.
- FAIL `L1_SPAN_VISIBLE_SAG_EVERY_BEARING`: the span droop is screen -Z only, so a north-south span draws on its chord, a
  ruler-straight wire (124 of 2000 random spans at the default sag show under 0.1 cell; shrunk: (0,0)->(0,8), 0.000).
- FAIL `L1_FALLEN_ON_GROUND_NOT_WALLS`: a fallen wire's grounded point lies on a wall cell (shrunk to one wall (9,0),
  base (0.5,0.5), toward (10.34,1.03), seed 512077717): the wander crosses the wall corner.
- FAIL `L1_FALLEN_STRANDS_EACH_ITS_OWN`: two of three fallen wires end 0.045 cell apart (seed 8081 case 554). My first
  threshold was 0.2 cell, a number the bar does not hold; the recorded one is 0.05 ("one point").
- Test bugs fixed before recording (my own): the first sag check projected points onto a slanted chord; the sag depth
  tolerance did not allow for the half-cell sampling.
- 27 UNSETTLED: 25 `not_kernel` rows (one per game-side leaf) and two kernel halves owed to callers (the re-string
  exemption keyed on the span; theft stopping on removal).

## Lane 2 reruns
Before the fixes (`lane2/reruns.jsonl`, recorded commands, private WINBUILD_ROOT): **25 of 25 verdicts match** the
recorded `runs_today` [measured]; 21 also match on the last line. The 4 last-line differences are where the recorded line came from
(stderr, a warning) or a check count that grew since 2026-11-14 (`T_CORD_GEOMETRY_OFFLINE` 4515 -> 4522), never a verdict.
The offline bars' decider `T_NO_HOSE` reran PASS. `T_CORD_GEOMETRY_OFFLINE` (recorded with `known_red`) reran PASS.
`T_GATE` was rerun after the fixes only. After the fixes (`lane2/reruns_after_fix.jsonl`): **11 of 11 PASS as recorded**
(T_NO_HOSE, T_CORE, T_SHOCK_RULE_OFFLINE, T_CORD_GEOMETRY_OFFLINE, T_GATE, T_H_PROOF_ALL, T_STATICS_CENSUS and four helpers).
Every one of the 27 offline tests in `test_table.json` was rerun at least once [measured: 0 not rerun].

## Planted
`lane2/planted_faults.json` (21 faults), `lane2/plant_faults.py`, results `lane2/planted_results.jsonl` (baseline first,
`tree_clean_after: true` last). **16 of 21 caught** by a new failing row [measured]:

| fault | where | caught by | |
|---|---|---|---|
| `NH_TEX_FILE_PIPESPAN` | `PipeSpan.png` | NOHOSE, LANE1 | |
| `NH_DEF_TEXPATH_FLOWWORKS_PIPE` | `MapMeshFlagDefs.xml` | NOHOSE, LANE1 | |
| `NH_DEF_LABEL_HOSE_REEL` | `MapMeshFlagDefs.xml` | **nothing** | |
| `NH_CALLER_HOSE_TEXTURE_LITERAL` | `AerialMaterials.cs` | LANE1 | |
| `NH_CALLER_PIPEMATS_OWN_ART` | `AerialMaterials.cs` | **nothing** | |
| `NH_CALLER_HOSE_TYPE` | `CordMaterials.cs` | NOHOSE, LANE1 | |
| `K_CANLINK_NO_RANGE` | `AerialMath.cs` | LANE1, CORE | |
| `K_TAP_NO_AVAIL_CAP` | `AerialMath.cs` | LANE1, CORE | |
| `K_GOODWILL_REMAINDER_LOST` | `AerialMath.cs` | LANE1 | |
| `K_SHOCK_FIXER_NOT_EXEMPT` | `AerialMath.cs` | LANE1, CORE | |
| `K_REMOVAL_CUT_FALLS_AGAIN` | `AerialMath.cs` | LANE1, CORE | |
| `K_PIPE_POLE_HOSTAGE_TO_MASTER` | `AerialMath.cs` | LANE1, CORE | |
| `K_THEFT_SIGHT_DOUBLED` | `AerialMath.cs` | LANE1, CORE | |
| `C_TWIN_APART_ZERO` | `CordBuilder.cs` | GEOM | |
| `C_TWIN_PICKS_CLOSER` | `CordBuilder.cs` | GEOM | |
| `C_STRANDFAULTS_OVERFACE_ZERO` | `CordBuilder.cs` | **nothing** | |
| `C_TWIN_MAY_ADD_FAULTS` | `CordBuilder.cs` | **nothing** | |
| `C_GRAPH_FAULT_LEAVES_RUNNING` | `CordBuilder.cs` | CORE | |
| `C_GRAPH_FAULT_FORGOTTEN` | `CordBuilder.cs` | CORE | |
| `R_STEPTRACE_RESET_DROPPED` | `GssSessionReset.cs` | CENSUS | |
| `R_RESET_RETURNS_EARLY` | `GssSessionReset.cs` | **nothing** | |

Suites: NOHOSE = `T_NO_HOSE`; LANE1 = my lane 1; CORE = `T_CORE`; GEOM = `--geometry-only` (the geometry half of
`T_CORD_GEOMETRY_OFFLINE`); CENSUS = `T_STATICS_CENSUS`. Four per offline bar (six NH faults), seven in the aerial kernel and
four in game-side callers (`AerialMaterials.cs`, `CordMaterials.cs`), and two in each changed code file (CordBuilder.cs six,
GssSessionReset.cs two). For changed test files the two are aimed at their new checks; records and the binary have none
(reasons in `planted_faults.json`, `not_planted`).
The survivors that showed a test gap became the four Problems below. `NH_DEF_LABEL_HOSE_REEL` and
`NH_CALLER_PIPEMATS_OWN_ART` also passed my own lane 1 (its prose rule and full-literal rule).
`C_TWIN_MAY_ADD_FAULTS` and `C_STRANDFAULTS_OVERFACE_ZERO` drew no defect on any test input: Polish, below.

## Faults
`lane2/faults.json`, each filed as a rimflow item. **4 Problems** (all FIXED, 1 `miss_of: 2`), **6 Polish** (all NOTED_FOR_CONDUCTOR, 4 `miss_of: 2`) [measured]:

- `RIMMANDRAKE_WIDEN_NO_HOSE_SCAN_CODE_PATHS_UNSEEN` (Problem, FIXED): T_NO_HOSE (sole decider) must see any hose, reel or pipe GSS ships or draws (tree oracle: 'no ThingDef, texture or class for hoses or reels'; sheet: '
- `RIMMANDRAKE_WIDEN_NO_HOSE_SCAN_LABELLED_REEL_SLIPS` (Problem, FIXED): as above: a ThingDef for a hose reel is refused whatever its defName
- `RIMMANDRAKE_RUN_GSS_TWIN_CHECK_IN_ITS_OWN_DECIDER` (Problem, FIXED): an offline decider of cords_never_repeat (test_table: T_CORE, sc_no_repeat) must go red when the twin pass that keeps equal leads apart is broken
- `RIMMANDRAKE_CARRY_GSS_GOODWILL_REMAINDER_TEST_DIVIDES_DAY` (Problem, FIXED, miss_of 2): goodwill drains steadily: perDay for each whole day drained, the remainder carried (AerialMath.TheftGoodwillAccrue's own contract); T_CORE decides the
- `RIMMANDRAKE_NOTE_GSS_NORTH_SOUTH_SPAN_RULER_STRAIGHT` (Polish, NOTED_FOR_CONDUCTOR, miss_of 2): 'It must not read as ... a ruler-straight wire'; scene sc_spans expects 'sag above zero'
- `RIMMANDRAKE_NOTE_GSS_FALLEN_WIRE_GRAZES_WALL_CORNER` (Polish, NOTED_FOR_CONDUCTOR, miss_of 2): a fallen wire lies on the ground
- `RIMMANDRAKE_NOTE_GSS_FALLEN_TIPS_NEARLY_MEET_RARELY` (Polish, NOTED_FOR_CONDUCTOR, miss_of 2): three wires fall as three (owner round 3, 2026-10-04); the kernel's doc: tips FallenSpread (1.15) apart
- `RIMMANDRAKE_NOTE_GSS_STATICS_CENSUS_READS_TEXT_ONLY` (Polish, NOTED_FOR_CONDUCTOR): the census supports (does not decide) the bars; sc_statics_new_game decides at Stage 6
- `RIMMANDRAKE_NOTE_GSS_PIPE_SPANS_DRAWN_BY_GSS_CODE` (Polish, NOTED_FOR_CONDUCTOR, miss_of 2): sheet: 'No hose, reel or pipe is drawn by this mod'; record no_hose: 'GSS draws no hose or pipe'
- `RIMMANDRAKE_NOTE_GSS_TWIN_GUARD_NEVER_EXERCISED` (Polish, NOTED_FOR_CONDUCTOR): a twin must not add a fault (CordBuilder: StrandFaults(twin) <= own)

The three lane-1 FAILs are Polish, each fault naming its row: `L1_SPAN_VISIBLE_SAG_EVERY_BEARING` ->
`RIMMANDRAKE_NOTE_GSS_NORTH_SOUTH_SPAN_RULER_STRAIGHT`, `L1_FALLEN_ON_GROUND_NOT_WALLS` ->
`RIMMANDRAKE_NOTE_GSS_FALLEN_WIRE_GRAZES_WALL_CORNER`, `L1_FALLEN_STRANDS_EACH_ITS_OWN` ->
`RIMMANDRAKE_NOTE_GSS_FALLEN_TIPS_NEARLY_MEET_RARELY`.

## Fixes
All four in `9126ead2a4`, test-only; no mod code changed, no assertion weakened. Red at `8e6c67eba7`, green at
`9126ead2a4`, each command run for real at both (`lane2/fixes.jsonl`):

- `check_nohose_catches.py --rev <sha>`: 0 of 3 caught, rc 1 -> 3 of 3, rc 0 (the two T_NO_HOSE Problems).
- `check_core_catches_twins.py`: T_CORE 0 of 2 twin-pass faults, rc 1 -> 2 of 2, rc 0.
- `check_core_catches.py --only K_GOODWILL_REMAINDER_LOST --match theft:`: 0 of 1, rc 1 -> 1 of 1, rc 0.

`T_CORE` 4514/4514 and `T_NO_HOSE` 14/14 green on the fix; `run_selftests.py --only` both GREEN. After the fixes lane 1 was
rerun into `lane2/lane1_rows_after_fix.jsonl`: the same 28 PASS / 3 FAIL (the kernel did not change; the 3 are Polish).

## Steward's decisions enacted
None: the brief carries no Conductor decision for this cycle. The standing default was followed (bars judged as locked, Problems fixed red first, wording questions NOTED).

## Tests edited
`tests_edited.json`: `northstar/selftest_gss_no_hose.py`, `Source/SelfTest/Program.cs`, `Source/SelfTest/CordGeometryChecks.cs`, `Source/SelfTest/TheftChecks.cs`. Each one strengthened; none weakened; before/after hashes at `8e6c67eba7` / `9126ead2a4`. `code_review_status.py check`: all four DIRTY (never or not since reviewed; not marked clean by me).

## Unsettled
- 27 lane-1 rows UNSETTLED, all owed to Stage 6: 25 `not_kernel` rows, one per game-side leaf, and two kernel halves owed to callers
  (the re-string exemption keyed on the span; theft stopping on removal). None names an offline bar.
- NOTED for the Conductor: sc_spans' "sag above zero" on a north-south span; the sheet's "no pipe is drawn by this mod" against
  the approved pipe-pole spans GSS draws with FlowWorks' art.
- The DLL is not rebuilt by me: the fixes touch the SelfTest project and a Python test only (the shipped DLL and its .srchash unchanged).

## Exit
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 0
exit_met: false

exit_met is false because this cycle FIXED four Problems: by the brief, a cycle's own fixes never pass its exit, so a new blind judge is owed.

## Owed
- A new blind judge (cycle 4 is the Conductor's call: this was cycle 3 of 3 in the visit).
- The six Polish items to the Conductor (polish list; two of them are wording for the steward or the neutral fixer).
- A review of the four edited tests (DIRTY).
