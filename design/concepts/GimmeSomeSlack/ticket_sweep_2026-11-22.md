# Gimme Some Slack ticket sweep, 2026-11-22

Item `RIMMANDRAKE_SWEEP_SLACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE` (detached run of the Conductor, seat BENCH). Owner's
order, 2026-11-22 about 3:05 PM PST: *"Clean house on advancing mods please! GSS too, but I think we already did that."*

## Was a sweep done before?

Yes, one: 2026-11-16 (night), `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_gss_20261116.md`, landed in `91a141b0e7`. It took
62 open GSS tickets to 35: 27 retired, 10 kept for the version, 17 kept as Polish, 6 pipeline. What it left: the 17 Polish
tickets stayed open as tickets (the rule that drops a ticket failing test 1 with one polish line came later), and every ticket
filed after it (the 0.1.0 walk, the 0.1.1 stages, the pipeline lanes) was new. This sweep drops those 17 the new way.

## How the open items were found

- Reader: `model.replay()` over the whole ledger (the same fold `rimflow queue` and `rimflow show` use), every item in an open
  state (proposed, ready, doing, built, validated): 1949 open items on 2026-11-22 3:20 PM PST [measured].
- Match: the item id or title names the mod (GimmeSomeSlack, Gimme Some Slack, GSS, SLACK), or its prose under
  `infrastructure/state/items/*.md` (never `closed/`) names it; then a second pass for old names and sub-systems (Messy Conduit,
  MESSYCONDUIT, GS-1/GS-2, aerial lines, power tap, fallen wire, cords, poles). 136 + 4 = 140 candidates [measured].
- 75 were read in depth (`rimflow show` history and prose). 64 were prose-only matches whose titles are other mods' work and name
  GSS once or twice (the 2026-10-23 FlowWorks + GSS GPT review set of pit and canal defects, tier mod lists): titles read, not
  classed here. One is this sweep's own item.
- Of the 75, 13 are other mods' or pipeline-wide tickets that only mention GSS (listed at the end, untouched). **62 open items are
  about Gimme Some Slack** [measured], against the Conductor's rough count of 107 item files. The gap: the rough count counted
  files naming GSS anywhere; 94 open prose files name it [measured], and most of the extra ones are the other-mod set above.
- Could not look: nothing in the ledger was unreadable. The live game was not used (ArchBig is his walk); every "PASS" below is a
  recorded row, read from `version/in_game/visit_{1,2,3}/rows.jsonl`.

## Count per class (62)

| class | count | what happened |
|---|---|---|
| DONE | 14 | closed, or dropped with the evidence where a retired-era owed criterion refused the close |
| STALE | 4 | dropped, each naming what replaced it |
| DUPLICATE | 1 | superseded into the one ticket of its cause |
| DEAD | 0 | |
| NOT WORTH THE TOUCH | 19 | dropped `not worth the touch: <why>`, one line each on `version/polish.md` |
| NEEDS HIM | 0 | his walk of 0.1.1 (Stage 8) is the only act of his on this mod, and it is a stage, not a ticket |
| KEEP, CURRENT VERSION | 8 | now 7 modern tickets (two merged into one) |
| KEEP, NEXT VERSION | 6 | now 7 modern tickets (one merged, one new from journal Questions 4) |
| KEEP, not a mod-version ticket | 10 | pipeline or Conductor acts that name GSS; noted where the GSS part is done, left open |

### DONE (14)

- `GSS_CORD_SILENCE_PHANTOM_SPARK` (his words 2026-10-16): `39b8193916`, `SelfTest/PhantomSparkChecks.cs`.
- `GSS_POWER_THEFT_FIX_WRONG_VICTIM`: `c29007b6b66e`; sc_tap_theft, P_M19_tap_drains_one_way PASS (visit 3).
- `GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE`: P_SC_no_two_cords_alike, sc_no_repeat PASS (visit 3).
- `GRAVSHIP_WIRES_SURVIVE_LAUNCH_1` (GS-1): P_GS1_* and sc_gravship PASS (visit 3).
- `FALLEN_WIRE_SHOCK_1` (GS-2, his card 2026-10-08): P_M20a/b/c, sc_shock, sc_fuel_ignition PASS (visit 3).
- `MESSY_CONDUIT_MOD_1`, `MESSYCONDUIT_CABLE_PILE_LOOK_1`, `MESSYCONDUIT_REVIEW_ROUND1_1`: the mod's old name; his 2026-10-04 words
  are vision line 2 of the passed 0.1.0; sc_junction_strips PASS.
- `RIMMANDRAKE_SWITCH_ON_PYRELANDS_AND_SLACK_WHEN_ROWS_CLEAR`, `RIMMANDRAKE_DELIVER_SLACK_THROUGH_STAGE_EIGHT_ITS_OWN_STAGES`: GSS is
  at Stage 8 on its own stages since 2026-11-21 10:32 PM PST.
