# Tree burst: water moves a giant only a bit along its life (2026-10-17)

**Authority:** the owner's card write-in of 2026-10-17, verbatim in
`infrastructure/state/items/TREE_BURST_DESIGN_SWEETLINE_TAKES_ITS_TIME.md`:

> (2) + grass cannot make wood of course. Wood should only come from tree-sized plants. And a bursting event for a tree
> should only advance such a massive plant a bit along its trajectory (long, long lifespan would need to absorb a LOT of
> water to "burst.") But if it does, then yes, it should potentially burst and produce logs, sprouts, fruit, the whole
> thing. Case by case let's look at huge tree-like plants to expand this mechanic out more. I am realizing the Rot should
> likely follow wet-biome rulings. Sweetline trees should be VERY slow-growing and long lived, so spilling water on them
> DOES produce a growth spike but will almost certainly not cause it to reach an end of life event.

Builds on `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md` (the ruled spec, "RS") and its rulings file.
Where this note and his words disagree, his words win. Code claims are **MEASURED (file:line)** against the bench clone
at `363b0be115` (ExplosiveGrowth as built in `846b07e973` + `ff4759f445`); every number not his is **PROPOSED**. Nothing
here is decided for him: section 8 is the list of his questions. **No code was changed by this pass.**

Paths are relative to `D:\Luke\dev\RimMandrake` (bench clone `/home/mandrake/rm/bench`).

---

## 1. What the build does to a tree today (MEASURED)

A "tree" in the built engine is any plant whose `woody` flag is set: `def.plant.IsTree || harvestedThingDef == WoodLog`
(`src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs:314`; vanilla `IsTree` is `harvestTag == "Wood"`
or `forceIsTree`, RimSage `RimWorld/PlantProperties.cs:207-215`). Woody only scales the rate:

| archetype | wet | dry | where |
|---|---|---|---|
| dry native, woody | ×10 × 0.625 = **×6.25** | ×0.1 × 0.625 = **×0.0625** (and ages at that, RS §5.2) | `Kernel/RM_ExplosiveGrowthKernel.cs:150-155`, `treeRatio` `ExplosiveGrowthMod.cs:34` |
| wet native, woody (at home) | ×4 × 0.625 = **×2.5, always** | same | same |

Then, at maturity, the tree runs the **same cycle as a weed** (`RM_TopResolver.Fire`, `RM_TopResolver.cs:82-114`):

- dry native: 1 in 3 Burst, else fruit + 4-7 sprouts, and **the parent dies either way** (`DryFruit` → `SplitAndDie`,
  `RM_TopResolver.cs:137-146`);
- wet native: prolific fruit, then **wither** (dies), 1-2 sprouts (`Wither`, `RM_TopResolver.cs:151-`);
- **no wood ever drops** from any outcome: `DropProduce` returns early when the harvest is `WoodLog`
  (`RM_TopResolver.cs:376-377`, added by `ff4759f445`). A tree whose harvest is logs drops nothing at all.

Consequences the owner's ruling now contradicts:

1. **Water drives a tree at ×6.25 to maturity, not "a bit along its trajectory".** A Wasteland Vault Root (growDays 18)
   on a hose spill matures in under 3 days and then dies in its cycle.
2. **Every wet-biome tree dies at maturity.** The Greentide giants are wet natives with the default Churn top, so they
   run ×2.5 to maturity and then wither. `RM_Greatbole` (the fellable tree, growDays 220) withers at about day 88 of its
   life, though its vanilla lifespan is 1,760 days. Every Greentide, Miasma, Fever Wood and Webwork tree in the table
   (section 7) does the same.
3. **A tree's cycle yields no logs, no sprouts worth the name (its seedlings), and fruit only if its harvest is not wood.**
4. **The Sweetline tree is not "woody" at all**: its harvest is `RM_SweetlineWool` with `harvestTag` Standard
   (`src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml:52-57`), so it runs the full dry-native
   ×10 wet / ×0.1 dry. Its `None` top (`RM_ExplosiveGrowthRoster.xml:89`) stops the cycle, but not the rate: a spill
   takes it 10× faster through a 240-day growth, the opposite of "VERY slow-growing". The same blind spot catches every
   `TreeBase` plant whose harvest is not logs (Corrisk, Lumbrel, Shinecap, Pusberry, the two SW port trees).
