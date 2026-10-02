# BIOME_TIER_CLEANUP_1 — tier cleanup found by the grandfathered bedazzle scoring

Decision taken by question card (owner, 2026-10-01): one FOUNDRY item for all three. Source and evidence:
`design/Jawa/worldbuilding/biomes/grandfathered_bedazzle_scores_2026-10-01.md` (cross-cutting findings). Needs a load to prove.

## (a) Move twin-only features onto the `RM_` biomes, so the repaint does not lose them
- **Greentide** roil (steam-fog) and wet-bulb locks: `src/RimUtinni/UtinniPatches/Patches/RUT_RoilLock_BiomeWiring.xml`,
  `RUT_GreentideWetBulbLock_BiomeWiring.xml`, weather `RUT_RoilWeather` (overlay C# is already free: `RM_WeatherOverlay_GreentideRoil.cs`). Target `RM_Greentide`.
- **Webwork** web front: `RM_FrontCreepExtension` on the twin `RUT_Webwork` only; the free def leaves it off at `RM_Webwork_Biome.xml` l.26 pending `WEBWORK_WEB_STRUCTURES_1`. Target `RM_Webwork`.

## (b) Scrub Star Wars IP from free-tier text
- The Rot: `RM_PaleTree` description says "a faint, tugging sense of the Force".
- Fever Wood: "canon dianoga" in `RM_SekkulaathSpleenChemicals`, `_Snare`, `_Lash`, `_Sentinel`.
- Slime: gene names `RM_Gene_B2_VestigialLekku`, `RM_Gene_B4_BanthaSnore`, `RM_Gene_B12_StartleJawaese` (rename with every reference).

## (c) Move `RUT_`-prefixed defs out of the free mods into the campaign layer
- The Sump: `RUT_SumpWeather`, `RUT_SumpDuskLock`, `RUT_TarPitBelch`, `RUT_GenStep_*`.
- Miasma: weather, conditions, hediffs, gensteps (`RUT_MiasmaWeather`, `RUT_MiasmaWeatherLock` inline in `RM_Miasma.xml` l.104, `RUT_SurgeWeather`, `RUT_GenStep_*`, `RUT_FeverForged_*`).
- Rust Cathedral: many `RUT_` defs, e.g. `RUT_LivingBolt` inline in the free def, `RUT_HumLayer*`.
- Lantern Deeps: `RUT_DeepHum` in `RM_DeepAmbience.xml`.
Note for the Sump: `RM_TheSump` already lists `RUT_SumpDuskLock` in its own `biomeMapConditions`, so its dusk is free content under a campaign prefix. Moving those defs to the campaign layer would strip the free biome's dusk; renaming them `RM_` keeps it (`sump_bedazzle_review_2026-10-01.md` §1).

## verify
- Load proves each feature still fires on the `RM_` biome; `Player.log` clean of unresolved refs after the gene renames.
- No `Force`, `dianoga`, `Lekku`, `Bantha` or `Jawaese` remains under any `RM_` mod's text/defNames.
- No `RUT_` def under `src/RimMandrake/`.
