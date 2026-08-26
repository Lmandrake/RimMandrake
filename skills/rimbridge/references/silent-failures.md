# Silent failures — engine calls that report success and change nothing

**This is the most expensive knowledge in the project.** Every entry was found by a tool
returning `success: true` while the game did not move, and every one is a call the RimWorld
API offers you with no warning. Measured live 2026-08-19 unless noted.

📁 **Which file am I in?** This one catalogues **ENGINE APIs** that mislead you.
`traps.md` catalogues **BRIDGE, CLIENT, BUILD and WORKFLOW** mistakes. If the thing that
lied to you was a RimWorld method, you are in the right place.

🔎 **This is a lookup, not a read.** `grep -i -n "<the method you called>" silent-failures.md`
— every entry names the call.

⚡ **The two that catch most people, before you go further:** nothing you write to a WORLD
is visible until `jawa/world_commit`, and nothing bulk-written to a MAP is consistent until
`jawa/map_commit`. If your write "did nothing", check that first.

🔑 **The pattern to internalise:** RimWorld's setters are frequently *advisory*. They write
a field and leave the consequences to a refresh you must know to call, or they refuse
conditions you must know to check. **Nothing throws.** So the discipline is always the
same — **write, then read back the RAW field, then look at the screen.**

---

## 1. Writes that need a refresh you must call yourself

| call | what silently doesn't happen | the fix |
|---|---|---|
| **anything touching a world tile** | nothing redraws. RimWorld has **no per-tile visual invalidation except pollution** | `jawa/world_commit` — a whole `WorldDrawLayer` mesh regeneration |
| **anything touching the map in bulk** | regions, rooms, path costs, reachability and power nets stay stale | `jawa/map_commit` |
| **`story.Childhood` / `Adulthood`** | disabled work types, skill disables, aptitudes and meditation focus all keep the OLD backstory. The setters only null a cache | **four** calls: `Notify_DisabledWorkTypesChanged`, `skills.Notify_SkillDisablesChanged`, `skills.DirtyAptitudes`, `MeditationFocusTypeAvailabilityCache.ClearFor` |
| **appearance fields** (head, body, hair, beard, colours) | the pawn keeps drawing its old face for the session | `pawn.Drawer.renderer.SetAllGraphicsDirty()` |
| **`WorldFeature.name` / `drawCenter` / `drawAngle`** | the OLD label text keeps drawing | `Find.WorldFeatures.textsCreated = false` |
| **substructure / foundation paint** | the overlay does not update | `Map.substructureGrid.MarkDirty()` |
| **bulk building spawn** | power nets stay unbuilt — the `Notify_*` calls only QUEUE delayed actions | `map.powerNetManager.UpdatePowerNetsAndConnections_First()` |

🔴 **The backstory one is the sharpest.** **RimWorld's own debug tool runs only the LAST of
those four calls.** Proven: doing all four moved a pawn's disabled-skill set from
`['Cooking']` to `['Social']`. Doing one leaves a pawn whose story says one thing and whose
work types say another.

---

## 2. Calls that refuse, quietly

| call | refuses when | symptom |
|---|---|---|
| **`equipment.AddEquipment`** | a Primary already exists | `Log.Error` and **nothing happens**. Call `MakeRoomFor(eq)` first |
| **`WorldGrid.OverlayRoad` / `OverlayRiver`** | the def is lower priority than what's there (`road.priority`, `river.degradeThreshold`) | the old def stays; no error |
| **`OverlayRoad(from,to,null)`** | always — removal is unsupported | `Log.ErrorOnce`. Removal means editing `potentialRoads`/`potentialRivers` on **both** endpoints |
| **`ageTracker.DebugSetAge`** | asked to go **backwards** — it walks birthdays forward only | 54 → 8 leaves the pawn at 54 **and reports success** |
| **`Zone.AddCell`** | impassable terrain, an existing zone, a blocking edifice | a short zone. Measured: a 6×6 stockpile took **11 of 36 cells** |
| **social `ThoughtDef` without an `otherPawn`** | always | the memory is dropped |
| **`TryAddOrTransfer`** | inventory full / unstorable | returns the **count moved** — it is an `int`, not a `bool` |

---

## 2b. 🔴 Tools that report a path, a name or a count they did not honour

Measured 2026-08-24, live, on the campaign world.

