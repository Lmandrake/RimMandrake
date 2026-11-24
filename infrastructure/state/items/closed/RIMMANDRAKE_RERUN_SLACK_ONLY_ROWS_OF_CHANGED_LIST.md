## spec
Gimme Some Slack (Design Version 0.2.0). Rank 6 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` sections 7 and 9; analysis.md had it as rank 7, a numbering error fixed 2026-11-24; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness change only: no mod bar moves.

**Measured:** the proof ran twice, on two mod lists. `runC` (110 rows) on the 12-mod list took 259 s; `runE` (the same 110 rows) on the 13-mod list took 609 s. `runB` and `runF` (62 rows) took 169 s and 163 s. The second run read 106 rows the first had already read; the one-page figure is 172 proof rows run again. The table gives only 4 scenes to the 13-mod list (`sc_true_to_grid`, `sc_cords_under_items`, `sc_shock_reach`, `sc_settings`), plus the 2 FlowWorks rows that read UNMEASURED on the 12-mod list. Saved: about 11 min a visit, about 100 s left [guess ~65%]. [measured, times and counts]
Build: medium, and no scene-library part is needed: a row filter in `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py`, which today selects only by block (`--only`, "a PARTIAL run, for debugging"). A partial run writes mode "partial", so the record must say which rows it read and which it left to the earlier full run.
Cost named by the study: if the 13-mod list breaks something else, only the 12-mod run or the walk finds it. Which rows still pass after the filter: shown by no run (UNMEASURED).
Files: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py`, `design/concepts/GimmeSomeSlack/version/test_table.json` (which scenes belong to which list). Library part waiting: none.

**Recommendation: current Design Version** (harness only; about 11 min per full visit that changes the list). The Conductor decides.

## verify
Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_RERUN_SLACK_ONLY_ROWS_OF_CHANGED_LIST.acceptance.sh`
- WATCHED FAIL today (2026-11-24): `proof options read 13; row/scene filter none (needs --rows or --scenes, our own rule); changed-list scenes in the table 4 of 4`, exit 1. `--selftest` prints SELFTEST OK (6 cases: block-only -> red; --rows -> green; --scenes -> green; a scene lost from the table -> could not look; no parser -> could not look; unreadable file -> could not look). Watched green.
- It is a PROXY (an option exists). UNRUN, live (needs the 13-mod list and a game): `python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --rows <the rows of those 4 scenes>` must read the 4 scenes and the 2 FlowWorks rows (6 reads) and the run record must name the rows it left unread. Empty selection must read "could not look", not PASS.

## criteria
- The acceptance script exits 0 AND the live filtered run reads exactly the changed list's scenes with the unread rows named.
