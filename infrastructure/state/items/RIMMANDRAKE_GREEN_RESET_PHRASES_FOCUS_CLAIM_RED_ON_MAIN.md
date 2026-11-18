## spec
Two selftests are red on origin/main, found by Lane C (RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_CONDUCTOR) while running `run_selftests.py --only` on everything that imports dispatcher.py; identical on base 0a46880422 in a throwaway `git clone --shared`, so no Lane C change caused them:
- `src/RimMandrake/rimflow/selftest_conductor_reset_mode.py`: 6 FAIL, all "<phrase> is not the switch" ('hold on, one thing', 'are you ready?', 'put it on hold', 'ready to go, do the hose', 'auto mode for pipes', 'holding'): the reset-mode switch matcher now takes ordinary phrases as the switch, or the test's expectation is stale. Under the harness it also runs past 240 s (CRASH timeout).
- `src/RimMandrake/rimflow/selftest_focus_cap.py`: 1 FAIL, "direct claim: the refused claim wrote no event".
Not known whether the code or the test is wrong: read each case's history (`git log -S` on the phrase list and the claim cap) before choosing.

## verify
python3 src/RimMandrake/rimflow/selftest_conductor_reset_mode.py && python3 src/RimMandrake/rimflow/selftest_focus_cap.py

## criteria
- A1: both selftests exit 0 (reset_mode with no FAIL line; focus_cap with no FAILS line).
- A2: a test edited to pass names, in the close note, the ruling or commit that made the old expectation wrong.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_conductor_reset_mode.py; python3 src/RimMandrake/rimflow/selftest_focus_cap.py`, each exit 0. Watched failing on 0a46880422 (2026-11-18 ~2 PM PST): reset_mode exit 1 with 6 FAIL; focus_cap exit 1 with `FAILS: 1`.
