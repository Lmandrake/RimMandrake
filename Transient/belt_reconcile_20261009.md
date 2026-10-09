# Reconcile local main vs origin/main, 2026-10-09

Measured after `git fetch` (origin 81efe7a0b). Local `main` has 14 commits not ancestors of origin/main
(`git log origin/main..main`). Nothing was missing; nothing needed re-landing.

## Per commit
- `git cherry` '-' (patch-equivalent already on origin): 8a5f89fd6 (GARDEN_ESCALATION, incl. DivingInteraction DLL),
  cc05f7bca, 66505e779, e67336b95, ef49dce2f, 431026de2, 597a5e11a, 8112c115e, 621a05ce5, e290f9771, a01ae857c.
- '+' (no patch-equiv): 2fb212ce8 (acceptance L1), 0fb7b7eb2 (BENCH shard sync), 10410cc15 (Long Shade ledger).
  Content check: all 7 acceptance Transient files exist on origin; every ledger line these add is already in
  origin's FOUNDRY.jsonl / BENCH.jsonl (0 missing lines each, 10410cc15, 2fb212ce8, 0fb7b7eb2, a01ae857c). Only the
  patch ids differ because the shards were landed via other commits.
- DivingInteraction DLL conflict: tree under `src/RimMandrake/DivingInteraction` is byte-identical between local main
  and origin/main; `dll_source_stamp.py check` reports MATCH for its DLL. No rebuild needed.

## Tree difference main -> origin (non-Transient, non-ledger)
Only: origin keeps 4 stale LIVE copies of `infrastructure/state/items/LONGSHADE_{EMPTY_PATCH_WARNING,LURE_AWNING,STAMPEDE_ROOF,TOLLOK_TICKS}_1.md`
alongside the `closed/` copies (the move landed as add without delete). Local main has them removed (the move).
Owed on origin: `git rm` those 4 live copies (not done here, to avoid touching items peers may edit).

## Safe final reconcile (run only when no helper is mid-edit)
```
cd /home/mandrake/rm/foundry
git fetch origin
git diff --quiet origin/main main -- src infrastructure/state/ledger || echo "STOP: content differs"
# backup branch foundry-unpushed-20261009 already holds old main
git reset --soft origin/main     # moves main, KEEPS working tree and peers' unstaged edits; no checkout
git restore --staged .           # unstage the soft-reset index so nothing is accidentally committed
```
`--soft` leaves the worktree untouched; afterwards `git status` shows only the intended local edits and
`git pull --rebase origin main` works again. (Plain `reset --hard` is NOT needed and must not be used.)
