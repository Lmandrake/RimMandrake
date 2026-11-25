# BOUNDARY: a walk save holds pens with six of each creature of the mod (walk_pens.py), Design Version 0.1.0

Code: `src/RimMandrake/Utils/modcheck/walk_pens.py`. It is called by a mod's walk staging (for Pyrelands:
`design/concepts/Pyrelands/version/in_game/visit_9/scripts/walk_restage.py`) and by its own command line. Tests:
`src/RimMandrake/Utils/modcheck/selftest_walk_pens.py` (offline). Live test: `walk_pens.py --mod <Mod> --check` on a loaded,
paused walk save (the command is in the module's docstring).

The rule: `src/RimMandrake/rimflow/roles/walk_brief.md` (a walk save for a mod that adds or changes creatures holds pens with six of
each creature of the mod).

## ACCEPTS

- **a-mod-name.** The name of a mod folder under `src/RimMandrake`, `src/RimStarWars` or `src/RimUtinni`.
- **a-biome-roster.** A BiomeDef of the mod with `<wildAnimals>` in the shorthand form (`<Kind>weight</Kind>`) or the `<li>` form
  (`<li><animal>Kind</animal>...`), and patches anywhere under `src/` that add, remove or replace children of that
  `<wildAnimals>`, a patch nested in `PatchOperationFindMod` or `PatchOperationSequence` included.
- **a-mod-with-no-biome.** Then the roster is each PawnKindDef of the mod whose race ThingDef in the mod is not Humanlike.
- **a-loaded-paused-map.** The live step runs on the current map of a paused game, through the bridge (python.exe).

## DOES NOT SURVIVE (not handled)

- **a-patch-with-a-complex-xpath.** A patch whose xpath does not name `BiomeDef[defName="<biome>"]/wildAnimals` directly is not read.
- **a-roster-change-in-csharp.** A roster that C# changes at load is not seen.
- **a-map-with-no-free-block.** When no block of the map is free of stations, water, roofs, pawns and fire, the step stages nothing
  and says so (`COULD NOT STAGE`). It never builds over a station.
- **a-kind-the-game-did-not-load.** It is named in `not_loaded`; it gets no pen.

## PROMISES (each one is owed a test of the same name)

- **the-roster-is-read-as-elements.** Comments and `<li>` tags are not counted; a commented-out kind is not on the roster.
- **patches-add-remove-and-replace.** A patch that adds a kind puts it on; a remove takes it off; a replace sets the list.
- **the-pyrelands-roster-is-sixteen.** The real defs of Pyrelands give the 16 kinds that the owner looked at on 2026-11-24.
- **a-mod-with-no-biome-uses-its-animal-kinds.**
- **a-pen-is-sized-by-body-size.** A larger body size never gets a smaller pen.
- **pens-do-not-overlap.** Each pen has a lane of two cells to its neighbours.
- **the-site-never-covers-a-station.** The chosen block, with its margin, holds no station cell and no blocked cell.
- **no-free-site-is-said.** The site chooser returns None, never a block over a blocked cell.
- **a-pen-has-walls-and-one-door.** The walls close the pen except for its one door cell.
- **six-spawn-cells-inside.** Six distinct cells, inside the walls.
- **the-age-plan-is-three-and-three.** Three male, three female; one juvenile and one baby where the race has those stages.
- **the-live-check-reads-state.** `--check` passes only when each pen holds six living animals of its kind, no hostile and none in
  a mental state; it exits 1 on a short pen and 2 when it could not look.

## LIMITS

None.
