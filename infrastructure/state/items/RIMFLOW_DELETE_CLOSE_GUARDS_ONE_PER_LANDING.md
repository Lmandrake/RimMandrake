# RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING

## spec

WP-09c: delete the old close guards (cli.py, relentless_wall.py GAP parsing, the .claude/settings.json hook, Utils/live_proof_lint.py), one guard per landing, each only after the evidence_gate shadow predicate (WP-09b) shows 30 closes with 0 disagreements on the corpus plus the shadow sample. Serial, wave E; each landing has a revert ready.

Done when: every old guard is deleted in its own commit that cites the evidence_gate shadow reading (>=30 closes, 0 disagreements) and the false-close and valid-close corpora still pass.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/redesign_final.md rows 09b, 09c; stage4_log.md
