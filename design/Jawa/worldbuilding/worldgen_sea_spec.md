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
| 4 | 🔴 **Bodies sit in the TERMINATOR BAND — mid-latitude** | **each body's centroid falls at latitude 0.35–0.65**, ⭐ **except one, which sits at high latitude on purpose** — see below |
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

### ✅ How the gate is READ — armed 2026-08-14, and it can be read BEFORE we commit

**`jawa/world_stats` reads FOUR of the seven requirements**, confirmed live in the
26-tool set: `tiles`, `pct`, `perimeter`, `raggedness` (perimeter²/tiles),
`centroidLat`, `bodiesTotal`, `bodiesOverMinSize` and the `minBodySize` passed in.
The "3-of-5 testable" caveat that used to sit against this gate was stale twice
over — it undercounted both the fields and the requirements they answer.

| req | read by | note |
|---|---|---|
| 1 · ~25% water | `pct` | |
| 2 · exactly three bodies | `bodiesTotal` **vs** `bodiesOverMinSize` | ⭐ **the gap between the two numbers IS the stray-tile test.** `3 / 3` passes; `47 / 3` is the fail this requirement was written for, and a percentage alone could never tell them apart |
| 3 · oddly shaped | `raggedness` | the compactness test, computed for us. Beat 25 |
| 4 · centroids in the terminator band | per-body `centroidLat` | including the one deliberate high-latitude body |

⭐ **The affordance that changes the process: a world merely being PREVIEWED at
the creation screen can be measured.** BRIDGE, 2026-08-14 — the call needs a world
loaded *or previewed*, and the main menu alone is not enough. ⇒ **We can reject a
candidate world at the preview screen instead of generating it, playing it, and
discovering the sea is round.** On a screen that is seen once, that is the
difference between a gate and a post-mortem.

**The three that are genuinely outside it, and why each is a different problem:**

| req | why no reader | disposition |
|---|---|---|
| 5 · elevation ≤ 0 **and** a water biome, per tile | a per-tile join the tool does not do — it reports `biomes` for land tiles only | 🔴 **requested of BRIDGE 2026-08-14, ranked third** behind `ideo_of` and `biome_probe`. It is the only remaining requirement whose failure is **visible to the player and unfixable after worldgen** — a tile written half-water reads as a desert square in the middle of the sea |
| 6 · deterministic from seed | needs *two* generations compared; one call cannot answer it | a process, not a tool. `seedString` ships, so the comparison is possible whenever we care |
| 7 · rivers terminate in our bodies | no reader at all | look at it once on a real world. Cheaper to see than to instrument |

🔴 **No candidate world is accepted on a partial pass, and four of seven is still
partial.** Requirement 5 in particular cannot be inferred from a good `pct` — a
world can score perfectly on water fraction while every claimed tile carries the
wrong biome.

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
> visual check shows three torn seas — two in the twilight band, one far out in
> the cold — with rivers running into them.**

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


---

## 🔴 TEST 4, IN FULL — corrected 2026-08-14, and read this before coding it

**Earlier versions of this file said "near a pole". That was wrong, and so was my
first correction. This is the settled version and it is self-contained — you should
not need any message to build test 4.**

### Why mid-latitude

**The planet is TIDALLY LOCKED.** `Alien Worlds - Tidally Locked` (ACTIVE) does not
build a day face and a night face geographically — **it remaps temperature onto
LATITUDE.** Its shipped curve:

| latitude | avg temp | what it is |
|---:|---:|---|
| 0.0 | **+70 °C** | the subsolar point — the burning dayside |
| 0.1 | +65 °C | |
| ⭐ **0.5** | ⭐ **+14 °C** | ⭐ **THE TERMINATOR.** The only band where water is neither boiled nor frozen |
| 1.0 | −37 °C | nightside |
| 1.3 | −70 °C | |
| 2.0 | −80 °C | deep night |

⇒ **Latitude IS the axis, and the terminator is a mid-latitude band.** Not the
equator. Not the poles.

### The test

1. **Two of the three bodies:** centroid at **latitude 0.35–0.65.**
2. ⭐ **The third sits at high latitude, deliberately off-pattern** — owner's
   instruction, *"one near the pole to make it feel really alien."* **On this
   planet that means a sea out on the nightside, freezing.** It is the strange one
   and it should look wrong.
3. ⛔ **NOT A RING.** Owner's explicit words: *"the ocean shouldn't literally be
   just a ring along the terminator, but they should lie NEAR it in natural
   elongated blob shapes."* **A band-shaped sea reads as a diagram.**
4. **Elongated.** Combined with the perimeter²/area ≥ 25 test, aim the growth
   along the latitude band rather than radially — **long and torn, not round and
   torn.**

⚠️ **This correction reached this file late.** It lived in messages and in
`tidally_locked_world.md` while the spec still said "near a pole" — **exactly the
failure the traps file now names: a correction that never reached the artefact
someone builds from.** If anything else here disagrees with a message, **this file
wins** and tell me.
