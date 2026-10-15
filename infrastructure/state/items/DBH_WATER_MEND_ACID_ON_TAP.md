# DBH_WATER_MEND_ACID_ON_TAP

FlowWorks: DBH tags on hazardous liquids, full DBH unsupported, bucket water value

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C9-F4** CONFIRMED MEDIUM — Acid, propane, tar, slime and poisoned-water terrains all carry DBH's dbh_water tag. 19 liquid TerrainDefs (e.g. Defs/LiquidTypes/TerrainDefs/RM_AcidWater.xml, 2 hits) inherit vanilla water tags; Tools/generate_liquid_suite.py:595-597 says it does no per-liquid filtering. With DBH, hazardous liquids become wash/drink sources.
- **C9-F5** CONFIRMED LOW — DBH water value of a bucket is fixed 5 while material scales its contents (metal 6, leather 4). Patches/LiquidTypes/RM_DBH_FreshWaterDrinkables.xml <water>5</water> vs capacityFactor 1.2/0.8 in RM_LiquidBottles_Base.xml.
- **C9-F6** CONFIRMED MEDIUM — DBH integration only fires for 'Dubs Bad Hygiene Lite'; full DBH gets none. Patches/LiquidTypes/RM_DBH_WaterTerrainTag.xml:12 and RM_DBH_FreshWaterDrinkables.xml:15 FindMod 'Dubs Bad Hygiene Lite' only; Defs/ManyWaters/ThingDefs/RM_ColoredWaterBottles.xml MayRequire Dubwise.DubsBadHygiene.Lite only.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
