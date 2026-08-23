# The creature resize list — approved for v1

**Owner, 2026-08-23:** *"nice job on the animals. I approve for v1. We'll have to meet them
and see how it feels during live play."*

⚠️ **Approved AS GENERATED, not reviewed row by row.** The sheet wrote its file at
`2026-08-23T08:13:26.343Z` with `savedBy: creature_size_review.html` — so the sheet really was opened and
linked — and **0 of 621 rows were overridden.** He agreed with
the pre-fill rather than editing it. That is a real decision; it is recorded as what it is.

🔑 **And he named the real test:** *"we'll have to meet them and see how it feels during
live play."* ⇒ **Nothing here is final.** These 25 are the changes worth making *before*
anyone plays. The verdict comes from play, not from this table.

Source `design/Jawa/fauna/creature_size_decisions.json` · sheet
`design/Jawa/fauna/creature_size_review.html` · regenerate with
`python3 design/Jawa/fauna/gen_creature_size_sheet.py`

## What changes

**25 of 621 creatures.** The other 596 keep the size they ship with.

🔑 **The magnitude is derived, not guessed.** A sprite should be drawn at a size its
resolution can carry, so the multiplier is `sqrt(px / band median px)`, clamped to
**0.55 – 0.95**. A creature at a quarter of its band's pixel budget gets drawn at half.

| creature | mod | band | sprite | field | change | biomes |
|---|---|---|---:|---|---|---|
| 🔼 **enlarge** `Zakkeg` — zakkeg | Star Wars Animal Collection (Continued) | huge | 4,015 px | `bodySize+drawSize` | `bodySize` 5 → **8.2** and `drawSize` ×1.64 | AB_MiasmicMangrove |
| 🔼 **enlarge** `BMT_Thrumbungus` — thrumbungus | Biomes! Caverns | huge | 5,172 px | `bodySize+drawSize` | `bodySize` 4 → **8.2** and `drawSize` ×2.05 | IceSheet |
| 🔽 shrink `JRWBrachiosaurus` — Brachiosaurus | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 887 px | `drawSize` | `drawSize` **×0.55** | Desert |
| 🔽 shrink `JRWDimetrodon` — Dimetrodon | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 1,070 px | `drawSize` | `drawSize` **×0.55** | AB_GelatinousSuperorganism |
| 🔽 shrink `JRWOuranosaurus` — Ouranosaurus | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 1,345 px | `drawSize` | `drawSize` **×0.60** | AB_GelatinousSuperorganism |
| 🔽 shrink `JRWAntarctopelta` — Antarctopelta | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 1,415 px | `drawSize` | `drawSize` **×0.62** | BMT_FungalForest |
| 🔽 shrink `AA_Behemoth` — Behemoth | Alpha Animals | SUPER | 1,614 px | `drawSize` | `drawSize` **×0.62** | PoisonForest |
| 🔽 shrink `KwazelMaw` — kwazel maw | Star Wars Animal Collection (Continued) | huge | 1,681 px | `drawSize` | `drawSize` **×0.67** | ExtremeDesert |
| 🔽 shrink `Procoptodon` — procoptodon | Megafauna | huge | 2,158 px | `drawSize` | `drawSize` **×0.76** | AB_TarPits |
| 🔽 shrink `Ronto` — ronto | Star Wars Animal Collection (Continued) | SUPER | 2,163 px | `drawSize` | `drawSize` **×0.71** | AB_FeraliskInfestedJungle |
| 🔽 shrink `GR_Thrumbalope` — thrumbalope | Vanilla Genetics Expanded | huge | 2,184 px | `drawSize` | `drawSize` **×0.77** | AB_MycoticJungle |
| 🔽 shrink `GR_Paraceramuffalo` — paraceramuffalo | Vanilla Genetics Expanded | SUPER | 2,214 px | `drawSize` | `drawSize` **×0.72** | AB_PropaneLakes |
| 🔽 shrink `Gomphotaria` — gomphotaria | Megafauna | huge | 2,294 px | `drawSize` | `drawSize` **×0.79** | BMT_CrystalCaverns |
| 🔽 shrink `GreaterKraytDragon` — greater krayt dragon | Star Wars Animal Collection (Continued) | SUPER | 2,322 px | `drawSize` | `drawSize` **×0.74** | AB_MechanoidIntrusion |
| 🔽 shrink `GR_Thrumbolizard` — thrumbolizard | Vanilla Genetics Expanded | huge | 2,324 px | `drawSize` | `drawSize` **×0.79** | AB_FeraliskInfestedJungle |
| 🔽 shrink `Roggwart` — roggwart | Star Wars Animal Collection (Continued) | huge | 2,347 px | `drawSize` | `drawSize` **×0.80** | AB_PyroclasticConflagration |
| 🔽 shrink `GR_Thrumbospider` — thrumbospider | Vanilla Genetics Expanded | huge | 2,359 px | `drawSize` | `drawSize` **×0.80** | AB_RockyCrags |
| 🔽 shrink `MA_Capryak` — Capryak | Mythic Ages: Megafauna Bestiary | huge | 2,378 px | `drawSize` | `drawSize` **×0.80** | ZBiome_Badlands |
| 🔽 shrink `JRWTorosaurus` — Torosaurus | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 2,508 px | `drawSize` | `drawSize` **×0.82** | ZBiome_Badlands |
| 🔽 shrink `Torton` — torton | Star Wars Animal Collection (Continued) | SUPER | 2,694 px | `drawSize` | `drawSize` **×0.80** | AridShrubland |
| 🔽 shrink `Dactillion` — dactillion | Star Wars Animal Collection (Continued) | huge | 2,707 px | `drawSize` | `drawSize` **×0.85** | ZBiome_DesertOasis |
| 🔽 shrink `VAEWaste_Pestigator` — pestigator | Vanilla Animals Expanded — Waste Animals | huge | 2,768 px | `drawSize` | `drawSize` **×0.86** | Volcano |
| 🔽 shrink `MA_Hellboar` — Hellboar | Mythic Ages: Megafauna Bestiary | huge | 2,818 px | `drawSize` | `drawSize` **×0.87** | ZBiome_DesertOasis |
| 🔽 shrink `AA_Atispec` — atispec | Alpha Animals | SUPER | 2,850 px | `drawSize` | `drawSize` **×0.82** | Wasteland |
| 🔽 shrink `Andrewsarchus` — andrewsarchus | Megafauna | huge | 2,859 px | `drawSize` | `drawSize` **×0.88** | Desert |

