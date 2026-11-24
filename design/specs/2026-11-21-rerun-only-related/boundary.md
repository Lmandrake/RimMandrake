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
  check exercises that it does not declare and whose types no declared C# file names, such as a class a def's XML
  names or one reached through a member of a type the check never names). The guards are the whole-mod checks, the next visit of the related checks,
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
  full-list check; the same change beside a shipped file still reruns them. An ignored file that a whole-mod check
  declares (its own script) still reruns that check.
- **csharp-relates-by-source-file.** A C# change relates through the changed `.cs` files; the DLL and its `.srchash`
  are derived and relate to nothing by themselves.
- **csharp-relates-by-scene-section.** In a changed `.cs` file, only the members and `case "x":` sections that changed
  count, and they touch a check only when what its id and entry reach includes one (its own section, the helpers and
  fields it names, a `goto case` target). Whole file when it does not read, the check anchors nowhere in it, a using
  line, an attribute or engine-called member, a member another file of the mod names, or a part no check reaches
  changed; a section that starts using a shared static another check reads touches that check. (ExplosiveKnockback
  visit 5, 2026-11-23: one scene's edit to RM_KnockbackProof.cs had sent all 54 scene checks back.)
- **csharp-reads-the-types-it-names.** A declared `.cs` file reads the mod's other `.cs` files that define a type it
  names, a partial class's other parts among them, to a fixed point, at either commit, of the C# project a `.srchash`
  names (an offline SelfTest program is not one). In such a file a changed member touches a check only when the names
  the check reaches include the member's name and its type's name; strings, case labels and list values do not reach
  there. An engine-called member there touches the checks that name its type. A using line there relates it whole; a
  check that anchors in none of its declared files, and lists no C# in `exercises`, relates it whole. (ExplosiveKnockback, 2026-11-23:
  sc_frame_probe_check's RM_FrameProbe lives in RM_KnockbackProof_StageThree.cs, which no check declares; with the
  section relation alone its change reran nothing, and with this it reruns sc_frame_probe_check, 4 of 56 in all.)
- **declared-exercises-bound-the-types-named.** A check that anchors in none of its declared C# and lists C# files in its
  `exercises` is related by that list: a change in a file that the list does not name does not touch it. A check with
  no such list still relates whole. (Gimme Some Slack, 2026-11-23: csharp-reads-the-types-it-names sent 75 listed rows
  back for CordBuilder.cs, which their lists leave out on purpose, so 206 of 206 reran.)
- **python-relates-by-symbol.** In a changed Python file, only the top-level names that changed count, and they
  touch a check only when the names its entry and id reach (across its declared Python files) include one of them; a
  dict literal relates key by key. A shipped def name (RM_, RSW_, RUT_) is never read as a row id. A top-level call that
  only registers another file's chains relates by itself. A file that does not parse at either commit relates whole.
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
- **stale-walk-folder-still-reads-the-source-change.** While that deploy is owed, a row made on the folder's own build
  counts only when the change to the source does not touch its check and can be read. (Measured 2026-11-23:
  GimmeSomeSlack visit 1 read "206 count, 0 to run" while the relation read 206 touched; item
  RIMMANDRAKE_JUDGE_ROWS_BY_SOURCE_WHILE_WALK_FOLDER_STALE.)
- **tier-list-of-any-install-here-counts.** A row does not name the install it ran on, so a minimal-list row's list is
  compared with the tier's list on this process's install, then on the machine's other game install. The list as either
  install gives it counts; a list that is the tier's on neither does not. (Measured 2026-11-23: 37 ArchSmall rows of
  Pyrelands visit 7 read "to run" against ArchBig's older About.xml; item
  RIMMANDRAKE_READ_TIER_LIST_FROM_EVERY_GAME_INSTALL_HERE.)
- **full-list-is-the-mods-the-game-can-load.** The identity of a full-list row lists the packages of ModsConfig that
  the machine has installed, because the game loads only those and a save names only those. A package left out is named
  in `not_installed`. A scan that fails leaves the list whole and gives the reason. (Measured 2026-11-23: koth.isid was
  in ModsConfig and not installed, so ExplosiveKnockback visit 4 read 315 mods against the save's 314; item
  RIMMANDRAKE_DROP_UNINSTALLED_MOD_FROM_FULL_LIST_IDENTITY_KOTH.)
- **python-imports-read-once-per-commit.** In one relation, the imports of a Python file at one commit are parsed once,
  however many checks declare or import that file: a git blob at a resolved commit never changes. (Measured
  2026-11-23: the tick's three relations parsed 1166 files for 107 checks, 86 s of a 204 s profiled tick; item
  RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN.)

Later lists beside this page: `polish.md`.
