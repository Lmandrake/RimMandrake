# RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING

## spec

WP-09c, corrected by `design/RimMandrake/evidence_gate_enforce_before_deletes_2026-11-06.md` (EVIDENCE_GATE_DESIGN_ENFORCE_BEFORE_DELETES),
which holds the readings and the reasons. The first spec named four guards and licensed each on a shadow reading of 30
closes with 0 disagreements. That reading cannot show the predicate does a guard's job, and no shadow reading speaks for
a warn-only hook.

Delete, one per landing, each with a revert ready:

1. D1: `.claude/hooks/warn_close_live_proof_owed.py`, its `.claude/settings.json` entry and its selftest. Move its line
   from `src/RimMandrake/rimflow/live_baseline.txt` to `src/RimMandrake/rimflow/live_retired.txt`, and fix the inbound
   references the note lists. Licensed by re-reading the count at landing: 0 hand closes naming a debt phrase since
   2026-11-03. A non-zero count stops the landing until those closes are read. The contract carries `--live "once: ..."`.
2. D2: `src/RimMandrake/rimflow/live_proof_lint.py`, after D1. Licensed by `entrypoint_inventory.py` showing no other entry point.

Do not delete:

- Any `cli.py` check (`_close_gate`, `close_refusals`, `_sha_refusals`, `_guard_refusals`, `marker_lock`, `_live_gate`)
  or `model._fold_close_gate`. The record has no entry for them, and hand closes and replays need them.
- `relentless_wall.py` GAP parsing. That reverses the owner's card "Narrow it now", and only a new card from him can.

The enforce flip is EVIDENCE_GATE_FLIP_ENFORCE_AFTER_NOV9, not this item, and neither deletion waits on it.

Done when: D1 and D2 are each in their own commit citing their reading, the false-close and valid-close corpora still
pass (`python3 src/RimMandrake/rimflow/evidence_gate.py corpus check`), and nothing references the deleted files except history.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/redesign_final.md rows 09b, 09c; stage4_log.md
