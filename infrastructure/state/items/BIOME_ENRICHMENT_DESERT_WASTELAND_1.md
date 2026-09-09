# BIOME_ENRICHMENT_DESERT_WASTELAND_1

Owner, 2026-09-09 (review B1, `WORLDMAP_FINAL_REVIEW_2026-09-08.md`): Desert and
Wasteland read mutator-thin where caravans travel most; place from their sheets'
own kit, dune sea stays barren by rule.

## Measurement (fresh, joined against the CURRENT frozen CSV)

`WORLDMAP_DESERT_BAND_REPAIR_1` retyped 1,542 tiles tonight (Desert -> ExtremeDesert
band A, Desert -> Wasteland band D) *before* this item ran, so the queue's 53%/63%
figures are stale. Re-measured by joining `world/ASHKARR_WORLDMAP_tiles.csv`
(current biome, post-repair, sha256 `756d9ffc...`) against
`Transient/final_review/mutators.json` (per-tile mutator counts, exported
2026-09-09T04:20:50Z, pre-repair) by tile ID — valid because both the
`WORLDMAP_DESERT_BAND_REPAIR_1` and `WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1`
commits moved only the `biome` column and explicitly called no mutator tool
("No mutator tool was called this pass" / mutators untouched), so tile->mutator
association is still current even though the export predates the repaint. Every
tile ID in the CSV has exactly one row in the mutator export (0 missing, 0 extra).

| biome | tiles (current) | zero-mutator | % |
|---|---|---|---|
| Desert | 2,390 | 1,372 | **57.4%** |
| Wasteland | 1,853 | 1,180 | **63.7%** |

## Why nothing was placed — the kit is not concrete enough to place without guessing

Checked, in order: `design/Jawa/worldbuilding/biomes/desert.md`,
`.../wasteland.md`, both biomes' fauna rosters (`rosters/desert.json`,
`rosters/wasteland.json` — fauna only, not mutators/landmarks),
`design/Jawa/worldbuilding/unused_mutators_full_list.csv` (255 unused
TileMutatorDefs, the actual placeable menu), and
`design/Jawa/worldbuilding/structure_injection_roster.md` (the only doc that pairs
this register of content with real defNames).

- **`desert.md` names zero RimWorld defNames.** Its §7/§8 "kit" (the dew line,
  crevice shelter, ultracactus, wide gaps as toll points, shade patches as
  middens) is narrative description with no mutator/landmark defName attached
  anywhere in the sheet or its roster.
- **`wasteland.md` §8's "mutator/injection palette" table is thematic categories,
  not defNames** — "hypersaline pools," "vitrified craters," "trench systems,"
  "rib-vaults," "trapped enrichment" etc. None of these strings match any
  TileMutatorDef in the 596-mod load (checked against the unused-mutator census
  and the in-use 88-def list in `unused_mutators_census.md`). Placing anything
  under these headings would mean *me* deciding which existing def stands in for
  "vitrified crater," which is inventing the kit, not executing it.
- **The one place in this repo that DOES pair this exact register of content
  with real defNames is `structure_injection_roster.md`'s RUT_/RSW_ "PROMISE"
  rows** (`RUT_OasisShrine`, `RUT_Cistern`, `RUT_TollGap`, `RUT_RakatanTrace`,
  `RUT_Monument`, `RUT_DeadBeacon`, `RUT_BrokenRing`, `RUT_ImperialWaystation`,
  the RSW batch-2/4 defs) — built with `extraGenSteps` and explicitly deferred
  ("NOT YET PLACED... out of scope for this pass, follow-up work"). But every
  one is gated by **arc/lore/character context** (Sh'kaar country, Ozzik,
  Ishko vs Sh'kaar, the terminator band, a specific road), not by biome —
  each batch file says so explicitly. Placing them here as generic Desert/
  Wasteland biome fill would be re-purposing content earmarked for a specific
  narrative promise, which is exactly what "patch a curated artifact, never
  re-allocate" (CLAUDE.md) rules out — plus most aren't gated to Desert or
  Wasteland at all (e.g. Cistern/Dead Beacon are terminator-band, Toll Gap is
  road-through-cliffs).
- Also checked and ruled out: `GL_Crater` and the other `GL_*` landforms would
  be the obvious engine match for "vitrified craters," but the world-editing
  skill (§3, measured 2026-08-26) is explicit that **the 45 `GL_*` defs cannot
  be written by any world tool** — Geological Landforms computes them at
  display time from hilliness/topology/elevation and they never enter
  `mutatorsNullable`.

## Disposition

Left **`doing`**, not closed. No bridge call made (bridge stayed FREE the whole
session — confirmed free at start and left free). No world file, tile CSV, or
frozen stamp touched.

**What would unblock this:** either (a) the owner/BENCH names concrete
TileMutatorDefs (or authors new biome-general ones — none exist for Desert
today) against Desert's §7/§8 kit and Wasteland's §8 family table, the way
`structure_injection_roster.md` did for the PROMISE content, or (b) a ruling
that increasing DENSITY of the biomes' own already-legal, already-in-use
mutators (Caves/Oasis/MineralRich/AncientRuins/etc., whichever pass
`TileMutatorDef.IsValidTile` for Desert/Wasteland) satisfies "place from the
kit" well enough to proceed without new thematic defs — that's a scope call
for the owner, not mine to assume.
