# RimWorld 1.6 biome: Pyrelands (repo root is this clone)

You are the Artisan loop on Pyrelands. `ralph/PROMPT.md` is your job. This file is how to run things.
Your source: `src/RimMandrake/Pyrelands/`. It never deploys alone: the biome ships COMPOSED inside `mandrake.rm.biomes` (`src/RimMandrake/Biomes.compose.json`). Read the `subject:` to `list:` header of `design/validation_walks/RimMandrake/Pyrelands.md`, and the top of `src/RimMandrake/Pyrelands/northstar_plan.py`, which explains the run and its long chains.

## Facts you cannot guess
- The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, never this repo. Writing a file is not deploying it.
- Every DLC is assumed. Never test without them.
- Never fullscreen or focus the game window. The owner uses this machine.
- The game runs on Windows and you run in WSL. `python.exe` does not understand `/home/...` paths and writes CRLF.
- A bridge call can report success and change nothing. Check the result on the map or in a screenshot.
- When something breaks, read the FIRST exception in `Player.log`, not the loudest.
- `Plant` ticks only through `CompTickLong()`. A patch that matches nothing logs nothing. `MayRequire` on a top-level `<Operation>` is ignored.
- The real animal cast is patch-added (`UtinniPatches/Patches/WildAnimals_Pyrelands.xml`), so reading the BiomeDef alone shows the wrong half.
- A map censuses as contaminated if its neighbouring tiles are other biomes. See the walk's note, and use the site in `northstar_site.py`.
- This biome has few or zero tiles on the planet today, and that is expected: the planet is painted once, at the very end. Never paint or generate the world, and never point it at another biome to make it appear.
- Never guess a defName or field. Read the def or the decompiled source.

## Commands (run from the repo root)
```
python3 src/RimMandrake/Utils/winbuild.py <csproj or mod>                          build the C#
python3 src/RimMandrake/Pyrelands/validation.py --help                             offline checks
python3 src/RimMandrake/Utils/run_selftests.py --only <selftest paths>             offline tests
modcheck status Pyrelands                                                          last recorded run

Game commands, refused while a loop ahead of you runs:
python3 src/RimMandrake/rimflow/cli.py bridge take --for "Artisan Pyrelands"       hold the game; release when you retire
python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Pyrelands --tier pyrelands \
    --plan src/RimMandrake/Pyrelands/northstar_plan.py --compose                   stop, small list, deploy, launch, run the suite (see --help)
python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes               composed deploy, dry run; add --apply to write
python3 src/RimMandrake/Utils/modset_builder.py --tier pyrelands --apply           small mod list; the game must be down
./game                                                                             is the game up?
python3 src/RimMandrake/Utils/logwait.py "Bridge token:" --timeout 900             wait for a launch
```
These environment settings are already made for you: a Windows PATH, and `RIMFLOW_SEAT=BENCH`.
Bridge client: `src/RimMandrake/Utils/rimbridge_client.py`. Screenshots: `rimworld/screenshot_cell_rect`.
Play zoom: the bar is about 64 px per cell, and a screenshot takes the CURRENT zoom unless you pass `rootSize`.

Traps earlier loops already paid for:
- The screenshot tool writes asynchronously. Reuse a filename and you copy the LAST run's picture. Use unique capture names.
- Colonists draw at their last on-screen spot after an advance with the camera elsewhere. Don't read pawn positions from a shot.
- `bridge who` in this clone can show a stale hold. It frees after 45 minutes.
- `jawa/time_set_ticks` refuses on a populated map.
- A launch that runs past your own time limit leaves the game at the main menu. Use the normal limit.
- Downed or attacked colonists can cut a long run short. Check the site's vitals when a block ends early.
- Concurrent `codex_image` jobs need their own `--codex-home`, or they harvest each other's images.

Skills worth loading when you get there: `rimbridge`, `rimworld-live-review`, `rimworld-debug-testing`, `rimworld-modding`, `generating-rimworld-sprites`.

## New art: do it yourself, now
```
python3 skills/generating-images/scripts/codex_image.py generate --out <png> --prompt "<prompt>"
python3 skills/generating-images/scripts/codex_image.py edit --help
python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py --help
```
It blocks until the image exists. Wait for it, look at it, put it in the right `Textures/` folder, deploy it. There is no queue, ticket or review sheet for you to go through. Check first; what you need may already be there.

## Git
You are on branch `ralph/pyrelands`. Commit often, by explicit path, and push with `git push origin ralph/pyrelands`. Never push to `main`. Never force-push. No file over 50 MB.
Stay out of `infrastructure/state/` apart from what the bridge command writes itself; read the items there freely.

## Never
- Edit the `## north star` section of `design/validation_walks/RimMandrake/Pyrelands.md`.
- Live-test or try to photograph a flying creature's flight. The fire-hawk included. The owner must be present for that. Check flight by reading `Pawn_FlightTracker` state, and judge its ember-carrying by what lands and burns.
- Paint, generate or edit the planet.
- Touch the saves named in `infrastructure/state/CANONICAL_SAVE.md`.
