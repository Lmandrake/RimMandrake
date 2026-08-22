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

## the job — stop them dying on arrival
**Owner, 2026-08-22:** *"ensure things like their diets and temperature tolerances make sense
so they don't just die."*

⛔ **Blocked on `BIOME_CREATURE_CAST_1`.** 🔴 **This one has a hard deadline the others do
not: a creature that cannot survive its biome is not a bug you notice, it is a population
that quietly never appears.**

**Temperature.** 🔴 **1,015 of 2,042 animals carry no explicit `ComfyTemperatureMin`** and
inherit a default written for a temperate world. Ash'karr is tidally locked with a ruled
**+14 °C terminator gradient** (`ASHKARR_WORLD_DEFINITION.md` §2, and the endpoints are the
owner's own ruling). ⇒ **That default is wrong nearly everywhere**, and it is wrong in both
directions — the substellar waste and the nightside are different problems.
⚠️ **§2 owns the temperature model. An animal pass that disagrees with it produces animals
that die on arrival.** Read it before setting a single value.

**Diet.** A carnivore in a biome with no prey starves; a grazer in `ExtremeDesert` needs the
plant list to actually support it. 🔑 **The plant side is settled and current** — the owner
ruled 2026-08-22 that **no plant is cut** (192 reviewed, 0 removed), so the food base is known
and stable. Use `design/Jawa/mods/plant_cherrypick_candidates.csv`.

## verify
Spawn each cast creature in its biome and let it run: none starves, none freezes, none cooks.
The temperature values agree with §2 rather than contradicting it.

## criteria
Every cast creature survives its assigned biome at both temperature extremes and can eat.
