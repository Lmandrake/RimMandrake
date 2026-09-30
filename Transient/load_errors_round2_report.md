# LOAD_ERRORS_ROUND_2_1 — fix report

Source: `Transient/load_errors_2026-09-30b.txt` (second cold load, after
`LOAD_ERRORS_FAUNA_FLORA_1` + `LOAD_ERRORS_DEF_FIELDS_1`). Scope: our defs only
(src/RimMandrake, src/RimStarWars, src/RimUtinni). Offline pass, no game/bridge touched.

Status: DONE, pushed to origin/main

## Per-line table

| Line(s) | Error | Verdict |
|---|---|---|
| 66-71 | RSW_Shokk_FeraliskBrood / RM_FactionDef_KurrethSwarm: no tech level, missing maxPawnCostPerTotalPointsCurve, raidLootValueFromPointsCurve must be defined | **FIXED** — added `<techLevel>Animal</techLevel>` + `<maxPawnCostPerTotalPointsCurve>` + `<raidLootValueFromPointsCurve>`, shape copied verbatim from vanilla `Insect` FactionDef (RimSage) |
| 95-97, 120-125 | RM_Fellome / RM_Verrow / RM_Tullick: undefined preferability, no foodType, Nutrition==0 | **FIXED** — these three are genuine wild-forage FOOD plants (`humanFoodPlant=true`, `purpose=Food`, described as staple calories) wrongly swept into `ParentName="PlantBaseNonEdible"` by the prior fauna/flora pass's blanket fix. Reverted to `ParentName="PlantBase"` (gives Plant/RawBad `<ingestible>` by inheritance) + added an explicit `<Nutrition>` stat (PlantBase itself sets none), matching this repo's own `RM_GiantLeaf`/`RM_Ultracactus` precedent and vanilla `Plant_Berry` |
| 75 | RUT_GaslightLamp: Refuelable consumes per tick, parent tickerType Never | **FIXED** — added `<tickerType>Normal</tickerType>`. Confirmed via RimSage: vanilla `TorchLamp` (refuelable, no CompPower) sets the same; `RUT_DryAirBlower`'s otherwise-identical refuelable doesn't need it because its own `CompProperties_Power` already drives ticking |
| 85 | RM_TarShallow: makes terrain filth and also accepts it | **LEFT — design decision needed.** Both halves are deliberate, already-shipped, heavily-documented mechanisms in two SEPARATE patch files: `RUT_TarShallow_GeneratedFilth.xml` (SUMP_WALKWAYS_1, pawns track `RM_Filth_Tar` off tar onto dry floors) and `RUT_TarShallow_FilthAcceptance.xml` (SUMP_MECHANICS_1 S4, `filthAcceptanceMask=Terrain` specifically so `RUT_Filth_MouseTrack` can land on it). Confirmed via decompiled `Verse/TerrainDef.cs:538` this is a pure advisory warning (`generatedFilth != null && filthAcceptanceMask has Terrain`), never blocking or breaking either mechanism. Silencing it would require dropping one of the two shipped mechanics — not mine to pick. |
| 92, 94 | RM_Slime_Mud / RM_Slime_Liquid: makes+accepts terrain filth | **FIXED** — unlike TarShallow, these never set `filthAcceptanceMask` at all (defaults to `Any`, which includes Terrain) and have no comparable second mechanism needing Terrain acceptance. Narrowed to `<li>Unnatural</li>` only, matching vanilla `Sand`'s own posture (generates `Filth_Sand`, accepts only Unnatural) |
| 86-91 | RM_FE_Ash_Trace/Light, RM_FE_Ground_Sand/Gravel/Soil/SoilRich: burnedDef is flammable | **NO ACTION — already ruled and documented as an accepted, advisory-only warning.** Both files (`AshLadder.xml`, `ScorchableGround.xml`) carry an explicit header: owner-ruled "accept" 2026-09-03/09-01, twelve log lines are "the accepted price" of the fire-ecology ladder (ground burns to ash, ash burns onward down the ladder). Do not zero Flammability or clear burnedDef — that deletes the mechanism. |
| 93 | RM_SeaDiveHatch: impassable building shoot/seen-over | **FIXED** — added `<disableImpassableShotOverConfigError>true</disableImpassableShotOverConfigError>`, the exact ThingDef field (`Verse/ThingDef.cs:163`) that exists to silence this specific, deliberate case: a sealed portal hatch is impassable on foot by design (entry is via the MapPortal interaction, not walking through) |
| 98 | RM_SlackwaxTimber: equipment with no verbs/tools | **FIXED** — its `ParentName="ResourceVerbBase"` (same as vanilla `WoodLog`) carries `equipmentType=Primary`+`CompEquippable`, requiring a `<tools>` block; it was dropped when the def's WoodLog-shape was hand-copied. Restored WoodLog's own single "log"/Blunt tool verbatim |
| 99,100,102,106,108,114-119 | CompRottable tickerType Never (RM_TarspoolStalk, RM_PitchpearlBeads, RM_StonewaterIce, RM_DeltaSilt, RM_GreatboleFruit, RM_ThornbugNectar, RM_DrommathSap, RM_DrommathBurstSap, RM_SekkulaathCream, RM_SeveredTentacleFlesh, RM_OssagrelSap) | **FIXED (11 defs)** — all inherit(ed) `ResourceBase`'s tickerType (Never/unset) while carrying a `CompProperties_Rottable`. Added `<tickerType>Rare</tickerType>` (RM_DeltaSilt had an explicit `Never`, changed to `Rare`), matching vanilla `RawBerries`' own pattern (RimSage-confirmed) |
| 101,103,104,109 | socialPropernessMatters=false w/ preferability > DesperateOnlyForHumanlikes (RM_PitchpearlBeads, RM_StonewaterIce, RM_MeltedWater, RM_GreatboleFruitSteak) | **FIXED (4 defs)** — added `<socialPropernessMatters>true</socialPropernessMatters>`, matching vanilla `RawBerries` |
| 105 | RM_Tarnn: Beauty stat on Pawn | **FIXED** — removed `<Beauty>2</Beauty>` from statBases; Beauty is inert on a `category=Pawn` Thing (vanilla animals never set it either) |
| 107 | RM_FrenzyDose: duplicate thingCategory Drugs | **FIXED** — removed the redundant explicit `<thingCategories><li>Drugs</li></thingCategories>`; `MakeableDrugBase` → `DrugBase` already gives it by inheritance |
| 110-113 | RM_BrakkelFruit/RM_TumbelGourd/RM_SarquinSap/RM_WollickTuber: duplicate thingCategory PlantFoodRaw | **FIXED (4 defs)** — same class as RM_FrenzyDose; `PlantFoodRawBase` already gives `PlantFoodRaw`, removed the redundant re-declarations |
| 126 | RM_Sunbeam: smeltable, gives nothing | **FIXED** — `BaseGun` sets `smeltable=true` but this def deliberately carries no `recipeMaker`/costList (purchasable/quest-only per its own header). Added a `<costList>` (Steel 45, ComponentSpacer 3) purely to feed value/smelt calc — does not create a craft recipe, same posture vanilla's `Gun_ChargeLance_Unique` uses (recipeMaker explicitly nulled, costList still present) |
| 127-130 | RM_ShadeTent/RM_SunShield (+Frame_ variants): madeFromStuff + constructEffect | **FIXED (2 defs; the two `Frame_*` variants are engine-auto-generated from these and clear automatically)** — removed the explicit `<constructEffect>ConstructDirt</constructEffect>`; both are `madeFromStuff` (stuffCategories Fabric/Leathery), so the stuff's own construct animation always wins anyway |

