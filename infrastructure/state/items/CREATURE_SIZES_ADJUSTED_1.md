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

## the job — resize to fit the pyramid and to hide bad art
**Owner, 2026-08-22:** *"We may need to re-size some of them to adjust for low-quality
graphics (make them smaller) or to fill in gaps (need more giant things)."*

Two distinct reasons to resize, and they must not be confused:
1. 🔽 **Shrink to hide weak art.** A low-fidelity sprite reads far better small. This is a
   legitimate art remedy that does **not** touch the standing art-fix directive, because
   nothing is redrawn.
2. 🔼 **Enlarge to fill a gap.** `BIOME_CREATURE_CAST_1` wants **one super-huge per biome**
   and there will not be 23 convincing giants in the pool. Promoting a good large sprite is
   cheaper and better than inventing a creature.

⚠️ **`bodySize` and `drawSize` are different fields with different consequences.** `drawSize`
is purely visual; `bodySize` moves meat, leather, hunting yield, carrying capacity, food need
and melee damage scaling. **Decide per creature which one you meant** — a giant that is only
`drawSize` is a cardboard cutout, and a giant that is `bodySize` changes the economy.

## verify
Each biome has its one super-huge; no shrunk creature has lost mechanical relevance it needed;
`bodySize` changes are deliberate and listed separately from `drawSize` changes.

## criteria
A resize list, per creature, naming which field and why.
