## spec
`src/Jawa/Inhabited/Source/WorldObject_Inhabited.cs`. Model on `RimWorld.Planet.Caravan`,
which is the settled shipped pattern for people held off-map — do not invent a
persistence layer. §3 of the design doc.
  `class WorldObject_Inhabited : WorldObject, IThingHolder, ILoadReferenceable`
  fields, all through `Scribe`:
     `ThingOwner<Pawn> roster`   🔴 ACTUAL `Pawn` OBJECTS, never records. Names,
                                skills, relationships, scars and memories then
                                survive with no serialisation of ours, and §3.2
                                ("sell a pawn and they stay") falls out free.
     `PlaceDef placeDef` · `CastDef castDef`   archetype + parameters
     `InhabitedState state`     enum: `Inhabited · Abandoned · Looted · Squatted`
     `ThingOwner<Thing> stock`  trade goods AND the larder (§2.1)
  `WorldObjectDef` in `Defs/WorldObjectDefs_Inhabited.xml` with
     `worldObjectClass="Inhabited.WorldObject_Inhabited"`, an expandingIcon, and
     `canHaveFaction=true` — faction is inherited from `WorldObject`.
  `GetInspectString()` renders the census line from §3.3:
     `12 souls . oil . will trade`  /  `9 souls fled . stock spoiling`
⛔ **No death record, no memorial, no ledger, no counter** (§3.1, owner verbatim:
*"eaten and forgotten"*). The roster simply IS the survivors; the absence is the
memory. Do not add a `died` int because it would be easy.

## verify
`dotnet build` clean; the def loads with 0 errors in a def-dump refresh
(`python3 src/RimMandrake/Utils/refresh.py`) and `WorldObjectDef` `Inhabited_*`
appears in the dump.

## criteria
a `WorldObject_Inhabited` spawned on the world map via the bridge draws its icon
and its inspect string on the planet view.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

built 2026-08-20, `f0a9f6c` — offline verify passes; **the def-dump half is owed
and needs a load.** Filed to CHECK as `INHABITED_DEFS_LOAD_CLEAN_1`.
🔴 **THREE DEVIATIONS FROM THE SPEC, and DECIDE should overrule any it dislikes:**
(a) **`InhabitedPlaceDef` / `InhabitedCastDef`, not the bare `PlaceDef` / `CastDef`
    the spec wrote.** A def type name IS the XML element name and is shared across
    the whole load order; this build set carries 577 mods. `PlaceDef` is a
    coin-flip collision and a collision here is silent.
(b) **`stock` is an `InhabitedStock` sub-holder, not a second `ThingOwner<Thing>`
    on the world object.** `IThingHolder.GetDirectlyHeldThings` returns exactly
    one owner, so a second one has to hang off a child holder. This is the shape
    `Caravan` uses for `pather` / `needs` / `beds` / `trader`.
(c) **the larder and the trade goods are one container**, as the spec asked, and
    the census line reads them: `12 souls . oil . will trade`.
⛔ No death record, no memorial, no ledger, no counter exists anywhere in the mod.
Checked by grep before commit.
