# Polish: the door's read records (page: boundary.md beside this file)

- `src/RimMandrake/Utils/publish.py` `_changed_since_origin`: `git diff --name-only` follows renames, so a `git mv a.py b.py` names only `b.py` (measured 2026-11-27, git 2.53). risk: a test whose code still imports `a` goes red on main, and the door leaves it out: the import closure, read on the new tree, cannot resolve `a`, so it names neither path. `--no-renames` alone does not close it (the read records only narrow what the closure names); the closure would also have to keep a test whose import no longer resolves.
