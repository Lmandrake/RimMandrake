## spec
🔴 **OWNER'S BRIEF, 2026-08-22 13:33 — the fauna pass is v1 and it is NOW.** Verbatim:
*"move the animal assignment task to v1 and right now… This is exciting! The biomes are
pretty much frozen right now as are the animals, so it's a good time for this."*

⭐ **Worked WITH the owner, not for him.** He asked for these as items *"to work through with
me now"*. Bring him decisions to react to, never a questionnaire.

### The measured starting state (578-mod dump, 2026-08-22)
| | |
|---|---|
| animals in the census (`animals.json`, corpses already excluded) | **1,260** |
| that can spawn anywhere on Ash'karr | **377** |
| 🔴 reach **no biome at all** | **883 — 70% of what we ship** |
| `(biome, animal)` pairs with `commonality > 0` on this planet | **1,685** |

🔑 **USE `<DefDump>/animals.json`, NOT `defs/ThingDef.json`.** The dumper already ships a
purpose-built animal census — `animalCount 1260`, **`corpseDefsSkipped 1264`** — plus
`biomeAnimals`, a table of **5,568 `(biome, pawnKind, race, commonality)` pairs across 80
biomes**. That is exactly the assignment table this work needs, pre-computed.
⚠️ **`animals.json` is BROADER than `intelligence == Animal`.** It carries 1,260 where a
strict intelligence filter gives 1,022; the extra **238** are `ToolUser` (140) and `Humanlike`
(98) flagged `isAnimal: true` — Alpha Mechs and kin. **Decide per pass whether those belong**;
for wildlife casting they mostly do not, except in `AB_MechanoidIntrusion`.
⚠️ **Earlier drafts of these items said 2,042 animals. That counted 1,020 `Corpse_*` defs**
off `ThingDef.json` — a census the dumper had already done correctly. Do not re-derive it.

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
