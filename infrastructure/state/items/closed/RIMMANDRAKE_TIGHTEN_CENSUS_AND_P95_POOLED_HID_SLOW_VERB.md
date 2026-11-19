## spec
Round-two Codex claims 8 and 9 (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_TWO_NINE_UNTRIED), reproduced on base 19d3e29026 by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round2.py`:
8. `control.call_sites` counts a systemd-run site routed when its function holds ANY launch_unit call, so a direct
   `subprocess.run(["systemd-run", ...])` beside one passes. Fix: each site is routed only when a launch_unit call
   consumes that argv (directly or through the name it is assigned to) and no other call runs it.
9. `t_verbs` asserts a pooled p95 while saying "every pipe verb's p95": a verb at 1.5 s passes. Fix: the check is per
   verb.
Acceptance test: selftest_control t_sites (mixed-function mutant) and t_verbs' per-verb check on a synthetic slow verb:
red on base, green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- The mixed-function mutant turns the census red; every live site stays routed.
- One slow verb fails t_verbs' p95 check.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
