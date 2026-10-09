# DEEP_DRILL_HOME_BIOME_1

## spec

Decision taken by question card 2026-10-03 and again 2026-10-09 (minerals design §7 Q4, option A): deep drilling finds iron everywhere; every other deep deposit only in its home biome. One small code change: Harmony postfix on `CompDeepScanner.ChooseLumpThingDef` filtering by `map.Biome` against the mineral allocation (design §6 W3; allocation data from `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`).

## criteria

- L0: selftest — on a biome with no home deposits, chosen lumps are only steel; on a home biome, its deposits can be chosen.
