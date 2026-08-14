# The sea step — build spec

_VISION, 2026-08-13. **v1, per PROJECT.** VISION specs, CREATE builds. Kill
condition: not demonstrably shaping a world within one working day → regenerate
with the sea as it comes and shaping becomes v2._

**Owner's ruling this implements:**

> *"A quarter ocean, split into three different bodies that are oddly shaped
> rather than round or reasonable. Only a few rivers flow from nearby mountains
> into these bodies."*

---

## What it is

**A `WorldGenStep` subclass, order ~20.** After `WorldGenStep_Terrain` (order 0),
**before `WorldGenStep_Lakes` (150) and the river step.**

⭐ **The order is the whole trick and it must not drift.** We do not build rivers.
We finish before vanilla builds them, so vanilla's river step flows into the seas
we just made. Proven in-stack: GravTide's `WorldGenStep_VolcanicBiome` writes
`info.PrimaryBiome` at order 20 in exactly this window.

## What must be true when it finishes

| # | requirement | acceptance test |
|---|---|---|
| 1 | **~25% of tiles are water** | count water tiles ÷ total. **Accept 22–28%** |
| 2 | **Exactly THREE connected bodies** | flood-fill the water set; **exactly 3 components** above a minimum size. Stray single tiles are a fail, not a rounding error |
| 3 | ⭐ **Each body is oddly shaped** | see the compactness test below |
| 4 | **Bodies sit at high latitude** | each body's centroid is nearer a pole than the equator |
| 5 | 🔴 **Elevation AND biome are both written** | every claimed tile has `elevation <= 0` **and** a water biome; every released tile has `elevation > 0` **and** a land biome |
| 6 | **Deterministic from the world seed** | same seed → same coastline, every time |
| 7 | **Rivers arrive afterwards** | the vanilla river step runs untouched and at least some rivers terminate in our bodies |

### ⭐ The compactness test — "oddly shaped", made measurable

**A circle has perimeter² / area = 4π ≈ 12.57. That is the number to beat.**

> **Every body must score at least 25 — i.e. twice as ragged as a circle of the
> same area.**

Perimeter = count of water tiles with at least one land neighbour. **This is the
one requirement most likely to be quietly failed**, because every natural
blob-growth algorithm trends toward round. If the score comes in at 13–15, the
step is producing exactly what the owner rejected.

⚠️ **Do not smooth the coastline.** A ragged frontier is the deliverable.

## What it must NOT do

- ⛔ **No coastline detailing, no per-body character, no shoreline biome art.**
  All v2, all explicitly out.
- ⛔ **Do not touch the land biome mix.** That is a separate ruling and the
  owner is still reviewing it. **This step decides where water is, and nothing
  else.**
- ⛔ **Do not adjust rivers or lakes.** Finish and get out of the way.
- ⛔ **No unbounded loops.** If the quota cannot be met, log the shortfall and
  stop. A worldgen that hangs is worse than a sea that is 21%.

## Notes that will save time

- **`SurfaceTile.WaterCovered` is `elevation <= 0`** — that is the whole sea-level
  rule, and there is no sea-level setting anywhere in vanilla.
- **`Ocean` is the Surface layer's `backgroundBiome`** and is `isBackgroundBiome`,
  so it is assigned by the elevation threshold, **not** by any biome worker.
  Biome-commonality mods cannot touch it.
- 🔴 **GravTide reads elevation, not the label.** A tile labelled `Ocean` while
  carrying land elevation looks like sea and behaves like ground — anything that
  goes underwater breaks on it. **Write both, always.**
- **Vanilla generates 43–55% ocean unaided**, measured across three real saves.
  **This step is mostly a REMOVAL job**, not an addition — expect to be raising
  elevation over most of the planet and lowering it in three places.

## Acceptance, in one line

> **Generate three worlds from three seeds. All three pass tests 1–6, and a
> visual check shows three torn seas near the poles with rivers running into
> them.**
