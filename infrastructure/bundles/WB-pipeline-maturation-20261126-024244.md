# Work bundle WB-pipeline-maturation-20261126-024244 (pipeline:maturation)

Worker: detached BENCH run, Opus, clone `/home/mandrake/rm/relentless/clones/RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH.det`.

## Members

| ticket | class | state |
|---|---|---|
| `RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH` | REAL (the Conductor's ruling, note 5: retire C5) | fixed in group "retire C5"; open: decline the 19 old C5 proposals, fresh reader, close |

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
