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

### 🔴 THE REAL SHAPE OF THE PROBLEM — it is INVERTED, not uniform
Measured from `animals.json > biomeAnimals`, commonality > 0, 2026-08-22. Cast size and size
pyramid per biome, biggest biome first:

| tiles | biome | cast | tiny | small | med | large | huge | SUPER |
|---|---|---|---|---|---|---|---|---|
| **4,703** | **`AB_RockyCrags`** | 🔴 **14** | 2 | 1 | 5 | 5 | 1 | **0** |
| 3,578 | `ExtremeDesert` | 100 | 8 | 25 | 18 | 20 | 24 | 5 |
| 2,147 | `Desert` | 155 | 13 | 37 | 30 | 33 | 35 | 7 |
| 2,138 | `AridShrubland` | 224 | 19 | 46 | 40 | 51 | 58 | 10 |
| 1,939 | `AB_MycoticJungle` | 40 | 7 | 11 | 11 | 3 | 6 | 2 |
| 1,721 | `Wasteland` | 🔴 28 | 3 | 11 | 6 | 6 | 2 | **0** |
| 604 | `PoisonForest` | 29 | 4 | 9 | 8 | 3 | 4 | 1 |
| 554 | `AB_PropaneLakes` | 21 | 2 | 6 | 5 | 5 | 3 | **0** |
| 546 | `ZBiome_Badlands` | 162 | 16 | 35 | 36 | 26 | 40 | 9 |
| 534 | `AB_FeraliskInfestedJungle` | 47 | 5 | 14 | 13 | 6 | 7 | 2 |
| 425 | `BMT_FungalForest` | 43 | 5 | 12 | 10 | 10 | 6 | **0** |
| 236 | `AB_MechanoidIntrusion` | 14 | 4 | 4 | 2 | 1 | 3 | **0** |
| **233** | `ZBiome_Grasslands` | ⚠️ **208** | 19 | 45 | 43 | 47 | 47 | 7 |
| 227 | `ZBiome_DesertOasis` | 147 | 11 | 32 | 26 | 36 | 35 | 7 |
| 127 | `BMT_CrystalCaverns` | 38 | 5 | 10 | 9 | 11 | 3 | **0** |
| 96 | `AB_GelatinousSuperorganism` | 43 | 6 | 11 | 11 | 5 | 8 | 2 |
| 90 | `Scarlands` | 99 | 11 | 23 | 27 | 15 | 18 | 5 |
| 65 | `AB_MiasmicMangrove` | 41 | 4 | 10 | 11 | 6 | 9 | 1 |
| 57 | `AB_TarPits` | 44 | 9 | 10 | 9 | 6 | 10 | **0** |
| 31 | `AB_PyroclasticConflagration` | 44 | 8 | 10 | 10 | 9 | 7 | **0** |
| 23 | `Volcano` | 41 | 6 | 12 | 12 | 7 | 4 | **0** |
| **15** | `LavaField` | ⚠️ **68** | 11 | 22 | 9 | 13 | 12 | 1 |
| 3 | `AB_OcularForest` | 35 | 8 | 11 | 7 | 4 | 4 | 1 |

⭐ **Three findings that shape the whole job:**
1. 🔴 **Cast size is inversely correlated with biome size.** `ZBiome_Grasslands` has **208
   creatures across 233 tiles**; `AB_RockyCrags` has **14 across 4,703**. `LavaField` has 68
   on **fifteen tiles**. The player spends most of their time in the thinnest casts.
2. 🔴 **Nine of 23 biomes have NO super-huge at all** — including the two biggest by far,
   `AB_RockyCrags` and `Wasteland`. The owner's "one super-huge rare entity in each biome" is
   currently satisfied by **zero** biomes: the rest have too many, not too few.
3. ⚠️ **The over-cast biomes break the pyramid the other way.** `AridShrubland` fields **10**
   super-huge, `ZBiome_Badlands` 9, `Desert` and `ZBiome_DesertOasis` 7. *"One super-huge rare
   entity"* means these need cutting down, not filling up.

⇒ 🔑 **This job is as much SUBTRACTION as addition**, which the original framing missed.

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


## ✅ ELIGIBILITY, RULED BY THE OWNER 2026-08-22

**Verbatim:** *"I never meant droids, mechs, vehicles for wildlife... we're allocating
existing animals to biomes, not inventing new animals from scratch. Some anomaly may be
re-used in the bioweapon-related biomes though! That stays."*

| class | n | verdict |
|---|---|---|
| wildlife | **1,006** | ✅ the casting pool |
| anomaly | **14** | ✅ eligible, but **only in the biomes named below** |
| mechanoid flesh | 93 | ⛔ out |
| vehicles / automatons | 43 | ⛔ out |
| other non-animals | 5 | ⛔ out |

