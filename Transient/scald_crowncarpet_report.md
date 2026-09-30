# SCALD_CROWNCARPET_NO_HABITAT_1 — investigation report

Status: DONE

## Task
MEASURED live 2026-09-30 (`Transient/quicktest_biomes_2026-09-30c.json`): a regenerated
RM_TheScald map had 1 plant (an anima tree). Per `BLUEDESERT_ZERO_PLANTS_1` precedent
(`Transient/bluedesert_zero_plants_report.md`, commit `788574ea0`), the Scald's only wild
plant, crowncarpet, grows only on a shallow-margin terrain that map generation never lays
down.

## Findings

Confirmed the design already diagnosed this exact defect on 2026-09-27
(`design/Jawa/worldbuilding/biomes/the_scald_underwater_flora_pass_2026-09-27.md`,
"Current state of the biome") but never landed the fix. Two independent causes,
both required for crowncarpet to have zero habitat:

1. **`RM_TheScald.plantDensity` was UNSET** (`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml`)
   → engine default 0 → the `<wildPlants><RM_Crowncarpet>0.4</RM_Crowncarpet></wildPlants>`
   row never fires through the wild-plant spawner at all, regardless of terrain tags.
2. **`RM_Crowncarpet`'s `wildTerrainTags`** (`RM_CrowncarpetBed`, `RUT_ScaldMarginMat`,
   `src/RimMandrake/LuminousPigment/Defs/ThingDefs_Plants/RM_Crowncarpet.xml`) match
   NEITHER of the Scald's own floor terrains:
   - `RM_CrowncarpetBed` is patched only onto vanilla `WaterOceanShallow`
     (`Patches/CrowncarpetBedTag.xml`) — the Scald's own shore terrain is the
     custom `RUT_ScaldWaterOceanShallow` (wired via `RM_SeaShoreExtension` +
     `terrainsByFertility`), which never received that tag.
   - `RUT_ScaldMarginMat` exists only on `RUT_ScaldMargin` — a terrain def whose
     own header states explicitly it is NEVER placed by map generation. It is
     deliberately reserved for hand/bridge map-authoring as a geometrically
     isolated cove, because `PawnUtility.KnownDangerAt` (and therefore
     `SwimPathFinder`/`JoyGiver_GoSwimming`) never reads terrain `burnDamage` —
     an auto-placed margin patch touching open boil water would let a pawn
     swim/path straight through boiling water to reach it (confirmed against
     the decompile by `SCALD_MECHANICS_1`'s own spike pass, 2026-09-13). This
     placement step is real, tracked, owed work (`SCALD_MECHANICS_1` S3),
     unchanged and undone as of its last pass (2026-09-18) — it needs the
     bridge, out of scope here, and should stay a hand-authoring step, not be
     automated.

So on any regenerated/quicktest Scald map, crowncarpet's habitat is empty by
construction — matches the measured 1-plant (anima tree) result exactly.

**Roster vs BiomeDef check**: `design/Jawa/worldbuilding/biomes/rosters/the_scald.json`
carries an empty `"flora": []` — no named flora defs are missing from `wildPlants`.
The 2026-09-27 design pass proposes NINE new Scald flora defs
(`RM_Simmerlace`, `RM_Kettlewick`, `RM_Vekkfan`, `RM_Thurlsponge`, `RM_Glasskelle`,
`RM_Pulsebead`, `RM_Foamgorse`, `RM_Seepcandle`, `RM_Threshreed`) — grepped `src/`,
confirmed none exist as defs yet (still purely a design proposal, item
`SCALD_UNDERWATER_FLORA_1`). That pass carries open owner questions (exact
`plantDensity` value, two harvest-item choices, one lore question) and needs new
art — out of scope for this habitat-only item; not built here.

## Fix

Minimal, reuses existing infrastructure exactly as the 2026-09-27 design pass
already recommended for crowncarpet specifically (its "one-line fix"), no new
terrain/tag invented:

1. `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml` —
   added `<plantDensity>0.3</plantDensity>` (the design pass's own proposed
   value; it states the roster works unchanged anywhere from 0.15-0.5, so this
   is the accepted default pending an owner card, not a new invention).
2. `src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RUT_ScaldWater.xml` —
   added `RM_CrowncarpetBed` to `RUT_ScaldWaterOceanShallow`'s `<tags>` only
   (the dive-layer floor terrain the gravship's sea-floor map actually
   generates with). Deliberately NOT added to the sibling
   `RUT_ScaldWaterShallow`/`Deep`/`MovingShallow`/`MovingChestDeep` terrains —
   crowncarpet's own header explains `RUT_ScaldMarginMat` (not the shared
   `Water` tag) was chosen specifically to keep the mat off the wider boil;
   this narrower fix only touches the one shallow-shore terrain, matching the
   plant's own shipped description ("thick and unbroken where the water
   boils") and the design pass's reading of ban 4 (aimed at macro-life/things
   that swim the roiling surface, not a sessile mat).

Did NOT touch `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheScald.xml` —
its own header marks it 🔴 FROZEN, "do not edit here", and it deliberately
carries an empty `<wildPlants/>` already. Did NOT auto-place `RUT_ScaldMargin`
via any GenStep/terrainPatchMaker — that remains `SCALD_MECHANICS_1`'s owed,
bridge-only map-authoring step (see Findings above); automating it risks the
swim-path hazard the terrain's own header warns against.

## Live check for coordinator

Regenerate/quicktest an `RM_TheScald` map and expect **more than the prior 1
plant** — crowncarpet (commonality 0.4, density 0.3) should now appear on
`RUT_ScaldWaterOceanShallow` cells. This is still just the incumbent plant, not
the 9-plant `SCALD_UNDERWATER_FLORA_1` roster (unbuilt, separate item, needs
owner rulings first). If the count still reads near-zero, check whether the
quicktest map actually generates on `RUT_ScaldWaterOceanShallow` cells at all
(vs. only the inland `RUT_ScaldWaterShallow`/`Deep` fresh-water terrains, which
intentionally do NOT carry the new tag).

## Verification

- `python3 -c "import xml.etree.ElementTree as ET; ET.parse(...)"` — both edited
  files parse clean.
- `python3 src/RimMandrake/Utils/run_selftests.py` — ran in foreground: **77/79
  passed** (2 skipped, 1 unmeasured — `bridgetools/selftest_tool_metadata.py`,
  needs the Windows-side .NET build, expected). **1 FAILED:**
  `selftest_deployed_biome_refs.py` — 19 dangling `RUT_*` wildPlants refs, all
  in `RUT_TheRot.xml`/`RUT_Contagion.xml`/`RUT_Miasma.xml`/`RUT_TheForge.xml`/
  `RUT_WeepingStones.xml` (a `mandrake.rut.rotsporekit` deploy gap). **Pre-existing
  and unrelated** — none of the 19 name `RM_TheScald`, `RM_Crowncarpet`, or any
  Scald terrain, and neither file this pass touched appears in the failure
  list.

Status: DONE.
