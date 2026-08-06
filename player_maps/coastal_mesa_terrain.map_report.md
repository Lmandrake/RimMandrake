# coastal_mesa — terrain-modification agent report

Every edit below was applied to the SEMANTIC TERRAIN GRID (cells = terrain names), driven by the hand-reasoned decisions in `authored/coastal_mesa_rationale.md`. Terrain only; plants/props are a later phase.

## Edits applied (in dependency order)

| # | Decision | Cells changed |
|---|---|---|
| 1 | Ocean coastline meander (headland N / cove mid / point S) | 224 |
| 2 | Water depth grade (shallow near shore -> deep offshore) | 340 |
| 3 | Beach ribbon + offshore sandbar in the cove | 121 |
| 4 | Dry wash (arroyo) SW->NE across the sand flat | 200 |
| 5 | Fertile hollow (SoilRich core) at the wash bend = farm start | 63 |
| 6 | Scrub-stand ground (MossyTerrain) clustered along the wash | 39 |
| 7 | Outcrop knoll (mid-map high ground) | 89 |
| 8 | Cavern chamber + throat carved into massif SE face | 109 |
| 9 | Talus/scree apron at the massif's west foot | 6 |
| 10 | Crashed Factory-ship scar (scorched furrow + hull footprint + debris) | 157 |
| 11 | Abandoned mine adit + gravel tailings fan (massif W flank) | 21 |
| 12 | Refinery ancient-concrete pad + ruptured-tank spill stain (SE) | 129 |
| 13 | Dead-droid impact crater (bowl + rim + scorch streak) | 45 |

## Terrain histogram: before -> after (cells)

| Terrain | Before | After | Δ |
|---|---:|---:|---:|
| Sand | 5030 | 4884 | -146 |
| RockRubble | 2991 | 2945 | -46 |
| WaterOceanShallow | 1440 | 1622 | +182 |
| RockFace | 1558 | 1468 | -90 |
| SoftSand | 925 | 1029 | +104 |
| Gravel | 1256 | 1011 | -245 |
| WaterOceanDeep | 1200 | 934 | -266 |
| AB_SolidifiedLava | 0 | 118 | +118 |
| CaveFloor | 0 | 112 | +112 |
| AncientConcrete | 0 | 94 | +94 |
| Soil | 0 | 41 | +41 |
| MossyTerrain | 0 | 39 | +39 |
| Mud | 0 | 30 | +30 |
| MetalTile | 0 | 26 | +26 |
| AB_VolcanicGravel | 0 | 23 | +23 |
| AB_ForsakenRock | 0 | 13 | +13 |
| SoilRich | 0 | 11 | +11 |

## Guardrail metrics: before -> after

| Metric | Before | After |
|---|---:|---:|
| transition_coherence | 1.0 | 0.9925 |
| fragmentation_tiny_patches | 7 | 20 |
| family_diversity | 0.9211 | 0.65 |

## Verification — did each decision land in the grid?

| Decision | Present? | Evidence |
|---|:---:|---|
| Depth-graded water (deep + shallow both present) | ✅ | deep=934 shallow=1622 |
| Fertile hollow (SoilRich core) | ✅ | SoilRich=11 Soil=41 |
| Cavern (CaveFloor carved in rock) | ✅ | CaveFloor=112 |
| Scrub-stand ground (MossyTerrain) | ✅ | MossyTerrain=39 |
| Outcrop knoll (ForsakenRock core) | ✅ | AB_ForsakenRock=13 |
| Crashed-ship scar (scorched ground) | ✅ | AB_SolidifiedLava=118 |
| Ship hull / droid metal footprint | ✅ | MetalTile=26 |
| Refinery concrete pad | ✅ | AncientConcrete=94 |
| Refinery/droid spill + crater scatter (Mud/VolcanicGravel) | ✅ | Mud=30 AB_VolcanicGravel=23 |
| Dry wash bed (SoftSand present as channel) | ✅ | SoftSand=1029 |

**All decisions present: YES ✅**
