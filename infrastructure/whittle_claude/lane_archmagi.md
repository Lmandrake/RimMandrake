# Lane archmagi: the live FlowWorks loop on Archmagi's game

You work FlowWorks items (ids matching `infrastructure/state/flowworks_lane.json`), built/validated needs=bridge items
first. The game you may drive is Archmagi's RimWorld and only that one. SteveDesktop's game belongs to
CLAUDE_STEVEDESKTOP_FWLIVE: never touch `infrastructure/whittle_claude/steve.sh`, ssh to stevedesktop, or
`--host stevedesktop` (the clone's gate hook refuses them).

## Using the game
1. `rimflow bridge who`. Free, or held by your own seat: `rimflow bridge take --idle-ok --for "<ID>: <what>"`. Held by
   another seat (the owner, BENCH, a window): do not wait on it and do not force it; do the item's offline part, note
   the live step, and end the round (the wrap-up calls it failed with "bridge held by X").
2. Deploy what you changed: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks` (plan; read it,
   refuse another seat's files), then `--apply`. C#: `python3 src/RimMandrake/Utils/winbuild.py` first.
3. The mod list: the small all-DLC FlowWorks tier, `python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks
   --apply` (read `--help`; a game load is ~30 s on it, against ~25 min on the owner's full list).
   `python3 src/RimMandrake/Utils/preflight_bridge.py --help` says how to check the bridge before a long run.
4. Start the game: `python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils/northstar_driver'); import live_session as L; L.launch_and_wait()"`
   (or `live_session.py --mod FlowWorks --tier flowworks --plan <plan>` for a north-star plan: read its docstring; it
   stops, tiers, deploys, launches and runs in one command). Mark the game state in the ledger with `./game up|down`
   (`./game --help`); `./game --why` writes an OWNER.jsonl DOWN event: commit it.
5. A long proof: load `live-debugging-proof-harness` once, read the proof script and the site first, classify every
   finding MOD, SITE or HARNESS.
6. Before you stop: `rimflow bridge release`. Leave the game up with the FlowWorks tier unless the item ended with the
   game in a broken state; then stop it (`live_session.stop_game()`) and mark it `./game --why "..." down`.

Never test a flyer's flight live. A dev quicktest colony (`rimworld-debug-testing`) is the usual site.
