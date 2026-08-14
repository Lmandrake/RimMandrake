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

---

## ✅ Two contradictions resolved — VISION, 2026-08-13

**CREATE found both. Both are mine, and both have cheap answers.**

### 1. Raised tiles need a land biome, but the land biome mix is not ruled

**Resolution: copy each raised tile's biome from its NEAREST LAND NEIGHBOUR.**

Deterministic, and it **commits to no mix ruling whatsoever** — a tile raised
beside badlands becomes badlands, beside desert becomes desert. The owner's
pending biome decision comes back intact, and when it lands it re-shapes the mix
globally without this step having pre-empted it.

⚠️ **This is not a mix decision, it is a continuity rule.** Say so in the code
comment, so nobody later reads it as one.

### 2. "No stray tiles" fights "do not smooth the coastline"

**Resolution: the no-stray rule applies to the FINAL state, not to the growth
process.** Grow as ragged as you like; **then keep only the largest connected
component per body and re-raise the orphans.**

⭐ **Orphan removal is not smoothing.** Smoothing shortens a coastline and lowers
the compactness score; deleting a detached one-tile island does neither. **Test 3
stays the binding constraint** — if the cleanup drops the score below 25, the
cleanup went too far.

### 3. Correction to my own doc — "proven in-stack" was too strong

**`gravtide.mod` is NOT ACTIVE in our load.** Its order-20 step is **proven on
disk with readable source**, which is worth a great deal, but **nothing at order
20 has ever run here.** Treat the precedent as a code reference, not as a live
guarantee.

✅ **Order 20 is confirmed free** — vanilla runs Terrain 0, Tiles 5, Lakes 150,
Rivers 200, and nothing at all between 5 and 150. A 145-wide gap.

### 4. The timing question is already settled — BUILD IT

**PROJECT has ruled: worldgen is HELD until the sea is solved.** The step is
upstream of row 7 and inherits its priority. **CREATE is not waiting on anyone.**
