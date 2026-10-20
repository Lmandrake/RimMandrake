# Paint inputs for the development world (G7)

The bundle `w9_run.py --inputs` stamps onto the new dev world (Option D: a DEVELOPMENT world, repaintable).
It is **not** the frozen record: `world/ASHKARR_WORLDMAP_*.csv` is untouched.

- **Source:** `world/rescue_2026-10-19/ported/`, the layers read from `CANONICAL_ASHKARR_START_2026-09-12.rws`
  by `world_layers_export.py`, names already through the historical renames and the retired-mutator port map.
- **Built by:** `python3 src/RimMandrake/Utils/paint_inputs_build.py` (rebuild = rerun; deterministic).
- **Remap table:** `design/RimMandrake/world_remake_2026-10-19/paint_inputs_remap.json`. Every PROVISIONAL row
  is a reversible agent default (owner asleep 2026-10-20); to undo one, edit the row and rerun the tool.
- **Resolution:** `RESOLVER.md` / `resolver.json` — every def name in every CSV here against the PAINT def
  closure (`ModsConfig.PAINT.RULED_2026-10-20.xml` × dump capture `2026-10-20T06-17-12Z`). **0 unresolved.**

## What changed from the source

| layer | change |
|---|---|
| tiles | 19,119 tiles: each frozen `RUT_` twin → its `RM_` survivor per `biome_paint_list.md` (25 pairs). Kept: `RUT_Umbra` ×2,531 (Auroral Umbra, owner 2026-10-19), `RM_Pyrelands` ×222 (the old `ZBiome_Grasslands` tiles). The 44 hash-56104 tiles are `RUT_TheForge` → `RM_TheForge` |
| settlements | `biome` column synced to the remapped tile (92 rows); faction defs already `RUT_Jawa_*` |
| mutators | the five unresolvable names (49 entries), table below; 24 tiles left with no mutator are dropped from the CSV |
| landmarks, links | unchanged (all resolve) |
| factions | 4 defs not on PAINT dropped (no settlement uses them), with their relation entries |
| features | the 71 labels: `WB_MapLabelFeature` → `Desert` (PROVISIONAL, below) |
| landforms | not copied: Geological Landforms names, no def type on the PAINT list, never stamped by w9 |

## Decisions that need the owner (PROVISIONAL defaults, all reversible)

| name | entries | default | why | to reverse |
|---|---|---|---|---|
| `AB_AncientDeathPallVent` | 33 | drop | **ruled** 2026-10-19: no zombies in Utinni | — |
| `AB_DerelictKemeticTemple` | 5 | → `AncientRuins` | no port (donor temple layout); nearest existing ancient structure | `"new": null` |
| `AB_DerelictBioLab` | 5 | → `AncientRuins` | no port (13 retired lab layouts) | `"new": null` |
| `AB_DerelictArchonexus` | 2 | → `RM_DerelictClusters` | no port (donor archotech art); our derelict-wreck site | `"new": null` |
| `WildDantooinePlants` | 4 | → `RSW_WildGalacticPlants` | no `RSW_` dantuber plant; generic SW wild plants | `"new": null` |
| factions `AM_EnemyPirate`, `TribalHostile`, `DP_GenericHostile`, `CASacrilegHunters` | 4 | dropped | defining mods not on PAINT (AM_EnemyPirate defined nowhere in the capture) | remove from `factions_drop` (and add the mod to PAINT) |
| region-label FeatureDef | 71 | `Desert` (Core) | `WB_MapLabelFeature` is Worldbuilder's, not on the ruled PAINT list; stage 6 imports labels under one def | set `WB_MapLabelFeature` and add `ferny.worldbuilder` to PAINT |

## Dry run

- `python3 src/RimMandrake/Utils/w9_run.py --inputs world/paint_inputs_2026-10-20 --check-inputs` → ok, offline
  (5 layers present, 21,872 distinct tiles, required columns; stage 6 def `Desert` read from the features CSV).
- The real dry run (`python.exe src/RimMandrake/Utils/w9_run.py --inputs world/paint_inputs_2026-10-20`) **needs the
  game**: it connects to the bridge and the live world. Not run (runbook S8, after S7).
- UNMEASURED: whether `jawa/world_features_import` accepts a Core FeatureDef for labels; whether `RM_FeverWood`,
  `RM_Wasteland`, `RM_WeepingStones` (`generatesNaturally=false`) behave once stamped — stamping does not consult it.
