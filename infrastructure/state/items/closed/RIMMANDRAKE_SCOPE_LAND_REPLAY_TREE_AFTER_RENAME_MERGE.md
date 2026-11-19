# RIMMANDRAKE_SCOPE_LAND_REPLAY_TREE_AFTER_RENAME_MERGE

## spec

Codex full-file review 2026-11-18 of src/RimMandrake/Utils/land.sh (D:\ClaudeWork\rimmandrake\lane_e\land_views_codex_review.md point 2), read not reproduced: the replay's scope check accepts the commit's own paths, then git merge-tree (rename detection on) may apply a change to allowed path a onto upstream's renamed b, an unlisted path, and the result is committed and pushed with no second scope check.

## verify

Acceptance test (drafted, NOT yet watched failing): a bare origin where upstream renamed a to b after the base; land.sh -m with path a modified: refused or the published tree changes only listed paths. Watch it fail on the base first; drop if git does not carry the change.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
