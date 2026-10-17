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

- **tree in body:** `visualSizeRange` max ≥ **2.0** (PROPOSED; the line is his to set, Q2), or it inherits vanilla `TreeBase`;
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
on any Rot row), so in practice a Rot fungus is DRY forever: it grows and ages at a tenth of vanilla. On top, 34 of the 36 plants in `RM_TheRot`'s `wildPlants` (all but `RM_AmbrosyxFungus` and `RM_TollukCap`, MEASURED by
parsing both files)
carry the roster's `None` top ("fungal ... deliberately do NOT", the 2026-09-21 roster's hard call 1, unruled,
`RM_ExplosiveGrowthRoster.xml:86-`), so they never cycle either.

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
PROPOSED, two readings for him (Q11):

- **(a)** vanilla growth and ageing (×1), no cycle, end-of-life burst only if a flood or player water makes it drink
  (section 3 applies as for dry trees): the jungle canopy is stable, which is how Greatbole lore reads ("what a
  greatbole becomes after centuries", `RM_Greatbole.xml` header);
- **(b)** ×4 growth to maturity (C1 "×4, always"), then ×1 ageing, end of life a full burst (section 4) instead of the
  wither at maturity.

Either way, the wither-at-maturity that kills every jungle tree today (section 1, point 2) goes.

## 6b. Sweetline: "VERY slow-growing and long lived"

Today: growDays 240, default lifespan ×8 = 1,920 days, not woody → ×10 on a spill (section 1, point 4). Under this
note: tree-class (TreeBase, visual 7.7-10), so a spill is +10 life-days (a 4 % growth spike) and the end of life needs
~168 spills. Its `None` top becomes moot (no tree cycles). Whether its burst drops logs (its harvest is wool, and it
cannot be chopped for wood today, `harvestTag` Standard) is Q12. Whether "VERY slow-growing" means growDays above 240
or a longer life (`lifespanDaysPerGrowDays` above 8) is Q13; its wool harvest re-grows from 0.05 growth
(`harvestAfterGrowth`, `RM_SweetlineTree.xml:57`), so a longer growth also slows the wool.

---

## 7. Case by case: every huge or tree-like plant we ship (for the sitting with BENCH)

**Census (MEASURED 2026-10-17, by parsing every `ThingDef` under `src/` with its `ParentName` chain resolved inside
`src/`, vanilla `TreeBase` treated as `harvestTag Wood` + `WoodLog`):** a row is here if it yields wood
(`harvestTag Wood` or `WoodLog`), inherits `TreeBase`, or draws at `visualSizeRange` max ≥ 4. **66 plants**, of which
**56 are tree-class** under section 2's proposed test (≥ 2.0 visual or TreeBase, and ≥ 60 life days or unlimited).
"life days" = `growDays × lifespanDaysPerGrowDays` (vanilla default 8 when unset). Archetype is the engine's seed:
wet if a wet biome's `wildPlants` lists it (section 6 list), else dry (our tier ships it). Current top from both rosters
(`Churn(default)` = no row). Water-to-burst uses the PROPOSED 40 L per day of life and the 400 L spill; "river" is the
days to burst with the tree's roots in permanent water at the proposed one extra day per day. Numbers are not tuned:
yields belong to `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE`.

Not in this table: donor flora enrolled only by roster row (`AB_JungleTree`, `AB_MangroveTree`, `AB_MangrovePalm`,
`AB_ParasiticMangrove`, `AB_SlimyTree`, `AB_LargeSlimyTree`, `AB_HalfAlienTree`, `AB_AlienTree`,
`AB_AlienTree_Polluted`, `AB_KeeningCordax`): their defs are not in `src/`, so their numbers are UNMEASURED here; they
take the same rule by the same test once the build reads the def. `RUT_Placeholder_GreentideGiantTree` is still a
roster row (`RUT_ExplosiveGrowthRoster.xml`) but the def was retired by `RM_Greatbole` (its header): a dead row.
**Greatbole:** the row is `RM_Greatbole`, the fellable tree; `RM_GreatboleCore` / `RM_GreatboleHeartwood` are the
unfellable landmark, not plants in this engine.

| plant | mod | growDays | lifespanDaysPerGrowDays (life days) | current burst behaviour (MEASURED) | proposed water-to-burst (from maturity, 40 L/day of life) | proposed burst yield | open question |
|---|---|---|---|---|---|---|---|
| `RM_GiantFibreStalk` | Abyss | 14 | 8 (default) (112) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 3,920 L ≈ 10 spills; river ~98 d | 10 WoodLog; 2-4 sprouts |  |
| `RM_TreeMushroom` | Abyss | 15 | 8 (default) (120) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 4,200 L ≈ 10 spills; river ~105 d | 25 WoodLog; 2-4 sprouts | 8-15 visual but harvestTag Standard: chopped as a crop; tree-class by size |
| `RM_Wickwood` | Abyss | 14 | 8 (default) (112) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 3,920 L ≈ 10 spills; river ~98 d | 18 WoodLog; 2-4 sprouts |  |
| `RM_GiantAgariTox` | Cauldron | 25 | 8 (default) (200) | dry native, ×10 wet / ×0.1 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | 7,000 L ≈ 18 spills; river ~175 d | no harvest: 2-4 sprouts only | no harvest at all: burst yields only sprouts? |
| `RM_TreeMartyr` | Cauldron | 10 | 40 (400) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | 15,600 L ≈ 39 spills; river ~390 d | 15 WoodLog; 2-4 sprouts | None top today (hoarder call); 400-day life |
| `RM_TwistingThornwood` | Cauldron | 15 | 40 (600) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 23,400 L ≈ 58 spills; river ~585 d | 25 WoodLog; 2-4 sprouts |  |
| `RM_Eyebark` | Contagion | 16 | 10 (160) | wet native, ×2.5 always; contaminated Rupture at maturity, dies; drops no logs (WoodLog guard) | 5,760 L ≈ 14 spills; river ~144 d (wet biome: Q11) | 6 WoodLog; 2-4 sprouts | Contagion: contaminated Rupture keeps its own odds? (Q15) |
| `RM_HalfmadeTree` | Contagion | 10 | 8 (80) | wet native, ×2.5 always; contaminated Rupture at maturity, dies; drops no logs (WoodLog guard) | 2,800 L ≈ 7 spills; river ~70 d (wet biome: Q11) | 18 WoodLog; 2-4 sprouts | Contagion Rupture (Q15) |
| `RM_HalfmadeTreeBlighted` | Contagion | 5 | 4 (20) | wet native, ×2.5 always; contaminated Rupture at maturity, dies; its non-WoodLog logs DO drop on fruit | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | Contagion Rupture, 20-day life (Q15) |
| `RM_Ammeth` | FeverWood | 17 | 8 (default) (136) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; its non-WoodLog logs DO drop on fruit | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today |  |
| `RM_CorriskTree` | FeverWood | 10 | 8 (default) (80) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 2,800 L ≈ 7 spills; river ~70 d (wet biome: Q11) | 30 Dye (fruit); logs ? ; 2-4 sprouts | dye tree, 5-10 visual, not woody today: logs on burst? |
| `RM_LumbrelTree` | FeverWood | 10 | 8 (default) (80) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 2,800 L ≈ 7 spills; river ~70 d (wet biome: Q11) | 40 RM_RawLumbrelFruit (fruit); logs ? ; 2-4 sprouts | fruit tree, 5-10 visual, not woody today: logs on burst? |
| `RM_Sodderel` | FeverWood | 22 | 8 (default) (176) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 6,160 L ≈ 15 spills; river ~154 d (wet biome: Q11) | 18 WoodLog; 2-4 sprouts |  |
| `RM_Varnoth` | FeverWood | 30 | 8 (default) (240) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 8,400 L ≈ 21 spills; river ~210 d (wet biome: Q11) | 60 WoodLog; 2-4 sprouts | harvestTag Standard but WoodLog 60 at 2.5 visual |
| `RM_CrackedThornwood` | FloodedCanyon | 15 | 40 (600) | dry native, ×6.25 wet / ×0.0625 dry; bursts at maturity (1 in 1), dies; drops no logs (WoodLog guard) | 23,400 L ≈ 58 spills; river ~585 d | 25 WoodLog; 2-4 sprouts | Burst top (1 in 1) today; keep 1 in 1 at end of life? |
| `RM_Harrovaq` | FloodedCanyon | 20 | 40 (800) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 31,200 L ≈ 78 spills; river ~780 d | 14 WoodLog; 2-4 sprouts |  |
| `RM_Plant_Thumbstalk` | GelatinousSlime | 12 | 14 (168) | dry native, ×6.25 wet / ×0.0625 dry; Slime top at maturity; its non-WoodLog logs DO drop on fruit | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | 1.5 visual, Slime top, WoodLog 14 (Q3) |
| `RM_Brakkel` | Greentide | 12 | 8 (default) (96) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 3,360 L ≈ 8 spills; river ~84 d (wet biome: Q11) | 10 RM_BrakkelFruit (fruit); logs ? ; 2-4 sprouts |  |
| `RM_Brunnock` | Greentide | 140 | 8 (default) (1,120) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 39,200 L ≈ 98 spills; river ~980 d (wet biome: Q11) | 30 WoodLog; 2-4 sprouts | growDays 140: second-slowest jungle tree |
| `RM_Cundral` | Greentide | 20 | 8 (default) (160) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 5,600 L ≈ 14 spills; river ~140 d (wet biome: Q11) | 8 WoodLog; 2-4 sprouts |  |
| `RM_Ghemmel` | Greentide | 30 | 8 (default) (240) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 8,400 L ≈ 21 spills; river ~210 d (wet biome: Q11) | ? (no yield set) WoodLog; 2-4 sprouts |  |
| `RM_Gorbeleth` | Greentide | 24 | 8 (default) (192) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts | 6,720 L ≈ 17 spills; river ~168 d (wet biome: Q11) | 8 RM_GorbelethToxin (fruit); logs ? ; 2-4 sprouts | harvest is a toxin, not logs: fruit = toxin? |
| `RM_Greatbole` | Greentide | 220 | 8 (default) (1,760) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 61,600 L ≈ 154 spills; river ~1,540 d (wet biome: Q11) | 150 WoodLog; 2-4 sprouts; fruit `RM_GreatboleFruit` | the FELLABLE giant (not `RM_GreatboleCore`/`RM_GreatboleHeartwood`, the mineable landmark); withers today at ~day 88. Fruit = `RM_GreatboleFruit`? |
| `RM_Illurin` | Greentide | 16 | 8 (default) (128) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 4,480 L ≈ 11 spills; river ~112 d (wet biome: Q11) | no harvest: 2-4 sprouts only | 4-7 visual, no harvest |
| `RM_Kaddrath` | Greentide | 48 | 8 (default) (384) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 13,440 L ≈ 34 spills; river ~336 d (wet biome: Q11) | ? (no yield set) WoodLog; 2-4 sprouts |  |
| `RM_Mirrelbole` | Greentide | 22 | 8 (default) (176) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 6,160 L ≈ 15 spills; river ~154 d (wet biome: Q11) | 18 WoodLog; 2-4 sprouts |  |
| `RM_Mourvel` | Greentide | 45 | 8 (default) (360) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 12,600 L ≈ 32 spills; river ~315 d (wet biome: Q11) | ? (no yield set) WoodLog; 2-4 sprouts |  |
| `RM_Nemmer` | Greentide | 26 | 8 (default) (208) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 7,280 L ≈ 18 spills; river ~182 d (wet biome: Q11) | 15 WoodLog; 2-4 sprouts |  |
| `RM_Quathis` | Greentide | 18 | 8 (default) (144) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 5,040 L ≈ 13 spills; river ~126 d (wet biome: Q11) | 12 WoodLog; 2-4 sprouts |  |
| `RM_Sarnstilt` | Greentide | 40 | 8 (default) (320) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 11,200 L ≈ 28 spills; river ~280 d (wet biome: Q11) | 20 WoodLog; 2-4 sprouts |  |
| `RM_Sarquin` | Greentide | 14 | 8 (default) (112) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 3,920 L ≈ 10 spills; river ~98 d (wet biome: Q11) | 9 RM_SarquinSap (fruit); logs ? ; 2-4 sprouts |  |
| `RM_Thalquith` | Greentide | 20 | 8 (default) (160) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 5,600 L ≈ 14 spills; river ~140 d (wet biome: Q11) | 10 WoodLog; 2-4 sprouts |  |
| `RM_Tumbel` | Greentide | 16 | 8 (default) (128) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 4,480 L ≈ 11 spills; river ~112 d (wet biome: Q11) | 8 RM_TumbelGourd (fruit); logs ? ; 2-4 sprouts |  |
| `RM_Veluthar` | Greentide | 55 | 8 (default) (440) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 15,400 L ≈ 38 spills; river ~385 d (wet biome: Q11) | 35 WoodLog; 2-4 sprouts |  |
| `RM_Vurmeloth` | Greentide | 50 | 8 (default) (400) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 14,000 L ≈ 35 spills; river ~350 d (wet biome: Q11) | 22 WoodLog; 2-4 sprouts |  |
| `RM_Wollick` | Greentide | 13 | 8 (default) (104) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 3,640 L ≈ 9 spills; river ~91 d (wet biome: Q11) | 11 RM_WollickTuber (fruit); logs ? ; 2-4 sprouts |  |
| `RM_Zhorrel` | Greentide | 28 | 8 (default) (224) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 7,840 L ≈ 20 spills; river ~196 d (wet biome: Q11) | 16 WoodLog; 2-4 sprouts |  |
| `RM_ThrakkCap` | LanternDeeps | 30 | 8 (default) (240) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | 8,400 L ≈ 21 spills; river ~210 d | 40 WoodLog; 2-4 sprouts | None top; no visualSizeRange in the def (size UNMEASURED) |
| `RM_VellokReed` | LanternDeeps | 5 | 9 (45) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | a 5-day reed yielding 20 WoodLog (Q3) |
| `RM_SweetlineTree` | LeaningScrub | 240 | 8 (default) (1,920) | dry native, ×10 wet / ×0.1 dry; rate only, never cycles | 67,200 L ≈ 168 spills; river ~1,680 d | 20 RM_SweetlineWool (fruit); logs ? ; 2-4 sprouts | wool tree, not woody today so ×10 on a spill; logs on burst? slower growDays or longer life? (Q12, Q13) |
| `RM_Shadespire` | LongShade | 40 | 60 (2,400) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 94,400 L ≈ 236 spills; river ~2,360 d | 40 WoodLog; 2-4 sprouts |  |
| `RM_Brelloch` | Miasma | 20 | 8 (default) (160) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts | 5,600 L ≈ 14 spills; river ~140 d (wet biome: Q11) | 12 RM_RawSalt (fruit); logs ? ; 2-4 sprouts | harvest is salt, not logs |
| `RM_IlbareenDead` | Miasma | 1 | 8 (default) (8) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; its non-WoodLog logs DO drop on fruit | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | growDays 1, a dead stalk yielding 2 WoodLog; not in any biome list (Q3) |
| `RM_Ollamane` | Miasma | 18 | 8 (default) (144) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 5,040 L ≈ 13 spills; river ~126 d (wet biome: Q11) | 18 WoodLog; 2-4 sprouts |  |
| `RM_Quennath` | Miasma | 15 | 8 (default) (120) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 4,200 L ≈ 10 spills; river ~105 d (wet biome: Q11) | 8 WoodLog; 2-4 sprouts |  |
| `RM_Thessamor` | Miasma | 25 | 8 (default) (200) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 7,000 L ≈ 18 spills; river ~175 d (wet biome: Q11) | 22 WoodLog; 2-4 sprouts |  |
| `RSW_Plant_HydenockTree_Wild` | SWBestiary | 10 | 8 (default) (80) | dry native, ×10 wet / ×0.1 dry; Flush: survives, drops produce | 2,800 L ≈ 7 spills; river ~70 d | 30 Dye (fruit); logs ? ; 2-4 sprouts | Flush giant (survives its top); not in our biome lists; logs on burst? |
| `RSW_Plant_JoganTree_Wild` | SWBestiary | 10 | 8 (default) (80) | dry native, ×10 wet / ×0.1 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | 2,800 L ≈ 7 spills; river ~70 d | 40 RSW_RawJoganFruit (fruit); logs ? ; 2-4 sprouts | fruit tree with Churn ×2.5 produce; logs on burst? |
| `RM_KneelOllim` | Stillsand | 400 | 0 (unlimited) (unlimited) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; its non-WoodLog logs DO drop on fruit | never (unlimited life); a spill = +10 days of growth | 5 RM_OllimWood; 2-4 sprouts | unlimited life, and only 2.6 visual: a tree? |
| `RM_Ollim` | Stillsand | 400 | 0 (unlimited) (unlimited) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | never (unlimited life); a spill = +10 days of growth | 15 RM_OllimWood; 2-4 sprouts | unlimited life: water can never burst it. Intended? (Q14) |
| `RM_Slackwax` | TerminalBiomes | 10 | 8 (default) (80) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; its non-WoodLog logs DO drop on fruit | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | 1.1 visual timber: wood from a non-tree (Q3) |
| `RM_HeatsinkFungus` | TheForge | 5.5 | 8 (default) (44) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | 0.6 visual and yields WoodLog: wood from a non-tree (Q3) |
| `RM_Arpeau` | TheRot | 5 | 9 (45) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | 6-10 visual, 45-day life: short-lived giant fungus; Rot wet rulings (Q8, Q9) |
| `RM_FlakespireFungus` | TheRot | 18 | 8 (default) (144) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | 5,040 L ≈ 13 spills; river ~126 d | 30 RM_MushroomLog; 2-4 sprouts |  |
| `RM_GreenArpeau` | TheRot | 5 | 9 (45) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | not in any biome list |
| `RM_Nogtyl` | TheRot | 7 | 9 (63) | wet native, ×2.5 always; rate only, never cycles | 2,240 L ≈ 6 spills; river ~56 d (wet biome: Q11) | 20 WoodLog; 2-4 sprouts | 7-12 visual, 63-day life; listed in Miasma's roster, not the Rot's |
| `RM_NogtylMarsh` | TheRot | 7 | 9 (63) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | 2,240 L ≈ 6 spills; river ~56 d | 20 WoodLog; 2-4 sprouts | marsh twin, not in any biome list (Q9) |
| `RM_PaleTree` | TheRot | 25 | 0 (unlimited) (unlimited) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | never (unlimited life); a spill = +10 days of growth | 25 WoodLog; 2-4 sprouts | unlimited life: never bursts; a Rot tree under the wet rulings (Q9) |
| `RM_Shinecap` | TheRot | 30 | 8 (default) (240) | dry native, ×10 wet / ×0.1 dry; rate only, never cycles | 8,400 L ≈ 21 spills; river ~210 d | 20 RM_Glimmerslime (fruit); logs ? ; 2-4 sprouts | slime-cap on TreeBase; tree-class by base, 3.0 visual |
| `RM_Skulltop` | TheRot | 8 | 0 (unlimited) (unlimited) | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | never (unlimited life); a spill = +10 days of growth | ? (no yield set) RM_MushroomLog; 2-4 sprouts | 0.7 visual, unlimited life, yields mushroom logs: tree-class? (Q3) |
| `RM_Brindeth` | TheSump | 18 | 8 (default) (144) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; its non-WoodLog logs DO drop on fruit | not tree-class: keeps the ruled cycle (RS §4); no logs | as its cycle today | 1.15 visual and yields WoodLog (Q3) |
| `RM_Pusberry` | Wasteland | 9 | 30 (270) | dry native, ×10 wet / ×0.1 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | 10,440 L ≈ 26 spills; river ~261 d | 10 RawBerries (fruit); logs ? ; 2-4 sprouts | berry bush on TreeBase (1.6 visual): a tree? (Q2) |
| `RM_VaultRoot` | Wasteland | 18 | 45 (810) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 31,680 L ≈ 79 spills; river ~792 d | 22 WoodLog; 2-4 sprouts |  |
| `RM_Dulloth` | Webwork | 25 | 8 (default) (200) | wet native, ×4 always; withers at maturity, dies, 1-2 sprouts | 7,000 L ≈ 18 spills; river ~175 d (wet biome: Q11) | no harvest: 2-4 sprouts only | 4-5.2 visual, no harvest |
| `RM_Kollavane` | Webwork | 35 | 8 (default) (280) | wet native, ×2.5 always; withers at maturity, dies, 1-2 sprouts; drops no logs (WoodLog guard) | 9,800 L ≈ 24 spills; river ~245 d (wet biome: Q11) | 50 WoodLog; 2-4 sprouts | harvestTag Standard but WoodLog 50 |
| `RM_Rockfinger` | WeepingStones | 60 | 8 (default) (480) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs (WoodLog guard) | 16,800 L ≈ 42 spills; river ~420 d | 16 WoodLog; 2-4 sprouts |  |


## 8. Open questions for the owner (nothing here is decided)

1. **Q1 Trajectory model.** Water buys days of a tree's life at a fixed exchange (section 3, PROPOSED 40 L per day of
   life, so one 400 L spill = +10 days). Is "litres buy life-days" the reading of "advance a bit along its trajectory"?
