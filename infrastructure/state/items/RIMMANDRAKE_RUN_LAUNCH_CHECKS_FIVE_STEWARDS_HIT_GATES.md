# RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES

## spec
Guard "Gate first" of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 3.2).
Protects against: a paid run whose first act is to run a program that tells it to stop. Evidence: five steward runs
(RIMMANDRAKE_ADVANCE_PYRELANDS_PAST_OFFLINE_BUILD USD 2.76; RIMMANDRAKE_ADVANCE_GRAFFITI_LOCKED_VERSION_TO_PREFLIGHT
307,402 tokens; RIMMANDRAKE_SIT_PYRELANDS_OWED_EXAM_AND_JUDGE_LOCKED_FIRST USD 1.80;
RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING 255,598 tokens; the 2026-11-13 07:54Z run that found the
coverage judge parked, 321,409 tokens) and eight fixers whose red test already passed on origin/main (seven
SELFTEST_FIX_* runs of 2026-11-15 and one "chunk 3 is already on main", 1.38M tokens).

Build:
1. `src/RimMandrake/rimflow/launch_checks.py`: `parse`, `run`, `block_for` (contract in the test's docstring). An item's
   `## launch-checks` section holds `must-pass: <command>` and `must-fail: <command>` lines. Only this declared block is
   read; prose never refuses.
2. `detached_helper.launch` runs the block in the run's clone before the unit starts
   (`launch_check_refusal`); a refusal exits 2 and prints evidence, would_pass and smallest_fix; exit 126/127, a timeout
   or an unknown line is "launch check did not run" and the launch goes ahead; `--skip-launch-checks "<why>"` is the
   Conductor's recorded bypass.
3. `maturation.py gate <Mod> --to <stage>`: read-only, exit 0 when `evaluate` refuses nothing but its own hand_steps.
4. `maturation_autonomy` writes the block (`launch_checks.block_for`) into the steward items it files for an advance,
   and the road-back and nightly filers write `must-fail: <the red test's command>` into a fixer item filed from a red
   test. Add the exam, certify and coverage-look lines only where that gate has a read-only command whose exit code you
   have checked both ways; name the ones left out in the close note.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
new: src/RimMandrake/rimflow/launch_checks.py
file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/acceptance/guard_launch_checks_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_launch_checks_accept.py

## criteria
- A1: the acceptance test prints `PASS 21/21` and exits 0.
- A2: the detached_helper, maturation and maturation_autonomy selftests stay green; a selftest for launch_checks runs at ./publish.
- A3: backtest in the close note, one line per cited run: would its launch have been refused, by which line.
- A4: one real launch is watched refused: file a throwaway item with `must-fail: true`, launch it, paste the refusal, drop the item.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_launch_checks_accept.py` exits 0 with `PASS 21/21`.
Watched failing at ed7e3b5389: `FAIL 0/21`, exit 1 (no module `launch_checks`, no `gate` verb). Not yet run against any
implementation.
