# BOUNDARY: the Stage 6 exit reads the three test kinds and the seven outcomes (live_kinds.py, hunt_open.py, shortfall.py), Design Version 0.2.0

Code: `src/RimMandrake/rimflow/live_kinds.py` (the reading), its use in `maturation.py` (`ingame_tests`,
`read_ingame_exit`, `ingame_to_run`, `ingame_facts`, the driver's brief), `build_match.py` (`carried_rows`),
`maturation_rescue.py` (a visit's refused bars), `maturation_autonomy.py` (the steward's rules),
`src/RimMandrake/rimflow/hunt_open.py`, `src/RimMandrake/rimflow/shortfall.py` (the escalation of a scene short of its X
of Y, called by `maturation_dispatch.py`'s tick, and the Conductor's call), and `testq/testq.py` (`already_tested`). Items
`RIMMANDRAKE_TEACH_EXIT_READER_KINDS_KNOWS_THREE_WORDS_ONLY` and
`RIMMANDRAKE_ENACT_SHORT_OF_X_OF_Y_ESCALATES_CONDUCTOR_CALLS_IT`. The rule:
`design/RimMandrake/standing_rulings.md` §Live tests have three kinds. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_live_kinds.py`, which also plants a fault in each part of the reader and sees a test go
red. Acceptance test: `design/specs/2026-11-23-three-test-kinds/accept_exit_reader_kinds.py`.

Words: a **spoiled row** is a row whose outcome is ENVIRONMENT FAULT (with `spoiled_by`), APPARATUS FAULT or COULD NOT
LOOK. The **deciding row** of a check is its last row that is not spoiled, or its last row when all are spoiled. A
**shortfall** is a kind B scene with `x_of_y` whose runs on one build ended (Y valid opportunities, or the budget spent)
with fewer than X successes. The **Conductor's call** answers whether the mod's function needs X of Y, or X was a guess.

## ACCEPTS (the only inputs this is built for)

- **an-old-row.** A row of `rows.jsonl` with no `outcome` and no `forbidden`. It is read by its `verdict` and `class`.
- **an-outcome-row.** A row with `outcome` (one of the seven, any letter case, `_` or `-` for a space), and as needed
  `spoiled_by` (what spoiled the run, and the record that shows it) and `forbidden` (a list of the forbidden effects
  that were seen; `[]` for none). One row per run.
- **a-tagged-scene.** `tests.<id>` of the test table with `test_kind` (A, B or C; absent is A), `tag_evidence`, `budget`
  (a whole number of runs, kind B) and `x_of_y` (`[X, Y]`, a result that is random by design; its default budget is Y).
- **a-classed-unresolved-row.** An UNRESOLVED row on which someone later wrote `classed`: `{"outcome": <one of the other
  six>, "why": <at least six words>, "by": <who>}`. The row stays; it then reads as that outcome. A row classed
  ENVIRONMENT FAULT also carries `spoiled_by`.

- **a-recorded-call.** `tests.<id>.x_of_y_calls` of the test table, a list that `shortfall.py call` writes: `{"call":
  "needed" | "guess", "x_of_y": [X, Y] at the call, "got", "valid", "mod_sha", "why", "by", "at"}`, and `to` for a guess.

## DOES NOT SURVIVE (not promised)

- **the-loaded-build.** A row's build is its `mod_sha` and the hash of the deployed folder. What the game had loaded is
  not read (the item names it; it needs the live game).
- **a-false-record.** `spoiled_by`, `tag_evidence` and `classed` are read as present, never as true. A driver who writes
  ENVIRONMENT FAULT with a record that shows nothing is believed.
- **a-check-changed-between-runs.** The runs of a kind B scene are grouped by `mod_sha`. A changed check or scene on one
  `mod_sha` stays in the group, and its earlier runs still spend the budget.
- **a-budget-written-late.** The reader cannot see when `budget` or `x_of_y` was written. A hand that edits `x_of_y`
  without `shortfall.py call` is not seen.
- **an-unpublished-call.** The exit reads the test table of its own clone: a call that was not published holds nothing
  open and passes nothing anywhere else.
- **a-visit-that-writes-no-exit.** A shortfall is raised when the visit's exit can be read (its Exit block is on disk).
- **a-runs-list-in-one-row.** A `runs` list inside a row is not read. No row on disk held one on 2026-11-23.

## PROMISES (each one is owed a test of the same name)

- **old-rows-read-as-today.** For a check with no tag whose rows are all old rows, the reading (state, why, rows, lines,
  bars, carried, to_run) equals the reading of the code before this change, for each verdict and each class.
- **absent-tag-is-kind-a.** A check with no `test_kind` reads as kind A; an unknown `test_kind` is refused by name.
- **unknown-outcome-refused.** An `outcome` that is none of the seven reads `refused`, not_met, and names the word and the
  seven. A `forbidden` that is neither a list nor a text reads the same way.
- **success-needs-a-pass.** `outcome` SUCCESS beside a verdict that is not PASS reads `refused`: the row contradicts
  itself.
- **spoiled-run-speaks-for-nobody.** A spoiled row neither passes nor fails a check, whatever its verdict word: a SUCCESS
  before it or after it stands, and the block's claim for that check is not held against it.
- **voided-run-speaks-for-nobody.** A row marked `void_system` is read as a spoiled row, whatever its class or verdict.
- **last-run-spoiled-runs-again.** A check with only spoiled rows reads `spoiled` ("run that scene again"), never
  unclassed, never an undecided bar. An APPARATUS FAULT or COULD NOT LOOK row that also carries class HARNESS or SITE, a
  `repair` or an `unrepaired` says that the check itself is wrong: it keeps the reading of an old row
  (`design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md`).
- **environment-fault-needs-its-record.** ENVIRONMENT FAULT with no `spoiled_by` reads UNRESOLVED. So does a spoiled
  outcome beside class MOD.
- **unresolved-holds-until-classed.** An UNRESOLVED row of this visit or of any earlier visit of the version holds its
  check (`unresolved`), under any later PASS, until its `classed` names an outcome, a why and a who. A visit's
  `rows.jsonl` that is there and cannot be read makes the exit not_met by name; one that is not there holds no run.
- **forbidden-effect-is-mod-failure.** A row with a forbidden effect, or with outcome MOD FAILURE, reads as a FAIL with
  class MOD in any run. A later SUCCESS hides it only with the `mod_fix` record. One from an earlier visit on the same
  `mod_sha` counts the same way.
- **random-miss-only-by-design.** RANDOM MISS on a scene without `x_of_y` reads `refused`.
- **kind-b-one-success.** A kind B scene passes on one SUCCESS in its runs, with no MOD FAILURE and no UNRESOLVED. Its runs
  are the rows of every visit on the `mod_sha` of its latest row: a SUCCESS on an earlier build neither passes the
  scene nor ends a later build's budget (fresh read, 2026-11-23: it read pass and re-ran past its budget). The deciding
  row and MOD FAILURE check use the latest build. After a MOD FAILURE on an older build, one ENVIRONMENT FAULT on the
  new build reads `spoiled` with three of four runs left. An outstanding MOD FAILURE on the latest build still blocks a
  SUCCESS there.
- **kind-b-x-of-y.** With `x_of_y`, the scene passes on X SUCCESS rows among the first Y valid opportunities (SUCCESS or
  RANDOM MISS).
- **inconclusive-is-not-pass-or-fail.** A kind B scene with no SUCCESS when its budget of runs is spent, or with fewer than
  X successes in Y valid opportunities, reads INCONCLUSIVE, not_met, no undecided bar. Before that it reads `spoiled`
  with the runs left. APPARATUS FAULT and COULD NOT LOOK spend no budget.
- **shortfall-escalates.** A shortfall with no call on its `[X, Y]` is in the exit's `shortfalls` (scene, X, Y, successes,
  valid opportunities, tag evidence). The tick writes, once for each mod, scene, `[X, Y]` and build: one RAISE FIRST line
  in the Conductor log and a note on the item of the mod's in-game run. Both carry the scene, X, Y, the count reached, the
  tag evidence, the question (does the mod's function need X of Y, or did X guard against environmental fluctuation) and
  the two commands. A line or note that could not be written is tried again (the note after 10 minutes), and named in the
  tick's reading; the reading carries a Needs Conductor line until the call is recorded. A mod that he holds raises
  nothing. A dry tick writes nothing.
- **shortfall-holds-until-call.** A shortfall with no call reads INCONCLUSIVE, not_met, and no run after the first Y valid
  opportunities passes it. An `x_of_y_calls` entry that names no call, or has no why of six words or no by, is no call.
- **call-needed-is-mod-failure.** With the call "needed" on this `[X, Y]`, the shortfall reads as a FAIL with class MOD and
  takes the road back of one. The call stands for the scene's `[X, Y]`: a later build that ends short reads the same with
  no new question, and a later build that reaches X of Y passes.
- **call-guess-judges-again.** The call "guess" writes the new `x_of_y` on the scene. The scene is judged again on it, and
  the opportunities already run on the same build count: the runs did not change, and the call says what they are worth.
  A later shortfall on the new `[X, Y]` is a new question.
- **conductor-records-the-call.** `shortfall.py call <Mod> <scene> needed|guess [--x N] [--y M] --item ID --why "..."`
  writes the entry, publishes the table, and writes the act on the item as the Conductor's (`conductor_acts.py`). Only the
  Conductor window may; a helper, a role run, the tick or another seat is refused. Exit 0 recorded and landed; 2 refused,
  nothing written (the line names why: not the Conductor window, no shortfall read, a short why, an N that leaves the
  scene short or is more than X, an M under Y); 3 could not look (the exit, the table or a row file cannot be read); 4 the
  table is written and a landing or the note failed, named. `guess` with `--y` also raises the budget to cover M.
- **tag-without-evidence-refused.** A B or C tag with no `tag_evidence`, a B tag with no usable `budget`, and an `x_of_y`
  that is not `[X, Y]` with 1 <= X <= Y each make the exit not_met by name.
- **hunt-is-never-in-the-exit.** A kind C check is no required check and is not in to_run. A bar whose only in-game
  deciders are kind C is named, not_met: a tag does not take a bar out of the exit.
- **per-scene-run-list.** `ingame_to_run` counts a check whose reading passes and whose deciding row is untouched; a
  spoiled or INCONCLUSIVE check runs.
- **a-spoiled-fail-is-no-refused-bar.** `maturation_rescue.py` does not count a spoiled row or a RANDOM MISS as a round that
  refused a bar.
- **briefs-name-the-fields.** The driver's brief, the steward's brief and `roles/designer_scene_contract.md` name the
  fields, and the steward's brief sends a spoiled, INCONCLUSIVE or unresolved scene to no earlier stage.
- **brief-names-unclassed-runs.** The driver's brief names each run of an earlier visit that reads UNRESOLVED with no usable
  `classed`, or whose words cannot be read, on a check of the table: the check, the visit, the evidence, the `classed` to
  write, and the `CLASS OWED:` note when the evidence cannot tell. With none, the section is absent. Measured 2026-11-24:
  FlowWorks visit 10's `sc_hung_bridge` run held the exit of visit 11, and its brief did not say so.
- **hunt-open-tells-both.** `hunt_open.py ITEM --what --why-it-matters --next-step --cost` writes one `HUNT OPENED` line
  (RAISE FIRST) in the Conductor log and a note on the item. Exit 0 both written; 2 a blank field, nothing written; 3 the
  log line was not written (no note tried); 4 the log line stands and the note did not land, named.
- **budgeted-runs-repeat.** `testq submit` passes, without `--retest-why`, a chain that a kind B check with tag evidence
  names while its DONE runs at the chain's current code version are fewer than the budget, and a chain that a kind C
  check with tag evidence names. A repair hold and a Test Pilot route still bind. A table that cannot be read passes
  nothing.

## LIMITS

- The word floor of `classed.why` (6): danger, "ok" or "yes" stands as a class; evidence, the same floor on `explained`
  was set after such entries (`RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES`). The same floor holds for a call's why.
- The 10 minutes between two tries of one note: danger, a ledger write each 60 s tick on a ledger that refuses it;
  predicted from the tick's 60 s timer, never seen.

Lists beside this page: `polish.md`.