## 🔑 Which field, and why it is not the same question twice

| field | what it moves | used here for |
|---|---|---|
| `drawSize` | **the picture and nothing else** | all 23 shrinks |
| `bodySize` | meat, leather, hunting yield, carrying capacity, food need, melee damage scaling | — |
| **both** | a creature that is genuinely bigger | the 2 promoted headliners |

⛔ **No shrink touches `bodySize`.** Shrinking to hide weak art is a rendering decision;
taking meat off a creature because its sprite is small is a balance change nobody asked for.

🔴 **The two promotions ARE balance changes, and they are the big ones.** `Zakkeg` 5 → 8.2
and `BMT_Thrumbungus` 4 → 8.2 roughly double meat, melee scaling and food need. Both biomes
had **no super-huge at all**, so the alternative was a headliner-less biome. ⭐ These two are
exactly what *"see how it feels during live play"* is for — watch them first.

## How the 23 shrinks were chosen

`design/Jawa/fauna/sprite_features.csv` measures each sprite's real pixel area. The
threshold is **each band's own 25th percentile** — *in the weakest quarter of its own size
class*, not an absolute the art has to clear:

| band | weak below | median px | cast |
|---|---:|---:|---:|
| SUPER | 3,311 | 4,238 | 24 |
| huge | 2,884 | 3,712 | 74 |
| large | 2,734 | 3,558 | 128 |
| med | 2,659 | 3,398 | 208 |
| small | 2,532 | 3,400 | 208 |
| tiny | 1,533 | 2,833 | 104 |

⚠️ **px measures RESOLUTION, not whether the art is good.** A crisp small sprite and a muddy
large one score the same. It decides where to look first; the eye decides the rest.
⛔ **Only `SUPER` and `huge` were proposed for shrinking.** A weak sprite on a `small`
creature costs nothing because it is seen small — those rows are flagged in the sheet and
deliberately not proposed.
