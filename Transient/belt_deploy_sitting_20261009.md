# Belt deploy sitting 2026-10-09

Started Fri Oct  9 06:58:51 PDT 2026

## 1 bridge
## 2 undeployed list
## 3 deploy
## 4 tier+launch
## 5 live checks
## 6 leave up
- 1 bridge: FOUNDRY took it 07:00; game UP on acc_20261009c (pid 33160)
- 2 undeployed: WasteRun, UtinniPatches(junker kinds/caravan/corpses), Warcasket, StructureInjectionsRUT(vault seal, inactive mod), FlowWorks DLL, Graffiti, Rites(RUT_Answering), StarWarsRaces(namers), SWBestiary(Nerf E art); composed biomes 21 files (LanternDeeps, EnvHazards bursts, Webwork, CreatureBehaviors, LongShade, TerminalBiomes, LeaningScrub namers). GSS hose: no game-side drift. Lifted DEPLOY_HOLD for RUT_FoundrySalvageCache + RUT_FoundryFloor_SalvageCache.
- 3 deployed 07:1x: 28 files (9 mods) + composed biomes 21 files, all VERIFIED in sync
- 4 tier acc_20261009d (68 mods, all 5 DLC) applied, landed 668b2663b. Decision strings before launch: "Config error in RUT_ThroatCask|RUT_VaultFleshSeal|RUT_Junker|RUT_Answering|RUT_FoundrySalvageCache", "Could not resolve cross-reference", "Harmony patch failed", "RM_AlphaAnimals_DeathBursts", "Bridge token:"
- launch 07:06 via steam://rungameid/294100
- 4 load: bridge token 07:09 (~2.5 min). 0 lines naming ThroatCask/VaultFleshSeal/JunkerCask/Answering/SalvageCache/DeathBurst/Flashstorm; 0 Harmony patch failed; cross-ref misses are donor-absent tier noise
- 5 quicktest map up 07:12; running checks script Transient/belt_deploy_checks_20261009.py
- 5 batch1: Answering 4/4 defs PASS; salvage 8/8 PASS (cache now deploys); throat cask, casked scavenger/elite kinds, junker caravan, vault flesh seal resolve (no criteria filed). Webwork walk: DESIGNATED->READ nodePresent False | weaveNear 3 | lastYield 3 PASS; ProofHarvest 3-field form unreachable (static_call splits args on |). Gloomcast: chorn/gennok/tebbra each read job=FollowClose target=RM_Gloomcast PASS.
- 5 batch2: GreenGoo death -> Filth_SpentAcid (patch filth) present; Thunderbeast death -> Flashstorm condition ticksPassed 137 (our SummonFlashstorm worker) PASS; goo deathAction class field unreadable (get_defs has no nested field). Log: RUT_Caravan_Junkers config error "RM_HalfExtractedCore tradeability does not allow traders to sell this thing" (new def).
- 5 rimflow verify: LANTERNDEEPS_ANSWERING_RITE_BUILD_1 A1 pass; GLOOMCAST_WAKE_RIDERS_1 A2 pass (closed); SALVAGE_WRECKAGE_EVERYWHERE_1 A1 pass; SHOKKWEAVE_SOLE_SOURCE_1 A3 pass; DONOR_CODE_BURST_REBUILD_1 A1+A2 partial. Notes on WARCASKET_JUNKER_KINDS_BUILD_1 (caravan config error), SHOKKWEAVE (static_call | split), THROAT_CASK_ITEM_1 (no criteria). VAULT_SEAL_PLUG_1 was never filed as an item.
- UNMEASURED: pit-lip cut visual (FlowWorks DLL loads, Harmony 31/0); hose matrix (no game-side drift); sweetline names / graffiti designator (owner-visual); vault seal V5 layout; throat cask comp (no proof hook).
## 6 leave up
Game UP on tier acc_20261009d (68 mods) with a quicktest map; bridge released. Owner's full list: `python3 src/RimMandrake/Utils/modset_builder.py --restore` (not run). Trade-mod retirement candidate: note only, not applied.
