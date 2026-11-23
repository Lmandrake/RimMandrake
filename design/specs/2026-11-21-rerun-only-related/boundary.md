# BOUNDARY: the change relation (`rerun_relation.py`) and the build match that uses it, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/rerun_relation.py` and `src/RimMandrake/rimflow/build_match.py`. Tests of the same
names: `src/RimMandrake/rimflow/selftest_rerun_relation.py`.

Rule: root `CLAUDE.md` §After a change, only the checks that the change touches run again; full text
`design/RimMandrake/standing_rulings.md` §After a change, only the checks that the change touches run again (item
`RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203`).

The question the relation answers: given a check of a mod's test table, the commit its last row was made on and the
commit now, does the change between them touch what the check reads or exercises? One module answers it for every
stage (the in-game build match, the Stage 6 exit, the visit brief, `./pipe why`, the walk build).

## ACCEPTS (the only inputs the relation is built for)

- **a-test-table-check.** A check is a test-table entry (`tests.<id>`) with any of `exercises` (a list of paths, or
  `"*"` for the whole mod), `reads` (paths) and `file` (its script). A path that ends in `/`, or names a folder, covers
  every file under it. A path followed by prose in brackets (`src/RimMandrake (every storage ThingDef)`) covers the
  path before the bracket.
- **row-commits-git-knows.** A row names the source commit it ran on (`mod_sha`); the commit now is the repository's
  HEAD. A commit git cannot resolve gives no relation.
- **the-mod-scope.** The change is the files that differ between the two commits under `src/RimMandrake/<Mod>/`,
  under `design/concepts/<Mod>/`, every file that any check of the table declares, and every C# file the mod's DLL is
  compiled from (its `.srchash`).

## DOES NOT SURVIVE (not handled)

- **a-change-no-declaration-connects.** A change can break a check whose declarations do not name what changed (a
  Python name reached only by a computed import or `getattr` on a string the check does not carry; a C# file the
  check exercises but does not declare). The guards are the whole-mod checks, the next visit of the related checks,
  and the owner's walk. No full rerun is added to cover it.
- **lookup-by-a-computed-key.** A dict read with a key the code computes is related through the keys the check's own
  strings name. A key computed from something else is not seen.

## PROMISES (each one is owed a test of the same name)

- **declared-paths-are-exercises-reads-and-file.** The paths a check declares are its `exercises`, its `reads` and its
  `file`, together.
- **untouched-row-counts.** A row made on an earlier commit counts when no changed file is one its check declares, or
  every changed declared file changed only in parts the check does not reach.
- **touched-check-reruns.** A check reruns when a changed file is one it declares and the change reaches it.
- **undeclared-change-reruns-nothing-and-is-listed.** A changed file under the mod that no check declares reruns no
  check, and the reading lists it, so that someone can declare it.
- **unreadable-relation-reruns-alone.** A check with no declared path, a row with no commit, or a commit git cannot
  resolve: that check reruns and is listed as unreadable; the other checks keep their own answers.
- **whole-mod-check-reruns-on-any-change.** A check that declares `"*"`, the mod folder itself, or is a full-list check
  (`kind` `live_full`), reruns on any change under the mod, the DLL included, except a file the mod's `.hashignore`
  lists (it never ships and the mod hash leaves it out; same grammar as `modcheck/status.py` `mod_hash`).
- **whole-mod-check-skips-hashignored.** A change only to files the mod's `.hashignore` lists reruns no whole-mod or
  full-list check; the same change beside a shipped file still reruns them.
- **csharp-relates-by-source-file.** A C# change relates through the changed `.cs` files; the DLL and its `.srchash`
  are derived and relate to nothing by themselves.
- **python-relates-by-symbol.** In a changed Python file, only the top-level names that changed count, and they
  touch a check only when the names its entry and id reach (across its declared Python files) include one of them; a
  dict literal relates key by key. A file that does not parse at either commit relates whole.
- **json-relates-by-entry.** In a changed JSON file that holds an object whose `id` (or key) is the check's id or
  entry, only that object's change touches the check; otherwise the file relates whole.
- **spec-change-reruns.** A check whose own test-table entry changed between the two commits in what it runs
  (`kind`, `file`, `entry`, `reads`, `exercises`, `command`, `tier`, `why_full_list`) reruns.
- **rows-from-several-builds.** Each row is related from its own commit: rows made on two earlier commits are judged
  apart.
- **a-path-outside-the-repo-is-not-in-the-change.** A declared path outside the repository (absolute, a drive path, or
  with `..`) is left out of the change git lists, so it never makes the relation unreadable; a check that declares only
  such paths is unreadable alone and reruns.
- **walk-not-the-source-is-one-deploy.** When the deployed walk folder is not the current source (its `.srchash`
  differs from the source's), the build match names one act, a deploy, and reruns no check for it.
- **python-imports-read-once-per-commit.** In one relation, the imports of a Python file at one commit are parsed once,
  however many checks declare or import that file: a git blob at a resolved commit never changes. (Measured
  2026-11-23: the tick's three relations parsed 1166 files for 107 checks, 86 s of a 204 s profiled tick; item
  RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN.)

Later lists beside this page: `polish.md`.
