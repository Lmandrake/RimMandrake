## spec
✅ **DECIDE has cast all 25 biomes.** Owner, 2026-08-22, going AFK: *"Go ahead and just
allocate creatures around the biomes... Just take a first whack and get through it all. Go as
far as you can in preparation for game load."*

**The deliverable is `design/Jawa/fauna/BiomeCast_Ashkarr.xml`** — 25 `PatchOperationReplace`
operations, **725 `BiomeAnimalRecord`s**, generated from `cast_assignment.csv`.
⚠️ **It is a PROPOSAL under `design/`, not a deployed mod file.** BUILD owns whether and how
it ships.

## what it does
Replaces each biome's `wildAnimals` wholesale. The shipped lists carry ~1,024 records of
which almost all sit at **commonality 0**; the replacement carries the ~29 actually cast.

| | |
|---|---|
| assignments | **725** across 25 biomes |
| distinct creatures used | **652** of 979 eligible |
| appear in exactly ONE biome | **581** |
| appear in 2–3 | 71 |
| 🔑 appear in 4+ | **0** — the ubiquity the owner objected to is gone |
| ⭐ dormant creatures brought to life | **458** |

**The pyramid, per biome:** 4 tiny · 8 small · 8 med · 5 large · 3 huge · **1 super-huge**,
at commonalities 1.0 / 0.7 / 0.4 / 0.18 / 0.07 / **0.012**. Every biome filled every slot;
**no creature needed enlarging** to fill a SUPER gap.

## 🔴 BUILD MUST DO THREE THINGS BEFORE THIS SHIPS
1. **Wrap the operations.** `validate_patch.py` returns **0 errors, 25 warnings**: every
   `PatchOperationReplace` is unwrapped. If a target mod is absent this logs a red error every
   launch. Wrap in `PatchOperationConditional` / `PatchOperationFindMod`.
2. **Re-validate with `--defs`.** Static checks only were run. *"no --defs given"* means an
   xpath that matches nothing would pass silently — the most common failure mode there is.
3. **Confirm the `MayRequire` packageIds.** Generated from the dump's `packageId`; vanilla
   biomes are deliberately left unwrapped.

## ⚠️ four exclusion classes, each found only after reaching a generated patch
| excluded | n | why |
|---|---|---|
| mechanoid flesh | 93 | not fauna |
| **sessile** (`doesntMove`) | 37 | 🔴 a thing that cannot move is not wildlife. `fleshmass nucleus` and `nociosphere` reached the patch as roaming fauna because the anomaly branch was tested first |
| **lifecycle stages** (larva/pupa/nymph/clutch) | 31 | 🔴 a pupa is a STAGE, not a population — the adult spawns it |
| **dryads** | 8 | bound to a Gauranlen tree; a wild dryad is meaningless |
| vehicles / automatons | 8 | not fauna |

## the anomaly carve-out, as ruled
**12 placements across 3 of the 4 licensed biomes** — `AB_GelatinousSuperorganism` (6),
`Scarlands` (5), `HorrorWastes` (1). `AB_OcularForest` drew none; at **3 tiles** it is too
small to matter. ⛔ No anomaly entity appears anywhere else.

## what is NOT done, honestly
- ⛔ **The shrink-for-bad-art call cannot be made from what exists.** Every sprite was
  downscaled to 128px at extraction, so pixel counts measure silhouette fill, not resolution,
  and the manifests did not record source dimensions. **It needs either a re-extraction that
  records original size, or a human looking.** `CREATURE_ART_REVIEW_FLAGS_1`.
- **Commonality is by size band, not tuned per creature** — `CREATURE_DENSITY_PER_TILE_1`.
- **No combat normalisation, no diet/temperature repair** — those are the next two items and
  the cast deliberately ignored existing stats, as the owner instructed.
- **`animalDensity` per biome is untouched.** `AB_RockyCrags` still runs 1.8 over what is now
  a 29-creature cast rather than 14, which should already read very differently.

## verify
`validate_patch.py --defs` clean; then in game, spawn each biome and confirm the cast is the
one listed, that the super-huge is genuinely rare, and that no creature turns up everywhere.
