# Work bundle WB-pipeline-maturation-20261126-024244 (pipeline:maturation)

Worker: detached BENCH run, Opus, clone `/home/mandrake/rm/relentless/clones/RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH.det`.

## Members

| ticket | class | state |
|---|---|---|
| `RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH` | REAL (the Conductor's ruling, note 5: retire C5) | fixed at cce06457 (polish 4ac2f63a); closed |

## Group "retire C5" (one cause: the Conductor's ruling of 2026-11-25)

- Red run: `python3 src/RimMandrake/rimflow/selftest_maturation_rescue.py` on the base code with the new test: 8 FAIL
  (C5 in CRITERIA, C5 proposes on a held-site record, C5 reads UNMEASURED, no Stage 6 rule line, no retired status line).
- Green run: the same, 80 checks, 0 FAIL. Also green: `selftest_live_kinds.py` (28), `selftest_own_cgroup.py` (32),
  `selftest_wrong_check_fixed_in_sitting.py` (23). The comparison page's cmd check exits 0.
- Files: `src/RimMandrake/rimflow/maturation_rescue.py` (C5 out of CRITERIA, `RETIRED`, `_c5`/`read_unrun`/C5
  unmeasured removed, retired criteria still tally), `src/RimMandrake/rimflow/maturation.py` (one line in
  `WRONG_CHECK_RULE`: a decider on a held site is a wrong scene, SITE; Test Pilot sitting if it still fails),
  `src/RimMandrake/rimflow/selftest_maturation_rescue.py`, `design/RimMandrake/standing_rulings.md`,
  `design/specs/2026-11-25-test-pilot-vs-fable-rescue/comparison.md`.
- Polish lines read: `design/specs/2026-11-22-mod-next/polish.md` (maturation_rescue.observe holds: a record, no work);
  `design/specs/2026-11-23-live-kinds-exit-reader/polish.md` (page says "a record; nobody works it");
  `design/specs/2026-11-23-raid-tests-paused/polish.md` lines on `maturation.py` (only_paused_scene_blocks_stage_six,
  walk_diagnostic_says_paused_after_lift): left. Each changes the raid-pause exit logic, which this run did not touch
  (its only `maturation.py` change is one string of `WRONG_CHECK_RULE`) and which no test of this run covers.

## Group "retire C5": landed

- Published `cce06457` (the retirement), `4d71ae8c` and `bc4abe4d` (guiding-prose repairs of standing_rulings.md),
  `4ac2f63a` (polish: the fresh reader's four nits). The `maturation_advance` calibration row was recalibrated
  alone (3 planted cases as planted); a full `calibrate` would have reset six other seats' rows, so it was not kept.
- Fresh reader (Opus, `code_review.md`): nothing significant; four nits, all done in `4ac2f63a`.
- Old proposals: 9 were open with C5 at 7:20 PM PST (23 ever; 4 made after the ruling). The 7 with C5 only were
  declined with the reason. 2 (`rp-explosiveknockback-1795451807`, `-1795460021`) carry C1 evidence too and stay open
  for the Conductor: declining them would hide the C1 evidence.
- Live reading: the dispatch clone `/home/mandrake/rm/dispatch` carries the fix; its tick at 2026-11-25 7:19 PM PST read
  3 mods and proposed nothing; `maturation_rescue.py scan ExplosiveKnockback` there: 0 proposals (that mod made every
  recent C5 proposal).
- Item check: `list_shape.py holds` HOLDS (parts comparison_page, c5_retired).
