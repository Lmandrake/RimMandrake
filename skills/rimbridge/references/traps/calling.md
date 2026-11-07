# RimBridge traps: calling the bridge: parameter names, return shapes, the client, python.exe from WSL

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

## 🔴 `python.exe` vs `python3` is a PER-SCRIPT choice, and the rule you carry points the wrong way half the time
**Symptom:** `preload_check.py` printed **NOT SAFE TO LOAD** for one seat and **SAFE TO LOAD** for two others, same commit, same minute, same files. It failed three Cherry Picker keys as unresolvable. A hand grep then "confirmed" it, and the pair went to the owner as a launch blocker. Both were wrong; the defs existed all along.
**Cause, and it is worse than a hardcoded path:** `preload_check.py:138` guards its platform-aware branch with `hasattr(GP, "STEAM_WORKSHOP")` — but `game_paths` exposes the attribute as **`WORKSHOP`** (`game_paths.py:64`, and it already resolves correctly under both interpreters). The guard is therefore **always False for every seat**, the resolved-path branch is dead code that has never once executed, and every run falls through to two hardcoded `/mnt/c/...` literals at `:139-140`. **A fallback that never falls back is indistinguishable from one that works, for as long as the fallback happens to be right.** **Windows Python cannot resolve a `/mnt/c` path**, so the Workshop root did not exist, every Workshop mod read as absent, and the gate reported a stack problem instead of its own blindness. The seat had run `python.exe` because of the standing rule *"use `python.exe`, never `python3` — WSL cannot reach the bridge."* **That rule is correct and it is about the NETWORK.** Applied to a script whose work is the FILESYSTEM, it silently inverts.
**Fix:** choose the interpreter from what the script TOUCHES, not from habit. **Talks to the bridge → `python.exe`** (WSL2 is NAT-mode and cannot reach Windows loopback). **Reads `/mnt/c` paths → `python3`.** Does both → it must resolve roots per-platform, and there is no interpreter that saves it. When a run disagrees with a peer's run of the same file, suspect the interpreter before the data.
**Recurs when:** any script that hardcodes one path style, and any rule that names a tool rather than a reason. ⚠️ **The deeper defect is that a MISSING root was indistinguishable from an EMPTY one** — `if not os.path.isdir(root): continue` swallows an absent root without a word, so the check failed OPEN and reported confidently. A configured root that is absent must make the tool REFUSE TO RUN, never report a result. Same mechanism produced the same seat's *"I grepped the whole tree"* an hour earlier: `common/RimWorld/Mods` + `Data` is **two of three roots**, and the missing third — `workshop/content/294100` — holds most of the stack. **Two wrong things pointing the same way read as corroboration.**

## Client-call gotchas that cost real minutes — the exact spellings
Collected 2026-08-13; each one cost a seat time before it was written down.

