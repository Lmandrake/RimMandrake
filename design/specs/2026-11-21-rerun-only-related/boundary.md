# BOUNDARY: the change relation (`rerun_relation.py`) and the build match that uses it, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/rerun_relation.py` and `src/RimMandrake/rimflow/build_match.py`. Tests of the same
names: `src/RimMandrake/rimflow/selftest_rerun_relation.py`.
The Dispatch forecast also uses `deploy_custom_mods.py`, `build_match.py`, `maturation.py` and
`maturation_dispatch.py`. The stamp checks live in `src/RimMandrake/rimflow/selftest_build_match.py`.

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
  path before the bracket. In `exercises`, `F.cs::Type,member` names parts of a C# file, `F.cs::~` the members of that
  file that the check's other declared C# names, and `none` says that the check was read and exercises no C# of the mod.
- **row-commits-git-knows.** A row names the source commit it ran on (`mod_sha`); the commit now is the repository's
  HEAD. A commit git cannot resolve gives no relation.
- **row-mod-lists.** A live row records the package IDs it ran on (`active_mods`). The reference is the walk save's
  list for a full-list check or the check's tier for a minimal-list check. The check or its scene can declare extra
  package IDs it reads or exercises in `mods`, none named or `[]` for no extra mods.
- **the-mod-scope.** The change is the files that differ between the two commits under `src/RimMandrake/<Mod>/`,
  under `design/concepts/<Mod>/`, every file that any check of the table declares, and every C# file the mod's DLL is
  compiled from (its `.srchash`).

## DOES NOT SURVIVE (not handled)

- **a-change-no-declaration-connects.** A change can break a check whose declarations do not name what changed (a
  Python name reached only by a computed import or `getattr` on a string the check does not carry; a C# file the
  check exercises that it does not declare and whose types no declared C# file names, such as a class a def's XML
  names or one reached through a member of a type the check never names). The guards are the whole-mod checks, the next visit of the related checks,
  and the owner's walk. No full rerun is added to cover it.
- **a-wrong-declaration-no-scene-names.** A check that exercises a changed file and whose list leaves the file out, where no
  string of its scene names anything in that file, reads untouched. (What a scene names is caught:
  `design/specs/2026-11-24-declaration-check/boundary.md`.) Only when every check leaves the file out is it listed as
  undeclared. Two things outside the relation still hold: an UNRUN row of the run that made the change (`unrun_owed`), and
  the whole-mod checks.
- **a-dll-with-no-srchash.** A shipped DLL that no `.srchash` describes (a third-party library) changes nothing in the
  relation.
- **lookup-by-a-computed-key.** A dict read with a key the code computes is related through the keys the check's own
  strings name. A key computed from something else is not seen.
- **edits-outside-the-compose-deploy.** Dispatch's forecast reflects the last stamped compose deploy. A direct edit
  inside the same deployed folder can change the current build before the next deploy stamps it. The steward's
  `maturation.py next`, the advance gate, and `build_match.py check` read the current files.

## PROMISES (each one is owed a test of the same name)

- **declared-paths-are-exercises-reads-and-file.** The paths a check declares are its `exercises`, its `reads` and its
  `file`, together.
- **untouched-row-counts.** A row made on an earlier commit counts when no changed file is one its check declares, or
  every changed declared file changed only in parts the check does not reach.
- **touched-check-reruns.** A check reruns when a changed file is one it declares and the change reaches it.
- **undeclared-change-reruns-nothing-and-is-listed.** A changed file under the mod that no check declares reruns no
  check, and the reading lists it, so that someone can declare it. C# that ships is the exception (next promise).
- **shipped-csharp-reruns-the-live-checks-that-name-none.** A check that runs in the game (`kind` starts `live`) and
  declares no C# file that ships has no readable relation to a change of shipped C#: it reruns, and the reading names the
  changed C#, so that someone can declare what it exercises (`version/exercises.json`). C# that ships is a `.cs` file
  that a `.srchash` of the mod lists, or one under the mod in a project a `.srchash` names. An offline check, a change
  to an offline SelfTest program, a def, a doc and a scene script do not reach this rule. (Measured 2026-11-24: Pyrelands
  a6f05380df, six C# fixes, touched 1 of 40; no Pyrelands check names a C# file, and nine stale PASS rows stood; item
  RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED.)
