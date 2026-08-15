---
name: rimbridge
description: Drive a live RimWorld from outside via the RimBridgeServer GABP bridge - spawn pawns and things, set stuff and quality, build structures, control time, screenshot and measure results. Use when automating in-game testing, building map content, or debugging mods without clicking.
---

# Driving RimWorld from the outside

Every claim here was **verified against a running game**. Nothing is repeated
from documentation without a live test. Guesses are marked ❓, provisional
findings ⚠️.

**Skim the contents of `references/traps.md` before your first mutation, then
read the entries that match what you are about to do.** It is far too long to
read whole and every entry cost a real debugging cycle — so it opens with a
table of contents. **Read that, not the whole file**, and open only what matches
your task. The entries marked 🔴 have each destroyed something real; read those
whatever else you skip.

⚠️ **If you are about to unpause or spawn a hostile, read §4b first; if you are
about to enumerate debug actions, read §4. Those are the ones that have destroyed
things** — a colony and a 568-mod game respectively.

---

## 0. 🔴 You probably may not drive this. The bridge belongs to CHECK.

**Owner's ruling, 2026-08-15.** Bridge rights are **AGENT CHECK's at all times**.
No other seat connects and drives the game on its own initiative.

**If you are not CHECK**, the whole protocol is three one-line messages:

1. **Ask CHECK**, one line: *"Bridge free? I need N minutes for \<what\>."*
2. **Drive only after CHECK grants it.** No grant is a no.
3. **Tell CHECK the moment you are done.** This is your responsibility, not
   theirs, and it is urgent — a borrower who goes quiet has taken the bridge
   indefinitely and CHECK is blocked behind you.

These three messages are a **sanctioned exception** to the project's
two-sentence live-messaging limit (`infrastructure/agents/POLICY.md`). Nothing
else about the bridge is: everything that is not the ask, the grant or the
hand-back goes in a queue item.

### What two drivers actually does — measured 2026-08-15

CHECK and BUILD called the bridge at the same time and it **went unresponsive**.

⭐ **It did NOT crash, and the game did not need reloading.** It was **stuck**,
and it came back on its own the instant BUILD's call finished. That distinction
is worth a cold load: **if the bridge stops answering, find out who else is on it
and wait for them to release — do not restart the game.** A reload costs ~25–30
minutes and would have bought nothing here.

---

## 1. Connect

```bash
python src/RimMandrake/Utils/rimbridge_client.py --call rimbridge/get_bridge_status --yes-i-know-this-is-live
```

The client scrapes host/port/token from `Player.log`, so a session never starts
with a paste-the-token step that silently uses last launch's value.

* Port **5174**, stable. Token **changes every launch**.
* Protocol **GABP** (`gabp/1`); `session/hello` first or *"Session not established."*
* Tool names use **slashes** — `rimworld/get_game_info`. Dotted MCP spelling is rejected.
* **125 tools**: `rimworld/` (107), `rimbridge/` (18).

**Drive it as a library, never through `--json` on the command line.** Debug
action paths contain backslashes and die twice through bash then JSON.

```python
import sys; sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")   # WSL: /mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/list_colonists", {"currentMapOnly": True})
```

In heredocs prefer `chr(92)` over `"\\"` — one escaping layer fewer to get wrong.

### Before the first call

🔴 **From WSL run `python.exe`, never `python3`.** RimBridge binds **Windows
loopback** and WSL2 is a separate network namespace, so `python3` gets
`ConnectionRefusedError` and an empty token — no route, not a timeout. The choice
is **per script, not per project**: talks to the bridge → `python.exe`; reads
`/mnt/c` paths → `python3` (Windows Python cannot resolve `/mnt/c`). A script
doing both must resolve its roots per platform, and no interpreter saves it. When
a run disagrees with a peer's run of the same file, suspect the interpreter
before the data.

🔴 **Turn on Options → Run in background before any unattended run.** RimWorld
ships `<runInBackground>False</runInBackground>`; unfocused it stops running its
main loop — measured 0.5% of one core against 79% — so every game-touching call
times out at 30 s while `rimbridge/ping` answers in 0.5 ms. Set it **in the
game's menu**: `Prefs.xml` is rewritten from memory on exit, so a disk edit while
the game runs is discarded. `src/RimMandrake/Utils/game_focus.py` has a
`preflight()`. An **all-null** `get_bridge_status` — `version` included, which
cannot depend on game state — is this, not "no map is loaded".

