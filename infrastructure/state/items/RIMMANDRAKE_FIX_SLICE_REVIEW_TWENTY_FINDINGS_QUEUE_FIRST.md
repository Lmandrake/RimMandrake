## spec
Codex's full-file review of slices 2-4 (control.py, pipeline_control.py; commits c180799371, 16ded1e1fb, 1b79ae76b0,
9a8593dc91; 2026-11-18 ~8:10 PM PST; raw `D:\ClaudeWork\scratch\control_claims_round2_20261118\codex_review_slices.txt`)
REFUSED them with twenty findings. Findings 1-6 (queue membership on move, add order, dropped listing, non-mod scopes,
the base list, add clamped at zero) reproduced on 1b79ae76b0 and are fixed in this run (t_slices_review). The other
fourteen are Codex's hypotheses, NOT verified here: split each with a red case first.
7. NEW — Typed counts cannot override existing reservation charges.
8. CHANGE — Undoing a look grant reports the wrong balance.
9. CHANGE — Reimporting a changed legacy balance adds it twice.
10. CHANGE — Failed counter migration leaves the new readers enabled.
11. NEW — Legacy undo reports success without changing the active control state.
12. CHANGE — A concurrent permit sync can undo `off all` containment.
13. CHANGE — Several global switch mutations never update the permit.
14. CHANGE — Stripping `.service` breaks runs recorded with that suffix.
15. CHANGE — The new terminal flag can suppress necessary killed-run cleanup.
16. NEW — Cgroup traversal errors can become “nothing was running.”
17. NEW — Doctor can report success while every write is locked out.
18. NEW — The retained pipeline-control entry point reports stale queue state.
19. NEW — The retained switch command can claim ON under an owner hold.
20. NEW — Grant commands have the same non-mod scope conversion defect.
Owner question open (the Conductor's note, 2026-11-18 6:54 PM PST): apply "one inspection, one repair check" to Codex
code reviews, outside findings to a next-version list.
Acceptance test: none at filing, the claims are unverified; each child carries its own, watched red.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/pipeline_control.py

## criteria
- Each remaining finding is refuted (evidence noted here) or a closed child whose test failed on base.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control,selftest_pipeline_control
