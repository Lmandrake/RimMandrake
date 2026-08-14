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

⚠️ **If you are about to unpause, spawn a hostile, or enumerate tools, read those
three entries first — they are the ones that have destroyed things.**

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

**Structure printing works today.** A 13×11 furnished room took 21 calls and
~40 seconds: wall rects, a floor rect, a door, 4 beds, an end table, a dining
table with chairs, 2 lamps, a plant pot.

```python
put(WALL,  X,   Z,   W,   1)      # rectangles, not cells
put(FLOOR, X+1, Z+1, W-2, H-2)    # interior
put(DOOR,  X+6, Z)
```

Three things make it a real generator:

* `apply_architect_designator` takes **`width`/`height`**.
* **`dryRun: true`** validates without mutating. **Use it** — two workbenches
  failed because they were given corners with no clearance.
* **`flood_fill_cells` with a `designatorId`** is a *site finder*: every cell
  where that building legally fits, honouring footprint, anchor, walkability
  and pawn reachability.

**God mode makes placement instant** — real things, not blueprints.

### 🔑 Laying a floor destroys what is under it

The most useful discovery for map authoring. A floor rectangle wipes grass,
bushes and plants inside it. This is the **indirect destruction primitive** —
there is no working direct one.

### ✅ Natural terrain IS painted — by our companion, not by the bridge

RimWorld's own `Set terrain (rect)` and `Clear area (rect)` still return
`success: true` and do nothing; they are drag tools and the bridge cannot drag.
**Do not call them.** The working route is the `JawaBench.BridgeTools` companion:

**Authoring — the terrain and object primitives**

| tool | use |
|---|---|
| `jawa/set_terrain` | one cell or one rect. `layer` = `top` \| `under`, `refresh` defaults true |
| `jawa/set_terrain_batch` | **many rects in one call** — this is the one a generator uses |
| `jawa/get_terrain_batch` | **read many cells in one call**, answering in the same ops grammar `set_terrain_batch` accepts — so a capture replays straight back as a restore |
| `jawa/spawn_batch` | **many things in one call**. Routes filth through `FilthMaker` (which declines cells whose terrain refuses filth) and everything else through `GenSpawn` |
| `jawa/destroy_batch` | **the first working direct destruction primitive.** Filter by category — `Plant`, `Item`, `Filth`, `Building`, `All`. **Never destroys pawns**, whatever you pass |
| `jawa/set_plants` | plant vegetation at a chosen growth stage; a refused cell reports why |
| `jawa/refresh_rect` | dirty the map mesh over a rect **without painting**. Paint many rects with `refresh=false`, then dirty the region once |

**Inspection — the things the stock bridge cannot answer**

| tool | use |
|---|---|
| `jawa/list_pawns` | every pawn on the map — **hostiles and animals too**, not just colonists. `rimworld/list_colonists` and `ResolvePawn` are player-side only |
| `jawa/list_things` | **the ThingID of a non-pawn** — the id `jawa/damage thingId=`, `jawa/order_pawn targetId=` and the destroy tools all demand and nothing else could produce. Filter by `defName` (comma list), `rect` or `group`. 🔴 **A zero is a filter result, not an empty map**: read `scanned` beside it, and `countMatched` beside `countReturned`. Before this, the only source of a ThingID was a human clicking the object, and the `NoPathToPilotConsole` v1 gate was SKIPPED on 2026-08-14 for exactly that |
| `jawa/get_def` | a def **as the game resolved it**, after patches and parent inheritance: `statBases`, comps with class names, and the mod that supplied it. The offline dump serialises none of that and has produced two wrong conclusions |
| `jawa/drain_log` | recent log messages. `effects.logs` structurally cannot see anything logged **during `step_game_ticks`** |
| `jawa/damage` | graduated damage to **anything, including hostiles**, via `Thing.TakeDamage`. The debug menu's `Apply damage...` is inert and player-side only |
| `jawa/spawn_pawn` | a pawn **in a chosen faction** — `player` \| `hostile` \| `none` \| a FactionDef. The debug menu always spawns player-side, which is how a "hostile" test ends up standing in your colony. `xenotype` forces a XenotypeDef **at generation time** via `PawnGenerationRequest.ForcedXenotype`, which `PawnGenerator` checks first and returns on, so it beats the kind's and the faction's own rolls |
| `jawa/list_factions` | every faction on the world, hidden ones included. Read `countAllIncludingHidden`, **never** `countReturned` — `includeHidden` defaults false and the visible subset read 34 against a true 54 |

**Staging a pawn for a look — art, apparel and xenotype audits**

