# RimBridge traps: loading, readiness, saves, maps and bridge time (ticks, pause)

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

## `token=NO` during a load is the game still loading, not the WSL bug
**Symptom:** `resolve_endpoint()` returns `127.0.0.1:5174` with **no token** and the first call dies with `AttributeError: 'NoneType' object has no attribute 'sendall'` — character-for-character the WSL-cannot-reach-the-bridge rule in `SKILL.md` §1, so you switch to `python.exe`, get the identical failure, and go hunting a networking problem that does not exist.
**Cause:** when you are already under `python.exe`, RimBridgeServer has not started yet. A cold load on this stack is 23–30 minutes and the bridge comes up late; `resolve_endpoint()` scrapes host/port/token out of `Player.log`, so before the startup line there is nothing to scrape. **An empty token is the tell** — a running bridge always has one.
**Fix:** settle it from the log before blaming the transport — `stat -c '%y %s' "$LOG"` (mtime ~now and small = still loading), `grep -ci rimbridge "$LOG"` (0 = server not started), `tail -3 "$LOG"` (def-loading lines = still in defs). A log being written **now** with no `rimbridge` line is a game mid-load; a **stale** log with no line is a game that is down.
**Recurs when:** two causes wearing one symptom — the symptom cannot be the diagnosis, so reach for the discriminator rather than the more familiar cause. `RimWorldWin64.exe` existing is not the service being ready.

## 🔴 `Player.log` PERSISTS between runs — the readiness grep matches the LAST session

Grepping `Player.log` for `GABP server running standalone` to know the bridge is up
**returns instantly on a stale line from the previous run**, before the new game has even
started. You then connect, get `ConnectionRefused`, and go looking for a bridge fault that
does not exist.

**Wait for the log to TRUNCATE first.** `src/RimMandrake/bridgetools/launch_and_wait.sh`
records the size, waits for it to shrink, and only then looks for the marker.

## ⚠️ An "ended" GameCondition still lists while the game is PAUSED

There is no `EndNow()`. Ending sets `Duration = TicksPassed`, which expires on the **next
tick** — so a paused game still shows it in `ActiveConditions` and it reads as a failed
end. Step a few ticks and it clears. Measured.

## 🔴 Bridge time is TICKS, and a step is not the step you asked for

A bridge test advances the game a few ticks per call, so three things a wall-clock
instinct gets wrong:

- **A tick-keyed cache outlives many calls.** A mod that caches an answer for N ticks
  (GSS `CompHoseReel.Port()`, 60) still serves the stale answer to a census 4 ticks after
  the change. Step enough TICKS past the change before reading — not enough seconds.
- **A coarse stepper overshoots short states.** `rimworld/play_for` (what `scenelib.run` used
  until 2026-11-06) on the full list overshoots by ~100+ ticks per call, so a ~50-tick mental state
  (`RM_ParentalEnrage` after the intruder leaves) starts and ends between two polls and
  reads as a behaviour FAIL. Step exactly (`B.ticks(n)`, safe_advance), never with
  `play_for`. Prefer a durable trace that a single read after the window can see (a
  counter, a log line, a hediff). A stop-on-state is PLANNED (item
  ADVANCEUNTIL_WIRE_PER_TICK_STOP). Until it lands, a small-step poll belongs in a throwaway
  diagnostic, not in a committed proof
  (`skills/live-debugging-proof-harness/references/lightspeed-authoring.md` §3).
- **Stats do not predict wall pace on the full list.** `Out of Combat ReBoost` walks
  colonists ~2 ticks/cell while `MoveSpeed` still reads 4.6 c/s, so "step K ticks and catch
  the pawn mid-walk" misses. Read the walk's own state (job, path, position) rather than
  predicting it from stats.

Detect: a result that flips when you change the step size is a timing artefact, not a verdict.
- **Throughput is far below real time on a big list.** `rimworld/step_game_ticks` advances only ~50 ticks/s on the 325-mod full list (506 of 2000 in a 10 s call), so an 8-day plant survival run is ~2.6 h. Prove plant-light mechanics from the inspect string instead (a light-limited plant reads "needs light level N%").

## `rimworld/load_game_ready` is NOT a readiness poll

CHECK, 2026-08-20, and it cost two dead waits totalling ~10 minutes. The name reads as
"is the game ready after a load"; it is not. It takes a **`saveName`** and answers whether
**that save exists and can be loaded** — a PREcondition check, not a POSTcondition. Called
with no argument it invents a default name, fails to find it, and returns
`success: false, "Save 'rimbridge_save_<timestamp>' does not exist."` forever. A polling
loop written around it never exits, while the game sat fully loaded the whole time.

