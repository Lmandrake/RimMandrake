# StructureInjectionsRUT — validation walk
subject: src/RimUtinni/StructureInjectionsRUT  (packageId `mandrake.rut.injections`)
feature: structure-templates
deps: mandrake.rm.injections (GenStep_RimplacePlan engine); RUT_WindowAdobe (used by homestead templates) is DesertFixtures' absorbed content, now defined in THIS mod's own Defs/DesertFixtures/ — not an external dependency
list: minimal+mandrake.rm.injections
status-hint: Ash'karr "promise/whisper" structure content — 12 GenStepDef/TileMutatorDef pairs (batches 3–6 plus the homestead family) that each replay a `Templates/*.txt` rimplace plan via `GenStep_RimplacePlan`; none are yet placed on any world tile.

## must be true
- Each of the 12 `TileMutatorDef`s (`RUT_OasisShrine`, `RUT_RakatanTrace`, `RUT_Cistern`, `RUT_TollGap`, `RUT_GlassSea`, `RUT_Monument`, `RUT_DeadBeacon`, `RUT_BrokenRing`, `RUT_ImperialWaystation`, `RUT_HomesteadAbode`, `RUT_Homestead`, `RUT_HomesteadCompound`) is `MayRequire="Ludeon.RimWorld.Odyssey"` and its `extraGenSteps` cites exactly one `RUT_GenStep_*` def of the matching name.
- Each `RUT_GenStep_*` def's `genStep` is `RimMandrake.StructureInjections.GenStep_RimplacePlan` pointing at its own `Templates/<name>.txt` file (all 12 files exist on disk), `centerOnMap=true`, `order=400`.
- Running a `RUT_GenStep_*` step actually paints the plan's `TERRAIN` lines and spawns its `THING` lines onto the map — e.g. `RUT_GenStep_OasisShrine` places `PavedTile` terrain in a 16×12 footprint plus one `PrimitiveWell` and four `SculptureSmall`; `RUT_GenStep_HomesteadAbode` places a 9×8 footprint including `AncientCrate`, `Bedroll`, `Campfire`, `DiningChair`, `Door`.
- The 3 homestead `TileMutatorDef`s each ALSO carry `Inhabited_Cast` and `RM_InhabitedStock` in `extraGenSteps`, gated `MayRequire="mandrake.rm.inhabited"` — those two steps no-op on a tile with no `WorldObject_Inhabited` place, so they must not error when that mod/place is absent.
- None of the 12 `TileMutatorDef`s are assigned to any Ash'karr world tile yet (confirmed by reading the defs — deliberate deferral per the roster's own protocol) — a walk cannot exercise the natural mapgen trigger path and must fire each GenStepDef directly instead.
- Without `Ludeon.RimWorld.Odyssey` active, all 12 `TileMutatorDef`s (via `MayRequire`) are silent no-ops — no error, nothing registered.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.injections" and no XML error naming any of GenStepDefs_Batch3/4/5/6/Homestead.xml or TileMutatorDefs_Batch3/4/5/6/Homestead.xml
2. [D] def read-back: TileMutatorDef `RUT_OasisShrine` exists; `extraGenSteps` contains `RUT_GenStep_OasisShrine`
3. [D] def read-back: GenStepDef `RUT_GenStep_OasisShrine` exists; `genStep.planFile` = `Templates/oasis_shrine.txt`; `genStep.centerOnMap` = True; `order` = 400
4. [D] def read-back: TileMutatorDef `RUT_HomesteadAbode` exists; `extraGenSteps` contains `RUT_GenStep_HomesteadAbode`, `Inhabited_Cast`, `RM_InhabitedStock`
5. [B] on a fresh quicktest map, `jawa/run_genstep` {genStepDef: "RUT_GenStep_OasisShrine"} → `success:true`, `threw` empty
6. [B] `jawa/list_things` {defName: "PrimitiveWell,SculptureSmall"} on that map → 1 `PrimitiveWell` and 4 `SculptureSmall` found
7. [B] `jawa/get_terrain_batch` over the oasis_shrine footprint (map origin, 16×12) → cells report `PavedTile`
8. [B] on a second fresh quicktest map, `jawa/run_genstep` {genStepDef: "RUT_GenStep_HomesteadAbode"} → `success:true`, `threw` empty; `jawa/list_things` {defName: "AncientCrate,Bedroll,Campfire,DiningChair,Door"} finds at least one of each
9. [S] (human pass) once a promise is actually placed on a real Ash'karr tile (follow-up work, not this pass): confirm the structure reads as intended in its arc/lore context, not just mechanically present

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**A placed structure reads as a place**
- [ ] `sirut_structure_reads_as_its_name` — each of the twelve plans (oasis shrine,
      cistern, toll gap, glass sea, monument, the homesteads and the rest), run on a
      map, reads at play zoom as what it is named. (guess)
- [ ] `sirut_oasis_shrine_reads` — `RUT_GenStep_OasisShrine` lays a paved court
      with a well and small sculptures that reads as a shrine.
- [ ] `sirut_homesteads_read_lived_in` — the homestead plans read as places someone
      lives, with adobe walls and the adobe window (`RUT_WindowAdobe`). (guess)

**Its own art**
- [ ] `sirut_adobe_window_reads` — `RUT_WindowAdobe` reads as a window set in an
      adobe wall, from every side it can be built facing. (guess)

### cannot show

- [ ] `sirut_never_floating_things` — structure pieces placed off the plan's
      ground, overlapping each other or stranded in rock.
