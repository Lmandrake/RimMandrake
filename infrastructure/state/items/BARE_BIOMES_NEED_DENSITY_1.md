
## spec
`BIOME_FLORA_ROSTERS_1` assigned every biome a signature flora roster. **Two of them will not
be seen**, and the cause is `plantDensity`, not the roster:

| biome | tiles | share | `plantDensity` | roster assigned |
|---|---:|---:|---:|---:|
| `ExtremeDesert` | 3,214 | 14.7% | **0.008** | 4 |
| `Wasteland` | 1,721 | 7.9% | **0.0099** | 8 |
| | **4,935** | **22.6%** | | |

⚠️ **These are the SHIPPED values, deliberately untouched.** Density is a different lever from
roster — it feeds forage, wood supply and the fire ecology in `hydrology_and_fire_ecology.md`
— so this pass changed rosters only and filed the question rather than moving it quietly.

**The case for leaving both alone.** `ExtremeDesert` is the lethal core of the dayside (median
48.2 °C) and `Wasteland` is **contamination class** per `ASHKARR_WORLD_DEFINITION.md` §6c —
poisoned ground where *"the danger is the ground, the air, the water."* Near-sterile is the
honest reading of both, and a player crossing 4,935 tiles of genuinely dead land is a real
experience of this planet rather than a defect.

**The case for raising `Wasteland` only.** It is 7.9% of the planet with a roster of eight
toxic plants — toxigrass, gutter plantain, twisted dandelion, scorched stars — that exist to
say *this ground is poisoned*, and at 0.0099 they say nothing. ⭐ **Poisoned ground reads more
strongly with sick plants on it than with nothing.** `ExtremeDesert` has no such argument: its
four succulents are meant to be scarce.

🔑 **DECIDE's recommendation, for the owner:** raise `Wasteland` to about **0.12** — an order
of magnitude up, still visibly barren, enough that the toxic flora registers — and **leave
`ExtremeDesert` at 0.008**. One value, one biome, reversible in one line.

## verify
A map in each. `Wasteland` should read as sick ground with scattered growth, not as sand.
⚠️ Judge after `NORMALIZE_TEMPERATURE_TOLERANCES_1` lands — `Wasteland`'s median is 0.8 °C and
642 of 669 plants stop at 0.0 °C, so today it would read bare at any density.

## criteria
- [ ] A ruling on `Wasteland`'s density, and a stated reason for `ExtremeDesert`'s.

## Watch out
⚠️ **`plantDensity` feeds the fire ecology.** `hydrology_and_fire_ecology.md` R-H3 makes plant
growth the fuel for a savanna that burns; every plant added is fuel. Raising a 1,721-tile
biome's density is not a cosmetic change.

## 🔴 DECIDE'S RULING, 2026-08-23 — raise `Wasteland` to 0.12; `ExtremeDesert` stays at 0.008

⚠️ **Routing: this was filed `needs: owner` by me, and that was wrong.** It is
`kind: decision --for DECIDE`, and how much grows on a biome is a question about **the world**.
The owner's calls are cost, taste and the scope of v1. Ruled here.

**`Wasteland` → 0.12** (12× up, from 0.0099). 1,721 tiles of **contamination-class** ground
carrying an eight-plant toxic roster — toxigrass, tall toxigrass, gutter plantain, twisted
dandelion, scorched stars, rashroot, doomsprout, toxic ivy — that exists to say *this ground is
poisoned*. At 0.0099 it says nothing at all. ⭐ **Poisoned ground reads more strongly with sick
plants on it than with nothing**; empty sand reads as *desert*, not as *contaminated*. 0.12 is
still visibly barren — an order below `AridShrubland`'s 0.72 — and it is the whole point of the
biome becoming legible.

**`ExtremeDesert` stays at 0.008, and that is a RULING, not an oversight.** It is the lethal
core of the dayside, median **48.2 °C**, and its four succulents are *meant* to be scarce. A
player crossing 3,214 tiles of genuinely dead sand is experiencing the planet, not a defect.
🔑 The two biomes read as bare for opposite reasons: one is bare because nothing survives there,
which is true and should stay; the other is bare because a number hides a roster we wrote.

**Applied:** `design/Jawa/mods/biome_flora.py` now carries a `DENSITY` dict beside `PLANTLESS`
and emits the op into `BiomeFlora_Ashkarr.xml` (24 roster + 1 density). Validated `--live`,
0 errors; deployed and verified byte-identical.
⛔ **It is a named exception list, never a sweep.** Density feeds the fire ecology
(`hydrology_and_fire_ecology.md` R-H3 makes plant growth the fuel for a savanna that burns), so
every future entry needs its own reason written beside it, as this one has.

## verify
⏳ Needs a cold load. A `Wasteland` map should read as **sick ground with scattered growth**,
not as sand.
⚠️ **Judge it only after `NORMALIZE_TEMPERATURE_TOLERANCES_1`** — `Wasteland`'s median is
**0.8 °C** and 650 of 669 plants stop at 0.0 °C, so today it would read bare at any density.
