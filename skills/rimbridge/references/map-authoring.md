# Map authoring — building, terrain, batches and staging

Read this before your first `apply_architect_designator`, `jawa/set_terrain*` or
`jawa/spawn_batch` call. It is the detail behind §5 of the skill.

---

## Structure printing

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
* 🔑 **A `designatorId` is a UI path, not a defName** — `architect-designator:
  floors:build-concrete`, not `Floor_Concrete`. **Resolve it at runtime** by
  matching the trailing segment (`find_designator` in
  `src/RimMandrake/Utils/bridge_latency.py`); `list_architect_designators` needs
  a `categoryId` from `list_architect_categories` and returns dropdown parents
  beside leaves. **Never hardcode one** — ids carrying a positional index
  (`…-tutortagnotset-3`) renumber as mods add architect entries, so a path
  captured on the 3-mod tier is not safe at 568.

### 🔑 God mode is the other half of authoring — turn it on, then off

An Architect designator **queues work for a colonist**. On an authored or wiped
map there is nobody home, so `apply_architect_designator` returns `success: true`,
sets `designationCount: 1`, and changes nothing — the call is not lying, it did
designate. `rimworld/set_god_mode {"enabled": true}` converts designators to
instant effect and adds the fill/refuel button to refuelable things (there is no
refuel primitive on the bridge; in god mode it is a **button on the thing's
menu**). It also matters for `spawn_batch`, which places buildings **factionless**
— a `GravEngine` then shows `Claim` disabled and offers no Launch gizmo.

⚠️ **Turn it back off** (`{"enabled": false}`): left on, everything the owner
builds next is free and instant, and they save a god-mode map without knowing.
⚠️ **A cell that already carries a designation refuses a second one**
(`success: false`) — cancel first with the category's `…-cancel` designator.

📌 Before concluding "the bridge cannot do X", ask what the UI would do with the
same click: the answer is often "X needs a worker and there is nobody home".

### 🔴 The build order is foundation → terrain → things, and it is the only one

`SetFoundation` is **refused on any cell that already carries a floor, silently
at the write** — `jawa/set_terrain_batch layer='foundation'` reported
`cellsChanged: 16` with `cellsFailedVerify: 12` on the 12 cells that had a floor.
Controlled three ways: bare ground 25/0/25 hold; `MetalTile` first
25/**25 failedVerify**/0; foundation then floor 25/0/25, surviving the floor.
**There is no retrofit** — a floor is a one-way door, recoverable only by
demolish-and-rebuild and undetectable by inspection afterwards. Only the
read-back catches it.

⚠️ **Affordance does not gate spawning.** `GravshipHull` declares
`terrainAffordanceNeeded=Substructure` and spawns happily on bare ground, because
`jawa/spawn_batch` routes through `GenSpawn`, which checks no affordance —
affordance constrains the *designator*. A substructure-less ship is buildable and
**not a gravship**, which is worse, because everything looks right.

### 🔑 Multi-cell things spawn CENTRED on the cell you name

`GenAdj.OccupiedRect` computes `minX = loc.x - (w-1)/2`, so `GravEngine:172,172`
— a 3×3 — occupies x/z **171–173**. Emit **centres** in any `Def:x,z` op grammar,
and test coordinate semantics with the **largest** thing you have, never the most
common one: 1×1 things read identically under both conventions, so a plan that is
95% single-cell looks perfect while every large thing places wrong.

### ⏳ Assert after time has run, not at tick 0

