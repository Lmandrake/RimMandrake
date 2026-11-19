## spec
Codex's full-file review of the round-three fix 53cb713db1 (`control.py`, `selftest_control.py`; 2026-11-18 ~7:35 PM
PST; raw `D:\ClaudeWork\scratch\control_claims_round2_20261118\codex_review_round3_fix.txt`) REFUSED it with fifteen
claims (8 REPAIR: in the fixed lines; 7 NEW: outside them). The findings count has risen across rounds (9, 11, 15)
while most are P2 edge cases: see the owner question below before another full round.
Fixed in the same run, tests red on 16ded1e1fb and green after (`t_review_round_four_p1`): #1 a later kill of a killed
run reaps it again; #2 `pipe stop <unit>.service` misses the run and its claude scope; #3 `_sr_unit` option arities
(attached -uNAME, --root-directory, operand-free --on-clock-change/--on-timezone-change, last --unit wins); #11 doctor
reports OK on a failed quick_check; #12 `pipe off` says "no run is live" when it could not read the runs.
Still unverified, NOT fixed (Codex's hypotheses: split each with a red case first):
4. (REPAIR P2) `_procs`: os.walk ignores scandir errors, so an unscannable cgroup dir reads [] / a subtree is skipped.
5. (REPAIR P2) census alias propagation ignores annotated assignments (`alias: list = argv`).
6. (REPAIR P2) a builder call inside another builder is exempt without checking where its argv goes.
7. (REPAIR P2) a failed escalation can put back an order after another kill finished the run.
8. (REPAIR P2) systemd expands `${...}` in ExecCondition/ExecStopPost paths (needs the `:` prefix or escaping).
9. (NEW P2) void before reserve: the reservation is accepted, then settle and void both return early: a stranded hold.
10. (NEW P2) a new owner hold, same mod and date, different words, after a lift is not imported (idem key lacks words).
13. (NEW P2) `_stage_advanced_on_voided` matches run ids by substring (rm-probe-1 in rm-probe-10).
14. (NEW P2) t_verbs p95 can approve a slow verb (Codex's text: see the raw file).
15. (REPAIR P2) new tests can pass while the advertised behaviour fails (see the raw file).
Owner question already open (the Conductor's note, 2026-11-18 6:54 PM PST): apply "one inspection, one repair check" to
Codex code reviews, outside findings to a next-version list. Until he answers, these stay as filed claims.
Acceptance test: none at filing, the remaining claims are unverified; each child carries its own, watched red.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Each remaining claim is refuted (evidence noted here) or a closed child whose test failed on base.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
