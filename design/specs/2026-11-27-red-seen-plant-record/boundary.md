# BOUNDARY: a planted fault never outlives the red-seen that planted it (plant_record.py, red_seen, certify, publish), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/plant_record.py`, `src/RimMandrake/rimflow/judge_certificate.py` (`red_seen`, `certify`,
`print_certificate`), `src/RimMandrake/rimflow/maturation.py` (the `red-seen` and `certificate` commands) and
`src/RimMandrake/Utils/publish.py` (`_publish`). Item `RIMMANDRAKE_RESTORE_TREE_WHEN_RED_SEEN_IS_KILLED_PLANT_STAYED_APPLIED`.
Measured 2026-11-27: the FlowWorks blind judge (cycle 5) killed `red-seen` at its own 500 s limit, and the planted fault
stayed in `RM_MapComponent_Sheet.cs`; reproduced on a fake tree with SIGTERM and with SIGKILL. Commit `79815237e7`
(`RIMMANDRAKE_RESTORE_RED_SEEN_TREE_WHEN_A_TIMEOUT_KILLS_IT`) made SIGTERM and SIGHUP run the restore; this page adds
the kill that no process can catch. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_red_seen_restore.py`.

## Design

Before `red-seen` plants a fault, it writes one record in the clone's git dir (`git rev-parse --git-path
rm_red_seen_plant.json`; outside a git work tree, `.rm_red_seen_plant.json` in the root): its pid and the pid's start
time, the mod, the test, the patch text, and each patched file's original bytes (base64; `null` for a file the patch
creates). The record is written atomically before `git apply` and removed after the restore. A caught end (a normal end,
an error, SIGTERM, SIGHUP, SIGINT) restores in the `finally` and removes the record. After a SIGKILL the record stays.
The next `red-seen`, `certificate` or `./publish` on that clone calls `plant_record.check(root)`: when the files differ
from the record, it reverses the record's patch with `git apply -R` and says so in one line.

## ACCEPTS (the only inputs these parts are built for)

- **one-clone-one-record.** The record belongs to the clone (its git dir). A clone has at most one `red-seen` at a time.
- **a-unified-diff-plant.** The plant is a unified diff that `git apply` applies in the root (as `red-seen` takes it).

## DOES NOT SURVIVE (not handled)

- **a-sigkill-during-the-record-write.** The record is written to a temporary file and renamed into place. A kill during
  the write leaves no record and no plant, because the plant is applied only after the rename.
- **a-test-write-after-a-sigkill.** After a SIGKILL, only the patch's own files are restored. A file that the test
  itself wrote is not in the record. (A caught end restores those files too, from the bytes that `red_seen` read before.)
- **a-signal-during-the-restore.** A second signal while the `finally` runs `git apply -R` can cut the restore. Then the
  record stays, and the next act restores the plant.
- **a-recycled-pid.** A pid that is alive with the same start time as the record reads as a `red-seen` still running.

## PROMISES (each one is owed a test of the same name)

- **sigterm-restores-the-tree.** A `red-seen` that gets SIGTERM, SIGHUP or SIGINT while its plant is applied ends with
  the original bytes in the tree, no red recorded, and no plant record left.
- **sigkill-leftover-is-restored-by-the-next-red-seen.** After a `red-seen` is killed with SIGKILL while its plant is
  applied, the next `red-seen` on that clone restores the file from the record before it does anything else, names the
  file in one line (`plant: restored ...`), and then runs as usual.
- **sigkill-leftover-is-restored-by-the-certificate.** The same leftover is restored and named by the next
  `certificate` (`certify` carries the line in `plant`, and `print_certificate` prints it).
- **sigkill-leftover-is-restored-by-publish.** The same leftover is restored and named by the next `./publish` on that
  clone, before `./publish` commits a named path.
- **normal-run-records-as-before.** A normal red run restores the tree, records the red in `version/evidence/red_seen.json`
  with the same fields as before, and leaves no plant record.
- **four-answers-stay-apart.** `plant_record.check` gives one of five states, each with its own words:
  `clean` (no record, or a record whose files already hold the original bytes: the record is removed); `restored`;
  `not restored` (the reverse does not apply: a stop that names each file and the record); `could not look` (the record
  is there but cannot be read: never `clean`, and the record is left in place); `running` (the record's pid is alive:
  its plant is in the tree on purpose). `red-seen`, `certificate` and `./publish` stop on `not restored`, `could not
  look` and `running`, and name the cause.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
