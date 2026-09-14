# MIGRATE_NAMES_BATCH_MV_1 — batch migrate_names.py's folder renames

## spec
`src/RimMandrake/Utils/migrate_names.py`'s `stage_folders()` ran `git mv`
once per row of `naming_rename_map.csv` (~71 `mod`-kind rows) against the
SHARED repo (`cwd=ROOT`) — 71 serial git spawns, each touching the shared
index, with real index.lock collision exposure against a live agent's own
add/commit landing between rows. Flagged as "the only finding with real
cross-agent exposure; fix before NAMING_SCHEME_EXECUTION runs it at scale."

## what changed
`stage_folders()` now does the filesystem move itself (`Path.rename()`, no
git needed for that part) for every row, then stages ALL of them in exactly
two git calls: `git rm -r --cached --quiet -- <old paths...>` followed by
`git add -- <new paths...>` — both with fully explicit pathspecs, never
`-A`/`.`/`-u`. The item's own suggested fix text ("ONE batched `git add -A
<explicit-paths>`") does not survive contact with this repo's own guard:
`.claude/hooks/block_blanket_git_stage.py` blocks any `git add` command
containing a bare `-A` token at all, pathspec attached or not — so the
`rm --cached` + `add` pair is the compliant equivalent, not `-A` scoped by
paths.

Verified in a throwaway repo (not this one — the hook fires on ANY `git add
-A`/bare `git commit` regardless of which tree, by design) that the
resulting index state is indistinguishable from `git mv`:
`git status --short` reports `R  old/file -> new/file` for every moved file,
and `git diff --cached --stat -M` shows clean renames with zero content
diff. Working tree left with no unstaged difference from the index.

Ran `--stage folders` (dry run) against the live map afterward: all 71 rows
report `SKIP (missing)` — every one was already migrated in an earlier pass,
so this repo has no live folder-rename left to prove `--apply` against
end-to-end; the throwaway-repo test above is the functional verification.

## verify
`python3 -m py_compile src/RimMandrake/Utils/migrate_names.py` — clean.
`python3 src/RimMandrake/Utils/migrate_names.py --stage folders` (dry run)
— runs without error, same SKIP output as before the change (no rows to
move currently, so behavior on the live map is unchanged).
Throwaway-repo functional test (see above) — git status confirms correct
rename staging with the new two-call approach.

## criteria
No `git mv` spawn per row; folder-rename staging happens in at most 2 git
calls regardless of row count; every path passed to git is explicit (no
`-A`/`.`/`-u`); dry-run output and skip behavior unchanged.
