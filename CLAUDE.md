# RimWorld 1.6 mod: GimmeSomeSlack (repo root is this clone)

You are the Ralph loop on the GimmeSomeSlack mod. `ralph/PROMPT.md` is your job. This file is how to run things.
Your mod: `src/RimMandrake/GimmeSomeSlack/` (packageId `mandrake.rm.gimmesomeslack`, namespace `RimMandrake.GimmeSomeSlack`; check the source before relying on the namespace).
Walk, north star and row meanings: `design/validation_walks/RimMandrake/GimmeSomeSlack.md`. Known limits: `src/RimMandrake/GimmeSomeSlack/KNOWN_LIMITS.md`.

## Facts you cannot guess
- Your game is SteveDesktop's, in `D:\SteamLibrary\steamapps\common\RimWorld\Mods` on that machine, never this repo. Writing a file is not deploying it. Archmagi's game is not yours to touch.
- Every DLC is assumed. Never test without them.
- You run in WSL on Archmagi. Everything that talks to the game runs on Steve, through `ralph/steve.sh run`. `python.exe` does not understand `/home/...` paths, so use paths relative to the repo root.
- A bridge call can report success and change nothing. Check the result on the map or in a screenshot.
- When something breaks, read the FIRST exception in `Player.log`, not the loudest.
- A patch that matches nothing logs nothing.
- Never guess a defName or field. Read the def or the decompiled source.

## Commands (run from the repo root)
```
python3 src/RimMandrake/Utils/winbuild.py GimmeSomeSlack                         build the C#
python3 src/RimMandrake/GimmeSomeSlack/validation.py                             offline checks
python3 src/RimMandrake/Utils/run_selftests.py --only <selftest paths>           offline tests
modcheck status GimmeSomeSlack                                                   last recorded run

```

## The game, on SteveDesktop
It lives on another machine and can die in minutes: read the section on it in `ralph/PROMPT.md`. Your build stays here (`winbuild.py` on Archmagi); `deploy` carries the DLL over. Steve has its own clone, `~/rm/gss`, at your branch plus your uncommitted `src/` and `ralph/` changes. Nothing else of yours is there.
```
ralph/steve.sh status                 uptime, last fault-canary cycle, game state, active mod count
ralph/steve.sh sync                   bring Steve's clone level with this one (it pushes ralph/gss)
ralph/steve.sh deploy                 sync, game down, deploy GimmeSomeSlack to Steve's game; follow with `up`
ralph/steve.sh tier                   game down, the small gimmesomeslack list (GSS, bridge, all DLC); follow with `up`
ralph/steve.sh up                     start the game and wait for the bridge (about 1 min on the small list)
ralph/steve.sh down                   stop it
ralph/steve.sh reboot                 restart the machine (about 6 min); game stays down
ralph/steve.sh run '<command>'        run it in ~/rm/gss on Steve. Use python.exe for anything that calls the bridge
ralph/steve.sh fetch '<path>' <dir>   copy a file or folder back, from a D:\ path or a repo-relative one
```
A live proof: run `python3 src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate` here first, then `ralph/steve.sh run 'python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --skip-offline --only core'`. Steve's WSL has no dotnet, so the offline gate belongs here. Don't record a run from it on the ledger. It took 185 s for `core` (47 rows) on 2026-11-07.
Steve's Saves folder holds only the `calm` test site (`RM_TestSite_calm_v3`, copied from Archmagi). A site save that isn't there makes `load_game` do nothing, and the proof polls its 420 s budget with no error. If you pick another site, scp it over first: read from Archmagi's Saves, write to `$RM_GAME_USERDATA/Saves` on Steve.
Shots land under `Transient/` in Steve's clone, and the proof's JSON under `northstar/` there: `fetch` them. Never read a shot's path as if it were on this machine.
Never wait on `pgrep -f` for a steve.sh command: your prompt holds that text, so it matches your own `claude -p` and never ends. steve.sh calls return when they are done.
Your own bridge script: put it under `ralph/live/`, `sync`, then `ralph/steve.sh run 'python.exe ralph/live/foo.py'`. The test lane's clone `~/rm/runner` is not yours: never write there. Don't take the bridge lock on Steve; the lane is paused and the game is yours.

Bridge client: `src/RimMandrake/Utils/rimbridge_client.py`. Screenshots: `rimworld/screenshot_cell_rect`.
Play zoom: the bar is about 64 px per cell, and a screenshot takes the CURRENT zoom unless you pass `rootSize`.

Traps the Graffiti loop already paid for:
- The screenshot tool writes asynchronously. Reuse a filename and you copy the LAST run's picture. Use unique capture names.
- Colonists draw at their last on-screen spot after an advance with the camera elsewhere. Don't read pawn positions from a shot.
- `bridge who` in this clone can show a stale hold. It frees after 45 minutes.
- `jawa/time_set_ticks` refuses on a populated map.
- Concurrent `codex_image` jobs need their own `--codex-home`, or they harvest each other's images.

Skills worth loading when you get there: `rimbridge`, `rimworld-live-review`, `rimworld-debug-testing`, `rimworld-modding`, `generating-rimworld-sprites`.

## New art: do it yourself, now
```
python3 skills/generating-images/scripts/codex_image.py generate --out <png> --prompt "<prompt>"
python3 skills/generating-images/scripts/codex_image.py edit --help
python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py --help
```
It blocks until the image exists. Wait for it, look at it, put it in `src/RimMandrake/GimmeSomeSlack/Textures/`, deploy it. There is no queue, ticket or review sheet for you to go through. Check `Textures/` first; what you need may already be there.

## Git
You are on branch `ralph/gss`. Commit often, by explicit path, and push with `git push origin ralph/gss`. Never push to `main`. Never force-push. No file over 50 MB.
Stay out of `infrastructure/state/` apart from what the bridge command writes itself; read the items there freely.

## Never
- Edit the `## north star` section of `design/validation_walks/RimMandrake/GimmeSomeSlack.md`.
- Drive Archmagi's game or its bridge, or work around `ralph/game_gate.py`.
- Copy a credential to SteveDesktop, or change its Windows settings.
- Live-test a flying creature's flight.
- Touch the saves named in `infrastructure/state/CANONICAL_SAVE.md`.