| tool | use |
|---|---|
| `jawa/set_pawn_rotation` | turn pawns to a named facing and **freeze them there** with `debugRotLocked`. A bare rotation write does not survive: the rotation tracker re-faces every pawn each tick from its job and drafted state. `dir='unlock'` releases. 🔴 **Always unlock when done** — `debugRotLocked` is written by `Thing.ExposeData`, so a pawn left locked stays locked across a save and load |
| `jawa/set_pawn_style` | hair, hair colour, beard, face and body tattoo, head type, body type, fur, skin colour. Every field optional; all defNames resolve **before** anything is written, so a typo changes nothing. Calls `Notify_StyleItemChanged()`, which is what rebuilds the graphics — without it the change is correct in the save and stale on screen |
| `jawa/set_pawn_xenotype` | convert spawned pawns to a XenotypeDef in place — what the vanilla dev "Set xenotype" action does, which is `pawn.genes?.SetXenotype(def)` and nothing else. ⚠️ It clears **xenogenes only**: an inheritable xenotype's genes land as endogenes and survive a later conversion, so pass `clearEndogenes` when converting a pawn that already has one. Jawa xenotypes on this stack: `BTD_Jawa` (the one our patches target), `OuterRim_Jawa`, `guy762_xenotype_jawa` |

⚠️ **All three refuse rather than pretend when the DLC is absent** — tattoos need
Ideology and xenotypes need Biotech, and RimWorld's own setters *return silently*
in both cases. A rotation applied to a **downed or sleeping** pawn is likewise a
perfect no-op: the renderer calls `LayingFacing()` for any non-standing posture
and ignores `Rotation` entirely, so the tool reports `visible: false` and you
photograph nothing.

**🔴 GM — these let the world act on the PLAYER**

| tool | use |
|---|---|
| `jawa/fire_incident` | fire a storyteller incident: raid, trader, flare, infestation. **`dryRun: true` asks whether it CAN fire without firing it — use that first** |
| `jawa/send_letter` | write to the notification pane, with an optional camera target. The only way to narrate into the game rather than into a chat window |

⚠️ **Everything else on this bridge changes only what the caller named. These two
do not.** The owner ruled on 2026-08-12 that they ship, and they are gated behind
a compile-time flag so the ruling is reversible in one shutdown window —
`src/RimMandrake/bridgetools/build.py` **without** `--gm` compiles them out, and the build refuses
to continue if the artifact disagrees with the flag. Never fire an incident on a
colony that matters without saying so first.

⏳ **The companion is 25 tools and EIGHT of them have never run in a live game** —
the roof pair, the pawn-appearance three above, and `jawa/get_defs`,
`jawa/fire_quest` and `jawa/list_things` (all deployed 2026-08-14 in the shutdown
window, game copy md5 `13fcb549`). They compile; nothing more is claimed. `jawa/list_factions` and
`jawa/order_pawn` **drove live 2026-08-14** and are no longer on this list;
`jawa/world_stats` was called and its answer was thrown away by a harness bug, so
it is unproven for a different reason. Companions register only at RimBridgeServer
startup. **First call of the next session: count the `jawa/` tools the bridge
reports — 25 means the current deploy took, 24 means the build before
`list_things`, 22 means before `get_defs`/`fire_quest`, 21 means before
`world_stats`, 7 means an older companion, 0 means the bundle did not load.** Every
other check is uninformative until that reads 25. 🔴 **The deploy must use
`--gm`**, or the game copy loses `jawa/fire_incident` and `jawa/send_letter` and
the census reads 23.

⚠️ **Three documents disagreed about this number on 2026-08-13** — 17 in
`EXPECTED_FAILURES_next_load.md`, 20 in `NEXT_RELOAD.md`, 21 here — and the
number moved again to **22** the same night, and to **25** on 2026-08-14.
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

The write tools read every cell back off the terrain grid before answering, so
`cellsFailedVerify` is real evidence rather than the usual `success: true`.

**Go through `src/RimMandrake/Utils/rimbench/terrain.py`, not the raw tools.** `TerrainPainter`
probes which route the running game supports, decomposes a cell map to rects
once, chunks against the companion's compiled-in guards (`MAX_OPS` 4096,
`MAX_CELLS` 70,000), and captures originals so a formation can undo itself. The
whole pipeline is proven offline — `python3 src/RimMandrake/Utils/rimbench/selftest.py`, no game
needed, under a second.

```python
tp = TerrainPainter(s)
tp.capture(cellmap)        # 1 call/cell — skip on a scratch map
tp.paint_map(cellmap)      # a 400-cell crater: 115 rects, ONE call
tp.restore()
```

**Call count is the only cost that matters.** A 6×6 rect is 15 ms; the same 411
cells as a dithered crater were 103 separate calls and 5.15 s. Batching a
formation is the whole reason the companion exists — never loop `set_terrain`
per cell.

### 🔑 Terrain choice is vegetation control

Painting **does** destroy plants — but only where the plant cannot grow on the
new terrain. Measured live on grass, dandelion and chokevine:

