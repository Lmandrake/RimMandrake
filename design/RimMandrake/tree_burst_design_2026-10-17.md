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
