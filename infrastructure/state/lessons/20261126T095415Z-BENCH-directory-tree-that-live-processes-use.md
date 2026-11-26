A directory tree that live processes use can be renamed under them on one filesystem: os.rename, then a symlink at the old path, in one process. Strings that name the old path resolve through the symlink, and /proc/<pid>/cwd and getcwd show the new real path, so every reader that compares a recorded path with a cwd or with a path from the other era compares realpaths. The pool move of 2026-11-26 needed no quiet window this way.
item: RIMMANDRAKE_RENAME_RUN_STORE_AND_POOL_OFF_TICK_PATH
home: design/specs/2026-11-26-run-root-rename/boundary.md