## Left for design / out of scope

- **RM_TarShallow "makes filth and also accepts it"** (line 85) — see table above. Two
  separately-shipped, well-documented mechanisms; picking one to break is a design call,
  not an offline fix.
- **RimThemes theme folder `src/RimUtinni/MenuShell/RimThemes/Utinni Shell/`** — the log's
  `Config error in Utinni Shellmandrake.rut.menushell: defName ... should only contain
  letters, numbers, underscores, or dashes` is our theme (`mandrake.rut.menushell`), but the
  malformed identifier is built by the THIRD-PARTY `aRandomKiwi.RimThemes` mod's own loader
  (not vanilla, not in RimSage's decompiled index) by concatenating the theme folder name
  with something mod-identifying — visible as `"Utinni Shell" + "mandrake.rut.menushell"`
  with no separator. Renaming the folder to drop the space (`UtinniShell`) is the obvious
  candidate, but our packageId's own periods would still land inside the same compound
  string if that guess about the concatenation source is right, and I have no source for
  RimThemes' actual loader to confirm either way — flagging rather than guessing a donor
  mod's internal naming contract (CLAUDE.md: never guess a defName/field without a source).
- **RUT_SteamCatch `[Def Error]`** (line 11) — carried over UNRESOLVED from
  `LOAD_ERRORS_DEF_FIELDS_1`'s own report: the digest line has no attached error text (eaten
  by log dedup), and that pass already checked every field on the def and its
  `CompProperties_ResourceCondenser` against RimSage with nothing found wrong. Nothing new
  to react to this round either.

