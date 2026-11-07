# RimWorld 1.6 mod: Graffiti (repo root is this clone)

You are the Ralph loop on the Graffiti mod. `ralph/PROMPT.md` is your job. This file is how to run things.
Your mod: `src/RimMandrake/Graffiti/` (packageId `mandrake.rm.graffiti`, namespace `RimMandrake.Graffiti`).
Spec: `design/Jawa/graffiti_spec.md`. Older agent notes on what failed: top of `design/validation_walks/RimMandrake/Graffiti.md`.

## Facts you cannot guess
- The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, never this repo. Writing a file is not deploying it.
- Every DLC is assumed. Never test without them.
- Never fullscreen or focus the game window. The owner is using this machine.
- The game runs on Windows and you run in WSL. `python.exe` does not understand `/home/...` paths and writes CRLF.
- A bridge call can report success and change nothing. Check the result on the map or in a screenshot.
- When something breaks, read the FIRST exception in `Player.log`, not the loudest.
- `Plant` ticks only through `CompTickLong()`. A patch that matches nothing logs nothing.
- Never guess a defName or field. Read the def or the decompiled source.

## Commands (run from the repo root)
```
python3 src/RimMandrake/Utils/winbuild.py Graffiti                         build the C#
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Graffiti         dry run; add --apply to write
python3 src/RimMandrake/Utils/modset_builder.py --tier graffiti_solo --apply   small mod list (Graffiti, bridge, all DLC); the game must be down
python3 src/RimMandrake/rimflow/cli.py bridge take --for "Ralph Graffiti"  hold the game; release when you retire
./game                                                                     is the game up?
python3 src/RimMandrake/Utils/logwait.py "Bridge token:" --timeout 900     wait for a launch

python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Graffiti --tier graffiti_solo \
    --plan src/RimMandrake/Graffiti/northstar_plan.py --deploy-mod Graffiti
    one command: stop, small list, deploy, launch, quicktest, run the north-star suite. Bridge held first.
python3 src/RimMandrake/Utils/run_selftests.py --only <selftest paths>     offline tests
modcheck status Graffiti                                                   last recorded run
```
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
- Live-test a flying creature's flight.
- Touch the saves named in `infrastructure/state/CANONICAL_SAVE.md`.