**The 14 anomaly entities:** bulbfreak · chimera · devourer · dreadmeld · fingerspike ·
fleshmass nucleus · gorehulk · metalhorror · nociosphere · noctol · revenant · sightstealer ·
toughspike · trispike.

**Owner named their biomes, 2026-08-22:** *"gelatinous superorganism, ocular forest, horror
wastes, scarlands"* ⇒ `AB_GelatinousSuperorganism` (96 tiles) · `AB_OcularForest` (3) ·
`Scarlands` (90) · 🔴 **`HorrorWastes` — installed but has ZERO tiles on Ash'karr.**

✅ **RESOLVED 2026-08-22 — `HorrorWastes` goes on the map.** Owner: *"HorrorWastes should be
on the night-side where the ancient bioweapons have adapted to the extreme cold and produced
utterly hostile lifeforms."* ⇒ It is **not** a mistake for `Wasteland`, and the two are
opposite threat classes — see `ASHKARR_WORLD_DEFINITION.md` §6c. Placement is
`HORROR_WASTES_ON_NIGHTSIDE_1`.

🔴 **DO THAT BEFORE CASTING.** It carves ~1,000–1,500 tiles out of `AB_RockyCrags`, which
changes the biome list from 23 to 24 **and re-opens the RockyCrags cast** — the one already
worked. Casting first means casting it twice.

⛔ **`Wasteland` and `AB_MechanoidIntrusion` are CONTAMINATION, not bioweapon** — radiation
and conventional poisoning, where the danger is the ground rather than the wildlife. **No
anomaly entity may be cast in either.**

⛔ **Anomaly entities may not be cast anywhere else**, and that includes the other
bio-horror biomes (`AB_MycoticJungle` 1,939, `AB_FeraliskInfestedJungle` 534,
`PoisonForest` 604). He named four; four is the list.

## ✅ BRIGHT COLOUR IS LICENSED BY DEFENCE — owner, 2026-08-22

**Verbatim:** *"finding things that are WILDLY differently colored is also biologically
plausible if they can defend themselves with poison or hostility though... or even
biological exuberance. So that's just one criteria."*

⇒ ⛔ **Do NOT minimise STANDOUT and do not cast for camouflage.** A creature is scored on
`standout` **against** a `defence` score built from armour, manhunter chance, predator
status, `deathAction`, toxic resistance and body size (`wildlife_filter.py`).
- **gaudy + defended** = aposematism. Plausible *and* memorable — actively wanted.
- **gaudy + defenceless** = 🚩 **FLAG ONLY.** Owner ruled 2026-08-22: *flag for review, do
  not act.* ⚠️ **Burrowing, flight and speed are defences the score cannot see**, so an
  auto-demotion would lose good creatures for a bad reason.


## 🔴 THE CANDIDATE POOLS, RE-MEASURED 2026-08-22 AFTER THE NIGHTSIDE PASS
_The earlier per-biome table in this item was taken over 23 biomes and the pre-pass map. It
is superseded by this one: **25 biomes**, and `AB_RockyCrags` has lost its coldest 1,200
tiles to `HorrorWastes`._

**"Wildlife viable" = eligible for wildlife casting AND survives the biome's MEDIAN tile
temperature.** That is the only hard filter we have, and it does almost all its work at the
extremes:

| biome | tiles | median °C | viable | of which SUPER |
|---|---|---|---|---|
| 🔴 **`HorrorWastes`** | 1,200 | **−69** | **89** | 12 |
| `BMT_CrystalCaverns` | 127 | −62 | 111 | 14 |
| `AB_PropaneLakes` | 554 | −60 | 137 | 14 |
| `AB_MechanoidIntrusion` | 236 | +62 | 151 | 10 |
| `AB_RockyCrags` | 3,423 | −35 | 294 | 17 |
| `Scarlands` | 90 | +59 | 328 | 12 |
| `ExtremeDesert` | 3,606 | +46 | 422 | 12 |
| `AB_MycoticJungle` | 1,939 | −19 | 535 | 30 |
| `Desert` · `Wasteland` · `AridShrubland` · `ZBiome_Badlands` · `AB_GelatinousSuperorganism` | | +1…+30 | **~990** | 39 |

⭐ **Two things follow, and they split the job in half:**
1. **The extremes cast themselves.** 89–151 candidates is a list a human can read. `HorrorWastes`
   is the tightest pool on the planet and **still has 12 super-huge to choose a set piece from**,
   so the constraint is real but not a dead end.
2. 🔴 **Temperature does nothing for the temperate biomes.** Nine of them sit at ~990 viable —
   essentially the whole pool. There, *appearance, defence and uniqueness must carry the entire
   decision*, because the physics has no opinion.

⚠️ **`AB_RockyCrags` got EASIER, not harder** — 232 viable before the split, **294** now. Losing
its deep-nightside end made it warmer (median −44.8 → −35), which widened its pool. That is the
opposite of what I assumed when I called it the hardest biome to cast.