A tool-built thing arrives in a state no played thing is ever in: every cached
comp value is cold and several refresh only on their own tick. A `ChemfuelTank`
filled by hand on a **paused** map still failed the launch check for "not enough
fuel" — the thrusters had not registered it. `ticksGame: 1` on every read-back is
the tell that you are asserting before the game has had a chance to disagree.
**Do not treat a refusal on a paused, just-built object as a defect** — run time
briefly and re-read.

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
| `jawa/clear_ui` | 🔴 **call this before EVERY screenshot.** The Debug log window covers the centre of the screen — exactly where `jump_camera_to_cell` puts the subject — so a shot taken without it photographs the log, not the map. All twelve art screenshots of the 2026-08-14 session were lost to this and had to be re-shot. Closing the log by hand does not hold: auto-open-on-error reopens it. `rimbench.core.look()` calls it automatically |
| `jawa/list_things` | **the ThingID of a non-pawn** — the id `jawa/damage thingId=`, `jawa/order_pawn targetId=` and the destroy tools all demand and nothing else could produce. Filter by `defName` (comma list), `rect` or `group`. 🔴 **A zero is a filter result, not an empty map**: read `scanned` beside it, and `countMatched` beside `countReturned`. Before this, the only source of a ThingID was a human clicking the object, and the `NoPathToPilotConsole` v1 gate was SKIPPED on 2026-08-14 for exactly that |
| `jawa/get_def` | a def **as the game resolved it**, after patches and parent inheritance: `statBases`, comps with class names, and the mod that supplied it. The offline dump serialises none of that and has produced two wrong conclusions. 🔴 **Any question of the form "does this def have X" is a LIVE question** — a mod restamps defs at load and nothing about that is visible in the XML: `GravEngine` carries `CompProperties_Power` / `CompPowerPlantGravEngine` that `Buildings_Gravship.xml` does not show, so "none of these need power" was wrong off a clean grep. Use the disk for structure and names only. ⚠️ The reader is **blind to properties and privates** — `Scalars()` enumerates `Public \| Instance` **fields** only, so `BiomeDef`'s `wildAnimals`, `pollutionWildAnimals` and `diseases` (private) and `AllWildAnimals` (property) are invisible, and a requested field comes back `"(no such field)"` whether it is misspelled or merely unreachable. Check the instrument can SEE a field (`meta.py <Type>` in `ilprobe`) before calling a conclusion "judged from def fields" |
| `jawa/drain_log` | recent log messages. `effects.logs` structurally cannot see anything logged **during `step_game_ticks`** |
| `jawa/damage` | graduated damage to **anything, including hostiles**, via `Thing.TakeDamage`. The debug menu's `Apply damage...` is inert and player-side only. ⚠️ **`amount` is a request, not a result** — a single instance is capped by the body part it hits plus armour, so `amount=400` landed as `totalDamageDealt: 32.0` and the pawn lived. Read the delivered quantity back, and for cleanup loop until `dead`/`destroyed` with exhausted attempts as a loud failure |
| `jawa/spawn_pawn` | a pawn **in a chosen faction** — `player` \| `hostile` \| `none` \| a FactionDef. The debug menu always spawns player-side, which is how a "hostile" test ends up standing in your colony. `xenotype` forces a XenotypeDef **at generation time** via `PawnGenerationRequest.ForcedXenotype`, which `PawnGenerator` checks first and returns on, so it beats the kind's and the faction's own rolls. ⚠️ **Never pass `"hostile"`** — it resolves by `FirstOrDefault` and lands on Insect/Hive, where a humanlike pawn throws inside `PawnGenerator.GeneratePawn` (*"Humanlike pawn X was added to non-humanlike faction hive"*) and looks like an intermittent unrelated failure. Name the FactionDef |
| `jawa/list_factions` | every faction on the world, hidden ones included. Read `countAllIncludingHidden`, **never** `countReturned` — `includeHidden` defaults false and the visible subset read 34 against a true 54 |

**Staging a pawn for a look — art, apparel and xenotype audits**

| tool | use |
|---|---|
| `jawa/set_pawn_rotation` | turn pawns to a named facing and **freeze them there** with `debugRotLocked`. A bare rotation write does not survive: the rotation tracker re-faces every pawn each tick from its job and drafted state. `dir='unlock'` releases. 🔴 **Always unlock when done** — `debugRotLocked` is written by `Thing.ExposeData`, so a pawn left locked stays locked across a save and load |
| `jawa/set_pawn_style` | hair, hair colour, beard, face and body tattoo, head type, body type, fur, skin colour. Every field optional; all defNames resolve **before** anything is written, so a typo changes nothing. Calls `Notify_StyleItemChanged()`, which is what rebuilds the graphics — without it the change is correct in the save and stale on screen |
| `jawa/set_pawn_xenotype` | convert spawned pawns to a XenotypeDef in place — what the vanilla dev "Set xenotype" action does, which is `pawn.genes?.SetXenotype(def)` and nothing else. ⚠️ It clears **xenogenes only**: an inheritable xenotype's genes land as endogenes and survive a later conversion, so pass `clearEndogenes` when converting a pawn that already has one. Jawa xenotypes on this stack, re-measured 2026-08-19: `MandrakeJawa` (35 genes, the owner's hand-built set and the only active one) and `RimMandrakeJawa` (24, generator output), both from `mandrake.starwarsraces`. ⚠️ `BTD_Jawa`, `OuterRim_Jawa` and `guy762_xenotype_jawa` are ALL GONE — the donor mods were switched off. Both live ones are labelled "Jawa", so read the defName, never the label |

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

# The 15 map tools — added 2026-08-19

Everything below is proven live. Silent-failure catalogue: `silent-failures.md`.

```
TERRAIN   get_terrain_layers · set_terrain_layer · set_substructure_batch
GRIDS     set_fog · set_weather_buildup · set_deep_resource · set_gas
BUILD     build_batch · build_check · designate_batch
PREFAB    prefab_capture · prefab_place · prefab_list
ZONES     map_zones (listZones/createZone/paintZone/deleteZone/listAreas/paintArea)
COMMIT    map_commit            ⬅ the map twin of world_commit
```

