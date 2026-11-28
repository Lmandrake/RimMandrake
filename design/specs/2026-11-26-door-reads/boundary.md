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
- **a-read-by-stat-only.** A test that only asks whether a repo file exists (`os.path.exists`, `os.stat`) and never
  opens it or lists its folder does not record that file. A change that adds or deletes only that file leaves the
  test out. No pipeline test was seen to do this (a census of `exists`/`isfile`/`stat` on repo paths, 2026-11-26).
- **a-record-on-a-shared-network-folder.** The record file takes one append per line from each process. On a folder
  whose appends interleave (`/mnt/d`, measured 2026-11-26), two lines can join into one false path, and both reads are
  lost. `publish.py` writes the record under its own `TMPDIR`, a local disk.
- **cost.** The hook adds about 7% to a test's time (`selftest_dispatch_pilot_holder.py`: 17.4 s to 18.7 s and
  13.4 s to 14.2 s, alternated, 2026-11-26, load 17).

## PROMISES (each one is owed a test of the same name)

- **records-what-a-test-reads.** Under the hook, a test's record holds the repo files that its Python processes
  open or import, in any thread (a hooked child's too, and `git show <rev>:<path>`), and the folders that they list. Without
  `RM_DOOR_READS` the hook does nothing.
- **a-read-the-hook-cannot-see-is-unknown.** A Python child that drops or skips the hook, a git child that reads the
  tree as a whole (`ls-files`, `status`, `clone`), and any other child aimed at the tree make the record answer
  "unknown", and so does a git child that takes its paths on its input (`cat-file --batch`, `hash-object
  --stdin-paths`) or names the whole tree after `--` (nothing, or `.`). A git child in a subfolder reads its `-- paths`
  under that subfolder. Then the door runs the test whenever its import closure names it.
- **an-untouched-test-is-left-out.** With a record that decides, a change touches the test when it edits the test, a
  file that the test read, or a folder that the test listed. A file in a folder that is new inside a listed folder
  changes that listing too (a glob of `design/specs/*/boundary.md`, or a walk, finds it). Any other change leaves the
  test out.
- **a-record-of-other-code-decides-nothing.** A record whose `.py` files differ at the change's base answers
  "unknown", and so do no record and a torn record. Data that moved on main does not stop a record from deciding.
- **a-tree-that-never-landed-hides-no-record.** A test keeps one record per distinct set of `.py` blobs that its green
  runs read, and the newest record whose `.py` blobs all match the base decides. So the green run of a publish whose
  tree never lands, or lands later, does not hide the record of the base's code (on 2026-11-27, 46 % of the door's
  selected runs were "another version", because each publish overwrote the one record of a test with its own tree's
  blobs: `design/specs/2026-11-26-slow-actions/publish_line.md`). The store keeps the newest `TREES` records of a test.
- **the-door-runs-only-the-tests-a-change-touches.** `publish.py` runs the pipeline tests with the hook, keeps the
  record of each green run, and leaves out a test that its import closure names only when a record that decides
  shows the change untouched and no `inputs` glob of the test names a changed path. With no base to read, every
  test that the closure names runs, and the door says why.

## LIMITS

- `TREES = 16` records per test (`door_reads.py`). Danger: a store that grows without end (a full set of records is
  14 MB, measured 2026-11-27, and about 100 publishes a day change code that tests read). Need: the line held 11
  publishes at once (4:05 PM PST 2026-11-27). A pruned record only makes its test run again.
- `keep` keeps the first 20 unknown reasons of a record (a display bound: one reason decides).

## PROOF

- The selftest is green on the fix. Five planted faults, each caught by the promise that it breaks
  (`evidence/plants.txt`): `relation` never answers touched; no `.py` check; the hook ignores children; `narrow`
  never leaves a test out; folder listings ignored.
- 2026-11-27, the fresh read (`RIMMANDRAKE_READ_DOOR_READS_FRESH_NOT_BY_ITS_WRITER`): six new checks, each red on the
  parent for its named reason and green on the fix: a new subfolder of a listed folder; `cat-file --batch`;
  `hash-object --stdin-paths`; an empty `--`; `-- .`; `-- paths` of a git child in a subfolder. The real records of
  `selftest_boundary_check.py` and `selftest_codex_lane.py` list `design/specs`, so a new spec folder read "not
  touched" before. Record format 2: a record parsed before the fix answers "unknown" until its test is green again.
- 2026-11-27, one record per tree (`RIMMANDRAKE_MEASURE_PUBLISH_SLOT_DANGER_BEFORE_ANY_CHANGE`):
  `t_a_tree_that_never_landed_hides_no_record` red on the parent (the base's record "ran another version of lib.py"
  after another tree's record was kept; no `TREES`), green on the fix. The one-record file of before
  (`<store>/<hash>.json`) is still read, after the per-tree records, and never written.
