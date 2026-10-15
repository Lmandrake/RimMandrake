# Static per-game state audit — GSS, FlowWorks, Pyrelands, JawaBench (BENCH, 2026-10-14)

Lesson: `infrastructure/state/lessons/20261015T025544Z-BENCH-static-session-wide-table-keyed-by.md`.
Fix commit: `92ada47568`. Ratchet: `python3 src/RimMandrake/Utils/selftest_static_game_state.py` (54/54).

## Engine facts that decide every row (read from RimSage, not guessed)

- **A game reload never runs `MapComponent.MapRemoved`.** `MemoryUtility.ClearAllMapsAndWorld` only nulls every
  class field of each `Map` and clears `Find.Maps`. What does run is `Game.Dispose -> Map.Dispose`
  (from `GameDataSaveLoader` l.156 and `GenScene` l.19): it disposes `IDisposable` map components and
  `pathFinder`. A cleanup hung on `MapRemoved` therefore does NOT fire on reload.
- **`Thing.GetHashCode` is `thingIDNumber`, but `Equals` is reference.** A `HashSet<Pawn>`/`Dictionary<Thing,…>`
  never false-hits across a reload (it only leaks). An `int`-keyed table (thingIDNumber) DOES false-hit: a fixture
  reload re-issues the same ids at the same tick.
- `Map` overrides neither, so `Map`-keyed tables are reference-keyed: no false hit, only a leak unless pruned.

## Method

Scanned every `static` field (not method, const or property) in `src/RimMandrake/GimmeSomeSlack`,
`src/RimMandrake/FlowWorks`, `src/RimMandrake/Pyrelands`, `src/RimUtinni/PyrelandsMechanics` and
`src/RimMandrake/bridgetools/JawaBench.BridgeTools` (SelfTest/obj/bin excluded). Settings, Def/Material/Texture
caches, Harmony handles, reflection handles and diagnostics counters were set aside as not per-game. Every field
whose type can hold per-game state (collection keyed by int/long/Thing/Pawn/Map/Ideo/tuple; a Map/Pawn/Thing/Game
reference; an int named `*Tick`) was READ and classified.

