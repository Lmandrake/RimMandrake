# P11 build log — LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (FOUNDRY offline builder, 2026-10-17)

Base: origin/main a00177add (P7 DLL 38aa4ddb6). No bridge, no game.
Ruling R11 (owner 2026-10-17, verbatim): "Vary it. Some lakes will be shallow and silted up. Others will be deep and
chasm-like. Depends on the biome. The more mountainous, the deeper in general. The more plains-like, the
smoother/shallower. They should also have some variation down there, not just a radial crater."

Built in the scratch clone /home/mandrake/rm/scratch/FOUNDRY/p11: the P12 builder was editing the same seat clone
(Mod.cs, both csproj, Excavation, Program.cs), so P11's hunks were ported there by script (zero swim lines carried).

## Stage (a) — read docs, find today's bed code and formation path
- status: DONE. Floors live in `RM_MapComponent_Excavation.bedRecord` (scribed byte grid, read first by `BedLevelsAt`;
  this is what P3's pond histogram reads; the brief's "dug-depth grid" would have made lake squares excavated). Formation
  was lazy (first touch). A full lake = surface 0 → `StageForExact` Original: no terrain change by construction (R10).

## Stage (b) — roughness source
- status: DONE. r = the tile's `HillinessForElevationGen` (what map generation used; Flat .05, SmallHills .30, LargeHills
  .55, Mountainous .80, Impassable .95) + a per-biome bias (our biomes from their own descriptions: Abyss, Cracked Lands,
  Scald, Forge, Contagion, Weeping Stones, Lantern Deeps deeper; Sump, Fever Wood, Miasma, Wastes, Stillsand, Leaning
  Scrub, Greentide, Pyrelands, Rust Cathedral, seas shallower; vanilla swamps/bog/grasslands shallower).

## Stage (c) — floor generator `Source/RM_LakeFloorMath.cs` (Verse-free)
- status: DONE. Per lake (key = its lowest square index, so walk order never matters; seed = world persistent value x
  map constant seed): a draw in the band's range (skewed shallow), silted chance, silt-flat bottom, terraces, grain
  direction. Per square: bowl by shore distance with band wall width (plains saucer → chasm walls) x 3-octave value noise
  (stretched along a grain: rifts), ridged trenches, small holes; normalised so the draw is the deepest. Then the shore
  shelf, then ONE BASIN + WAY OUT until settled. No System.Random (own hash noise). Radial slope, `BedDepths`,
  `DeepBedLevels`, `deepBedCellsPerLevel` deleted (R11 replaced them).
- One-basin pass (found by the legacy recession test going red): the level solver keeps a pond as ONE node with one
  surface (`RM_LevelSolve`: a pond is its floor histogram), exact only if a drawn-down lake cannot split into pools
  behind an inner sill. A hole with no downhill route to the deep water is silted to its sill.

## Stage (d) — wiring, formation, settings
- status: DONE. `RM_LiquidStock.RecordLakeFloor` at formation (limited, still lakes; moving water keeps the terrain
  rule; every footprint square recorded; no terrain written). `FormAllBodies` from `FinalizeInit` behind scribed
  `RM_lakeFloorsFormed` (new map: before the first tick; old save: once on load; an indexed lake keeps its floor).
  Settings: ceiling `deepBedMaxDepth` default 100 = 50 m (slider to 125 m), `lakeDepthScale` 1, `lakeFloorRoughness` 1,
  `lakeShoreShelfMetres` 0.5, `lakeWayOutMetres` 1. Tables: site_spec, review_map_coverage (COVERAGE.md regenerated),
  deep_lake_proof (+ its selftest: sheer steps recorded, not judged).

## Stage (e) — tests
- status: DONE. SelfTest 522/522 (+8 `Lake_floor*`, DeepBed cases moved onto the generator). Measured table (40 lakes per
  class, radius 8..71): Flat mean deepest 2.6 m / max 4.5 m, silted 18/40; SmallHills 4.3/9.0, 15/40; LargeHills
  9.2/19.5, 8/40; Mountainous 16.0/34.5, 5/40; Impassable 26.8/50.0, 2/40. A 230-wide chasm lake reaches 48.5 m (best
  of 30). Off-radial (>= 1 m from its ring's mean): mean 0.24 over 20 lakes >= 6 m; radial control 0. Drained lakes: no
  person pocket (K>=2) at r .05/.55/.95 x 6 seeds; water's edge in reach at every 5% drawdown (person, defaults; small
  animal with way out 0.5 m); control (no shelf, no way out) strands. Full lake: water = floor, every square Original.
  Bench: 38k-square lake 27 ms once at map creation.
- Oracle differential kernel == PulseOracle 3000/3000 in depth, surface, levelset, shipped, pond, exact, exactpond.
- vv_shipped_matrix --skip-ep: SHIPPED kernel_fuzz 0/10000, fills_from_limitless 0/10000, surface_random 0/1000, seq_* 0,
  hose 0/2798, trail 0/1500; OFF_edgeSinks kernel_fuzz 142/2000 (known); forced-flag SHIPPED suite 24 fails, set identical
  to the pre-P11 run (diff empty); VERDICT FAIL only on AUTHORED Thirst_slime_last_resort_ruled (known, BENCH).
- run_selftests --only (36 FlowWorks python + settings): 34/36 PASS; reds are the known human_review
  still_water_one_surface_height and settings_screens SWBestiary#BeastMechanics.

## Stage (f) — offline preview
- status: DONE. `src/RimMandrake/FlowWorks/Tools/lake_floor_preview.py` runs the C# generator (SelfTest `--lake-floors`)
  and renders `Transient/fw_scenes/lake_floors/index.html` + lake_1..8.png: plains pond 3 m, plains silted 2 m, swamp 2 m,
  low hills 3.5 m, hills 12.5 m, canyon hills 16 m, mountain 27 m, chasm 46 m; each with contours, a cross-section through
  the deepest square (the pre-way-out floor dotted) and a caption. Each lake takes the first draw of its named kind
  (silted/open), skips disclosed on the picture.

## Defaults chosen (veto list; each a Mod Setting)
- Roughness table (band ranges/caps/silt odds) in the preview: PROVISIONAL tuning, his to approve.
- Shore shelf 0.5 m on every lake's outer ring (play Q4a). A deep-water shore square reads 0.5 m while drawn vanilla deep
  until drawn down (R10: nothing on screen changes).
- Way out 1 m: every floor square has a walked route to land, no step over 1 m (owner ruling 4 kept for people). 0.5 m
  = small animals too (shallower lakes); 0 = true chasms that can strand.
- One basin (no setting): inner holes with no route down silted to their sill.
- Ceiling 50 m default (settable 2..125 m); 50 m reachable only in the mountain/chasm bands at depth x1.
- Oceans and edge rivers get no floor record (spec §5.3; the item's "floor for the readout" is the P8 limitless mark).

## Live proofs owed (L2, P10 walk)
- Owner looks at lake variety on a staged savegame: one flat-biome and one mountainous map, lakes drawn down.
- A new map logs "lake floors: N natural body(ies) formed at map load" before the first tick; terrain grid diff = 0.
- An old save forms its lakes once on load; a lake formed before keeps its floor (save, reload, `DeepestRecordedBed`).
- deep_lake_proof.py rerun with lakeDepthScale 2 (DL_* rows).