⏳ **The bridge answering is NOT the game being reactive.** Owner's measurement,
2026-08-14: the game becomes drivable about **forty seconds** after the bridge
first responds, and every readiness flag we have describes the earlier event.
Read-only calls are fine inside that window; **hold mutations.**
`load_session.py --settle` waits it out and records the wait. Do not optimise it
away because a run once worked without it.

⚠️ **A timeout is fatal to the CONNECTION, not to the call.** The late response
sits in the socket buffer and the next request reads it as its own reply
(`unexpected response id '<guid>'`), so later numbers are quietly wrong rather
than absent. Drop the socket, open a fresh `RimBridge`, and **poll the
post-condition** — never retry on the same connection, and never re-issue a call
whose idempotence you have not established.

🔑 **Never type a namespace prefix you did not just read.** `jawa/` records
**which assembly registered the tool**, not what it does — `jawa/spawn_batch` and
`rimworld/spawn_thing` are the same verb in different namespaces, because one was
added and one was already there. Read the leaf out of
`references/capability-matrix.md`, which prints every call fully qualified.
Guessing `jawa/` is wrong about 84% of the time by count.


### Census the companion before you trust any `jawa/` call

⏳ **The companion is 26 tools and NINE of them have never run in a live game** —
the roof pair, the pawn-appearance three in `references/map-authoring.md`, and `jawa/get_defs`,
`jawa/fire_quest`, `jawa/list_things` and `jawa/clear_ui` (all deployed
2026-08-14 in the shutdown window, game copy md5 `55b2362`). They compile; nothing more is claimed. `jawa/list_factions` and
`jawa/order_pawn` **drove live 2026-08-14** and are no longer on this list;
`jawa/world_stats` was called and its answer was thrown away by a harness bug, so
it is unproven for a different reason. Companions register only at RimBridgeServer
startup. **First call of the next session: count the `jawa/` tools the bridge
reports — 26 means the current deploy took, 24 means the build before
`list_things`/`clear_ui`, 22 means before `get_defs`/`fire_quest`, 21 means before
`world_stats`, 7 means an older companion, 0 means the bundle did not load.** Every
other check is uninformative until that reads 26. 🔴 **The deploy must use
`--gm`**, or the game copy loses `jawa/fire_incident` and `jawa/send_letter` and
the census reads 24.

⚠️ **Three documents disagreed about this number on 2026-08-13** — 17 in
`EXPECTED_FAILURES_next_load.md`, 20 in `NEXT_RELOAD.md`, 21 here — and the
number moved again to **22** the same night, and to **26** on 2026-08-14.
**Measure it, do not quote it** — `load_session.py` now derives the gate from
`EXPECTED_TOOLS` and `prove_new_tools.py` reads it out of the deployed DLL, so
neither carries a literal to go stale.
A census gate that three files answer differently is worse than no gate, so
check the DLL rather than any of the three:
`strings -a "<gamedir>\BridgeTools\JawaBench\JawaBench.BridgeTools.dll" | grep -o "jawa/[a-z_]*" | sort -u | wc -l`.
🔴 **That command proves a tool NAME only.** Tool names are attribute blobs and
are UTF-8; a method-body MESSAGE is UTF-16LE and needs `strings -a -el`, or it
reports ABSENT on a string that is present.
Deciding strings per tool: `src/RimMandrake/bridgetools/prove_new_tools.py`.

---

## 2. The one law

> **`success: true` means the tool RAN, not that the game CHANGED.**

`spawn_thing` returns a real `thingId` while logging an error. Every
`Set terrain (rect)` call returns success and changes nothing. **Verify every
mutation against an independent channel**, cheapest first:

1. **`effects` on the response** — `effects.logs` / `logCount` is per-call log
   capture. Read it on every mutation. But `effects.debugToolChanged` is **NOT**
   a success signal (see traps).