## Not touched (donor-mod / non-our-tier, confirmed out of scope)

BoneWall, AM_Entrance_LargeElevator, AM_Entrance_UndergroundGarage, Prj_SW_Electricgryllotalpa,
WeatheredBasalt, PassableBasalt, PassableVacstone (referenced by our files but not our own
defNames), TargetedInsultingSpree, Eclipse, AM_AncientLogisticsSystem, SolarFlare,
CannibalPirate, PirateYttakin, ModernFixtures/AdvancedShowers/RR_Furniture/VCE_StewCooking
research-coord collisions, RR_LateralThinking, RR_Organization, guy762_* weapons,
Techprint_RR_lighting, all "Could not resolve cross-reference" lines naming vanilla/donor
SoundDefs, BodyPartGroupDefs, ThingDefs (RawVegetables, EmptyAICore, HungerRateMultiplier,
etc. — none owned by src/), the JumppackForMeleeAI Harmony patch exception, and the generic
`System.ArgumentNullException`/`System.Exception: Wrong null argument` lines with no def
attribution.

## Verification

- All 18 touched files parse clean (`xml.etree.ElementTree`).
- `run_selftests.py`: **77/79 passed**, 2 skipped (human/venv-gated, by design),
  1 UNMEASURED (`selftest_tool_metadata.py` — no local .NET build here, expected),
  1 FAILED — `selftest_deployed_biome_refs.py`, the same pre-existing
  `mandrake.rut.rotsporekit`-gated failure both prior LOAD_ERRORS_* reports named
  (RotSporeKit retirement, `ROTSPOREKIT_MAYREQUIRE_ORPHANED_1`) — unrelated to any
  fix in this pass, unchanged by it.
- No C# touched this pass — no DLL rebuild needed.

## Commits (this worktree, rebased and pushed to origin/main)

- `24ac7b092` — FactionDef ConfigErrors (Kurreth Swarm / Feralisk Brood)
- `57d0ca829` — RM_Fellome/Verrow/Tullick reverted to real food plants
- `8bfa557b8` — CompRottable tickerType, social properness, RM_SlackwaxTimber tools
- `cfde72034` — RM_Slime_Mud/Liquid filthAcceptanceMask
- `bf74a3a6a` — duplicate thingCategory re-declarations removed
- `590ae71c3` — RM_Tarnn Beauty stat removed
- `7f76cc717` — RUT_GaslightLamp tickerType
- `dda8de2a1` — RM_SeaDiveHatch disableImpassableShotOverConfigError
- `0abeb3768` — RM_Sunbeam costList
- `328162236` — RM_ShadeTent/RM_SunShield constructEffect removed
- (this report itself, final commit)
