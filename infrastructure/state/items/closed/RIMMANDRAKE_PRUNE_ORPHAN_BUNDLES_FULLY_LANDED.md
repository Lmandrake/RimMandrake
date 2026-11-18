# RIMMANDRAKE_PRUNE_ORPHAN_BUNDLES_FULLY_LANDED

## spec

relentless.bundle_clone writes a bundle for every returned pool clone that held anything
(/home/mandrake/rm/relentless/store/orphans/bundles/<stamp>-<ITEM>/) and nothing pruned them: 359 entries, 7.9 GB on
2026-11-16 08:50 PST. `src/RimMandrake/Utils/orphan_bundles.py` judges each bundle against origin/main by content
(tracked edits reverse-apply or their post-image blob is in origin's history at that path, or for append-mostly files
every added line is in origin's file; untracked files' bytes are in origin's history or now ignored; each commit's
post-image the same way; ignored.tar is derived) and `prune --apply` deletes only LANDED bundles. scratch_reap.py's
hourly real run (rm-scratch-reap) now calls it and records the result as `orphan_bundles` in last_run.json.
First prune 2026-11-16: 306 deleted (4.23 GB); left 27 UNLANDED, 24 UNJUDGED (17 older format without
real_untracked.tar, 3 with a `carry` member), 3.9 GB. Lists:
D:\ClaudeWork\rimmandrake\conductor\orphan_bundles_prune_20261116.txt and .json. The 27 UNLANDED are mostly derived
(ModsConfig snapshots, a Pyrelands DLL, blind-challenge baselines, Transient PNGs, CONDUCTOR_ADDENDUM_READ_ME.md);
the ones that may be real work: 20261116T004959Z (designer_stage.py edit), 20261116T080058Z (maturation_dispatch.py
commit f5e43d59fd), 20261115T220750Z (selftest_graffiti_raid_tag_wall.py), 20261116T135004Z
(RM_KnockbackProof_StageThree source), 20261113T* d86f682b5e (a CLAUDE.md edit carried by 6 bundles).

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_orphan_bundles` (1 test): six fixture bundles, two
must stay. Watched red with the judge mutated to call everything landed (3 FAIL); green as built.

## criteria

- Only bundles whose work origin holds in content are deleted; UNLANDED and UNJUDGED are listed, never touched.
- The hourly reap prunes, so the store stops growing with landed work.
