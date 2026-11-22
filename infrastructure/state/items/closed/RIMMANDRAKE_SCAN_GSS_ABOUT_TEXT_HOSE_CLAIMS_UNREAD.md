# RIMMANDRAKE_SCAN_GSS_ABOUT_TEXT_HOSE_CLAIMS_UNREAD

## spec
found-by: BENCH detached helper RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_SIX_TESTS_FIRST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 6, judge-1794822790, 2026-11-16, code c991553a4f). Class Polish, bar no_hose_in_gss.
Criterion: no shipped text reads as a hose left behind in GSS
Evidence:
- lane2/planted_results.jsonl P05_ABOUT_SAYS_HOSES_SHIP_HERE: About.xml saying 'The flexible hoses and their reels still ship here' stays green under T_NO_HOSE (LANE1 row S_ABOUT_HOSE_ONLY_ELSEWHERE catches it)
- the bar's scenario names defs and C# only, and today's About text says the hoses moved to FlowWorks (lane 1 S_ABOUT_HOSE_ONLY_ELSEWHERE PASS)
Would pass: python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane2/acceptance_polish.py about exits 0
Smallest fix: selftest_gss_no_hose.py scan(): read About/About.xml description sentences; a sentence naming a hose or reel (HOSE_PART) must also name FlowWorks, else hit 'about: <sentence>'; add the P05 text as a mutant
Verdict on the criterion: outside the bar's scenario (defs and C#); Polish

## verify
Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane2/acceptance_polish.py about` exits 0 (1 check).
Watched fail on c991553a4f: rc 1 (T_NO_HOSE stays green with the plant). It restores the planted file byte for byte; `git diff --quiet -- src/RimMandrake/GimmeSomeSlack` after.
