# YOBSHRIMP_DEFNAME_COLLISION_1

## Found

During DIRTY_CODE_REVIEW_STANDING_LOOP_1 full-file review of
`src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_NurseryJuveniles.xml`
(reviewing `RSW_YobshrimpJuv`'s `ParentName="RSW_Yobshrimp"`).

## Mechanism

Two SEPARATE `ThingDef`s, and two separate `PawnKindDef`s, are both defined with
`<defName>RSW_Yobshrimp</defName>` inside the same mod (`mandrake.rsw.swbestiary`):

- `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Swarm.xml`
  line 10 (`ThingDef ParentName="AnimalThingBase" Name="RSW_Yobshrimp"`, label
  "pale yobshrimp") and line 84 (`PawnKindDef ... Name="RSW_Yobshrimp_Kind"`,
  defName `RSW_Yobshrimp`) — the aquatic SeaBeasts swarm variant.
- `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Yobshrimp.xml` line 41
  (`ThingDef ParentName="AnimalThingBase" ADogSaidBody="LegsTail"`, NO `Name=`
  attribute, label "yobshrimp") and line 159 (`PawnKindDef`, defName
  `RSW_Yobshrimp`) — a land crustacean added later by the MLIE_FAUNA_ABSORPTION_1
  Wave C absorption pass, which evidently never checked for a collision with the
  earlier SeaBeasts merge.

`DefDatabase<T>.AddAllInMods()` (`Verse/DefDatabase.cs`, decompiled reference at
`/mnt/d/Luke/dev/reference/rimworld-decompiled/Verse/DefDatabase.cs` lines 20-40)
builds a per-mod `HashSet<string>` of defNames across ALL of that mod's own XML
files before adding any of them to the database. The second `ThingDef`/
`PawnKindDef` it enumerates with the colliding defName fails `hashSet.Add(...)`
and is **silently skipped entirely** — logged as `Mod <X> has multiple ThingDefs
named RSW_Yobshrimp. Skipping.`, never added to `DefDatabase<ThingDef>` at all
(not even the "add with a randomized suffix" path `DefDatabase<T>.Add` takes for
a same-defName collision from DIFFERENT mods). Enumeration order across a single
mod's own def files was not established this pass (would need a fresh def-dump
load-order check) — this item does not know which of the two currently survives,
only that exactly one of them is silently absent from every load right now.

## The ParentName inheritance itself is NOT ambiguous

`RSW_YobshrimpJuv`'s `ParentName="RSW_Yobshrimp"` resolves at the earlier
XML-inheritance stage, which matches on the `Name=` XML attribute, not
`defName`. Only `SeaBeasts_Swarm.xml`'s ThingDef carries `Name="RSW_Yobshrimp"` —
`RSW_Yobshrimp.xml`'s ThingDef has no `Name=` attribute at all, so it can never
be a `ParentName` target. `RSW_YobshrimpJuv` unambiguously inherits from the
aquatic SeaBeasts swarm variant. The live bug is purely the defName-registration
collision, not the inheritance.

## Evidence the split is intentional, not an accident to merge away

`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (generated,
**do-not-hand-edit** per this file's own DEPLOY/generator convention) already
carries TWO separate `<RSW_Yobshrimp>` wildAnimals entries in two different
biome blocks, under different comments:

```
line 271:  <RSW_Yobshrimp>0.3</RSW_Yobshrimp> <!-- pale yobshrimp - nursery, import -->
line 285:  <RSW_Yobshrimp>0.8</RSW_Yobshrimp> <!-- yobshrimp - arthropod-floor, import -->
```

The generator's own source data (`design/Jawa/fauna/` cast assignment) already
treats these as two distinct species that happen to share a defName — the
comments track the SeaBeasts nursery variant separately from the arthropod-floor
land variant. This is a naming collision to FIX, not a duplicate to delete.

## Other referencers found (repo-wide grep for bare `RSW_Yobshrimp`, excluding
`RSW_Yobshrimp_Kind`/`RSW_YobshrimpJuv`)

- `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml:10264` — a
  `BodyDef` named `RSW_Yobshrimp` ("clawed crustaceous animal"). BodyDef is a
  separate DefDatabase<T> from ThingDef/PawnKindDef, so this does NOT collide
  with either ThingDef — flagged only so the eventual rename keeps this BodyDef
  paired with whichever ThingDef it actually belongs to (reads as the land one,
  by description).
- `src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_MlieWaveC_Resources.xml:2659`
  — `<hatcherPawn>RSW_Yobshrimp</hatcherPawn>` (Wave C egg/hatcher item).
- `src/RimStarWars/SWBestiary/art/SeaBeasts/tools/sea_creatures.py:202` — art
  tooling keyed on `("RSW_Yobshrimp", "pale yobshrimp", ...)` — the SEA variant.
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` — also references
  `RSW_Yobshrimp`; not yet checked which variant it means.
- `design/Jawa/fauna/BiomeCast_Ashkarr.xml` — the design-side copy of the
  generated patch above (same generated-do-not-hand-edit status).

## Fix shape (not done this pass — needs the generator, not a hand-edit)

1. Rename ONE pair (recommend the Wave-C land ThingDef+PawnKindDef in
   `RSW_Yobshrimp.xml`, e.g. to `RSW_YobshrimpLand`) and its own BodyDef.
2. Update `RSW_MlieWaveC_Resources.xml`'s `hatcherPawn` and any other same-file
   cross-references to match.
3. Check `RUT_Miasma.xml`'s reference and correct it to whichever variant it
   actually means.
4. Update the generator's own source data (design/Jawa/fauna's cast-assignment
   input, whatever feeds `gen_cast_patch.py`) so the arthropod-floor wildAnimals
   entry emits the renamed defName, THEN regenerate
   `BiomeCast_Ashkarr.xml` via the real generator — never hand-edit either
   committed copy (design/ or src/RimUtinni/UtinniPatches/Patches/).
5. Confirm via a fresh def dump (not a grep) which ThingDef/PawnKindDef pair is
   CURRENTLY the one DefDatabase kept, since the other has been silently absent
   from every load until this rename lands — that pawn kind may need a
   from-scratch reintroduction to biomes/trade rather than "restoring" something
   that was ever actually reachable in play.

## Status

Filed, not started. `needs: offline`. Left DIRTY (not mark-cleaned) in
CODE_REVIEW_STATUS.json: `SeaBeasts_NurseryJuveniles.xml`,
`SeaBeasts_Swarm.xml`, `RSW_Yobshrimp.xml`.
