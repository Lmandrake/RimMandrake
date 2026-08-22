## spec
🔴 **OWNER'S BRIEF, 2026-08-22 13:33 — the fauna pass is v1 and it is NOW.** Verbatim:
*"move the animal assignment task to v1 and right now… This is exciting! The biomes are
pretty much frozen right now as are the animals, so it's a good time for this."*

⭐ **Worked WITH the owner, not for him.** He asked for these as items *"to work through with
me now"*. Bring him decisions to react to, never a questionnaire.

### The measured starting state (578-mod dump, 2026-08-22)
| | |
|---|---|
| animal `ThingDef`s installed (intelligence `Animal`, corpses excluded) | **1,022** |
| that can spawn anywhere on Ash'karr | **377** |
| 🔴 reach **no biome at all** | **645 — 63% of what we ship** |
| animals whose `ComfyTemperatureMin` is explicitly set | **1,015 of 1,022** |

⚠️ **Two numbers here were wrong when these items were first written, 2026-08-22, and both
were corrected the same hour.** (a) *"2,042 animals"* counted **1,020 `Corpse_*` ThingDefs**,
which carry a copied `race` block — the real population is **1,022**, which cross-checks
against the 1,024 rows in every biome's candidate table. (b) *"1,015 of 2,042 have NO explicit
`ComfyTemperatureMin`"* was **backwards**: 1,015 of 1,022 **DO** have one. 🔑 **The temperature
job is therefore not "most animals have no value" but "most animals have a value tuned for
somebody else's world."**

🔑 **The mechanism, so nobody invents one.** Every `BiomeDef.wildAnimals` **already lists all
1,024 candidates** as `BiomeAnimalRecord`s; assignment is the `commonality` number and most
sit at **0** (never). ⇒ This is **re-weighting an existing table in XML**, not new content.
⚠️ **Never count `wildAnimals` entries** — every biome returns 1,024 and the number is
meaningless. Count `commonality > 0`.

## the job — which creatures live in which biome
**The owner's rules of thumb, verbatim, and they are the spec:**

> *"there should be many small, some medium, a few large, and one super-huge rare entity in
> each biome, their appearance should match the biome when possible, ignore existing stats
> like combat heat and diet as we can change that, try to make creatures unique to a biome as
> much as possible and not have ubiquitous creatures"*

⇒ Five rules, and each is testable:
1. **A size pyramid per biome** — many small · some medium · a few large · **exactly one
   super-huge rare**. That last one is a set piece, not a population.
2. **Appearance matches the biome** where the sprite allows it. This is judged by LOOKING at
   the sprite, not by reading the defName.
3. ⛔ **IGNORE existing combat stats, heat tolerance and diet.** They are downstream and we
   change them (`CREATURE_COMBAT_NORMALIZED_1`, `CREATURE_DIET_AND_TEMPERATURE_1`). **Do not
   let a bad stat disqualify a creature that looks right.**
4. **Unique to a biome wherever possible.** A creature the player meets everywhere is worth
   less than one that means *"you are in the Crags"*.
5. Draw from the **1,665 currently unreachable** first — that is where the payoff is.

### the biomes to cast, worst first
`AB_RockyCrags` 4,703 tiles / **14 spawnable today** · `ExtremeDesert` 3,578 / 100 ·
`Desert` 2,147 / 155 · `AridShrubland` 2,138 / 224 · `AB_MycoticJungle` 1,939 / 40 ·
`Wasteland` 1,721 / 28 · `PoisonForest` 604 / 29 · plus 16 smaller.
🔴 **`AB_RockyCrags` is the priority** — biggest biome on the planet, 14 animals, high density,
so the player meets the same fourteen across a fifth of the world.

## verify
Every biome fields a cast matching the pyramid, with a named super-huge; no creature appears
in so many biomes that it reads as ubiquitous; the 1,665 unreachable set is materially reduced.

## criteria
An owner-approved cast list per biome, recorded as data, ready for `commonality` weights.
