## spec
./publish from a sparse pool clone (scratch_clone.py's default cone) refused on 7 whole-tree checks that could not see the
files they read (src mods, design/ records: lessons 20261115T194926Z and 20261115T195130Z); three helpers got past by hand
on 2026-11-15 (sparse-checkout disable, RM_PUBLISH_SKIP_TREE_CHECKS twice). Other checks went green blind (git grep skips
out-of-cone files). Fix at the cause: publish.py tree_checks() detects a sparse clone (skip-worktree entries) and runs the
checks on a throwaway full checkout of HEAD (`git clone --shared` inside the clone's git dir, removed after), so the commit
being pushed is what is checked. GIT_WORKFLOW.md and publish_tree_checks.json say a sparse clone needs no bypass.

## criteria
A1 L0: selftest_publish_tree_checks.py sparse_cases: a sparse git fixture whose check joins an in-cone list with an
out-of-cone record passes on a clean HEAD (red blind on the base commit) and refuses a violation committed in the cone; no
check tree is left in the git dir.
A2 L1: a real ./publish from a default sparse pool clone lands with no env override and no un-sparsing; a planted
violation committed there makes the same ./publish refuse naming the check.
