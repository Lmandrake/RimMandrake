# RIMMANDRAKE_MEND_ERA_SPLIT_SELFTEST_CALLS_REMOVED_REFUSAL

## spec
Found 2026-11-18 by a lane run's selftests: `src/RimMandrake/rimflow/selftest_relentless.py` crashes before a verdict,
`AttributeError: module 'rimflow.concept_tree' has no attribute 'relentless_refusal'`, on origin/main 3e3f32e503 with
no other change (measured in a throwaway `git clone --shared`). Commit 0e52f58619 ("era split: ... concept_tree.relentless_refusal
(only the tick called it) goes") removed the function; something the test still reaches calls it. The era-split lane
owns that code and may be mid-change: check its state first, then remove the remaining call (or the test's case for
the retired tick), keeping both lanes' behaviour.

## criteria
- Acceptance test: `python3 src/RimMandrake/rimflow/selftest_relentless.py` reaches a verdict and passes; it crashes
  today (watched 2026-11-18).

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_relentless.py` GREEN.

## refs
file: src/RimMandrake/rimflow/selftest_relentless.py
file: src/RimMandrake/rimflow/concept_tree.py
