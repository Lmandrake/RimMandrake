## spec
Round-three Codex claims 1 and 6 on `src/RimMandrake/rimflow/control.py` (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_THREE_ELEVEN_UNTRIED, whose
spec lists each claim), reproduced on origin/main 0117263ccf by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round3.py` (log probe3_base.log next to it).
1. A re-admission refused on a resource had already deleted the first admission, so a third admission reused run_<unit> and the first's queued unit started on it. Fix: replace the old row only after every check passes (the old row's held reservations do not count against its own replacement).
6. unit_of read a payload argument --unit as systemd-run's own option (a launch with a spec unit was refused). Fix: read only systemd-run's option region (option operands, the command, --).
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` part t_review_claims_round_three, claims 1 and 6: red on
0117263ccf, green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Each listed claim's check in t_review_claims_round_three fails on 0117263ccf and passes after.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