| call | what it reported | what actually happened |
|---|---|---|
| 🔴 **`rimworld/save_game` with `saveName`** | `success: true`, `path: …\Saves\ASHKARR_worldwork_2026_08_24.rws`, **`exists: true`**, `sizeBytes: 21258468` | **No such file was ever created.** The game wrote its CURRENT save slot — `WORLDMAP_V1_original.rws` — **overwriting it**. The `exists`/`sizeBytes` pair was stat'd against a file that is not the one named |
| **`jawa/world_tile_get`** | 200 rows for a 400-id request | **caps at 200 tiles per call.** It DOES set `truncated`, and that field is the only thing between you and a half-empty census |
| **`jawa/world_links_get`** | fewer edges than the world holds | **same 200-tile cap.** A 1,498-tile sweep in 200-chunks returned **915 road edges**; the same sweep in 100-chunks returned **1,224** — the true number. It reports `count` and `requested`, and they differ |

🔑 **The lesson is one line: an id-list tool answers about the ids it CHOSE, not the ids you
sent.** Compare `requested` against `count`, or diff the ids you asked for against the ids
you got back, on every bulk read. A census assembled from truncated chunks is not short by
an obvious amount — it is short by exactly the amount you will not notice.

⚠️ **And `save_game`'s entry contradicts a note in the `rimbridge` skill** that said
`saveName` "IS honoured — measured 2026-08-20". Both measurements are real; something
between them changed, or the 2026-08-20 test was run in a state where the current slot
happened to match. **Treat the written path as a claim and stat the Saves folder yourself.**

## 3. Getters that lie

| getter | lies because | read instead |
|---|---|---|
| **`SkillRecord.Level`** | **adds aptitudes**, so read-back ≠ what you wrote | `GetLevel(false)` |
| **`Tile.HillinessLabel`, `MinTemperature`, `MaxTemperature`, `Biomes`** | lazily cached with **no reset method anywhere in RimWorld** — stale for the session after any write | the raw fields: `hilliness`, `temperature`, `PrimaryBiome` |
| **`SurfaceTile.Roads` / `Rivers`** | biome-FILTERED views — `allowRoads ? potentialRoads : null`. A water biome **hides** links without deleting them | `potentialRoads` / `potentialRivers` to validate; the views only to answer "what does the player see" |
| **`RaidStrategyDef.Worker.CanUseWith`** | meaningless while `parms.faction` is **null** — every strategy reports unusable | resolve an attacker first |
| **`IncidentWorker.CanFireNow`** | carries storyteller **pacing** that `TryExecute` never consults | `false` does **not** block a raid. Just fire it |

---

## 4. Constructors and factories that leave the object unusable

* 🔴 **`PrefabUtility.CreatePrefab` NEVER SETS `size`.** It comes back `(0,0)`, and `size`
  drives `GetRoot` and every bounds check — so `CanSpawnPrefab` refuses and `SpawnPrefab`
  cannot place. **A prefab captured with vanilla's own API is unusable until you set
  `size` yourself.**
* 🔴 **`ThingMaker.MakeThing` calls `PostMake`, which RANDOMISES HitPoints** from
  `def.startingHpRange`. Set HP **after** the spawn or it is silently overwritten.
* ⚠️ **`Frame.CompleteConstruction` and `Blueprint.TryReplaceWithSolidThing` hard-require a
  non-null worker `Pawn`** — NRE otherwise.

---

## 5. Rules that exist but are not enforced

* 🔴 **`GainTrait` checks NO conflicts, and `TraitSet` has NO trait cap.** Check
  `TraitDef.ConflictsWith` and `BackstoryDef.DisallowsTrait` yourself or a pawn ends up
  Kind *and* Psychopath.
* 🔴 **`WorldLandmarks.AddLandmark` never calls `LandmarkDef.IsValidTile`.** Measured on a
  settlement tile: verdict `False`, landmark added anyway. `IsValidTile` is the
  *generator's* rule, not a guard on the setter.
* 🔴 **A `Settlement` with a null faction is DESTROYED on load**, with only a warning.
* ⚠️ **Nothing validates appearance**: off-gender head types, gene-requiring heads and an
  adult body on a child all "work". Child body is forced only at load.
* ⚠️ **Non-player pawns ignore player forbid flags entirely** — `Thing.IsForbidden(faction)`
  returns false for any non-player faction. NPCs will eat the colony's meals.

---

## 6. Facts that cannot be checked offline

* 🔴 **`BiomeDef.allowRivers` / `allowRoads` are ABSENT from the def dump** — all 80 biomes
  report neither field — yet live they are `False` on `Ocean`, `IceSheet`, `GlacialPlain`.
