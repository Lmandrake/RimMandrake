# PROPANELAKE_ANIMALDENSITY_ZERO_1 — six authored animals that can never spawn

Found 2026-09-26 by BENCH while discharging the long-open "do `<wildAnimals>` spawn on an
impassable water biome" question before the three sea sittings.

## the defect

| def | `animalDensity` | inline animals | can they spawn? |
|---|---|---|---|
| `RM_PropaneLake` | **UNSET** | 6 | **No. Ever.** |
| `RUT_PropaneLake` | **UNSET** | 3 | **No. Ever.** |
| `RM_GreySea` | 0.1 | 6 | yes |
| `RM_TwilightSea` | 0.1 | 6 | yes |
| `RM_TheScald` | 0.15 | 3 inline + 3 canon patch-added | yes |

The Propane Lake's authored floor cast is `AA_AuroraSylph`, `AA_Skyeel`, `RM_Vaunoom`,
`RM_Heemin`, `RM_Oovanam`, `RM_Hoolen`. None of them will appear.

## why — MEASURED from the decompiled engine, not inferred

`BiomeDef` declares `public float animalDensity;` with **no initializer**, so an absent
tag is `0f`, not a default.

In `WildAnimalSpawner`:
- `DesiredAnimalDensity` starts from `map.TileInfo.AnimalDensity` and multiplies through.
- `DesiredTotalAnimalWeight` returns **0 immediately** when that density is `0f`.
- `AnimalEcosystemFull => CurrentTotalAnimalWeight >= DesiredTotalAnimalWeight` is
  therefore **true from tick zero**.
- `GenStep_Animals.Generate` loops `while (!AnimalEcosystemFull)` — it runs **zero
  iterations**. `WildAnimalSpawnerTick` is likewise gated behind `!AnimalEcosystemFull`.

⇒ Nothing spawns at map generation and nothing spawns later. The roster is inert.

## 🔑 `impassable` was never the gate — that question is closed

The long-standing note said this was an engine question about impassable water biomes and
was UNMEASURABLE off the Desktop. It is now measured, and the premise was wrong:
**nothing in `GenStep_Animals` or `WildAnimalSpawner` reads `impassable` at all.** The
real gates are `animalDensity > 0` and — for ongoing (not map-gen) spawns — a walkable
cell satisfying `CanReachMapEdge`.

⇒ So the Scald's floor animals were never "somebody's bet": they work because the Scald
sets `animalDensity` to 0.15. And the other seas needed nothing proven before authoring —
they needed this one field checked.

## the fix

Set `animalDensity` on both Propane Lake defs. ⚠️ **Do not copy 0.1 unthinkingly** — pick
it against the fiction. A lake of liquid propane should plausibly be the *sparsest* of the
four seas, so a value at or below the Grey Sea's 0.1 is the likely call, but it is a design
number and belongs to the Propane Lake's floor pass (`PROPANELAKE_FLOOR_PASS_1`), not to
whoever fixes the field.

## the second question this raises, and it is worth answering once

`DesiredAnimalDensity` reads `map.TileInfo.AnimalDensity` — the **tile's**, not the def's
directly. For a sea floor reached by diving rather than by settling the tile, confirm which
tile the pocket map inherits its `AnimalDensity` from before calling this fixed. A correct
`animalDensity` on a def that the floor map never consults would read as fixed and still
spawn nothing.

## criteria
- [ ] `animalDensity` set on `RM_PropaneLake` and `RUT_PropaneLake`, value chosen by the
      floor pass rather than copied.
- [ ] Confirmed which tile a dive-generated floor map takes `AnimalDensity` from.
- [ ] A sweep of every one of our BiomeDefs for an unset `animalDensity` with a non-empty
      `wildAnimals` — the Propane Lake is unlikely to be the only one.

## ⚠️ trap for whoever measures this
Parse `<wildAnimals>` as an XML element and count its CHILDREN. `BiomeAnimalRecord` uses a
custom loader with **no `<li>`** — `<RM_Hoolen>0.4</RM_Hoolen>`. Counting `<li>` returns
**0 for a fully populated roster**, which happened twice in this session's first two passes.
