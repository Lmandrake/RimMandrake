# RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS

## spec
Guard "Stage five by program" of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 3.3).
Protects against: paying a Designer run to write down what a program already knows. Evidence: ten Designer runs,
USD 8.39 measured (`D:\ClaudeWork\rimmandrake\dispatcher\roles`): seven that ended "no lock: the coverage judge
returned not_covered, every gap returns to stage 3" (FlowWorks 11-05, Gimme Some Slack 11-06 twice and 11-13, Pyrelands
11-05 and 11-06, Graffiti 11-15; USD 0.55 to 1.00 each) and three Graffiti runs on 11-15 that ended "locked" after a
signed verdict (USD 1.29, 0.73, 0.87).

Build `designer_stage.program_result(st, verdict, run)` (pure; contract in the test's docstring) and use it in
`role_launch` at stage 5 after the pre-launch coverage judge: when it returns a result, open the run, write that
result.json, and close it through `designer_stage.close_run` with no model started and no tokens charged; if the close
rejects it, launch the Designer exactly as today. A gap that returns anywhere but stage 3 (his answer is needed), an
unsigned or malformed verdict, or a verdict on another tree still gets a Designer. The lock summary and park rules that
a Designer close triggers must fire the same way; say in the close note how you checked.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/role_launch.py
file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/acceptance/guard_stage5_program_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_stage5_program_accept.py

## criteria
- A1: the acceptance test prints `PASS 13/13` and exits 0.
- A2: the designer_stage, role_launch and Designer-chain selftests stay green, with a new case: a stage-5 concept with a not_covered verdict moves to stage 3 with no run launched, and one whose program result is rejected launches the Designer.
- A3: the live half is recorded UNRUN with its command if no concept reaches stage 5 before close.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_stage5_program_accept.py` exits 0 with `PASS 13/13`.
Watched failing at ed7e3b5389: `FAIL 0/13`, exit 1 (no `program_result`). Not yet run against any implementation.