**To wait out a load, poll `rimworld/get_game_info` for `status == "game_loaded"`** and a
`ticksGame` that answers. That is the postcondition.

🔴 **It can also lie about a load that never happened.** Called right after a killed
`start_debug_game_ready`, it returned `success: true` + "game data is available and is
paused for automation" while `programState` was `Entry` and `hasCurrentGame` was `false` —
it loaded nothing. A plain `rimworld/load_game` from a settled Entry then worked in 4 s.
**Assert on `programState == "Playing"`, never on the load call's own `success`.**

🔴 **And `Playing` right after `rimworld/load_game` is the OLD map.** `load_game` answers
`queued`; on a big list the old game stays `programState == "Playing"` for 3-8 s before
`MapInitializing`. A wait-for-Playing issued straight after it returns at once
(`loadSeconds` 1-4) and every "after load" read comes off the old map or mid-load. **Wait
for the state to LEAVE `Playing` first, then for it to come back** (worked code:
`GimmeSomeSlack/validation.py` `_wait_playing`, 2026-10-10).
🔴 **`load_game_ready` is not a safe fallback for the `start_debug_game_ready` world-gen crash.** Loading a real save on the full 629-mod list hit the identical `SetupForQuickTestPlay`/`WorldPathGrid` `ArgumentOutOfRangeException`, confirmed on two saves.
**`save.missing_mods` is RimWorld's own native mod-compat gate** (the bridge surfaces it structurally); interactively it only warns "some mods are missing, load anyway?". The bridge exposes the same escape as `ignoreModCompatibility: true`, and the save then reaches `programState: Playing`. Use it only for read/verify loads; it never authorizes a RESAVE of a canonical save (owner-reserved).
**Reloading in-session right after dropping a generated map is not clean on the full list.** `settlement_remove mode=map force=true` then `load_game_ready` logged `Could not do PostLoadInit on RimWorld.FactionManager: KeyNotFoundException key 0` (Vehicle Framework's static per-map cache `SmashTools.DetachedMapComponentCache` keyed on the stale map index). A SECOND reload of the same save was clean. After dropping maps reload twice, or grep the log for `FactionManager PostLoadInit` after the first; a half-initialised FactionManager is not a clean game.

## A game can wedge on "Loading world." forever, and nothing on the bridge recovers it

2026-08-30, FOUNDRY. Bridge itself stayed healthy (~15 ms `rimbridge/ping`) while the game
sat on a "Loading world." long event that never completed: `get_game_info` answered
`game_loaded` with `mapCount 0` and `ticksGame` frozen, `go_to_main_menu` NREd, and
`Root_Play` threw every frame. `start_debug_game_ready` and `load_game` both did nothing.
`take_screenshot` still worked and is what identified it — every data-side readiness call
lied or crashed.

⇒ **Not recoverable from the bridge.** The owner has to restart. Treat a frozen `ticksGame`
plus a healthy ping as the signature, and screenshot before concluding anything else.

## `rimworld/save_game` DOES honour a filename — under `saveName`

Same session, and it corrects a line that stood in the skill for months. `{"saveName":
"rt_probe"}` wrote `rt_probe.rws`. The old note said the tool "ignores your `fileName`":
it does, because `fileName` is not a parameter it has, and **an unknown parameter name is
dropped before the tool runs** — the documented failure mode, mistaken for a tool quirk.
Generalises: before recording "tool X ignores argument Y", check Y is spelled the way the
schema spells it.

## `[JawaBench] ready` is LAZY — a missing line is not a failed deploy

The module initializer WAS lazy (it waited for the first `jawa/*` **tool call**); since 2026-10-10 `RimBridgeServer` constructs `JawaBenchTpsTools` at companion registration (game load), so `JawaBenchInit.Announce` fires before the GABP server even listens. Still never treat a missing `[JawaBench] ready` line as a failed deploy (census the live tool list), and anything that must hold with no bridge call should install explicitly from that ctor. The companion DLL lives in `GAME_DIR/BridgeTools`, not a mod Assemblies folder, so a `[StaticConstructorOnStartup]` class there never runs. Older note:
`tools/list` does not trigger it. Measured 2026-08-26: `harvest_log.py` scored
`RED  JawaBench ready  0  MISSING` at the main menu with a perfectly good 166-tool DLL, and the line
appeared the instant `jawa/get_def` was called. ⇒ **Census the live tool list; never use that line as
the deploy signature.**

## `rimworld/start_debug_game_ready` returns before the map is DRIVABLE

```
start_debug_game_ready -> success true, "RimWorld map data is available"
                          state: programState MapInitializing, currentMapId NULL
get_game_info          -> mapCount 1                       <- and yet
jawa/spawn_pawn        -> "No current map. Load a game first."
```

⚠️ **`mapCount: 1` answers "does a map exist", NOT "can I drive it".** `Find.CurrentMap` was still
null. Poll `rimworld/get_cell_info` → `state.currentMapId` until it is non-null (a few seconds); that
is the only reading that means the map will accept a write.

## 🔴 `rimworld/start_debug_game_ready` called with a `forcePause` modal on the stack killed the process

2026-08-31, FOUNDRY. A `Verse.Dialog_NodeTree` (the same forcePause-modal family as above)
sat on the window stack when `start_debug_game_ready` was called — the result was
`ConnectionResetError`, the RimWorld process gone, clean log, one occurrence, not isolated
further. **Clear dialogs with `jawa/window_list_close` before starting a map**, never after.

## 🔴 Closing the ESCAPE MENU resumes the game at its previous speed
The paused state you read while `RimWorld.MainTabWindow_Menu` (the Esc menu) is open
is the MENU's pause, not a real speed-0. `rimworld/close_window {"windowType":
"MainTabWindow_Menu"}` closed it and the sim resumed at the owner's underlying speed
instantly — ~1,300 ticks ran before it was caught (2026-09-03, gravship_scratch_b,
18 freshly spawned wild predators on the map; no losses, by luck). `jawa/clear_ui`
does NOT close this window (`closedCount: 0`, listed in `remaining`) — same family
as the Dialog_NodeTree entry above. Also: `set_time_speed 0` during a forced-speed
stretch can report "Paused" while ticks still advance — verify with two
`jawa/time_clock` reads and RETRY; the second call stuck.
**Fix:** `set_time_speed 0` and VERIFY the freeze BEFORE `close_window` on the menu.
**Generalises to:** any pause you observed while a modal was open is unproven the
moment that modal closes.

## 🔴 `jawa/world_tile_map_generate`'s SECOND call at a DIFFERENT tile, same session, silently reuses the FIRST map

Measured 2026-09-04. Call 1 (`tile: 701`) genuinely generated a new map:
`wasAlreadyGenerated: false`, `mapIndex: 1`, `pawnCount: 71`. Call 2, same connection,
different tile (`tile: 703`, a different empty land tile — confirmed via
`jawa/world_tile_get` before either call): returned `success: true,
wasAlreadyGenerated: false, mapIndex: 1, pawnCount: 49` — DIFFERENT numbers from call 1,
so it is not a bare stale-cache echo. But `rimworld/get_game_info` afterward reported
`mapCount: 2` (not 3, so no second Map object exists), and `jawa/map_info` (reads the
live `Find.CurrentMap`) reported `tile: 701` for that same `mapId: 1` — the ONLY map
besides the player's colony is still tile 701's. **Tile 703 was never actually
generated**; the tool fabricated a plausible-looking but wrong response. A THIRD call
for the same tile 703 then reported `wasAlreadyGenerated: true` with the SAME numbers,
compounding the lie into an apparently-stable, apparently-idempotent false state.

⇒ **Do not trust `wasAlreadyGenerated`/`mapIndex`/`pawnCount` from a second
`world_tile_map_generate` call in one session if the tile differs from the first
call.** Verify independently: `rimworld/get_game_info`'s `mapCount` before and after
(it must increase), and `jawa/map_info` (or a fresh `jawa/world_objects_get` /
`list_pawns` scoped to the new map) actually reflecting the requested tile — not the
generator tool's own say-so.

**Generalises to:** a companion tool that internally caches "the map I just made" and
reuses it in place of doing the requested work again is invisible from its own return
value, because that value is shaped exactly like a real success and even varies
plausibly between calls. Cross-check against an INDEPENDENT reader (`get_game_info`,
`map_info`) that did not go through the same code path.

## `jawa/world_tile_map_generate` on an unfamiliar tile spawns that tile's own faction
`world_tile_map_generate`'s default `suggestedMapParent: "Settlement"` generates the tile's OWN resident faction settlement, not a neutral scratch site: forcing a river tile's biome, planting a colonist and unpausing brought a real raid from the tile's owner faction within seconds (`rimworld/list_letters` showed it targeting the scratch map's own mapId). Check `jawa/world_tile_get` feature/faction fields before generating on an unfamiliar tile.

## Standing up a bridge test site that survives save and a long chain
A generated bridge map needs a player settlement (`jawa/colony_found`) or it is culled on save; load saves from the main menu, once. Closing the naming dialog hops the current map. A paused site no-ops `ordered_job waitTicks`. `step_game_ticks` needs `timeoutMs`. In zsh a multi-path variable needs `${=P}` to split.

## GameComponentTick-driven async delivery never drains while PAUSED
`GameComponentTick`, and any `ConcurrentQueue`-based async delivery built on it (the Oracle's), never drains while the game is PAUSED, which `start_debug_game_ready` leaves it by default. `step_game_ticks` a handful of ticks (still paused) to force delivery before reading a result.

## A swapped Greater Landforms recipe needs a full process restart
A GL custom landform swapped into `Config\CustomLandforms-v1\` while the game runs is NOT picked up by `go_to_main_menu` + `start_debug_game_ready` (confirmed live twice); a full process kill plus Steam relaunch is required. A same-recipe tile re-roll via `go_to_main_menu` needs no restart.

## A failed `jawa/set_current_map` does not stop later calls
A failed `jawa/set_current_map` does not stop later calls: they land on whatever map is current. Two failed `set_current_map(12)` calls (the map had auto-culled) sent `jump_camera`/`set_time_speed` to the owner's real campaign map and unpaused ~10 game-minutes. Re-check `jawa/map_info` mapId immediately before any `set_time_speed(>0)`; never trust an earlier `set_current_map` return. Separately the World-tab UI can stay on screen while `jump_camera_to_cell` reports the right mapId (`TryHideWorld` does not stick); only a screenshot shows what the owner sees.

## A "Playing" wait does not prove a map was regenerated or reloaded
After `Actions\Regenerate Current Map` `programState` stays `Playing`, so a wait-for-Playing loop passes at once and censuses the OLD map; "map regenerated" is proven by `jawa/map_info` `mapId` changing, not by `mapBiome` (`Map.Biome` reads the tile live, so it shows the new biome straight after `world_tile_set`) nor `programState`. And `jawa/list_things` returns at most `limit` rows (default 200): count from `perDef`/`countMatched`, which cover every match.

## `status: game_loaded` is not proof the game loaded (zombie session)
- **`status: "game_loaded"` is not proof the game loaded.** A save can abort in `ScribeLoader.FinalizeLoading` (e.g. a mod's Harmony postfix on `CrossRefHandler.ResolveAllCrossReferences` throwing `Collection was modified`); the engine shows "An error occurred while loading a map", bails to the main menu, and the process then runs for hours reporting `game_loaded`, answering every bridge call and returning plausible numbers from the world object still in memory. The canary is `ErrorWhileLoadingGame` in `Player.log`, written only when the engine has given up on a load; it is written AFTER `status` flips, so settle (a check at t+0 passed, at t+60 failed) before reading it. Not canaries: the debug `Actions` tree (few or no visible children whenever no map is loaded, and it enumerated fine on an aborted game) . What still counts from a zombie session is results about the TOOLS (a tile import reporting 21,872/21,872 and validating 100% really did that); nothing about game state, save or behaviour counts. And take the screenshot: the error dialog was on screen the whole time and no number revealed it.

## 0b. 🔴 Claim the bridge before you drive it — `rimflow bridge take`/`release`
- **Never `--force-take` the bridge from a stale-looking lock.** First check `D:\ClaudeWork\rimmandrake\scratch\bridge_calls.jsonl` for a live foreign client: a force-take once loaded another seat's walk save over a running test site.
- **Never hand game or bridge powers to a subagent** without checking `rimflow bridge who` and the driver lock first. After any launch, compare `jawa/running_mods` to `ModsConfig.xml` (a 26-mod game ran while the file said 544). Windows case-twin texture files (`PaleTree_B` / `PaleTree_b`) block the art compose: retire the stray twin via `artledger.retire`.

## 1. Connect
- **A second RimWorld on one machine gets its own bridge only if BOTH `GABP_SERVER_PORT` and `GABP_TOKEN` are set before launch.** RimBridgeServer has no port fallback: without them it logs `[RimBridge] Failed to start server` and the game runs with no bridge. In env mode the `Bridge token:` line is not written, so log-waiters must accept the port line. On a machine where the bridge mod is a Workshop item (not a local Mods folder), a failed `SteamAPI.Init` makes the game carry on without Workshop mods, so it has no bridge and looks fine on screen; whether a second concurrent game gets Init must be measured.