2. **Q2 What is tree-sized?** PROPOSED: visual size ≥ 2.0 or vanilla `TreeBase`, and a life of ≥ 60 days. Where is
   the line (e.g. is `RM_Pusberry`, a TreeBase berry bush at 1.6, a tree)?
3. **Q3 Small plants that yield wood today** (`RM_HeatsinkFungus` 0.6, `RM_Slackwax` 1.1, `RM_Brindeth` 1.15,
   `RM_Plant_Thumbstalk` 1.5, `RM_IlbareenDead`, `RM_VellokReed` a 5-day reed with 20 logs, `RM_Skulltop` 0.7):
   stop yielding wood (economy item), or count as trees?
4. **Q4 Litres or events?** Proportional to litres (long life needs a lot of water, as said) or a fixed fraction of the
   remaining life per water event (every tree bursts after the same number of spills)?
5. **Q5 "Potentially burst":** at a water-driven end of life, does every tree burst, or roll its rupture odds (1 in 3
   default) and otherwise fall over dead with its logs and no blast?
6. **Q6 Old age without water:** stays vanilla's quiet death, or also bursts?
7. **Q7 Pyrelands grass sprouts:** with bursting back on, keep the 6-9 sprouts ("spread itself super-fast")?
8. **Q8 The Rot's `None` rows:** under the wet rulings, do the 34 Rot plants now on `None` fruit and wither like
   jungle natives, or stay "×4 but never cycle"?
