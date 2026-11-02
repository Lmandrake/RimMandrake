# Geological Landforms: replicate or keep? Judgment, 2026-11-02

Item `LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT`. Owner, C06, 2026-10-10: *"If we can replicate them then yes they
can go. Landforms seems like a big lift though. Experiments required to validate. May end up keeping landforms for that
reason."*

**Verdict: GO.** We can replicate it, so `m00nl1ght.geologicallandforms` comes off `ModsConfig.FULL.LATEST.xml` (316
mods). Decided under the delegation policy, because his C06 ruling sets the condition and the experiment below meets it.
Evidence: `design/RimMandrake/geological_landforms_judgment_2026-11-02.evidence.json`, written by
`src/RimMandrake/Utils/gl_landforms_evidence.py`; guard: `src/RimMandrake/Utils/selftest_landforms_verdict.py`.

## What it does

GL adds 44 landforms, each registered as a `GL_*` TileMutatorDef. It also patches `TerrainPatchMaker`. Under Odyssey,
its own settings switch off 14 of those landforms in favour of the vanilla ones. They also switch off vanilla's `River`,
`RiverDelta`, `Headwater`, `RiverIsland` and `RiverConfluence` in favour of GL's own river landforms. That leaves 30
landforms active. They roll **at map generation** from tile conditions such as topology, hilliness, temperature and a
commonness. They are **never stored on a tile**, so nothing can force one onto a tile or remove one from a tile:
`world_mutators_set` reports `added: 1` and the landform is gone again
(`skills/rimworld-world-editing/references/mutators-and-objects.md`).

## Why the lift is smaller than it looked

- **Nothing needs it.** No active mod hard-depends on it. The two hard dependents, `biometransitions` and
  `biomescaverns`, are not on the list. `mandrake.rm.biomes` only names it in a `loadAfter`. Map Preview, Vehicle
  Framework and MapModeFramework mention it in their DLLs as optional compatibility.
- **The world does not carry it.** The R3 world save holds 27,913 tile-mutator entries. All of them resolve against the
  2026-11-02 dump, and none is `GL_*`. The only GL trace is an empty `GeologicalLandforms.LandformData` world component
  with 4 cached tiles and no landforms. With the mod gone, Scribe drops it with one load error.
  `save_adoption_check.py` reads the save identically with and without GL.
- **Most shapes already exist.** For each of the 30 active landforms the evidence names the def that already makes it:

| coverage | count | landforms |
|---|---|---|
| full | 20 | Atoll, Caldera, Canyon, CaveEntrance, SurfaceCave, CoastCorner, Crater, DesertPlateau, Gorge, Rift, Island, LoneMountain, five river forms, SecludedValley, Sinkhole |
| partial | 5 | CoveWithIsland and SecludedCove (Cove/Bay, no island), Badlands (RM_JaggedRocks/RM_StoneForest), Cirque (Basin), IceOasis (Oasis) |
| gap | 5 | Glacier, Landbridge, Tombolo, Skerry, SwampHill |

  The four landforms our sheets ask for (map-makers design §4.3 Q1: Canyon, Crater, DesertPlateau, LoneMountain) are
  all covered.
- **The one GL-only shape the sheets want is now ours.** `RM_LoneMountain` (mandrake.rm.tilefeatures) is one rock
  mountain rising from an open plain. The whole map's elevation is replaced, and the mountain is shrunk when needed so no
  rock comes within 6 cells of an edge. It took one pure geometry function, one ~40-line worker and one def, the same
  cost as each of the 29 VEE ports. Its offline sweep of 540 maps (three map sizes, the radius range, the worker's
  extreme centre offsets, 20 seeds) shows:
  - the centre is always rock;
  - every edge band is open;
  - rock covers 9–23% of the map;
  - at least half the map is open plain reachable from the edge.

  A planted negative (an oversized mountain without the fit) is caught. It sits under the Landforms switch in Mod
  Settings and has `chanceOnNonLandmarkTile` 0: it appears only on a tile painted with it.

## Why it goes

- **A painted world needs a painted landform.** Every tile of ours gets its shape by hand at the single painting pass
  (`BIOME_PAINT_ONCE_AT_THE_END_1`). GL's landforms cannot be placed or removed, so on its tiles the shape is chance, not
  authorship. That breaks the owner's 2026-10-10 card choice: *"build each landform as our own tile modifier
  (force-placeable at the painting pass…), not landform-mod data files"*.
- **It overrides our terrain.** On a tile where it rolls, a landform's graph writes terrain over the biome's. GL's
  DryLake, for example, hard-codes soft sand where our salt crust belongs (`JawaTerrain_SaltPans.xml`).
- **It replaces vanilla's rivers.** While it loads, its settings switch off vanilla's river family and its own river
  landforms draw the rivers instead. Without it, vanilla's river family runs again.

**What we lose:** the 5 gap shapes and the island or ice detail of the 5 partial ones, on tiles where GL would have
rolled them. None is asked for by a biome sheet. If one is wanted, it is one worker in TileFeatures, as Lone Mountain
was.

## Limits

- Offline. `RM_LoneMountain` builds (`winbuild.py TileFeatures`) and its geometry is proven, but no map has been
  generated with it yet. Its first in-game look belongs to the map-maker pilot (`MAP_LANDFORM_MUTATORS_DESIGN_1`).
- Coverage is judged from each def's worker, description and geometry, not from side-by-side maps.
- The census reads the list as it stood with GL on it (316 + GL) and the R3 world save. It is a size for the question,
  not a claim about the final planet.
- `JawaTerrain_SaltPans.xml` still explains GL's DryLake override. That note is true only while GL loads; it is left
  as provenance.
