# Git reconcile 2026-10-05

Cherry-picked 17 bench '+' commits (oldest first) onto origin/main cb40b829e in a scratch clone.
- Empty (content already on origin, skipped): 101aa2013, 9e705a989, 93669c1a2, b2e7592f5, e5ab82d21.
- Landed: a774c7ce1 (one conflict), 0940542db, 50c15f19d, 546f90755, 4120d38dc, 6e2e36064 (one conflict), a982f6bb4, 1b57b91b9, b933de948, f934ab4ee, 4c9762722, 5e0bf5cb7.
- Calls: gelatinousslime snapshot.json -> origin's (c46bfc123, 20:26 vs 19:20). abyss_sitting2_close_progress md -> origin's (586d7bcc3, 20:39 vs 20:36; carries the later "old singles stay" correction).
- Check: every non-ledger file the 17 commits touched is byte-identical to bench HEAD; ledger shard lines are a superset. ledger_lint: 0 findings.
