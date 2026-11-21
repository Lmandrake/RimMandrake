# BOUNDARY: a refused launch that waits is not a fault; an in-game visit deploys what the game loads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`deploy_state`, `mod_deployed`, `deploy_repair`, the in-game branch of
`launch_mod`, `WAIT_MARK`), `src/RimMandrake/rimflow/maturation_autonomy.py` (`wait_refusal`, `_retriable`,
`_execute_one`), `src/RimMandrake/rimflow/maturation_dispatch.py` (`retriable`, `still_retried`, `launch_counted`,
`drain_gate` in `_tick`) and `src/RimMandrake/rimflow/run_void.py` (`sync_system`'s never-started branch).
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
- **the-tick-waits-on-a-drain.** While the drain notice stands, the tick launches nothing and every row it would have
  launched reads `account_hold`, "waiting: account switch".

## LIMITS

- The game stop waits up to `REPAIR_STOP_S` = 120 s for the process to exit, then stops it with `/F`. Danger: a DLL
  written while the game holds it fails, and a game that ignores the close would hold the tick. Evidence: none
  measured for RimWorld's close time on this machine; the limit only bounds the wait, and the `/F` stop it falls back
  to is the one `game_instance.stop --force` already offers.

Later lists beside this page: `polish.md`.
