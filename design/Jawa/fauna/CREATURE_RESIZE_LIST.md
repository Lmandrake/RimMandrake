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
| ⛔ ~~shrink~~ **OVERRIDDEN — see below** `AA_Behemoth` — Behemoth | Alpha Animals | SUPER | ~~1,614 px~~ **1,024 px, redrawn** | `drawSize` **+ `bodySize`** | 🔴 **PROMOTED to 16.00 / bodySize 16**, not ×0.62 | PoisonForest |
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

---
## ⛔ AA_Behemoth is no longer on this list's terms — owner, 2026-08-24

> *"Behemoth (forsakendragon) is so cool it really deserves to be MUCH larger now. One of the
> most massive creatures."*

**This list shrank it ×0.62 because its art was bad** — 1,614 px carrying a SUPER silhouette, the
weakest headliner in the cast. 🔑 **That premise no longer holds.** The owner authorised the redraw
and it ships at **1,024 px**, so the derived multiplier is measuring art that does not exist.

Then, in the same sitting: *"double it again, AND do it for bodySize fully. This is now the night
side's heaviest hitter and most amazing thing."*

| | shipped by Alpha Animals | after the shrink | **now** |
|---|---|---|---|
| adult `drawSize` | 7.00 | 4.34 | **16.00** |
| life stages | 4.19 / 5.77 / 7.00 | 2.60 / 3.58 / 4.34 | **9.58 / 13.20 / 16.00** |
| `baseBodySize` | 8 | 8 | **16** |
| `baseHealthScale` | 10 | 10 | **20** |

`bodySize` is matched numerically to adult `drawSize`, which is this file's own precedent — Zakkeg
carries `drawSize` 8.20 with `baseBodySize` 8.2.

⚠️ **16.00 IS PAST WHAT THE ART SUPPORTS, and that was a knowing call, not an oversight.** The
sizing rule is texture edge = drawSize × 128, so 16.00 wants a **2,048 px** sprite and the approved
art is **1,024** — it renders at **64 px/cell, half the standard**. ⛔ **Do not "fix" this by
upscaling the PNG**: resampling 1024 → 2048 adds no detail and only makes the number look
compliant. The real fix is a **regeneration at 2,048 px**, which needs the owner's approval because
he approved *this* sprite. 🔑 In practice the softness shows only at maximum zoom — at play zoom a
16-tile creature is well under 1,024 px on screen — which is why it ships.

## ⚔️ And then every other attribute, ×2 — owner, 2026-08-24: *"Yes, scale ALL its attributes along with bodysize."*

| field | was | now |
|---|---|---|
| `MeatAmount` | 250 | **500** |
| `LeatherAmount` | 50 | **100** |
| `MarketValue` | 50,000 | **100,000** |
| dragonclaw `power` (×2 tools) | 18 | **36** |
| dragonclaw surprise `Stun` | 22 | **44** |
| razorfangs `power` | 15 | **30** |
| razorfangs surprise `Stun` | 14 | **28** |
| devour `power` | 5 | **10** |
| `ArmorRating_Sharp` | 0.60 | **0.85** ⚠️ |
| `ArmorRating_Blunt` | 0.40 | **0.75** ⚠️ |
| `ArmorRating_Heat` | 0.30 | **0.60** ⚠️ |

🔑 **The tool `power` operations are the ones that actually delivered "heaviest hitter."** RimWorld
reads `power` as a flat per-tool number that does **not** scale with `bodySize` — without them the
creature would have doubled in size and health and hit exactly as hard as before.

⚠️ **ARMOUR IS RAISED HARD BUT DELIBERATELY NOT DOUBLED.** `ArmorRating_*` are **fractions, not
points**: Sharp 0.60 doubled is **1.20**, and at ≥1.00 the armour roll deflects *every* sharp hit —
the creature becomes literally unkillable by bullets and blades. That is not a heavy hitter, it is a
bug that looks like a feature until a raid cannot be stopped. ⛔ **Do not "finish the job" by taking
these to 1.20.** True immunity is a different design and should be said out loud.

### ⛔ Deliberately untouched, so the omission reads as a decision

| field | why not |
|---|---|
| `MoveSpeed` 4 | doubling makes a 16-tile monster faster than a sprinting human — nothing disengages, nothing escapes. That is chase balance, not mass; mass makes a thing *slower* if anything |
| `ComfyTemperatureMin/Max` | owned by `AnimalTolerances_Ashkarr.xml`, set from the tiles it lives on. Two patches writing one field is how a value silently depends on load order |
| `baseHungerRate` 0.3 | food need **already** scales with `bodySize` in engine — doubling this doubles the appetite twice over |
| `Wildness` 0.99, `Flammability` 0 | already at ceiling and floor |

✅ **Every operation verified against the real 581-mod load set:** each matches exactly one node in
`Alpha Animals: Races_Behemoth.xml`. `validate_patch.py` with `--defs`, 0 errors.

⛔ **Do not regenerate this row from `creature_size_decisions.json`.** It would silently restore
the shrink. The live values are in `src/Jawa/Jawa_Patches/Patches/CreatureResize_Ashkarr.xml`.
