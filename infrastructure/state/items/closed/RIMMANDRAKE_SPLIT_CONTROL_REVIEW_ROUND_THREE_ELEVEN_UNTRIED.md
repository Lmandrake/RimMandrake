## spec
Codex's full-file review of the round-two fix be673ed895 (`src/RimMandrake/rimflow/control.py`, `selftest_control.py`;
2026-11-18 ~6:50 PM PST; raw `D:\ClaudeWork\scratch\control_claims_round2_20261118\codex_review_round2_fix.txt`)
REFUSED it with eleven claims. They are Codex's hypotheses, NOT verified here (Codex says it probed 1, 4 and 5 in
isolation on inlined bodies): split first, a red case per claim, as rounds one and two did.
1. (P1) `_admit` deletes the old row before a resource refusal commits: a third admission reuses `run_<unit>`.
2. (P1) a locked-store emergency kill then books an anonymous stand-in when `ended()` landed first: no void, no books.
3. (P1) `stop --idem` replay checked only after BEGIN IMMEDIATE: a locked store kills again; the retry's replay ignored.
4. (P1) `kill_units` final reread `(_procs(cg) or [])` turns an unreadable reread into verified death.
5. (P1) two due escalation timers on one run both call the reaper (reap not gated on the killed transition).
6. (P2) `unit_of` scans payload arguments as systemd options (a payload `--unit x` reads as the unit).
7. (P2) `call_sites` builder branch still accepts a caller function holding any launch_unit call.
8. (P1) `_procs` fallback verification excludes descendant cgroups.
9. (P2) `escalate`: a failed kill retires the cooperative stop order.
10. (P2) hook command construction breaks paths containing spaces.
11. (P2) accepted short deadlines can silently disable escalation.
Acceptance test: none at filing, the claims are unverified; each child carries its own, watched red.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Each of the 11 claims is refuted (evidence noted here) or a closed child whose test failed on base.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
