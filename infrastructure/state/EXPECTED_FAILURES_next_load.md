# Decision strings — the load of 2026-09-07 (GravTide + the three seas)

Written BEFORE launching, per `rimworld-load-round` §2. A signature invented
after reading the log is a story that fits, not evidence.

## What is riding this load

1. **`gravtide.mod` activated** — 598 → **599** active mods, inserted at index
   172 (after `brrainz.harmony` @1 and `ludeon.rimworld.odyssey` @9, before the
   `mandrake.*` block).
2. **Four new sea BiomeDefs parsed for the first time** — `RUT_TheScald`,
   `RUT_GreySea`, `RUT_TwilightSea`, `RUT_PropaneLake`, each now carrying
   `terrainsByFertility`, `baseWeatherCommonalities`, `wildAnimalsCanWanderInto`.
3. **Assemblies deployed in the shutdown window**, incl.
   `RimMandrakeVisibility.dll`.

## The strings that settle each one

| # | claim | string / check | baseline |
|---|---|---|---|
| 1 | GravTide loaded, not dead | `harvest_log.py` DEAD MODS (static ctor / type load) | **0**; any hit naming GravTide = it did not load |
| 2 | the four sea defs parsed | `jawa/world_tile_get` on a Scald tile returns `biome: RUT_TheScald`, **not `Lake`** | today it returns `Lake` |
| 3 | no def was silently discarded | `harvest_log.py` DEFS DISCARDED | **0** — any hit is NEW, read the file it names |
| 4 | the seas' terrain resolves | `Player.log` must NOT contain `No terrain found in biome` for any `RUT_*` | absent |
| 5 | weather resolves | must NOT contain `All weather commonalities were zero` for a `RUT_*` biome | absent |
| 6 | patch failures did not rise | `harvest_log.py` patch operations failed | **8** (5 pre-existing + 3 `[Jawa Armoury Rebalance]`, see `ARMOURY_PATCH_INNER_MISS_1`). GravTide may add its own — attribute before filing |
| 7 | config errors did not rise | `harvest_log.py` def ConfigErrors | **17** |
| 8 | cross-references clean | `harvest_log.py` cross-reference (def loader) | **0** |

⚠️ **Absence is necessary, not sufficient** (§2). #2 is the only
expected-PRESENT check here, and it is the one that actually proves the seas
exist. The rest are expected-absent.

## Then, and only if #1–#3 pass

- Load `WORLDMAP_V2_merged_2026-09-07`.
- `python.exe src/RimMandrake/Utils/w9_run.py --apply --load WORLDMAP_V2_merged_2026-09-07`
  — paints the **1135** sea tiles stage 1 skipped last run
  (`unknownBiomes` was `[RUT_TwilightSea, RUT_GreySea, RUT_TheScald]`).
- **Success condition:** stage 1 reports `applied=21872`, `unknownBiomes=[]`.
- Then re-export and diff against `world/ASHKARR_WORLDMAP_tiles.csv`:
  **expect 0 mismatches** (last run: 1135, all of them sea tiles).

## Also measure, do not assume

⚠️ **River link count discrepancy, open.** Last run imported 292 river links but
`world_links_validate` reported `riverEntries 634` (=317 links) over
`riverTiles 347` against our graph's 308. The import appears to ADD rather than
replace. **Measure it this load before deciding whether a `clearFirst` is owed.**
