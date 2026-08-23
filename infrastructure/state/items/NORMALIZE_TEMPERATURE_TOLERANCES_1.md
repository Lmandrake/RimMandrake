
## spec
🔴 **OWNER, 2026-08-23, verbatim:** *"We can set the appropriate temperatures later, don't worry
about that as a constraint… please put a specific item to 'normalize the temperature tolerances
of all xenotypes, animals, and plants' into BUILD's queue."*

**Why it exists.** Ash'karr is tidally locked and its ground runs **−82.0 °C to +66.1 °C** —
measured across all 21,872 tiles. Nothing shipped by any mod was authored for that range, so
every roster we write is currently gated by tolerances that describe a normal planet:

| | shipped reality, MEASURED 2026-08-23 |
|---|---|
| plants | **642 of 669** have `minGrowthTemperature` **0.0 °C**. Only **19** go below zero — 5 Alpha Biomes crystal/rime plants at −60, 13 Biomes! Caverns fungi at −50, one at −45. **593 of 669** cap at `maxGrowthTemperature` 58.0 |
| ground that defeats them | `AB_RockyCrags` median **−45.3**, `AB_PropaneLakes` median **−59.8**, `HorrorWastes` median **−49.3**, `BMT_CrystalCaverns` median **−62.4** · at the other end `ExtremeDesert` median **48.2** and max **66.1**, `AB_MechanoidIntrusion` median **62.5** |
| animals | the same shape — `HorrorWastes`' three shipped animals are all comfy 0–40 °C on ground at −49 |

⇒ **Roughly half the planet is outside the tolerance band of almost everything installed.** The
symptom is silent: a plant below `minGrowthTemperature` does not grow and logs nothing, so a
correct roster produces bare ground and reads as a bad roster.

🔑 **This is a NORMALIZATION pass, not a per-def fix.** The question is what the tolerance
bands should be for a world with these extremes, then a patch that moves every plant, animal
and xenotype onto them — not 669 hand edits.

⛔ **It does NOT gate the flora rosters.** The owner ruled temperature is not a constraint on
that work, so `BIOME_FLORA_ROSTERS_1` assigns by look and lore and this item makes them live.

## verify
Pick one biome at each extreme — `AB_PropaneLakes` (−59.8) and `AB_MechanoidIntrusion` (+62.5)
— generate a map, and count living plants and surviving animals. **Bare ground at a correct
roster is the failure this closes.**

## criteria
- [ ] A stated tolerance band, written down, that covers −82 … +66 °C.
- [ ] Plants, animals and xenotypes all moved onto it.
- [ ] A map at each extreme grows and holds life.

## Watch out
⚠️ **Three def families, three different field names** — plants use
`plant.minGrowthTemperature` / `maxGrowthTemperature`; animals use `statBases`
`ComfyTemperatureMin` / `ComfyTemperatureMax`; xenotypes carry theirs on **genes**, not on the
`XenotypeDef`. A patch written for one shape silently matches nothing on the others.
⚠️ **`PatchOperationReplace` that matches nothing is a RED ERROR, not a no-op.** Wrap in a
`Conditional` on the def; `MayRequire` only checks the MOD.
⚠️ **Do not widen tolerance to infinity.** Temperature is what makes the nightside hostile and
the dayside lethal; a world where everything survives everywhere has no climate.

---

## ⬅ STATUS 2026-08-23 — two thirds shipped, one third measured and filed

| leg | state |
|---|---|
| **plants** | ✅ `PlantTolerances_Ashkarr.xml`, 577 plants, deployed. 0 errors. |
| **animals** | ✅ `AnimalTolerances_Ashkarr.xml`, 456 cast animals, deployed. 0 errors. |
| **xenotypes** | 🔴 NOT DONE — measured and filed as `XENOTYPE_TOLERANCES_BAND_1` for DECIDE |

### ⚠️ A number in this item's own spec is wrong
This file reasons from *"a baseline human is roughly −17…+40 °C comfy"*. **That is a CLOTHED
human.** Measured from `ThingDef Human` `statBases`: baseline naked is comfy **16…26**, and
what actually matters is `SafeTemperatureRange`, which `GenTemperature.cs:86` defines as comfy
**±10** → safe **6…36**.

⇒ The real gap is **bigger** than this item implies: **88.0 °C short on cold**, 30.1 on heat,
and **34 of our 69 species carry no temperature-affecting gene at all**. Full measurement,
mechanism and the three candidate routes are in `XENOTYPE_TOLERANCES_BAND_1`.

🔑 **The remaining work is a DESIGN call, not a build one** — what band a person survives on
Ash'karr — and the owner's 2026-08-23 renormalization ruling puts that with DECIDE. BUILD
measured it and stopped there deliberately.
