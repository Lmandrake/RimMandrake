# LEDGER_CANNOT_BE_COMMITTED_1 — the ledger guard blocks every commit of the ledger

## spec

`.claude/hooks/queue_lint.py:157` denies any git-commit command that names the ledger
file while that file has uncommitted changes. Since committing the ledger is by
definition committing a changed ledger, the guard fires on **every** legitimate commit,
not only on hand-edits. `changed()` cannot tell a `rimflow` append from an editor write,
and the rule is written as if it could.

⚠️ **It is worse than that: the check is on the command TEXT.** Any command whose text
merely mentions the ledger path alongside the words git and commit is refused — this
item's own spec had to be written with the dedicated Write tool because a heredoc
quoting the failing command tripped the guard.

Consequence: the ledger — now the single source of truth for 144 items and 358 events —
has been committed twice ever (`ecee610`, `d5110f1`) and cannot be committed again. It
lives on one disk, which is the exact failure the owner's standing push-immediately rule
was written after.

Reproduced 2026-08-21 06:41 by REP, with five pending seat-ready appends.

The guard's *intent* is right — the advisory `flock` does not protect against an editor,
and unlocked concurrent writes measurably tore the file on this mount. What is wrong is
the enforcement point: **committing is not writing.** Block the WRITE (Edit/Write, and a
shell redirect targeting the ledger), and leave the commit path alone.

## verify

- Committing the ledger succeeds with a pending append.
- An `Edit`/`Write`/`>>` against the ledger is still refused.
- A command that only *mentions* the path in prose is not refused.
- `.claude/hooks/selftest_queue_lint.py` passes, with a new case per branch.

## criteria

The ledger can be pushed after every turn, and no path that bypasses `rimflow` can write
it.
