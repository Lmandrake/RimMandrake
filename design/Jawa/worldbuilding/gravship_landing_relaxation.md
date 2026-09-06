# GRAVSHIP_LANDING_CRUSH_1 — relaxing gravship landing and launch

Research + design pass, 2026-09-05. **Nothing built, nothing deployed.** Awaiting the
owner's approval of the approach.

Owner's requirement, verbatim (2026-09-05):

> "We absolutely need mods that let the ship just plop down on top of small barriers and
> blockages or a ship that size will never find clear landing. Major mountains should be a
> no no as is deep water or lava but otherwise it should just crush stuff and be done with
> it. Also we should let it take off even if the thrusters are blocked. The grav engine
> just goes straight up before the thrusters are even needed."

---

## 1. The gates

### 1.1 Landing — one method, and it is the whole gate

`RimWorld.Designator_MoveGravship.IsValidCell(IntVec3 cell, Map map)` —
`Source/RimWorld/Designator_MoveGravship.cs:113-158`, `private static`, returns
`AcceptanceReport`. It is called per-cell over the ship's footprint by
`ValidGravshipLocation` (`:76`), which is called by `CanDesignateCell` (`:71`) and by
`SelectedUpdate` (`:204`) for the red/white ghost.

It is the **sole** landing gate. The "Confirm landing" button
(`Source/Verse/WorldComponent_GravshipController.cs:570-583`) only checks
`landingMarker.Spawned`, and the marker is spawned solely by
`Designator_MoveGravship.DesignateSingleCell`, which the `Designator` base class calls only
after `CanDesignateCell` accepted. There is no second validation at commit time.

Its refusals, in order:

| # | Condition | Message | Owner's ruling |
|---|---|---|---|
| 1 | `!cell.InBounds(map)` | `GravshipOutOfBounds` | KEEP |
| 2 | `!cell.InBounds(map, 1) \|\| cell.InNoBuildEdgeArea(map)` | `GravshipInNoBuildArea` | KEEP |
| 3 | cell inside any `map.landingBlockers` rect | `GravshipInBlockedArea` | KEEP (quest/scenario no-land zones) |
| 4 | `cell.Roofed(map)` — **ANY** roof | `GravshipBlockedByRoof` | **RELAX** → refuse only `RoofDef.isThickRoof` (= overhead mountain) |
| 5 | `cell.Fogged(map)` | `GravshipBlockedByFog` | KEEP |
| 6 | any `Thing` with `def.preventGravshipLandingOn`, **or** a `Building` whose `def.building.canLandGravshipOn` is false | `GravshipBlockedBy(thing)` | **RELAX** → this is the whole complaint |
| 6b | a `Pawn` that is `RaceProps.Humanlike` **or** hostile to the player | `GravshipBlockedBy(pawn)` | RELAX for hostiles; keep for player humanlikes |
| 7 | `!GenConstruct.CanBuildOnTerrain(TerrainDefOf.Substructure, cell, map, Rot4.North)` | `GravshipBlockedByTerrain` | **KEEP — already exactly right** |

**Gate 7 already implements two of the three hard refusals.** `Substructure`
(`Defs/Odyssey/TerrainDefs/Terrain_Foundation.xml:5`) declares
`<terrainAffordanceNeeded>Walkable</terrainAffordanceNeeded>`. Deep water, ocean and lava do
not carry the `Walkable` affordance, so `GenConstruct.CanBuildOnTerrain`
(`Source/RimWorld/GenConstruct.cs:207`) already refuses them. **Do not touch gate 7.**

**Gate 4 is the mountain rule, wrongly generalised.** `RoofDef`
(`Source/Verse/RoofDef.cs:5-7`) has both `isNatural` and `isThickRoof`. Vanilla refuses on
*any* roof, so a constructed shack roof or a thin rock outcrop refuses the same as an
overhead mountain. `isThickRoof` is the "major mountain" the owner means.

