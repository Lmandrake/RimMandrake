# BOUNDARY: the per-game hold and ArchSmall's own install, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/control.py` (the `game:` scope, `game_held`, `game_holds`), `src/RimMandrake/rimflow/maturation_dispatch.py` (`game_hold`, `full_list_only`, `pick_game`), `src/RimMandrake/rimflow/host_guard.py` (`crossing` with `new_run`), `src/RimMandrake/rimflow/detached_helper.py` (`run_game`), `src/RimMandrake/Utils/game_instance.py` (`install`, `game_dir`, `seed_site_saves`, `hold_refusal`, `held_by_anyone`, `leftovers`, `stop`, `brief`), `src/RimMandrake/Utils/game_paths.py` (`GAME_DIR`, `LOCAL_MODS`, `GAME_DATA`, `A_GAME_DIR`), `src/RimMandrake/Utils/deploy_custom_mods.py` (`--instance`, the hold on `--apply`), `src/RimMandrake/bridgetools/build.py` (`aim`, `--instance`), `src/RimMandrake/Utils/modset_builder.py` (`owned_backups`).
Item: `RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST`, written 2026-11-20. The owner walked ArchBig twice
that day while every in-game run waited, although ArchSmall existed. His words at 6:20 AM PST: *"We can run two games you
know..."*; at 3:40 PM PST: *"You should not have been waiting for the game. there are two games"*. Each promise has a
test of its name in `src/RimMandrake/rimflow/selftest_game_hold_split_install.py`. This page covers only these parts of
the files named; the rest of each file has its own page or none.

A game's name (ArchBig, ArchSmall, Steve1, Steve2) and the map from its letter and key are on
`design/specs/2026-11-22-game-names/boundary.md`; this page's letters are those internal keys.

## ACCEPTS (the only inputs this is built for)

- **a-game-letter.** A game is one letter: `a` is Steam's install (ArchBig, the full list); `b` and on are named games, each with a
  data folder and an install under the instances root (`RM_INSTANCES_ROOT`, else `<data root>/instances`).
- **the-control-store.** The one control store of `control.py`. A store that does not exist on a machine holds no game:
  a hold is only ever written into it.
- **game-as-install-copy-source.** ArchBig's install folder, read only. Its `Mods`, `BridgeTools`, `Data`,
  `MonoBleedingEdge`, `RimWorldWin64_Data` and the top-level game files are what a named game's install copies.

## DOES NOT SURVIVE (not promised)

- **a-full-list-on-game-b-beside-game-a.** His full list on ArchSmall beside ArchBig does not fit in memory on Archmagi
  (about 17.5 GB needed, 19.6 GB headroom, a 12 GB floor; measured 2026-11-20). A visit whose every owed check needs the
  full list waits for ArchBig; a full-list check inside a mixed visit on b is recorded UNMEASURED by the driver.
- **a-third-party-mod-updated-after-the-copy.** ArchSmall's copy of a third-party mod in `Mods` is the copy of the day it
  was made; `install --refresh` adds and updates, and never deletes.
- **a-unity-registry-key.** ArchSmall's exit writes a Unity registry key that ArchBig reads at its next launch (design note
  `design/RimMandrake/two_rimworld_instances_2026-11-07.md`). Nothing here touches it.
- **a-tool-that-writes-the-game-folder-by-a-literal-path.** Only `deploy_custom_mods.py` and `bridgetools/build.py` write
  into an install (census of 2026-11-20 over every file naming the install); a new tool that hard-codes Steam's path
  writes ArchBig's folder whatever game it means.

## PROMISES (each one is owed a test of the same name)

- **a-game-hold-is-a-scope-that-refuses-runs-on-that-game-only.** `pipe off game:ArchBig` (or `game:a`) writes a switch on the store's scope `game:a`;
  a run whose spec names ArchBig is refused at admission and at its start; a run on ArchSmall, or one that names no game,
  is not.
