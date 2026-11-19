## spec
Codex FULL-FILE review 2026-11-18 of `src/RimMandrake/Utils/publish.py` (copy
`D:\ClaudeWork\rimmandrake\lane4_publish_sync\skip_codex.md`, point 3; read, not reproduced): when a door check is red,
`_publish` runs `git reset --soft <made>~1` without checking HEAD is still `<made>`. The publish lock does not cover a
plain `git commit`, so a peer commit B made on top of this run's commit A during the checks is taken off the branch
with A (its changes stay staged, its commit is gone).

## verify
Acceptance test: none yet, not watched failing. The builder first writes a selftest_publish.py case: a door check
that makes a commit on top of HEAD and then fails; assert the peer commit is still on the branch (or the refusal names
it and leaves HEAD alone). Fix shape: `git update-ref HEAD <made>~1 <made>` (expected-value update) instead of a bare reset.

## criteria
- A refused publish never removes a commit it did not make.
