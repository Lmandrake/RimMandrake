# LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST

## spec

The supervisor's tick starts a paced live round (`relentless_live_round.py round`, rules `live.*` in
relentless_rules.json). A round runs only the criteria that have a proof line in the item's prose:

    live-proof A2: python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_PaleMoss

Nothing turns a criterion's English into a proof, so each line is written by hand. The worked example is
items/EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS.md. Make the def resolve first (live_def_check.py --has), so a log silent
about a def the load never had cannot pass.

The scan of 2026-11-01 (D:\ClaudeWork\rimmandrake\RA_S09\scan.json) found 34 built items with 52 live-level criteria
on clean game files that are not cut and not about a flyer. Start with those. `relentless_live_round.py eligible`
prints what a round would run now and why the rest wait.

## Watch out

- The exit code is the verdict: 0 PASS, 1 FAIL, anything else UNMEASURED. A proof that cannot see what it judges must
  exit 2, never 0.
- A FlowWorks or Gimme Some Slack item is FOUNDRY's, and the round skips it.
- A proof line only reads. It never swaps the mod list, applies a deploy or changes game state (rules live.forbid_re).
