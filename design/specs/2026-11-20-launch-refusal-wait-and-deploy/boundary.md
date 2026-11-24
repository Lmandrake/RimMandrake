# BOUNDARY: a refused launch that waits is not a fault; an in-game visit deploys what the game loads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`deploy_state`, `mod_deployed`, `deploy_repair`, the in-game branch of
`launch_mod`, `WAIT_MARK`, `_companion_cmd`), `src/RimMandrake/rimflow/maturation_autonomy.py` (`wait_refusal`, `_retriable`,
`_execute_one`), `src/RimMandrake/rimflow/maturation_dispatch.py` (`retriable`, `still_retried`, `launch_counted`,
`drain_gate` in `_tick`), `src/RimMandrake/rimflow/run_void.py` (`sync_system`'s never-started branch) and
`src/RimMandrake/Utils/game_instance.py` (`alive`, the wait after the deploy's stop).
Items: `RIMMANDRAKE_DEPLOY_BEFORE_GAME_VISIT_PYRELANDS_REFUSED_THRICE` and
`RIMMANDRAKE_STOP_COUNTING_DRAIN_REFUSALS_AS_SYSTEM_FAULTS`, written 2026-11-20.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_launch_wait_and_deploy.py`.

Why: on 2026-11-20 the Dispatch tick counted two kinds of refused launch as system faults and retried them unchanged,
and `OPS_MATURATION_SYSTEM_FAULT_LOOP` paused two mods with nothing broken. FlowWorks: three fixer launches refused by
the account drain before the planned switch (6:08 to 6:12 PM PST). Pyrelands: three in-game visit launches refused
because the composed Baroque Biomes copy differed from the repo, by one dev script of another member mod
(`Biomes/Cauldron/mutants_cauldron_trunk_deposits.sh`) and nine textures that only the game folder held (6:03 to
6:15 PM PST). No file the game loads and no def differed.

## The answers to the four design questions (item RIMMANDRAKE_DEPLOY_BEFORE_GAME_VISIT_PYRELANDS_REFUSED_THRICE)

1. **What must match:** only the files the game loads, for the whole composed mod (option b). The danger is an
   in-game verdict on a copy that is not the committed one (2026-11-19: GimmeSomeSlack visit 2 with an old DLL). A file
   outside a loaded folder (a `.sh`, `Source/`, a README) cannot change what the game plays, so it cannot cause that.
   A def, patch or DLL of another member biome can change what the visited mod's scenes see, so the whole composed mod
   is read, not the visited mod alone (option c would miss that).
2. **Game-only files (`-` lines):** a game-only file in Defs, Patches, Assemblies, Languages, About or LoadFolders.xml
   is drift: the game loads it and the repo does not ship it. A game-only texture or sound is drift only when a def,
   patch or C# file in the repo names its path: a texture nobody names is never drawn, so it cannot change a verdict.
3. **Self-repair:** when loaded drift exists that a plain `--apply` cures (`+`, `~`, and `-` files the repo deleted),
   the launch deploys before it launches: game down if it is up, `deploy_custom_mods.py ... --apply` for the game the
   visit drives, game up again if it was up, and the plan read again. A game-only loaded file the repo never deleted
   is not cured by `--apply` (it needs `--pull` to rescue or `--prune` to delete, a hand's choice): the launch refuses
   and names it.
4. **Refusals left:** a deploy that fails, a game that will not stop or start, a plan still differing after the
   deploy, and a game-only loaded file. Each names its cause and counts as a real fault. A held bridge, a held game and
   the account drain are waits.

## ACCEPTS (the only inputs this is built for)

- **a-deploy-plan.** The text `deploy_custom_mods.py` prints in plan mode: drift lines `+  <rel>`, `~  <rel>`,
  `-  <rel>   (in game, not in repo; <note>)`, held lines `H  ...`, and the last line `Drift found. ...` or
  `Everything in sync.`. `<rel>` is relative to the game's mod folder (for Baroque Biomes, `Biomes/<Member>/...`).
- **a-launch-text.** A launch's refusal text: `detached_helper.drain_refusal`'s ("refused: the account ... is
  draining"), and `launch_mod`'s, which starts with `WAIT_MARK` when the cause ends by itself.
- **the-dispatch-books.** `state.json`'s per-mod books as `run_void` reads them; a never-started entry has `failed`,
  no `unit`, and `tries`.

## DOES NOT SURVIVE (not promised)

- **a-take-between-stop-and-deploy.** The repair does not take the bridge: it reads it takeable, stops the game
  (`game_instance.stop`, which reads the bridge again), deploys and starts the game, and the launched driver then takes
  it. A seat that takes the bridge inside those minutes is not seen.
- **a-texture-named-by-a-computed-path.** A texture whose path the C# builds at run time from parts is not found by
  the name search, so a game-only copy of it reads as not drift.
- **a-plan-format-change.** A plan whose drift lines change shape is read as could-not-look only when it prints
  neither last line; a new line kind beside `+ ~ -` is not read.

## PROMISES (each one is owed a check of the same name)

- **non-game-drift-launches.** A plan whose only drift lines are outside the loaded folders, or game-only textures no
  repo file names (this evening's real plan), reads current: the visit launches, with no deploy and no game restart.
- **loaded-drift-deploys-then-launches.** A `~` on a def: the launch stops nothing when the game is down, deploys once
  with `--apply` for the visit's game, reads the plan again, and launches.
- **a-dll-deploys-with-the-game-down.** A `~` on a DLL with the game up: the game is stopped before the deploy and
  started after it, then the plan is read again, then the visit launches.
- **a-closing-game-is-waited-on-by-pid.** After the deploy's own stop, the wait reads the stopped pids by pid
  (`game_instance.alive`), never by owner: a closing RimWorld reads an empty command line before it leaves the process
  list, and on 2026-11-22 Pyrelands visit 5 was refused "game a could not be stopped for the deploy: Blind" on its own
  stopped game (pid 15352; item RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_SIX). The `/F` stop still goes
  through `game_instance.stop`, which reads the owner again, so nothing is signalled on a guess.
- **a-seatless-tick-stops-its-game.** The deploy's game stop hands the launch's seat to `game_instance.stop`, which
  passes it to `rimflow bridge idle` as `--seat`: the systemd tick names no seat in its env, and a seatless reading
  refused "I cannot tell which seat I am" (GimmeSomeSlack visit 2, 2026-11-21).
- **a-stale-companion-rebuilds-with-the-game-down.** A JawaBench companion that `companion_current` does not read
  FRESH, with the bridge free: the game is stopped if it is up, `bridgetools/build.py --gm --apply --instance <game>`
  runs once for the visit's game, the game is started again if it was up, the companion is read again, and the visit
  launches. On 2026-11-21 FlowWorks visit 3 was refused for a STALE companion with the bridge free and the fix named,
  and the tick never sends a refused input again (item RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FOUR).
  `build.py` reads only its own game's process: game b up never refuses game a's companion deploy
  (`game_a_deploy_ignores_game_b` in `src/RimMandrake/bridgetools/selftest_build_deploy.py`).
- **a-stale-companion-and-drift-share-one-restart.** A stale companion and loaded drift: one stop, the rebuild and the
  deploy, one start.
- **a-failed-companion-build-is-a-fault.** A rebuild that exits non-zero, or a companion still not current after it:
  REFUSED, naming the cause; not a wait.
- **a-stale-companion-on-a-held-game-waits.** His hold on the game: no rebuild and no stop; the refusal starts with
  `WAIT_MARK`.
- **a-repair-holds-the-game-for-its-whole-window.** The repair takes the game's driver lock before it stops the game,
  runs the rebuild and the deploy under that take (`RM_HOST_GUARD_GEN`, `RM_DRIVER_PID`, a seat), and frees the lock
  only after the game is up again. Without it, another run claimed ArchBig while it was down for Pyrelands visit 6's
  rebuild, and `build.py` refused the deploy (2026-11-22, 9:07 PM PST). `build.py` reads game a's lock held by its
  caller's take (inherited `RM_HOST_GUARD_GEN`, or an ancestor) as no hold, and another process's BENCH hold still as a
  hold: a seat name cannot tell two detached runs apart (`own_take_is_no_hold` in
  `src/RimMandrake/bridgetools/selftest_build_deploy.py`).
- **a-repair-on-a-game-another-run-holds-waits.** Another run's live lock: a wait (`WAIT_MARK`), the game left up and
  nothing rebuilt. A lock that could not be looked at is a fault named, with nothing done.
- **the-real-repair-lock-takes-and-frees-this-process.** `_repair_lock` holds the lock for this process, never its
  parent (the systemd tick's parent never exits); `game_instance.stop`'s gate passes that take; release frees it and
  restores the environment; another live process's lock reads as held.
- **a-failed-deploy-is-a-fault.** A deploy that exits non-zero: REFUSED, naming the deploy failure; not a wait.
- **a-blind-plan-is-could-not-look.** A plan that cannot run, or prints neither last line: REFUSED as could-not-look,
  never read as current, and no deploy is tried.
- **a-held-bridge-or-game-waits.** The bridge not takeable, or the game under his hold: no deploy, the refusal starts
  with `WAIT_MARK`, and the tick counts no fault and spends no try on it.
- **a-game-only-def-refuses.** A `-` line on a def XML that the repo never deleted: REFUSED, naming the file and
  `--pull`/`--prune`; no deploy.
- **an-empty-or-add-only-plan.** An empty drift list with "Everything in sync." reads current; a plan with only `+`
  lines on loaded files deploys.
- **drain-refusals-count-no-fault.** Three launches refused in a row by the account drain leave the mod's fault count
  0, spend no try, and read as a wait.
- **a-never-started-launch-owes-a-repair.** A launch that never started for any other reason counts no fault and
  owes one repair run (design/specs/2026-11-21-repair-at-the-refusal/boundary.md).
- **a-visit-item-name-passes-the-spawn-guard.** `maturation_dispatch.ingame_item_id` names only items the RUNNER spawn
  guard (`model.RUNNER_INGAME_NAME`) takes, also when the visit's two names are taken: after the 7:10 PM clear the bare
  `RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT` was refused at its spawn.
- **a-stale-walk-build-is-the-ticks-deploy.** An ended in-game visit whose one open reason is the stale walk folder
  launches no steward: the tick deploys it to ArchBig through `deploy_repair` (act `autodeploy`, no slot, no run). A
  held game is a wait that spends no try; a failed deploy, or a reading still stale after it, pauses the mod by name.
  With any other reason beside it, the steward reads the visit.
- **a-build-match-that-could-not-look-is-a-wait.** An ended in-game visit whose build match could not look (a read of
  an installed mod that keeps failing for want of memory, `modset_builder.AboutUnreadable`) launches no steward and no
  deploy, whatever other reasons stand beside it: the row waits, and the next tick reads it again. A build match that
  cannot run for any other cause still brings the steward.
- **about-read-waits-out-enomem.** `modset_builder.scan` reads a file or a folder again while it raises ENOMEM, and then
  raises; it never returns a map with that mod left out
  (its check: `src/RimMandrake/Utils/selftest_modset_about_enomem.py`). A malformed About.xml still reads "not installed".
- **the-tick-waits-on-a-drain.** While the drain notice stands, the tick launches nothing and every row it would have
  launched reads `account_hold`, "waiting: account switch".

## LIMITS

- A read of an installed mod is tried again after 0.5, 1, 2, 4 and 8 s (`modset_builder.ABOUT_WAITS`). Danger: a tick
  held by a read that never works. Evidence that the failure ends by itself within seconds: the same waits of
  `deploy_custom_mods._read_retry`, measured 2026-10-31; Biotech's and Anomaly's About.xml at 8:46 AM PST 2026-11-24.

- The game stop waits up to `REPAIR_STOP_S` = 120 s for the process to exit, then stops it with `/F`. Danger: a DLL
  written while the game holds it fails, and a game that ignores the close would hold the tick. Evidence: none
  measured for RimWorld's close time on this machine; the limit only bounds the wait, and the `/F` stop it falls back
  to is the one `game_instance.stop --force` already offers.

- The deploy and the companion rebuild each run for up to 1800 s. Danger: a hung `deploy_custom_mods.py` or
  `build.py` (a stuck Windows build server) would hold the tick for ever. Evidence: none measured for a hang; the
  limit is far above a normal run (a companion build is minutes), so it bounds a hang only.

Later lists beside this page: `polish.md`.
