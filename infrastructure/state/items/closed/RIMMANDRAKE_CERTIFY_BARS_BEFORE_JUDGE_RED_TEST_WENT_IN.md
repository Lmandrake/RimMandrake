# RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN

## spec
Guard "Pre-judgement certificate" of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 4). The owner, 2026-11-15: "how do we certify then that it has all
the tests needed to pass before we throw it to judgement? ... No reason to send it in knowing it will fail, right?"
Protects against: launching a blind judge or an in-game driver on a mod a program can already see will not pass.
Evidence: Explosive Knockback blind cycle 1 ended not met because the offline bar `inv_proof_scenes` was red when the
judge went in (RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE, 3,416,406 tokens); Gimme Some Slack's
cycle-2 judge found `T_STATICS_CENSUS` red and `T_CORE` failing 3 of 3 (USD 7.95); Pyrelands was sent to advance on a
stored flag with 28 of 42 bars not runnable (USD 2.76; that flag is fixed in 79483e1558, keep it).

Build `src/RimMandrake/rimflow/judge_certificate.py` (no model anywhere): `build_id`, `run_offline`, `certify` and the
verb `maturation.py certificate <Mod> [--to STAGE] [--run] [--json]`, with clauses `registered`, `ran_on_this_build`,
`green` refusing and `red_seen` only warning (the next ticket makes it refuse). The test table's `runs_today` gains
`build`, a hash of the CONTENT of the test's `reads` and its own file. `maturation.evaluate` carries the clause
`judge_certificate` on offline_build -> blind_challenge and blind_challenge -> in_game (keep
`every_bar_has_a_check_that_runs` and the owed-scene-parts reading as they are), and the Dispatch tick reads the
certificate before it launches a blind judge or an in-game visit; a refused mod reads as waiting on its certificate on
the status page, with the refusal's smallest_fix. `--run` is the path to pass for a stale table and spends no tokens.
The exact contract is the acceptance test's docstring.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
new: src/RimMandrake/rimflow/judge_certificate.py
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/selftest_maturation.py
file: src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md
item: RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD
item: RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py

## criteria
- A1: the acceptance test prints `PASS 18/18` and exits 0.
- A2: the four maturation selftests stay green, with new cases for the clause in `evaluate` and the tick's wait.
- A3: `maturation.py certificate <Mod> --run` is run for each advancing mod; its output and wall time per mod are in the close note. A mod it refuses is not hand-waved: its refusal is filed down the road back like any failed line.
- A4: backtest in the close note: check out the test table as it stood when Knockback cycle 1 was launched (the cycle's opening commit, `maturation.cycle_open_sha`) and say what `certify` reads there; the same for Gimme Some Slack cycle 2.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_judge_certificate_accept.py` exits 0 with `PASS 18/18`.
Watched failing at ed7e3b5389: `FAIL 0/18`, exit 1 (no module `judge_certificate`). Not yet run against any implementation.
