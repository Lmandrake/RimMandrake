git apply --cached --unidiff-zero with filtered -U0 hunks (only my lines from a shared dirty file) inserts them at the NEW-side line numbers of the full worktree diff, i.e. at wrong positions in the index blob. For partial commits of a shared file, build the blob by inserting after anchor lines in a temp index (GIT_INDEX_FILE) and assert it against the worktree.
home: git-efficiency
