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

## Screenshots and modal dialogs (read before any live look)
- Load `rimbridge` and `rimworld-live-review` once before a live look. `jawa/clear_ui` first (the dev log window sits in frame), frame with a camera tool (`jawa/jump_camera_to_cell`, `rimworld/set_camera_zoom`; take_screenshot ignores x/z/zoom), then:
  `python.exe "$(wslpath -w src/RimMandrake/Utils/rimbridge_client.py)" --call jawa/take_screenshot --json '{"fileName":"<bare_name>"}' --yes-i-know-this-is-live`
  (`.png` is appended; the result's `filePath` is a Windows path under `...\RimWorld by Ludeon Studios\Screenshots\`; `wslpath -u` it, copy under `/mnt/d/ClaudeWork/rimmandrake/whittle_claude/$RIMFLOW_SEAT/`). Then LOOK at the PNG with the Read tool before you claim any visual bar; success:true is not a picture.
- Whole desktop incl. dialogs: `python.exe "$(wslpath -w src/RimMandrake/Utils/system_screenshot.py)" 'D:\ClaudeWork\rimmandrake\whittle_claude\x.bmp'` (WSL `python3` only prints "Windows-only").
- After any new colony or map call `jawa/name_colony` (factionName, settlementName): the naming dialog `Dialog_NamePlayerFactionAndSettlement` force-pauses and re-raises every ~1000 ticks until named; closing never sticks. Stuck already: `jawa/name_colony` then `rimworld/close_window`.
- Before trusting a timed run, `rimworld/get_ui_state`: `windowsForcePause=true` means a blocked run, not a result. Fix table: `skills/northstar-validation/SKILL.md` row `modal_open`; `belt_watchdog.py` BAD_MODALS.