- `RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_ACCEPTANCE_VISIT_TWO`: recorded `3252972cf5`.
- `RIMMANDRAKE_AUTOBUILD_GIMMESOMESLACK_FOUR_BARS_LEFT`: `90660c8ae3`, `934b35e053`; its wait (journal Questions 4) is answered here.
- `RIMMANDRAKE_FIX_MATURATION_NOW_SELFTEST_PINNED_TO_LIVE_GSS`: selftest_maturation_now PASS today.
- `RIMMANDRAKE_REPAIR_DECK_COLLAPSE_SEAM_CHECK_LOST_ITS_ANCHOR`: `cf6efc3055`, `4b37a37db9`.

### STALE (4)

- `RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE_RUN_TWO`, `..._VISIT_TWO_RUN_TWO`: replaced by visit 3 (exit met 2026-11-21).
- `LIGHTSPEED_WIRE_GSS_FIRST_NO_LLM_PATH` (his words 2026-11-06): written up in `design/RimMandrake/lightspeed_2026-11-06.md`; its
  wiring was Relentless-era, deleted in `d2a0462048` under the standing ruling that retires the pipelines before the Maturation
  Pipeline.
- `RIMMANDRAKE_READ_SLACK_REWORK_BARS_ON_FULL_LIST`: replaced by sc_walk on his full list (visit 2) and his walk on ArchBig.

### DUPLICATE (1)

- `RIMMANDRAKE_TRACE_SLACK_MINIFIED_LOOKUP_ERROR_WITH_FLOWWORKS` into `RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR`.

### NOT WORTH THE TOUCH (19)

