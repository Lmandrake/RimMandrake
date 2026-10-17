# THIRST_RULES_BUILD_SALT_OFF_THE_MENU — build progress (BENCH AFK, 2026-10-17)

## Status
ALL SLICES PUBLISHED (last 71153b893b). Item not closed: live rows owed (see below).

## Slice 1: rule breaks in today's code — DONE `037fbdf94d`
- per-row `useClass` on LiquidDef (generator USE_CLASS table, refuses an unclassified row): Potable fresh/icy/5 coloured;
  BreakOnly salt+brine; LastResort toxic+4 slimes; Never boiling/acid/liquor/tar/propane/chemfuel/lava.
- auto-fill and fill-from-tank take Potable only unless the job is forced (an order).
- every drink search (bottle, tank, terrain, caravan, administer) gates through RM_ThirstMath.MayDrink and ranks
  use class > quality > distance. Salt never outside the break; LastResort only at need 0 (vanilla desperate rule).
- animals: any potable; terrible water only when on the map biome's wild-animal roster, no consequences.
- setting `lastResortDrinking`; selftests Thirst_use_class_gate_ruled, Thirst_autofill_potable_only_in_source;
  validation rows Tu/Ta offline, T11-T14 live (owed).
- pre-existing reds NOT mine: selftest_hose_port P9 (RM_LiquidBath credit site), selftest_review_map (RM_WaterThin.png uncovered).

## Slice 2+: ruled design
- `c72cea8a08` slime last resort: thirstQuality Slime (x0.6), RM_Thought_DrankSlime -20/1d x2, RM_SlimePurge 1 day
  (vomit mtb 0.1 d, thirst x1.5), red RM_ContagionTouched 1.0, green slime dose x5, white RM_SporeFlesh, yellow
  RM_SlimeNausea; slime bottles/buckets/barrels (order only); RM_Slime_Liquid drinkable via RM_DrinkableTerrainExtension.
- `6154689f5c` salt break: RM_Break_DrinkBrine (Major, mood pool) + worker gate (parched, no potable reachable, not
  poisoned, salt in reach); RM_DrinkBrine state drinks to 0.9; RM_Thought_SaltRelief +8/3h; RM_SaltPoisoning 0.25/drink,
  lethal 1.0, tendable, thirst x3 above 0.2. Salt's 20% food poisoning REMOVED (salt poisoning is its harm now).
  Dubs mode: JobGiver_RM_Drink drinks LastResort only, read off DBHThirst; drinks Dubs cannot see fill DBHThirst.
  FIX in the same commit: slice 2's MayRequire named member ids (mandrake.rm.contagion/...): composed into
  mandrake.rm.biomes, so they would never have loaded. csproj needed the new file (EnableDefaultCompileItems false; lesson filed).
- `fa4101455e` awkward access: RM_Thought_DrankRough -3/6h (nullifyingTraits Ascetic/Tough/Undergrounder; wild,
  tribal, animals exempt in code); awkward = caravan, bucket/barrel scoop, bottle/tank away from home; ponds free.
  Buckets/barrels drinkable (CompRM_DrawnLitres, RM_DrinkFromContainer); giver prefers free sources.
- `b96a8febf3` Q10 drinking reserve 200 L (sprinklers, converters, bath, reaction; VE adapter exempt); Q9 a Fill-mode tank
  holding a non-potable liquid = standing order to gather it; sprinklers never pick salt/brine (neverSprayed).

- `d2c44a20cf` §8.3: bucket firefighting (RM_DouseFireWithBucket, ahead of vanilla beating); snow/ice to water
  (RM_GatherSnow only where no liquid water fills the bucket; RM_BucketSnow melts >0 C in ~2 h or by stove bill; blue ice
  5 blocks / stonewater 38 chips + empty bucket -> bucket of water, RecipeWorker keeps the bucket's stuff); water items
  folded in (meltwater can + distilled = distilled grade, stilled + melted = fresh); HemogenPack quenches hemogen-gene
  pawns as one full drink. Cooled boiled water: already built (boiling containers revert to fresh).
- `731132ca58` §8.2 step 8: filledBottlesPerColonist stock target (3, inventories count), fill/wash batches of 10.
- `71153b893b` review pass (docs), snow buckets stuffable; DLL rebuilt on the tree merged with FOUNDRY's P3.
- Not built, by design: C's machine ports (only when a liquid-burning machine needs one); the bottler (dropped by §8.1).
  Q9 is the Fill-mode tank (FlowWorks machines take from tanks, not bills).

## Code review
- CLEAN (full read): all 11 Thirst/*.cs, 10 LiquidTypes files, CompLiquidConverter, RM_LiquidBath, RM_LiquidReaction,
  RM_Sprinkle, DefOf, ThirstChecks, GptFixesAChecks; the new Thirst defs/patches.
- STILL DIRTY (owed full reviews, big files touched by small edits): Tools/generate_liquid_suite.py, validation.py,
  review_map_coverage.py, Defs/LiquidTypes/ThingDefs/RM_LiquidBottles_Base.xml.

## Owed deploys / live rows
- Deploy owed: FlowWorks (python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply) when the game is down.
- Live rows owed (validation.py thirst chain, all UNMEASURED): T5 (salt ordered), T11-T29.
- Pre-existing reds, not this item: selftest_hose_port P9 (RM_LiquidBath credit site), selftest_review_map (RM_WaterThin.png).