2. **`get_cell_info`** — what is actually in a cell, including `stuffDefName`.
3. **`save_game` then parse the `.rws`** — exact hediff severities and body
   parts; the only way to measure damage. `save_game` **ignores your
   `fileName`** and writes `rimbridge_save_<timestamp>.rws`.

🔑 **The envelope's `Success` is not the tool's `success`.** `"Status": 2,
"Success": true` on the operation envelope sits directly above `"success": false`
and a refusal message in the payload — a tool that correctly refuses is a
successful *operation*. **Assert on the PAYLOAD field**
(`resp.get("success") is True`); grepping raw output for `Success` matches the
wrong one.

🔑 **An unknown parameter NAME is dropped before the tool runs**, so a wrong name
is indistinguishable from an omitted one and the call reports success — the
handler cannot see that you passed anything at all. `jawa/damage` given
`targetId` instead of `thingId` damaged nothing and very nearly closed a working
ion weapon as broken. **When a call succeeds and nothing happens, suspect the
parameter name before suspecting the game.**

⚠️ **`get_cell_info` does not list pawns.** A pawn spawned on a cell leaves that
cell's `things: []`, which reads exactly like the documented no-op failure. Check
pawns with `jawa/list_pawns`, `list_colonists` or a save parse instead.

🔴 **The law's blind spot: a correct number can answer the wrong question.**
`jawa/order_pawn` once returned `canReach: true` from a real
`ReachabilityUtility.CanReach` call that ran and answered honestly — against a
**cell** with `PathEndMode.OnCell`, where the game's own launch gate passes the
**thing** with `PathEndMode.InteractionCell`. Two verdicts wearing one field
name, and `true` looks identical either way. So:

* When a tool answers a question the GAME also asks, **read the engine's own call
  and reproduce its arguments exactly** — not an equivalent-looking one.
* Before committing any prediction, **name the exact call and the exact field
  that will carry the answer**, and confirm that field exists **in the tool
  surface**, not merely in the source. A predicate nothing returns fails
  silently: a call that answers nothing looks like a condition that did not fire.
* Where no engine call exists to copy, score a **null baseline**. A number with
  no baseline cannot tell "my method worked" from "anything would have scored
  that".
* ⭐ **Prefer testing the MECHANISM synthetically over testing your artifact** —
  a sealed room built from nothing on a throwaway map tests the rule every
  derived claim rests on, and needs no save, no deck and no import.

---

## 3. The verified palette

Full evidence in `references/capability-matrix.md`.

| goal | how |
|---|---|
| spawn a thing | `spawn_thing` (defName, x, z) — **cannot set stuff** |
| set material | `execute_debug_action` `Actions\T: Set Stuff...\<StuffDef>` + `thingId` |
| set quality | `Actions\T: Set Quality...\<Awful..Legendary>` + `thingId` |
| spawn a pawn | `Actions\Spawn Pawn...\<PawnKindDef>` + `x`/`z` |
| dress a pawn | `select_pawn`, then `Actions\Wear apparel (selected)...\<def>` |
| strip a pawn | `Actions\Wear apparel (selected)...\*Remove all apparel` |
| kill a pawn | `Actions\T: Damage To Death` + `pawnId` |
| make a **prisoner** | `Actions\T: Turn into prisoner` + `pawnId` — works on your own colonists |
| make a **slave** | ⚠️ **spawn into ANOTHER faction first**, then imprison, then `Actions\T: Enslave`. You cannot enslave a pawn already in your faction — the call returns `success: true` and does nothing |
| build anything | `apply_architect_designator` — rectangles, `dryRun` first |
| clear ground | `jawa/destroy_batch`, or paint a terrain the plant cannot grow on (§5) |
| advance time | `step_game_ticks` (exact) or `play_for` (wall-clock) |
| see it | `take_screenshot` → absolute path you can read back |

🔴 **`jawa/clear_ui` before every screenshot** — see §5.

### Spawn-with-material recipe

