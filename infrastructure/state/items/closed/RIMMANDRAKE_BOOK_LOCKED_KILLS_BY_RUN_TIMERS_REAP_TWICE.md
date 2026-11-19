## spec
Round-three Codex claims 2, 3, 4, 5, 8 and 9 on `src/RimMandrake/rimflow/control.py` (parent RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_THREE_ELEVEN_UNTRIED, whose
spec lists each claim), reproduced on origin/main 0117263ccf by `D:\ClaudeWork\scratch\control_claims_round2_20261118\probe_round3.py` (log probe3_base.log next to it).
2. A locked-store emergency kill whose run delivered ended() first was booked as an anonymous stand-in (no void, no dispatch books). Fix: read the run's identity (WAL read, no lock) before the kill and book that run.
3. A --idem replay on a locked store killed again. Fix: check the key with a lock-free read before any side effect; honour a replay found by the late booking.
4. An unreadable final cgroup reread read as verified death. Fix: None stays UNVERIFIED.
5. Two due escalation timers (or two concurrent kills) reaped one detached run twice. Fix: reap only on the run's own killed transition.
8. The fallback cgroup read ignored descendant cgroups (no live unit has one today: no Delegate= in src). Fix: walk the subtree; an unreadable one is UNVERIFIED.
9. A failed escalation retired the stop order, so the surviving agent's hook stopped delivering it. Fix: the order goes back to its state; the escalate verb exits non-zero.
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` part t_review_claims_round_three, claims 2, 3, 4, 5, 8 and 9: red on
0117263ccf, green after.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Each listed claim's check in t_review_claims_round_three fails on 0117263ccf and passes after.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
