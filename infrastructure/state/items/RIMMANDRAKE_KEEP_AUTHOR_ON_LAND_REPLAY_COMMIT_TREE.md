# RIMMANDRAKE_KEEP_AUTHOR_ON_LAND_REPLAY_COMMIT_TREE

## spec

Codex full-file review 2026-11-18 of src/RimMandrake/Utils/land.sh (D:\ClaudeWork\rimmandrake\lane_e\land_views_codex_review.md point 3), read not reproduced: in the replay branch the GIT_AUTHOR_NAME/EMAIL/DATE assignments prefix the git show side of a pipeline, so git commit-tree (the right side) gets none of them; a replayed commit carries the landing clone's identity and the replay time instead of the original author.

## verify

Acceptance test (drafted, NOT yet watched failing): replay a commit authored by X at time T through land.sh's non-fast-forward branch; git log -1 --format=%an%ad on origin shows X and T. Watch it fail on the base first.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
