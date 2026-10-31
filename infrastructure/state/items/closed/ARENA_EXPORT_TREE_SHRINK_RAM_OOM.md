# ARENA_EXPORT_TREE_SHRINK_RAM_OOM

Filed (OWNER): `export_tree` reads the whole 7.7 GB base tree into RAM through one `git cat-file --batch`; the v3 runner
was OOM-killed at the tester step. Same seam in v3, ralph_a, trio and base_export_run. Fix before any relaunch.

## verify
- L0: `src/RimMandrake/Utils/arena/v3_control.py` `export_tree` and the same capture in `ralph_a_loop.py` stream each
  object to disk (as `arena_safe_git.verify_tree` does), no whole-output capture left in any arm's export path; the
  exported tree stays byte-identical to the old export on a small fixture, including the refusal on a bad header; the
  arena selftests for v3, ralph_a and trio are green.
- L1: one real export of the real base tree at the trial's parallelism (every arm's tester step at once) finishes
  inside the `rm-harness.slice` memory limit, with the measured peak recorded on this item.
- Stopping point: finish.

## criteria
- A1 L0: no arm's export buffers a whole tree; output unchanged; selftests green
- A2 L1: a real all-arms export stays under the slice limit, peak measured
