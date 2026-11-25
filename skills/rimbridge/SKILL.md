---
name: rimbridge
description: Drive a live RimWorld from outside via the RimBridgeServer GABP bridge and its JawaBench companion - author the planet, author the map, deep-edit pawns, and drive weather, game conditions and raids. Use when automating in-game testing, building map or world content, debugging mods without clicking, and above all whenever a bridge call reports success and the game did not move.
---

# Driving RimWorld from the outside

Every claim here was **verified against a running game**. Nothing is repeated
from documentation without a live test. The mark ❓ is for a guess. The mark ⚠️ is for a provisional finding.

**`references/traps.md` is the index of the trap catalogue.** The index lists the title of every entry.
Each title stands under the topic file that holds the entry. The seven topic files are in `references/traps/`.

- Do not read the topic files whole. **Grep them for your verb**
  (`grep -i -n "roof\|spawn\|screenshot" references/traps/*.md`).
- Read the hits. Read also every entry marked 🔴. Each of those entries has destroyed something real.

🔴 **Before your first WRITE of any session, read `references/silent-failures.md` instead.**
That file is the catalogue of engine calls that report success and change nothing. Its knowledge is the single most
expensive knowledge in this project.

⚠️ **Read §4b first if you are about to unpause or spawn a hostile. Read §4 if you are about to enumerate debug
actions.** Those two acts have destroyed a colony and a 568-mod game respectively.

---

## 0. Where to go — read this row, then that file

| you are about to | read |
|---|---|
| 🔴 **write ANYTHING to the game** | **`references/silent-failures.md`** — 30+ engine calls that report success and change nothing. The most expensive knowledge in the project |
| author the **planet** — tiles, biomes, rivers, roads, mutators, landmarks, settlements, regions | `references/world-authoring.md` |
| author a **map** — terrain, substructure, buildings, prefab copy/paste, fog, snow, zones | `references/map-authoring.md` |
| edit **pawns**, or make pawns that live somewhere | `references/pawn-authoring.md` |
| **add a tool the bridge does not have** | §9 (no permission needed for a generic tool; tests stay in Python), then the `rimbridge-companion` skill |
| something "worked" and did not | grep `references/traps/` for your verb |
| meet a pawn/creature you did not put there, or start any debugging theory | `references/first_look.md` — the 7-step first look (`modcheck/scene_report.py`), and what you may NOT claim about origin |
| **stage a raid** (`jawa/fire_raid`, `jawa/raid_shape_fire`, a raid incident through `jawa/fire_incident` or `jawa/storyteller_fire`) | The client refuses a call that stages a raid while raid tests are paused (raid_pause.py show). The calls, their traps and the faction rewrite: `references/traps/pawns-factions.md`, `references/silent-failures.md` §`jawa/fire_raid` |
| optimise, or quote a timing | `references/performance.md` |
| **launch** the game (cold load), or attach after one | `references/preflight.md` — `preflight_bridge.py --tier full [--deep]` before, `--live` after; GREEN or do not spend the load |

**The house rule everything collapses to:**
> **Write → read back the RAW field → look at the screen.**
> ⛔ A tool that returns `success: true` is not evidence. It never was.

---

## 0b. 🔴 Claim the game before you drive it — `game_lock.py claim`/`release`

Whoever drives a game claims the lock of that game first, and releases the lock the instant it stops. A driver is, for
example:

- a testq lane (proofs that run with no LLM);
- a Test Pilot;
- an owner live look;
- an Opus evaluation (L3 is level 3 of the validation ladder, `infrastructure/VALIDATION_LADDER.md`).

A refused claim is your answer. Exit 75 is held, 3 is his hold, 2 is could not look.

```
python3 src/RimMandrake/rimflow/game_lock.py claim ArchBig --for "<what for>"   (or rimflow bridge take)
...drive it...
python3 src/RimMandrake/rimflow/game_lock.py release ArchBig
```

🔴 **There are several games, and each has its own bridge, lock and holder.**

