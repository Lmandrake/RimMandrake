# WB-pipeline-operations-20261127-222228

State: complete. 1 of 1 members closed. Nothing is next.

- `OPS_WORKER_CLONE_POOL_RESTORE_HMOQ_PBAL`: class done already. Closed at 207e406f8e.
  - Cause of the 2026-11-27T22:09Z ring (disk.pool_breach = 2): two Codex-lane scratch clones under
    `rm/scratch/UNKNOWN/` kept their staged change after their work units ended `built`. No live seat dir owned
    the clones, so they read stranded one idle hour later.
  - Fix, by the live Operations alarm run `rm-role-operations-1795817498`: ed970cf55b and 207e406f8e. The Codex lane
    frees its `cx-` clone once the patch is saved. da73cbc922 had already moved new clones from seat UNKNOWN to BENCH.
  - Guard: `selftest_codex_lane.py` (`t_the_scratch_clone_is_freed_when_the_patch_is_saved`). It is red on the
    parent's `codex_lane.py` and green on origin/main (10 of 10). The guard event is published in 5b32742fd4.
  - Reading after the fix: Archmagi pool breach 0, stranded [], scratch_stranded [] (2026-11-27 18:11 PST).
- Steps B and C: no member was kept, so no check was written and no code changed in this run.