**Gate 6 is why nothing is ever landable.** `BuildingProperties.canLandGravshipOn` defaults
to **false**, and across all of Core + the DLCs only ~25 defs opt in (Ancient ruins rubble,
a handful of Buildings_Misc / _Security / _Power entries). Natural rock is a Building →
refuses. Every wall, every ruin, every piece of ancient junk → refuses. What *already*
passes: plants and trees (`thing.def.building == null` → `continue`), chunks, filth, items,
corpses, non-humanlike friendly animals. Only `Wastepack`
(`Data/Biotech/.../Items_Resource_Manufactured.xml:280`) sets `preventGravshipLandingOn`.

### 1.2 Launch — thrusters, one property

`RimWorld.Building_GravEngine.CanLaunch(CompPilotConsole)` —
`Source/RimWorld/Building_GravEngine.cs:299-327`. It has **no thruster-obstruction check of
its own**. The refusal is indirect:

```
Building_GravEngine.cs:318   if (MaxLaunchDistance <= 0) return "CannotLaunchNoThrusters";
Building_GravEngine.cs:105   MaxLaunchDistance => (int)this.GetStatValue(StatDefOf.GravshipRange);
```

`GravshipRange` is contributed by thrusters as a facility `statOffset`
(`Source/RimWorld/CompProperties_Facility.cs:78`), and a facility only contributes while it
is active — `CompAffectedByFacilities.cs:545` → `CompFacility.CanBeActive`.

`RimWorld.CompGravshipThruster` (`Source/RimWorld/CompGravshipThruster.cs`):

- `Blocked` (`:24-38`) is true when `blockedBy != null` **or** `blockedBySubstructure`
  **or** `outdoors == false`.
- `CanBeActive` (`:40-60`) early-returns false `if (Blocked)`, and finally returns
  `outdoors == true`.
- `CanLink()` (`:83-93`) returns false `if (Blocked)` — a blocked thruster does not even
  link to the engine.
- `IsBlocked(...)` static (`:120-149`) walks the thruster's exclusion zone and sets
  `blockedBy` on the first `Thing` with `def.blockWind` that is not a `Plant`, or
  `blockedBySubstructure` if any exclusion cell has substructure foundation.
- `IsOutdoors(...)` static (`:151-167`) — false if any cell along the exhaust edge is in a
  room that does not use outdoor temperature (i.e. someone roofed the thruster bay).

So: block every thruster → range 0 → `CannotLaunchNoThrusters`. Nothing else refuses launch
for obstruction.

*(The same static `IsBlocked` also drives `PlaceWorker_GravshipThruster`
(`Source/RimWorld/PlaceWorker_GravshipThruster.cs:23`) — the build-time ghost. Leave that
alone so the build warning stays honest.)*

---

## 2. The crush path already exists — and it is total

🔑 **The engine already destroys everything under the ship's footprint.** No new destruction
code is needed. The validator is simply far more conservative than the placement code that
follows it.

```
WorldComponent_GravshipController.cs:531  GravshipPlacementUtility.PlaceGravshipInMap(...)
GravshipPlacementUtility.cs:20            → SpawnFoundations(gravship, map, root)
GravshipPlacementUtility.cs:48            →   SpawnTerrain(map, root, gravship.Foundations, clear: true)
GravshipPlacementUtility.cs:204           →     ClearThingsAt(cell, map, ClearMode.All)
GravshipPlacementUtility.cs:327           →       thing.Destroy()   // every destroyable thing
```

`ClearMode` (`GravshipPlacementUtility.cs:10-16`) is a four-value ladder already used
elsewhere by map generation: `All`, `AllButNonTreePlants` (used by
`ClearAreaForGravship`, `:228`), `BlockingBuildingsOnly` (`GenStep_GravshipMarker.cs:22`),
`NaturalRockOnly` (`GenStep_ReserveGravshipArea.cs:57`).

`ClearArea` (`:233-275`) additionally:
- replaces impassable/dangerous terrain via `GetReplacementTerrain` (`:296-312`), which
  honours `TerrainDef.gravshipReplacementTerrain`;
- **removes the roof** — `ShouldRemoveRoof` (`:278-294`) returns true for every mode except
  `NaturalRockOnly`;
- unfogs and de-pollutes.

**The one real gap:** the player-driven landing path calls `SpawnTerrain(clear: true)`,
which clears *things* but never touches `map.roofGrid`. Destroy a rock wall under a thin
rock roof and RimWorld's roof-collapse checker drops rock on the ship you just landed. So
relaxing gate 4 requires a matching roof clear — which is one call to the engine's own
`ClearArea(..., ClearMode.All)`.

