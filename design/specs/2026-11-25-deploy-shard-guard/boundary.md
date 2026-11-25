# BOUNDARY — Missing ledger shards and stale deploy locks

Code: `src/RimMandrake/rimflow/model.py` and `src/RimMandrake/Utils/ops_core/deploy_update.py`.
Tests: `src/RimMandrake/rimflow/selftest_ledger_sparse_deploy.py`.

## ACCEPTS

- Implicit seat-shard appends, including a first append to a new seat and a ledger outside a Git worktree.
- Updates of the dedicated Linux deploy checkout with a regular `.git` directory.

## DOES NOT SURVIVE

- The shard guard needs a readable Git index to identify tracked files. If Git is missing, an implicit append can
  still create the file.
- Lock recovery can only see the file descriptors exposed to the updater by Linux `/proc`.

## PROMISES

- **implicit-append-preserves-tracked-history.** If a sparse checkout omits a tracked shard or a full checkout has
  lost it, an implicit append raises a ledger error naming the checkout and leaves the shard absent. Appends to
  existing shards skip the Git check. Implicit appends can create new untracked shards or write outside a worktree.
- **deploy-recovers-abandoned-index-lock.** Before the pull, the updater clears an index lock older than its pass
  budget if no process holds it open and returns its age in seconds as `cleared_lock`. Fresh and held locks stay on
  disk and Git still reports a blocked pull.
