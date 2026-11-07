# RimWorld 1.6 mod: FlowWorks (repo root is this clone)

You are the Artisan loop on the FlowWorks mod. `ralph/PROMPT.md` is your job. This file is how to run things.
Your mod: `src/RimMandrake/FlowWorks/` (packageId `mandrake.rm.flowworks`, namespaces `RimMandrake.FlowWorks.*`; check the source before relying on one).
Walk, north star and row meanings: `design/validation_walks/RimMandrake/FlowWorks.md`. The pit's authority is `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`, not the older pit spec.

## Facts you cannot guess
- Your game is SteveDesktop's game A, in `D:\SteamLibrary\steamapps\common\RimWorld\Mods` on that machine, never this repo. Writing a file is not deploying it. Archmagi's game is not yours to touch.
- Game B on the same machine is the Graffiti loop's. Both games read that one `Mods` folder; game B's list loads neither FlowWorks nor GimmeSomeSlack, so deploying FlowWorks doesn't touch it. Deploy only FlowWorks.
- `src/RimMandrake/_Shared/SlackGeometry/` is compiled into both FlowWorks and GimmeSomeSlack, and the GSS loop is changing it on its own branch. Don't edit it. If you truly must, say so in `ralph/PROGRESS.md`, because both DLLs then need rebuilding at landing.
- Every DLC is assumed. Never test without them.
- You run in WSL on Archmagi. Everything that talks to the game runs on Steve, through `ralph/steve.sh run`. `python.exe` does not understand `/home/...` paths, so use paths relative to the repo root.
- A bridge call can report success and change nothing. Check the result on the map or in a screenshot.
- When something breaks, read the FIRST exception in `Player.log`, not the loudest.
- A patch that matches nothing logs nothing. `MayRequire` on a top-level `<Operation>` is ignored.
- Never guess a defName or field. Read the def or the decompiled source.

## Commands (run from the repo root)
```
python3 src/RimMandrake/Utils/winbuild.py FlowWorks                              build the C# (staged on D:\ClaudeWork\rimmandrake\build)
python3 src/RimMandrake/Utils/selftest_flowworks_stock.py                        the C# self-test (Source/SelfTest), with planted faults
python3 src/RimMandrake/Utils/run_selftests.py --only <selftest paths>           offline tests (src/RimMandrake/FlowWorks/selftest_*.py, northstar/selftest_*.py)
python3 src/RimMandrake/FlowWorks/validation.py                                  which proof row is evidence for which bar
modcheck status FlowWorks                                                        last recorded run (reads RED)
```
A committed DLL travels with its `.srchash`: rebuild with `winbuild.py` after any C# change, then commit both.

## The game, on SteveDesktop
It lives on another machine and can die in minutes: read the section on it in `ralph/PROMPT.md`. Your build stays here (`winbuild.py` on Archmagi); `deploy` carries the DLL over. Steve has its own clone, `~/rm/flowworks`, at your branch plus your uncommitted `src/` and `ralph/` changes. Nothing else of yours is there.
```
ralph/steve.sh status                 uptime, last fault-canary cycle, game A's state, active mod count
ralph/steve.sh sync                   bring Steve's clone level with this one (it pushes ralph/flowworks)
ralph/steve.sh deploy                 sync, game A down, deploy FlowWorks to Steve; follow with `up`
ralph/steve.sh tier                   game A down, the small flowworks list (FlowWorks, GSS, bridge, all DLC); follow with `up`
ralph/steve.sh up | down | restart    start game A and wait for the bridge | stop it, by pid | both
ralph/steve.sh run '<command>'        run it in ~/rm/flowworks on Steve. Use python.exe for anything that calls the bridge
ralph/steve.sh fetch '<path>' <dir>   copy a file or folder back, from a D:\ path or a repo-relative one
```
There is no reboot verb, on purpose: a reboot drops game B with it. Restart the game, not the machine.
On 2026-11-07 game A was left up on GSS's own list (10 mods). The first time, run `tier`, then `deploy`, then `up`; GSS rides along on the `flowworks` list because the bridge's playtest tools need its types.
The core live proof is `src/RimMandrake/FlowWorks/northstar/validation_v2.py` (offline tier and `--mock` here first; `--live --fresh-map` on Steve). The pit scripts are in `src/RimMandrake/FlowWorks/northstar/` (`pit_superdeep_walk.py`, `climb_proof.py`, `trench_cover_proof.py`, `proof_pit_lip_cover.py`, `raid_trench_proof.py`, `suspension_bridge_proof.py`, `pit_rescue_live.py` and more). Don't record a run from Steve on the ledger.
Steve's Saves folder held only the `calm` test site (`RM_TestSite_calm_v3`) on 2026-11-07. A site save that isn't there makes `load_game` do nothing, and a proof polls its budget with no error. If you need another site, scp it over first: read from Archmagi's Saves, write to `$RM_GAME_USERDATA/Saves` on Steve.
Shots land under `Transient/` in Steve's clone: `fetch` them. Never read a shot's path as if it were on this machine.
Never wait on `pgrep -f` for a steve.sh command: your prompt holds that text, so it matches your own `claude -p` and never ends. steve.sh calls return when they are done.
Your own bridge script: put it under `ralph/live/`, `sync`, then `ralph/steve.sh run 'python.exe ralph/live/foo.py'`. Don't take the bridge lock on Steve; its test lane is paused and game A is yours.
The gate matches the names of the live scripts anywhere in a local command, a `grep` included. Open those files with Read.