- **rebuilt-dll-relates-by-its-srchash.** A `.cs` file whose hash in a `.srchash` differs between the two commits
  changed in the DLL, though its text may have landed in an earlier commit: it relates whole to the checks that reach
  that file, and by the promise above to the live checks that name no C#. (FlowWorks 4e3323090718, a DLL-only commit:
  1 of 30 touched.)
- **unreadable-relation-reruns-alone.** A check with no declared path, a row with no commit, or a commit git cannot
  resolve: that check reruns and is listed as unreadable; the other checks keep their own answers.
- **whole-mod-check-reruns-on-any-change.** A check that declares `"*"`, the mod folder itself, or is a full-list check
  (`kind` `live_full`), reruns on any change under the mod, the DLL included, except a file the mod's `.hashignore`
  lists (it never ships and the mod hash leaves it out; same grammar as `modcheck/status.py` `mod_hash`).
- **whole-mod-check-skips-hashignored.** A change only to files the mod's `.hashignore` lists reruns no whole-mod or
  full-list check; the same change beside a shipped file still reruns them. An ignored file that a whole-mod check
  declares (its own script) still reruns that check.
- **csharp-relates-by-source-file.** A C# change relates through the changed `.cs` files; the DLL's bytes and the
  `.srchash` file relate to nothing by themselves.
- **csharp-relates-by-scene-section.** In a changed `.cs` file, only the members and `case "x":` sections that changed
  count, and they touch a check only when what its id and entry reach includes one (its own section, the helpers and
  fields it names, a `goto case` target). Whole file when it does not read, the check anchors nowhere in it, a using
  line, an attribute or engine-called member, a member another file of the mod names, or a part no check reaches
  changed; a section that starts using a shared static another check reads touches that check. (ExplosiveKnockback
  visit 5, 2026-11-23: one scene's edit to RM_KnockbackProof.cs had sent all 54 scene checks back.)
- **csharp-code-after-a-switch-runs-when-a-section-falls-out.** The code after a method's one top-level switch (plain
  statements and if/else/try blocks only: no lambda, no local function) is reached only when a check calls the method
  by name, or when a section it reaches can end without `return` or `throw` (a break, goto, continue or yield
  anywhere in the section counts as one). Where an overload shares the method's name, a call counts only with a count
  of arguments that fits the method; a method group, a generic call or an unclear count counts. Any other shape keeps
  that code in its method, reached with it. (ExplosiveKnockback visit 2, 2026-11-26: `Build`'s
  `if (s.name.StartsWith("settings_sweep_")) return SettingsSweep(s);` after its switch, and the placement helper
  `Build(def, cell, stuff)`, sent all 64 scene checks back for a change in SweepLane; with this, 16.)
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
- **csharp-part-relates-by-its-members.** A check that declares parts of a C# file (`F.cs::Type,member`) is touched when a
  changed member is one of those types' or members, or one that they name in the same file, to a fixed point. A member
  that the engine calls, an attribute or an unnamed member touches the checks that declare its type; an instance field's
  initializer touches those that declare any member of it. A using line, a file that does not read, and a recompiled file
  whose text did not change relate whole. The file or a folder over it declared beside a part is the whole file. (Pyrelands
  a6f05380df, 2026-11-24: 38 of 40 by whole files, because the settings file, one file of seven patches and the ash field
  are in nearly every list; 17 by parts.)
- **unknown-part-relates-whole.** A declared part that the file holds at neither commit relates the whole file, and the
  reading names it. A part that the change renames touches the check.
- **reached-part-follows-the-declared-csharp.** `F.cs::~` is touched by a changed member that the check's other declared
  C# names, at either commit, through `F.cs` to a fixed point: a setting, a tuning number or a kernel. With no other C#
  that reads, it relates whole.
- **changed-member-no-check-declares-is-listed.** In a C# file that checks declare only by parts, the changed members that
  no check reaches rerun nothing and are listed (`F.cs::member`). A file that one check declares whole lists nothing.
- **declared-none-is-read-as-no-csharp.** A live check whose `exercises` says `none` keeps its row on a change of shipped
  C#. `none` hides no declared C# beside it, and its scene script still relates.
- **python-relates-by-symbol.** In a changed Python file, only the top-level names that changed count, and they
  touch a check only when the names its entry and id reach (across its declared Python files) include one of them; a
  dict literal relates key by key. A shipped def name (RM_, RSW_, RUT_) is never read as a row id. A top-level call that
  only registers another file's chains relates by itself. A file that does not parse at either commit relates whole.