| new terrain | plants |
|---|---|
| Sand, PackedDirt, WaterShallow, `<stone>_Rough` | **destroyed** |
| **Gravel** | **survive** |
| the cell's own existing terrain | no-op, nothing dies |

So a "gravel crater bowl" fills with healthy grass and looks absurd. Choose
terrain for what it does to the vegetation as well as for its colour. This
replaces flooring as the way to clear ground.

### ⚠️ Restoring terrain is NOT undoing the paint

`capture()`/`restore()` puts the **TerrainDef** back — verified over 2,601 cells,
0 wrong — and leaves the ground bare, because the plants the paint destroyed do
not come back. Say "terrain is exactly restorable", never "the paint is
reversible". On a colony that matters, **the save is the undo.**

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

## 8. Speed — measured, and it changes the design

**Cost tracks CALL COUNT, not cell count.** That one sentence is the whole
performance model, and everything below follows from it.

| operation | measured |
|---|---|
| `rimbridge/ping` | 0.3 ms — does not touch the main thread |
| any main-thread call | **~16.7 ms**, one 60 Hz frame. This is the floor |
| `save_game` (13.9 MB) | 0.5 s |

A call in a tight sequence costs ~50 ms, three frames — not the 16.7 ms an
isolated call costs. So the number that matters is how many calls you make:

| a 421-cell dithered crater | calls | time |
|---|---|---|
| one cell at a time | 421 | ~7.0 s |
| one call per rect | 124 | 1,611 ms |
| **`jawa/set_terrain_batch`** | **1** | **14.0 ms** |
| capture, one `get_cell_info` per cell | 421 | 6,086 ms |
| **`jawa/get_terrain_batch`** | **1** | **17.5 ms** |

Measured 2026-08-12 on a live 250×250 map. A whole `formations.crater()` — 977
ground cells plus 100 scattered objects — is **0.52 s**, of which the terrain is
a single hop.

**Consequence:** each time you batch one layer, the cost moves to the next.
Terrain stopped dominating and object spawning took over — a crater became one
terrain call and ~100 `spawn_thing` calls. `jawa/spawn_batch` closes that too.
Measured against a stub, per formation:

| formation | per-call companion | batched |
|---|---|---|
| crater | 199 calls | **2** |
| cavern | 49 calls | **1** |
| geyser field | 67 calls | **2** |

Batch anything you do per-cell, or design around ~20 unbatched calls per second.
`src/RimMandrake/Utils/rimbench/selftest.py` asserts these call counts, so a refactor that
reintroduces a per-cell loop fails a test rather than just running 100× slower.

⚠️ The old "0.002 s per call" figure in this file was measured on **3 mods,
paused**, and did not survive the full stack. Treat any timing note as carrying
the tier it was measured on.

**Consequence:** prefer live bridge work over save-editing. Bridge changes are
also **reversible** — the player reloads if they dislike the result — where a
save-edit permanently changes state.

Full reasoning, tradeoffs and the test order:
`design/RimMandrake/map_authoring_decision.md`.

## 9. Extending the bridge — companion DLLs are a first-class path

RimBridgeServer 2.x loads mod-authored `[Tool]` methods from `BridgeTools`
folders. This is documented and supported, not a hack:

* `vendor/mod_sources/RimBridgeServer-main/skills/rimbridge-companion-tools/SKILL.md`
* `vendor/mod_sources/RimBridgeServer-main/skills/rimbridge-companion-tools/references/companion-dll-guide.md` (243 lines: csproj, load model,
  authoring pattern, validation checklist)

**This stopped being a proposal.** The three methods sketched here originally —
`set_terrain`, `destroy_at`, `damage` — became the 14 tools in §5; `destroy_at`
generalised into `jawa/destroy_batch`, because call count turned out to be the
only cost that matters (§8). Source and build:

```
src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs   all 14 [Tool] methods
src/RimMandrake/bridgetools/build.py                                        build + verify + deploy
```

The pattern that made them cheap to add: **compile against the running game's own
assemblies** (`Assembly-CSharp.dll` from the install, `RimBridgeServer.Sdk.dll`
from the workshop copy). The compiler then verifies every API you guessed at —
`FilthMaker.TryMakeFilth`, `ThingMaker.MakeThing`, `GenSpawn.Spawn`,
`thingGrid.ThingsListAtFast` were all confirmed that way, and **a compiler is a
better checker than IL archaeology.**

`IRimBridgeContext` also exposes `ctx.Tools.CallAsync` for composing existing
tools, `ctx.Game.StepTicksAsync/RunUntilAsync`, and `RimBridgeEvidenceManifest`
— a built-in screenshot-plus-assertion result format that is RimBench already
designed for us.

Gotcha the guide flags: `ExcludeAssets="runtime"` so the companion never bundles
`RimBridgeServer.Sdk.dll`; the host resolves it.
