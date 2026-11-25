# BOUNDARY: a blind reader fixes the fault it sees, and a new fresh reader validates the fix (maturation.py review_state; coverage_judge.py judge_fix), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`review_state`, `review_sound`, `run_lineage`, `FIX_CHAIN_ENDED`, and
their use in `read_exit`, `read_ingame_exit` and the walk's landed changes), `src/RimMandrake/rimflow/maturation_autonomy.py`
(the fresh-reader bullet of `STEWARD_RULES`, `_fix_chain_ended` and the decision `fix_chain_ended` in `_route`), and
`src/RimMandrake/rimflow/coverage_judge.py` (`JUDGE_FIX_TEXT`, `JUDGE_FIXABLE`, `judge_tail(may_fix)`, `judge_fix`,
`own_fix_only`, the judge's claims in `delta_plan`, the chain stop in `stop_reason`). Item
`RIMMANDRAKE_LET_BLIND_READERS_FIX_TWO_STILL_FORBIDDEN_IN_CODE`. Tests of the same names:
`src/RimMandrake/rimflow/selftest_blind_readers_fix.py` (`--mutants` plants a fault in each promise's code).

The owner's ruling, 2026-11-25, 11:48 AM PST: "I disagree! A blind judge absolutely CAN fix and SHOULD fix! But it would
then require a new blind judge run to validate its work thereafter. But if it just went through the trouble to blind
judge and can see the problem... friggin fix it! You're about to fail the mod anyway... why wouldn't you?" The rule text:
`CLAUDE.md` §Touching code has a cost.

## ACCEPTS (the only inputs these parts are built for)

- **a-reader-fix-row.** A `fix_reviews.jsonl` row `{"fix": <commit> | "fault": <id>, "reader": <unit>, "verdict":
  "fixed", "fixed_at": <the reader's commit>, "red": {"cmd", "rc"}, "green": {"cmd", "rc"}, "why"}`, beside the rows
  `sound` and `unsound` of `design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md` (a-fix-review).
- **a-validator-row.** A row keyed `"fix": <the reader's fixed_at>` (a short or a full sha), by a reader that made
  neither fix.
- **a-conductor-row.** After a chain ends, a row on the last fix with `"reader": "CONDUCTOR"` and `sound` or `unsound`.
- **a-judge-fixed-gap.** A coverage gap with `judge_fixed` (what the judge changed in `scenes.json`), in a look whose
  judge edited the concept's files while it judged.

## DOES NOT SURVIVE (not handled)

- **a-reader-that-hides-its-fix.** A reader that changes the mod and writes `sound` is read as sound. The code cannot
  see who made a commit; the steward brief carries the rule.
- **a-validator-outside-the-records.** A run that carries on a fixer's session with no detached record, or with no
  `continued_from` / `continue_root`, is not seen as the fixer (`run_lineage` reads only those records).
- **a-judge-edit-outside-the-concept-inputs.** The coverage judge's tail denies no tool. An edit outside the six
  concept inputs (a role file, the bar rule) is not seen by `moved_inputs`; the prompt forbids it, and the brief hash
  (refusal_contract) sees an edit of a brief file.
- **a-judge-fix-in-the-tree-or-sheet.** A judge's edit of any input but `scenes.json` is no fix: it is read as an input
  that moved under the judge (`stale_inputs`), as before. The tree and the sheet are the Cold Reader exam's frozen inputs
  (`designer_stage.EXAM_FROZEN`), and `record.json` holds his words, so those gaps stay the Designer's.

## PROMISES (each one is owed a test of the same name)

- **a-readers-fix-is-no-pass-and-owes-one-fresh-validator.** A row that reads `fixed` at a commit is no pass: the
  state reads `owed`, names the reader and its commit, and lists the fix in `chain`. A validator's `sound` on that
  commit reads sound, its `unsound` reads unsound. A `fixed` row with no commit reads unsound (the fault stands). A
  `fixed` row whose red then green is not shown still owes the validator, and says so.
- **the-validator-starts-fresh-and-made-no-fix.** A row on the reader's fix by that reader, by the maker of the first
  fix, or by a run that carries on the reader's run (`run_lineage`: its record's `continued_from` or `continue_root`)
  is not counted. A row by another run is.
- **the-chain-ends-at-the-second-fix.** When the validator also reads `fixed`, the state reads `ended`, its reason
  starts with `FIX_CHAIN_ENDED`, and a row on that second fix by any other reader is not counted: there is no third
  read. Only a row by `CONDUCTOR` on the second fix decides it, sound or unsound.
- **the-blind-exit-reads-the-chain.** A blind cycle's FIXED mod Problem read `fixed` by its reader reads not_met with
  `fix_reader_owed` and `reader_fixes`; with a validator's `sound` it reads met; with a second fix it reads not_met
  with `fix_chain_ended`, no `fix_reader_owed`, and a reason that carries `FIX_CHAIN_ENDED`.
- **the-visit-exit-reads-the-chain.** The same for a visit's mod fix made in the sitting: `fix_readers_owed`, met
  after a validator's `sound`, and `fix_chain_ended` after a second fix.
- **the-tick-sends-an-ended-chain-to-the-conductor.** An exit not met whose reasons carry `FIX_CHAIN_ENDED` gets the
  decision `fix_chain_ended` and no steward run (a steward would be the third reader); an exit not met without it gets
  its steward as before.
- **the-steward-brief-lets-the-reader-fix.** The steward's fresh-reader bullet takes `sound`, `unsound` or `fixed`,
  says to fix test first and how to write the row, that the row is no pass of its own fix, that one new fresh reader
  that starts fresh validates it, that the chain ends at the validator's fix with no third read, and that a fix never
  moves a bar; it no longer says "never fix the fix yourself".
- **the-coverage-judge-may-fix-and-its-second-reader-reads-only.** The coverage judge is started with no tool denied;
  its second reader, which grades criteria from JSON and opens no file, is still started with Edit, Write and
  NotebookEdit denied.
- **the-coverage-prompts-carry-the-fix-rule.** The full and the delta prompt carry `JUDGE_FIX_TEXT` (fix a gap whose
  repair is known and lies wholly in `scenes.json`; write `judge_fixed`; the fix is no pass; a fresh judge checks it;
  the chain ends at a second fix) and no longer say "Do not edit any file" or "edit nothing".
- **a-judges-fix-is-no-pass-and-no-refusal.** A look whose gaps carry `judge_fixed` and whose moved inputs are only
  `scenes.json` records `judge_fixed`, reads not_covered (also when the judge wrote covered), signs nothing, counts as no
  refusal (`is_refusal` false), and the next look is a delta whose claims are the fixed gaps, checked by a fresh judge.
- **a-judges-fix-outside-scenes-is-no-fix.** The same with `sheet.md` moved records `judge_fix_refused`, no
  `judge_fixed`, and the moved inputs as stale, as any input that moved under a judge.
- **the-coverage-chain-ends-at-the-second-fix.** A look after a `judge_fixed` look that fixes again records
  `fix_chain_ended`; `run` stops and holds the concept for the Conductor; `plan` then reads stopped and no third judge
  is launched until `coverage_judge.py release`. Each look is a new unit with no `--resume`.

## The rule that ends the chain

A reader's fix gets one validator. When that validator also fixes, the chain ends: no third blind read of the same fix.
For a mod fix, the exit reads `fix_chain_ended` and the tick launches nothing on it until the Conductor writes a row
with reader `CONDUCTOR` on the last fix. For a coverage look, judging stops (the concept is held on
`REFUSAL_NOTHING_COULD_EVER_PASS`, the Conductor is told) until `coverage_judge.py release` grants one look.

## What runs again after a reader's fix

A reader's fix is a change to the mod or its tests, so §After a change, only the checks that the change touches run
again decides: the validator reads only that fix, and the exit readers keep every row whose check the fix did not touch.
A coverage judge's fix moves `scenes.json` only, so the next look is a delta over the claimed gaps and the changed
scene entries, not a full inspection. The judge's `scenes.json` edit lands with the Designer harvest that lands
`coverage_verdict.json` (`designer_stage.state_paths`: every concept file the clone changed).

## Untested here

A real reader that fixes in a real stage. The first stage that will show it: the next blind cycle or in-game visit
whose exit owes a fresh reader of a mod fix (the steward run of `exit_not_met`), and the next stage-5 coverage look of
a Designer concept.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
