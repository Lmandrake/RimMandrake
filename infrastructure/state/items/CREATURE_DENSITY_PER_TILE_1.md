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
| already spawning on Ash'karr | **377** |
| live only in biomes we do NOT have — **redistributable** | **85** |
| 🔴 have **no wild biome ANYWHERE**, in any mod | **798** |

🔴 **The 798 are not "unassigned" — their own authors never made them wild-spawning.** 764 do
not appear in the biome table at all; only 34 sit there at commonality 0. They are VGE lab
hybrids (140), Jurassic dinosaurs (104), Big and Small framework stock (61), Alpha Mechs,
insectoid faction units. **238 of them are not even animals** — 98 `Humanlike`, 140 `ToolUser`.
⇒ ⚠️ **An earlier draft said "883 reach no biome" and treated them as one pool. That was
wrong and it hid the real question:** the ready pool is **462** (377 + 85), and whether any of
the remaining **560 animal-intelligence** creatures should become wild at all is a **flavour
decision for the owner**, not a gap to be filled.
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