- **There is no `rimbridge/list_tools`.** Use the protocol-level `tools/list`, or `rimbridge_client.py --list-tools`.
- **`RimBridge()` takes `timeout=`, not `read_timeout=`.**
- 🔴 **`RimBridge()` does NOT open the socket and does NOT find the token.** The constructor takes an explicit host/port/token; the token is regenerated every game start. Use `resolve_endpoint(None, None, None, None)` to scrape it from `Player.log`, then `rb.connect()`. Symptom of getting this wrong: `AttributeError: 'NoneType' object has no attribute 'sendall'`, then `session/hello failed: Invalid authentication token`.
- **WSL cannot reach the bridge at all** — RimBridge binds Windows loopback and WSL2 is NAT-mode. Run `python.exe`, never `python3`. This is not a timeout, it is no route.
- **`rimworld/set_camera_zoom` takes `{"rootSize": <number>}`** — a number, not a zoom name. `{"zoom": "Furthest"}` is an unknown key: dropped silently, `success: true`, camera does not move.
- **`rimworld/execute_gizmo` takes `{"gizmoId": "<id>"}`, not an index**, and the id changes every time the selection changes. Re-list; never cache one.
- 🔴 **Loose gizmo LABEL matching executes the WRONG gizmo with `success: true`** — matching on `'fill'` hit "Allow manual refill" and filled nothing. Match the exact prefix (e.g. `"DEBUG: Fill"`), never a bare substring (2026-08-29, BENCH).
- **`rimworld/update_mod_settings` wants `values` as a DICT** — `{"gravEngineSupport": 4500}`. A list of pairs returns *"At least one settings path/value pair is required."*
- **`jawa/damage` takes `thingId`**, not `targetId`/`pawnId`/`id`. **`jawa/destroy_batch` takes `categories`**, plural.
- ⭐ **The pattern behind half of these: an unknown parameter name is DROPPED SILENTLY before the tool runs**, so a wrong name is indistinguishable from an omitted one and the call reports success. When a call succeeds and nothing happens, suspect the parameter NAME before suspecting the game.
- 🔴 **`jawa/order_pawn` UNPAUSES the game by default.** Pass `unpause: false`. Measured 2026-08-15: the owner had deliberately left time stopped, one `order_pawn` ran the clock from tick 1035 to 19634 (~5 in-game hours) across a few calls, and nothing in the reply says time moved. Verify with two `ticksGame` reads seconds apart, not with the call's own `success`.
- **`jawa/order_pawn` `timeoutSeconds` is the SERVER's ceiling, not the client's.** Setting it above the client's 30 s socket timeout kills the connection mid-call — `timed out after 30.0s waiting for the bridge`. Keep `waitTicks` small enough to answer inside 30 s and loop, rather than asking for one long wait.
- **An UNDRAFTED pawn does not hold a move order** — it walks off to its own AI job, so a reachability measurement reads as failure. Draft for the measurement (`draft: true`), undraft only when you want the pawn to take a work job at the destination.
- 🔴 **A FactionDef's defName is not its filename.** `JawaAscendantHelix.xml` contains `<defName>Jawa_AscendantHelix</defName>`. Querying the filename returns `found=false`, which reads exactly like the def being absent — and on 2026-08-15 that manufactured a false "five factions are still broken" finding that was reported to another seat. Read the defName out of `<defName>`. A control def in the same call does NOT catch this unless the control is misspelt the same way.
- 🔴 **`Actions\T: Destroy` with `thingId` can kill something you did not name.** Measured 2026-08-15: 77 pawns targeted by explicit `Thing_<id>`, **78 died** — the one survivor I had deliberately excluded by name was destroyed too, and 3 of the 77 calls reported `success: false`. Cause not established; suspect an unresolvable `thingId` falling back to the current selection or the cursor cell. **Never fire a long batch of destroy calls and check the total only at the end** — re-read the survivor set every ~10 and abort on the first unexpected loss. Losing one wrong pawn is invisible in an aggregate count.
- **`rimworld/get_cell_info` has no `mapIndex` param** (current map only). **`rimworld/select_pawn` needs `Thing_<id>`** even though `jawa/spawn_pawn` returns a bare id; the bare id fails with "Could not find player-controlled colonist id". The client's declared-parameter check refuses an unknown param name loudly, so trust it over guessing.
- **`jawa/get_terrain_batch` refuses more than 70,000 cells per call in total** (MaxCells, `JawaBenchTerrainTools.cs`): it sums ALL rects, so semicolon-joining rects does not help — split into SEPARATE calls. A whole-map rect `0,0,sizeX,sizeZ` therefore works only up to ~264x264; read bigger maps in z-bands of `70000//sizeX` rows. It also silently skips out-of-bounds cells (`cellsOutOfBounds` counts them, nothing fails): assert `cellsRead` covers `sx*sz`, or a census over a hardcoded rect reads a partial/empty map as "no change".
- **Tools whose list params want a comma-separated STRING.** `jawa/world_tile_get` `tiles` and `jawa/inspect_string` `thingIds` take "1,2,3"; a Python list raises `Object must implement IConvertible` with a stack trace that never names the parameter.
- **`jawa/world_neighbors` `path` is an OUTPUT FILE path, not a tile id.** It wrote an 840 KB neighbour dump into the game install root while reading as a query. Read the tool's param meaning before passing a `path`.
- **`jawa/ordered_job` with `waitTicks>0` on a PAUSED clock burns the whole tool timeout (~17 s per order):** 72 queued Mine orders ate 20 minutes of a 25-minute budget. Queue with `waitTicks=0` and read the effect after a real wait.
- **An unnamed colony re-raises `Dialog_NamePlayerFactionAndSettlement` every ~600 ticks**, force-pausing the clock mid-chain even when a `modal_open` detector ignores it. `jawa/name_colony` names faction+settlement (idempotent, same as the dialog's OK). A `jawa/fire_incident` `dryRun` that cannot fire returns `success=false` WITH `canFireNow=false`: read `canFireNow`, never `success`.
- **`CompTargetable` items need `selectedTarget` set via `OrderForceTarget`:** a plain `UseItem` is accepted and does nothing (an antidote test read UNMEASURED for this reason). Also `jawa/fire_incident` defaults `dryRun=true`: pass `dryRun=false` to actually fire.
- **The rimbridge CLI client has its own default wait (~30 s)**, separate from a tool's `timeoutSeconds`/`timeoutMs`. A tool that legitimately needs 30-90 s (quicktest boot, an `ordered_job` wait) needs `--timeout <N>` on the CLI call too, or it times out client-side first.
- **A scenario FILE name is not its defName.** `Scenario_Utinni.xml` holds defName `RUT_Jawa_UtinniStart`; `jawa/scenario_select {scenario:'Scenario_Utinni'}` can never match. Read the defName out of the def before writing it into a tool call or runbook.
- **`jawa/flowworks_excavation_report` has NO terrain key** (depth, fill, isExcavated, source/sink only): read a cell's terrain from `rimworld/get_cell_info` `cell.terrainDefName`; `r.get("terrain")` is always None.
- **`jawa/static_call` args.** Multi-arg is `a|b|c` (a comma fails); it cannot pass byte args; `args=''` reads as ZERO params, so a one-string-arg method is not found: pass a single space `' '` for one empty arg. And a pawn holding the same job 10,000+ ticks is not necessarily stuck: read the work toil's duration first (`RM_RaiderFillTrench`'s Delay toil is sized by the deep-dig cost curve x MiningSpeed, so one notch at D8 took ~22,400 ticks for a gunner at MiningSpeed 0.336).
- **`jawa/order_pawn`'s `success` means the pawn ARRIVED on the cell**; with `waitTicks=1` it is false for every pawn. Read the per-pawn `orderAccepted` (`live_session.order_taken`). Never walk bystanders across a map (on a river map they swim and the current bruises them): teleport instead (`HoseProbe pawn:<id>=tp:x,z`).
- **`rimworld/get_ui_layout` has no `disabled` key** on widgets, so a greyed-out switch cannot be read from the layout: prove greying by a capture plus "click changes nothing" (snapshot the settings fields before and after). The HoseProbe `pawn:<id>=tp` and `colonists` commands take the numeric `thingIDNumber` (107458), not `list_pawns`' `Human107458`, which answers "no such pawn on this map".
- **`jawa/list_things` rows carry `x` and `z`, not `position`.** A proof comparing `r.get("position")` before vs after got None==None, so "moved" was always False. Match rows by id and compare `(x, z)`.
- **`rimworld/get_game_info` carries NO key naming the loaded save** (keys: status, ticksGame, mapCount, selectedPawns, operation, state). Identify the map from `jawa/world_info_get` (`info.name` + `info.seedString`) and compare with the save's `<world><info>`. `hasCurrentGame` lives on `get_ui_state`, NOT `get_game_info`: reading it from the wrong reply gives None, and a check written `is not False` passes with no game. Assert the field is True.
- **`jawa/destroy_batch` takes rects as `x,z,w,h`**, while other jawa tools take corners: passing corners `36,36,58,52` with `categories=All` wiped a 58x52 area. Read the tool's rect format before every call. A `spawn_batch` lattice on `WaterDeep` spawns fine but GSS marks every cell buried (census `cordEdges 0`): sample the terrain before staging a GSS site.
- 🔴 **`python.exe` bridge scripts die at import with `RmDataRootUnset` unless the storage root reaches them.** WSL's `RM_DATA_ROOT`/`AGENT_STORAGE_ROOT` do not cross into Windows: pass it inline, `AGENT_STORAGE_ROOT="$(python3 ~/dev/Lodestar/bin/lib/agent_storage.py --native)" WSLENV=AGENT_STORAGE_ROOT python.exe ...` (or `export RM_DATA_ROOT='D:\ClaudeWork\rimmandrake' WSLENV=RM_DATA_ROOT:$WSLENV`); any other env a script reads needs its own `WSLENV` entry. Also: bridge reply envelopes carry `/operation/DurationMs`, so a serial-vs-X equality probe must ignore timing metadata or it false-FAILs.

