# NIGHTSIDE_ICE_DEF_1 — author RUT_NightsideIce and paint the deep-night highland

Owner ruling 2026-09-06 (`nightside_ice.md` §0): our own def, not a patch of vanilla
`IceSheet`.

## spec
- `RUT_NightsideIce` BiomeDef inheriting vanilla `IceSheet`'s shape (terrain `Ice`, no
  roads, no rivers, `isExtremeBiome`, `allowFarmingCamps false`) and OVERRIDING every
  list: no `wildAnimals` (the arctic zoo is evicted), no `coastalWildAnimals`, no
  `fishTypes`, weather = Clear-with-aurora as the standing state plus the ruled
  margin-only ablation/rime-fall (no snow/blizzard on the interior), `plantDensity 0`,
  `forageability 0`, disease list per the freeze review. Label "nightside ice". Naming
  per the tier grammar (`RUT_` — the fixed world is campaign-specific).
- Paint its 802 tiles (MEASURED: ring highland sectors 1–3 + former crystal caverns'
  tiles ≥ 900 m + vanilla IceSheet's 49) as part of `HORRORWASTES_BIOME_DISSOLVE_1`'s
  mosaic; add the def to the world tools' biome list; render for the owner before
  painting; re-freeze the savegame.
- 🔴 Anti-bullseye: highland lobes across ten sectors are accepted as topography
  (owner); document the sector census on the item when painted.
- Roster (tunnelers, icy insects) and events (thaw pulse, calving delivery, the lost
  soul) are separate authoring — this item is the def and the paint only.

## verify
`RUT_NightsideIce` resolves in the dump; CSV re-count = 802 on the ruled tiles and 0
vanilla `IceSheet` tiles remain; savegame re-frozen; render reviewed by the owner.
