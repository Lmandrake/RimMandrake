# INHABITED_STOCK_ONTO_MAP_AND_FATE_1

A FEATURE, not a bug fix, and it was filed as one line during a sweep of a
bigger bug list. The brief is the mod's own doc comments, which a previous
pass had already corrected to state the truth about themselves:

* `InhabitedPlaceDef.cs`, on `InhabitedFate`: *"DECLARED, NOT WIRED.
  `InhabitedPlaceDef.fate` is the only field of this type and no code in this
  mod reads it, so every value below is at present a statement of intent that
  changes nothing in play."*
* `InhabitedPlaceDef.cs`, on `larder`: *"NOTHING spawns those things onto a
  generated map and nothing collects them back at teardown, so the larder is
  BOOKKEEPING, not scenery: it cannot be seen, stolen or burned. 'Burn the
  granary and they leave, with no new code' describes the intended design,
  not the build."*

## spec

Three outcomes, decided here because the item filed none.

**1. The goods exist as real Things on a map.** A new GenStep drops the whole
`InhabitedStock` holder onto every generated map at the place's tile, and
empties the holder in doing so. The bar is *findable and stealable*, not
*beautifully laid out*.

**2. What is left comes back.** At teardown the same holder takes back
whatever survived, so `WorldObject_Inhabited.stock` afterwards is the place's
REMAINING goods rather than its authored ones. Nothing records the loss; the
container is the record, exactly as the roster already works.

**3. A fate fires, at minimum `FleeIfThreatened`.** The headline case in the
doc is literal — burn the granary and they go — so burning the granary is a
literal test, not a metaphor for a generic hostility check.

### What I decided, and the two things I rejected

**I rejected making the cast physically walk off the map.** It is the obvious
build and it destroys the roster. `Pawn.ExitMap` despawns a non-player pawn
with no caravan and calls `Find.WorldPawns.PassToWorld`; `WorldPawnGC` then
collects it, which is precisely the failure `WorldObject_Inhabited`'s own class
comment (divergence 1) exists to prevent, and which
`INHABITED_ROSTER_LIFECYCLE_SWEEP_1` has already been bitten by once through
`LordJob.ShouldRemovePawn`. So the CAUSE is detected live during the visit
(`MapComponent_InhabitedWatch`, with a message so the player knows) and the
CONSEQUENCE lands at teardown (`InhabitedFateWorker.Apply`, roster to
`DisplacedPool` with `DisplacedReason.Fled`). The place is empty next time you
come. A visible walk-off needs a prefix on `Pawn.ExitMap` to intercept a
resident before `PassToWorld`; that is a new Harmony target to prove and it is
deferred, not forgotten — named in `InhabitedFateWorker`'s class comment.

**I rejected an authored "granary" marker in the district template.** I
checked the format first: a compiled rimplace plan
(`src/RimMandrake/StructureInjections/Source/RimplacePlan.cs`) is a footprint
plus flat lists of `Foundation`/`Terrain`/`Things`/`Roof`/`Paint` cells. There
is no role, tag or marker vocabulary in it at all, so there is nothing a
GenStep could read and adding one is a change to the template format and its
offline compiler — a different item. The anchor is derived instead:
`GenStep_ComposeSettlementDistrict` now publishes the composed district's
map-space rect as a `MapGenerator` var, and the stock step prefers a roofed
standable cell inside it, which in practice is inside one of the district's
own buildings.

**`Squatted` I left alone.** The task suggested `InhabitedState` might record a
fired fate's consequence, and it does — `Apply` writes `Looted` when the larder
is empty and `Abandoned` when it is not, both of which
`GetInspectString` already draws differently. `Squatted` stays unwritten
because nothing in this mod moves a second party into an emptied place;
inventing a trigger would have been a guess. Said so in the enum's own comment.

## verify

* **Compiles.** `dotnet build Inhabited.csproj -c Release --no-incremental`:
  0 warnings, 0 errors, DLL newer than every source touched.
* **XML well-formed**, all five files parsed.
* **Every engine call read before use, not assumed** — via RimSage against
  1.6 source: `ThingOwner.TryDrop(Thing, IntVec3, Map, ThingPlaceMode, out
  Thing)` (`Verse/ThingOwner.cs:880`) and the fact that it returns the SURVIVING
  stack after a merge, not the one handed in; `ThingOwner.TryAdd`'s merge path
  using `TryAbsorbStack(respectStackLimit: true)` (`ThingOwner.cs:177`);
  `Map.FillComponents` instantiating every non-abstract `MapComponent` subclass
  with a `(Map)` ctor (`Verse/Map.cs:710`); `GravshipUtility.PlayerHasGravEngine(Map)`
  carrying its own `!ModsConfig.OdysseyActive` guard
  (`RimWorld/GravshipUtility.cs:177`); `CellFinder.TryFindRandomCellInsideWith`,
  `CellRect.RandomCell`/`CenterCell`/`Empty`/`CenteredOn`,
  `ListerThings.AllThings`, `MapPawns.FreeColonistsSpawnedCount`,
  `ThingDefOf.Fire`, `MessageTypeDefOf.NeutralEvent`. The
  `MapGenerator.SetVar`/`TryGetVar` channel between two GenSteps is the one
  `GenStep_ReserveGravshipArea` uses for `UsedRects`.
