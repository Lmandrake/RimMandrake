# Mineable scatterers outside GenStep_RocksFromGrid — census, 2026-11-05

Item: MINERAL_SCATTERERS_AUDIT_OUTSIDE_ROCKS (caused by MINERALS_WHERE_THEY_BELONG_1). Rows and covers:
`design/RimMandrake/mineral_scatterers_census_2026-11-05.tsv`. What R5 still owes:
`infrastructure/state/items/MINERAL_ADAPTERS_BUILD_DONOR_SOURCES.md`. Guard:
`src/RimMandrake/Minerals/selftest_mineral_scatterer_census.py`.

## The premise, corrected

The item assumed the sources outside RocksFromGrid "pick by mineableScatterCommonality". Measured, almost none do:

- **Core and every DLC** read `mineableScatterCommonality` in two places only: `GenStep_ScatterLumpsMineable.ChooseThingDef`
  (unforced instances; in vanilla only the one inside RocksFromGrid, which the surface placer already covers) and
  `TileMutatorWorker_MineralRich` (a lump-count scale, not a pick). Asteroids, PreciousLump, the long-range scanner,
  generated locations and the asteroid quest draw from **explicit lists**: they never lose a governed def; they ignore the
  policy instead. `RM_MineralExplicitLists.cs` already prunes those lists.
- The real hazards are the opposite shape: code that draws from **every isResourceRock def** (VEE meteorite shower,
  VGE asteroid boon), and code that **scales a count by the zeroed weight** and so hits a `<2` lump fallback
  (MineralRich, VE Exploration's MineralDevoid). Those four rows are R5's.
- One real bug in our own code: DeepDrill's mineral-devoid strip tests the live weight, so zeroed governed veins survive
  (filed MINERAL_DEVOID_FIX_ZEROED_VEINS_SLIP_THROUGH).

## Method (how to re-run it)

1. Core/DLC: decompile of the live `Assembly-CSharp.dll` (md5 `bf39a6f68f2deda9b09d66f6ceffecf3`, matched on the day),
   grepped for `mineableScatterCommonality`, `GenStep_ScatterLumpsMineable`, subclasses of it and of RocksFromGrid;
   Core/DLC `Data/*/Defs` grepped for the lump and asteroid steps and their lists.
2. Mods: `python3 src/RimMandrake/Minerals/scatterer_census.py --root <Mods> --root <workshop 294100> --shard i/8`
   (8 shards in parallel: one pass over the workshop mount takes longer than a command may run). It flags every DLL whose
   metadata names the field or the step types, and every XML node whose Class is a lump step. A mod with no hit cannot
   hold a weighted scatterer: the field and type are reached by name. 166 raw rows; 69 were bundled copies of
   Assembly-CSharp.dll and dropped.
3. Kept only mods on `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (the owner's list; the live ModsConfig
   was on a test tier). Their DLLs were decompiled (ilspycmd 8.2) and each hit was read by hand.
4. KCSG `postGenerateOre` and BiomesCore's island/cavern rock steps are unforced weighted scatterers. A grep of all 413
   full-list mod folders found no def that uses either; the grep was sanity-probed and does see our own comments that name
   `GenStep_ScatterLumpsMineable`. They are listed as latent. Re-run step 2 when the list changes.

Scratch (TSVs, decompiles): `D:\ClaudeWork\rimmandrake\minerals_scatterers\`.
