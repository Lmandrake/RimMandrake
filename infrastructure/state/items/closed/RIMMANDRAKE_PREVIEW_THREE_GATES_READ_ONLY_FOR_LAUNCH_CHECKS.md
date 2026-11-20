## spec
DESIGN DECISION 2026-11-18 (on RIMMANDRAKE_ADD_LAUNCH_CHECKS_EXAM_CERTIFY_JUDGE_THREE_UNCAUGHT, which this item replaces): a launch check reads the gate's OWN decision function through a read-only flag, never a second copy of the gate's rules. Exit 0 = the gate would open; 1 = it would refuse, the gate's own words printed; 126 = could not look (launch_checks.py already reads 126 as "did not run", never a refusal).
- `designer_stage.py open <dir> --run <any> --preview`: calls `open_run(..., commit=False)` (the launcher's existing preview), prints no packet, writes nothing.
- `coverage_judge.py status <dir> --would-judge`: exit 0 only when `plan(d)` says `judge`; `skip`, `stopped`, `parked`, `ceiling` exit 1; `error` exits 126. Without the flag `status` is unchanged.
- `concept_tree.py certify <dir> --owner-event OWNER:<tsn> --check`: `certify(..., check=True)` runs every check certify runs and stops before the ledger note and the stamp.
- `launch_checks.block_for("designer_open"|"coverage_judge", mod=...)` and `block_for("certify", mod=..., owner_event="OWNER:<tsn>")` return the must-pass block; a missing or malformed mod or event raises ValueError.
- The one steward the code files for these gates, `exam_retake` (maturation_autonomy.py:1149), gets the `designer_open` block the way `advance_checks` gives `advance` its block. The exam, re-certify and coverage-judge items the Conductor files by hand take the same block from `block_for` (say so in roles/conductor.md §Builds, one line).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/concept_tree.py
file: src/RimMandrake/rimflow/launch_checks.py
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- The acceptance test passes 30 of 30; selftest_launch_checks and selftest_maturation_autonomy stay green.
- An `exam_retake` steward item is filed with its `## launch-checks` block (a selftest_maturation_autonomy case).

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/gate_previews_accept.py` (30 checks; on 0117263cc in a throwaway `git clone --shared`, watched: 21 red, 9 green). Covers, per gate: would open, would refuse with the gate's words, could not look, a real locked concept, a missing folder; every coverage plan value; that no concept file and no ledger shard changes; each block and its malformed inputs.