5. **Pyrelands grass never bursts**: `RM_FE_Plant_Quickgrass` and `RM_FE_Plant_EmberGrass` carry
   `<ruptureChance>0</ruptureChance>` (`RM_ExplosiveGrowthRoster.xml:30-31`). Reversed by this ruling (section 5).

---

## 2. Which plants are "trees" (wood only from tree-sized plants)

*"grass cannot make wood of course. Wood should only come from tree-sized plants."*

PROPOSED: a plant is **tree-class** when it is a tree in body AND in life, read from its def, never from a list:

- **tree in body:** `visualSizeRange` max ≥ **2.0** (PROPOSED; vanilla's oak and poplar draw at 1.5-2.0... the line is
  his to set, Q2), or it inherits vanilla `TreeBase`;
- **tree in life:** `LifespanDays` (= `growDays × lifespanDaysPerGrowDays`, default 8, RimSage `PlantProperties.cs:73,219`)
  ≥ **60 days**, or unlimited (`lifespanDaysPerGrowDays` 0, `PlantProperties.cs:223`).

Tree-class replaces today's `woody` flag in the engine (D17 of RS §8 becomes this). Its effects:

| | tree-class | not tree-class (grass, shrub, cap, reed) |
|---|---|---|
| growth on water | **trajectory advance** (section 3), no ×10 | the ruled rates, unchanged (RS §2.5) |
| maturity cycle (fruit/burst/wither) | **none**: the end of life is the burst (section 4) | unchanged (RS §4) |
| wood in any outcome | yes, its logs (section 4) | **never** (keeps `ff4759f445`'s guard) |
| `treeRatio` 0.625 | retired for tree-class (it existed only to slow the ×10) | n/a |

The census in section 7 finds **woody plants that are not tree-sized** (a 0.25-0.6 heatsink fungus, a 0.7-1.1
slackwax, a 0.7-1.15 brindeth, a 1.0-1.5 thumbstalk, the 1-gd dead ilbareen) and **tree-sized plants that yield no
wood** (Sweetline wool, Corrisk dye, Lumbrel and Jogan fruit). Whether a small woody plant stops yielding `WoodLog`
is a def change owned by `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE`, not by this engine (Q3).

## 3. Water advances a tree "a bit along its trajectory"

*"a bursting event for a tree should only advance such a massive plant a bit along its trajectory (long, long lifespan
would need to absorb a LOT of water to "burst.")"*

**The trajectory** is the tree's whole life: growth 0 → 1 over `growDays`, then age on to `LifespanDays`, where vanilla
kills it (`Plant.Dying`, RimSage `Plant.cs:810-868`). Water does not change the speed of that clock; it **jumps the tree
forward along it** by an amount paid for in litres.

PROPOSED rule, one number per tree:

- A tree-class plant on a WET cell **drinks** the water there: litres leave the source (spill filth, poured mark,
  channel cell, at most `treeDrinkLitresPerDay` from a continuous source such as river, mud or a running flood).
- Every litre drunk advances it `1 / treeLitresPerLifeDay` days along its life: growth while immature (growth +=
  Δ / growDays), age once mature (age += Δ). Young and old alike, one exchange rate.
- So **litres to reach the end of life from any point = remaining life days × `treeLitresPerLifeDay`**. Long life
  means a lot of water, by construction, with no per-plant tuning.
- On dry ground the tree keeps the ruled dry rate and dormancy (×0.1 growth and ageing, RS §5.2): a dry giant is
  nearly frozen, a watered one jumps.

PROPOSED numbers (sliders; the spill is 400 L, a bucket 15 L, a barrel 208 L, `design/RimMandrake/liquid_litres_2026-10-16.md:48,73`):

| knob | proposed | what it means |
|---|---|---|
| `treeLitresPerLifeDay` | **40 L** | one spill (400 L) = 10 days of a tree's life |
| `treeDrinkLitresPerDay` | **40 L** | a tree in a river, on mud or in a flood gains at most one extra day per day (life runs ×2) |

Worked through (remaining life from maturity; litres = days × 40):

| tree | growDays | life days | one spill does | spills to burst from maturity | on a riverbank, burst after |
|---|---|---|---|---|---|
| `RM_SweetlineTree` | 240 | 1,920 | +4.2 % growth (the spike) | 168 (67,200 L) | ~840 days (14 years) |
| `RM_Greatbole` | 220 | 1,760 | +4.5 % growth | 154 (61,600 L) | ~770 days |
| `RM_VaultRoot` | 18 | 810 | +56 % growth | 80 (31,680 L) | ~396 days |
| `RM_CrackedThornwood` | 15 | 600 | +67 % growth | 59 (23,400 L) | ~293 days |
| `RM_Ollim` | 400 | unlimited | +2.5 % growth | never | never |

