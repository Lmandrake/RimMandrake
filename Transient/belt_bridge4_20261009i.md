# belt bridge4 — full-list sitting, 2026-10-09 (helper #3)

## Status
- 19:38 started; bridge held by FOUNDRY.

## Decision strings (written BEFORE launch)
- Load finished: `Bridge token` in Player.log (expect ~15-21 min). Dump/def counts not in scope.
- DONOR_CODE_PLAIN_PORTS_1 A2 (L1): PASS = zero `Config error` / `Could not resolve cross-reference` lines naming RM_Radyak|RM_Thermadon|RM_Agaripawn|RM_Agaripod|RM_MycoidColossus|RM_DecayDrake|RM_RipperHound|RM_OssrithCrystal|RM_DuskfireSpit|RM_FermentedMound, AND expected-present: `jawa/get_defs` ThingDef/<each> foundCount 7. Texture misses on donor paths (Radyak, RipperHound) are art-owed, not A2 fails.
- DONOR A3 (L1): spawn each cast port on a quicktest map (spawn_batch), `jawa/list_things defName=<x>` count >=1; biome roster read via get_defs BiomeDef RM_Miasma/RM_Cauldron/RM_TheRot wildAnimals contains the RM_ name.
- SHOKKWEAVE A1 (L2): `ProofHarvest true;RM_Webwork_Anchor;34` result reads `designatable True | workgiver True | yield 3 | weaveNear 0->3 | spawned 1`. Prior full-list run read designatable False/workgiver False (partial).
- TICKER A1 RUT_DyingCreep (L1): spawn on soil, step ticks; DyingCreep count >1 within 4 h, 0 by ~8 h, RUT_DeadCreep present. Log: no ConfigErrors line naming RUT_DyingCreep (was the UtinniPatches fix).
- CREATURE_BEHAVIORS_CONFIGERRORS_1 (already done): confirm zero `Config error` lines naming VerminBreeder/ParentalEnrage/DungSeeder/DrumLure on the FULL list.
- BAZAAR_DISPLACEMENT_PASS_1: ModsConfig diff vs FULL.LATEST = exactly -hobtook.tradeui, -vanillaexpanded.vanillatradingexpanded. Load: no red error naming VanillaTradingExpanded/TradeUI. Rehearsal (save COPY): Scribe `Could not find class` / `Could not load reference` lines naming VTE types (VanillaTradingExpanded.*) counted; wealth read after load.
- Baseline from 07:32 full load: FIRST exception = Worldbuilder FactionDef.ConfigErrors NRE (donor); crossref 3; patchfail 6; ConfigErrors 42.

## Deploys
- 19:40 game PID 34060 killed (minimal 15-mod test list, disposable); prior Player.log copied aside.
- 19:41 UtinniPatches: no drift (bridge3 had deployed). SWBestiary: BeastMechanicsRSW DLL+srchash + Nerf_f_east.png. Compose biomes: no drift (bridge3 deployed). Also 10 mods' DLL drift deployed (CathedralPass, ExplosiveGrowth, ExplosiveKnockback, HugeThings(+Keyed), Inhabited, KeelHoist, PlantGrowth, RiverColors, ShipShields, SolarMirrors), 21 files.

## Mod list
- 19:44 live ModsConfig backed up to deployed/config/ModsConfig.before-bridge4-fulllist_20261009.xml (15-mod list); CANDIDATE_NO_TRADEUI_VTE installed: 612 active, diff vs FULL.LATEST exactly -hobtook.tradeui -vanillaexpanded.vanillatradingexpanded, order identical.

## Cold load
- 19:45 launched via Steam (PID 9104). 20:00 still loading (4789 log lines).
- VTE prep (offline, during load): VTE 1.6 assembly's only GameComponent is `VanillaTradingExpanded.TradingManager` (also NewsDef, BankExtension, LordToil_DefendTraderCaravan). Canonical save holds exactly ONE VTE block: `<li Class="VanillaTradingExpanded.TradingManager">` (~1.26 MB: priceModifiers 27 keys, all wools/silks, values 2.67-7.92; news, banks, companies, contracts). No other VTE class in the save; TradeUI string 0 hits. Save COPY made: Saves/BAZAAR_VTE_UNWIND_REHEARSAL_20261009.rws (canonical untouched, 17,483,421 B both).

