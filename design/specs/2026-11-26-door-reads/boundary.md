# BOUNDARY: the door runs only the pipeline tests whose last green run read a changed path, Design Version 0.1.0

Code: `src/RimMandrake/Utils/door_reads.py`, `src/RimMandrake/Utils/door_reads_hook/sitecustomize.py`, used by
`src/RimMandrake/Utils/publish.py` (`narrow_by_reads`, the record step in `_run_tree_checks`). Item:
`RIMMANDRAKE_UNJAM_PUBLISH_DOOR_LEDGER_WAITED_THIRTY_MINUTES`, written 2026-11-26. Each promise has a test of its
name in `src/RimMandrake/Utils/selftest_door_reads.py`.

Why: `CLAUDE.md` §After a change, only the checks that the change touches run again. The door picked pipeline tests by
their import closure (`publish.door_inputs`). Hub modules tie that closure to almost every pipeline file
(`role_launch` → `ops_watch` → `testq`; `control` → `detached_helper` → `guiding_prose` → `publish`), mostly through
imports inside functions that a test never calls. Measured on 2026-11-26: a change to `publish.py`, `maturation.py`
or `testq.py` selected 228 or 229 of the 243 tests, about 3640 s of test time. With one read record per test (a
hooked run of all 243 on f3db6b951b, 2026-11-26 4:05 PM PST; 242 green, one `ENOMEM` read of `/mnt/d` that is green
again), 187 records decide and 56 answer unknown (`git ls-files` 16, `git clone` 9, `systemctl` 7, others). Tests run
per change, the closure's against the records' (`evidence/narrow_measure.txt`, test time from a run on origin/main):
`publish.py` 228 → 102 (3638 s → 2556 s); `treecheck_slots.py` 228 → 96 (2542 s); `list_dispatch.py` 228 → 107
(3205 s); `maturation_dispatch.py` 228 → 131 (3419 s); `maturation.py` 229 → 158 (3502 s). The slowest tests read
most pipeline files, so the time falls less than the count.

## ACCEPTS (the only inputs this is built for)

- **pipeline-tests-run-by-the-door.** Python tests that `publish.py` runs from `pipeline_tests.json`, in a check tree
  that is a git work tree, with `RM_ROOT` naming the machine's state folder (`RM_ROOT/door-reads/`).
- **python-with-audit-hooks.** Python 3.8 or later; the hook uses `sys.addaudithook`.

## DOES NOT SURVIVE (not promised)

- **a-read-steered-by-data.** A record decides while the `.py` files the test ran are unchanged at the change's base.
  Data (ledger shards, items, mod records, configs) may move on main meanwhile. A test whose data steers it into code
  that its last run did not load can then be left out when that code changes. A pipeline test is built on fixtures,
  so this needs a test that reads live state (`live_excluded` holds the known ones).
- **a-new-module-that-shadows-an-import.** The import system's own folder listings are not recorded. A new module that
  would shadow one the test imports from a later `sys.path` folder is not seen.
- **a-reader-that-is-not-python.** A non-Python child aimed at the tree (other than `git` with named paths, and a
  short list of programs that read no file) makes the record "unknown": the door keeps the import closure for it.
- **cost.** The hook adds about 7% to a test's time (`selftest_dispatch_pilot_holder.py`: 17.4 s to 18.7 s and
  13.4 s to 14.2 s, alternated, 2026-11-26, load 17).

## PROMISES (each one is owed a test of the same name)

- **records-what-a-test-reads.** Under the hook, a test's record holds the repo files that its Python processes
  open or import (a hooked child's too, and `git show <rev>:<path>`), and the folders that they list. Without
  `RM_DOOR_READS` the hook does nothing.
- **a-read-the-hook-cannot-see-is-unknown.** A Python child that drops or skips the hook, a git child that reads the
  tree as a whole (`ls-files`, `status`, `clone`), and any other child aimed at the tree make the record answer
  "unknown". Then the door runs the test whenever its import closure names it.
- **an-untouched-test-is-left-out.** With a record that decides, a change touches the test when it edits the test, a
  file that the test read, or a folder that the test listed. Any other change leaves the test out.
- **a-record-of-other-code-decides-nothing.** A record whose `.py` files differ at the change's base answers
  "unknown", and so do no record and a torn record. Data that moved on main does not stop a record from deciding.
- **the-door-runs-only-the-tests-a-change-touches.** `publish.py` runs the pipeline tests with the hook, keeps the
  record of each green run, and leaves out a test that its import closure names only when a record that decides
  shows the change untouched and no `inputs` glob of the test names a changed path. With no base to read, every
  test that the closure names runs, and the door says why.

## LIMITS

- None of its own. A record is written once per green run. `keep` keeps the first 20 unknown reasons of a record
  (a display bound: one reason decides).

## PROOF

- The selftest is green on the fix. Five planted faults, each caught by the promise that it breaks
  (`evidence/plants.txt`): `relation` never answers touched; no `.py` check; the hook ignores children; `narrow`
  never leaves a test out; folder listings ignored.
