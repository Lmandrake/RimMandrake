# North-star seeding pass — 2026-10-01 (NORTH_STAR_WALK_AUTHORING_1)

Owner ruling 2026-10-01: *"There will be many such mods that require a human nearby to build them
proper northstar scripts. You are mostly seeding the field right now with reasonable initial
guesses for refinement later through debugging needs or live feedback."*

Every section seeded here is `state: DRAFT` with an empty `validated-hash:` — it binds nothing.
`modcheck validate` was not run. Lines tagged `(guess)` are the least certain.

## Baseline (before any edit, worktree at origin/main b819a5d76)
- `modcheck lint`: 3 FAIL (BAD_PACKAGEID `mandrake.rm.biomes` in Cauldron/GelatinousSlime/TheForge), 12 WARN
- `floor --all`: 0 refusals among seeded mods (all DRAFT, "no bar")
- run_selftests.py: (pending)

## Batches
- run_selftests.py baseline: 100/105, 4 FAILED pre-existing (selftest_walklint, selftest_one_path_seam, selftest_sound_paths, selftest_sun_heat), 1 unmeasured

### Batch 1 — creatures (SWBestiary subject, 1,748 PNGs)
SWBestiary, SeaBeasts, SeasWaterline, Livestock, JawaIkee, HelixTellurox, BeastNorm — 7 walks.
Lint/floor: no new findings. Notable seeded question: Cindermare/Skarnix/Karrask/Tellurox each ship ONE
`Graphic_Single` texture (no facings) — seeded as a `(guess)` cannot-show for him to rule.

### Batch 2 — gear, species, droids, vehicles
Armoury, StarWarsRaces, Droidworks, KotORBandolierNorthFix, CereanManeFix, MSEDroidFix, JawaIonWeapons,
DesertVehicleReskin — 8 walks. Lint/floor: no new findings. The three single-PNG fixes get a tight
must/cannot pair naming the exact defect they repair.

### Batch 3 — biomes, world art, UI skin, structures
Contagion, LeaningScrub, Cauldron, FireEcology, AshkarrLandmarkArt, RustChrome, MenuShell,
StructureInjectionsSW, StructureInjectionsRUT — 9 walks. Lint/floor: no new findings.
Deliberately NOT seeded: BeastLairs, DesertFixtures, UtinniShell — each is the second walk of an
unresolved duplicate-PNG pair (item step 3); seeding both halves would make competing demands on one
image, so only the mod-named walk of each pair got lines.
Noticed, not fixed: FireEcology.md's `## must be true` still names `RSW_FE_*` defs; the shipped defs are
`RM_FE_*` (src/RimMandrake/Pyrelands/Defs). The seeded section uses the live `RM_FE_*` names.

### Batch 4 — single-file art repairs, medical/food/relic items, places
ToolBeltFix, SauridFrillFix, ResearchKitEastFix, PhytokinBarkHeadFix, GravshipAstronautFix,
BlastDoorFrameAsyncFix, Bacta, Cuisine, SacredGraffiti, Antiquities, Inhabited, MandrakePatches,
StarWarsPatches — 13 walks. Lint/floor: no new findings.

## Result
37 walks seeded (7 + 8 + 9 + 13), every one `state: DRAFT`, empty hash, `modcheck validate` never run.
No `shows=` wiring added: `shows=` naming an id no VALIDATED checklist defines is a lint error (spec §2),
so wiring a DRAFT id would only add failures.
After: run_selftests.py 102/107, the same 4 pre-existing FAILs, no new failures. lint: same 3 FAIL /
12 WARN as baseline. floor --all: no refusals introduced.

Not seeded (judged): RiverSteam (inside VALIDATED FlowWorks); BeastLairs, DesertFixtures, UtinniShell
(duplicate-PNG pair halves); pure code/prose mods (Oracle-style read-axis candidates: Aftermath,
AftermathRites, PawnFlavor, JawaVoice; arithmetic: Visibility, RimDefDump, LoadTracer, etc.).