Bridge client: `src/RimMandrake/Utils/rimbridge_client.py`. Screenshots: `rimworld/screenshot_cell_rect`.
Play zoom: the bar is about 64 px per cell, and a screenshot takes the CURRENT zoom unless you pass `rootSize`.

Traps earlier loops already paid for:
- The screenshot tool writes asynchronously. Reuse a filename and you copy the LAST run's picture. Use unique capture names.
- Colonists draw at their last on-screen spot after an advance with the camera elsewhere. Don't read pawn positions from a shot.
- `jawa/time_set_ticks` refuses on a populated map.
- Concurrent `codex_image` jobs need their own `--codex-home`, or they harvest each other's images.
- A long bridge script: write its output to a file and run it in the background with a long timeout. Piping through `cut` hides everything. A killed script leaves the game running, so pause it.
- The self-test log from `dotnet.exe` has bytes that make plain `grep` silent: use `grep -a`. To pass an env var into a Windows `.exe` from WSL: `WSLENV=NAME NAME=1 ...`.
- When the gate delivers a note or a context warning it refuses the WHOLE command: run it again.
- `steve.sh fetch` one file at a time is slow: tar a prefix on Steve with `run`, fetch the tar once.
- Decompiled RimWorld: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse}/`.

Skills worth loading when you get there: `rimbridge`, `rimworld-live-review`, `rimworld-debug-testing`, `rimworld-modding`, `live-debugging-proof-harness`, `generating-rimworld-sprites`, `telemetry`.

## New art: do it yourself, now
```
python3 skills/generating-images/scripts/codex_image.py generate --out <png> --prompt "<prompt>"
python3 skills/generating-images/scripts/codex_image.py edit --help
python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py --help
```
It blocks until the image exists. Wait for it, look at it, put it in `src/RimMandrake/FlowWorks/Textures/`, deploy it. There is no queue, ticket or review sheet for you to go through. Check `Textures/` first; what you need may already be there.

## Git
You are on branch `ralph/flowworks`. Commit often, by explicit path, and push with `git push origin ralph/flowworks`. Never push to `main`. Never force-push. No file over 50 MB.
Stay out of `infrastructure/state/` apart from what the bridge command writes itself; read the items there freely.

## Never
- Edit the `## north star` section of `design/validation_walks/RimMandrake/FlowWorks.md`.
- Drive Archmagi's game or its bridge, touch game B, or work around `ralph/game_gate.py`.
- Reboot SteveDesktop, copy a credential to it, or change its Windows settings.
- Kill a game by image name (`taskkill /IM`): that takes game B too.
- Live-test a flying creature's flight.
- Touch the saves named in `infrastructure/state/CANONICAL_SAVE.md`.