---

## 3. Existing mod

**Yes — "Land On Anything", Steam Workshop `3545384484`, by Nepenthe.**
<https://steamcommunity.com/sharedfiles/filedetails/?id=3545384484> · updated 2025-09-29 ·
declares RimWorld 1.6 · requires Odyssey. **NOT currently installed** in the owner's set.

It covers **both halves**:

- **Landing** — "land on top of whatever you want. Walls? Roofs? Buildings? Hostiles?" By
  default things on the gravship take up to 50% max-health damage on landing; adjustable, or
  removable entirely.
- **Launch** — "unblock-able engines … eliminates the pain of not being able to launch
  because your idiot colonists built a roof over your enclosed thruster zone."
- Has mod settings: choose what you can and cannot land on, optionally clear everything
  within two tiles of the ship, adjust or remove the damage.

⚠️ Feature list is the mod page's own claim; not verified in-game or against its IL.

Nothing in the owner's 595 installed mods does either half. The gravship mods he already has
are adjacent but unrelated: `planetace.nondestructivegravlaunch` (stops the old-tile crater),
`qwertaii.SubstructureAnywhere` (substructure outside engine range),
`nep.enginesunlimited` (engine count cap), `RedMattis.BiggerGravship` (size/range sliders).
`Land Ship On Any Tile` (`3547652788`) removes the *world-tile* "occupied" refusal only —
a different gate (`TileFinder.IsValidTileForNewSettlement`, `Source/RimWorld/Planet/TileFinder.cs:65`)
and not what is being asked for.

**Recommendation: try Land On Anything first.** It is a subscribe, it has the settings the
owner would otherwise ask us to build, and it is somebody else's maintenance burden across
1.7. Build ours only if its defaults cannot be tuned to the ruling (in particular: keep deep
water and lava refused, and set landing damage to zero).

---

## 4. If we build it: the minimal patch

New mod `src/RimMandrake/GravshipLandingRelax/`, packageId `mandrake.rm.gravshiplandingrelax`,
namespace `RimMandrake.GravshipLandingRelax`, prefix `RM_`. Tier is **RimMandrake** — this is
a general RimWorld fix, not campaign content. No new defs, no saved state, no ThingComp.

No existing mod of ours is the right home: `GravshipAstronautFix` is textures-only with no
assembly, `MandrakePatches` is XML-only, and `RimUtinni/ShipMemory` is the Anomaly
memory-core mod despite the name. Three Harmony patches, all postfix/prefix — **no
transpilers**.

### Patch 1 — landing validator (postfix, widen)

```
target: AccessTools.Method(typeof(Designator_MoveGravship), "IsValidCell")   // private static
kind:   Postfix
sig:    static void Postfix(IntVec3 cell, Map map, ref AcceptanceReport __result)
```

Vanilla returns on the *first* failing condition, so the postfix cannot learn which one
fired. It must re-derive the hard refusals — six cheap checks, and doing so makes the patch
independent of vanilla's ordering:

```
if (__result.Accepted) return;
if (!cell.InBounds(map)) return;                                    // gate 1
if (!cell.InBounds(map, 1) || cell.InNoBuildEdgeArea(map)) return;  // gate 2
if (map.landingBlockers != null && any rect contains cell) return;  // gate 3
if (cell.Fogged(map)) return;                                       // gate 5
var roof = map.roofGrid.RoofAt(cell);
if (roof != null && roof.isThickRoof) return;                       // gate 4, NARROWED
if (!GenConstruct.CanBuildOnTerrain(TerrainDefOf.Substructure, cell, map, Rot4.North))
    return;                                                         // gate 7, untouched
if (setting_protectColonists)
    foreach (Thing t in cell.GetThingList(map))
        if (t is Pawn p && p.RaceProps.Humanlike && p.Faction == Faction.OfPlayer) return;
__result = true;                                                    // everything else: crush it
```

This is the whole landing change. It keeps all three of the owner's hard refusals — thick
roof (major mountain), and deep water / lava via the untouched terrain affordance — and it
widens nothing else.