* 🔴 **`WorldInfo.overallPopulation` and `landmarkDensity` are not scribed** — whatever you
  set, they revert on the next load.
* 📌 **`isThickRoof` lives under the `fields` sub-object** in the dump, not at top level.
  Easy to read as absent.
* 📌 **Never guess a defName.** 1,225 BackstoryDefs, 2,129 ThoughtDefs, 265 TraitDefs,
  336 TileMutatorDefs, 113 LandmarkDefs, 41 PawnRelationDefs. Four invented names failed
  in one session.
* 📌 **Only 9 of 41 `PawnRelationDef`s are storable.** `Sibling` and `Child` are **implied**
  — computed from the family graph, refused by `AddDirectRelation`.

---

## 7. Geometry that isn't what it looks like

* 🔴 **A contiguous tile-ID range is NOT a contiguous region on the globe.** Painting ids
  20000–23999 produced scattered rosettes; importing 0–21871 produced a hard diagonal seam.
  Use the neighbour graph, never id arithmetic.
* 🔴 **`SpawnPrefab` CENTRES on `pos`** — the min corner is `pos - ((size-1)/2)`.
* ⚠️ **Walls create no roof.** A room built from walls is open to the sky until roofed.

---

## 8. The house rule that falls out of all of this

> **Write → read back the RAW field → look at the screen.**
> Two instruments, always. `jawa/world_stats`' biome histogram and `jawa/pawn_get`'s
> `levelRaw` exist precisely so a write can be checked by something other than the writer.
> ⛔ **A tool returning `success: true` is not evidence.** It never was.

## `jawa/world_mutators_set` on any `GL_*` def — reports `added: 1`, changes nothing

Measured 2026-08-26 on six genuinely empty world tiles across six biome/hilliness
combinations. Every `GL_*` (Geological Landforms / Biome Transitions) write returned
`success: true, added: 1` and left the tile empty; a normal mutator landed on the same tile
in the same call. Nothing was logged, and no category conflict was possible.

⇒ **Not a bug.** Those defs are computed at display time and never enter
`Tile.mutatorsNullable`; the mod's `TileMutatorWorker_Landform` removes what `AddMutator`
appended. There is no way to author them and no reason to — landform assignment happens at
MAP generation from the tile's hilliness, topology and elevation.

🔑 The tell that they are live anyway: an in-game world-tile pane listing a feature that
`world_mutators_get` does not return for the same tile.

## `jawa/world_landmarks_set` — `isValidTile: false` on a landmark that was placed correctly

The validity array is evaluated AFTER the add, so it reports the landmark you just wrote.
`added >= 1` plus a read-back showing your def is the only trustworthy signal. Conversely a
landmark CAN be placed on a tile the engine considers invalid — the flag never blocks.

## `jawa/build_batch` — `placed` counts spawn attempts, not survivors

Measured 2026-08-26, full 582-mod list, one run of 8 calls / 81 ops.

```
reported: placed 4+1+1+3+3+1+3+65 = 81, failed: [] on every call
map held: 78
```

The three missing things were each **destroyed by a LATER op in the same run** whose multi-cell
footprint covered them — a `Table1x2c` (1×2) over a `DiningChair`, and a third `Shelf` over the
two before it. 🔴 **Both the destroying op and the destroyed op reported success.**

⇒ Diffing `placed` against `requested` — the obvious check, and the one a build-verification pass
will reach for — sees a perfect run. **The only honest success signal is a cell-by-cell read-back
with `rimworld/get_cells_info` after `jawa/map_commit`.**

⚠️ Also: `jawa/set_terrain_batch` and `jawa/set_roof_batch` take **`ops`** (`'<Def>:x,z,w,h'`
joined by `;`), NOT a `rect` parameter. Passing `rect` fails loudly — `success: false`,
*"ops is required"* — so this one is safe, but a compiler that emits `rect` loses every cell.

## Nothing reads a `Room` or a pawn's `StatDef` from outside the game

`rimworld/get_cell_info` has **no room object** (terrain, roof, fog, walkable, zone, areas,
things, designations — that is all), and no tool in the 246 reads room temperature or role.
`jawa/pawn_get` returns identity, apparel, equipment, hediffs, needs, skills, traits and xenotype
and **no stats**; `rimworld/select_pawn` is colonist-only and `Dialog_InfoCard` has no
parameterless constructor, so the UI route is shut too.
🔑 A question about `Room.Role`, room temperature or `ComfortableTemperatureRange` is
**UNMEASURED** today — not "probably fine".
