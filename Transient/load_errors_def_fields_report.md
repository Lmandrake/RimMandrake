# LOAD_ERRORS_DEF_FIELDS_1 — report

Source: `Transient/load_errors_2026-09-30.txt` (cold load 2026-09-30 23:09, full list, deploy of origin/main 7443a66d7).
Scope: our defs only (src/RimMandrake, src/RimStarWars, src/RimUtinni). Skipping donor-mod errors and the
parallel agent's classes (tool body-part-group mismatches, Nutrition/preferability NeverForNutrition,
trainability null).

## Status: DONE, pushed to origin/main

## 1. Bad field names ([Def Error] / "doesn't correspond to any field")

- RM_LiquidDrill / RM_LiquidTank: stray `<coverEffectiveness>` on ThingDef (already had the real field,
  `<fillPercent>`) — removed the invalid duplicate.
- RM_GameCondition_Undersurge: `<letterLabel>`/`<displayOrder>` are not real GameConditionDef fields
  (confirmed via decompiled `Verse/GameConditionDef.cs`) — removed; `label`+`letterText`+`letterDef` already
  cover the letter.
- RM_TetherChain: `<ingredients>`/`<fixedIngredientFilter>` on `recipeMaker` (RecipeMakerProperties has
  neither — it auto-generates from the ThingDef's own `costList`) — moved the Steel/ComponentIndustrial
  cost onto the ThingDef's `<costList>`, which also fixes the paired "has a recipeMaker but no costList"
  config error.
- RM_VauliskLure (RM_CompProperties_VaeuliskLure): `<checkIntervalTicks>` — the C# class has no such field
  by design (its own header explains the engine's TickLong cadence already throttles the check) — removed
  the stray XML.
- RM_Oommok / RUT_Radiothermal: `<wildness>` inside `<race>` isn't a RaceProperties field in 1.6 (confirmed:
  no such field anywhere in the decompiled source) — both defs already carry the correct `<Wildness>` StatDef
  in `statBases` with the identical value, so the race-block line was a stray duplicate — removed.
- RUT_SlimeGrazer: `<soundCall>` inside `<race>` — real field is `LifeStageAge.soundCall`, not
  `RaceProperties.soundCall` (confirmed via decompiled source) — moved onto the `AnimalAdult` lifeStageAges
  entry.
- RM_Zisska (RM_CauldronFauna.xml): `<butcherProducts>` inside `<race>` — that field lives on ThingDef, not
  RaceProperties — moved to the ThingDef's own top level (sibling of `<statBases>`).
- RM_FossilDisplaySlab / RM_FossilDisplayMount: `<fixedIngredientFilter>`/`<ingredients>`/`<products>` on
  `recipeMaker` (none are real RecipeMakerProperties fields). Removed rather than promoted to a hand-authored
  RecipeDef: both defs are also `madeFromStuff` (costStuffCount+stuffCategories), and a hand-written RecipeDef
  would have to hand-replicate `RecipeDefGenerator`'s stuff-cost plumbing to keep that working — new
  mechanism, not a load fix. Net effect: both pieces now build from plain stuff like any vanilla sculpture;
  the "must be built FROM a harvested fossil" gate is NOT currently enforced — flagged in the file's own
  header for whoever next owns FloodedCanyon fossils.
- RM_OllathrixVenom: `<lethal>` on a HediffStage — real field is `lifeThreatening` (confirmed via decompiled
  `Verse/HediffStage.cs`) — renamed.
- RSW_TunnelSnake: `<specialTrainables>` directly on the PawnKindDef (PawnKindDef has no such field — it's a
  RaceProperties field, and this ThingDef's own `<race>` block already sets it correctly) — removed the
  duplicate/misplaced PawnKindDef copy.
- RM_TavroskLiquor / RM_ThornbugNectar / RM_DrommathSap / RM_DrommathBurstSap / RM_OssagrelSap: `<nutrition>`
  inside `<ingestible>` — Nutrition is a StatDef (`statBases`), not an IngestibleProperties field — moved.
- RM_PitchpearlBeads / RM_StonewaterIce / RM_MeltedWater: `<nutritionInterval>` inside `<ingestible>` — not a
  real IngestibleProperties field at all (no corresponding concept in 1.6), and all three already carry the
  correct `<Nutrition>` in `statBases` — removed the stray line rather than inventing a destination for it.

Root-caused but not touched (belongs to the parallel agent's classes per the brief): the `Config error`
lines for trainability=null, tool linkedBodyPartsGroup mismatches, and Nutrition==0/NeverForNutrition.

## 2. Exception loading def from file

- RSW_Shokk_FeraliskBrood.xml / RM_FactionDef_KurrethSwarm.xml: both crashed with
  `ArgumentNullException` in `PawnGenOption.LoadDataFromXmlCustom` (`Single.Parse(null)`). Root cause:
  `<options>` (a `List<PawnGenOption>`) was written in the long `<li><kind>X</kind><selectionWeight>N</selectionWeight></li>`
  form, but `PawnGenOption`'s custom XML loader only supports the vanilla shorthand
  `<DefName>Weight</DefName>` — for a bare `<li>` node it reads the WHOLE li's `InnerText` as the kind's
  cross-ref string (concatenating "Wyyyschokk"+"10" with no separator) and tries `Single.Parse` on the
  `<li>`'s FirstChild, which is an element, not text, hence null. This is also what produced the
  `RM_GreatboleFruitSteak4`/`RM_RoyalRind1`/`RM_GreatboleSeed1`/`RM_RadioactiveSuppressant5` cross-reference
  errors elsewhere (same bug, different field — `RecipeDef.products`, same underlying
  `ThingDefCountClass.LoadDataFromXmlCustom` shorthand-only contract). Fixed both `<options>` blocks to the
  shorthand form; fixed the two malformed `<products>` blocks (`RM_GreatboleHarvest_Recipes.xml`,
  `RM_RadioactiveSuppressant.xml`) the same way. Swept the whole repo for both patterns — no other
  occurrences.
- Also in `RM_GreatboleHarvest_Recipes.xml`: `<effectWorking>Butcher</effectWorking>` and
  `<soundWorking>Recipe_Butcher</soundWorking>` referenced non-existent vanilla defs — real names are
  `ButcherFlesh` (EffecterDef) and `Recipe_ButcherCorpseFlesh` (SoundDef), confirmed via RimSage. Fixed.
- RM_TheSump: `Exception in ConfigErrors()` NRE in `BiomeDef.ConfigErrors()` — confirmed by reading the
  decompiled method: it's `wa.animal.defName` on a null `.animal`, a direct side effect of the unresolved
  wildAnimals cross-references below (class 3). No separate fix needed — resolved by the DEPLOY_HOLD fix.
- `RSW_VentStalker` duplicate-key: searched for two live ThingDef/PawnKindDef definitions of that defName
  in src/ — found only ONE definition (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_VentStalker.xml`).
  The duplicate-add exception (`GiddyUp.MountUtility.BuildAnimalBiomeCache`) is a donor mod (Giddy-Up)
  iterating `BiomeDef.AllWildAnimals`, which itself throws from the SAME TheSump NRE above (see its own
  stack trace: `RimWorld.BiomeDef.CommonalityOfAnimal` → `AllWildAnimals` → `GiddyUp`) — RSW_VentStalker
  appearing twice in that cache build is a cascade off the aborted enumeration, not a real duplicate def in
  our source. Should clear once the TheSump NRE is gone; flagged, not independently fixable in our XML.

## 3. Could not resolve cross-reference (ours)

- TheSump biome (`RM_TheSump_Biome.xml`) wires 5 SUMP_FAUNA_ROSTER_1 rows and 8 SUMP_FLORA_ROSTER_1 rows
  (RM_SumpMouse/RM_Brommet/RM_Dredgel/RM_Skarrid/RM_Skellarn, RM_Dorvel/RM_Skelver/RM_Korveth/RM_Brindeth/
  RM_Soffeth/RM_Tolleth/RM_Mirrelin/RM_Pallick) into `wildAnimals`/`wildPlants`. All of these defs DO exist
  in `RM_SumpFauna.xml`/`RM_SumpFlora.xml` — but both those files are held in `src/DEPLOY_HOLD.txt` (no art
  yet), while `RM_TheSump_Biome.xml` itself was never held, so it deployed and dangled 13 cross-references.
  Added `RM_TheSump_Biome.xml` to `DEPLOY_HOLD.txt`, held with the same two files — per
  `BIOME_PAINT_ONCE_AT_THE_END_1` this biome carries 0 tiles pending the terminal repaint, so nothing
  user-visible is lost. Also fixes the `RM_TheSump` ConfigErrors NRE and the RSW_VentStalker cascade above.
- `RUT_FoundrySalvageCache`/`RUT_FoundryTowerEntrance`/`RUT_TibannaGas`: all three held in DEPLOY_HOLD.txt
  for art, but their REFERENCING files were not: `RUT_FoundryFloor_SalvageCache.xml` and
  `RUT_FoundryTowerScatter.xml` (both `RM_SetPieceElement_SpawnMarker.markerDef`) and
  `RUT_TibannaTap_BeldonWiring.xml` (`CompProperties_GatherableGas`). Added all three to DEPLOY_HOLD.txt,
  held with their respective target.
- `RM_GreatDevourer` (LongShade, franchise-free RM_ tier): its `CompProperties_EggLayer` pointed at
  `RM_GreatDevourerEggUnfertilized`/`RM_GreatDevourerEggFertilized`, which don't exist. The real egg items
  (`RM_LongShade_FaunaSupport.xml`) are named `RM_EggGreatDevourerFertilized`/`RM_EggGreatDevourerUnfertilized`
  — same naming convention as this file's sibling species (RM_EggBokka*/RM_EggOssik*). Repointed the comp to
  the real names. Also clears the paired "eggFertilizedDef is null" config error.
- `Misc13` KeyBindingDef on `RUT_DigShaft` — only Misc1–Misc12 exist in 1.6 (confirmed via RimSage). Removed
  the hotkey binding rather than risk a collision picking a used slot; purely cosmetic (no accelerator key),
  not a functional loss.
- `RUT_Sagecrust`/`RUT_Dewshrooms`/`RUT_DeadCreep` (RotSporeKit, retired, not in the canonical mod list —
  overlaps `ROTSPOREKIT_MAYREQUIRE_ORPHANED_1`, fixed only the mechanical dangling refs, not the fuller
  retirement):
  - `RUT_TheForge.xml` wildPlants: unguarded `RUT_Sagecrust` row repointed to `RM_Sagecrust` (built
    `mandrake.rm.therot` equivalent, confirmed to exist).
  - `RUT_WeepingStones.xml` wildPlants: unguarded `RUT_Dewshrooms` row repointed to `RM_Dewshrooms` (same,
    confirmed to exist — note `RM_WeepingStones_Biome.xml`'s OWN copy of this row already correctly guards
    the RUT_ name with `MayRequire="mandrake.rut.rotsporekit"`, so only the campaign-tier twin was broken).
  - `RUT_ContagionRingScatter.xml`: `<filthDef>RUT_DeadCreep</filthDef>` — no RM_ equivalent exists (checked
    `src/RimMandrake/TheRot`) — added `MayRequire="mandrake.rut.rotsporekit"` directly on the field (DirectXmlToObject
    honours MayRequire on a plain Def-typed field, not just list `<li>`s). The GenStep's own C# already
    null-guards `filthDef` gracefully.
- `Recipe_Butcher`/`Butcher` (SoundDef/EffecterDef) — see class 2 above, fixed alongside the products bug.

Not touched (genuinely donor-mod or generic, no owning def in our src/): `RawVegetables`, `Ingest_Vegetable`,
`Pawn_Insect_Ambient`, `Warg_Eat`, `Muffalo_Eat`, `Pawn_Melee_SmallBite_*`, `Pawn_Dog_Wounded`,
`Pawn_Squirrel_Call`, `HindlegsFrontClaws`/`FrontLegs`/`FrontLeftFoot`/`FrontRightFoot`/`Jaw`/`Tail`
(BodyPartGroupDef — these are the parallel agent's tool/body-part-group class), `TrainabilityDef Simple`/
`Minimal`, `BodyDef Rat`, `AteUltracactus`, `SkillDef Tailoring`/`TableTailor` (no owning def found in our
mods), `EmptyAICore`, `HungerRateMultiplier`.

## 4. Missing textures

- `RM_MirrorGiant` (now `RM_Oommok`'s PawnKindDef, texPath never updated after the rename): an artpipe job
  (`rmmirrorgiant_v1_{south,east,north}`) is recorded as `status: ok` in `infrastructure/artpipe/done/`, but
  the actual PNG it claims to have written (`infrastructure/artpipe/_artsrc/rmmirrorgiant_v1_*/…png`) was
  never committed to the repo and does not exist on disk anywhere in this worktree (`git log --all` on that
  path returns nothing). **BLOCKED** — the render is lost, not merely unwired; needs re-queuing through
  `fill_queue.py`, not a load-error fix.

Also added, found mid-pass, same class of bug: `RM_GreatboleHarvest_Items.xml`'s `RM_Apparel_RindCoat`
recipe named a SkillDef "Tailoring" (doesn't exist in 1.6 — real name `Crafting`) and a recipeUsers
ThingDef "TableTailor" (doesn't exist — real names `ElectricTailoringBench`/`HandTailoringBench`, matching
this repo's own convention elsewhere).

RUT_SteamCatch's `[Def Error]` tag in the digest has no XML-error text of its own attached (the dedup ate
it as a duplicate of an earlier, already-shown line). Read the whole file and its C# comp
(`CompProperties_ResourceCondenser`) field-by-field against RimSage — every field it uses is real and
correctly spelled. Could not attribute a specific bad field to it; flagged rather than guessed at.

## Selftests

`run_selftests.py`: **77/79 passed**, 2 skipped (need a human/lupa env), 1 UNMEASURED (bridgetools, no
local .NET build here), 1 FAILED — `selftest_deployed_biome_refs.py`, the pre-existing known failure named
in the brief. **Could not measure whether it changed**: that script hardcodes
`/mnt/d/Luke/dev/Rimworld/src/...` (the MAIN checkout) rather than resolving from its own file location,
so running it from this worktree reads the *main checkout's* files, not this worktree's — it cannot see
any worktree-local fix (mine or the sibling `LOAD_ERRORS_FAUNA_FLORA_1` agent's) until this push lands
there. Its failures are otherwise all `mandrake.rut.rotsporekit`-gated rows (the known RotSporeKit
retirement, `ROTSPOREKIT_MAYREQUIRE_ORPHANED_1`) plus the two rows this pass fixed
(`RUT_Sagecrust`/`RUT_Dewshrooms`), which is exactly why it can't reflect the fix from here. Confirmed
correct the other way instead: `git grep` on the pushed tree shows zero remaining bare (unguarded)
`RUT_Sagecrust`/`RUT_Dewshrooms` rows, and every touched file parses clean XML.

## Rebase note

`git rebase origin/main` hit 3 conflicts (`RM_SapSuckerGuildProducts.xml`, `RM_FeverWoodFlora.xml`,
`RM_WebworkFlora.xml`) against a sibling agent's already-pushed `LOAD_ERRORS_FAUNA_FLORA_1` commit, which
independently fixed the SAME `<nutrition>`-inside-`<ingestible>` bug on the SAME five defs (same root
cause, same destination field, different agent). Resolved by keeping the sibling's version (it carries an
explanatory comment mine didn't) — end state identical either way, no intent lost from either side.

## Commits (on origin/main, in order)

- `7745701f8` — class 1 (bad field names)
- `8d1049db2` — class 2 (exception-loading-def crashes)
- `f3dca8ebb` — class 3 (dangling cross-references + DEPLOY_HOLD.txt)
- `cdfc40cd0` — chore: pre-existing health-dashboard drift (unrelated, committed only to clear the rebase gate)

Confirmed `cdfc40cd0` (HEAD) is an ancestor of `origin/main` after push.
