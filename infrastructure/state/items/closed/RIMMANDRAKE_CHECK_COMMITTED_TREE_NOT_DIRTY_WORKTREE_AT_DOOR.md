## spec
Codex FULL-FILE review 2026-11-18 of `src/RimMandrake/Utils/publish.py` (copy
`D:\ClaudeWork\rimmandrake\lane4_publish_sync\skip_codex.md`, point 4; read, not reproduced): in a full (not sparse)
clone, `tree_checks` and `pipeline_checks` run the tests in the working tree, so an unstaged edit to a test or a file it
reads can make a check green while the committed tree, the thing that lands, would be red. Sparse clones already run
on a full checkout of HEAD (`full_head_tree`).

## verify
Acceptance test: none yet, not watched failing. The builder first writes a selftest_publish_tree_checks.py case: a
configured check that fails on the committed bytes but passes on an unstaged edit of a file it reads; publish of an
unrelated named file must refuse. Weigh the cost first (a HEAD checkout per publish, ~20 s measured for sparse clones).

## criteria
- The door's verdict is about the committed tree, whatever the working tree holds.
