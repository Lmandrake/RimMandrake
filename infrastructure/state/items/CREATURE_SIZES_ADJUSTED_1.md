## ✅ APPROVED FOR v1 — owner, 2026-08-23

> *"nice job on the animals. I approve for v1. We'll have to meet them and see how it
> feels during live play."*

**The deliverable this item asked for — *a resize list, per creature, naming which field
and why* — is `design/Jawa/fauna/CREATURE_RESIZE_LIST.md`.** 25 changes out of 621 cast
creatures. BUILD executes it under `CREATURE_RESIZE_PATCH_1`.

| | |
|---|---|
| creatures reviewed | **621** (the cast, not the 1,260-animal census) |
| 🔽 shrink, `drawSize` only | **23** |
| 🔼 enlarge, `bodySize` + `drawSize` | **2** |
| unchanged | **596** |

⚠️ **Approved as generated, not row by row.** The sheet wrote its own file at
`2026-08-23T08:13:26Z` with `savedBy: creature_size_review.html`, so it really was opened
and linked — and **0 of 621 rows were overridden**. He agreed with the pre-fill rather than
editing it. 🔑 That is a real decision and it is recorded as what it is, not dressed up as
621 individual judgements. A row that looks wrong in game is a correction, not a reversal.

## How each criterion was met

- ✅ **"Each biome has its one super-huge."** It did not: `AB_MiasmicMangrove` and
  `IceSheet` had **none**. The sheet proposed the fix rather than reporting the gap —
  `Zakkeg` and `BMT_Thrumbungus`, each already the biggest thing cast in its own biome.
  **24 of 26 → 26 of 26.**
- ✅ **"No shrunk creature has lost mechanical relevance it needed."** Guaranteed by
  construction: **every shrink is `drawSize` only**, which moves nothing but the picture.
- ✅ **"`bodySize` changes are deliberate and listed separately."** There are exactly two,
  both promotions, both called out as the risky half — `Zakkeg` 5 → 8.2 and
  `BMT_Thrumbungus` 4 → 8.2 roughly double meat, melee scaling and food need.

## 🔑 The art evidence was already on disk

The owner's *"adjust for low-quality graphics"* had a measurable proxy waiting in
`design/Jawa/fauna/sprite_features.csv`: **`px`, the sprite's real pixel area.** The flag is
each band's own 25th percentile — *the weakest quarter of its own size class* — so it never
asks small art to clear a big-art bar. The worst case was `JRWBrachiosaurus` at **887 px**
carrying a `huge` silhouette, and `AA_Behemoth` at **1,614 px** carrying a SUPER one.
⚠️ **px measures RESOLUTION, not whether the art is good.** It decided where to look; it did
not decide.

## ⏳ What is deliberately NOT settled

🔑 The owner named the real test himself: **live play.** ⛔ Nothing in the list is frozen,
and the two promotions especially should be watched before anyone trusts them. The sheet
regenerates from `gen_creature_size_sheet.py` and merges his file per row, so a second pass
after play costs nothing and loses nothing.

---

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
