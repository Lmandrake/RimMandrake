# BOUNDARY: the gravship layout library, Design Version 0.1.0

Code: `src/RimMandrake/Utils/gravship_layout.py`. Skill: `skills/gravship-layout/SKILL.md`.
Item: `RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT`.

## ACCEPTS
- A layout file whose root is `<ShipLayoutDefV2>`: an export in `Config\GravshipExport`, or a file that `save` wrote.

## DOES NOT SURVIVE
- A layout inside a mod (a `<GravshipExport.ShipLayoutDefV2>` element under a `<Defs>` root): `load` raises and names the root.
- A `defName` that no mod defines. `validate` does not look up defs.
- The exclusion zone of a thruster. `validate` does not read it.
- `foundationStuff` and `terrainStuff`. `save` writes both as absent. The exporter never writes a value in either.

## PROMISES (tests of the same name in `src/RimMandrake/Utils/selftest_gravship_layout.py`)
- **a-real-export-validates-without-an-engine-thing**: an export holds no `GravEngine` thing, and `validate` returns `[]`.
- **an-engine-thing-away-from-the-coordinates-is-reported**: a `GravEngine` thing in another cell than `gravEngineX/Z` is one problem that names that cell.
- **coordinates-on-a-cell-with-no-foundation-are-reported**: the margin, a cell outside the grid, and absent coordinates are each a problem.
- **a-save-keeps-storage-and-comp-settings-and-the-description**: the 26 settings blocks of the ring export, and a description, are the same after a load and a save.
- **the-round-trip-fails-on-a-dropped-setting**: a `save` that drops `compSettings` makes `--roundtrip` report a difference.