* **The three unrelated pre-existing selftest failures** (`selftest_one_path_seam`,
  `selftest_river_link_order`, `selftest_validate_patch`) are in the worldmap
  and xpath-validator domains and are untouched by this work.

### 🔴 OWED, and it is more than the usual "needs a live check"

**A live settlement visit cannot be run, and not because of anything in this
item.** Both routes that would execute `GenStep_InhabitedStock` are dead in the
current build set, and both blockers predate this work:

1. `WorldObject_InhabitedSettlement` is not a `MapParent`, so
   `Inhabited_SettlementMapGenerator` never runs at all —
   `INHABITED_SETTLEMENT_MAPPARENT_GAP_1`, filed and open.
2. **No `TileMutatorDef` anywhere in the build set names `Inhabited_Cast`.**
   Checked by grep across `src/` and `deployed/`: the four mutator files that
   exist (`StructureInjectionsSW`, `StructureInjectionsRUT`) name none of this
   mod's GenSteps. So the wilderness route the mod's class comment describes
   has no way in either. This is a second reachability gap, of the same shape
   as the first, and it is not filed anywhere — noting it here rather than
   opening an item from a build seat.

So the *mechanism* is complete and the *GenStep wiring* (order 910, the
district-rect var, the mapgen list entry) has never executed and cannot until
one of those closes. What CAN be exercised offline-of-mapgen, and what the
five new debug actions exist for, is every method the GenStep and the teardown
patch call (the sixth line is the existing action, now assigning an archetype):

```
RimMandrake.Inhabited: Create place at current tile   (now assigns an archetype)
RimMandrake.Inhabited: Set place archetype
RimMandrake.Inhabited: Stock: dump onto this map
RimMandrake.Inhabited: Stock: collect from this map
RimMandrake.Inhabited: Fate: test the cause now
RimMandrake.Inhabited: Fate: fire the consequence now
```

The live check owed is a quicktest map: create a place, dump, confirm the
goods are on the ground and haulable, burn or carry off most of them, "test
the cause" and confirm it names `InhabitedFateBurned`/`InhabitedFateRobbed`,
then collect and confirm the holder holds only what survived. Not run — this
pass is compile-clean only, and the repo had other live work potentially in
flight.

## criteria

My own bar, stated plainly:

1. Larder goods reach a generated map as real `Thing`s inside the place's own
   district, and can be seen, hauled, stolen and burned. **Met in code.**
2. Whatever is still there at departure returns to `InhabitedStock`, and what
   the player took does not. **Met in code.**
3. `FleeIfThreatened` fires off a real cause including burning the stores, and
   has a consequence the player can see on the world map next visit. **Met in
   code.**
4. `FleeOnArrival` and `Transient` wired if cheap once the scaffold exists.
   **Met** — one line each, since the scaffold made them one line each.
5. It is reachable in play. **NOT MET, and not by this item's hand.** See
   OWED above.

Criterion 5 is why this item stays `doing`. Every line of the mechanism is
built, but "a feature nothing can reach" is the exact pattern this project
spent today catching, and calling it closed would be that pattern with better
paperwork.

---

## Built 2026-09-03 (FOUNDRY)

### New

* **`Source/GenStep_InhabitedStock.cs`** — order 910, after `Inhabited_Cast`
  (900) and that ordering is load-bearing: `InstantiateCast` is what fills the
  holder and the cast step is what calls it, so dropping first would empty an
  empty holder. Anchors on the composed district rect, preferring a roofed
  standable cell; falls back to the district centre, then to the same
  `map.Center` worksite anchor `GenStep_InhabitedCast` uses, so a place with no
  composed district still puts its people and its goods in the same place.
* **`Source/InhabitedFateWorker.cs`** — `DetectCause` (pure, returns a
  translation key or null) and `Apply` (at teardown; may destroy the world
  object in the `Transient` case, which is why it is the last statement in the
  recall). Four menaces for `FleeIfThreatened`, cheapest first: fire inside the
  stock area; the place's faction now hostile; a resident dead or downed while
  the player has pawns on the map; more than half the dropped stock gone.
  `FleeOnArrival` is `GravshipUtility.PlayerHasGravEngine(map)`. `Transient`
  fires on being visited at all and destroys the place, whose existing
  `Destroy()` already absorbs the roster into the pool.
