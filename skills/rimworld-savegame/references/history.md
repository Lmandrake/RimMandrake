# History: the measurements, and the lines that were wrong

The active files hold the lessons. This file holds dates, full measurements and corrected lines (corrected 2026-11-23).
Engine facts of that date were read in the decompiled 1.6 source through RimSage. Save facts of that date were read from
`ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (R3) and `CANONICAL_ASHKARR_START_2026-09-12.rws`.

## Dates of the lessons

| lesson | date |
|---|---|
| a dependency check is not sufficient before a retirement | 2026-09-09/10 |
| VEF `futureQuests` in the save | 2026-09-10 |
| a substring hit inside `Techprint_guy762_ResearchKotOR_workbench` | 2026-09-14 |
| gene `loadID` collision in a splice | 2026-09-21 |
| the loaded mod set is not `ModsConfig.xml` | 2026-09-19 |
| a stale capture with a matching `modCount` (seat FOUNDRY, retired) | 2026-08-31 |
| text mode collapses CRLF | 2026-09-20 |

## Measurements

- The offline hash formula against the live dump: BiomeDef 66/66, RoofDef 6/6, TerrainDef 1,227/1,238. The 11 misses are all
  +1, moved by a collision.
- A reload after a corrupted save once read "~23–30 minute". `rimworld-load-round` holds the newer times.
- R3, 2026-11-23: 13,531,124 bytes, 367,723 lines, each ending in CRLF, parsed in 0.30 s. Grids: `topGridDeflate`,
  `underGridDeflate`, `foundationGridDeflate`, `tempGridDeflate` and `roofsDeflate` are 125,000 bytes each; `fogGridDeflate` is
  7,813 bytes. `foundationGrid` reads `0` in 59,225 cells and `Substructure` in 3,275.
- The 4 DefDump captures of 2026-08-29 and 2026-11-23 on disk write `shortHash` as a number.

## Corrected lines

- **Who may write a save.** The skill did not name the owner's ruling of 2026-08-18. Two offline `.rws` writers had passed each
  check and killed the game at load. Nine save-writing scripts were deleted on 2026-08-19. His words of 2026-09-06 are on
  `DROID_ASIMOV_SAVE_SCRUB_1`. Later small repairs of R3 are in `infrastructure/state/CANONICAL_SAVE.md`.
- **`SaveMap.paint` as a route.** The old text said "RimBridge and save-editing are complements". The old division: the bridge did
  things and structures, live, and the save did the substrate (terrain, rock, water, roofs). Nothing calls `paint` or
  `write` of `SaveMap` (2026-11-23). The bridge has `jawa/set_terrain_batch`.
- **The snow grid.** The old block listed `<snowGrid><depthGridDeflate>` among the shortHash grids. `SnowGrid.ExposeData`
  writes a float depth as a ushort.
- **`foundationGrid`.** The old text said that it is UNIFORM across all 62,500 cells on the map measured. R3 varies.
- **World biomes.** The old text sent biomes to `rimbench/savemap.py`. That module reads map grids only. World tiles are in
  `worldmap.py`.
- **"Things are indices".** Only the things that pass `IsSaveCompressible` are in `compressedThingMap`. R3 holds 6,605
  `<thing>` elements as text.
- **`el.clear()`.** The old text said: never clear a parent while its children are still in flight. The fault is the reverse. The
  `end` event of a child comes first, so a clear of each element empties the children before the handler of their parent.
- **A substring hit inside `<def>NAME</def>`.** The old text said that a search scoped to `<def>NAME</def>` can match a longer
  defName. The full string cannot give those 9 hits. The true search of 2026-09-14 is not known.
- **A hand-tuned crew.** The old table said "this is how you hand-tune a crew". The ruling of 2026-08-18 ended that route.
- **`missing_mods`.** The old text said that the gate checks "unconditionally". The bridge takes `ignoreModCompatibility: true`
  (`skills/rimbridge/references/traps/lifecycle.md`).
- **The loaded mod set.** The old text named the newest autosave as the only answer. `jawa/running_mods` reads the running game.
