# RIMMANDRAKE_TIGHTEN_SHADOW_ACCEPT_FOUR_CLAUSES_PASS_ON_LESS

## spec
Codex's full-file review of `src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py` (2026-11-18, evidence
`D:\ClaudeWork\rimmandrake\lane_a_20261118\criteria_fixes_codex_review.md`) found four clauses that pass on less than
they state. The build they guard meets the strict form (measured 2026-11-18): only the test is lenient.
1. "detached_helper.launch runs the preflight" checks the text `ticket_preflight` in `launch`: an unused import passes.
   Require a call to `ticket_preflight.<attr>(...)` inside `launch`.
2. "the start event carries preflight_run" does not check `preflight_ms` (the claim clause does). Require it numeric.
3. The planted clause counts any `group` label: ten rows labelled `invalid_0..9` pass. Count only groups A-I.
4. "per-door timing" passes with one door. Require the file, claim, start and helper_launch doors.
Same 21 clauses; no clause is removed or loosened.

## verify
`python3 src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py` still reads `PASS 21/21` on main, and each of
the four mutations reads below 21 (watched): `launch` with only an unused import; a start event without preflight_ms;
planted groups relabelled `invalid_N`; a timing table with only `claim`.

## criteria
- each of the four clauses fails on its mutation
- the unmutated build still reads PASS 21/21

## refs
file: src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py
