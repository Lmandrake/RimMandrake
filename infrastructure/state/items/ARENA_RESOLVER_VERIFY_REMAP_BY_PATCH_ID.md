# ARENA_RESOLVER_VERIFY_REMAP_BY_PATCH_ID

## spec
arena_tasks.Resolver maps a pre-rewrite close sha to the one current commit that has the same (author date, author, subject) triple. That triple is not unique in the old history. Measured 2026-10-30 with `git log --all` and `uniq -d`: duplicated triples number 10047 in mirror.git, 10619 in retired-trees/bench-git-20261029062325 and 10208 in retired-trees/foundry-git-20261029053023. Most of these are probably rebased copies of the same change. An excised commit that shares its triple with a surviving commit of different content would still remap to that survivor, and the task would get the wrong fix and base. GPT second read, finding 2.
Add a content check after the triple match: the `git patch-id --stable` of the old commit's diff, with excised paths removed, must equal the remapped commit's. Otherwise reject with "remap content differs". Measure how many of the 241 pool tasks change.

## criteria
Done when: a fixture pair with the same triple but different content is rejected, the real-pool delta is reported, and selftest_arena_tasks passes.
