# BOUNDARY: the declaration check (`declaration_check.py`), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/declaration_check.py`, called by `rerun_relation.py` (`Relation.touches`). Item
`RIMMANDRAKE_CATCH_WRONG_CHECK_DECLARATION_FOUR_PLANTS_MISSED`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_declaration_check.py`.

An entry of a mod's `version/exercises.json` says what C# a check exercises, and the rerun decision believes the entry.
Measured 2026-11-24 on Pyrelands a6f05380df: four wrong entries were planted, and the rerun decision missed all four. The
declaration check reads each entry against the check's own scene: the scene names C#, and the entry must hold that C#.

## ACCEPTS (the only inputs this is built for)

- **a-check-with-a-csharp-list.** A live check whose `exercises` names C# files, or says `none`. A check with no C# list,
  a whole-mod check and a full-list check have no entry to be wrong.
- **names-in-strings.** The scene's Python names a C# type by its full name, a C# method that one type defines, a def of
  the mod, a switch (a static field of a `*Settings` type), or a field that it reads of a def.
- **a-reason-for-what-is-left-out.** `left_out` in `exercises.json` names a C# file, or parts of one, and why the entry
  leaves it out.

## DOES NOT SURVIVE (not handled)

- **csharp-no-scene-names.** C# that a check exercises and no string of its scene names (a Harmony patch on a vanilla
  method, a kernel, a gate). Measured 2026-11-24 on Pyrelands, each declared C# path dropped alone: 73 of 176 named. The
  other 103 drops are still seen by nothing but an UNRUN row and the whole-mod checks.
- **a-wrong-reason.** A `left_out` reason is not judged. A reader of the change judges it.
- **a-name-shared-by-many-scenes.** A name in more than `shared(n)` checks' scenes is staging. A check that tests that
  thing is then not named for it.
- **an-unseen-scene-in-the-rerun-decision.** A check whose scene is not found or does not read keeps the relation's own answer; the
  command lists it as COULD NOT LOOK.

## PROMISES (each one is owed a test of the same name)

- **left-out-csharp-is-named.** An entry that leaves out C# that its scene names is named, with the file, the member and
  the name in the scene. Each kind of name is enough by itself. The four wrong entries of 2026-11-24 are named.
- **true-declaration-is-not-named.** Pyrelands' reconciled table of 2026-11-24 is named by nothing, on the code of that
  day and on a6f05380df. An entry that holds the type, one member of it, the member that reads a switch, or the folder is
  not named.
- **staging-names-nothing.** A name in many checks' scenes, and a name in a constant or table of three or more names, says
  nothing of one check.
- **left-out-with-a-reason-is-not-named.** What `left_out` names with a reason is not named. An empty reason, another file
  or another member covers nothing.
- **named-check-reruns.** A named check is touched by a change in a type that it left out, at either commit, and not by a
  change elsewhere. An entry that says `none` while its scene names C# has no readable relation: the check reruns on any
  change of C# that ships.
- **scene-check-off-reruns-nothing.** `"scene_check": "off: <why>"` in `exercises.json` keeps the names from the rerun
  decision. The command still prints the names.
- **no-scene-found-is-could-not-look.** A check whose scene no Python of the mod holds is listed as COULD NOT LOOK with the
  cause, and so is each check when a scene, a C# file or a def file does not read; the command exits 2; a table with no C# list, or a commit that git does not hold, also exits 2.

Later lists beside this page: `polish.md`.
