# WORLDMAP_LIQUID_TAGS_1 — typed liquid bodies on the frozen world drive landing mapgen

Filed by BENCH, 2026-09-13 (owner ruling: typed tiles drive mapgen —
`design/RimMandrake/liquids_framework_design.md` §4 "Typed worldmap → mapgen").

## spec

Two halves. (1) AUTHORING: the planet's water tiles and named bodies carry a
liquid TAG — which `LiquidDef` row that body's water is — covering
`LIQUID_BIOMES_MAP_1`'s four authored bodies (boiling ocean, two brine seas,
propane lake); read through a WorldComponent keyed by tile ID. No worldgen, no
re-render. (2) MAPGEN: a GenStep reads the landing tile's tag and REPAINTS the
vanilla-generated shores/lakes to that row's terrain suite — paint-over of
generated terrain, untyped tiles untouched.

🔴 **The tags are DATA that ships in the mod, not a live write onto the frozen
world.** This replaces the filing's original "one bridge pass writes worldTag
onto the tiles, committed with `world_commit`", which two measurements ruled
out on 2026-09-19:

- **`jawa/world_tile_set` writes exactly seven vanilla scalars** — biome,
  elevation, hilliness, temperature, rainfall, swampiness, pollution. A world
  tile has no free metadata field, so "write a tag onto the tile" could only
  have been done by overwriting one of the seven hand-authored values on a
  frozen planet. That is the displaced-field regression this item's own
  `## Watch out` exists to prevent.
- **A WorldComponent dictionary is SAVE state.** It lives only inside a `.rws`,
  and `## verify` below forbids saving over the canonical start save — so a
  live-authored dictionary would have been discarded by the session that wrote
  it.

Deriving each tile's tag from `RM_LiquidBodyDef` rows has neither problem: the
frozen save gains its tags with zero bytes rewritten, an in-flight campaign
gets them on its next load, and a wrong tag is an XML edit rather than a bridge
session on a frozen planet.

🔑 **Ash'karr has no ordinary seas or lakes.** MEASURED 2026-09-19 against
`world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows, frozen 2026-09-07): all 1,448
water tiles on the planet are `RUT_TwilightSea` (607), `RUT_GreySea` (472),
`RUT_TheScald` (312) or `RUT_PropaneLake` (57). The last vanilla water was
removed 2026-09-07. So the filing's "plus the ordinary vanilla seas/lakes" set
is EMPTY and there is no fifth row to author.

## state — 2026-09-19, FOUNDRY

BUILT and committed at `91092390a`; **not deployed and not live-tested.**

Shipped in FlowWorks (`mandrake.rm.flowworks`), built clean, `validate_patch`
clean, 61/61 selftests:

- `Source/LiquidTypes/RM_LiquidBodyDef.cs` — a body row: one `LiquidDef`, plus
  the BiomeDef defNames (strings, so an absent campaign biome costs nothing)
  and/or explicit tile ids that belong to it.
- `Source/LiquidTypes/RM_WorldComponent_LiquidTags.cs` — the per-tile tag layer
  keyed by tile ID. **No `ExposeData` override, deliberately** — it derives from
  the defs each load and writes nothing to any save.
- `Source/LiquidTypes/RM_GenStep_LiquidShores.cs` — the landing repaint.
- `Defs/LiquidTypes/LiquidBodyDefs/RM_LiquidBodyRegistry.xml` — the four rows:
  Scald → `RM_Liquid_BoilingWater`, Twilight Sea and Grey Sea →
  `RM_Liquid_Brine`, Propane Lake → `RM_Liquid_Propane`.
- `Defs/LiquidTypes/GenStepDefs/RM_GenStep_LiquidShores.xml` — order **245**
  (after Terrain 210 / MutatorPostTerrain 220 / RemoveTinyIslands 240, before
  Roads 390).
- `Patches/LiquidTypes/RM_LiquidShores_MapGenPatch.xml` — adds it to
  `MapCommonBase`, the same self-gating shape `RUT_FungalSoilScatter` uses.
- Mod Settings: **"Landing repaints typed water"**, default ON.

What the repaint does and does not touch: it replaces the four STANDING-water
terrains the map's own biome would have produced (fresh deep/shallow, ocean
deep/shallow, resolved biome-field-first exactly as `MapGenUtility` does).
**Rivers are never repainted** — a river feeding a brine sea is still fresh —
and neither is shore sand or ice. On an untyped tile it reads the tag, gets
null and returns having touched nothing.

**NO live world write was made, and none is owed.** Backup taken first
(`jawa/world_tile_export`, read-only) and it showed the running game is not
Ash'karr: 119,904 tiles, seed `bluff`, **0% water, 0 water bodies**, only two
distinct (elevation, temperature, rainfall, hilliness) tuples across the whole
planet — a scratch world carrying the name and none of the data. Confirmed by
`jawa/world_stats` and by `jawa/world_tile_get` on three known Ash'karr tile
ids. Summary kept at
`Transient/WORLDMAP_LIQUID_TAGS_1/live_world_capture_2026-09-19.md`. Bridge
taken and released; nothing on the planet was altered.

## owed

1. **Deploy.** `deploy_custom_mods.py --mod FlowWorks --apply`. Blocked while
   the game runs — a companion/mod DLL cannot be written to the Mods folder
   with RimWorld holding it. ⛔ Do NOT deploy the XML alone: without the new
   assembly the `Class=` on the GenStepDef and the `RM_LiquidBodyDef` root
   nodes resolve to nothing and the defs are discarded with red errors.
2. **The `## verify` quicktest**, which has never run. It needs a world that
   actually has the four biomes on it — the canonical Ash'karr save — so it is
   a cold-load item, not a minimal-list one.

## verify

Read the tags back through `RM_WorldComponent_LiquidTags.TagForTile` on a tile
of each of the four bodies. Land a quicktest colony on a tagged tile: shores
read the row's TerrainDefs via `get_terrain`; land on an untyped tile:
byte-identical vanilla behavior. Save nothing over the canonical start save.

## Watch out

- 🔴 The world is frozen and hand-authored. This item no longer needs a world
  WRITE at all, and it should not acquire one: there is no tile field to write
  a tag into, so any future "just write it live" is an overwrite of authored
  data. One bridge driver at a time for the read half.
- The 100-row cap on every bridge world read — page, never trust one read.
  `jawa/world_tile_export` has no cap and is read-only; prefer it.
- Depends on LIQUID_REGISTRY_CORE_1 for the rows the tags name. Three rows
  carry a `worldTag` today (`RM_Liquid_BoilingWater`, `RM_Liquid_Brine`,
  `RM_Liquid_Propane`) and those are exactly the three the four bodies use.
- model: opus (frozen-world reads + mapgen GenStep C#).
