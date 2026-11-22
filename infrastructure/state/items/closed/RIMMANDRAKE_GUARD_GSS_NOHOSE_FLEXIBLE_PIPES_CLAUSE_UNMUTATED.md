# RIMMANDRAKE_GUARD_GSS_NOHOSE_FLEXIBLE_PIPES_CLAUSE_UNMUTATED

## spec
found-by: BENCH detached helper RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_SIX_TESTS_FIRST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 6, judge-1794822790, 2026-11-16, code c991553a4f). Class Polish, bar no_hose_in_gss.
Criterion: T_NO_HOSE can fail: every clause of its scan is guarded by a self-mutant that goes red when the clause is lost
Evidence:
- lane2/planted_results.jsonl P15_DECIDER_FORGETS_FLEXIBLE_PIPES: MISSED (dropping \bflexible pipes?\b from CLAIM leaves all 25 of its PASS lines PASS)
- M20 plants 'Drawn flexible hoses', which \bhoses?\b still catches, so the 'flexible pipes' clause (cycle 5's fix for the header) has no mutant of its own
- today the decider does catch the real header regression: P03_HEADER_FLEXIBLE_PIPES_BACK CAUGHT by NOHOSE
Would pass: python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane2/acceptance_polish.py flexible_pipes exits 0 (planting P15 turns T_NO_HOSE red)
Smallest fix: src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py: add mutant M21_planted_settings_text_flexible_pipes writing 'const string H = "Drawn flexible pipes and wires to better display simple circuit-like plans underneath.";' and expecting 'text: Drawn flexible pipes'
Verdict on the criterion: criterion sound; the bar is met today, the test's self-check is one mutant short (Polish: no player-visible effect, no wrong verdict today)

## verify
Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane2/acceptance_polish.py flexible_pipes` exits 0 (1 check).
Watched fail on c991553a4f: rc 1 (T_NO_HOSE stays green with the plant). It restores the planted file byte for byte; `git diff --quiet -- src/RimMandrake/GimmeSomeSlack` after.
