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

## the job — make threat mean the same thing everywhere
**Owner, 2026-08-22:** *"combat stat normalization across the world."*

⛔ **Blocked on `BIOME_CREATURE_CAST_1`.** ⭐ **And this is the item that makes rule 3 of the
cast safe** — the owner said to *ignore* existing combat stats when casting precisely because
this pass fixes them afterwards.

The problem: creatures drawn from four unrelated mods (Star Wars Animal Collection 320 defs ·
Alpha Animals 282 · Vanilla Genetics Expanded 279 · Jurassic 262) were balanced against four
different games. Dropped into one world they produce a threat curve nobody designed.

**Normalise against a stated yardstick**, and write the yardstick down: what a *small*, a
*medium*, a *large* and a *super-huge* should mean in damage, health and speed on Ash'karr.
⚠️ Interacts with the Jawa's own weakness: a clan of scavengers with cut firearms cannot fight
a mod-default megafauna curve. **The player's actual arsenal is the calibration input.**

## verify
A manhunter pack of each size class is survivable-but-serious for the intended colony strength;
no creature is an outlier by an order of magnitude.

## criteria
A stated threat yardstick per size class, and every cast creature normalised to it.
