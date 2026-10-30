# ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE

## spec
arena_replay.sandbox_masks() hides bench, foundry, store.git, mirror.git and the D:\ mirror from an arm. It does not hide /home/mandrake/rm/retired-trees/, which since 67094dc0f6 is the census's load-bearing old history: the retired pre-rewrite clones hold EVERY replay task's fix commit, now pinned under refs/arena/old/. An arm sandboxed by that list can run `git -C /home/mandrake/rm/retired-trees/<x>-git-<ts> show <sha>` and read the answer. The list also does not hide D:\ClaudeWork\rimmandrake (notes such as review_debt_* that some task prompts point to). Found 2026-10-30 by the BENCH review of 67094dc0f6 (10-task audit). Audit every arm launcher the same way (arena_judge.judge_masks, the ralph_a/ralph_c/trio/v3 bwrap hide lists): sandbox_masks() itself has no caller, it is a contract.
Derive the mask list from arena_tasks.old_history_repos() so it cannot drift, add the retired-trees root and the ClaudeWork scratch root (but not the arena tasks/events dirs an arm may read), and add a selftest that every old-history repo is masked.

## criteria
Done when: sandbox_masks() includes every old_history_repos() entry and the retired-trees root, a selftest fails if a new OLD_HISTORY_DEFAULT entry is not masked, and an arm-side probe cannot list refs/arena/old/.
