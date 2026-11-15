# RIMMANDRAKE_ALIGN_BLIND_BRIEF_EXIT_WITH_JUDGE_OWED_READER

## spec
`maturation.blind_brief_text` told the blind judge "A Problem FIXED red-first is closed", so ExplosiveKnockback cycle 3's
judge wrote `exit_met: true` after fixing 3 Problems, while the exit reader (RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE,
the owner's road back: "send it back to just before Stage 4 again for a new blind judgement pass") reads the same cycle
as not met. Evidence: `design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_3/SUMMARY.md` §Owed. Fix: the
brief's exit paragraph says a cycle's own fixes owe a new blind judge and such a cycle writes `exit_met: false`.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_blind_brief_exit_owed.py` — FAIL 3 on the base commit
(watched), PASS 1 after the fix.