**MEASURED: 44 per-game static fields** found by the ratchet's scanner (it prints the count), plus 7
ConditionalWeakTable fields at HEAD (weak, reference-keyed, safe by construction; 2 of them are today's fixes) and
1 instance table already fixed today (`lastBurrowNudge`, 0afba7de51). 5 defects + 2 leaks fixed below.

## Defects (fixed in 92ada47568)

| file:line | field | holds | cleared on reload? | failure after a reload | fix | item |
|---|---|---|---|---|---|---|
| `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:645` | `lastReroute` `Dictionary<int,int>` | pawn id -> tick of last pit re-plan | no (only a 256-entry purge) | loading an EARLIER save makes `now - last` negative: every re-plan for that pawn id is refused until the clock passes the old tick, so a held pawn's stale path fails instead of re-routing to the ladder (the pit_escape Wait-forever class); a same-tick reload blocks up to 60 ticks | Game guard (`rerouteGame`) + `now < last` reads as expired | `PIT_REROUTE_FIX_TIME_TRAVEL_FORGIVEN` |
| `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:280` | `regionCache` `Dictionary<int,RegionEntry>` | pawn id -> trap region this tick | per tick only | a reload at the same tick with the pawn at the same cell returns the OLD map's region for that tick (held/trapped verdict from a dead map) | entry carries its `Map`; hit requires `ReferenceEquals(e.map, p.Map)` | same |
| `src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs:87` (old) | `lastTimeout` `Dictionary<int,int>` | pawn id -> tick of last burrow timeout | no | the burrow-nudge bug (0afba7de51) again on the timeout path: a timeout from the previous load refuses the first burrow of the reloaded fixture (same id, cooldown not elapsed) | moved to an instance table on `MapComponent_BurnLine` (`NoteBurrowTimeout`/`LastBurrowTimeout`) | `BURROW_TIMEOUT_FIX_DEJA_VU_CURED` |
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchArtboardTools.cs:84` (old) | `ArtboardPawnIds` `HashSet<int>` | ids of pawns artboard_stage spawned | no | **destructive**: after a reload a real player pawn that gets an old artboard pawn's id is exempt from the "clearRect holds player pawns" refusal and is destroyed by the clear | `ConditionalWeakTable<Pawn,object>` (by object, not id) | `ARTBOARD_PAWNS_HARDEN_IDS_ARE_NOT_PEOPLE` |
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs:65` | `Specimens` `Dictionary<int,Thing>` (+ `_specimenLost`, `SpecimensUnresolved`) | armed specimen Things | `EnsureEpoch` cleared histories but NOT specimens | after a reload the vitals stream reads the dead game's Thing objects (stale health, or a false `specimen lost`) for specimens alive in the new game — a confident wrong instrument reading | `EnsureEpoch` re-resolves the same ids in the new game and clears `_specimenLost` | `VITALS_SPECIMENS_FIX_GHOSTS_REHOMED` |

Leaks fixed in the same commit (no wrong behaviour, unbounded growth across reloads):
`RM_LiquidNet.toldAboutHoses` `HashSet<Map>` (never pruned) -> ConditionalWeakTable;
`RM_PitExposure.charityCache` `Dictionary<Ideo,…>` (per-tick cache, never pruned) -> cleared past 64 entries.

## Safe, with the reason (each is listed in the ratchet's REVIEWED table)

GSS: `CompAerialAnchor.aboardCacheFor/aboardCache` (rebuilt when the Gravship object changes);
`CompAerialAnchor.groundedMessageTick` (accepted: a launch on the exact reload tick loses one message);
`SectionLayer_RM_MessyCords.PrintedVariants` (keyed by strand variant). `PrintedStatic` (string key
`map.uniqueID:x,z`, probe-only) is overwritten by every section regenerate, and a reload regenerates all sections.

FlowWorks: `RM_PitPathing.grids/ladderGrids` (pruned vs `Find.Maps`), `entryCache` (key holds the Map ref, cleared
per tick); `RM_CliffMask.masks` (released by `PathFinderMapData.Dispose`, which reload runs); `RM_LiquidNet.states/
rotations/byMap` (pruned on miss); `RM_PitRooms.floodMap/sweepMap`, `RM_PitDepthDraw.cachedMap/Comp`,
`RM_Patch_SuperdeepShooting.cachedMap/Engine`, `RM_DigDiscovery.poolMap/poolTick` (reference caches);
`RM_CliffMask.notedPawn`, `RM_PitStepCost.current` (one-call hand-offs); `HoseRelay.NoFeeders`,
`RM_MapComponent_Hoses.NoJoints` (empty sentinels); `shadowPool`, `HoseCarry.Default` (not game state).
Weak tables: `RM_PocketGrid.grids`, `RM_PitRooms.regionSide`, `Building_LiquidPump.toldPourNeedsDump`.

Pyrelands: `FurnaceWarmthField.byMap` (Game guard `ownerGame` + dead-map prune); `PyrelandsAshField.lastMap/
lastComp` (reference cache); `FireEcologyHook.rolledFiresByMap` (weak, fixed 68049f4519);
`MapComponent_BurnLine.lastBurrowNudge` (instance, fixed 0afba7de51). PyrelandsMechanics: settings only.

JawaBench: `JawaBenchVitals.Critical` (caller-armed ids; a reload re-issuing them is what the caller means),
`Prev/_threats/...` (reset by `EnsureEpoch`); `JawaBenchAwareness.Open` (our own context ids);
`JawaBenchTpsSampler._game` (Game guard); GSS/FlowWorks playtest runs abort on map change.

## Not fixed, noted

- `CompAerialAnchor.groundedMessageTick`: cosmetic, accepted.
- A clean pattern for future code: key by object reference or guard with `if (owner != Current.Game) { clear; owner = Current.Game; }`.
  Never hang reload cleanup on `MapRemoved`.
