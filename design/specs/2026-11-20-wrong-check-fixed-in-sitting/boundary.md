# BOUNDARY: a wrong check is repaired or removed in the sitting (maturation.py read_ingame_exit, read_exit, the stage briefs), Design Version 0.2.0

Code: `src/RimMandrake/rimflow/maturation.py` and `src/RimMandrake/rimflow/maturation_autonomy.py`. Owner rulings
2026-11-20: the first part, and the follow-up of item `RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION`
(a needless check is removed; a mod fault the judge or driver can fix is fixed in the sitting, with one fresh reader of
the fix). **This page covers
only how a failed or unmeasured line is classed and what each class does to the exit**: `line_class`, `repair_shown`
and their use in `read_ingame_exit`; `check_repair` and its use in `read_exit`; and the class text in
`ingame_brief_text`, `blind_brief_text`, `steward_brief` and `fixer_brief`, with the three duties of
`FIX_IN_SITTING_RULE` and the Dispatch step's line after a visit whose exit is not met
(`maturation_dispatch.INGAME_NOT_MET`; item `RIMMANDRAKE_REFUSE_OWN_MOD_HANDOFF_DRIVER_RENAMED_NOTHING`, the owner on
2026-11-25: "I want Option (3) absolutely."). Item
`RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED`; the rule is
`design/RimMandrake/standing_rulings.md` §Touching code has a cost, "A fault is fixed in the sitting; a wrong check is
repaired or removed there; neither sends the mod back". A row with an `outcome`, and a tagged scene, are
read first by `live_kinds.py` (`design/specs/2026-11-23-live-kinds-exit-reader/boundary.md`).
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py`;
that selftest also plants a fault in each part of the reader and sees its test go red.

## ACCEPTS (the only inputs these parts are built for)

- **a-classed-row.** A stage-6 row of `rows.jsonl` with `class` MOD (the mod is wrong), HARNESS (the check is wrong)
  or SITE (the staged scene is wrong), the classes of skill `live-debugging-proof-harness`, or no `class`.
- **a-repair-record.** A re-run row with `repair`: `{"class": "HARNESS"|"SITE", "commit": <sha>, "planted":
  {"plant": <what was planted or the known-bad state>, "command": <its command>, "verdict": "FAIL", "evidence":
  <path>}}`. The row's own verdict is the real-build reading.
- **an-unrepaired-row.** A last row classed HARNESS or SITE with `unrepaired` (why the driver could not repair it: no
  tools, the fix is not known, another run holds the files) and `owner` (the run or the filed item that keeps it).
- **a-mod-fix-record.** A re-run row after a MOD FAIL with `mod_fix`: `{"commit": <sha>, "red": {"cmd", "rc"}, "green":
  {"cmd", "rc"}}`, the before/after test (red an rc non-zero on the parent, green rc 0 on the fix).
- **a-fix-review.** One row per mod fix in `fix_reviews.jsonl` (the visit folder, or the cycle's `lane2/`): `{"fix":
  <commit> | "fault": <id>, "reader": <unit>, "verdict": "sound"|"unsound", "why"}`, by a reader that did not make the
  fix. A reader that fixes the fix writes `"verdict": "fixed"`; that row and the fresh validator it owes are on
  `design/specs/2026-11-25-blind-readers-fix/boundary.md`.
- **a-blind-check-fault.** A blind-cycle Problem with `against` `check` or `scene`, FIXED, whose `fixes.jsonl` row
  carries `plant`, `red` (the repaired check on the plant, an rc non-zero), `green` (the repaired check on the real
  build, rc 0) and `sha`.

## DOES NOT SURVIVE (not handled)

- **a-reader-that-says-it-did-not-fix.** The reader checks that the review's `reader` is not the fix's `unit`. It
  cannot check that the reader really read the fix.
- **a-repair-not-recorded.** A driver that changes a check and re-runs it without writing `repair` gets the reading of
  an unchanged re-run: an earlier HARNESS or SITE row spends nothing, and the last PASS counts. The reader cannot see
  that the check changed.
- **a-plant-that-is-not-a-fault.** The reader checks that a planted reading exists and reads FAIL. It cannot check
  that the plant was a real fault.

## PROMISES (each one is owed a test of the same name)

- **all-pass-met.** Every check's last row PASS, unclassed, with no earlier FAIL: the visit reads met, as before.
- **mod-wrong-not-met.** A FAIL classed MOD reads not_met, the line's class reads `mod`, and an earlier MOD FAIL is not
  hidden by a later PASS.
- **check-wrong-repaired-counts.** A HARNESS FAIL followed by a PASS whose `repair` shows a planted FAIL and a commit
  counts as PASS; the visit reads met, and the reading keeps the class, the commit and both readings.
- **repair-without-planted-not-pass.** The same with the planted reading missing, or not FAIL, reads the check
  `not_counted`, never PASS; its bar, with no other counted decider, reads undecided, and the visit not_met.
- **needless-check-is-removed.** A HARNESS or SITE line whose every bar another check decides reads not_met with
  "remove it from the test table"; the same visit with that check taken out of the table reads met. A `set_aside`
  field changes nothing.
- **not-counted-needs-owner.** A needed check (its bar has no other decider) that is repaired and not shown both ways,
  or said `unrepaired`, reads `not_counted` only with an `owner`; its bar reads undecided. Without an owner it reads
  `unhandled`.
- **mod-fixed-in-sitting-counts.** A MOD FAIL followed by a PASS whose `mod_fix` shows red then green counts as PASS
  when a reader that did not make the fix wrote a `sound` review of it; with no review, an `unsound` one, or a review by
  the fixer's own unit, the visit reads not_met and names the owed reader. A `mod_fix` with no red reads `mod`.
- **one-build-is-the-last-rows.** Earlier rows on the build before a fix in the sitting do not make the visit read two
  builds; the last rows of the checks must name one build.
- **scene-wrong-same-as-check.** A SITE line follows the same rules as a HARNESS line.
- **unclassed-not-silent.** An UNMEASURED or FAIL last row with no class reads not_met and is named `unclassed`.
- **wrong-unhandled-not-silent.** A HARNESS or SITE last row neither repaired nor said `unrepaired` reads
  not_met and names what is owed.
- **mix-reads-each-line.** A visit with each kind of line reads each line's class, and only the `mod` and undecided
  lines send it back.
- **blind-check-repair-owes-no-judge.** A blind cycle whose only FIXED Problem is `against: check`, shown on its plant
  and on the real build, with a fix sha whose files are all in `tests_edited.json`, reads met; the same Problem
  `against: mod`, or with no `plant`, or with a fix sha that touches another file (or git cannot read), is a mod fix.
- **blind-mod-fix-owes-one-fresh-reader.** A blind cycle whose FIXED mod Problem has a `sound` review by a reader that
  is not the fix's `unit` reads met, also when the judge wrote exit_met false; with no review, an `unsound` one, a
  review by the fixer's unit or a fix row that names no unit, it reads not_met and names `fix_reader_owed`.
- **briefs-carry-the-rule.** The in-game driver, blind-judge, steward (router) and fixer briefs each carry the
  classing step, the two tests, the repair rule, the mod fix in the sitting with one fresh reader, the live game taken
  when free (`bridge take --idle-ok`) and the `red-seen` record for an edited deciding test; none still says to set a
  check aside, that a wrong check is only a note, or that a cycle's fixes owe a new blind judge.
- **exit-not-met-sends-back-only-unknown-causes-and-undecided-bars.** The Dispatch step's line after a visit whose exit
  is not met sends down a road back only a mod fault whose cause stays unknown after the driver's sincere attempt, and
  an undecided bar, each with its red deciding test or its open hunt item. It says that a mod fault with a known fix
  that the driver left is a defect of that visit, whose next act is a run that fixes it on a free game, not a road back.
  It no longer sends each mod-wrong line back.
- **the-driver-brief-states-the-three-duties.** The in-game driver's brief carries `FIX_IN_SITTING_RULE`: a mod fault
  with a known fix is fixed in the sitting (red on the parent build, green on the fix, then the checks that the fix
  touches); a behaviour that no check sees gets its check in the sitting, seen FAIL on a planted fault and PASS on the
  real build; a fault goes back only after a sincere attempt at its cause, naming each thing that was tried. A strange
  thing that is a mod fault with a known fix is fixed before it is filed, and "the fix is not known" is no reason
  without the sincere attempt.
- **the-steward-brief-states-the-three-duties.** The steward's brief on a visit whose exit is not met carries the same
  three duties, and routes a known fix that the driver left as a defect of that visit, not a road back.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
