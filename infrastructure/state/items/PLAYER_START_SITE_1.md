# The player's formal start site — the Hutt junkyard (owner, 2026-09-08)

Owner: *"create the world location where the player formally starts: a place of ruined
ships and old megastructures."*

## What the lore already fixes (read 2026-09-08)
- **Scenario_Utinni**: the start is a **Hutt junkyard** — "The Hutts keep a mountain of
  the galaxy's discards out here" — with the dead Rakatan hull (the gravship), Gamorrean
  guards, and the clan sneaking in. The junkyard is **old accumulation**, hauled and
  piled for decades.
- **fall_line.md (frozen)**: the Fall Line's wreckage is **fresh** ("Nothing here is
  old"), renewable, Empire-claimed salvage rights, region not biome, hard bans on new
  BiomeDefs/water/lush. A Hutt yard is downstream of it in the salvage economy — the
  yard is where hauled wreckage goes to pile up, not the deposition belt itself.
- **MEASURED constraint**: no tile is near both the Fall Line and the Rust Cathedral
  (min distance > 8 tiles everywhere). "Ruined ships AND old megastructures" therefore
  means: one anchor is real worldmap terrain, the other arrives by **structure
  injection on the local map** (StructureInjectionsRUT already carries templates, incl.
  `broken_ring.txt`).

## Candidates (MEASURED off live V27 + canon CSV, 2026-09-08)
- **A — "Zeddo's Yard"**: the tile cluster at **Zeddo's Toll** (Hutt, tile 17006,
  Ashfall Range, dFall=1). Candidate start tiles 17007 / 1621 / 17011 — Fall Line
  Barrens, arc 53–57, ~40 °C, road distance 0–1, Hutt distance 1–2. Ships-first: the
  belt supplies the yard, the toll road brings "anyone who has garbage to haul" (ties
  the waste economy to GAPING_DOOM_SITE_1); megastructures injected locally.
- **B — "Gorga's shadow"**: near **Gorga the Immense's Palace** (Hutt, tile 3638,
  Anvil, dCathedral=3, arc 15.5, 61.7 °C). Megastructure-first: the collapsing works
  three tiles off; discards hauled in by the Cartel. Brutally hot and deep dayside —
  strong imagery, harsh start.
- (Checked and weaker: Hurgo's Kennels (21230) — neither anchor; no Hutt site near the
  Cathedral's cooler flanks exists.)

## RULED — owner picked A, "Zeddo's Yard", by card 2026-09-08
The junkyard anchors at the Zeddo's Toll cluster (candidate start tile **17007**,
alternates 1621/17011 — final tile chosen at build time when the local map is judged).
Ships are the real terrain (Fall Line Barrens); the old megastructures arrive by
structure injection. The toll road carries the waste-hauling economy (ties to
GAPING_DOOM_SITE_1 and the Junkers).

## spec (fills in at build)
- World presence: the start tile marked (landmark/world object per the pattern the
  owner rules), scenario's start location pinned to it; junkyard identity carried by
  injected structures + the scenario opening.
- Respect fall_line.md's hard bans if in the region (no new BiomeDef, no water, no
  affiliated ferals).

## verify
- Scenario actually starts on the chosen tile (quicktest); site content visible on the
  local map; owner LOOKS at a staged shot before freeze.

## criteria
- The formal start exists on THE map, matches the crawl ("mountain of the galaxy's
  discards"), and both promised skylines — ruined ships and old megastructures — are
  present at the site (one real, one injected).