9. **Q9 The Rot's giant fungi** (Pale Tree, Arpeau, Nogtyl, Shinecap, Flakespire, Tree Mushroom in the Abyss): trees
   (section 3-4, burst at end of life) or fungi (wet cycle at maturity)?
10. **Q10 The Sheen as water** for Rot plants (T2 "Only for adapted plants")? Moot for wet natives, matters if any
    Rot plant stays dry-native.
11. **Q11 Jungle trees** (every Greentide, Miasma, Fever Wood, Webwork, Contagion tree): (a) vanilla speed, burst only
    when flood or player water makes them drink; or (b) ×4 to maturity, then vanilla ageing, burst at end of life?
    Either way they stop withering at maturity.
12. **Q12 Sweetline's burst:** it yields wool and cannot be chopped for wood today. Does its burst drop logs too?
    Same for the other non-wood trees: Corrisk (dye), Lumbrel and Jogan (fruit), Hydenock (dye), Shinecap (slime).
13. **Q13 "VERY slow-growing and long lived":** raise Sweetline's growDays above 240, its life above 8× growth, or both?
    (A longer growth also slows its wool, which re-grows from 0.05.)
14. **Q14 Unlimited-life trees** (`RM_Ollim`, `RM_KneelOllim`, `RM_PaleTree`, `RM_Skulltop`): never burst by water, or
    give them a life for this mechanic only?
