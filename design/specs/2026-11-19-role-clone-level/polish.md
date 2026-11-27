# Later list: polish for levelling a role clone (beside `boundary.md`)

One line per claim. Nothing here is a ticket or owed work. The next Work Bundle that changes the file a line names
takes the line, does it, and removes it.

- `src/RimMandrake/rimflow/selftest_role_clone_level.py` `t_a_twin_held_by_dirt_is_stranded_with_its_fix` checks only
  that `fix` names `seat_sync.py` and the twin's sha; it never runs the line. risk: a `fix` that loses `--repo <clone>`
  or names a wrong seat_sync path still passes the test, and the Conductor's printed fix then fails to level the
  Designer clone. Measured kept on 2026-11-27: after `git checkout -- code.txt`, the printed line run from `/tmp`
  exits 0 and levels the clone. Repair: clear the dirt, run `fix` with `cwd` outside the clone, check `level_after`.
