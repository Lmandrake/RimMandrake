# Lane steve: the live FlowWorks loop on SteveDesktop's game

You work FlowWorks items (ids matching `infrastructure/state/flowworks_lane.json`), built/validated needs=bridge items
first. You run on Archmagi, but the game you drive is SteveDesktop's game A, and only that one, through
`infrastructure/whittle_claude/steve.sh` (run it with no argument for its verbs). Archmagi's game belongs to
CLAUDE_ARCHMAGI_FWLIVE: never `./game`, `deploy_custom_mods.py --apply`, `modset_builder.py --apply`, `live_session`,
rimbridge or a proof script on Archmagi (the clone's gate hook refuses them). Game B on SteveDesktop is not yours either.

## Using the game
1. `rimflow bridge who --host stevedesktop`. Free or your own: `rimflow bridge take --host stevedesktop --idle-ok --for
   "<ID>: <what>"`. Held by another seat (the testq runner, the owner, a window): do not force it; do the item's offline
   part, note the live step, end the round (the wrap-up calls it failed with "Steve's game held by X").
2. `infrastructure/whittle_claude/steve.sh sync` brings your clone's committed and uncommitted src/ and whittle/ work to
   SteveDesktop's clone `~/rm/claude-fwlive`. C# is built here on Archmagi (`python3 src/RimMandrake/Utils/winbuild.py`)
   and the built DLLs travel with the sync.
3. `steve.sh deploy` (sync, game down, deploy FlowWorks on Steve), then `steve.sh up` (applies the FlowWorks tier first if
   another loop left its own mod list, then starts the game and waits for the bridge).
4. `steve.sh run '<command>'` runs a proof script, modcheck or any bridge call in Steve's clone; the guard generation of
   your take is passed along, so it counts as your drive. `steve.sh fetch <Steve path> <local dir>` copies evidence
   back: put it under `/mnt/d/ClaudeWork/rimmandrake/whittle_claude/$RIMFLOW_SEAT/`.
5. A long proof: load `live-debugging-proof-harness` once, read the proof script and the site first, classify every
   finding MOD, SITE or HARNESS. `steve.sh status` when the game looks gone; `steve.sh restart` to recover. There is no
   reboot verb: a machine reboot drops game B too.
6. Before you stop: `rimflow bridge release --host stevedesktop`. Leave game A up.

SteveDesktop being unreachable (steve.sh exit 75, STEVE_UNREACHABLE) is weather: do the offline part and end the round.
Never test a flyer's flight live.
