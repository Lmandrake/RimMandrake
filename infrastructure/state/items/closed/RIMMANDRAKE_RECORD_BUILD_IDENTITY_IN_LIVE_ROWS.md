# RIMMANDRAKE_RECORD_BUILD_IDENTITY_IN_LIVE_ROWS

## spec
Found while building `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO` (his ruling of 2026-11-17: a verdict whose
mod hash or game build differs from the build he walks does not count; its line item is re-run). The Stage 6 exit now
runs `src/RimMandrake/rimflow/build_match.py`, which needs every in-game row to carry `mod_hash`, `game_build`,
`active_mods`, `tier` or `full_list`, and `unit`: the JSON line `build_match.py identity --mod <Mod> --tier <T>` (or
`--full`) prints. The in-game brief in `maturation.py` tells the runner to merge it. Nothing else does yet:
- the SteveDesktop test queue jobs (`src/RimMandrake/Utils/testq/`) write no identity fields;
- every existing visit's rows (Gimme Some Slack, Pyrelands, FlowWorks, Explosive Knockback) lack them, so
  `build_match.py check --mod <Mod>` reads every check "re-run it" (measured on Gimme Some Slack:
  `D:\ClaudeWork\rimmandrake\conductor\bm_live_check_gss.txt`). That is as ruled, not a defect.
- no stage-6 test in Pyrelands' test table (45 checks) declares `tier` or `why_full_list`, so each is read as a
  minimal-list test whose tier comes from its row.

Work: make the queue runner and any scripted in-game driver call `build_match.py identity` after the deploy and the
list swap and merge it into each row; make the test-table makers write each stage-6 check's `tier` (or
`why_full_list`).

## verify
A queue job run offline on a fixture writes rows that `build_match.py check` counts; a row written before a redeploy
reads "re-run it".

## criteria
- every row a live driver or queue job writes carries the fields `build_match.py identity` prints;
- each stage-6 check in a test table declares `tier` or `why_full_list`.
