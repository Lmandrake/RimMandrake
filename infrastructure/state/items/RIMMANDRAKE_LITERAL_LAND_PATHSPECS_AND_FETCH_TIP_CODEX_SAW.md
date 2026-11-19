## spec
Codex FULL-FILE review 2026-11-18 of `src/RimMandrake/Utils/land.sh`, run on the fix for
RIMMANDRAKE_SCOPE_LAND_REPLAY_TREE_AFTER_RENAME_MERGE, all three reproduced here [measured]:
(1) `git diff-tree -z | tr '\0' '\n'` lets a path `x<newline>x` pass `covered()` as two copies of a listed `x`
(both the commit's own paths and the merged tree); (2) `git add`/`git rm`/`git ls-tree` read listed paths as
pathspecs, so `land.sh -m ... 'a[1].txt'` also staged and published `a1.txt`; (3)
`UP=$(git rev-parse origin/main 2>/dev/null || git rev-parse FETCH_HEAD)` keeps the failed call's echoed
`origin/main` line, so a clone whose fetch refspec has no origin/main cannot land at all.

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_land.py` prints `ALL PASS`. Its three cases ("a renamed
path holding a newline", "a listed path is literal, never a glob", "a clone with no origin/main") watched FAIL
2026-11-18 ~6:20 PM PST on 8716c3bcd plus the scope/author fix.

## criteria
- No path outside the list is published by either mode, whatever bytes the path holds.
- A clone with no origin/main ref lands on the fetched tip.
