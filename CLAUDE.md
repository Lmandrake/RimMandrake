# RimWorld 1.6 mod: GimmeSomeSlack (repo root is this clone)

You are the Ralph loop on the GimmeSomeSlack mod. `ralph/PROMPT.md` is your job. This file is how to run things.
Your mod: `src/RimMandrake/GimmeSomeSlack/` (packageId `mandrake.rm.gimmesomeslack`, namespace `RimMandrake.GimmeSomeSlack`; check the source before relying on the namespace).
Walk, north star and row meanings: `design/validation_walks/RimMandrake/GimmeSomeSlack.md`. Known limits: `src/RimMandrake/GimmeSomeSlack/KNOWN_LIMITS.md`.

## Facts you cannot guess
- The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, never this repo. Writing a file is not deploying it.
- Every DLC is assumed. Never test without them.
- Never fullscreen or focus the game window. The owner uses this machine.
- The game runs on Windows and you run in WSL. `python.exe` does not understand `/home/...` paths and writes CRLF.
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

Game commands, refused while the Graffiti loop runs:
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod GimmeSomeSlack         dry run; add --apply to write
python3 src/RimMandrake/Utils/modset_builder.py --tier gimmesomeslack --apply    small mod list (GSS, bridge, all DLC); the game must be down
python3 src/RimMandrake/rimflow/cli.py bridge take --for "Ralph GSS"             hold the game; release when you retire
./game                                                                           is the game up?
python3 src/RimMandrake/Utils/logwait.py "Bridge token:" --timeout 900           wait for a launch
python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live          the live proof, once launched
```
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
- Drive the game or the bridge while `ralph/game_gate.py` refuses it, or work around that gate.
- Live-test a flying creature's flight.
- Touch the saves named in `infrastructure/state/CANONICAL_SAVE.md`.