* **`Source/MapComponent_InhabitedWatch.cs`** — every 250 ticks, on any map
  with a place on its tile, until a cause fires once. A MapComponent rather
  than a Harmony hook on some damage or destruction method: `FillComponents`
  needs no def, no patch and no registration, and cannot go stale against a
  renamed target.
* **`Defs/PlaceDefs/Places_Inhabited.xml`** — `RM_InhabitedPlace_Scrapyard`,
  **the first `InhabitedPlaceDef` that has ever existed.** There were zero, and
  no code anywhere assigned `WorldObject_Inhabited.placeDef`, so the larder,
  the trade table and the fate were all running on C# defaults with nothing in
  them. A stock feature with no archetype to stock is unreachable by
  construction, so one ships here; the full six-to-eight archetype table is not
  this item's to author. `RM_` prefix per `design/NAMING_SCHEME_PLAN.md` (new
  defNames take the tier grammar; the `Inhabited_*` siblings migrate under
  NAMING_SCHEME_EXECUTION_1, not ahead of it), and the same for the new
  `RM_InhabitedStock` GenStepDef.

### Changed

* **`InhabitedStock.cs`** — `DumpOnto` / `CollectFrom` / `CountOnMap` /
  `IsPlaceGoods` / `TotalStackCount`, and the class comment rewritten from
  "🔴 THE CONTENTS NEVER REACH A MAP YET" to what it now does.
  * The ledger records the **resulting** stack's `thingIDNumber`, not the input's:
    `GenDrop.TryDropSpawn` merges into an existing stack where it can, which
    destroys the thing handed in — recording the input's ID would have written
    down an ID present on no map, and the recall would have found nothing.
  * `IsPlaceGoods` accepts an item that is either **in the ledger anywhere on
    the map** or **lying in the stock area**, because the ledger is a floor and
    never a census (a split or merged stack has an ID nobody wrote down). The
    area half means a player who leaves goods at the granary has given them
    away — which costs nothing, since the map is destroyed on departure either
    way.
  * **Corpses are excluded and that is load-bearing.** A `Corpse` is
    `ThingCategory.Item` and passes every other test, and it HOLDS ITS PAWN:
    absorbing one would deep-scribe a dead resident into the world object
    forever, which is exactly the record "the absence is the memory" says must
    not exist.
  * `Fill` now splits at the def's `stackLimit`. Writing `stackCount` straight
    from the authored count was invisible while the holder was a ledger and
    stops being invisible the moment the contents hit a map — 200 steel is
    nearly three times the def's own limit of 75.
* **`WorldObject_Inhabited.cs`** — `stockOnTheGround`, `stockSpot`,
  `stockRadius`, `stockSpawnedCount`, `threatened`, `threatReason`, all
  scribed; `StockArea`; and `InstantiateCast` restructured.
  * **The stock fill used to sit BELOW the "no cast" early return.** A place
    with a larder and no `InhabitedCastDef` — which is every place in this
    build set, since no cast defs are authored anywhere — therefore got no
    goods either. Nothing about a granary depends on somebody living in it.
    Now `FillStock()` runs first.
  * `FillStock` gates the trade table on `HasTrader`, which is
    `InhabitedPlaceDef.stock`'s own documented meaning ("trade goods held for
    a cast that contains a dealer") finally enforced. It mattered more once the
    goods land on the ground where the player can take them.
* **`Patch_MapRemoval.cs`** — collects the stock in the same prefix and for the
  same reason the pawns are collected there (one step later `MapDeiniter` has
  begun), then calls `InhabitedFateWorker.Apply` **last**, because the fate
  empties the roster the recall has just refilled and judges Looted-vs-Abandoned
  on the stock it has just collected.
* **`GenStep_ComposeSettlementDistrict.cs`** — publishes the district rect as
  a `MapGenerator` var, and assigns `settlement.placeDef` from the manifest.
* **`SettlementManifestDef.cs`** — new `place` field, **the only route by which
  a settlement ever gets an `InhabitedPlaceDef`**; and
  `SettlementManifestDefs_TheClaimJump.xml` names the scrapyard archetype.
* **`InhabitedPlaceDef.cs`** — the two doc comments this item was filed off
  now state what is true; `InhabitedState` gained a comment naming its three
  writers and saying plainly that `Squatted` has none.
* **`DebugActions_Inhabited.cs`** — the actions listed under OWED.

### Not done, deliberately

* **Visible walk-off.** Needs a `Pawn.ExitMap` prefix; reason in the spec.
* **A marked storage room in the template format.** Needs a marker layer in
  rimplace and its offline compiler.
* **`Squatted`.** No trigger exists to invent one from.
* **Reachability.** Both gaps are pre-existing and named under OWED.
