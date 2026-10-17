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
was decided by us: the owner ruled every question by card on 2026-10-17 (section 8), and this note is written to
those rulings. **No code was changed by this pass.**

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
   run ×2.5 to maturity and then wither. `RM_Veluthar` (growDays 55) withers at about day 22 of a 440-day life.
   Every Greentide, Miasma, Fever Wood and Webwork tree in the table (section 7) does the same.
3. **A tree's cycle yields no logs, no sprouts worth the name (its seedlings), and fruit only if its harvest is not wood.**
4. **The Sweetline tree is not "woody" at all**: its harvest is `RM_SweetlineWool` with `harvestTag` Standard
   (`src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml:52-57`), so it runs the full dry-native
   ×10 wet / ×0.1 dry. Its `None` top (`RM_ExplosiveGrowthRoster.xml:89`) stops the cycle, but not the rate: a spill
   takes it 10× faster through a 240-day growth, the opposite of "VERY slow-growing". The same blind spot catches every
   `TreeBase` plant whose harvest is not logs (Corrisk, Lumbrel, Shinecap, Pusberry, the two SW port trees).
5. **Pyrelands grass never bursts**: `RM_FE_Plant_Quickgrass` and `RM_FE_Plant_EmberGrass` carry
   `<ruptureChance>0</ruptureChance>` (`RM_ExplosiveGrowthRoster.xml:30-31`). Reversed by this ruling (section 5).

---

## 0. Greatbole is not part of this design