Sweetline's case reads exactly as he asked: a spill is a visible growth spike, and the end of life needs about 168
spills or 14 years with its roots in a river. A desert tree with a short life (Vault Root) still needs 80 spills.

The **visible spike**: the swell tell (RS §4.1 tell ladder, `Kernel/RM_ExplosiveGrowthKernel.cs:53-61`) plays once per
drink event (a creak and a size step), so a spill on a giant reads as "it drank and grew", without any cycle.

Alternative he may prefer (Q4): advance a fixed **fraction** of the remaining life per water event (e.g. 1 %), which
makes every tree burst after the same number of events and does not need litres; it contradicts "long, long lifespan
would need to absorb a LOT of water", so it is not proposed.

## 4. The burst of a tree: logs, sprouts, fruit, "the whole thing"

*"But if it does, then yes, it should potentially burst and produce logs, sprouts, fruit, the whole thing."*

PROPOSED: a tree-class plant has **no maturity cycle**. Its burst is its **end of life**, reached when water carries its
age past `LifespanDays`. At that moment, instead of vanilla's quiet death:

| part | amount (PROPOSED) | source |
|---|---|---|
| **logs** | the def's own wood: `harvestYield` of its `harvestedThingDef` when that is `WoodLog` or a wood-like log (`RM_MushroomLog`, `RM_OllimWood`, `RM_SlackwaxTimber`), at full growth (its `YieldNow()` at growth 1) | the plant's def; no invented yields |
| **fruit** | `harvestYield` × `produceFactor` of its harvest when that is not wood (wool, dye, fruit, sap); for a log tree, its declared fruit if it has one (`burstFruit`, new roster field) | Greatbole: `RM_GreatboleFruit` (`src/RimMandrake/Greentide/Defs/ThingDefs/RM_GreatboleHarvest_Items.xml:25`, today dropped only by the `RM_GreatboleFruitfall` incident) |
| **sprouts** | its own seedlings, **2-4** (PROPOSED; a giant's ring), respecting built ground | `RM_SproutRing.Sow` as today |
| **the blast** | the Burst top (sound, scatter, `burstHurtsPawns` setting) | existing `Burst`, `RM_TopResolver.cs` |

"Potentially burst" (Q5): either every water-driven end of life bursts, or it rolls the plant's `ruptureChance` (default
1 in 3 for dry natives) and otherwise falls over dead as vanilla does (a felled log pile without the blast). Old age
without water (vanilla's clock alone) stays a quiet vanilla death in both readings (Q6).

Code consequence: `DropProduce`'s wood guard (`RM_TopResolver.cs:376-377`) stays for every non-tree outcome; the tree
burst gets its own drop path that does include logs. RS §5.1 "Wood is never a cycle drop" stays true, because a tree no
longer cycles.

## 5. Pyrelands grass bursts too (reverses the build's call)

He took option (2) "Let Pyrelands grass burst too", reversing the build's reading of C3 ("does not rupture"). Code to
change when FOUNDRY builds it (none changed here):

| file | change |
|---|---|
| `src/RimMandrake/ExplosiveGrowth/Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml:27-31` | remove `<ruptureChance>0</ruptureChance>` from the `RM_FE_Plant_Quickgrass` and `RM_FE_Plant_EmberGrass` rows (they fall to the dry default, 1 in 3), rewrite the comment to cite this ruling; keep `fireAdapted` and (Q7) `sproutCount 6~9` |
| `src/RimMandrake/Utils/selftest_explosivegrowth_archetype_seed.py:48-51` | the `ruptureOdds "0"` assertion for both grasses becomes the default (`1/3`) |
| `src/RimMandrake/ExplosiveGrowth/archetype_seed.py:119` | comment only; the "deciding row" logic still matters (fireAdapted outranks the under-a-day clause for EmberGrass, growDays 0.8) |
| `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md` §4.1 "Pyrelands grass" | now false; corrected in the same commit as this note |
| `src/RimMandrake/ExplosiveGrowth/validation.py` | any live row that expects zero bursts from Pyrelands grass (none found by grep; the Quickgrass rows at :989-991 are the Tinder ring, unaffected) |

Grass never yields wood: both grasses' harvests are not `WoodLog`, and the guard in section 2 holds for all
non-tree-class plants.

## 6. The Rot follows the wet-biome rulings

*"I am realizing the Rot should likely follow wet-biome rulings."*

**What the Rot is:** `RM_TheRot` (mod `src/RimMandrake/TheRot`, campaign twin `RUT_TheRot`), the fungal jungle;
`design/Jawa/worldbuilding/biomes/the_rot.md` §"The Sheen": *"The fungi own all the moisture they need; what falls here
is emitted, not received"*, with **no water rain, ever** (R-H1) and the Sheen (white slime, `flowworks_liquid_matrix.md:87`)
as its only precipitation.

**The wet-biome rulings** are the owner's C1/C2/WP3 cards (`explosive_growth_rulings_2026-10-16.md` rounds 1-2):
wet-biome natives run **×4 at home, always**, and at maturity **fruit prolifically, then wither with just a few
sprouts**; they never rupture unless a sheet row says so (RS §4.2). The wet biomes are seeded by a list
(`<wetNativeBiomes>`: Greentide, Miasma, Fever Wood, Webwork, Contagion and their `RUT_` twins,
`RM_ExplosiveGrowthRoster.xml:232-238`, `RUT_ExplosiveGrowthRoster.xml` same block).

**What the Rot gets today (MEASURED):** it is not in that list, so its plants seed as **dry natives** (×10 wet, ×0.1
dry, ageing ×0.1 dry). It has no water rain, and the Sheen is not an accepted liquid for its plants (no `adaptedLiquids`
on any Rot row), so in practice a Rot fungus is DRY forever: it grows and ages at a tenth of vanilla. On top, 24 Rot
fungi carry the roster's `None` top ("fungal ... deliberately do NOT", the 2026-09-21 roster's hard call 1, unruled,
`RM_ExplosiveGrowthRoster.xml:86-` ), so they never cycle either.