## ⚠️ `jawa/inspect_string` takes `thingIds`, and a JSON LIST throws
Singular `thingId` is dropped and the tool answers *"Give thingIds, defName, or
rect"*. Passing `thingIds` as a JSON array throws
`System.InvalidCastException: Object must implement IConvertible`. Pass a
**comma-separated string**.

## 🔑 Two things that worked first time, worth reaching for
* `rimworld/screenshot_cell_rect {x, z, width, height, paddingCells}` frames and crops
  to a cell rect — better than aiming the camera by hand. It writes
  `<name>__cell_rect.png`, not `<name>.png`.
* `rimworld/start_debug_game_ready {"readiness": "playable", "pauseIfNeeded": true}`
  took a quicktest colony from the main menu to paused-and-drivable in **118 s**, and
  returns the whole readiness ladder so there is nothing to poll yourself.

## ⚠️ From WSL, `python.exe` dies on non-ASCII output
`UnicodeEncodeError: 'charmap' codec` on a tool message containing an em-dash — the
call had already SUCCEEDED, so this destroys the report, not the work. Open every
bridge script with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.


## `.get("children") or []` turns a FAILED call into "zero results"

CHECK, 2026-08-20. `list_debug_action_children("Actions")` was returning
`success: false` with a NullReferenceException, and my reader did
`len(r.get("children") or [])` — printing "Actions children: 0". I read that as an empty
tree and went looking for why dev mode was off. Dev mode was on; the call was failing.

