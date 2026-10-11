# 22 — clone2 diff vs origin/main, then cleanup (2026-10-11)

Status: DONE. Owner (typed): "(2) then clean it up. No residual trash."

## Commit classification (66, merge-base e0c6f6dd4..efe67213ab)
Method: every blob each commit wrote was looked up in origin/main's full object set, and each subject matched against origin's 1,371 commits since the merge-base.
- LANDED 65: an origin commit carries the identical subject, and every blob they wrote exists on origin.
  The only blob misses were the two append-only jsonl shards (rewritten in another order on origin). All 204 FOUNDRY ledger lines and the 1 BENCH line are present at origin.
- 87aef7bd88 "LongShade second pass clean marks; Slack matrix imports its own scenes; drop 5 stale placeholder entries"
  LANDED as 90a537fafc (clean marks + allowlist), without its sys.path reorder in 7 northstar_matrix modules.
  SUPERSEDED-ON-PURPOSE: a6c8d2de12 fixed the same Utils/scenes shadowing at the entry points (design_spec, matrix, proof_all). Matrix selftest passes 58/58 at origin.
- NEVER-LANDED (lost after landing): 90a537fafc's 7 LongShade clean records were erased one minute later by 2fec559019, a FOUNDRY.jsonl rewrite from a stale copy (its subject is about other files, so this was not deliberate).
  5 of the 7 files are byte-identical to the reviewed version, so they were re-recorded with `code_review_status.py mark-clean --sha 90a537fafc`: RM_LongShadeMapgen, RM_Patch_DewfringeWildSpawnGate, RM_ShipfallCommons, Kernel/RM_LongShadeKernel, SelfTest/Program. RM_ShadeExtras.cs and SelfTest/LongShadeFuzz.cs changed since then, so they are DIRTY.

## 12 differing files
- 9 item .md files (the "8" was 9): all are now in origin's items/closed/, and the clone's text is in origin's history. They are superseded by closure.
- 4 matrix .py files (det_export, fakegame, oracle, placer): differ only by the sys.path reorder above. Superseded.
- The ~80 other diverged files were all changed again by later origin commits. Every clone2 version exists in origin history.

## Deleted
- /home/mandrake/.seat-tmp/clone2 (no process had its cwd inside it)
- rescued/clone2/clone2_main_unlanded_66_commits.bundle (git rm)
- rescued/sitting3_clone/ModsConfig.before-tier-acc_20261009c.xml (git rm). Its 58 mods match no tracked sibling, but `modset_builder.py --tier acc_20261009b` regenerates the list to within 1 mod, so it is a derived artifact. It was not moved into deployed/config/, because modset_builder --restore compares against the newest before-tier-* by mtime.
