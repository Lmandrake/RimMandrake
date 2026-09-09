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

## RUN-SHEET — the flight to Zeddo's Yard (state as of 2026-09-09 05:40Z, game DOWN)
Owner's overnight mandate: fly it, crew it, ready the map for play. Baseline save:
**EXPERIMENTAL_shipprint_2026-09-09.rws** (V28 content + A4 spur clear + the printed
ship at footprint 143,59,86,133 on the colony map, tile 16869).
1. Game-up (FOUNDRY owns the relaunch) → `rimflow bridge take` → load EXPERIMENTAL save.
2. ⚠️ Re-read faction with the RIGHT field: `list_things` returns **`faction`**, not
   `factionName` — the "everything factionless" reading was my wrong key. If truly
   unclaimed: per-cell Claim designator id
   `architect-designator:orders:highlight-designator-tutortagnotset-7` (cell apply only).
3. Clear the rocks: `destroy_batch` chunks/outcrops in and beside the footprint (the
   pre-clear sweep I owed — owner saw rocks right of the ship).
4. Build `PilotConsole` (vanilla Odyssey def — the layout ships none) on powered
   substructure near the engine (187,150); conduit if needed.
5. Fuel: fill the 2 ChemfuelTanks (dev refuel route), verify thruster pipe nets see it.
6. Engine inspection by a colonist (order a pawn; gate is upstream of everything).
7. Crew: apply `Transient/final_review/crew_spec.json` — remove the 3 test colonists,
   spawn + author the Five Founders aboard (fidelity scope, characterful not optimal).
8. Pre-flight save (the landing chain can wedge — no retry exists).
9. Launch → target tile 17007 → land; the map generates with the Zeddo ruin-field
   mutators. 10. Ready-for-play pass + CANONICAL save.
