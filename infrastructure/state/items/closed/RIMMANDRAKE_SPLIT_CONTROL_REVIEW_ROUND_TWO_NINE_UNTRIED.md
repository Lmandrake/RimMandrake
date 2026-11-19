## spec
Codex's second full-file review of `src/RimMandrake/rimflow/control.py` (2026-11-18 ~5:55 PM PST; raw
`D:\ClaudeWork\scratch\control_claims_review_20261118\codex.txt`) made nine claims about code older than the fixes it
was asked about. They are Codex's hypotheses, NOT verified: split first (a red case or a read with file:line per
claim), file a named child with its own acceptance test for each real one, note each refuted one here.
1. (P1) Two launches of one unit name in one process: B's re-admission replaces A's, so A's payload starts on B's
   authority; retries under one run id meter one fault (control.py ~l.791, 815). Fix offered: a unique run id per
   admission attempt.
2. (P1) `launch_unit` with `spec["unit"]` set and an argv without `--unit`: systemd names the unit itself, control
   records another name, a stop misses it (~l.977). Fix offered: insert the spec's name; refuse a conflict.
3. (P1) `stop <unit> --kill` waits the 3 s busy timeout on a locked store before its emergency fallback (~l.1176).
4. (P1) `kill_units` verifies only the pids snapshotted before the kill: a child forked after it survives unseen
   (~l.1102). Fix offered: reread the cgroup after the kill.
5. (P2) `ended()` landing while a kill verifies leaves the run `ended`, not `killed` (`_mark` frm excludes ended).
6. (P1) Two deadlines on one unit: the timer name `rm-control-escalate-<unit>` collides, the second timer is not set
   (reported "NOT set", but the order still promises its deadline) (~l.1256).
7. (P2) `pipe stop --idem` is accepted by the CLI but neither passed nor honoured (~l.1161).
8. (P2) The call-site census counts a function routed if it holds ANY launch_unit call, so a direct systemd-run beside
   one passes (~l.1502).
9. (P2) `t_verbs` asserts a pooled p95, not each verb's (selftest_control.py ~l.131).
Advice only: the header's locked-store `show` text (STORE LOCKED vs exit 3).
Acceptance test: none at filing, the claims are unverified; each child carries its own, watched red.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Each of the 9 claims is refuted (evidence noted here) or a closed child whose test failed on base.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
