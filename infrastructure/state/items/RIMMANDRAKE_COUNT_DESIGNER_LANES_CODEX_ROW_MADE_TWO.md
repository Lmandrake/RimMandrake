## spec

`src/RimMandrake/rimflow/selftest_concept_tree.py` found the Designer row in `dispatcher_schedule.json` by its
ledger item and required exactly one. The DesignerCodex lane (b947951936, 2026-11-15) shares that ledger item, so the
check read two rows and failed on every run since (`FAIL Designer row exists, off, no slots`). The schedule is right;
the test was wrong. Fix: pick the Claude lane (no `runner`, or `runner: claude`) for the existing checks, and add one
check that every lane under the item is off, not local, and that no two share a runner.

## criteria

- `python3 src/RimMandrake/rimflow/selftest_concept_tree.py` prints `selftest_concept_tree: PASS`.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_concept_tree.py; echo $?` expects `selftest_concept_tree:
PASS` and exit 0 (1 test). Watched it fail on the base (e7478a9864..ad4201c7b): `FAIL Designer row exists, off, no
slots`, `selftest_concept_tree: FAIL 1`. Found by RIMMANDRAKE_APPLY_BARS_CARD_PATCH_WHEN_BLIND_JUDGES_END while running
the Designer selftests after the bars-card patch; fixed in the same run (the pipeline fixes its own defects).

## refs

file: src/RimMandrake/rimflow/selftest_concept_tree.py
file: src/RimMandrake/rimflow/dispatcher_schedule.json