## 🔑 1.6 has FIVE terrain layers, not two

**top · under · FOUNDATION · TEMP · plus a colour grid.** The original `set_terrain` /
`get_terrain_batch` only ever reach `top`, so they cannot tell a floor laid over
substructure from bare ground. `get_terrain_layers` reads all five.

**SUBSTRUCTURE IS NOT A GRID.** It is a foundation-layer `TerrainDef`
(`TerrainDefOf.Substructure`, `IsSubstructure => HasTag("Substructure")`) in
`TerrainGrid.foundationGrid`. `Map.substructureGrid` is **only an overlay drawer** — its
sole state-changing method is `MarkDirty()`. Odyssey-gated.
⚠️ `SetFoundation` **errors** if the cell has under-terrain; `set_substructure_batch`
checks first and returns a per-cell reason instead of red log lines.

## `map_commit` — what it actually does

```csharp
map.regionAndRoomUpdater.Enabled = true;
map.regionAndRoomUpdater.RebuildAllRegionsAndRooms();   // also resets the temp/vacuum cache
map.pathing.RecalculateAllPerceivedPathCosts();
map.reachability.ClearCache();
map.powerNetManager.UpdatePowerNetsAndConnections_First();   // Notify_* only QUEUE; this flushes
map.mapDrawer.WholeMapChanged(Buildings|Things|Terrain|Roofs|GroundGlow|Snow|PowerGrid);
```

✅ **Everything else is automatic.** `Thing.SpawnSetup` already handles listerThings,
listerBuildings, thingGrid, edificeGrid, coverGrid, linkGrid, glowGrid, fertilityGrid,
attackTargetsCache, snow/sand, exitMapGrid, mapTemperature, gasGrid, zoneManager, per-cell
mesh dirtying and region dirtying.

For speed on a big batch, wrap the spawn loop in `regionAndRoomUpdater.Enabled = false` and
`using (map.pathing.DisableIncrementalScope())`.

## ⭐ Prefabs — copy and paste regions of map

Base 1.6 and ungated. `prefab_capture` takes a `CellRect` into a named capture;
`prefab_place` stamps it back. **63 of 63 terrain cells and all 34 things replayed
identically** in the proving run.

* 🔴 **`CreatePrefab` never sets `size`** — vanilla's own capture is unusable until you
  fill it in. `prefab_capture` does.
* 🔑 **`SpawnPrefab` CENTRES on `pos`** — min corner is `pos - ((size-1)/2)`.
* ⚠️ Captures are **session-only** by design: not in `DefDatabase`, gone on restart.
* 📌 `copyAllThings=false` still captures natural rock — the flag governs loose items and
  filth, not edifices.

## Building

`build_batch` takes `'ThingDef:x,z[,rot]'` ops separated by `;`. It is the god-mode path
`Designator_Build` itself takes: `MakeThing` → `SetFactionDirect` → `GenSpawn.Spawn`.

* 🔴 **Set HitPoints AFTER the spawn** — `MakeThing` calls `PostMake`, which randomises
  them from `startingHpRange`. Proven: asked 175, got 175/300 on every wall.
* 🔴 **WALLS CREATE NO ROOF.** Confirmed by building a room and finding it open sky.
* ⛔ **Do not drive `Designator_Build`** — `placingRot` is protected and it reads
  `Find.CurrentMap` plus tutor/sound/fleck state.
* `build_check` returns the engine's own `AcceptanceReport`, so a refusal explains itself.
* `designate_batch` queries before adding — `AddDesignation` logs a red error on double-add.

## Fog defeats screenshots

A slab written correctly in unvisited territory **photographs as nothing**. Run
`set_fog action=unfogAll` before any map capture. This cost one wasted screenshot cycle.

## `connect_cells` — routing A to B

Copies vanilla's own conduit router (`GenStep_Power`): a **4-connected flood fill over
placeability**, not a pathfinder, so the route is placeable end-to-end by construction.

| in the way | `strict` | `mine` | `bridge` |
|---|---|---|---|
| wall / rock | refuses, names the cells | **straight through** | — |
| shallow water | **routes around** | — | **bridges through** |
| **deep water** | around | around | **will not bridge — impossible** |

🔴 `WaterDeep` has **no terrain affordances** and is not Bridgeable. No mode forces it.
🔴 A `PathFinder` route is **8-connected** and must be densified to cardinal steps, or the
conduit net breaks at every diagonal — it looks connected and is not.
🔴 **Maps are not square.** One quicktest was 100×400. `map_commit` reports `mapSize`.
✅ **Atomic** — the whole route is validated before anything is placed.
