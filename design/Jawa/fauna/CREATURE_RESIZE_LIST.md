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


---

# The SECOND resize pass — from the owner's art review, 2026-08-23

🔴 **A different owner session, a different instrument, and 21 more shrinks.** He reviewed all
621 cast creatures himself in `creature_art_review.html` and chose `shrink` on these. ⚠️ **Unlike
the 25 above, these were NOT approved as-generated** — he overruled the sheet on 8 rows and wrote
12 notes, so these carry his reasoning and it is quoted below.

⛔ **`bodySize` is untouched on every row here, exactly as in the first pass.** Shrinking to suit
a picture is a RENDERING decision; taking meat off a creature because its sprite is small is a
balance change nobody asked for.

## Class A — resolution-driven, and the documented rule applies unchanged

`sqrt(px / band median px)`, clamped 0.55–0.95, against the cast's own band medians
(SUPER 4,000 · huge 3,711 · large 3,558 · med 3,398 · small 3,396 · tiny 2,689).

| creature | mod | band | sprite | change | why |
|---|---|---|---:|---|---|
| `JRWBrachiosaurus` — Brachiosaurus | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 887 px | `drawSize` **×0.45** | 🔴 **BELOW THE CLAMP ON HIS EXPLICIT INSTRUCTION.** The rule floors at 0.55; he asked for more · *"Shrink a lot. It's familiar outline is also a negative, so make it ver"* |
| `JRWDimetrodon` — Dimetrodon | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 1,070 px | `drawSize` **×0.55** | below its band budget; drawn at a size its resolution can carry |
| `JRWOuranosaurus` — Ouranosaurus | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 1,345 px | `drawSize` **×0.60** | below its band budget; drawn at a size its resolution can carry |
| `JRWAntarctopelta` — Antarctopelta | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 1,415 px | `drawSize` **×0.62** | below its band budget; drawn at a size its resolution can carry |
| `KwazelMaw` — kwazel maw | Star Wars Animal Collection (Continued) | huge | 1,681 px | `drawSize` **×0.67** | below its band budget; drawn at a size its resolution can carry |
| `Ronto` — ronto | Star Wars Animal Collection (Continued) | SUPER | 2,163 px | `drawSize` **×0.74** | below its band budget; drawn at a size its resolution can carry |
| `GR_Paraceramuffalo` — paraceramuffalo | Vanilla Genetics Expanded | SUPER | 2,214 px | `drawSize` **×0.74** | below its band budget; drawn at a size its resolution can carry |
| `GreaterKraytDragon` — greater krayt dragon | Star Wars Animal Collection (Continued) | SUPER | 2,322 px | `drawSize` **×0.76** | below its band budget; drawn at a size its resolution can carry |
| `Procoptodon` — procoptodon | Megafauna | huge | 2,158 px | `drawSize` **×0.76** | below its band budget; drawn at a size its resolution can carry |
| `GR_Thrumbalope` — thrumbalope | Vanilla Genetics Expanded | huge | 2,184 px | `drawSize` **×0.77** | below its band budget; drawn at a size its resolution can carry |
| `Gomphotaria` — gomphotaria | Megafauna | huge | 2,294 px | `drawSize` **×0.79** | below its band budget; drawn at a size its resolution can carry |
| `GR_Thrumbolizard` — thrumbolizard | Vanilla Genetics Expanded | huge | 2,324 px | `drawSize` **×0.79** | below its band budget; drawn at a size its resolution can carry |
| `Roggwart` — roggwart | Star Wars Animal Collection (Continued) | huge | 2,347 px | `drawSize` **×0.80** | below its band budget; drawn at a size its resolution can carry |
| `GR_Thrumbospider` — thrumbospider | Vanilla Genetics Expanded | huge | 2,359 px | `drawSize` **×0.80** | below its band budget; drawn at a size its resolution can carry |
| `MA_Capryak` — Capryak | Mythic Ages: Megafauna Bestiary | huge | 2,378 px | `drawSize` **×0.80** | below its band budget; drawn at a size its resolution can carry |
| `JRWTorosaurus` — Torosaurus | Jurassic Rimworld - Dinosaurs Only (Continued) | huge | 2,508 px | `drawSize` **×0.82** | below its band budget; drawn at a size its resolution can carry |

🔴 **`JRWBrachiosaurus` breaks the clamp deliberately, and only because he said so:**
*"Shrink a lot. It's familiar outline is also a negative, so make it very small to make it
interestingly different than Earth"* ⇒ ×0.45, past the 0.55 floor. ⭐ **Note his reason — a
FAMILIAR silhouette is a defect on this planet.** That is a criterion no sprite metric contains.

## Class B — silhouette-driven, where the documented rule RETURNS A NO-OP

🔴 **These five come back at ×0.94–0.95 from the formula, which is invisible in play.** Their
sprites are already at or above their band median, so a resolution-derived multiplier correctly
reports *nothing to fix* — **and he asked for them to be smaller anyway.**

🔑 **His reason is not resolution, it is silhouette.** *"Fascinating profile shape, so keep in and
make smaller"* · *"Keep for the silhouette… it's very exotic"* · *"Fascinating outline and unique"*.
He is keeping strange-looking creatures and making them curiosities rather than landmarks.

⚠️ **×0.80 below is DECIDE's judgement, not a derivation, and it is the one number on this page
nobody has ruled on.** It is chosen to be visible without being drastic. If it reads wrong in
play, change this number — do not reach for the formula, which has already said it has no opinion.

| creature | mod | band | sprite | change | why |
|---|---|---|---:|---|---|
| `BMT_Screecher` — screecher | Biomes! Polluted Lands | med | 3,030 px | `drawSize` **×0.80** | ⚠️ judgement — the formula returns ×0.94, a no-op · *"It has an interesting shape... v2 tag for redraw candidate"* |
| `BMT_Pillbug` — pillbug | Biomes! Caverns | small | 4,831 px | `drawSize` **×0.80** | ⚠️ judgement — the formula returns ×0.95, a no-op |
| `BMT_SludgeCrawler` — sludgecrawler | Biomes! Polluted Lands | large | 3,955 px | `drawSize` **×0.80** | ⚠️ judgement — the formula returns ×0.95, a no-op · *"Fascinating profile shape, so keep in and make smaller. Good v2 redraw"* |
| `BMT_TripleSnapper` — triple snapper | Biomes! Polluted Lands | med | 3,398 px | `drawSize` **×0.80** | ⚠️ judgement — the formula returns ×0.95, a no-op · *"Fascinating outline and unique. Keep and shrink, v2 redraw candidate"* |
| `Noctol` — noctol | Anomaly | med | 6,788 px | `drawSize` **×0.80** | ⚠️ judgement — the formula returns ×0.95, a no-op · *"Keep for the silhouette... it's very exotic"* |

## What both classes share

⚠️ **`drawSize` is not on the `ThingDef` and the def dump does not carry it** — the same warning
the first pass carries. Current values come from each mod's source XML, per creature. That is why
this page states MULTIPLIERS and not absolutes.
🔑 **And he named the real test again:** these are the changes worth making before anyone plays.
The verdict comes from play.
