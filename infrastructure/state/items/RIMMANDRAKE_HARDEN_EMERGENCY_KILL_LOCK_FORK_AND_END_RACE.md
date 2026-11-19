## spec
Round-two Codex claims 3, 4 and 5 on `control.py` (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_TWO_NINE_UNTRIED), reproduced on base
19d3e29026 by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round2.py`:
3. `pipe stop <unit> --kill` on a locked store waited 3.02 s (the txn busy timeout) before its emergency fallback; the
   header promises emergency stopping never waits on the store. Fix: the unit-kill path tries the store with a short
   timeout, kills on the fallback at once, and records the kill afterwards when the store frees.
4. `kill_units` verifies only the pids snapshotted before the kill: when `systemctl kill` fails, a process that
   entered the cgroup after the snapshot survives and the unit reads dead. Fix: when systemctl's kill fails, reread the
   cgroup and SIGKILL until it is empty; an unreadable reread is UNVERIFIED.
5. An `ended()` receipt landing while a kill verifies leaves the run `ended`, not `killed`. Fix: a kill that
   killed processes records the captured run killed from `ended` too (a run that had nothing running stays ended).
Acceptance test: selftest_control part t_review_claims_round_two (claims 3, 4, 5): red on base, green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- A unit kill on a locked store returns in under 1 s and the run is recorded killed once the store frees.
- A late cgroup member after a failed systemctl kill is killed or reported a survivor, never "dead".
- An end receipt during the verify still reads killed.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
