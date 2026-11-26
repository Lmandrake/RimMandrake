# POLISH: maturation.py's stage record (beside `boundary.md`)

Review claims that break no promise on the page and that no ordinary input reaches; one line each.

- `maturation_now`'s run view carries no `token_unit`, so `_spend_row` reads a run's unit from its end time against the
  weighted_v2 switch. Carrying the record's own `token_unit` in the view would make that exact (`_spend_row` already
  takes it when present). `maturation_now.py` is another lane's file (RIMMANDRAKE_FIX_MODLEDGER_CUTOVER_AND_SEAL_EMPTY_SHARD).
- The weighted_v1 history in a stage's `tokens_other` is not converted: its rows name no model (the stage rows before
  2026-11-19 stored none). A conversion would read each run's record for its model (`role_launch.tokens_v2`).
