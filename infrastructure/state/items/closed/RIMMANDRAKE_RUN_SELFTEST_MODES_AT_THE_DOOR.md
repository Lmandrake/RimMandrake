# RIMMANDRAKE_RUN_SELFTEST_MODES_AT_THE_DOOR

## spec
`src/RimMandrake/rimflow/selftest_maturation.py` has four modes: the default `main()` and `--ingame`, `--blind`,
`--launch`. `src/RimMandrake/Utils/pipeline_tests.json` lists the file once with no arguments, and neither it nor
`run_selftests.py --only` can pass arguments, so the door (`./publish` pipeline checks) runs only the default mode.
A change that breaks the in-game exit reader, the blind reader or the launcher alone publishes green.
`selftest_build_match.py --mutants` is likewise not run at the door. Found 2026-11-17 while building
`RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO` (all four modes and the mutants were run by hand, all pass).

Work: either make the default `main()` run every mode (each is about a second), or let a `pipeline_tests.json` entry
carry `args` and have `publish.py pipeline_checks()` and `run_selftests.py` pass them.

## verify
Break the in-game reader in a scratch copy: the door's run of the maturation selftests goes red.

## criteria
- a fault in any one mode of selftest_maturation.py, or a surviving build_match mutant, turns the door red.
