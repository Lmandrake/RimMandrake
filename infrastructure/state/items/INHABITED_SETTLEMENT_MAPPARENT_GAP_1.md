# INHABITED_SETTLEMENT_MAPPARENT_GAP_1

The single most severe finding from an opus code review of the whole
Inhabited mod (2026-09-02). Confirmed independently against real engine
source (RimSage) before writing this up — not trusted on the review's
prose alone.

## The finding

```csharp
public class WorldObject_Inhabited : WorldObject, IThingHolder, IThingHolderTickable
public class WorldObject_InhabitedSettlement : WorldObject_Inhabited
```

`WorldObject_InhabitedSettlement` derives from plain `WorldObject`, not
`MapParent`. Confirmed from `RimWorld/Planet/MapParent.cs` (read via
RimSage): `MapParent : WorldObject, IThingHolder` is the class that
actually owns `Map => Current.Game.FindMap(this)`,
`MapGeneratorDef => def.mapGenerator ?? MapGeneratorDefOf.Encounter`, and
offers the "enter" float menu option
(`CaravanArrivalAction_Enter.GetFloatMenuOptions` inside
`MapParent.GetFloatMenuOptions`). Every enterable vanilla world object —
`Settlement`, `Site`, `Camp`, `EscapeShip`, `PocketMapParent` — derives
from it.

`WorldObjects_InhabitedSettlement.xml` declares
`<mapGenerator>Inhabited_SettlementMapGenerator</mapGenerator>` and
`<canHaveMap>true</canHaveMap>` — both fields `WorldObjectDef` carries
generically, but which only mean anything to code that reads them through
`MapParent`. On a plain `WorldObject` they are inert: nobody reads
`def.mapGenerator`, nothing offers "enter", nothing calls
`GetOrGenerateMapUtility`/`MapGenerator.GenerateMap` for this object at
all. The XML's own comment ("so the compose-stub and cast steps run
without needing a tile mutator") states the false belief directly.

**Consequence, if this is really unreachable**: `GenStep_ComposeSettlementDistrict`,
`GateSearchHook`, `SettlementCasing`, and `Patch_SettlementDeparture` can
never fire for a settlement (as opposed to the wilderness/tile-mutator
path, which `WorldObject_Inhabited`'s own class comment describes and
which does NOT need `MapParent` — that route works through
`TileMutatorDef.extraGenSteps` instead). The entire
`MapGeneratorDefs_InhabitedSettlement.xml` generator may be dead code.

## Why this is filed for the owner, not fixed outright

1. **Save compatibility**: changing a scribed `WorldObject`'s base class
   is not a safe in-place edit — the reviewer flagged this explicitly, and
   it needs a fresh world, not a save migration, per this project's own
   standing rule that a save holding a dead type/name is a different
   failure class than a def-loader cross-reference.
2. **Scope of the real fix is a design call, not obviously one line**:
   does `WorldObject_Inhabited` itself move to `MapParent` (affecting the
   working wilderness/tile-mutator path too, which does NOT currently need
   it), or only `WorldObject_InhabitedSettlement`? What happens to
   existing behavior/comps that assume plain `WorldObject`?
3. **Consequence not yet live-confirmed**: this is the review's read of
   the engine source, not yet proven by watching a settlement actually
   fail to generate a district live. Worth a quick live check (spawn/place
   a settlement, try to enter it, see whether `Inhabited_SettlementMapGenerator`
   ever runs) before committing to the architecture change — cheap to
   falsify if wrong.

## spec

Determine (live, via the bridge, not more code reading) whether an
`InhabitedSettlement` world object can currently be entered at all and
whether its district/cast GenSteps ever run. If confirmed dead: decide
with the owner/BENCH whether `WorldObject_InhabitedSettlement` (or
`WorldObject_Inhabited` itself) should derive from `MapParent`, and what
that costs the working wilderness path and any existing saves.

## verify

Bridge test: place/find an `InhabitedSettlement` world object, attempt to
enter it (caravan arrival action), and check whether a map generates and
whether `Inhabited_ComposeSettlementDistrict`/`Inhabited_Cast` GenSteps run
(their own log lines, or a live `jawa/list_things` census of the resulting
map for district-placed structures/cast pawns).

## criteria

Live-confirmed either way. If confirmed dead: an owner-approved fix
lands, on a fresh world, with the wilderness path's continued behavior
verified unchanged.

## Live-confirmed DEAD (2026-09-04, FOUNDRY, minimal-list quicktest)

Placed a real `Inhabited_Settlement` WorldObjectDef (`jawa/world_objects_add`,
faction OutlanderCivil) at an empty world tile, committed, then called
`jawa/world_tile_map_generate` on that same tile with `suggestedMapParent:
Inhabited_Settlement`:

```
"success": false,
"message": "GetOrGenerateMap threw: InvalidCastException: Specified cast is not valid."
```

This is `GetOrGenerateMapUtility.GetOrGenerateMap` throwing directly on the object,
live, in the running engine — the same tool called the SAME way on a plain vanilla
`Settlement` at a different tile (control case, same session) generated a real
250x250 map with 71 pawns, no error. The InvalidCastException is exactly what the
review's engine-source read predicted: something in the generate path casts the
tile's WorldObject to `MapParent`, and `WorldObject_InhabitedSettlement` (derives
from plain `WorldObject`) fails that cast. Confirms the finding is not just a
correct reading of the class hierarchy but an actual live breakage — nothing else
in the engine compensates for the missing MapParent base.

Remaining blocker is exactly what "why filed for the owner" already said: this is
a save-compat-sensitive base-class change needing an owner/BENCH scope call
(`WorldObject_Inhabited` itself vs only the `Settlement` subclass), not a live-
confirmation gap anymore.