- **a-run-names-a-game-only-when-it-drives-one.** `detached_helper.run_game` gives a run's game as its
  `RM_GAME_INSTANCE`, else ArchBig for an in-game run (an item that names `IN_GAME_ACCEPTANCE` or `IN_GAME_VISIT`), else
  no game. A steward run at stage `in_game` names no game, so `pipe off game:ArchBig` does not refuse it; if it needs a game
  later, `game_lock` refuses the held one.
  (2026-11-21: his walk hold on ArchBig refused Pyrelands' offline steward run eight times in 51 minutes.)
- **a-held-game-is-never-picked-and-game-b-takes-the-run.** `pick_game` never returns a held game, whatever its bridge
  reading says, so his walk is kept when the Conductor's bridge hold lapses; the next free game takes the run. A store
  that cannot be read holds the game.
- **a-full-list-only-visit-waits-for-game-a-and-says-so-by-name.** A visit whose every owed stage-6 check (its `to_run`,
  the checks not counted from an earlier visit) needs the full list is offered ArchBig only; while ArchBig is held it waits, and the tick's reason names those checks and the hold.
- **the-askers-own-hold-is-a-hold-for-a-new-run.** `crossing(new_run=True)` reads a live driver lock as held even when
  the holder is the asker's own window; without `new_run` it does not (the holder may drive its own game).
- **leftovers-never-offers-a-held-game.** `leftovers` never lists a game that is held, or whose driver lock has any
  live holder, the asker's own window included; an idle game with neither is still listed.
- **stop-of-a-held-game-refuses-unless-despite-hold.** `stop` of a held game signals nothing and refuses by name;
  `--despite-hold "<why>"` passes it to the bridge check as before.
- **a-named-games-paths-are-its-own-install.** With `RM_GAME_INSTANCE=b`, `game_paths.GAME_DIR`, `LOCAL_MODS` and
  `GAME_DATA` lie under ArchSmall's own install; `WORKSHOP` and `A_GAME_DIR` stay Steam's. With no game named they are
  Steam's, as before.
- **a-deploy-for-game-b-writes-only-under-game-b.** `deploy_custom_mods.py --instance ArchSmall` plans into ArchSmall's own `Mods`;
  with no instance it plans into ArchBig's, as before. A composed def-guard repair for a stale SandLion and a folded-mod
  redirect both include the resolved instance in the printed command.
- **a-deploy-into-a-held-game-refuses-and-writes-nothing.** From WSL, `deploy_custom_mods.py --apply` into a held game
  exits non-zero naming the hold, before any write. Native Windows `--apply` refuses before any write, names the target,
  and prints the equivalent WSL command so that the authoritative hold store is consulted. Native Windows dry runs are allowed.
- **a-companion-build-for-game-b-writes-only-under-game-b.** `bridgetools/build.py` aimed at ArchSmall deploys into ArchSmall's
  own `BridgeTools/JawaBench`; aimed at ArchBig it keeps Steam's.
- **the-in-game-gate-reads-the-runs-own-game.** `companion_current(game=b)` reads ArchSmall's own companion DLL, and
  `mod_deployed(game=b)` runs the deploy plan with `--instance ArchSmall`.
- **install-writes-only-under-the-named-game.** `install` writes only under the named game's own install folder, copies
  the game's files and `Mods` and not the rest of ArchBig's folder, keeps an install that exists (copying only a top-level
  game file it lacks), and refuses an install folder that overlaps ArchBig's.
- **a-named-game-gets-the-registered-site-saves-it-lacks.** `prepare` (so every `launch` of a named game) copies each
  save that `modcheck/test_site_saves.json` registers and the named game's own `Saves` lacks, from ArchBig's `Saves`. It
  never overwrites a save the named game has, never copies one that ArchBig lacks, never writes ArchBig's folder, and copies
  nothing for ArchBig. A copy that cannot be made does not stop the launch: the check that needs the save still says so by
  name. (2026-11-25: Pyrelands on ArchSmall read `SiteError: programState 'Entry'` for a save made on ArchBig.)
- **a-named-games-list-swap-is-its-own.** `modset_builder.owned_backups(<seat>)` with a named game is
  `modset_swaps/<seat>.<game>`, so a seat's list swap on ArchBig never refuses a list for ArchSmall; ArchBig keeps
  `modset_swaps/<seat>`.
- **game-bs-brief-names-its-own-install-and-its-unmeasured-full-list-checks.** A run brief for ArchSmall says that ArchSmall has
  its own install, and names each full-list check the visit holds as UNMEASURED on b.

Later lists beside this page: `polish.md` (three lines) and `next_version.md` (none yet).
