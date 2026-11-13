# RIMMANDRAKE_STORE_TEXT_WHOLE_FINISH_LEFTOVERS

## spec

What RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS left undone (owner, 2026-11-12: "WHY would anything cut off text at 600
characters?! please get rid of these arbitrary cuts!"). Census: D:\ClaudeWork\rimmandrake\refusal_contract\truncation_census.md

1. Twelve bare cuts in the four files the refusal-contract T1-T3 helper owned at the time (not edited, by brief):
   designer_stage.py 1270, 1373, 1579, 1604; coverage_judge.py 335, 389; refusal_contract.py 98;
   evidence_gate.py 117, 495, 669, 686, 718 (line numbers as of 2026-11-12). Store them whole (or `fulltext.fit`
   where a real bound exists), then drop those four names from `SKIP` in
   src/RimMandrake/rimflow/selftest_no_bare_cuts.py so the lint covers them.
2. Two-digit slices (`[:80]`) are not caught by the lint; about 297 in rimflow (most are ids, slugs, hashes).
   Classify them, fix the text ones, and extend the lint's regex.
3. The ~240 files changed by the sweep are DIRTY in code_review_status (mechanical edit, never reviewed): review
   and mark clean.