```python
tid = rb.call("rimworld/spawn_thing", {"defName":"Apparel_PlateArmor","x":X,"z":Z})["thingId"]
rb.call("rimworld/execute_debug_action", {"path": SET_STUFF_PLASTEEL,   "thingId": tid})
rb.call("rimworld/execute_debug_action", {"path": SET_QUALITY_LEGENDARY,"thingId": tid})
# verified: "Plasteel plate armor (legendary)", stuffDefName Plasteel, hitPoints 810
```

---

## 4. Debug actions are the real surface

The 125 tools are a thin API. **`execute_debug_action` reaches the whole dev
menu** — 1,119 matches for "apparel" on a *three-mod* list.

`get_debug_action` returns `actionType`, which decides targeting:

| actionType | invoke with | works |
|---|---|---|
| `Action` | `path` alone, acts on **current selection** | ✅ |
| `ToolMapForPawns` | `path` + `pawnId` / `pawnName` | ⚠️ **player colonists ONLY** |
| `ToolMap` | `path` + `x`/`z`, or `thingId` | ✅ single cell, **any target** |
| anything **`(rect)`** | needs a drag | ❌ §5 |

🔑 **`pawnId` is `Thing_<id>` for `rimworld/…` tools, but bare `<id>` from
`jawa/list_pawns`.** The companion returns `Human1066`; the stock tools want
`Thing_Human1066` and answer a bare id with *"Could not find current-map pawn"*,
which reads as "that pawn does not exist" rather than "wrong id format". Read
`pawnId` off `rimworld/list_colonists` when calling a `rimworld/` tool.

🔑 **`ResolvePawn` accepts player-controlled colonists only** — *"A
player-controlled colonist name or id is required."* **Hostiles cannot be
targeted by `pawnName`/`pawnId` at all.** This is why `Apply damage...` looked
mysteriously broken for so long. To affect a hostile, use a `ToolMap` action and
give it `x`/`z`: `Actions\Explosion...\EMP` works on anything, anywhere.

⚠️ **`get_debug_action` returns `actionType: null` for some working leaves**, so
it is not a reliable diagnostic. Compare against a known-good sibling instead.

⚠️ **NEVER call `search_debug_actions` against the full mod stack — with or
without a `limit`.** It livelocked and killed a 568-mod game on 2026-08-12.
`limit` truncates the returned rows; it does not bound the search, because
`totalMatchCount` requires walking the whole tree regardless. The old "safe with
`query` + `limit`" note was measured on three mods and does not transfer.

✅ **`list_debug_action_children` IS safe on the full stack** — it walks one
bounded level, unlike `search_debug_actions`, which traverses the whole tree.
Browse down from `list_debug_action_roots`; `Actions` has 596 children and
returns in about a second. **This is the discovery route to use on the full stack.**

🔑 **Never CONSTRUCT a leaf path — read it and use it verbatim.** Some nodes key
on `"<defName>\t (<label>)"`, with a real tab:

```python
ch = rb.call("rimworld/list_debug_action_children", {"path": node})["children"]
P  = next(c["path"] for c in ch if c["path"].split(chr(92))[-1].startswith("BTD_Jawa"))
```

`Actions\Spawn Pawn...\<Kind>` takes the bare defName and works, so the tab
convention is **per-node, not global** — one node's grammar tells you nothing
about another's. A `success: false` with no message means the path did not
resolve, which is a different failure from the action refusing.

---

## 4b. ⚠️ Unpausing is the most consequential call on the bridge

Everything else changes one thing you named. **This hands the whole simulation
permission to act — including whatever you spawned earlier and forgot about.**

On 2026-08-12 two individually-correct tests (spawn hostile droids for an EMP
test; unpause for a voice test) were run in the same session. ~2 in-game hours
later the colony had lost 2 pawns dead and several downed. Neither call was
wrong; only the combination was.

* **Spawn hostiles at the map edge, never near the colony.**
* **Keep hostile tests PAUSED.** Debug actions apply damage with time frozen;
  `step_game_ticks` resolves an explosion **without unpausing**.
* **Before `set_time_speed(>0)`, list what is on the map** and ask what it will
  do with the next few thousand ticks.
* **Re-pause the moment a timed test ends** — thousands of ticks elapse while you
  read a screenshot.
