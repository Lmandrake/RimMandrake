# FORGE_SKY_PASTURES_1 — sky pastures

Split from `FORGE_GPT_ENRICHMENT_1` §5 (owner-picked).

## already built (checked 2026-10-01)

`RM_MapComponent_VaporColumns` and `RM_CompVaporDrifter` (EnvironmentalHazards), with `RM_JobGiver_ColumnWander`.
The drifter comp is already on `RM_FleetFlier` and `RM_Jossur`. The jossur already has real 1.6 flight stats
(`MaxFlightTime` 20); its flight frames are `JOSSUR_FLIGHT_FRAMES_1`.

## owed

1. Render the column grid: ash spiralling upward in the columns (flecks).
2. Column-aware hunting for the jossur, with real flying stoops on prey.
3. Selecting a flier highlights the useful columns, with no permanent overlay.

All of this is EnvironmentalHazards work, in a shared assembly. It was not built in the parent because another
agent had a biome item open on that assembly at the same time.

## open question (owner)

The spec says "the aerofleets, beldons, fleet fliers and admitted giants congregate there". Beldons are campaign
tier (`RSW_Beldon`, Utinni patch), and "aerofleets" and "admitted giants" name no def in this mod. Which defs are
these, and do the RM-tier pastures carry only the fleet flier and the jossur?