- **ArchBig** is Steam's install on Archmagi. ArchBig holds the full list, and he looks at staged work there. Its bridge port is 5174. Its
  lock is `archmagi`, the default.
- **ArchSmall** is its own install on Archmagi (`D:\ClaudeWork\rimmandrake\instances\b\game`). Its bridge port is 5175.
  Its lock is `archmagi.b`.
- **Steve1** and **Steve2** are the SteveDesktop games. Those two games take work through `infrastructure/stevedesktop/RUNBOOK.md`.
- To drive ArchSmall, first run `eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"`. The bridge
  client, `game_paths` and the driver lock all follow that command. Name ArchSmall in the claim too
  (`game_lock.py claim ArchSmall`, or `--host ArchSmall` for `rimflow bridge`).
- `python3 src/RimMandrake/Utils/game_instance.py status` lists the games and their drivers. `launch ArchSmall --wait`
  starts ArchSmall.
- If ArchBig is busy or held, drive ArchSmall. Only a check that needs his full list waits for ArchBig.
- Never write "waiting for the live game". Name the game. Say why no other game can take the work.

Four rules for a driver:

- 🔴 **A holder is a PROCESS.** A live holder holds the game, with or without events. The game is free at once when that
  process ends. The 45-minute rule covers only his OWNER hold (root `CLAUDE.md` §The bridge is passed through one file).
  Before you restart a game whose hold looks stale, cross-check `rimworld/get_game_info` and `Player.log`'s mtime.
- ⚠️ **`Player.log`'s mtime can read hours stale against a just-recorded `bridge take`.** Before you trust the content
  of the log as this session, `stat` the log and check `tasklist.exe`.
- 🔴 **If a subagent must start or wait on a cold load, tell it up front to block in a foreground loop.**
  Tell the subagent never to end its turn "to wait for the monitor's notification". No background notification reaches a subagent.
- **Two drivers at once on one game leave its bridge STUCK, not crashed.** The bridge comes back when the other call
  finishes. Find out who else is on that game. Do not restart that game. Do not wait: take another free game for your
  work.

Detail and the incidents behind each: [references/connect-and-claim.md](references/connect-and-claim.md).

More traps for this section: [references/traps/lifecycle.md](references/traps/lifecycle.md) § 0b. 🔴 Claim the bridge before you drive it — `rimflow bridge take`/`release`.

## 1. Connect

```bash
python.exe src/RimMandrake/Utils/rimbridge_client.py --call rimbridge/get_bridge_status --yes-i-know-this-is-live
```

- The client scrapes host, port and token from `Player.log`. ArchBig's port is **5174**, stable. The token **changes
  every launch**.
- The protocol is GABP (`gabp/1`). Send `session/hello` first.
- Tool names use **slashes** (`rimworld/get_game_info`).
- The tool count moves. Recount with `python.exe src/RimMandrake/Utils/rimbridge_client.py --list-tools`. The names are
  in `references/tool_census.txt`.

**Drive the client as a library, never through `--json` on the command line.** Debug-action paths carry backslashes. In
heredocs prefer `chr(92)`.

```python
import sys; sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")   # WSL: /mnt/d/Luke/dev/RimMandrake/src/RimMandrake/Utils  (read-only mirror)
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/list_colonists", {"currentMapOnly": True})
```

### Before the first call

- 🔴 **From WSL run `python.exe`, never `python3`, for anything that talks to the bridge.** The bridge binds Windows
  loopback. A script that reads `/mnt/c` paths needs `python3`. The choice is per script, not per project.
- 🔴 **Turn on Options → Run in background before any unattended run.** Do it in the game's menu. The game discards a
  `Prefs.xml` edit that you make while it runs. An all-null `get_bridge_status` means that this option is off and the game is
  unfocused. An all-null status does not mean "no map is loaded".
- ⏳ **The bridge answering is NOT the game being reactive.** The game becomes drivable about forty seconds after the
  bridge first answers. Hold mutations until then (`load_session.py --settle`).