- **json-relates-by-entry.** In a changed JSON file that holds an object whose `id` (or key) is the check's id or
  entry, only that object's change touches the check; otherwise the file relates whole.
- **spec-change-reruns.** A check whose own test-table entry changed between the two commits in what it runs
  (`kind`, `file`, `entry`, `reads`, `exercises`, `command`, `tier`, `why_full_list`) reruns. A live check's tier
  change is judged by its mod-list relation when the caller compares the lists.
- **rows-from-several-builds.** Each row is related from its own commit: rows made on two earlier commits are judged
  apart.
- **a-path-outside-the-repo-is-not-in-the-change.** A declared path outside the repository (absolute, a drive path, or
  with `..`) is left out of the change git lists, so it never makes the relation unreadable; a check that declares only
  such paths is unreadable alone and reruns.
- **walk-not-the-source-is-one-deploy.** When the deployed walk folder is not the current source (its `.srchash`
  differs from the source's), the build match names one act, a deploy, and reruns no check for it.
  A stamp that agrees beside a DLL whose bytes are not the source's owes the same deploy.
- **stale-walk-folder-still-reads-the-source-change.** While that deploy is owed, a row made on the folder's own build
  counts only when the change to the source does not touch its check and can be read. (Measured 2026-11-23:
  GimmeSomeSlack visit 1 read "206 count, 0 to run" while the relation read 206 touched; item
  RIMMANDRAKE_JUDGE_ROWS_BY_SOURCE_WHILE_WALK_FOLDER_STALE.)
- **tier-list-of-any-install-here-counts.** A row does not name the install it ran on, so a minimal-list row's list is
  compared with the tier's list on this process's install, then on the machine's other game install. The list as either
  install gives it counts. A mismatch on both goes to the mod-list relation. (Measured 2026-11-23: 37 ArchSmall rows of
  Pyrelands visit 7 read "to run" against ArchBig's older About.xml; item
  RIMMANDRAKE_READ_TIER_LIST_FROM_EVERY_GAME_INSTALL_HERE.)
- **mod-list-only-reruns-related-rows.** A package joining or leaving the reference list owes only rows that read or
  exercise it. Every check reads the mod itself, its declared dependencies, and the mods named by its XML guards or
  small-list `also` entries. Extra reads come from the check's or its scene's `mods`. An unreadable old or new list,
  or a membership change with an unreadable mod read list, owes the row and names the cause. A list with the same members
  in a different order still owes the row. The tick and the next visit apply the same membership rule when the
  published small list changes, or the check names a different tier.
- **full-list-is-the-mods-the-game-can-load.** The identity of a full-list row lists the packages of ModsConfig that
  the machine has installed, because the game loads only those and a save names only those. A package left out is named
  in `not_installed`. A scan that fails leaves the list whole and gives the reason. (Measured 2026-11-23: koth.isid was
  in ModsConfig and not installed, so ExplosiveKnockback visit 4 read 315 mods against the save's 314; item
  RIMMANDRAKE_DROP_UNINSTALLED_MOD_FROM_FULL_LIST_IDENTITY_KOTH.)
- **python-imports-read-once-per-commit.** In one relation, the imports of a Python file at one commit are parsed once,
  however many checks declare or import that file: a git blob at a resolved commit never changes. (Measured
  2026-11-23: the tick's three relations parsed 1166 files for 107 checks, 86 s of a 204 s profiled tick; item
  RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN.)
- **commit-reads-shared-across-relations.** In one process, a file read at a full commit id, and the C# units parsed
  from it, are read once for every relation built with the same runner: a blob at a full commit id never changes. A
  name that can move (`HEAD`, a branch) is resolved by each relation. (Measured 2026-11-25: `maturation_dispatch.py
  next --within 30m` builds the relations again on each of its 31 simulated ticks, 62 s of git reads each, and did
  not finish in 30 minutes; item RIMMANDRAKE_FIND_SLOW_PIPELINE_COMMANDS_HE_ASKED_FOR_INSTANT_ONES.)
- **tick-uses-deploy-build-without-walking.** A compose apply replaces the build stamp with the hash of the actual
  deployed folder, including held or extra files. Dispatch reuses a valid stamp for that installation and folder
  without enumerating its tree. Missing or invalid stamps, including older installs before their first stamped apply,
  fall back to the direct read. An explicit build check or advancement still verifies the current tree.

Later lists beside this page: `polish.md`.