* **Verify the pause like any mutation:** read `ticksGame` twice, seconds apart.
  `success: true` on `set_time_speed` is not evidence that time stopped.

---

## 5. Map authoring

Building structures, painting terrain, batching spawns, clearing ground, staging
a pawn for a photograph, and the full table of the companion's `jawa/` tools:
**`references/map-authoring.md`**. Read it before your first
`apply_architect_designator`, `jawa/set_terrain*` or `jawa/spawn_batch` call —
four of the things in it are one-way doors:

* **god mode** — an Architect designator queues work for a colonist, so on a map
  with nobody home it returns `success: true` and builds nothing.
* **foundation → terrain → things** — `SetFoundation` is refused, silently at the
  write, on any cell that already carries a floor. There is no retrofit and no
  inspection afterwards can see it.
* **multi-cell things spawn CENTRED** on the cell you name.
* **laying a floor and painting terrain both destroy the plants under them**, and
  `restore()` puts the TerrainDef back but not the plants.

Go there too when: a build reported success and nothing is there · you need a
ThingID · you need to damage, spawn or list a hostile · you need a pawn posed,
dressed, restyled or re-xenotyped for a shot · you are about to take a screenshot
(🔴 `jawa/clear_ui` first, always — the debug log window sits exactly where
`jump_camera_to_cell` puts your subject, and it cost twelve shots on 2026-08-14).

---

## 6. Macros that exist

| script | does |
|---|---|
| `src/RimMandrake/Utils/rimbridge_lineup.py` | one of every pawn kind in a grid, framed and shot |
| `src/RimMandrake/Utils/rimbench/crater.py` | radial crater: zones, dithered edges, ellipse squash, ejecta rays |
| `src/RimMandrake/Utils/modset_builder.py` | dependency-complete minimal mod lists (`--tier bridge` = 3 mods) |

**Prove new bridge work on the 3-mod tier.** Three suspects instead of five
hundred, and the load is seconds rather than half an hour.

---

## 7. Keep this skill learning

After any RimBridge task, ask **what surprised you**.

* New **verified capability** → §3 and `references/capability-matrix.md`, with
  the evidence that proves it.
* A **failure that cost time** → `references/traps.md`: symptom, cause, fix, and
  **"generalises to"**.
* When a trap would change default behaviour, **promote it here and delete it
  from the log.**

Two standing rules, both learned painfully:

1. **Never mark something broken from one example.** Test a second member of the
   same class, and read the shipped docs first — full MIT source and a
   1,087-line tool reference sit in `vendor/mod_sources/RimBridgeServer-main/`.
2. **Record negatives with their evidence and a confidence marker.** A wrong
   negative sends the next session down a pointless rabbit hole.

---

## 8. Speed

**Cost tracks CALL COUNT, not cell count.** That one sentence is the whole
performance model. Batch anything you do per-cell, or design around ~20
unbatched calls per second — `jawa/set_terrain_batch` did in **1** call and
14.0 ms what 421 per-cell calls took 7.0 s to do.

⚠️ **A single latency number is not quotable.** The 16.7 ms one-frame floor was
refuted and the cause of the spread is unknown. Record the workload and
`ticksGame` beside every benchmark, and quote a range with its conditions or
quote nothing.

**Consequence:** prefer live bridge work over save-editing. Bridge changes are
reversible — the player reloads if they dislike the result — where a save-edit
permanently changes state.

The measured tables — per-operation timings, the 421-cell crater at 421 vs 124 vs
1 call, per-formation call counts, and why an old timing note does not transfer
across mod tiers — are in **`references/performance.md`**. Read it before you
optimise anything, before you quote a timing, and when a loop is slower than you
expected.


## 9. Extending the bridge

When the bridge cannot do something, **adding a `[Tool]` method to a companion
DLL is a documented, supported path, not a hack** — it is where every `jawa/`
tool came from. **`references/extending.md`** has the source and build paths, the
compile-against-the-running-game's-own-assemblies pattern that makes a guessed
API a compiler error instead of a live failure, `IRimBridgeContext`'s composition
surface, and the `ExcludeAssets="runtime"` gotcha. Read it before you conclude
"the bridge cannot do X".