- ⚠️ **A timeout is fatal to the CONNECTION, not to the call.** Open a fresh `RimBridge` and poll the post-condition.
  Never retry on the same connection. Never re-issue a call whose idempotence you have not established.
- 🔴 **`python.exe` cannot open a script under `/tmp/...` or the session scratchpad.** Write bridge scripts into
  `Transient/`.
- ⚠️ **`python.exe` can spawn a WINDOWS `python3` with exit code 0.** So `python.exe` drives the bridge only. WSL
  `python3` owns everything Unix-only.
- **Never type a namespace prefix you did not just read.** Read the leaf from `references/capability-matrix.md`.

### Census the companion before you trust any `jawa/` call

**First call of any session: count the `jawa/` names the bridge reports.** Count them each time; never quote a count.
Companions register only at RimBridgeServer startup. So a low count means that the deploy did not take. **0 means the
bundle did not load.**

- 🔴 **The deploy must use `--gm`.** Without it, the game copy loses every player-acting tool. `build.py` refuses such a
  deploy and names the tools.
- 🔴 **`brrainz.rimbridgeserver` must be ACTIVE in ModsConfig.** The bridge mod discovers the companion in
  `<gamedir>\BridgeTools\` at startup.
- ⛔ **Never count tools with `strings | grep` on the DLL.** Names and messages live in different heaps. When the game is
  down, use `build.tool_surface()`. When the game is up, use
  `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --census`.

Which source file holds which tools, the census commands and the incidents: [references/connect-and-claim.md](references/connect-and-claim.md).

More traps for this section: [references/traps/companion.md](references/traps/companion.md) § Census the companion before you trust any `jawa/` call.

More traps for this section: [references/traps/lifecycle.md](references/traps/lifecycle.md) § 1. Connect.

## 2. The one law

> **`success: true` means the tool RAN, not that the game CHANGED.**

`spawn_thing` returns a real `thingId` while it logs an error. Every `Set terrain (rect)` call returns success and
changes nothing. **Verify every mutation against an independent channel**, cheapest first:

1. **`effects` on the response.** `effects.logs` / `logCount` is per-call log capture. Read it on every mutation. But
   `effects.debugToolChanged` is **NOT** a success signal (see traps).
2. **`get_cell_info`** shows what is actually in a cell, including `stuffDefName`.
3. **`save_game`, then parse the `.rws`.** The save holds exact hediff severities and body parts. For a spawned
   pawn, `jawa/pawn_get` also returns the first 40 hediffs: def, part def and severity, but not which side.

🔴 **`saveName` was NOT honoured on 2026-08-24.** The call asked for `ASHKARR_worldwork_2026_08_24`. The reply gave that
path and `exists: true`. But the game had written its CURRENT slot, `WORLDMAP_V1_original.rws`, **overwriting it**.
⚠️ The opposite was measured on 2026-08-20: `{"saveName": "rt_probe"}` did write `rt_probe.rws`. So the behaviour is
state-dependent, not a flat lie. **Stat the Saves folder yourself before you believe the path.** Never assume the slot
you overwrote was expendable.

**The envelope's `Success` is not the tool's `success`.** The operation envelope holds `"Status": 2, "Success": true`.
The payload directly below can hold `"success": false` and a refusal message. A tool that correctly refuses is a
successful *operation*. **Assert on the PAYLOAD field** (`resp.get("success") is True`). A grep of raw output for
`Success` matches the wrong field.

**An unknown parameter NAME is dropped before the tool runs.** The handler cannot see that you passed anything at all.
So you cannot tell a wrong name from an omitted one, and the call reports success. `jawa/damage` once got `targetId`
instead of `thingId`. That call damaged nothing and very nearly closed a working ion weapon as broken. **When a call
succeeds and nothing happens, suspect the parameter name before suspecting the game.**

⚠️ **`get_cell_info` does not list pawns.** A pawn spawned on a cell leaves that cell's `things: []`. That reading looks
exactly like the documented no-op failure. Check pawns with `jawa/list_pawns`, `list_colonists` or a save parse instead.

🔴 **The law's blind spot: a correct number can answer the wrong question.** `jawa/order_pawn` once returned
`canReach: true` from a real `ReachabilityUtility.CanReach` call. That call ran and answered honestly. But the call asked
about a **cell** with `PathEndMode.OnCell`. The game's own launch gate passes the **thing** with
`PathEndMode.InteractionCell`. Two verdicts wore one field name, and `true` looks identical either way. So:

* When a tool answers a question the GAME also asks, **read the engine's own call and reproduce its arguments exactly**.
  Equivalent-looking arguments are not enough.
* Before you commit any prediction, **name the exact call and the exact field that will carry the answer**. Confirm
  that the field exists **in the tool surface**, not merely in the source. A predicate that nothing returns fails
  silently: a call that answers nothing looks like a condition that did not fire.
* Where no engine call exists to copy, score a **null baseline**. A number with no baseline cannot tell "my method
  worked" from "anything would have scored that".
* **Prefer testing the MECHANISM synthetically over testing your artifact.** For example, build a sealed room from
  nothing on a throwaway map. That room tests the rule every derived claim rests on. The test needs no save, no gravship deck
  and no import of an exported gravship layout.

---

## 3. The verified palette

Full evidence in `references/capability-matrix.md`.

| goal | how |
|---|---|
| spawn a thing | `spawn_thing` (defName, x, z) — **cannot set stuff** |
| set material | `execute_debug_action` `Actions\T: Set Stuff...\<StuffDef>` + `thingId` |
| set quality | `Actions\T: Set Quality...\<Awful..Legendary>` + `thingId` |
| spawn a pawn | `jawa/spawn_pawn` (below). `Actions\Spawn Pawn...\<PawnKindDef>` + `x`/`z` only on a list without VEF: on a VEF-loaded list it NPEs (`references/traps/pawns-factions.md`) |
| dress a pawn | `select_pawn`, then `Actions\Wear apparel (selected)...\<def>` |
| strip a pawn | `Actions\Wear apparel (selected)...\*Remove all apparel` |
| kill a pawn | `Actions\T: Damage To Death` + `pawnId` |
| make a **prisoner** | `Actions\T: Turn into prisoner` + `pawnId` — works on your own colonists |
| make a **slave** | ⚠️ **spawn into ANOTHER faction first**, then imprison, then `Actions\T: Enslave`. You cannot enslave a pawn already in your faction — the call returns `success: true` and does nothing |
| build anything | `apply_architect_designator` — rectangles, `dryRun` first |
| clear ground | `jawa/destroy_batch`, or paint a terrain the plant cannot grow on (§5) |
| advance time | `jawa/safe_advance`, via `B.ticks(n)` (`validation_core._BridgeBase.ticks` → `clockgate.advance_chunk`): many ticks per frame. Raw `step_game_ticks` is one tick per frame; keep it for frame-sensitive steps (flyer landing) and legacy callers. Never an advance-read-repeat loop, and never `play_for` / unpaused play inside a proof (`skills/live-debugging-proof-harness/references/lightspeed-authoring.md` §3; `B.until`/`B.watch` PLANNED). ⚠️ Advance more than 30,000 ticks only when the colony is safe (owner, 2026-11-23; `design/RimMandrake/debug_process.md` § "A long clock advance"); `jawa/time_set_ticks` simulates nothing but ages every absolute-tick timer; ⚠️ it is REFUSED on a map with a spawned colonist unless you pass `timeException=true` (+ `why="…"`), or set the clock before the colonists exist — both in `references/silent-failures.md` |
| reload edited XML defs, no restart | ⛔ **NOTHING — `jawa/hot_reload_defs` is RETIRED** (owner, 2026-09-03: unstable). It hung a 589-mod game 5 min and left it unable to generate any pawn while reporting healthy. Restart on the minimal list instead (22 s, measured on the 13-mod list of 2026-08-19). Canonical entry `skills/rimworld-modding/SKILL.md` §2 |
| batch-read resolved defs | `jawa/get_defs` — `DefType/defName;…` pairs + reflective `fields`, dozens per call; ⚠️ scalar fields only, unless `deep=true` |
| see it | `take_screenshot` → absolute path you can read back |

🔴 **`jawa/clear_ui` before every screenshot** — see §5.

### Spawn-with-material recipe

```python
tid = rb.call("rimworld/spawn_thing", {"defName":"Apparel_PlateArmor","x":X,"z":Z})["thingId"]
rb.call("rimworld/execute_debug_action", {"path": SET_STUFF_PLASTEEL,   "thingId": tid})
rb.call("rimworld/execute_debug_action", {"path": SET_QUALITY_LEGENDARY,"thingId": tid})
# verified: "Plasteel plate armor (legendary)", stuffDefName Plasteel, hitPoints 810
```

### Spawning pawns — `jawa/spawn_pawn` works; the `GenSpawn` routes NPE

🔴 **MEASURED live on a VEF-loaded game, same map/session/defName: `rimworld/spawn_thing`
and `jawa/spawn_batch` NPE on a Pawn defName; `jawa/spawn_pawn` succeeds** (65 pawns spawned
one session, zero failures). Non-pawn Things spawn fine through all three.

- The cause: the two failing routes hand a `ThingMaker`-made Thing straight to `GenSpawn.Spawn`. So the Pawn never ran
  `PawnGenerator`, and its sub-trackers are null. The NPE comes when a mod's own `SpawnSetup` postfix (e.g. VEF) reads
  a null tracker. The consumer mod is the victim, not the cause.
- **Call `jawa/spawn_pawn` for a live pawn-spawn quicktest.**
- `jawa/spawn_batch`'s `ops` param is a STRING, not a list. The form is `'Def:x,z[,count]'`, split on `;` (2026-09-20,
  `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`).

⚠️ **`jawa/list_things` returns the faction key as `faction`, not `factionName`.** A read of the wrong key once
diagnosed a healthy player-owned ship as factionless for an hour (2026-09-09).

⚠️ **A raw hediff-severity write via `jawa/pawn_health` (`remove`+`add`+set `Severity`) never
triggers vanilla's needs recompute.** `HediffSet.DirtyCache` only refreshes the disabled-needs
cache. `AddOrRemoveNeedsAsAppropriate()` fires only from `HediffSet.AddDirect`. `AddDirect` makes that call once, at
whatever stage the hediff was at when first added. So test a stage-dependent mechanic through the
real player path (a bench recipe / bill), not a raw severity poke (2026-09-09).

---

More traps for this section: [references/traps/pawns-factions.md](references/traps/pawns-factions.md) § Spawning pawns — `jawa/spawn_pawn` works; the `GenSpawn` routes NPE.

## 4. Debug actions are the real surface

The bridge's built-in tools are a thin API. **`execute_debug_action` reaches the whole dev
menu.** A *three-mod* list gave 1,119 matches for "apparel".

`get_debug_action` returns `actionType`, which decides targeting:

| actionType | invoke with | works |
|---|---|---|
| `Action` | `path` alone, acts on **current selection** | ✅ |
| `ToolMapForPawns` | `path` + `pawnId` / `pawnName` | ⚠️ **player colonists ONLY** |
| `ToolMap` | `path` + `x`/`z`, or `thingId` | ✅ single cell, **any target** |
| anything **`(rect)`** | needs a drag | ❌ §5 |

**`pawnId` is `Thing_<id>` for `rimworld/…` tools, but bare `<id>` from
`jawa/list_pawns`.** The companion returns `Human1066`. The stock tools want
`Thing_Human1066`. The stock tools answer a bare id with *"Could not find current-map pawn"*.
That answer reads as "that pawn does not exist" rather than "wrong id format". Read
`pawnId` off `rimworld/list_colonists` when you call a `rimworld/` tool.

**`ResolvePawn` accepts player-controlled colonists only.** Its message is *"A
player-controlled colonist name or id is required."* **Hostiles cannot be
targeted by `pawnName`/`pawnId` at all.** This is why `Apply damage...` looked
mysteriously broken for so long. To affect a hostile, use a `ToolMap` action and
give it `x`/`z`. For example, `Actions\Explosion...\EMP` works on anything, anywhere.

⚠️ **`get_debug_action` returns `actionType: null` for some working leaves.** So
`get_debug_action` is not a reliable diagnostic. Compare against a known-good sibling instead.

⚠️ **Some `ToolMap` leaves refuse a `thingId` param outright despite the table above.**
`Actions\T: Resurrect` and `Actions\T: Destroy` both answer *"Could not find current-map
thing id X"* for a thing that visibly exists via `jawa/list_things`. For these specific
tools, `x`/`z` cell targeting works where `thingId` does not. Most `ToolMap` actions accept
both forms. Do not assume that every one does (2026-09-10).

🔴 **`Actions\T: Destroy` targeted by `x`/`z` destroys EVERY thing in that cell, not
just the one you meant.** One such call destroyed the damaged pipes that were
the target, and with them a healthy conduit and a decorative sign. Read `solidThingDefs` in
that cell before AND after a cell-targeted destroy. Rebuild anything that was not
the intended target (2026-09-10).

⚠️ **NEVER call `search_debug_actions` against the full mod stack — with or
without a `limit`.** It livelocked and killed a 568-mod game on 2026-08-12.
`limit` truncates the returned rows. `limit` does not bound the search, because
`totalMatchCount` walks the whole tree regardless. The old "safe with
`query` + `limit`" note was measured on three mods and does not transfer.

✅ **`list_debug_action_children` IS safe on the full stack.** `list_debug_action_children` walks one
bounded level. `search_debug_actions` traverses the whole tree.
Browse down from `list_debug_action_roots`. `Actions` has 596 children and
returns in about a second. **This is the discovery route to use on the full stack.**

**Never CONSTRUCT a leaf path. Read it and use it verbatim.** Some nodes key
on `"<defName>\t (<label>)"`, with a real tab:

```python
ch = rb.call("rimworld/list_debug_action_children", {"path": node})["children"]
P  = next(c["path"] for c in ch if c["path"].split(chr(92))[-1].startswith("MandrakeJawa"))
```

`Actions\Spawn Pawn...\<Kind>` takes the bare defName, and that path works (on a VEF-loaded
list its spawn NPEs, §3). So the tab
convention is **per-node, not global**: one node's grammar tells you nothing
about another's. A `success: false` with no message means that the path did not
resolve. That failure is different from a refusal by the action.

---

More traps for this section: [references/traps/debug-actions-ui.md](references/traps/debug-actions-ui.md) § 4. Debug actions are the real surface.

## 4b. ⚠️ Unpausing is the most consequential call on the bridge

Every other call changes one thing you named. **Unpausing hands the whole simulation
permission to act — including whatever you spawned earlier and forgot about.**

On 2026-08-12 one session ran two individually-correct tests. One spawned hostile droids for an EMP
test. The other unpaused for a voice test. ~2 in-game hours later the colony had lost 2 pawns
dead and several downed. Neither call was wrong; only the combination was.

* **Spawn hostiles at the map edge, never near the colony.**
* **Keep hostile tests PAUSED.** Debug actions apply damage with time frozen.
  `step_game_ticks` resolves an explosion **without unpausing**.
* **Before `set_time_speed(>0)`, list what is on the map.** Ask what each thing will
  do with the next few thousand ticks.
* **Re-pause the moment a timed test ends.** Thousands of ticks elapse while you
  read a screenshot.
* **Verify the pause like any mutation:** read `ticksGame` twice, seconds apart.
  `success: true` on `set_time_speed` is not evidence that time stopped.
* ⚠️ **This applies to friendly pawns too, not just hostiles.** Unpaused
  colonists treat bridge-printed furniture as theirs to optimize. In a 90k-tick
  blind run, the colony's own haulers MINIFIED two gravship fuel tanks. The haulers took
  the tanks off to a corner stockpile (2026-09-09).

---

## 5. Map authoring

**`references/map-authoring.md`** covers structures, terrain paint, batched spawns, ground clearance, and how to stage a
pawn for a photograph. The file also covers the map-scoped tools. The world, pawn and event families have their own
reference files. Read `references/map-authoring.md` before your first
`apply_architect_designator`, `jawa/set_terrain*` or `jawa/spawn_batch` call.
Four of the things in it are one-way doors:

* **god mode.** An Architect designator queues work for a colonist. So on a map
  with nobody home it returns `success: true` and builds nothing.
* **foundation → terrain → things.** `SetFoundation` is refused, silently at the
  write, on any cell that already carries a floor. There is no retrofit, and no
  inspection afterwards can see it.
* **multi-cell things spawn CENTRED** on the cell you name.
* **laying a floor and painting terrain both destroy the plants under them.**
  `restore()` (`src/RimMandrake/Utils/rimbench/terrain.py`) puts the TerrainDef back but not the plants.

One more thing in that area: **the inhabited leave/re-enter harness silently no-ops on PLAYER settlements.** The harness
is the pair of debug actions "Leave settlement now" and "Re-enter settlement here" of the Inhabited mod
(`src/RimMandrake/Inhabited/Source/DebugActions_Inhabited.cs`). The harness needs a `WorldObject_InhabitedSettlement`. On a player settlement it gives `success: true` plus a warning only in the log. The
real player-map regen route is the vanilla debug action `Actions\Regenerate Current Map`. That action wipes colonists
(Game Over letter). The action honours the tile's CURRENT biome fresh, with no restart needed (2026-09-14).

Go to `references/map-authoring.md` too in each of these cases:

* a build reported success and nothing is there;
* you need a ThingID;
* you need to damage, spawn or list a hostile;
* you need a pawn posed, dressed, restyled or re-xenotyped for a shot;
* you are about to take a screenshot. 🔴 `jawa/clear_ui` first, always. The debug log window sits exactly where
  `jump_camera_to_cell` puts your subject. That window cost twelve shots on 2026-08-14.

---

## 6. Macros that exist

| script | does |
|---|---|
| `src/RimMandrake/Utils/rimbridge_lineup.py` | one of every pawn kind in a grid, framed and shot |
| `src/RimMandrake/Utils/rimbench/crater.py` | radial crater: zones, dithered edges, ellipse squash, ejecta rays |
| `src/RimMandrake/Utils/modset_builder.py` | dependency-complete minimal mod lists (`--tier bridge` = Core, every DLC, Harmony, RimBridgeServer and two helper mods) |
| `src/RimMandrake/Utils/logwait.py` | wait on a literal `Player.log` string; only text after the call counts, no scan override |
| `src/RimMandrake/Utils/modcheck/reviewmap.py` | review maps: `save_keeper` (before/after Saves stat), `sweep_pawns` (clear hostiles), signs |

⚠️ **Do not restore the owner's mod list.** Leave ModsConfig on the tier that serves your work (root `CLAUDE.md` §Facts
you cannot guess). If you do run `modset_builder.py --restore`, know three things:

* `--restore` puts back the list from before the first `--apply` of the swap, verified by md5. `--restore` refuses a running
  game, a missing marker, a changed before-copy and a live list that it does not know. A chain of tiers keeps that
  first before-copy, or the next `--apply` refuses. `--restore-full` writes the stored full list.
* `--restore` refuses a seat that does not hold the bridge of that game. The override is `--not-my-bridge "<reason>"`.
* To count the mods of a list or a backup, parse the file and count `activeMods`. Never grep `<li>`.

**Prove new bridge work on `--tier bridge`.** That tier leaves a few suspects instead of five
hundred. Its load is seconds rather than half an hour (said of the old
3-mod tier; not re-measured at 10 entries).

---

## 7. Keep this skill learning

**Where a new finding goes — decide by WHAT FAILED, not by which file you read last:**

| the finding | file |
|---|---|
| an **engine API** reported success and changed nothing | 🔴 `references/silent-failures.md` |
| the **bridge, client, build or workflow** misled you | `references/traps.md` (the index) and `references/traps/` |
| a `jawa/world_*` behaviour | `references/world-authoring.md` |
| a `jawa/`-map or building behaviour | `references/map-authoring.md` |
| a pawn-editing behaviour | `references/pawn-authoring.md` |
| a timing number | `references/performance.md` |


After any RimBridge task, ask **what surprised you**.

* A new **verified capability** goes into §3 and `references/capability-matrix.md`, with
  the evidence that proves it.
* A **failure that cost time** goes into its topic file in `references/traps/`. Its title goes into the `traps.md`
  index. The entry gives symptom, cause, fix, and **"generalises to"**.
* When a trap would change default behaviour, **promote it here and delete it
  from the log.**

Two standing rules, both learned painfully:

1. **Never mark something broken from one example.** Test a second member of the
   same class. Read the shipped docs first: a 1,087-line tool reference
   (`docs/tool-reference.md`) and the tests sit in `vendor/mod_sources/RimBridgeServer-main/`. That folder is
   untracked: it is on the mirror `D:\Luke\dev\RimMandrake`, not in a WSL clone.
2. **Record negatives with their evidence and a confidence marker.** A wrong
   negative sends the next session down a pointless rabbit hole.

---

## 8. Speed

**Cost tracks CALL COUNT, not cell count.** That one sentence is the whole
performance model. The mechanical stack itself is cheap. Measured 2026-09-12:
≤0.1 s/action (python.exe spawn 38 ms, `hello` 0.8 ms, main-thread call ~16.6 ms median
@593 mods). **The slowness of a bridge session is LLM turns, not the bridge.**
`bridge_latency_bench.py` re-measures. So compose the sequence into a
script and run it once: that matters more than any per-call optimisation.

Batch anything you do per-cell, or design around ~20
unbatched calls per second. `jawa/set_terrain_batch` did in **1** call and
14.0 ms what 421 per-cell calls took 7.0 s to do.

⚠️ **A single latency number is not quotable.** The 16.7 ms one-frame floor was
refuted, and the cause of the spread is unknown. Record the workload and
`ticksGame` beside every benchmark. Quote a range with its conditions, or
quote nothing.

**Consequence:** prefer live bridge work over save-editing. Bridge changes are
reversible: the player reloads if they dislike the result. A save-edit
permanently changes state.

The measured tables are in **`references/performance.md`**. The tables hold the per-operation timings, the 421-cell crater at
421 vs 124 vs 1 call, and the per-formation call counts. The same file says why an old timing note does not transfer
across mod tiers. Read that file before you optimise anything and before you quote a timing. Read it also when a
loop is slower than you expected.


## 9. Extending the bridge — now its own skill

When the bridge cannot do something, **you can add a `[Tool]` method to a companion DLL.** A companion `[Tool]` is a
documented, supported path, not a hack. Every `jawa/` tool came from that path. One single day added
59 of them.

**Do not ask first, and do not poll from Python around the wall.** A thing that Python cannot control or measure today is
enough reason to add a generic tool. Examples: a capture or an act on each tick, a private value, a live write of a value,
an event between two ticks. The agent that hits the wall builds the tool, test first, or files a ticket for the tool.

**Tests, scene steps and verdicts stay in Python.** Ask of each new tool: could a scene of another mod call this tool
unchanged? Yes: an instrument, so add it. No: a test, a scene or a check of one mod, so keep it in Python. The owner's
words: `design/RimMandrake/standing_rulings.md` §What Python cannot reach goes into the bridge's C#.

⇒ **Use the `rimbridge-companion` skill.** That skill has the tool pattern, the build guards, and the
edit→build→deploy→test cycle (about **one minute** on a minimal mod list). The skill also has
the traps that make a new tool silently absent.
`references/extending.md` keeps the lower-level assembly and csproj detail.

The evidence and old figures that left this file: `references/history.md`.