## Acceptance sweep

## Findings / fixes
- 20:05 `Bridge token` (cold load ~20 min, 612 listed). Log harvest (Player.log copied aside): FIRST exception line 1189 = Worldbuilder `ConfigErrors() of CannibalPirate` NRE (donor, same as 07:32 baseline). Then VBE `-1§Vanilla` KeyNotFound, Quarry duplicate `Sandstone` (both baseline), and NEW-vs-07:32-note: HAR `Error during patching PregnancyUtility.CanEverProduceChild ... Wrong null argument: brtrue NULL` (line 5660; donor HAR vs another transpiler; our only CanEverProduceChild reference is a JawaBench read tool, not a patch). Crossref 0 (was 3). Patchfail 4 (donor: Mining Outpost, Intimacy x3). ConfigErrors 29 (ash burnedDef x6 RM_FE_*, research coords, guy762 forcedMiss; none ours-new). Couldnotfindclass 1 (PrisonerRealism settings).
- Texture misses that ARE ours, fixed in src: (a) RUT_DyingCreep `Graphic_Single` on a folder holding RUT_DyingCreep_a.png -> `Graphic_Random`; (b) 12 catch items (RUT_Tubbik/Zhurr/Hurrok/Vhessa/Fessu/Krellik/Oddu/Oovu/Tarnn, RSW_Mee/Faa/LaaCatch) used vanilla `Meat_Small` with `Graphic_Single`; the engine's own meat uses `Graphic_StackCount` on that folder -> fixed. Takes effect next load. Swarmling (TheRot patch) texture miss = baseline, art-owed.
- No VTE/TradeUI line (only vanilla RimWorld.TradeUI ctor). No WetBulb line. MeleeAnimation: only CherryPicker removal-list lines (AM_LassoHyperwave/Devilstrand cut), no error. No InvalidProgramException.
- 20:15 quicktest started. DONOR A2 read: get_defs ThingDef+PawnKindDef 7/7 found, extras (OssrithCrystal, FermentedMound, DuskfireSpit, RefineOssrithCrystal) 4/4; 0 log lines name any port; biome_probe: Cauldron {Radyak,DecayDrake} Miasma {Thermadon,DecayDrake} TheRot {Agaripawn,Agaripod,MycoidColossus} all 'spawning', AA_ donors absent; RipperHound cast nowhere (known). Texpaths: our art on Thermadon/Agaripod/DecayDrake/Agaripawn/Mycoid (RotSpecies), donor placeholders on Radyak/RipperHound (art owed). Evidence Transient/belt_bridge4_defs_out_20261009i.txt
- 20:20 DONOR A3: biome maps generated on tile 114480 for RM_Cauldron/RM_Miasma/RM_TheRot (4-5 s each); each cast port spawn_pawn ok and alive at +300 ticks on its own biome map (Ossrith, Duskfire, Fermatalis x2 biomes, Rennok, Gromma, Vorrugath). Natural wildlife on the 100x100 maps (8-9 animals) drew none of them at commonality 0.1 (not evidence either way). Evidence Transient/belt_bridge4_maps_out_20261009i.txt.
- 20:25 SHOKKWEAVE A1: `ProofHarvest true;RM_Webwork_Anchor;34` -> `designatable False | workgiver False | yield 3 | weaveNear 0->3 | spawned 1` (same as the 16:32 full-list run). ROOT CAUSE measured: jawa/harmony_patches on Designator_Deconstruct.CanDesignateThing shows a Real Fog of War prefix (com.github.lukakama.rimworldmodrealfow, DesignatorPrefix.CanDesignateThing_Prefix) - on the full list a thing spawned and checked in the same paused tick is unseen, so the designator refuses; the def is right (alwaysDeconstructible true, claimable false, webHarvestEnabled True). The REAL route on the full list: anchor spawned 3 cells from a colonist, 300 ticks, designate_batch Deconstruct, +1000 ticks -> `nodePresent False | weaveNear 3 | lastYield 3`. Harvest works; the proof hook's same-tick designator check is what fails under RealFoW. Evidence Transient/belt_bridge4_shokk_out_20261009i.txt, Transient/belt_bridge4_web_route_out_20261009i.txt.