Owner, 2026-10-17, by card write-in: *"Greatbole have an entirely different mechanic that's well articulated, NOT part
of the bursting discussion. They express the same mechanic through their self healing."* The greatbole's mechanic is
its healing: `design/Jawa/worldbuilding/biomes/kits/greatbole_harvest_spec.md` (§1 the healing race, §2b "The violent
healing", :65-74 *"This makes the tree's identity and its danger the same mechanic"*), built as
`src/RimMandrake/Greentide/Source/RM_CompGreatboleHarvestLadder.cs`. This note does not touch it. `RM_Greatbole` (the
fellable tree) is **excluded** from every tree-burst rule, table row and build line below, including the jungle-tree
rule of §6a; the build leaves its ExplosiveGrowth handling as it is.

## 2. Which plants are trees (RULED Q2, Q3)

*"grass cannot make wood of course. Wood should only come from tree-sized plants."*

- **A tree is a plant whose `visualSizeRange` max is 3.0 or more** (Q2, by card: "SIZE 3.0+ ONLY"). Size alone: no
  `TreeBase` clause, no lifespan clause. Read from the def, never from a list.
- **Fungi are never trees** (Q9, by card: "ALL FUNGI (no tree rules)"), whatever their size: the Rot's Pale Tree,
  Arpeau, Nogtyl, Shinecap, Flakespire, and the Abyss Tree Mushroom by name; `RM_GiantAgariTox` (Cauldron, a giant
  agaric at 4.5) is a fungus by the same principle though not on his list (FLAGGED for the sitting). The build marks
  fungi by a roster field, not by name-matching.
- **A plant under 3.0 stops giving wood** (Q3, by card: "stop giving wood"). Fifteen defs today
  (section 7, "stops giving wood"). The new harvest per def is owned by `PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE`;
  until then the build's interim is no `WoodLog` in their harvest.
- Grass never yields wood (his words); Pyrelands grass included.

| | tree (≥ 3.0, not a fungus) | everything else |
|---|---|---|
| growth on water | **trajectory advance** (§3) | the ruled rates (RS §2.5) |
| maturity cycle | **none**: the end of life is the event (§4) | unchanged (RS §4) |
| wood | logs in the burst | **never** (keeps `ff4759f445`'s guard) |
| `treeRatio` 0.625 | retired (it existed only to slow the ×10) | n/a |

## 3. Water advances a tree along its life (RULED Q1, Q4)

*"a bursting event for a tree should only advance such a massive plant a bit along its trajectory (long, long lifespan
would need to absorb a LOT of water to "burst.")"*

Ruled (Q1/Q4, by card): **litres buy days of life**, at **40 L per day of life** (the proposal taken as is).

- A tree on a WET cell **drinks**: litres leave the source (spill filth, poured mark, channel cell). From a continuous
  source (river, mud, a running flood) it drinks at most `treeDrinkLitresPerDay`, PROPOSED **40 L/day** (one extra day of
  life per day, life runs ×2).
- Every 40 L drunk moves the tree one day along its life: growth while immature (growth += 1 / growDays), age once mature.
- **Litres to reach the end of life = remaining life days × 40.** Long life means a lot of water, by construction.
- On dry ground a dry-biome tree keeps the ruled dry rate and dormancy (×0.1 growth and ageing, RS §5.2).
- The swell tell (`Kernel/RM_ExplosiveGrowthKernel.cs:53-61`) plays once per drink event: a spill on a tree reads as
  "it drank and grew".
- **Immortal trees** (unlimited life, `lifespanDaysPerGrowDays` 0): **never burst; water still gives a growth spike**
  (Q14, by card). Follow-up card: "Immortal wins" for Pale Tree and Skulltop (no wither, no burst), and Kneeling Ollim is raised to 3.0 (§8).
- **Jungle trees** (wet-biome trees) are not advanced by litres: §6a.

Worked through (spill 400 L, `design/RimMandrake/liquid_litres_2026-10-16.md:73`):

| tree | growDays | life days | one spill | spills to end of life from maturity | roots in a river |
|---|---|---|---|---|---|
| `RM_SweetlineTree` (today's numbers; Q13 raises both) | 240 | 1,920 | +4.2 % growth | 168 (67,200 L) | ~1,680 days |
| `RM_VaultRoot` | 18 | 810 | +56 % growth | 79 (31,680 L) | ~792 days |
| `RM_CrackedThornwood` | 15 | 600 | +67 % growth | 59 (23,400 L) | ~585 days |
| `RM_Ollim` | 400 | unlimited | +2.5 % growth | never | never |

## 4. Death and the burst (RULED Q5, Q6, Q12, Q15, Q16, Q17)

*"How about this then. Every tree that hits a water-driven death bursts. But a natural death that isn't water-driven
can just fall over dead."* (Q5/Q6, by card write-in.)

- **Water-driven death bursts, always.** A tree whose age passes `LifespanDays` on a step paid for by drinking (§3)
  bursts: no odds roll.
- **Natural death falls over dead**: vanilla's quiet death of old age, untouched.
- **Jungle trees** burst at their end of life (Q11, §6a).
- **What a burst yields** (Q12, Q16/17, by card):

| part | ruled | source |
|---|---|---|
| **logs** | every tree: its own wood (`harvestYield` of a `WoodLog` or wood-like log harvest at full growth); a tree whose harvest is not wood also gives logs (Q12 "logs PLUS their own product"), count owed by the economy item (interim PROPOSED: a per-plant `burstLogs` field) | its def |
| **its own product** | a non-wood tree's harvest (wool, dye, fruit, sap) at `harvestYield` × `produceFactor`; a log tree's own fruit **if it has one** (Q16, per-plant `burstFruit`) | its def / roster |
| **seedlings** | **2-4** of its own (Q17), respecting built ground | `RM_SproutRing.Sow` |
| **the blast** | the Burst top (sound, scatter, `burstHurtsPawns`) | existing `Burst` |

- **Contagion trees** (`RM_Eyebark`, `RM_HalfmadeTree`): their contaminated Rupture **is** their burst (Q15, by card).
  `RM_HalfmadeTreeBlighted` (2.8) is not a tree under Q2 and keeps its Rupture as its cycle.
- `DropProduce`'s wood guard (`RM_TopResolver.cs:376-377`) stays for every non-tree outcome; the tree burst gets its own
  drop path with logs. RS §5.1 "Wood is never a cycle drop" stays true: a tree no longer cycles.

## 5. Pyrelands grass bursts too (RULED Q7)

He took option (2) "Let Pyrelands grass burst too", reversing the build's reading of C3, and **keeps 6-9 sprouts**
(Q7, by card). Code for FOUNDRY:

| file | change |
|---|---|
| `src/RimMandrake/ExplosiveGrowth/Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml:27-31` | remove `<ruptureChance>0</ruptureChance>` from the `RM_FE_Plant_Quickgrass` and `RM_FE_Plant_EmberGrass` rows (default 1 in 3); keep `fireAdapted` and `sproutCount 6~9`; comment cites this ruling |
| `src/RimMandrake/Utils/selftest_explosivegrowth_archetype_seed.py:48-51` | `ruptureOdds "0"` for both grasses becomes the default |
| `src/RimMandrake/ExplosiveGrowth/archetype_seed.py:119` | comment only |
| `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md` §4.1 | corrected in `0db128f17a` |

## 6. The Rot follows the wet-biome rulings (RULED Q8, Q9, Q10)

*"I am realizing the Rot should likely follow wet-biome rulings."*

**The Rot** is `RM_TheRot` (mod `src/RimMandrake/TheRot`, twin `RUT_TheRot`), the fungal jungle: *"The fungi own all
the moisture they need; what falls here is emitted, not received"*, no water rain ever, the Sheen (white slime) its only
precipitation (`design/Jawa/worldbuilding/biomes/the_rot.md` §"The Sheen"). **The wet-biome rulings** are C1/C2/WP3
(`explosive_growth_rulings_2026-10-16.md`): ×4 at home always, fruit prolifically at maturity, then wither leaving a
few sprouts (RS §4.2).

Today (MEASURED) the Rot is not in `<wetNativeBiomes>` (`RM_ExplosiveGrowthRoster.xml:232-238`), so its plants seed as
dry natives, and 34 of the 36 plants in `RM_TheRot`'s `wildPlants` carry the `None` top (all but `RM_AmbrosyxFungus`
and `RM_TollukCap`).

Ruled:
- `RM_TheRot` / `RUT_TheRot` join `<wetNativeBiomes>`: Rot natives are wet natives.
- **Q8 (by card): yes, the `None` plants cycle like wet natives** — their `None` rows come off.
- **Q9 (by card): the Rot's giant fungi are all fungi**, no tree rules (§2).
- **Q10: the Sheen is moot.** Rot plants are wet natives now, and a wet native ignores the water on its cell
  (`RM_MapComponent_ExplosiveGrowth.cs:295`), so whether the Sheen waters them changes nothing.

## 6a. Jungle trees (RULED Q11)

Every Greentide, Miasma, Fever Wood, Webwork and Contagion tree (**except `RM_Greatbole`, §0**): **×4 to maturity,
then normal ageing; burst only at end of life** (Q11, by card). The wither-at-maturity that kills them today
(§1 point 2) goes. They are not advanced by litres (the jungle is the water; INFERRED from Q11's "normal ageing"),
and their end of life is a full burst (§4).

## 6b. Sweetline (RULED Q13)

*"Sweetline trees should be VERY slow-growing and long lived, so spilling water on them DOES produce a growth spike but
will almost certainly not cause it to reach an end of life event."* Q13 (by card): **both slower growth (more than 240
days) and a longer life.** Today: growDays 240, lifespan ×8 (1,920 days), and it is not "woody", so a spill speeds it
×10 (§1 point 4). Under this note it is a tree (visual 7.7-10): a spill is a growth spike (+40 L/day of life), and
its burst gives logs plus wool (Q12) plus 2-4 seedlings. Ruled (follow-up card): growDays **480**,
`lifespanDaysPerGrowDays` **12** (5,760 days, ~528 spills from maturity); its wool re-grows from
0.05 growth (`RM_SweetlineTree.xml:57`), so slower growth slows the wool too.

---

## 7. Case by case: every huge or tree-like plant we ship

**Census (MEASURED 2026-10-17, re-run on the Q2 ruling):** every `ThingDef` under `src/` with its `ParentName` chain
resolved; a row is here if it yields wood, inherits `TreeBase`, or draws at visual max ≥ 4. **65 plants** (with
`RM_Greatbole` removed, §0): **39 trees** (≥ 3.0, not fungi; Kneeling Ollim raised to 3.0 by ruling), **10 fungi**, **16 not trees** (15 of which stop
giving wood). "life days" = `growDays × lifespanDaysPerGrowDays` (default 8). Current behaviour from both rosters as built.
Water-to-burst uses the ruled 40 L per day of life and the 400 L spill. Yields are not tuned here
(`PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE`).

Six jungle plants are trees only by the size-only rule (`RM_Brakkel`, `RM_Tumbel`, `RM_Sarquin`, `RM_Wollick`,
`RM_Illurin`, `RM_Dulloth`: PlantBase, no wood today); under Q2/Q12 they become trees that burst with logs.
Not in the table: donor flora enrolled by roster row only (`AB_JungleTree`, `AB_MangroveTree`, `AB_MangrovePalm`,
`AB_ParasiticMangrove`, `AB_SlimyTree`, `AB_LargeSlimyTree`, `AB_HalfAlienTree`, `AB_AlienTree`,
`AB_AlienTree_Polluted`, `AB_KeeningCordax`): defs outside `src/`, numbers UNMEASURED; the same rule applies by the same
test. `RUT_Placeholder_GreentideGiantTree` is a dead roster row (def retired).

| plant | mod | growDays | lifespanDaysPerGrowDays (life days) | visual max | current burst behaviour (MEASURED) | ruled class | water-to-burst (from maturity) | burst yield | note |
|---|---|---|---|---|---|---|---|---|---|
| `RM_GiantFibreStalk` | Abyss | 14 | 8 (default) (112) | 5.0 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | tree | 3,920 L ≈ 10 spills; river ~98 d | 10 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_TreeMushroom` | Abyss | 15 | 8 (default) (120) | 15.2 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | fungus (Q9) | no tree rules; its archetype's cycle | as its cycle | |
| `RM_Wickwood` | Abyss | 14 | 8 (default) (112) | 3.6 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | tree | 3,920 L ≈ 10 spills; river ~98 d | 18 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_GiantAgariTox` | Cauldron | 25 | 8 (default) (200) | 4.5 | dry native, ×10 wet / ×0.1 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | fungus (Q9 principle; not on his list) | no tree rules; its archetype's cycle | as its cycle | |
| `RM_TreeMartyr` | Cauldron | 10 | 40 (400) | 3.0 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | tree | 15,600 L ≈ 39 spills; river ~390 d | 15 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_TwistingThornwood` | Cauldron | 15 | 40 (600) | 3.0 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | tree | 23,400 L ≈ 58 spills; river ~585 d | 25 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Eyebark` | Contagion | 16 | 10 (160) | 3.4 | wet native, ×2.5 always; contaminated Rupture at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | its contaminated Rupture IS the burst (Q15) | |
| `RM_HalfmadeTree` | Contagion | 10 | 8 (80) | 3.0 | wet native, ×2.5 always; contaminated Rupture at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | its contaminated Rupture IS the burst (Q15) | |
| `RM_HalfmadeTreeBlighted` | Contagion | 5 | 4 (20) | 2.8 | wet native, ×2.5 always; contaminated Rupture at maturity, dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | 2.8: not a tree; its Rupture stays its cycle |
| `RM_Ammeth` | FeverWood | 17 | 8 (default) (136) | 1.4 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_CorriskTree` | FeverWood | 10 | 8 (default) (80) | 10.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 30 Dye + 2-4 seedlings (Q12) | |
| `RM_LumbrelTree` | FeverWood | 10 | 8 (default) (80) | 8.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 40 RM_RawLumbrelFruit + 2-4 seedlings (Q12) | |
| `RM_Sodderel` | FeverWood | 22 | 8 (default) (176) | 2.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Varnoth` | FeverWood | 30 | 8 (default) (240) | 2.5 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_CrackedThornwood` | FloodedCanyon | 15 | 40 (600) | 3.0 | dry native, ×6.25 wet / ×0.0625 dry; bursts at maturity (1 in 1), dies; drops no logs | tree | 23,400 L ≈ 58 spills; river ~585 d | 25 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Harrovaq` | FloodedCanyon | 20 | 40 (800) | 2.4 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Plant_Thumbstalk` | GelatinousSlime | 12 | 14 (168) | 1.5 | dry native, ×6.25 wet / ×0.0625 dry; Slime top at maturity; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Brakkel` | Greentide | 12 | 8 (default) (96) | 4.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 10 RM_BrakkelFruit + 2-4 seedlings (Q12) | PlantBase, no wood: a tree by the size-only rule |
| `RM_Brunnock` | Greentide | 140 | 8 (default) (1,120) | 6.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 30 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Cundral` | Greentide | 20 | 8 (default) (160) | 2.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Ghemmel` | Greentide | 30 | 8 (default) (240) | 6.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | ? WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Gorbeleth` | Greentide | 24 | 8 (default) (192) | 3.0 | wet native, ×2.5 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 8 RM_GorbelethToxin + 2-4 seedlings (Q12) | |
| `RM_Illurin` | Greentide | 16 | 8 (default) (128) | 7.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 2-4 seedlings | PlantBase, no harvest: a tree by the size-only rule |
| `RM_Kaddrath` | Greentide | 48 | 8 (default) (384) | 9.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | ? WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Mirrelbole` | Greentide | 22 | 8 (default) (176) | 4.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 18 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Mourvel` | Greentide | 45 | 8 (default) (360) | 8.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | ? WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Nemmer` | Greentide | 26 | 8 (default) (208) | 5.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 15 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Quathis` | Greentide | 18 | 8 (default) (144) | 4.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 12 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Sarnstilt` | Greentide | 40 | 8 (default) (320) | 7.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 20 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Sarquin` | Greentide | 14 | 8 (default) (112) | 4.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 9 RM_SarquinSap + 2-4 seedlings (Q12) | PlantBase, no wood: a tree by the size-only rule |
| `RM_Thalquith` | Greentide | 20 | 8 (default) (160) | 4.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 10 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Tumbel` | Greentide | 16 | 8 (default) (128) | 5.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 8 RM_TumbelGourd + 2-4 seedlings (Q12) | PlantBase, no wood: a tree by the size-only rule |
| `RM_Veluthar` | Greentide | 55 | 8 (default) (440) | 10.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 35 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Vurmeloth` | Greentide | 50 | 8 (default) (400) | 5.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 22 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Wollick` | Greentide | 13 | 8 (default) (104) | 4.0 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 11 RM_WollickTuber + 2-4 seedlings (Q12) | PlantBase tuber plant: a tree by the size-only rule |
| `RM_Zhorrel` | Greentide | 28 | 8 (default) (224) | 5.0 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 16 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_ThrakkCap` | LanternDeeps | 30 | 8 (default) (240) | - | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not a tree (no size in def) | ruled cycle (RS §4) | **stops giving wood** (Q3) | no visualSizeRange in the def: size UNMEASURED, read as not a tree |
| `RM_VellokReed` | LanternDeeps | 5 | 9 (45) | 2.5 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_SweetlineTree` | LeaningScrub | 240 | 8 (default) (1,920) | 10.0 | dry native, ×10 wet / ×0.1 dry; rate only, never cycles | tree | 67,200 L ≈ 168 spills; river ~1,680 d | logs (count owed) + 20 RM_SweetlineWool + 2-4 seedlings (Q12) | slower growth AND longer life (Q13) |
| `RM_Shadespire` | LongShade | 40 | 60 (2,400) | 3.0 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | tree | 94,400 L ≈ 236 spills; river ~2,360 d | 40 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Brelloch` | Miasma | 20 | 8 (default) (160) | 1.6 | wet native, ×2.5 always; withers at maturity, dies | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_IlbareenDead` | Miasma | 1 | 8 (default) (8) | 2.0 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Ollamane` | Miasma | 18 | 8 (default) (144) | 3.6 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 18 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Quennath` | Miasma | 15 | 8 (default) (120) | 1.8 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Thessamor` | Miasma | 25 | 8 (default) (200) | 3.4 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 22 WoodLog + own fruit if any + 2-4 seedlings | |
| `RSW_Plant_HydenockTree_Wild` | SWBestiary | 10 | 8 (default) (80) | 10.0 | dry native, ×10 wet / ×0.1 dry; Flush: survives, drops produce | tree | 2,800 L ≈ 7 spills; river ~70 d | logs (count owed) + 30 Dye + 2-4 seedlings (Q12) | |
| `RSW_Plant_JoganTree_Wild` | SWBestiary | 10 | 8 (default) (80) | 8.0 | dry native, ×10 wet / ×0.1 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | tree | 2,800 L ≈ 7 spills; river ~70 d | logs (count owed) + 40 RSW_RawJoganFruit + 2-4 seedlings (Q12) | |
| `RM_KneelOllim` | Stillsand | 400 | 0 (unlimited) (unlimited) | 2.6 → 3.0 (ruled) | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | tree (raised to 3.0) | never bursts; water = growth spike (Q14) | 5 RM_OllimWood (keeps wood) | immortal like Ollim |
| `RM_Ollim` | Stillsand | 400 | 0 (unlimited) (unlimited) | 5.5 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | tree | never bursts; water = growth spike (Q14) | 15 RM_OllimWood + own fruit if any + 2-4 seedlings | immortal: never bursts, water = growth spike (Q14) |
| `RM_Slackwax` | TerminalBiomes | 10 | 8 (default) (80) | 1.1 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_HeatsinkFungus` | TheForge | 5.5 | 8 (default) (44) | 0.6 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Arpeau` | TheRot | 5 | 9 (45) | 10.0 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | fungus (Q9) | no tree rules; Rot: wet-native cycle, ×4, fruit, wither, few sprouts (Q8) | as its cycle | |
| `RM_FlakespireFungus` | TheRot | 18 | 8 (default) (144) | 2.0 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | fungus (Q9) | no tree rules; Rot: wet-native cycle, ×4, fruit, wither, few sprouts (Q8) | as its cycle | |
| `RM_GreenArpeau` | TheRot | 5 | 9 (45) | 2.5 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | fungus (Q9) | no tree rules; Rot: wet-native cycle, ×4, fruit, wither, few sprouts (Q8) | as its cycle | |
| `RM_Nogtyl` | TheRot | 7 | 9 (63) | 12.0 | wet native, ×2.5 always; rate only, never cycles | fungus (Q9) | no tree rules; Rot: wet-native cycle, ×4, fruit, wither, few sprouts (Q8) | as its cycle | |
| `RM_NogtylMarsh` | TheRot | 7 | 9 (63) | 2.5 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | fungus (Q9) | no tree rules; Rot: wet-native cycle, ×4, fruit, wither, few sprouts (Q8) | as its cycle | |
| `RM_PaleTree` | TheRot | 25 | 0 (unlimited) (unlimited) | 6.0 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | fungus, immortal | "Immortal wins": never withers or bursts; growth spike only | as today (harvest only) | follow-up card |
| `RM_Shinecap` | TheRot | 30 | 8 (default) (240) | 3.0 | dry native, ×10 wet / ×0.1 dry; rate only, never cycles | fungus (Q9) | no tree rules; Rot: wet-native cycle, ×4, fruit, wither, few sprouts (Q8) | as its cycle | |
| `RM_Skulltop` | TheRot | 8 | 0 (unlimited) (unlimited) | 0.7 | dry native, ×6.25 wet / ×0.0625 dry; rate only, never cycles | fungus, immortal | "Immortal wins": never withers or bursts; growth spike only | as today (harvest only) | follow-up card |
| `RM_Brindeth` | TheSump | 18 | 8 (default) (144) | 1.15 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | not a tree (< 3.0) | ruled cycle (RS §4) | **stops giving wood** (Q3) | |
| `RM_Pusberry` | Wasteland | 9 | 30 (270) | 1.6 | dry native, ×10 wet / ×0.1 dry; 1/3 Burst else fruit + 4-7 sprouts; dies | not a tree (< 3.0) | ruled cycle (RS §4) | as its cycle | |
| `RM_VaultRoot` | Wasteland | 18 | 45 (810) | 5.2 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | tree | 31,680 L ≈ 79 spills; river ~792 d | 22 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Dulloth` | Webwork | 25 | 8 (default) (200) | 5.2 | wet native, ×4 always; withers at maturity, dies | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | logs (count owed) + 2-4 seedlings | PlantBase, no harvest: a tree by the size-only rule |
| `RM_Kollavane` | Webwork | 35 | 8 (default) (280) | 4.8 | wet native, ×2.5 always; withers at maturity, dies; drops no logs | tree | none: ×4 to maturity, normal ageing, bursts at end of life (Q11) | 50 WoodLog + own fruit if any + 2-4 seedlings | |
| `RM_Rockfinger` | WeepingStones | 60 | 8 (default) (480) | 4.8 | dry native, ×6.25 wet / ×0.0625 dry; 1/3 Burst else fruit + 4-7 sprouts; dies; drops no logs | tree | 16,800 L ≈ 42 spills; river ~420 d | 16 WoodLog + own fruit if any + 2-4 seedlings | |


## 8. The owner's rulings (by card, 2026-10-17; write-ins verbatim)

| Q | question | ruling |
|---|---|---|
| Q1 | trajectory model | litres buy days of life, 40 L per day |
| Q2 | what is tree-sized | **size 3.0+ only** |
| Q3 | small plants that yield wood | stop giving wood |
| Q4 | litres or events | litres (follows Q1) |
| Q5/Q6 | "potentially burst"; old age | *"How about this then. Every tree that hits a water-driven death bursts. But a natural death that isn't water-driven can just fall over dead."* |
| Q7 | Pyrelands grass sprouts | keep 6-9 |
| Q8 | the Rot's `None` plants | yes, cycle like wet natives |
| Q9 | the Rot's giant fungi | all fungi, no tree rules |
| Q10 | the Sheen as water | moot (Rot plants are wet natives) |
| Q11 | jungle trees | ×4 to maturity, then normal ageing; burst only at end of life |
| Q12 | non-wood trees' burst | logs plus their own product |
| Q13 | Sweetline | both slower growth (> 240 days) and longer life |
| Q14 | immortal trees (Ollim, Kneeling Ollim, Pale Tree, Skulltop) | never burst; water still gives a growth spike |
| Q15 | Contagion trees | their contaminated rupture IS their burst |
| Q16/Q17 | burst yield | own fruit if it has one + 2-4 seedlings |
| Greatbole | — | *"Greatbole have an entirely different mechanic that's well articulated, NOT part of the bursting discussion. They express the same mechanic through their self healing"* (§0) |

**Follow-up rulings (by card, 2026-10-17):**

| item | ruling |
|---|---|
| `RM_PaleTree`, `RM_Skulltop` (Q9 fungus vs Q14 immortal) | **"Immortal wins"**: they never wither or burst; water gives a growth spike only (they stay out of the wet-native cycle) |
| `RM_KneelOllim` (2.6, named in Q14) | write-in *"Make it 3.0"*: its visual size is raised to 3.0, so it is a tree, immortal like `RM_Ollim` (never bursts, growth spike only); it keeps its wood |
| Sweetline numbers | **"Accept 480 days, 12x life"**: growDays 480, `lifespanDaysPerGrowDays` 12 (5,760 days) |
| `RM_GiantAgariTox` | treated as a fungus by Q9's principle (not on his list; unchanged) |

## 9. Build delta (ruled; for FOUNDRY, sizes INFERRED)

| # | where | change | size |
|---|---|---|---|
| T1 | `RM_ExplosiveGrowthRegistry.cs:314` | `woody` → `isTree` = visual max ≥ 3.0 and not a fungus (roster `fungus` flag on the 10 fungi); exclude `RM_Greatbole` | S |
| T2 | `Kernel/RM_ExplosiveGrowthKernel.cs:145-156` | trees: no ×10 rate, no `treeRatio`; dry ×0.1 and dormancy kept; jungle trees ×4 to maturity then ×1 ageing | S |
| T3 | new: tree drink pass | litres from spill / poured / channel, capped 40 L/day on continuous sources; 40 L = one day of life (growth, then age); swell tell per drink; unlimited-life trees grow only | M |
| T4 | `RM_TopResolver.cs` | trees never run `Fire` at maturity; new end-of-life burst: logs (own path past the `WoodLog` guard at :376-377), own product / `burstFruit`, 2-4 seedlings, Burst top; Contagion trees use Rupture | M |
| T5 | `Plant.TickLong` prefix (RS D13) | an age step bought by drinking that crosses `LifespanDays` → T4; a natural crossing → vanilla death | S |
| T6 | 15 defs under 3.0 (section 7) | drop `WoodLog`/log harvests (interim, pending the economy item) | S |
| T7 | `RM_ExplosiveGrowthRoster.xml:27-31`, `selftest_explosivegrowth_archetype_seed.py:48-51` | Pyrelands grass bursts, 6-9 sprouts kept | S |
| T8 | both rosters | `RM_TheRot`/`RUT_TheRot` into `<wetNativeBiomes>`; drop the `None` rows of Rot plants | S |
| T9 | `RM_SweetlineTree.xml`, Stillsand `RM_KneelOllim` | Sweetline growDays 480, `lifespanDaysPerGrowDays` 12 (ruled); Kneeling Ollim `visualSizeRange` max to 3.0 (ruled), so it is a tree and keeps its wood | S |
| T11 | registry | immortal plants (`RM_Ollim`, `RM_KneelOllim`, `RM_PaleTree`, `RM_Skulltop`): never wither or burst, water = growth spike only (overrides the Rot wet-native cycle for the two fungi) | S |
| T10 | `validation.py`, fuzz, proof `FirstOf(..., woody)` (`RM_ExplosiveGrowthProof.cs:203-210,269`) | the ×6.25 chain becomes drink/advance; rows: jungle tree survives maturity, water-driven death bursts, natural death falls, Ollim never bursts | M |
