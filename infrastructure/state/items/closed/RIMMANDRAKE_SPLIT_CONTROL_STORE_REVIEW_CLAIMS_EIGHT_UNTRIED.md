## spec
Codex full-file review of `src/RimMandrake/rimflow/control.py` on 2026-11-18 (raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), asked about the hook-path fix
(`RIMMANDRAKE_POINT_CONTROL_HOOKS_AT_RUN_CLONE_LAUNCHER_DELETED`), also reported eight flaws that predate it. They
are Codex's hypotheses, NOT verified by Claude: split first (a red case or a read with file:line per claim), file a
named child with its own acceptance test for each real one, note each refuted one here.
1. (P1) A failed `systemctl show` reads as an empty cgroup, so `kill_units` can say "nothing was running" and `stop`
   records a kill that did not happen (~l.1047).
2. (P1) Stopping with an unreadable store uses `spec="{}"`, losing a role run's `extra_units` (its claude scope), so
   the scope may outlive a "successful" stop (~l.1167).
3. (P1) A unit-targeted stop skips `_cancel_in_scope` and `_live_runs` reads only `started`, so an ADMITTED run keeps
   its admission after `--kill` and may still start (~l.1136, 1145).
4. (P1) Re-admitting an ambiguous admission deletes and recreates the row under the same run id without checking a
   queued unit, so the old unit's condition can consume the new admission (~l.773).
5. (P2) `fail_launch` releases reservations but re-admission deletes only HELD ones; the released rows keep their
   unique key and the retry reads as an unreadable store (~l.779).
6. (P2) `escalate` takes the newest pending order without checking its deadline, so an older timer can escalate a
   newer order (~l.1224).
7. (P2) `_mark(..., fault=True)` and `_reap` count faults without calling `_fault_alarm`, so FAULT_LIMIT can pass
   silently (~l.865).
8. (P2) An unreadable store at `condition` leaves the run `admitted`; `ended` only moves `started`, so the run can
   stay admitted forever (~l.831, 844).
Advice (polish, not a flaw unless a real clone path holds a space): hook command strings interpolate paths unquoted.
Acceptance test: none at filing, the claims are unverified; each child carries its own, watched red.

## refs
file: src/RimMandrake/rimflow/control.py

## criteria
- Each of the 8 claims is refuted (evidence noted here) or a closed child whose test failed on base.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
