## spec
Round-three Codex claims 7, 10 and 11 on `src/RimMandrake/rimflow/control.py` (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_THREE_ELEVEN_UNTRIED, whose
spec lists each claim), reproduced on origin/main 0117263ccf by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round3.py` (log probe3_base.log next to it).
7. The census routed a builder called beside a launch_unit call, an alias run directly, and two literals on one line by the first; and refused an alias passed to launch_unit. Fix: sites by AST node, aliases followed, builder calls checked like literals.
10. Hook commands broke on a db or clone path with a space. Fix: quote each argument.
11. A sub-second --deadline parsed to 0 and silently meant no deadline. Fix: refuse a deadline that is not at least 1 s.
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` part t_review_claims_round_three, claims 7, 10 and 11: red on
0117263ccf, green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Each listed claim's check in t_review_claims_round_three fails on 0117263ccf and passes after.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
