# BOUNDARY: a wrong check is repaired or set aside in the sitting (maturation.py read_ingame_exit, read_exit, the stage briefs), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` and `src/RimMandrake/rimflow/maturation_autonomy.py`. **This page covers
only how a failed or unmeasured line is classed and what each class does to the exit**: `line_class`, `repair_shown`
and their use in `read_ingame_exit`; `check_repair` and its use in `read_exit`; and the class text in
`ingame_brief_text`, `blind_brief_text`, `steward_brief` and `fixer_brief`. Item
`RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED`; the rule is
`design/RimMandrake/standing_rulings.md` §Touching code has a cost, "A wrong check is repaired or set aside in the
sitting". Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py`;
that selftest also plants a fault in each part of the reader and sees its test go red.

## ACCEPTS (the only inputs these parts are built for)

- **a-classed-row.** A stage-6 row of `rows.jsonl` with `class` MOD (the mod is wrong), HARNESS (the check is wrong)
  or SITE (the staged scene is wrong), the classes of skill `live-debugging-proof-harness`, or no `class`.
- **a-repair-record.** A re-run row with `repair`: `{"class": "HARNESS"|"SITE", "commit": <sha>, "planted":
  {"plant": <what was planted or the known-bad state>, "command": <its command>, "verdict": "FAIL", "evidence":
  <path>}}`. The row's own verdict is the real-build reading.
- **a-set-aside-row.** A last row classed HARNESS or SITE with `set_aside`: the polish line, or with `unrepaired`: why
  the driver could not repair it (no tools, the fix is not known, another run holds the files).
- **a-blind-check-fault.** A blind-cycle Problem with `against` `check` or `scene`, FIXED, whose `fixes.jsonl` row
  carries `plant`, `red` (the repaired check on the plant, an rc non-zero), `green` (the repaired check on the real
  build, rc 0) and `sha`.

## DOES NOT SURVIVE (not handled)

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
- **set-aside-does-not-block.** A HARNESS FAIL with `set_aside` (a polish line) does not count and does not block when
  another in-game check of each of its bars counts PASS; when none does, the bar reads undecided and the visit not_met.
- **scene-wrong-same-as-check.** A SITE line follows the same rules as a HARNESS line.
- **unclassed-not-silent.** An UNMEASURED or FAIL last row with no class reads not_met and is named `unclassed`.
- **wrong-unhandled-not-silent.** A HARNESS or SITE last row neither repaired, set aside nor said `unrepaired` reads
  not_met and names what is owed.
- **mix-reads-each-line.** A visit with each kind of line reads each line's class, and only the `mod` and undecided
  lines send it back.
- **blind-check-repair-owes-no-judge.** A blind cycle whose only FIXED Problem is `against: check`, shown on its plant
  and on the real build, with a fix sha whose files are all in `tests_edited.json`, reads met; the same Problem
  `against: mod`, or with no `plant`, or with a fix sha that touches another file, still owes a new blind judge.
- **briefs-carry-the-rule.** The in-game driver, blind-judge, steward (router) and fixer briefs each carry the
  classing step, the two tests and the repair rule; the driver brief no longer says a wrong check is only a note.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