### Patch 2 — clear the roof so the crush is survivable (prefix, reuse engine code)

```
target: GravshipPlacementUtility.PlaceGravshipInMap(Gravship, IntVec3, Map, out List<Thing>)
kind:   Prefix, [HarmonyPriority(Priority.First)]
body:   GravshipPlacementUtility.ClearArea(map, root, new HashSet<IntVec3>(gravship.Foundations.Keys),
                                           GravshipPlacementUtility.ClearMode.All);
```

That is one call to the engine's own public method. We write no destruction logic. It clears
things, clears the roof (`ShouldRemoveRoof` returns true for `ClearMode.All`), replaces
impassable terrain and unfogs — before any gravship thing is spawned, so nothing of ours is
at risk. Consider expanding the cell set with
`GravshipPlacementUtility.GetCellsAdjacentToSubstructure(gravship.OccupiedRects, 1)` so the
ship is not born wedged against a wall.

### Patch 3 — thrusters (postfix, two one-liners)

```
target: CompGravshipThruster.get_Blocked      Postfix: __result = false;
target: CompGravshipThruster.IsOutdoors       Postfix: __result = true;   // optional, same setting
```

`Blocked` is the single choke point: it gates `CanBeActive` and `CanLink()`, so forcing it
false relinks the thruster and restores its `GravshipRange` statOffset, and
`Building_GravEngine.CanLaunch`'s `MaxLaunchDistance <= 0` no longer fires. `IsOutdoors`
covers the roofed-thruster-bay case, which the owner's word "blocked" also reaches; ship
both behind one setting.

⛔ **Do not patch `Building_GravEngine.CanLaunch` directly.** Forcing it to accept does not
restore range, so the ship would launch with range 0 and no reachable destination tile.

### Settings (all default ON except the last)

`relaxLanding` · `crushRoofs` · `unblockThrusters` · `protectPlayerColonists`
· `confirmWhenCrushingPlayerBuildings`

---

## 5. Risk

- **Duplicate patching.** "Land On Anything" patches this exact area. If the owner installs
  it, do not also ship ours — two postfixes on `get_Blocked` are harmless, but two different
  landing validators are not worth debugging.
- **Unverified against the 595 stack.** The mod census read About.xml text, not IL. Some
  installed assembly could already patch `Designator_MoveGravship.IsValidCell`.
- **Private-method target.** `IsValidCell` is private static. `AccessTools.Method` finds it
  today; a 1.7 rename makes it null. Guard the `Harmony.Patch` call and `Log.Error` with the
  method name if it resolves null, so it fails loudly rather than silently.
- **Save compatibility: none at risk.** No defs, no `ExposeData`, no comps. Uninstalling
  leaves nothing behind. The only durable effect is whatever was destroyed — and a ship
  parked where vanilla would not have allowed it, which is harmless because validation only
  runs at landing time.
- **Irreversible crush.** The clear is unconditional and covers player buildings. Landing on
  your own base eats it. Hence the confirmation setting.
- **Big holes.** Clearing thin rock roof over a whole footprint opens a large hole in a
  mountain — cosmetic, but it changes room temperature and can invite raids indoors.
- **Roof collapse timing.** If patch 2 is wrong about when the collapse checker runs, the
  first live test drops rock on the ship. Test on a quicktest map, not the campaign.

---

## 6. Least sure

1. **`GravshipRange` delivery.** I inferred the thruster contributes range as a
   `CompProperties_Facility.statOffset` gated by `CanBeActive`, from
   `CompProperties_Facility.cs:78` and `CompAffectedByFacilities.cs:545`. I did not read the
   StatPart itself. If it arrives another way, patch 3 may not restore range.
2. **Whether patch 2 is needed at all.** `GravshipPlacementUtility.placingGravship` already
   suppresses room and temperature updates (`Room.cs:699`, `RoomTempTracker.cs:73`) during
   placement; there may be an existing suppression that makes roof collapse a non-issue.
3. **Land On Anything's actual behaviour** — whether it keeps deep water and lava refused by
   default, and whether landing damage really can be set to zero. Page claim only.
4. **Whether any installed assembly already patches these members.** Not checked at IL level.
