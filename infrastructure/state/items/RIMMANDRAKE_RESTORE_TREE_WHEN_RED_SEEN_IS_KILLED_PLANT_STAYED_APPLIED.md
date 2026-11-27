# RIMMANDRAKE_RESTORE_TREE_WHEN_RED_SEEN_IS_KILLED_PLANT_STAYED_APPLIED

## spec
`maturation.py red-seen` (`judge_certificate.red_seen`) applies a planted fault with `git apply`, runs the deciding
test, and reverses the fault in a `finally` block. A SIGTERM (Python's default action) or a SIGKILL ends the process
without that `finally`, so the planted fault stays in the mod's source. Seen 2026-11-27: the FlowWorks blind judge
(cycle 5) killed `red-seen` at its own 500 s limit and found its plant still applied in `RM_MapComponent_Sheet.cs`.

Owed: (1) `red-seen` restores the tree on any end a process can catch (normal end, error, SIGTERM, SIGINT); (2) before
it plants, `red-seen` writes a record of the plant (each file's original bytes); the next `red-seen`, `certificate` or
`./publish` on that clone restores a leftover plant from the record and says so in one line; (3) four answers kept
apart: clean, leftover restored, leftover not restored (a stop that names the file), record unreadable (could not look).

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_red_seen_restore.py` (fake mod tree, fake deciding test):
SIGTERM while planted leaves the original bytes; SIGKILL while planted is restored and named by the next act; a normal
run restores and records as before; a damaged record reads could not look, never clean. The SIGTERM case is red on the
base commit.

## criteria
- a planted fault never outlives the `red-seen` that planted it; a leftover is restored and named by the next act on
  that clone.

## refs
file: src/RimMandrake/rimflow/judge_certificate.py
file: src/RimMandrake/rimflow/maturation.py
