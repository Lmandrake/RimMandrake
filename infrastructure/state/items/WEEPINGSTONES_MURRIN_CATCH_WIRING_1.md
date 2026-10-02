# WEEPINGSTONES_MURRIN_CATCH_WIRING_1 — make the stocked pool's baseline fish (the murrin) catchable: floor resident and catch item

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier**, `mandrake.rm.weepingstones`. Design:
`design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §1 (c) 1, §4 row 0, §8. Ruling: build first, **land what was decided plus the giant's story**
(decision taken by question card 2026-10-02 12:53 PDT). Sea/pool law (owner, 2026-09-21): a fish owes **two**
defs, a floor resident in `<wildAnimals>` and a catchable entry in `<fishTypes>`.

## What exists

- `RM_Murrin` ThingDef + PawnKindDef (`Defs/ThingDefs_Races/RM_StockedPoolFauna.xml`), `RM_MurrinMeat`,
  `RM_MurrinBreedingStock`, `RM_CookMurrinBroth`, `RM_MealMurrinBroth`, `RM_AteMurrinBroth`.
- The six other pool fish each have an `RM_<Name>Catch` item in `Defs/ThingDefs_Items/RM_StockedPoolCatchItems.xml`
  and a `fishTypes` row. **No `RM_MurrinCatch`** exists anywhere in `src/` (MEASURED 0, 2026-10-02).
- `RM_Murrin` is on no `wildAnimals` and no `fishTypes`. Its wiring is cited as *"owed to FISH_BY_BIOME_1's
  successor"* in the BiomeDef header (l.53), `About.xml` l.111, `RM_WeepingStonesNatives.xml` l.14 and
  `RM_MapComponent_PoolStock.cs` l.51. **No item of that name exists in the ledger**; this item is that successor.
- Art: pawn art exists (artpipe `done/weepingstones_murrin_{east,north,south}`, `_artsrc/`). The catch item
  has none (art list `weepingstones_turn1_2026-10-02.csv`).

## spec

1. `RM_Murrin` inline on `RM_WeepingStones` `<wildAnimals>` (element form, `<RM_Murrin>x</RM_Murrin>`, never
   `<li>`); commonality an `// INVENTED` first value, the gentlest and most common of the pool fish.
2. `RM_MurrinCatch` in `RM_StockedPoolCatchItems.xml`, same shape as `RM_SkarrinCatch`, wired into the
   biome's `fishTypes` (the commonest, gentle row).
3. The netting job (`RM_JobDriver_NetPoolBreeder`) can net murrin stock from the wild into
   `RM_MurrinBreedingStock`, so a stocked pool can start from its baseline rather than its biters.
4. Delete every "owed to FISH_BY_BIOME_1's successor" citation (four sites above); the comment says what is wired.

## criteria

- `jawa/get_defs` `ThingDef/RM_MurrinCatch`: `foundCount` 1.
- Loaded `RM_WeepingStones.wildAnimals` contains `RM_Murrin` and its `fishTypes` contains `RM_MurrinCatch` (def read).
- On a Weeping Stones quicktest map: murrin present wild in a pool; fishing yields `RM_MurrinCatch`; a net job
  produces `RM_MurrinBreedingStock`.
- `grep -rn FISH_BY_BIOME_1 src/RimMandrake/WeepingStones` returns nothing.