**Assert on `success` before reading the payload.** `or []` is the same defect as ignoring
an exit code: it converts "I could not answer" into "the answer is nothing", and those need
completely different responses. Generalises to every `.get(x) or default` over a bridge
reply.
The same defect appears when a check substring-matches the raw payload: a FAILED call reads as ABSENT. Read `success`/`foundCount`/`notFound` and keep "could not ask" as UNMEASURED, never as a pass or an absence.

## Three parameter names that produced fake catastrophes in one session — 2026-08-21, CHECK

All three calls returned `success: true` and answered a **different question than was asked**.
An unknown parameter name is dropped before the tool runs, so a wrong name is
indistinguishable from an omitted one. Generalises to: **every one of these looked like a
devastating content finding, and every one was the caller.**

| I passed | the tool wants | what it looked like |
|---|---|---|
| `jawa/pawn_get` `pawnId=` | **`pawn=`** | the param was dropped, the tool returned its brief LISTING with no `equipment` field, and every pawn read as unarmed — **a clean 0 of 270 armed** |
| `jawa/spawn_pawn` `faction="hostile"` | the kind's **own faction defName** | all 67 of our kinds carry `useFactionXenotypes: true`, so xenotype comes from the faction the pawn JOINS — reading **"49 of 55 kinds spawn Baseliners"**, i.e. the species identity of twelve factions apparently gone. Re-spawned into their own factions: Geonosians 4/4, Jawa 5/5, a five-species mercenary company. Exactly one faction was genuinely wrong |
| `rimworld/load_game` — | *(name was right)* | it returned `success: false, code: "save.missing_mods"` naming the mod, and I diagnosed "the load will not dispatch" from `Player.log` not growing for an hour **without reading the response** |

🔑 **The rule these three share is not "check parameter names".** It is: when a result is
dramatic, the caller is the first suspect, not the content. Re-run the same question a second
way before writing it down. Two of the three were caught that way; the third was caught by
finally reading a return value that had been sitting there the whole time.

⚠️ `jawa/pawn_gear` is a **WRITER**. Reading equipment off it answers with *"Give a
ThingDef."* and reports every pawn bare — a fourth route to the same false catastrophe.

## 🔴 The bridge SILENTLY DROPS any parameter a tool's schema does not declare

Proven 2026-08-26 on purpose, after two calls in one session were mis-named and nothing complained.

```
jawa/new_allowed_area {label: "CHECK_correct"}           -> success, label "CHECK_correct"
jawa/new_allowed_area {name: "CHECK_wrong", banana: 42}  -> success, label "Area 3"
jawa/time_clock       {zzz: "nonsense"}                  -> success, full correct payload
```

`success: true` every time. ⇒ **A typo in a parameter name is invisible.** It is caught only when the
tool then misses a *required* field and refuses; where a default exists you get a successful call
that did something else — `new_allowed_area` wants `label` not `name`, `stop_job` wants `mode` not
`action`, and both quietly used their defaults.

⚠️ **Four grammars on tools that look alike, all in one session:**
`rect` (`room_get`) · `rects` (`destroy_batch`) · `ops` (`set_terrain_batch`, `set_roof_batch`,
`paint_area`, `build_batch`) · and `faction: "player"` accepted by `spawn_pawn`, refused by
`build_batch` which wants `PlayerColony`.

🔑 **Read the schema, not the sibling tool.** `b.list_tools()` carries the accepted keys; diff your
arguments against them before a batch. This is a property of the BRIDGE, not of any one tool.


## An UNKNOWN call blocks the bridge client until reconciled
When a timeout kills a `python.exe` bridge script mid-call, the client records that mutating call as UNKNOWN and refuses EVERY later call, read-only ones included, until `rimbridge_client.py --reconcile --resolve CID --as applied|not-applied`. On a game whose frame takes ~75 s (a choking map current) budget watchdogs do not fire because one call blocks: set the outer timeout and expect to reconcile. Two `python.exe` bridge processes in parallel (a sampler loop plus a `set_time_speed`) share `scratch\bridge_calls.jsonl`: the other process's in-flight mutating call reads as UNKNOWN and raises `IndeterminateError` on the next call, killing the sampler mid-window; catch it, sleep 0.5 s, continue (`--reconcile` a moment later shows 0 pending). WSL env vars reach `python.exe` only via `WSLENV`.
