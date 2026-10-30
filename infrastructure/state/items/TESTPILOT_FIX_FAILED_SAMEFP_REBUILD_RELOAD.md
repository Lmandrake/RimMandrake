# TESTPILOT_FIX_FAILED_SAMEFP_REBUILD_RELOAD

Independent check of eb295521da plus blind GPT F1 (part) on src/RimMandrake/Utils/arena/testpilot.py, probe
p_samefp_fail (actions [reload R2, idle], verdict fail, no scenario run). Evidence /mnt/d/ClaudeWork/rimmandrake/arena_testpilot/gpt_blind/ (gpt_round2.md, probes.py, probes_out.txt).

## spec
A rebuild at its parent's own fingerprint is the same artifact: every result at that fingerprint is already its
result. eb295521da resolved such a rebuild with no reload only when every scenario was PASS/carried; with a counted
FAIL it fell through to R2, reloaded, ran nothing and resolved fail. Fix: decide()'s no-game resolve (action
`carry`) also takes a rebuild whose every scenario is counted (pass/fail/carried, none hot-fixed) at its
fingerprint and nothing must run: carry() resolves it through _resolve (verdict fail) with no reload.
Scope: the reload only. F1's other half (a taint note naming an already-passed scenario does not force its re-run
at the same fingerprint) is deliberately unchanged: the parent itself never re-runs a counted PASS for a taint
(_pending), and the same fingerprint has the same evidence; a rebuild that wants it re-run changes the plan entry.

## criteria
- A1 L0: selftest t_samefp_failed_rebuild: a same-fingerprint rebuild of a failed parent resolves fail with no reload and no scenario run (red before: one R2 reload)
