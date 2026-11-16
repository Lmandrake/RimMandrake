# RIMMANDRAKE_CHECK_DESIGNER_RESULT_BEFORE_EXIT_EIGHT_REJECTED

## spec
Guard "Result before exit" of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 3.1).
Protects against: a Designer run that ends without a result.json the stage machine accepts, so the run is rejected after
it is paid for. Evidence: 16 rejected stage runs 2026-11-04 to 11-15 (each concept's stage.json `results`): 8 "no
result.json (a closing message is not a result)", 4 "source path ... does not exist" for a file origin/main held
(Gimme Some Slack, 2026-11-05, 11-06 twice, 11-13), each followed by a paid retry (USD 0.99, 0.79, 1.28).

Build two things:
1. `.claude/hooks/role_result_before_stop.py`, a Stop hook registered in `.claude/settings.json`, active only when
   `role_launch` has set RM_DESIGNER_DIR for a stage-machine run. It runs `designer_stage.py check <folder>`; a failing
   check blocks the stop with the check's own words, at most twice per unit; the third time it lets the run end.
   `role_launch` sets RM_DESIGNER_DIR and RM_ROLE_UNIT for Designer (Claude) stage runs.
2. `designer_stage.source_errors` gains `on_origin`: a cited repo path missing in the clone but present on origin/main
   is not an error.
The exact contract (environment names, outputs, the three origin answers) is the acceptance test's docstring.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
new: .claude/hooks/role_result_before_stop.py
file: .claude/settings.json
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/role_launch.py
file: src/RimMandrake/rimflow/acceptance/guard_designer_result_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_designer_result_accept.py

## criteria
- A1: the acceptance test prints `PASS 12/12` and exits 0.
- A2: `run_selftests.py --only` the designer_stage and role_launch selftests stays green; a new selftest for the hook runs at ./publish.
- A3: backtest in the close note: for each of the 16 rejected runs, would the hook or the origin check have caught it (expected: the 8 no-result runs and the path rejections origin held; not the other 4).
- A4: the live half is recorded UNRUN with its command if no Designer run happens before close: the next stage run that tries to end without result.json shows one block in its transcript.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_designer_result_accept.py` exits 0 with `PASS 12/12`.
Watched failing at ed7e3b5389: `FAIL 0/12`, exit 1 (no hook file; `source_errors` takes no `on_origin`). Not yet run against
any implementation.