15. **Q15 Contagion trees** (`RM_Eyebark`, `RM_HalfmadeTree`, `RM_HalfmadeTreeBlighted`): does their contaminated
    Rupture become the end-of-life event, keeping its own odds (OQ-5)?
16. **Q16 Burst fruit for log trees:** a new per-plant `burstFruit` (Greatbole → `RM_GreatboleFruit`)? Which other
    log trees have a fruit we ship?
17. **Q17 Burst sprouts:** 2-4 of its own seedlings (PROPOSED) for a giant?

## 9. Build delta when he has ruled (for FOUNDRY; sizes INFERRED)

| # | where | change | size |
|---|---|---|---|
| T1 | `RM_ExplosiveGrowthRegistry.cs:314` | `woody` → `treeClass` (section 2 test), new profile fields `burstFruit`, life days | S |
| T2 | `Kernel/RM_ExplosiveGrowthKernel.cs:145-156` | tree-class: no ×10 / ×4 rate and no `treeRatio`; dry ×0.1 kept | S |
| T3 | new: tree drink (map component pass) | litres drunk from spill filth / poured mark / channel, capped per day on continuous sources; advance growth then age; swell tell per drink | M |
| T4 | `RM_TopResolver.cs` | tree-class never runs `Fire` at maturity; new end-of-life burst: logs (bypassing the `WoodLog` guard at :376-377 for this path only), fruit, sprouts, Burst top | M |
| T5 | `Plant.TickLong` prefix (RS D13) | detect the water-driven end of life before vanilla's `Dying` check and route it to T4 | S |
| T6 | `RM_ExplosiveGrowthRoster.xml:27-31`, `selftest_explosivegrowth_archetype_seed.py:48-51` | Pyrelands grass bursts (section 5) | S |
| T7 | both rosters' `<wetNativeBiomes>` | add `RM_TheRot`, `RUT_TheRot` (section 6) | S |
| T8 | `validation.py`, fuzz, proof `FirstOf(..., woody)` (`RM_ExplosiveGrowthProof.cs:203-210,269`) | the ×6.25 tree chain becomes the drink/advance chain; a Greatbole-never-withers row | M |
