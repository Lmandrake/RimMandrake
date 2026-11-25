# Polish: ./publish's kept check tree (a record; nobody takes lines from it)

- `split_pre_existing` still makes two fresh trees (HEAD's commit and the base) inside the pipeline checks' kept tree; a second kept slot would spare them, at 4.6 GB more a clone. 2026-11-25.
- The kept tree's own `.git/objects` keeps any object a check run wrote there (a `git fetch` inside the tree, as in bench's leftover of 2026-11-24); nothing prunes them. 2026-11-25.
- `scratch_clone.py` is not a pipeline file, so a change to `shed` does not run selftest_treecheck_kept at the door; making it one first needs its 6 could-not-look places and 8 unnamed budgets answered. 2026-11-25.
