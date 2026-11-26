The pre-push hook refuses an item spec (infrastructure/state/items/<ID>.md) whose ledger row is not in the same push: rimflow file the item BEFORE the first ./publish that carries its spec, and name the seat shard in that publish. Write a new item's prose file only together with its rimflow file.

- Before 2026-11-15 publish retried that refusal and showed only 'failed to push some refs'; git push --dry-run printed the reason.
- 2026-11-22, sweep of ExplosiveKnockback: the push guard refuses a commit that holds infrastructure/state/items/<ID>.md with no ledger row ('no ledger row at all'), and a ./publish of two new prose files then waits until BOTH ids are filed. Order: write the prose, run 'rimflow file <ID> --spec <that path> --publish' per id, then publish other docs.
item: RIMMANDRAKE_SWEEP_KNOCKBACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE
home: skills/using-rimflow/SKILL.md
