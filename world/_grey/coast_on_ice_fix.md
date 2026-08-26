# `Coast` on a sea-ice shore is illegal, and the audit's default scope is the only thing that catches it

**Measured 2026-08-26, after the Grey Sea passes.**

The Grey Sea pass wrote `Coast` onto 47 ring tiles. **Eleven of them border the sea only
through `SeaIce`** — and RimWorld's `World.CoastDirectionAt` recognises **`Ocean` only**, so a
tile whose every water neighbour is sea ice is *not* coastal by the engine's reckoning. The
`Coast` marker there is an illegal placement: it lands, reports success, and then misbehaves.

```
2910  AridShrubland   water neighbours: SeaIce ×4
6899  ZBiome_Badlands water neighbours: SeaIce
9986  Desert          water neighbours: SeaIce
…11 in total, every one written this session
```

All 11 removed. `jawa/world_mutators_audit` → `offenderCount 0`.

## Two traps this exposed

🔴 **The audit's `marineChecked` scope is `['Coast']` by DEFAULT, and widening it invents
offenders.** The implementing agent widened the scope to `VEE_RisingWaters, Archipelago,
Iceberg` and got `offenderCount: 33` — a number that mixed 15 unrelated pre-existing
placements elsewhere on the planet with its own. An earlier agent widened it to include
`VEE_SaltPlains`, which flagged **313** unrelated placements and auto-removed **50** before
anyone noticed. ✅ **Run the audit at its default scope and treat a non-zero count as real.**
⛔ Never bulk auto-remove what an audit flags.

🔑 **The same blind spot has now been seen three times**: `CoastDirectionAt` counts `Ocean`
and nothing else, so a shore of `SeaIce` — and, on the Scald, a shore of `Lake` — reads as
landlocked. Any coastline-gated def (`Coast`, `VEE_RisingWaters`, `Archipelago`, `Bay`,
`CoastalIsland`, `VEE_GravelBeach`, `VEE_MarineSanctuary`) placed against ice or lake is
placed against a coast the engine does not believe in.
