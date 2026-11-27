# BOUNDARY: a judge that starts a built item keeps its pass, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/model.py` (`_verify_target`, the `started_judge` test only).
Item: `WORLD_FACES_REDRAW_ABYSS_ROT_RUST`, written 2026-11-27. The ticket lane's judge brief orders `rimflow start <ID>`,
which moves a built or validated item to `doing`. `verify` then refused every criterion pass ("counts only against a
BUILT artifact. Record `implemented` first"), and a fresh `implemented` forgets the item's earlier passes, so the
judge's PASS on this item could not be recorded. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_judge_start_keeps_pass.py`, which writes a temp ledger through the real CLI.
This page covers only that test in `_verify_target`; the rest of `model.py` has its own pages.

## ACCEPTS (the only inputs this is built for)

- **a-verify-pass-with-a-criterion.** A `verify --result pass --criterion <C>` event on an item that `implemented`
  built at a sha, then `claim` and `start` moved to `doing`, naming that built sha (the CLI's default with
  `--criterion`).

## DOES NOT SURVIVE (not promised)

- **a-pass-on-a-rebuilt-tree-under-the-same-sha.** A pass is trusted to be about the sha it names; this code does not
  check that the artifact under that sha is what was judged.

## PROMISES (each one is owed a test of the same name)

- **a-pass-at-the-built-sha-on-a-started-built-item-counts.** On a `doing` item with a built sha, a criterion pass
  that names the built sha is recorded, and the last owed criterion's pass finishes the item (`done`).
- **a-pass-at-another-sha-or-on-an-unbuilt-item-stays-refused.** A criterion pass on a `doing` item at a sha other
  than its built sha (the build may be under rework) is refused as before and changes nothing; a criterion pass on an
  item that was never built is refused as before.

Later lists beside this page: `polish.md` (none yet) and `next_version.md` (none yet).