PROPOSED change (one line per roster, plus his questions):

- add `RM_TheRot` to `<wetNativeBiomes>` in the RM roster and `RUT_TheRot` in the RUT roster: Rot natives run ×4 always
  and fruit-wither-few-sprouts at maturity;
- Rot **tree-class** fungi (Pale Tree, Arpeau, Nogtyl, Shinecap; section 7) follow section 3-4 instead, like every
  wet-biome tree (Q9);
- whether the `None` rows on Rot fungi survive the move is his (Q8): under the wet rulings, `None` would mean "×4 but
  never fruits or withers".
- the Sheen as a liquid for Rot plants (T2 "Only for adapted plants") is a per-biome sheet call (Q10); with the wet
  archetype it changes nothing, because wet natives ignore the cell's water (`RM_MapComponent_ExplosiveGrowth.cs:295`).

## 6a. Wet-biome trees (all of Greentide, Miasma, Fever Wood, Webwork, Contagion)

A wet native ignores cell water (always ×4), so "water advances a tree" never happens to it: the jungle is the water.
PROPOSED: a wet-biome tree-class plant grows at vanilla speed × `wetNative`... (Q11 decides between):

- **(a)** vanilla growth and ageing (×1), no cycle, end-of-life burst only if a flood or player water makes it drink
  (section 3 applies as for dry trees): the jungle canopy is stable, which is how Greatbole lore reads ("what a
  greatbole becomes after centuries", `RM_Greatbole.xml` header);
- **(b)** ×4 growth to maturity (C1 "×4, always"), then ×1 ageing, end of life a full burst (section 4) instead of the
  wither at maturity.

Either way, the wither-at-maturity that kills every jungle tree today (section 1, point 2) goes.

## 7. Sweetline: "VERY slow-growing and long lived"

Today: growDays 240, default lifespan ×8 = 1,920 days, not woody → ×10 on a spill (section 1, point 4). Under this
note: tree-class (TreeBase, visual 7.7-10), so a spill is +10 life-days (a 4 % growth spike) and the end of life needs
~168 spills. Its `None` top becomes moot (no tree cycles). Whether its burst drops logs (its harvest is wool, and it
cannot be chopped for wood today, `harvestTag` Standard) is Q12. Whether "VERY slow-growing" means growDays above 240
or a longer life (`lifespanDaysPerGrowDays` above 8) is Q13; its wool harvest re-grows from 0.05 growth
(`harvestAfterGrowth`, `RM_SweetlineTree.xml:57`), so a longer growth also slows the wool.

---
