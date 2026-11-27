# POLISH: maturation.py's stage record (beside `boundary.md`)

Review claims that break no promise on the page and that no ordinary input reaches; one line each.

- The weighted_v1 history in a stage's `tokens_other` is not converted: its rows name no model (the stage rows before
  2026-11-19 stored none). A conversion would read each run's record for its model (`role_launch.tokens_v2`).
- `src/RimMandrake/rimflow/maturation.py` (`advance` on the command line): a move made with `--per-ruling` and no
  `--owner-said` stores the text "per-ruling <ID>: <why>" in the move's `confirmed.owner_said`, and the journal prints it
  under "Owner said:". The text is the helper's own why, not his words. Store it under its own key (`per_ruling`) and
  print "Per ruling:". risk: the exit clauses and the pass record read `confirmed.owner_said` of a move; a move by a
  ruling that the Conductor made could then stop reading as authorized.
