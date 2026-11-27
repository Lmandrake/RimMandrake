# BOUNDARY: maturation_convergence.py's Needs Conductor asks, Design Version 0.1.0

Code: `src/RimMandrake/Utils/maturation_convergence.py`. **This page covers only the asks**: `needs_lines`,
`quiet_mods` and the tick hook `annotate_reading`. The per-stage reading (rounds, new, fixed, open and the word) has no
page yet; its fixture tests are `src/RimMandrake/Utils/selftest_maturation_convergence.py`. Each promise below has a
test of its name in `src/RimMandrake/Utils/selftest_maturation_convergence_asks.py`. Items
RIMMANDRAKE_MEASURE_MATURATION_CONVERGENCE_PER_ROUND (the asks) and
RIMMANDRAKE_HUSH_DIVERGING_ASKS_ON_PASSED_AND_HELD_MODS (the hush).

## ACCEPTS (the only inputs the asks are built for)

- **a-reading-from-read-all.** `needs_lines(d)` takes the dict that `read_all(root)` returns, with its `mods` and
  `quiet` keys.
- **records-written-whole.** `src/RimMandrake/rimflow/mod_owner_hold.json` as `mod_owner_hold.py` writes it, and each
  `design/concepts/<Mod>/version/stage_record.json` as `maturation.py` writes it, under the root that `read_all` reads.

## DOES NOT SURVIVE (not handled)

- **a-hold-only-in-the-control-store.** `quiet_mods` reads the file mirror, not `mod_owner_hold.load()`, so that a
  `--root` fixture tree reads alone. A hold or lift that the control store records and whose mirror failed to publish
  (the alarm control:owner_hold_mirror) is not seen until the mirror is written. A `pipe off <Mod>` switch is not an
  owner hold here.
- **an-unhashable-mod-in-the-hold-file.** A hold row whose `mod` is a list or a dict raises TypeError in `quiet_mods`;
  `read_all` fails and the tick's reading carries `convergence_error` and no ask. `mod_owner_hold.load_file` refuses
  such a file, so only a hand edit makes one.

## PROMISES (each one is owed a test of the same name)

- **a-diverging-stage-asks-the-conductor.** For a mod that is neither passed nor held, each DIVERGING stage gives one
  line that names the mod, the stage, open and new by measured round, and says that it pauses nothing and changes no
  bar. A CONVERGING, FLAT or UNMEASURED stage gives no line.
- **a-passed-or-held-mod-asks-nothing.** A mod whose `stage_record.json` reads stage `passed`, or that
  `mod_owner_hold.json` holds, gives no line. `read_all(...)["quiet"]` names it with the reason, and its convergence
  reading (the table and the JSON) is still there.
- **an-unreadable-record-quiets-nothing.** A hold file or a stage record that is missing, empty, not JSON or of the
  wrong shape quiets no mod: every DIVERGING stage of that mod still asks.
- **the-tick-reading-carries-the-asks.** `annotate_reading(root, rd)` puts `convergence` in `rd` and appends each line
  to `rd["needs_conductor"]`, after any lines already there. When the reading fails, `rd` gets `convergence_error`
  and keeps everything else.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
