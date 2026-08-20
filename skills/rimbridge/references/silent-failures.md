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
