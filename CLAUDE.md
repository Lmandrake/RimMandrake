# RimWorld 1.6 mod: Graffiti (repo root is this clone)

You are the Ralph loop on the Graffiti mod. `ralph/PROMPT.md` is your job. This file is how to run things.
Your mod: `src/RimMandrake/Graffiti/` (packageId `mandrake.rm.graffiti`, namespace `RimMandrake.Graffiti`).
Spec: `design/Jawa/graffiti_spec.md`. Older agent notes on what failed: top of `design/validation_walks/RimMandrake/Graffiti.md`.

## Facts you cannot guess
- Your game is game B on SteveDesktop. It reads `D:\SteamLibrary\steamapps\common\RimWorld\Mods` on that machine, never this repo. Writing a file is not deploying it. Game A on that machine and Archmagi's game are not yours to touch.
- Every DLC is assumed. Never test without them.
- Never fullscreen or focus a game window.
- You run in WSL on Archmagi. Everything that talks to the game runs on Steve, through `ralph/steve.sh run`. `python.exe` does not understand `/home/...` paths and writes CRLF, so use paths relative to the repo root.
- A bridge call can report success and change nothing. Check the result on the map or in a screenshot.
- When something breaks, read the FIRST exception in `Player.log`, not the loudest.
- `Plant` ticks only through `CompTickLong()`. A patch that matches nothing logs nothing.
- Never guess a defName or field. Read the def or the decompiled source.

## Commands (run from the repo root)
```
python3 src/RimMandrake/Utils/winbuild.py Graffiti                         build the C#
python3 src/RimMandrake/Utils/run_selftests.py --only <selftest paths>     offline tests
modcheck status Graffiti                                                   last recorded run
```

## The game, game B on SteveDesktop
It lives on another machine and can die in minutes: read the section on it in `ralph/PROMPT.md`. Your build stays here (`winbuild.py` on Archmagi); `deploy` carries it over. Steve has its own clone, `~/rm/gameb`, at your branch plus your uncommitted `src/` and `ralph/` changes. Nothing else of yours is there.
```
ralph/steve.sh status                 uptime, last fault-canary cycle, game B's state, active mod count
ralph/steve.sh sync                   bring Steve's clone level with this one (it pushes ralph/graffiti)
ralph/steve.sh deploy                 sync, game B down, deploy Graffiti to that machine's Mods; follow with `up`
ralph/steve.sh tier                   game B down, the small graffiti_solo list (Graffiti, bridge, all DLC); follow with `up`
ralph/steve.sh up                     start game B and wait for the bridge
ralph/steve.sh down                   stop game B; game A stays up
ralph/steve.sh run '<command>'        run it in ~/rm/gameb on Steve with game B's environment. Use python.exe for anything that calls the bridge
ralph/steve.sh fetch '<path>' <dir>   copy a file or folder back, from a D:\ path or a repo-relative one
```
A live run, after `deploy` and `up`:
```
ralph/steve.sh run 'python.exe src/RimMandrake/bridgetools/prove_quicktest_world.py'
ralph/steve.sh run 'python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Graffiti --plan src/RimMandrake/Graffiti/northstar_plan.py'
```
Those are the last two steps of `live_session.py`. Don't use it here: it stops at the ledger's bridge hold, and `steve.sh` does its other steps. Don't record a run from it on the ledger.
Game B's own folder is `D:\ClaudeWork\rimmandrake\instances\b` on Steve (`$RM_GAME_USERDATA` inside `ralph/steve.sh run`), with its `Player.log`, `Saves` and `JawaBench` folders. Its Saves folder starts empty. A site save that isn't there makes `load_game` do nothing, so scp one over first if you need it, reading from Archmagi's Saves.
Shots land under `Transient/` in Steve's clone, and a run's JSON under `Transient/northstar/` there: `fetch` them. Never read a shot's path as if it were on this machine.
Never wait on `pgrep -f` for a steve.sh command: your prompt holds that text, so it matches your own `claude -p` and never ends. steve.sh calls return when they are done.
Your own bridge script: put it under `ralph/live/`, `sync`, then `ralph/steve.sh run 'python.exe ralph/live/foo.py'`. Don't write in Steve's other clones, `~/rm/runner` and `~/rm/gss`. Don't take the bridge lock on Steve: game B is yours, and `steve.sh` holds that game's lock itself for each `up` and `down`.
Bridge client: `src/RimMandrake/Utils/rimbridge_client.py`. See `src/RimMandrake/Graffiti/graffiti_v1_live_proof.py` for working calls, including screenshots via `rimworld/screenshot_cell_rect`.
Play zoom: the bar is about 64 px per cell, and a screenshot takes the CURRENT zoom unless you pass `rootSize`.

Skills worth loading when you get there: `rimbridge`, `rimworld-live-review`, `rimworld-debug-testing`, `rimworld-modding`, `generating-rimworld-sprites`.

## New art: do it yourself, now
```
python3 skills/generating-images/scripts/codex_image.py generate --out <png> --prompt "<prompt>"
python3 skills/generating-images/scripts/codex_image.py edit --help
python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py --help
```
It blocks until the image exists. Wait for it, look at it, put it in `src/RimMandrake/Graffiti/Textures/`, deploy it. There is no queue, ticket or review sheet for you to go through. Check `src/RimMandrake/Graffiti/Textures/` first; what you need may already be there.

## Git
You are on branch `ralph/graffiti`. Commit often, by explicit path, and push with `git push origin ralph/graffiti`. Never push to `main`. Never force-push. No file over 50 MB.
Stay out of `infrastructure/state/` apart from what the bridge command writes itself.

## Never
- Edit the `## north star` section of `design/validation_walks/RimMandrake/Graffiti.md`.
- Drive Archmagi's game or SteveDesktop's game A, reach their bridges, or work around `ralph/game_gate.py`.
- Copy a credential to SteveDesktop, change its Windows settings, or reboot it.
- Live-test a flying creature's flight.
- Touch the saves named in `infrastructure/state/CANONICAL_SAVE.md`.