One line each in `version/polish.md` (section "Ticket sweep of 2026-11-22"): the 13 blind-cycle and lane findings (restring NaN,
fallen-wire coils and wall half-step, hose names in the DLL and T_NO_HOSE blind spots, caller plants, cord-guard plants, geometry
tell, async cap, sharp-row window, lay cost), `CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS`, `GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT`,
`RIMMASTER_POLISH_GSS_CORD_LEFTOVERS_AFTER_APPROVAL`, `RIMMANDRAKE_MEASURE_SLACK_LIVE_END_PARITY_COPY_AGAINST_GAME`,
`RIMMANDRAKE_EXPLAIN_SLACK_DECK_SHOCK_COUNTED_VICTIM_UNMARKED`, and `RIMMANDRAKE_TRACE_TURRET_TICK_EXCEPTION_ON_FULL_LIST_WALK_SAVE_LOAD`
(not ours: the throwing frame is the third-party LargePawns mod's dictionary).

## The modern tickets that remain

### Current version, 0.1.1 (7)

| ticket | one line | state |
|---|---|---|
| `RIMMANDRAKE_SEAT_SLACK_CORDS_IN_OFF_SWITCH_NOT_CUT` | an off switch keeps its cords connected (his walk 2026-11-20) | built `90660c8ae3`; sc_switch_off_ends PASS; closes at his walk |
| `RIMMANDRAKE_LOAD_SLACK_POLE_ICONS_ON_MAIN_THREAD` | pole buttons show their icons | built; sc_pole_icons_loaded PASS; closes at his walk |
| `RIMMANDRAKE_DRAW_SLACK_POLES_IN_FRONT_WHEN_SOUTH` | a pole south of something draws in front | built; sc_pole_south_of_tree PASS; closes at his walk |
| `RIMMANDRAKE_BLOCK_SLACK_ROOF_OVER_POLE_KEEP_THE_CUT` | no roof forms over a standing pole | built `934b35e053`; sc_no_roof_over_pole PASS; closes at his walk |
| `RIMMANDRAKE_CORRECT_SLACK_TWO_FALSE_LINES_AFTER_HIS_WALK` (new; merges two) | the review generator's sway line and the dripLoops comment are false | ready; lands when his walk ends (a mod-hash move under his walk sends the mod back to Stage 6) |
| `RIMMANDRAKE_JUDGE_SLACK_COVERAGE_AGAIN_UNDER_CALIBRATED_BRIEF` | coverage judged again under a CALIBRATED brief (his card 2026-11-16, point 19) | acceptance red today (unproven_signatures lists GSS); the Conductor launches the judge |
| `RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR` | FlowWorks `RM_PitAccess.cs:277` asks vanilla for ThingsOfDef(MinifiedThing) and logs an error | cause named, one-line fix written, acceptance red; for the FlowWorks lane (FlowWorks fixers are live) |

### Next version (7)

| ticket | one line |
|---|---|
| `RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU` | one proper icon per look in every look menu (his walk 2026-11-20) |
| `RIMMANDRAKE_STYLE_SLACK_BATTERY_LIKE_THE_LAMP` | the battery takes the four looks (his walk 2026-11-20) |
| `RIMMANDRAKE_CUT_SLACK_REVIEW_STATIONS_NOBODY_READS` | delete the review stations nobody reads (his walk 2026-11-20) |
| `RIMMANDRAKE_SPREAD_SLACK_LOOK_ALONG_LINE_EACH_MOD_ITS_OWN_ITEMS` | a look picked on one GSS item spreads along its line (his words today); next by the obvious reading, see below |
| `RIMMANDRAKE_LOOSEN_SLACK_POLE_WIRE_SWAY_STILL_TOO_STIFF` (new; from the sway ticket's open half) | pole wires sway like a hanging wire, not a rod (his words 2026-11-16) |
| `RIMMANDRAKE_ORDER_SLACK_MAST_BEHIND_TALL_SOUTHERN_PICTURES` (new; journal Questions 4 (a)) | a tall building south of a mast draws in front of it (1170 pairs today) |
| `RIMMANDRAKE_REWORD_GSS_NO_HOSE_BAR_POLES_DRAW_PIPES` | the no-hose bar text says what its oracle checks, at the next lock |

### Not a mod-version ticket, kept (10)

`SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST` (GSS half done; Pyrelands' half is that sweep's), `RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY`
(waits for the Conductor's non-author judge), `RIMMANDRAKE_TRACE_REMINE_NEAR_TWIN_WRITTEN_WITHOUT_ITS_REASON` (fix unknown),
`RIMMANDRAKE_PROVE_OBS_REPORT_ON_A_KEPT_GSS_RESULT` (tried on visit 2's kept runA_core.json: the bridge call log has rotated past
it; needs the next live run), `RIMMANDRAKE_RECORD_SLACK_DELIVERY_MISSES_BEFORE_ANY_MACHINERY` (unblocked today by DELIVER closing),
`RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK` (one false FAIL happened; fix unknown until reproduced),
`RIMMANDRAKE_ROUTE_SLACK_VISIT_TWO_FAILURES_READ_LATE_RUNS`, `RIMMANDRAKE_LAUNCH_CODEX_REVIEWS_OF_MOD_CODE_AND_ART`,
`RIMMANDRAKE_RELEASE_STAGE_CEILINGS_WHEN_THREE_MODS_REACH_THEM`, `RIMMANDRAKE_READ_SLACK_WALK_BRIEF_ARRIVAL_TWO_BEFORE_STAGING_HIS_WALK`
(the Conductor's own acts; their GSS parts are done or under way).

## What was built in this run

Nothing in the mod. Every Gimme Some Slack fix still open touches a hashed mod file, and 0.1.1 is at Stage 8, his walk on ArchBig:
a hash move under his walk is what sent the mod back to Stage 6 on 2026-11-21 7:02 PM PST. The two false lines wait on
`RIMMANDRAKE_CORRECT_SLACK_TWO_FALSE_LINES_AFTER_HIS_WALK`, ready to land when the walk ends. The FlowWorks one-line fix is in
FlowWorks' files, held by its live fixer runs. Paper written: journal Questions 4 answered; polish lines; this page; prose for
the new and merged tickets.

## For the Conductor

- **Version call to confirm:** `RIMMANDRAKE_SPREAD_SLACK_LOOK_ALONG_LINE_EACH_MOD_ITS_OWN_ITEMS` is filed next version by the
  obvious reading ("Restyle this run" already repaints cords, touching masts and lamps; following the line across overhead wires
  and switches extends it). If you read his "GSS needs" as a 0.1.1 Problem, move it.
- **Journal Questions 4** was answered under Evidence-for-Ask: both regions are outside the 0.1.1 bar; (a) is next version, (b) a
  polish line.
- **Owed acts of yours on this mod:** launch the coverage judge (`RIMMANDRAKE_JUDGE_SLACK_COVERAGE_AGAIN_UNDER_CALIBRATED_BRIEF`)
  and the miner's round-5 judge; land `RIMMANDRAKE_CORRECT_SLACK_TWO_FALSE_LINES_AFTER_HIS_WALK` after his walk.

## Not GSS, untouched (13)

`PIPE_POLE_REDRAW_NOT_A_POWER_LINE` (FlowWorks files), `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE`, `VALIDATION_UNPOISON_AUDIT_STATEFUL_CHAINS`,
`SCAN_MARKED_HARDEN_YOUNG_SIBLING_BLINDS`, `SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE`, `DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR`,
`JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS`, `RIMMANDRAKE_FADE_LAID_HOSE_ON_PIT_FLOOR_LIKE_CORDS`, `RIMMANDRAKE_TRIAGE_TWENTY_TWO_REDS_BORN_AFTER_THE_NIGHTLY`,
`RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY`, `RIMMANDRAKE_NAME_STAGE_CEILING_DANGER_OR_REMOVE_THE_LIMIT`,
`RIMMANDRAKE_OWN_RED_SUPPORTING_TEST_SIXTEEN_HOURS_UNSEEN`, `RIMMANDRAKE_WORK_HANDOFF_POINTERS_OF_NOV_TWENTY_SITTING`.
