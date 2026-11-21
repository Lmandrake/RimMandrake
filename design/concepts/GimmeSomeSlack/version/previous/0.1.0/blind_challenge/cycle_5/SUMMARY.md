# GimmeSomeSlack 0.1.0, blind challenge cycle 5

Judge: detached BENCH helper on RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_FIVE_FROM_PACKET (holder run-1794814806, role blind_judge).

## Start time
2026-11-16T07:40:43Z (11:40 PM PST 2026-11-15), before any mod file was opened.

Blindness note: this run started from the mod-ledger packet, which lists the mod's open findings by earlier cycles
(titles, evidence lines, proposed fixes). The judge therefore was NOT blind to earlier findings. Recorded as a pipeline
defect (see Owed / Faults).

## Changed files to bars
`git diff --name-only 47882f8c22 origin/main` (brief's command) at 863ca5c461 lists 11 files [measured]:

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` | `no_hose`, `no_hose_in_gss` (their decider T_NO_HOSE) |
| `design/concepts/GimmeSomeSlack/version/test_table.json` | read in lane 2: only `runs_today` refreshes and a `known_red_cleared` note on T_CORD_GEOMETRY_OFFLINE changed; no bar, `decides` or `proves_at` moved [measured] |
| `version/stage_record.json`, `version/run_spend.jsonl`, `journal.md`, `ledger/*.jsonl`, `ledger/views/*` | records only: no bar input |

No locked file (`tree.json`, `sheet.md`, `scenes.json`, `plan.md`, `record.json`, `VERSION.json`, `bars.md`) changed.
Lane-1 scope: the two offline bars, then the kernel `AerialMath.cs` for stage-6 bars whose logic lives there.

## Lane 1
Written from tree.json, sheet.md, record.json (the no_hose row), VERSION.json, bars.md, AerialSettings.cs (defaults,
slider ranges), Defs/, Patches/ and the kernel AerialMath.cs; nothing sealed opened. Command:
`python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_5/lane1/run_lane1.py` (rc 1).

70 rows [measured]: 21 PASS, 7 FAIL, 3 INFO, 39 UNSETTLED (39 `not_kernel`, every one a stage-6+ bar).

FAIL rows:
- `NH_SOURCE_NO_TEXT_SAYING_GSS_DRAWS_PIPES` (no_hose, no_hose_in_gss): the Mod Settings header,
  `GimmeSomeSlackMod.Header` = "Drawn flexible pipes and wires to better display simple circuit-like plans underneath."
- `NH_SHIPPED_DLL_NO_HOSE_SYMBOL` (no_hose, no_hose_in_gss): the shipped DLL holds `HoseBaseLift`, `HoseFittingLift`,
  `HoseQueue`, `HoseTopAltitude`, `LayerHose` (from the shared `_Shared/SlackGeometry/DrawOrder.cs` compiled in; no GSS
  caller found by grep).
- `L1_SPAN_VISIBLE_OFF_CHORD_EVERY_BEARING` (spans_above_everything): 104 of 2000 random spans at sag 0.06 leave their chord
  by under 0.1 cell; shrunk to a north-south span, drawn exactly on its chord.
- `L1_RESTRING_TICKS_SWEEP` (restring_cut_span): `RestringTicks(NaN)` = -2147483648, `RestringTicks(+inf)` = 0.
- `L1_FALLEN_ON_GROUND_NOT_IN_WALLS` (fallen_span_on_ground): 7 of 2500 fallen wires put a grounded point inside a wall cell
  (deepest 0.139 cell), Blocked false.
- `L1_FALLEN_LENGTH_NOTHING_CREATED` (fallen_span_on_ground): 7 of 2500 draw over 2 x cable + 2 cells on the ground
  (13.9 cells for a 5.6-cell cable).
- `L1_FALLEN_STRANDS_EACH_ITS_OWN` (fallen_span_on_ground): 32 tip pairs under 0.25 cell apart in 1000 spans (closest 0.066).

INFO: `NH_PIPE_POLE_SPANS_DRAWN_BY_GSS_CODE` (GSS code draws FlowWorks' overhead pipe-pole spans: the sheet's "no ... pipe
is drawn by this mod" and the record's `pipe_pole_switch` bar disagree), `NH_DEFS_PROSE_MENTIONS`, `L1_SPAN_SAG_SLIDER_ZERO_IS_STRAIGHT`.

Blindness, stated plainly: the run's packet named earlier cycles' open findings, several of which (restring NaN, fallen wire
in walls / coils, tips meeting, north-south span, pipe-pole wording) overlap these rows. The rows were written from the bars
and measured here, but they are not independent of that knowledge.

## Lane 2 reruns
`lane2/rerun_offline.py` reran all 27 offline tests of `test_table.json` with their recorded commands (private
`WINBUILD_ROOT`) [measured]: **27 of 27 same verdict (PASS), 26 of 27 same last line**; T_GATE's last line differs only in
its `wall_s` timings. T_NO_HOSE (sole decider of both offline bars): PASS, matching. After the fix,
`lane2/reruns_after_fix.jsonl`: the 23 short offline tests again 23 of 23, T_NO_HOSE 25 PASS rows (rc 0).

## Planted
`lane2/planted_faults.json` (20 faults), `lane2/plant_faults.py`, `lane2/planted_results.jsonl` (baseline first,
`tree_clean_after: true` last) [measured]:
- **Before this cycle's fixes: 7 of 19 caught.** Caught: NH_ANCHOR_TEXPATH_HOSE, the two faults in the changed decider
  (NHT_PROSE_TAKES_LABEL, NHT_WORD_DROPS_PIPE), and all four kernel faults (K_GOODWILL_REMAINDER_LOST, K_INRANGE_STRICT,
  K_CUT_SPANS_FALL_AGAIN by T_CORE and lane 1; K_SHOCKRULE_FLOOR_BITES_UNDER_DOWNED by T_CORE).
- Missed: NH_VERSION_FOLDER_HOSE_DEF, NH_EXTRA_ASSEMBLY_HOSE_DLL, NH_JOINED_PATH_LITERAL, NH_HEADER_SAYS_HOSES (the Problem
  below); TT_NO_HOSE_COMMAND_TRUE and TT_NO_HOSE_BAR_DECIDES_NOTHING (the pipeline certificate, below); six caller/patch faults
  every offline suite missed (C_FALLEN_SHOCK_EXTERNAL_GATED, C_FLOOR_DEAD_END_BITES, C_FLOOR_ANY_BUILDER_EXEMPT,
  C_TAP_OWN_NET_STEALS, C_RESTRING_IGNORES_SPEED, C_PATCH_SWITCH_XPATH_TYPO: Verse-bound or patch-level, their bars prove at
  stage 6).
- **After the fixes: 12 of 19 applicable caught**: the four no-hose escapes now go red by name (NH_HEADER_SAYS_HOSES replaced by
  NH_HEADER_SAYS_HOSES_AFTER_FIX, its old text being gone), and TT_NO_HOSE_BAR_DECIDES_NOTHING is refused by the certificate.
  Still missed: TT_NO_HOSE_COMMAND_TRUE (today's stamps predate the recorded command; see Owed) and the six caller faults.
- Lane 1 "missed" on NH_HEADER_SAYS_HOSES_AFTER_FIX is an artefact: its baseline row already failed on the old header.
- Changed files that are records only (journal, ledger shards and views, stage_record, run_spend) got no planted fault: no
  suite reads them as a bar input.

## Faults
`lane2/faults.json` [measured counts]: **1 Problem, 8 Polish.**
- Problem `RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_LOAD_FOLDERS_SAID_PIPES` (no_hose, no_hose_in_gss), `miss_of: 4`: the Mod
  Settings header told the player "Drawn flexible pipes and wires ..." (lane-1 row NH_SOURCE_NO_TEXT_SAYING_GSS_DRAWS_PIPES),
  and T_NO_HOSE could not see a hose def in `1.6/Defs`, a hose DLL in `Assemblies/`, a joined path or settings text. FIXED.
- Polish, each naming its lane-1 row or plant: `RIMMANDRAKE_SPLIT_GSS_DLL_HOSE_DRAW_ORDER_SHARED_TABLE` (new; row
  NH_SHIPPED_DLL_NO_HOSE_SYMBOL), `RIMMANDRAKE_REWORD_GSS_NO_PIPE_BAR_POLES_ON_PURPOSE` (NOTED; row
  NH_PIPE_POLE_SPANS_DRAWN_BY_GSS_CODE), `RIMMANDRAKE_NOTE_GSS_NORTH_SOUTH_SPAN_RULER_STRAIGHT` (NOTED; row
  L1_SPAN_VISIBLE_OFF_CHORD_EVERY_BEARING), `RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME` (row L1_RESTRING_TICKS_SWEEP;
  new detail: +inf gives 0 ticks), `RIMMANDRAKE_TIGHTEN_GSS_FALLEN_WIRE_WALL_CHECK_HALF_STEP` (row L1_FALLEN_ON_GROUND_NOT_IN_WALLS),
  `RIMMANDRAKE_TRIM_GSS_FALLEN_WIRE_COILS_OUTGROW_CABLE` (row L1_FALLEN_LENGTH_NOTHING_CREATED),
  `RIMMANDRAKE_NOTE_GSS_FALLEN_TIPS_NEARLY_MEET_RARELY` (row L1_FALLEN_STRANDS_EACH_ITS_OWN: 32 pairs under 0.25 cell in 1000
  spans, more often than "rarely"), `RIMMANDRAKE_COVER_GSS_CALLERS_FOUR_PLANTS_WALKED_PAST` (the six caller plants).
  All but the first were already filed; this cycle added notes to two of them.
- Pipeline defects (not mod faults): `RIMMANDRAKE_BIND_CERTIFICATE_TO_OFFLINE_DECIDERS_NO_OP_PASSED`, fixed and closed at
  `094cd380de` (acceptance test red 2/8 on the base, 8/8 after; registered in pipeline_tests.json);
  `RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED`, handed to the Conductor (it changes the ledger's fencing).

## Fixes
`lane2/fixes.jsonl` [measured]: RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_LOAD_FOLDERS_SAID_PIPES at `396433f04a`. Red:
`python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_5/lane2/check_nohose_at.py --sha 094cd380de... --test-from 396433f04a...`
rc 2 (T1 red on the header). Green: the same with `--sha 396433f04a...` rc 0. The header now reads "Drawn wires to better
display simple circuit-like plans underneath." (his 2026-10-04 B27 line less its stale hose clause; logged
`--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`). GSS DLL rebuilt with its `.srchash`; not deployed.
Lane 1 after the fix, `lane2/lane1_rows_after_fix.jsonl`: 22 PASS, 6 FAIL, 3 INFO, 39 UNSETTLED; the six FAILs are the
Polish rows above.

## Steward's decisions enacted
The Conductor opened cycle 5 (2026-11-15 11:35 PM PST) because "17 blind faults stand claimed-fixed with no judge verdict,
which only a blind cycle can confirm or refute" (logged `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`). Verdicts
(the mod ledger refused to take them: this run writes as HOLDER, which may not write `finding.verified`; filed as
RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED):
- Confirmed by a re-plant: CARRY_GSS_GOODWILL_REMAINDER_TEST_DIVIDES_DAY (K_GOODWILL_REMAINDER_LOST now red in T_CORE).
- Confirmed for what they named, but the scan was still short (the Problem above): WIDEN_GSS_HOSE_SCAN_ONE_TEST_TWO_BARS,
  WIDEN_GSS_NO_HOSE_SCAN_PIPE_PLANT_PASSED, WIDEN_NO_HOSE_SCAN_CODE_PATHS_UNSEEN, WIDEN_NO_HOSE_SCAN_LABELLED_REEL_SLIPS,
  WIDEN_GSS_NOHOSE_SCAN_FIVE_LEFTOVERS_SLIPPED (their mutants M1-M15 each red by name).
- Code confirmed, guard weak: UNGATE_GSS_DROPPED_CORDS_FROM_OVERHEAD_MASTER (ExternalContacts runs unconditionally; its guard
  reads text, and an `if` around the call passes it: Polish, stage 6 decides).
- Confirmed by rerun only (the decider's recorded verdict repeats; not re-measured independently): VARY_GSS_SHORT_CORDS_TWINS_AT_FOUR_CELLS,
  UNBEND_GSS_RANDOM_BASES_SEVEN_SCENES_HID_IT, SLACKEN_GSS_CUT_END_LEADS_WHIP_STEALS_SLACK, STRAY_GSS_CORDS_A_CELL_OFF_THEIR_LINE,
  SWEEP_GSS_WALLED_RESIDUE_TWO_THOUSAND_SCENES (its 2000-scene sweep not rerun), RUN_GSS_TWIN_CHECK_IN_ITS_OWN_DECIDER (twin
  plants not re-planted), STEADY_GSS_GATE_RED_ONCE_THEN_GREEN, REPIN_GSS_GATE_O7_ON_SUPERSEDED_SHAPE,
  RESET_GSS_STEPTRACE_STATIC_CENSUS_CAUGHT_IT, WIDEN_GSS_FAULT_GUARD_LAY_NEEDED_SIXTY_THREE (one T_CORE run, not three).
- Refuted: none.

## Tests edited
`tests_edited.json`: `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` (strengthened; nothing removed or
loosened; mutants M16-M20 and green G3 added; five shared draw-order names and the legacy settings-file name allowed by name),
and the new pipeline test `src/RimMandrake/rimflow/acceptance/guard_certificate_binds_offline_bars_accept.py`.

## Unsettled
39 `not_kernel` lane-1 rows, every one a bar proving at stage 6 or later (stage 8 for the walk). None names an offline bar.

## Exit
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 0
exit_met: false

A Problem was FIXED in this cycle, so a new blind judge is owed.

## Owed
- A new blind judge (cycle 6) on the changed files: `selftest_gss_no_hose.py`, `GimmeSomeSlackMod.cs`, the DLL.
- `TT_NO_HOSE_COMMAND_TRUE` stays uncaught until each mod's table is restamped: `python3 src/RimMandrake/rimflow/maturation.py certificate <Mod> --run`
  records the command each test ran, after which a swapped command refuses.
- The pre-judgement certificate now refuses GSS on stale stamps for T_NO_HOSE and T_SETTINGS_SWEEP_OFFLINE (this cycle changed
  `selftest_gss_no_hose.py` and `GimmeSomeSlackMod.cs`): `python3 src/RimMandrake/rimflow/maturation.py certificate GimmeSomeSlack --run`
  (zero tokens, about 15 minutes) restamps them before cycle 6 launches.
- `maturation.py next GimmeSomeSlack` at the end of this run [measured]: "blind cycle 5 (visit 5, total 5): exit not_met: the
  judge's block says exit_met false"; NEXT: "PAUSED: three cycles, the Conductor decides". Its one FORM reason (planted rows
  lacked a top-level `caught` flag) was repaired from each row's recorded status; no verdict changed.
- The mod ledger: this run's lease lapsed after 45 idle minutes (no modledger append; rimflow notes do not renew it) and only
  DISPATCH can regrant it, so no `session.checkpoint` and none of the verdicts above reached the mod ledger (NO_CHECKPOINT
  expected). Lesson filed.
- Blindness: the run's packet named earlier cycles' findings (see Start time); this judge was not blind to them.

Spend: about $11 of the $35 bound [guess ~85%, from the session's budget line].
