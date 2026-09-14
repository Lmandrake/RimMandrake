# CODE_REVIEW_STATUS_MIGRATE_BATCH_1 — batch migrate-hashes' git show calls

## spec
`code_review_status.py migrate-hashes` (lines ~783-795, one-time backfill of
`{hash}` onto pre-rewrite entries) ran `git show sha:path` once per entry
needing a hash. One-time migration path, low priority — filed for
completeness, collapse to one `git cat-file --batch`.

## what changed
Added `_batch_cat_file(specs)`: takes a list of `sha:path` object
specifiers, writes them all to a single `git cat-file --batch` subprocess on
stdin, and parses the batched output (binary-safe — reads the declared byte
count per object rather than splitting on newlines, since a PNG's own
embedded newlines would otherwise desync the parse; a `missing` line marks
an unresolvable spec). `cmd_migrate_hashes` now builds every entry's `sha:rel`
spec up front and resolves them all in one call instead of one `git show`
subprocess per entry.

## verify
`python3 -m py_compile src/RimMandrake/Utils/code_review_status.py` — clean.
Live `CODE_REVIEW_STATUS.json` currently has 0 of 2363 entries missing a
hash (already migrated), so `migrate-hashes` itself only exercises the
"nothing to do" path against real data — ran it, confirmed unchanged
("Nothing to migrate"). Functionally verified `_batch_cat_file` directly:
resolved 3 real `sha:path` specs from the live log against their recorded
`{hash}` values (exact sha256 match on all 3) and one deliberately-invalid
spec (correctly reported missing, not an exception).

## criteria
`migrate-hashes` uses at most one `git cat-file --batch` call regardless of
how many entries need backfilling; output/behavior (messages, safe-to-rerun,
unresolvable handling) unchanged from the per-entry version.
