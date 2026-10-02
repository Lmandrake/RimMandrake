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

## 2026-10-02 additions (Fever Wood)

`FEVERWOOD_SCORING_SITTING_1` turn 1 (decision taken by question card 2026-10-02 11:12 PDT): **fix the free
mod's ten `RUT_`-prefixed defs**, which the 2026-10-01 scores doc missed
(`feverwood_bedazzle_review_2026-10-02.md` §1):
- **(c) Fever Wood, rename `RUT_` → `RM_` in place** (they are the free biome's own content, like the Sump's
  dusk, so moving them to the campaign layer would strip the free biome): `RUT_FeverWoodMirrorPool`,
  `RUT_Boughway`, `RUT_BoughSoil`, `RUT_StiltPlatform`, `RUT_FeverTrunkCore`, `RUT_FeverTrunkHeartwood`,
  `RUT_FeverWood_MirrorBreak`, `RUT_FeverWood_MirrorList`, `RUT_GenStep_GroundRefusal`,
  `RUT_GenStep_ScatterPools` (files under `src/RimMandrake/FeverWood/Defs/`, several named `RUT_*.xml`), with
  every reference (`RM_FeverWood.xml`, C# string lookups, `RM_LurkingWaterExtension` pool lists,
  `PlantGrowthConfig.cs`, the frozen twin `RUT_FeverWood.xml` if it names them, patches) in the same change.
  Also in the free kit: the C# `RUT_HaulPawnAndExit` (and its JobDef, if `RUT_`-named) in
  `mandrake.rm.environmentalhazards`. Placed terrain in saves: the world remake is the last step, so a save
  carrying the old names is not a blocker; if a keeper save must load, add `BackCompatibility`-style
  defName aliases rather than keeping the `RUT_` names.
- **(b) Fever Wood** above is unchanged and is now depended on by `FEVERWOOD_DIANOGA_GIANT_MAP_1`, which puts
  the canon facts the free text drops back in the campaign layer.
- verify, Fever Wood: offline parse finds no `<defName>RUT_` and no `"RUT_` string literal under
  `src/RimMandrake/FeverWood/` or `src/RimMandrake/EnvironmentalHazards/`; `jawa/get_defs` on the ten `RM_`
  names returns `foundCount` 10; `Player.log` has no `Could not resolve` naming any old or new name.

## 2026-10-02 additions (Weeping Stones)

`WEEPINGSTONES_SCORING_SITTING_1` turn 1 (`weepingstones_bedazzle_review_2026-10-02.md` §1 (b), §4 row 0): the
snow-strip and label ops in `src/RimUtinni/UtinniPatches/Patches/OasisMutator_DesertOasis.xml` target the donor
`ZBiome_DesertOasis` only. Harmless (the `RM_` def has neither problem); retire them with the donor. The whitelist and
palm ops in the same file are `WEEPINGSTONES_OASIS_MUTATOR_FLORA_1`'s, not this item's.
