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

## the job — names that belong to this planet
**Owner, 2026-08-22:** *"we'll scan their names and find better Star Wars-style animal reskins
for them instead of latin dinosaur names (particularly terrible)."*

🔴 **The Jurassic mod alone is 262 defs of Latin binomials**, and the owner has named that as
the worst offender. A player meeting a *Pachycephalosaurus* on a Star Wars desert world is
being told, in one word, that this is a mod stack.

✅ **The source material already exists and is unbuilt.** `design/Jawa/worldbuilding/Alien_Bestiary.md`
names **108** creatures; `canon.yml > bestiary.built` reads **0** — not one has ever been
applied. **Start there, not from a blank page.**

🔑 **Label patches, not new defs.** A rename is `<label>` and `<description>`; creating a
parallel def loses every other mod's interactions with the original.
⚠️ **A def can be renamed and still be referenced by its defName** in quests, incidents and
other mods' patches. **Never change a `defName`** — only the label a player reads.

## verify
No Latin binomial survives in a label a player can see; every renamed creature keeps its
defName; the 108 bestiary names are used before any new name is invented.

## criteria
A label/description patch set, with the bestiary drawn down toward 0 unused names.
