## spec
🔴 **OWNER'S BRIEF, 2026-08-22 13:33 — the fauna pass is v1 and it is NOW.** Verbatim:
*"move the animal assignment task to v1 and right now… This is exciting! The biomes are
pretty much frozen right now as are the animals, so it's a good time for this."*

⭐ **Worked WITH the owner, not for him.** He asked for these as items *"to work through with
me now"*. Bring him decisions to react to, never a questionnaire.

### The measured starting state (578-mod dump, 2026-08-22)
| | |
|---|---|
| animal `ThingDef`s installed (intelligence `Animal`) | **2,042** |
| that can spawn anywhere on Ash'karr | **377** |
| 🔴 reach **no biome at all** | **1,665 — 82% of what we ship** |
| animals with no explicit `ComfyTemperatureMin` | **1,015 of 2,042** |

🔑 **The mechanism, so nobody invents one.** Every `BiomeDef.wildAnimals` **already lists all
1,024 candidates** as `BiomeAnimalRecord`s; assignment is the `commonality` number and most
sit at **0** (never). ⇒ This is **re-weighting an existing table in XML**, not new content.
⚠️ **Never count `wildAnimals` entries** — every biome returns 1,024 and the number is
meaningless. Count `commonality > 0`.

## the job — how OFTEN each creature appears
**Owner, 2026-08-22:** *"it's then time to decide on their frequency/density in the tiles."*

⛔ **Blocked on `BIOME_CREATURE_CAST_1`** — you cannot weight a cast that has not been chosen.

Two knobs, and they are not the same:
- **`BiomeAnimalRecord.commonality`** — the *relative* chance of this creature versus the
  others in that biome. This is where the size pyramid becomes real: the super-huge gets a
  tiny commonality, the many-small get large ones.
- **`BiomeDef.animalDensity`** — how much wildlife the biome carries *in total*.

⚠️ **The current densities are already uneven and some look wrong against the cast.**
`AB_RockyCrags` runs **1.8 with only 14 animals** — high density over a tiny cast is exactly
what makes a biome feel repetitive. `AB_MiasmicMangrove` 6.5 · `BMT_FungalForest` 4.25 ·
`AB_FeraliskInfestedJungle` 5.4 · `ExtremeDesert` and `Wasteland` **0.1** · `Volcano` 0.25.
🔑 **A desert reading as empty is correct; a desert reading as repetitive is not.** Density
and cast size have to be set against each other, not independently.

## verify
The super-huge is genuinely rare in play; no biome repeats one creature; density reads as
sparse where the fiction wants sparse.

## criteria
Commonality per (creature, biome) and a reviewed `animalDensity` per biome.
