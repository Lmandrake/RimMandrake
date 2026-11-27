# One-call walk staging: boundary page

Code: `src/RimMandrake/Utils/walk_stage.py`. Tests: `src/RimMandrake/Utils/selftest_walk_stage.py` (offline) and
`walk_stage.py accept <Mod> --game <free game>` (live; it writes `design/concepts/<Mod>/version/walk_stage_accept.json`,
and `walk_stage.py verify <Mod>` reads that record). Item: `RIMMANDRAKE_BUILD_ONE_CALL_WALK_STAGING_NO_MODEL_HE_WAITED_FORTY_MINUTES`.

The owner's question, 2026-11-24 9:45 AM PST: *"Boy it feels like writing a testing environment should just be a Python
call -> BRIDGE -> done in under a minute. What are all the delays as it works? Why are LLM calls being used to set up a
testing environment for GSS?"*

## Where the 42 minutes went (Gimme Some Slack 0.2.0 walk, ArchSmall, 2026-11-24)

Read from the timestamps of the model helper's own transcript (`agent-aab61463dec693bf5.jsonl` under the bench seat's
session `6fa1d8fe`), 8:58 to 9:43 AM PST. Each row is wall time.

| span (PST) | minutes | what | kind |
|---|---|---|---|
| 8:58-9:03 | 5 | read the ruling, the brief, the mod's patches, modset_builder, game_instance, the review skill; work out which mods the small list holds | model reading |
| 9:03-9:06 | 3 | write `small_list.json`, tier `gimmesomeslack_walk` and its selftest; publish (2.5 of the 3) | a missing piece, made once |
| 9:06-9:10 | 4 | deploy (3 min) and two hash checks of the deploy | machine (3) + model (1) |
| 9:10-9:14 | 4 | write ModsConfig; find and fix a fault (the swap books of ArchSmall overwrote ArchBig's), test first | a tool fault, fixed once |
| 9:14-9:15 | 0.7 | launch ArchSmall | machine |
| 9:15-9:17 | 2 | find how the walk map is built (human_review.py, visit 2's stand_020.py); write a driver script | model reading |
| 9:17-9:20 | 3.2 | rebuild the walk map (175 s) and its stands (12 s); sweep, pause, save | machine |
| 9:20-9:30 | 10 | read the log, write a capture script, judge station 32, a census, relight lamps that were not lit (they need ticks), draft the colonists | model judging and repair |
| 9:30-9:33 | 3 | try to capture the Restyle menu (the bridge cannot hold it open) | model |
| 9:33-9:37 | 4 | file two lessons and an item; edit the walk brief | paperwork |
| 9:37-9:43 | 6 | selftests, publish (2 min), a note (2 min), release | paperwork |

Machine work: about 8 minutes (deploy 3, list 0.5, launch 0.7, rebuild 3.2, captures under 1). The other 34 minutes were
a model reading code to learn steps that do not change between walks, two one-time fixes, judging, and paperwork.
`walk_stage.py` does the machine steps alone and reads the steps from data. A walk whose save is on the list and whose
game is up on that list costs: list 16 s, deploy plan 80 s (measured 2026-11-26 on ArchSmall, in sync), load, sweep,
pause and 38 captures. A restart adds the cold load; a rebuild adds about 3 minutes. The deploy plan is the slowest
fixed step: its def guard reads every mod over the Windows mount.

## ACCEPTS

- **a-mod-with-two-files.** `<Mod>` with `design/concepts/<Mod>/version/small_list.json` (a modset_builder tier) and
  `design/concepts/<Mod>/version/walk_stage.json`: `save` (the walk save's name, no `.rws`), `stations` (`name`, `rect` =
  x, z, w, h), and optional `rebuild` (`steps`: `{run: <repo path of a python.exe script>, args}` or `{ticks: N}`;
  `save_as`). `{out}` in an arg is the capture folder.
- **a-game-name.** `--game` ArchBig or ArchSmall, in any letter case.
- **a-planted-file.** `--spec` and `--config` read another file instead (a test plants a fault there). `--rebuild`
  rebuilds even when the save is on the list.

## DOES NOT SURVIVE (not handled)

- **a-hung-step.** A rebuild script that does not end in 2400 s, or a bridge phase that does not end in 6000 s: the hang
  guard stops it, `NOT READY ... (the hang guard)`, exit 2.
- **a-silent-bridge.** A game whose bridge does not answer: exit 2, never READY.
- **a-taste-call.** It does not judge what the captures show. A taste call on a capture is a judge's.

## PROMISES (each one is owed a test of the same name)

- **a-missing-mod-is-named.** A needed mod that is not installed on the game, or a mod that small_list.json names and
  the resolved list lacks, stops the run before the game lock is taken: exit 1, and the NOT READY line names the mod.
- **the-save-is-loaded-only-on-the-list.** The save is loaded when its header holds the list; a header that lacks only
  harness mods (bridge, zoom, Character Editor) is loaded and saved once as `<save>_SMALL`, which later runs load first;
  any other difference, an unreadable header or no file is a rebuild.
- **a-save-comes-with-its-labels.** A save in the other game's Saves is copied in with its sign sidecar (the station
  labels); a save already here is never overwritten.
- **a-game-on-the-list-is-reused.** A game that is up, runs the list (jawa/running_mods) and got no new deploy is reused;
  else it is stopped by pid, ModsConfig is written and read back, and it is launched.
- **a-bad-config-is-refused-by-name.** A walk_stage.json with no save, a bad rect, a repeated station or a bad rebuild
  step is refused with the fault named; an unreadable one is COULD NOT LOOK.
- **a-logged-exception-is-found.** The first exception line of the cold load's Player.log is found; a clean log has none.
- **no-step-names-a-model-door.** The stager names no model door (claude, codex, an API, a helper launcher).
- **the-model-watch-can-see.** The live acceptance's watch sees a claude child in the command's process tree, and sees
  none when there is none.
- **the-acceptance-verdict-needs-every-row.** The acceptance is PASS only when every row below passes.
- **a-station-past-the-map-edge-is-clamped.** A station rect is cut to the map's cells before its capture; a rect with
  no cell on the map is named as a missing capture.
- **an-unknown-game-is-refused-by-name.** `--game` with a name that is no game: exit 1, the name in the line.

## Live acceptance (`walk_stage.py accept`, recorded in walk_stage_accept.json)

Rows: `planted_exits_nonzero`, `planted_names_the_mod`, `real_exits_0_ready`, `read_save_loaded` (a fresh bridge read,
another process: the save named and Playing), `read_paused`, `read_zero_hostiles`, `capture_per_station` (one picture
file per station, on disk), `no_model_process`. READY is printed only after the bridge reads the save loaded and Playing,
0 hostile pawns, the tick unmoved over 2 s and after the captures, one picture per station, and no exception since the
load (jawa/first_exception) or in the cold load's Player.log. The game is held for the whole staging (game_lock.run): a
held game is refused, exit 75, and work goes to another game.
