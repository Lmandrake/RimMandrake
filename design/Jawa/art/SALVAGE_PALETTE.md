<!-- status: live -->
# SALVAGE_PALETTE.md — which shipped wreck props the player can actually strip

🔴 **GENERATED FILE. Do not hand-edit.** Regenerate with `python3 design/Jawa/art/salvage_filter.py`.

Read from the **live merged def state** (`DefDump/defs/ThingDef.json`), not shipped XML, because mods patch each other's defs — *Vanilla Vehicles Expanded* has already rewritten the entire Core vehicle-wreck salvage list in this install. **Re-run this after any modstack change.**

Yield shown is what a colonist actually receives: `costList x resourcesFractionWhenDeconstructed` (RimWorld's default fraction is 0.5 when unset). ⚠️ A fractional return is rounded by `GenMath.RoundRandom`, so 0.4 means *a 40% chance of one*, not a reliable return — only entries of 1 or more count as a yield here. Sub-1 returns are kept in the `chance` column of the TSV.

| bucket | count | meaning |
|---|---:|---|
| 🔴 **EXCLUDED** | 73 | refuses deconstruction — removable only by explosives |
| ✅ **USABLE-YIELDS** | 315 | deconstructs AND returns materials |
| ⚠️ **USABLE-DESTROY-ONLY** | 26 | deconstructs for nothing; must be destroyed for `killedLeavings` |
| ⚪ **USABLE-EMPTY** | 635 | deconstructs, returns nothing, ever — pure scenery |

---

## 1. 🔴 EXCLUDED — do not place where the clan must salvage

These descend from `NonDeconstructibleAncientBuildingBase` or otherwise set `building.deconstructible false`. **They are indistinguishable from the usable ones in a mod's texture folder**; the difference surfaces only when a colonist refuses the job. Place one only where a *permanent* scar is wanted.

| defName | mod | size | label |
|---|---|---|---|
| `AB_AncientBloodRainVent` | Alpha Biomes | 7x7 | ancient blood rain vent |
| `AB_AncientDeathPallVent` | Alpha Biomes | 7x7 | ancient death pall vent |
| `AB_AncientFreezingVent` | Alpha Biomes | 7x7 | ancient freezing vent |
| `AB_AncientGreyPallVent` | Alpha Biomes | 7x7 | ancient gray pall vent |
| `AB_SmoothedAncientMetals` | Alpha Biomes | 1x1 | smoothed ancient metal |
| `GU_AncientMetals` | Alpha Biomes | 1x1 | ancient metal |
| `AM_DownwardStairs` | Ancient urban ruins | 2x3 | Ancient construction site staircase |
| `AM_Entrance_Bunker` | Ancient urban ruins | 2x3 | Ancient staircase |
| `AM_Entrance_CommercialStreet` | Ancient urban ruins | 4x4 | Ancient escalator |
| `AM_Entrance_Mall_A` | Ancient urban ruins | 2x4 | Ancient escalator |
| `AM_Entrance_Mall_B` | Ancient urban ruins | 2x4 | Ancient escalator |
| `AM_Entrance_ReserveBunker` | Ancient urban ruins | 2x3 | Ancient staircase |
| `AM_Entrance_Shelter` | Ancient urban ruins | 2x3 | Ancient staircase |
| `AM_Entrance_Subway` | Ancient urban ruins | 4x4 | Ancient escalator |
| `AM_Exit_DoubleElevator` | Ancient urban ruins | 4x4 | Ancient escalator |
| `AM_Exit_Elevator` | Ancient urban ruins | 2x4 | Ancient escalator |
| `AM_Exit_L` | Ancient urban ruins | 4x4 | Ancient escalator |
| `AM_Exit_S` | Ancient urban ruins | 2x4 | Ancient escalator |
| `AM_Exit_Staircase` | Ancient urban ruins | 2x3 | Ancient staircase |
| `AM_Trader` | Ancient urban ruins | 4x4 | ancient logistics terminal |
| `ScrapCubeSculpture` | Anomaly | 1x1 | scrap cube sculpture |
| `AncientCryptosleepPod` | Core | 1x2 | ancient cryptosleep pod |
| `AncientMechGestatorTank` | Core | 2x2 | ancient mech vat |
| `CollapsedRocks` | Core | 1x1 | collapsed rocks |
| `CQF_CryptosleepCasket` | Custom Quest Framework | 1x2 | Ancient cryptosleep casket |
| `QE_Cabinet` | Custom Quest Framework | 2x1 | Ancient cabinet |
| `QE_DamagedSign` | Custom Quest Framework | 1x1 | Damaged sign |
| `AncientCommsConsole` | Ideology | 3x2 | ancient comms console |
| `SpaceshipDamaged` | MiningCo. Spaceship (Continued) | 9x18 | damaged spaceship |
| `AncientBlastDoor` | Odyssey | 1x1 | ancient blast door |
| `AncientFortifiedWall` | Odyssey | 1x1 | fortified wall |
| `AncientGravEngine` | Odyssey | 3x3 | ancient grav engine |
| `AncientGravReactor` | Odyssey | 5x5 | ancient grav reactor |
| `AncientHatch` | Odyssey | 3x3 | ancient stockpile entrance |
| `AncientHatchExit` | Odyssey | 3x3 | ancient stockpile exit |
| `AncientHeatVent` | Odyssey | 7x7 | ancient heat vent |
| `AncientSmokeVent` | Odyssey | 7x7 | ancient smoke vent |
| `AncientTerraformer` | Odyssey | 4x4 | ancient terraformer |
| `AncientToxVent` | Odyssey | 7x7 | ancient toxic vent |
| `AncientTransportPod` | Odyssey | 1x1 | ancient transport pod |
| `CerebrexCore_Destroyed` | Odyssey | 7x7 | destroyed cerebrex core |
| `MechRelay_Crashed` | Odyssey | 3x3 | crashed mechanoid relay |
| `OrbitalAncientFortifiedWall` | Odyssey | 1x1 | fortified wall |
| `Turret_AncientArmoredTurret` | Odyssey | 1x1 | ancient defender turret |
| `KOTOR_MineableJunk` | Star Wars KotOR Resources and Materials | 1x1 | Piled Junk |
| `VQEA_AncientBroadcastingStation` | Vanilla Quests Expanded - Ancients | 3x3 | ancient broadcasting station |
| `VQEA_AncientEmergencyPurifier` | Vanilla Quests Expanded - Ancients | 3x3 | ancient emergency purifier |
| `VQEA_AncientEmergencyPurifier_Off` | Vanilla Quests Expanded - Ancients | 3x3 | ancient emergency purifier |
| `VQEA_AncientVaultDoor` | Vanilla Quests Expanded - Ancients | 1x1 | ancient vault door |
| `VQEA_AncientVaultDoor_Large` | Vanilla Quests Expanded - Ancients | 2x1 | ancient large vault door |
| `VQEA_AncientVaultWall` | Vanilla Quests Expanded - Ancients | 1x1 | ancient vault wall |
| `VQEA_LockedAncientVaultDoor` | Vanilla Quests Expanded - Ancients | 1x1 | locked ancient vault door |
| `VQEA_LockedAncientVaultDoor_Large` | Vanilla Quests Expanded - Ancients | 2x1 | locked ancient large vault door |
| `VQEA_SplicehulkContainment` | Vanilla Quests Expanded - Ancients | 2x2 | splicehulk containment |
| `VQE_AncientAirlock` | Vanilla Quests Expanded - Cryptoforge | 1x1 | ancient airlock |
| `VQE_AncientAirlock_Large` | Vanilla Quests Expanded - Cryptoforge | 2x1 | ancient large airlock |
| `VQE_AncientBlackBox` | Vanilla Quests Expanded - Cryptoforge | 3x1 | ancient black box |
| `VQE_AncientFloorHeater` | Vanilla Quests Expanded - Cryptoforge | 2x2 | ancient floor heater |
| `VQE_AncientLandmine` | Vanilla Quests Expanded - Cryptoforge | 1x1 | ancient landmine |
| `VQE_AncientShipLandingBeacon` | Vanilla Quests Expanded - Cryptoforge | 1x1 | ancient ship landing beacon |
| `VQE_AncientTransmitterBeacon` | Vanilla Quests Expanded - Cryptoforge | 1x1 | acient transmitter beacon |
| `VQE_BustedShieldedTurret` | Vanilla Quests Expanded - Cryptoforge | 1x1 | busted shielded turret |
| `VQE_BustedSpacerAutocannon` | Vanilla Quests Expanded - Cryptoforge | 2x2 | busted spacer autocannon |
| `VQE_CryptoAncientTerminal` | Vanilla Quests Expanded - Cryptoforge | 1x1 | ancient terminal |
| `VQE_CryptoAncientTerminalBank` | Vanilla Quests Expanded - Cryptoforge | 3x1 | ancient terminal bank |
| `VQE_ForcedAncientAirlock` | Vanilla Quests Expanded - Cryptoforge | 1x1 | forced ancient airlock |
| `VQE_ForcedAncientAirlock_Large` | Vanilla Quests Expanded - Cryptoforge | 2x1 | forced ancient large airlock |
| `VQE_JammedAncientAirlock` | Vanilla Quests Expanded - Cryptoforge | 1x1 | stuck ancient airlock |
| `VQE_JammedAncientAirlock_Large` | Vanilla Quests Expanded - Cryptoforge | 2x1 | stuck ancient large airlock |
| `BTD_GravEngine_Damaged` | [BTD] Gravship Blueprints | 3x3 | damaged grav engine |
| `BTD_GravhulkEngine_Damaged` | [BTD] Gravship Blueprints | 5x5 | damaged gravhulk engine |
| `BTD_GravhulkEngine_Encrypted` | [BTD] Gravship Blueprints | 5x5 | encrypted gravhulk engine |
| `BTD_GravjumperEngine_Damaged` | [BTD] Gravship Blueprints | 1x1 | damaged gravjumper engine |

---

## 2. ✅ USABLE — deconstructs and yields

This is where the salvage economy gets tuned. Sorted by defName; `Graphic_Random` entries are marked because repetition is what makes a big wreck read as wallpaper, and variety is free when the def already has it.

| defName | mod | size | graphic | frac | a colonist receives |
|---|---|---|---|---|---|
| `AB_Mech_RuinedActivator` | Alpha Biomes | 1x1 | Graphic_Single | 0.5 | ComponentIndustrial x1.5 |
| `AB_Mech_RuinedAssembler` | Alpha Biomes | 3x3 | Graphic_Single | 0.5 | Steel x10.0, ChunkSlagSteel x2.5 |
| `AB_Mech_RuinedCapsule` | Alpha Biomes | 2x3 | Graphic_Single | 0.5 | Steel x5.0, ChunkSlagSteel x1.5 |
| `AB_Mech_RuinedCell` | Alpha Biomes | 1x1 | Graphic_Single | 0.5 | ComponentIndustrial x1.5 |
| `AB_Mech_RuinedLargeGunPlatform` | Alpha Biomes | 2x2 | Graphic_Single | 0.5 | Steel x2.5, ChunkSlagSteel x1.5 |
| `AG_AncientBandNode` | Alpha Genes | 2x2 | Graphic_Single | 0.5 | Steel x7.5 |
| `AG_AncientBasicRecharger` | Alpha Genes | 3x1 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AG_AncientFaultyLamp` | Alpha Genes | 1x2 | Graphic_Single | 0.5 | Steel x2.0 |
| `AG_AncientGeneAssembler` | Alpha Genes | 3x2 | Graphic_Multi | 0.5 | Steel x20.5 |
| `AG_AncientGeneBank` | Alpha Genes | 2x1 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AG_AncientGeneExtractor` | Alpha Genes | 2x2 | Graphic_Multi | 0.5 | Steel x20.5 |
| `AG_AncientGeneProcessor` | Alpha Genes | 2x2 | Graphic_Single | 0.5 | Steel x20.5 |
| `AG_AncientGrowthVat` | Alpha Genes | 1x2 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AG_AncientHugeBank` | Alpha Genes | 4x2 | Graphic_Single | 0.5 | Steel x20.5 |
| `AG_AncientLamp` | Alpha Genes | 1x1 | Graphic_Single | 0.5 | Steel x7.5 |
| `AG_AncientLargeMechGestator` | Alpha Genes | 4x3 | Graphic_Multi | 0.5 | Steel x20.5 |
| `AG_AncientLargeRecharger` | Alpha Genes | 3x2 | Graphic_Multi | 0.5 | Steel x20.5 |
| `AG_AncientMechGestator` | Alpha Genes | 3x2 | Graphic_Multi | 0.5 | Steel x20.5 |
| `AG_AncientPollutionPump` | Alpha Genes | 1x1 | Graphic_Single | 0.5 | Steel x7.5 |
| `AG_AncientSubcoreRipscanner` | Alpha Genes | 3x2 | Graphic_Multi | 0.5 | Steel x20.5 |
| `AG_AncientVitalsMonitor` | Alpha Genes | 1x1 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AG_AncientWastepackAtomizer` | Alpha Genes | 3x2 | Graphic_Single | 0.5 | Steel x20.5 |
| `AG_RuinedHospitalBed` | Alpha Genes | 1x2 | Graphic_Multi | 0.5 | Steel x40.0, ComponentIndustrial x2.5 |
| `AG_RuinedLabLamp` | Alpha Genes | 1x2 | Graphic_Single | 0.5 | Steel x2.0 |
| `AM_Amublance` | Ancient urban ruins | 5x2 | Graphic_Single | 0.5 | Steel x15.0, VVE_EngineBlock x1.0, VVE_CarAlternator x1.0, VVE_CarWheel x2.0, ChunkSlagSteel x4.0 |
| `AM_AncientDismantlingWorkbench` | Ancient urban ruins | 3x1 | Graphic_Multi | 0.5 | Steel x75.0, ComponentIndustrial x2.5 |
| `AM_AncientPodCar` | Ancient urban ruins | 3x2 | Graphic_Single | 0.5 | Steel x15.0, ChunkSlagSteel x1.5 |
| `AM_AncientRustedCar` | Ancient urban ruins | 2x4 | Graphic_Random | 0.5 | Steel x15.0, VVE_CarAlternator x1.0, VVE_CarWheel x1.0, ChunkSlagSteel x1.5 |
| `AM_AncientRustedCarFrame` | Ancient urban ruins | 2x3 | Graphic_Multi | 0.5 | Steel x15.0, VVE_CarAlternator x1.0, VVE_CarWheel x1.0, ChunkSlagSteel x2.5 |
| `AM_AncientRustedJeep` | Ancient urban ruins | 3x5 | Graphic_Multi | 0.5 | Steel x15.0, VVE_CarAlternator x1.0, VVE_CarWheel x1.5, ChunkSlagSteel x1.5 |
| `AM_AncientRustedTruck` | Ancient urban ruins | 2x4 | Graphic_Multi | 0.5 | Steel x15.0, VVE_CarWheel x2.0, ChunkSlagSteel x1.5 |
| `AM_AncientTruckCarriages` | Ancient urban ruins | 3x5 | Graphic_Multi | 0.5 | Steel x25.0 |
| `AM_ArmoredGate` | Ancient urban ruins | 3x1 | Graphic_Multi | 0.5 | Steel x30.0 |
| `AM_ArmoredGateL` | Ancient urban ruins | 4x1 | Graphic_Multi | 0.5 | Steel x50.0 |
| `AM_ArmoredGateS` | Ancient urban ruins | 2x1 | Graphic_Multi | 0.5 | Steel x25.0 |
| `AM_ArmoredGateXS` | Ancient urban ruins | 1x1 | Graphic_Multi | 0.5 | Steel x20.0 |
| `AM_ArmoredGate_invincible` | Ancient urban ruins | 3x1 | Graphic_Multi | 0.5 | Steel x30.0 |
| `AM_BDAShelfA_Open_Decoration` | Ancient urban ruins | 4x2 | Graphic_Single | 0.5 | Steel x7.5 |
| `AM_BDAShelfB_Open_Decoration` | Ancient urban ruins | 4x2 | Graphic_Single | 0.5 | Steel x7.5 |
| `AM_BTR82A` | Ancient urban ruins | 3x6 | Graphic_Multi | 0.5 | Steel x15.0, VVE_CarAlternator x1.0, ChunkSlagSteel x4.0 |
| `AM_DamagedEmptyShelves` | Ancient urban ruins | 2x1 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AM_DoubleDeckRacks_Open_Decoration` | Ancient urban ruins | 4x2 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AM_FireTruck` | Ancient urban ruins | 7x3 | Graphic_Single | 0.5 | Steel x15.0, VVE_EngineBlock x1.0, VVE_CarAlternator x1.0, VVE_CarWheel x2.0, ChunkSlagSteel x4.0 |
| `AM_MI26_D` | Ancient urban ruins | 13x5 | Graphic_Single | 0.5 | Steel x15.0, VVE_EngineBlock x2.5, VVE_CarAlternator x1.5, VVE_CarExhaust x4.0, VVE_CarWheel x2.0, VVE_CarBattery x1.0, VVE_CarSuspension x1.5, ChunkSlagSteel x6.0 |
| `AM_ThreeLayerRacks_Open_Decoration` | Ancient urban ruins | 4x2 | Graphic_Multi | 0.5 | Steel x7.5 |
| `AM_Wall_Atlas_AcientConcrete` | Ancient urban ruins | 1x1 | Graphic_Single | 0.5 | Steel x3.0 |
| `AM_Wall_Atlas_Concrete` | Ancient urban ruins | 1x1 | Graphic_Single | 0.5 | Steel x3.0 |
| `AM_Wall_Atlas_LoadBearing` | Ancient urban ruins | 1x1 | Graphic_Single | 0.5 | Steel x3.0 |
| `AM_WatchForGorehulk` | Ancient urban ruins | 1x1 | Graphic_Single | 0.5 | Steel x2.5 |
| `AncientAPC` | Core | 5x3 | Graphic_Single | 0.5 | VVE_CarWheel x1.5, VVE_CarSuspension x3.0, ComponentIndustrial x1.0, ChunkSlagSteel x6.0 |
| `AncientBandNode` | Biotech | 2x2 | Graphic_Single | 0.5 | Steel x12.5 |
| `AncientBarrel` | Core | 1x1 | Graphic_Random | 0.5 | Chemfuel x1.5, Steel x2.5 |
| `AncientBasicRecharger` | Core | 3x1 | Graphic_Multi | 0.5 | Steel x12.5 |
| `AncientConcreteBarrier` | Core | 1x1 | Graphic_Random | 0.5 | Steel x7.5 |
| `AncientCrate` | Core | 1x1 | Graphic_Random | 0.5 | Steel x3.5 |
| `AncientCryptosleepCasket` | Core | 1x2 | Graphic_Multi | 0.5 | Steel x90.0, Uranium x2.5 |
| `AncientDropshipEngine` | Core | 3x2 | Graphic_Single | 0.5 | ChunkSlagSteel x1.5 |
| `AncientExostriderCannon` | Biotech | 3x2 | Graphic_Single | 0.5 | ChunkMechanoidSlag x3.0 |
| `AncientExostriderHead` | Biotech | 2x2 | Graphic_Single | 0.5 | VVE_CarSuspension x1.0, ComponentIndustrial x1.5, ChunkMechanoidSlag x3.0, Steel x5.0 |
| `AncientExostriderLeg` | Biotech | 2x1 | Graphic_Random | 0.5 | ChunkMechanoidSlag x3.0 |
| `AncientFence` | Core | 1x1 | Graphic_Single | 0.5 | Steel x1.5 |
| `AncientFuelNode` | Core | 1x1 | Graphic_Random | 0.5 | Chemfuel x25.0 |
| `AncientGenerator` | Core | 2x2 | Graphic_Random | 0.5 | Chemfuel x14.5, Steel x17.5 |
| `AncientGiantWheel` | Core | 2x2 | Graphic_Random | 0.5 | Steel x7.5 |
| `AncientJetEngine` | Core | 3x2 | Graphic_Single | 0.5 | ChunkSlagSteel x3.0, ComponentIndustrial x1.0 |
| `AncientLamppost` | Core | 1x1 | Graphic_Random | 0.5 | Steel x7.5 |
| `AncientLargeMechGestator` | Core | 4x3 | Graphic_Single | 0.5 | Steel x22.5 |
| `AncientLongCrate` | Core | 1x1 | Graphic_Single | 0.5 | Steel x3.5 |
| `AncientMachine` | Core | 5x3 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.5, Steel x17.5 |
| `AncientMechDropBeacon` | Core | 1x1 | Graphic_Random | 0.5 | Steel x10.0 |
| `AncientMechGestator` | Core | 3x2 | Graphic_Multi | 0.5 | Steel x12.5 |
| `AncientMegaCannonBarrel` | Core | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.5, Steel x10.0 |
| `AncientMegaCannonTripod` | Core | 3x3 | Graphic_Random | 0.5 | ChunkSlagSteel x2.5, Steel x5.0 |
| `AncientMiniWarwalkerRemains` | Core | 5x3 | Graphic_Single | 0.5 | ChunkSlagSteel x5.0 |
| `AncientPipelineSection` | Core | 2x1 | Graphic_Single | 0.5 | ChunkSlagSteel x2.5, Chemfuel x18.5, Steel x2.5 |
| `AncientPipes` | Core | 1x1 | Graphic_Random | 0.5 | Steel x2.5, Chemfuel x1.5 |
| `AncientPodCar` | Core | 3x2 | Graphic_Single | 0.5 | VVE_CarSuspension x1.0, ComponentIndustrial x1.0, ChunkSlagSteel x3.0, Steel x5.0 |
| `AncientRustedCar` | Core | 2x4 | Graphic_Random | 0.5 | VVE_CarWheel x1.0, VVE_CarSuspension x1.0, ChunkSlagSteel x4.5, Steel x5.0 |
| `AncientRustedCarFrame` | Core | 2x3 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.5 |
| `AncientRustedDropship` | Core | 6x5 | Graphic_Single | 0.5 | ChunkSlagSteel x5.0 |
| `AncientRustedJeep` | Core | 3x5 | Graphic_Multi | 0.5 | VVE_CarWheel x1.0, VVE_CarSuspension x2.5, ComponentIndustrial x1.0, ChunkSlagSteel x5.0, Steel x5.0 |
| `AncientRustedTruck` | Core | 2x4 | Graphic_Multi | 0.5 | VVE_CarWheel x1.5, VVE_CarSuspension x2.0, ChunkSlagSteel x4.5, ComponentIndustrial x1.0, Steel x5.0 |
| `AncientSecurityTurret` | Core | 1x1 | Graphic_Random | 0.5 | Steel x5.0 |
| `AncientShipBeacon` | Core | 1x1 | Graphic_Single | 0.5 | Steel x3.5 |
| `AncientSmallCrate` | Core | 1x1 | Graphic_Single | 0.5 | Steel x3.5 |
| `AncientStandardRecharger` | Core | 3x2 | Graphic_Multi | 0.5 | Steel x22.5 |
| `AncientStorageCylinder` | Core | 2x1 | Graphic_Multi | 0.5 | Steel x12.5 |
| `AncientStorageUnitLGE` | Go Explore! | 4x2 | Graphic_Multi | 0.5 | Steel x40.0, ComponentIndustrial x1.5, Plasteel x13.5, Uranium x10.0 |
| `AncientTank` | Core | 5x3 | Graphic_Single | 0.5 | VVE_CarWheel x3.0, VVE_CarSuspension x4.0, ComponentIndustrial x1.0, ChunkSlagSteel x7.5 |
| `AncientTankTrap` | Core | 2x2 | Graphic_Random | 0.5 | Steel x3.5 |
| `AncientToxifierGenerator` | Biotech | 2x2 | Graphic_Single | 0.5 | Steel x12.5 |
| `AncientUplink` | Odyssey | 2x2 | Graphic_Single | 0.5 | Steel x50.0 |
| `AncientWarspiderRemains` | Core | 5x5 | Graphic_Single | 0.5 | ChunkSlagSteel x5.0 |
| `AncientWarwalkerClaw` | Core | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.5 |
| `AncientWarwalkerFoot` | Core | 2x2 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0 |
| `AncientWarwalkerLeg` | Core | 2x4 | Graphic_Multi | 0.5 | ChunkSlagSteel x3.0 |
| `AncientWarwalkerShell` | Core | 5x3 | Graphic_Single | 0.5 | VVE_CarSuspension x1.5, ChunkSlagSteel x4.0 |
| `AncientWarwalkerTorso` | Core | 4x6 | Graphic_Multi | 0.5 | ChunkSlagSteel x5.0 |
| `AncientWheel` | Core | 1x1 | Graphic_Random | 0.5 | Steel x5.0 |
| `BreadMoAM_AncientAutomaticDrillingRig` | Ancient mining industry | 3x3 | Graphic_Single | 0.5 | Steel x75.0 |
| `BreadMoAM_AncientBarrierGate` | Ancient mining industry | 4x1 | Graphic_Multi | 0.5 | Steel x10.0 |
| `BreadMoAM_AncientBrokenTurret` | Ancient mining industry | 2x2 | Graphic_Multi | 0.5 | Steel x15.0 |
| `BreadMoAM_AncientElectricalEquipment` | Ancient mining industry | 1x4 | Graphic_Multi | 0.5 | Steel x7.5 |
| `BreadMoAM_AncientEmptyMiningCar` | Ancient mining industry | 5x3 | Graphic_Single | 0.5 | Steel x125.0 |
| `BreadMoAM_AncientExcavatorBucketWheel` | Ancient mining industry | 5x5 | Graphic_Multi | 0.5 | Steel x27.5, Plasteel x7.5, Uranium x7.5 |
| `BreadMoAM_AncientExcavatorPowerFacilities` | Ancient mining industry | 5x5 | Graphic_Single | 0.5 | Steel x75.0 |
| `BreadMoAM_AncientGiantRockExcavator` | Ancient mining industry | 9x9 | Graphic_Single | 0.5 | Steel x125.0 |
| `BreadMoAM_AncientIndoorFireHydrants` | Ancient mining industry | 1x1 | Graphic_Multi | 0.5 | Steel x5.0 |
| `BreadMoAM_AncientMineralConveyor` | Ancient mining industry | 1x4 | Graphic_Multi | 0.5 | Steel x2.5 |
| `BreadMoAM_AncientMineralExports` | Ancient mining industry | 1x2 | Graphic_Multi | 0.5 | Steel x2.5 |
| `BreadMoAM_AncientMudCarriage` | Ancient mining industry | 5x3 | Graphic_Single | 0.5 | Steel x125.0 |
| `BreadMoAM_AncientOreDressingMachine` | Ancient mining industry | 5x5 | Graphic_Single | 0.5 | Steel x17.5, Plasteel x7.5 |
| `BreadMoAM_AncientPlasteelMiningCars` | Ancient mining industry | 5x3 | Graphic_Single | 0.5 | Steel x175.0, Plasteel x187.5 |
| `BreadMoAM_AncientRockMiningCar` | Ancient mining industry | 5x3 | Graphic_Single | 0.5 | Steel x125.0 |
| `BreadMoAM_AncientRustedTruck` | Ancient mining industry | 4x2 | Graphic_Multi | 0.5 | Steel x50.0 |
| `BreadMoAM_AncientSemiTrailer` | Ancient mining industry | 4x2 | Graphic_Multi | 0.5 | Steel x45.0 |
| `BreadMoAM_AncientSteelMiningCars` | Ancient mining industry | 5x3 | Graphic_Single | 0.5 | Steel x375.0 |
| `BreadMoAM_AncientTruckCompartment` | Ancient mining industry | 4x2 | Graphic_Multi | 0.5 | Steel x40.0 |
| `BreadMoAM_AncientTunnelBoringMachine` | Ancient mining industry | 5x7 | Graphic_Multi | 0.5 | Steel x42.5, ComponentIndustrial x2.0, Plasteel x32.5, Uranium x8.5 |
| `BreadMoAM_AncientTunnelStructuralSupport_a` | Ancient mining industry | 1x4 | Graphic_Multi | 0.5 | Steel x75.0 |
| `BreadMoAM_AncientTunnelStructuralSupport_b` | Ancient mining industry | 1x4 | Graphic_Multi | 0.5 | Steel x7.5 |
| `BreadMoAM_AncientTunnelStructuralSupport_c` | Ancient mining industry | 1x4 | Graphic_Multi | 0.5 | Steel x7.5 |
| `BreadMoAM_AncientUraniumMiningCars` | Ancient mining industry | 5x3 | Graphic_Single | 0.5 | Steel x175.0, Uranium x187.5 |
| `BreadMoAM_Turret_ShotgunTurret` | Ancient mining industry | 1x1 | Graphic_Single | 0.5 | Steel x35.0, ComponentIndustrial x1.5 |
| `BreadMo_AncientRemoteMineralScanners` | Ancient mining industry | 3x3 | Graphic_Single | 0.5 | Steel x100.0, ComponentIndustrial x3.0, ComponentSpacer x1.0 |
| `BrokenGravEngine` | Gravship Crashes | 3x3 | Graphic_Single | 0.5 | GravlitePanel x17.5, Steel x40.0 |
| `BrokenStorageUnitLGE` | Go Explore! | 4x2 | Graphic_Single | 0.5 | Steel x40.0, ComponentIndustrial x5.0, Plasteel x30.0 |
| `ChunkA` | Adaptive Ideology Storage | 5x2 | Graphic_Single | 0.5 | Steel x262.5 |
| `ChunkB` | Adaptive Ideology Storage | 5x2 | Graphic_Single | 0.5 | Steel x262.5 |
| `GR_AncientBioBattery` | Vanilla Genetics Expanded | 1x2 | Graphic_Multi | 0.5 | Steel x7.5, ChunkSlagSteel x1.0 |
| `GR_AncientCrate` | Vanilla Genetics Expanded | 1x1 | Graphic_Random | 0.5 | Steel x1.0 |
| `GR_AncientCrateDouble` | Vanilla Genetics Expanded | 2x1 | Graphic_Multi | 0.5 | Steel x2.0 |
| `GR_AncientCratePile` | Vanilla Genetics Expanded | 2x2 | Graphic_Random | 0.5 | Steel x2.0 |
| `GR_AncientCryofreezer` | Vanilla Genetics Expanded | 3x3 | Graphic_Single | 0.5 | Steel x25.0, ChunkSlagSteel x1.0 |
| `GR_AncientElectrowomb` | Vanilla Genetics Expanded | 1x1 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_AncientElectrowombLarge` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x10.0, ChunkSlagSteel x1.0 |
| `GR_AncientGeneticsTinkeringTable` | Vanilla Genetics Expanded | 5x2 | Graphic_Multi | 0.5 | Steel x5.0, ChunkSlagSteel x1.0 |
| `GR_AncientGenomeExtractor` | Vanilla Genetics Expanded | 3x1 | Graphic_Multi | 0.5 | Steel x10.0 |
| `GR_AncientGenomeRecombinator` | Vanilla Genetics Expanded | 3x2 | Graphic_Multi | 0.5 | Steel x15.0 |
| `GR_AncientGenomorpher` | Vanilla Genetics Expanded | 5x5 | Graphic_Multi | 0.5 | Steel x50.0 |
| `GR_AncientTechCrate` | Vanilla Genetics Expanded | 3x1 | Graphic_Multi | 0.5 | Steel x2.0 |
| `GR_AncientTissueGrinder` | Vanilla Genetics Expanded | 3x2 | Graphic_Multi | 0.5 | Steel x10.0, ChunkSlagSteel x1.0 |
| `GR_BioLight` | Vanilla Genetics Expanded | 1x2 | Graphic_Multi | 0.5 | Steel x2.0 |
| `GR_CommsTable` | Vanilla Genetics Expanded | 3x3 | Graphic_Single | 0.5 | Steel x2.5 |
| `GR_MonitorBank` | Vanilla Genetics Expanded | 5x2 | Graphic_Multi | 0.5 | Steel x25.0, ChunkSlagSteel x1.0 |
| `GR_Rack` | Vanilla Genetics Expanded | 1x1 | Graphic_Single | 0.5 | Steel x2.5 |
| `GR_RuinedAncientBioBattery` | Vanilla Genetics Expanded | 3x3 | Graphic_Single | 0.5 | Steel x10.0 |
| `GR_RuinedAncientGeneTailoringPod` | Vanilla Genetics Expanded | 3x2 | Graphic_Single | 0.5 | Steel x10.0, ChunkSlagSteel x1.5 |
| `GR_RuinedAnimalControlHub` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x2.5, ChunkSlagSteel x1.5 |
| `GR_RuinedAnimalEnrichmentCenter` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x12.5, ChunkSlagSteel x1.5 |
| `GR_RuinedArchotechPlatform` | Vanilla Genetics Expanded | 7x6 | Graphic_Single | 0.5 | Steel x50.0, ChunkSlagSteel x1.0 |
| `GR_RuinedBarrelDouble` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_RuinedGeneDuplicator` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x12.5, ChunkSlagSteel x1.0 |
| `GR_RuinedGenePod` | Vanilla Genetics Expanded | 2x2 | Graphic_Random | 0.5 | Steel x5.0 |
| `GR_RuinedGeneRecombinator` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x7.5, ChunkSlagSteel x1.0 |
| `GR_RuinedGeneticDatabase` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x7.5, ChunkSlagSteel x1.0 |
| `GR_RuinedGeneticExtractionTable` | Vanilla Genetics Expanded | 3x1 | Graphic_Multi | 0.5 | Steel x10.0 |
| `GR_RuinedGeneticStorage` | Vanilla Genetics Expanded | 1x1 | Graphic_Random | 0.5 | Steel x5.0 |
| `GR_RuinedGenomeSequencer` | Vanilla Genetics Expanded | 3x3 | Graphic_Single | 0.5 | Steel x20.0 |
| `GR_RuinedHexagelPlant` | Vanilla Genetics Expanded | 6x6 | Graphic_Single | 0.5 | Steel x50.0, ChunkSlagSteel x1.0 |
| `GR_RuinedIncubator` | Vanilla Genetics Expanded | 1x1 | Graphic_Single | 0.5 | Steel x2.5 |
| `GR_RuinedLabBarrel` | Vanilla Genetics Expanded | 1x1 | Graphic_Random | 0.5 | Steel x2.5 |
| `GR_RuinedLabShelf` | Vanilla Genetics Expanded | 3x1 | Graphic_Multi | 0.5 | Steel x5.0 |
| `GR_RuinedMechanoidTinkeringTable` | Vanilla Genetics Expanded | 5x2 | Graphic_Multi | 0.5 | Steel x10.0, ChunkSlagSteel x1.0 |
| `GR_RuinedMutaniteCentrifuge` | Vanilla Genetics Expanded | 3x3 | Graphic_Single | 0.5 | Steel x10.0 |
| `GR_RuinedNutrientVat` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_RuinedPulpRecycler` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x7.5, ChunkSlagSteel x1.0 |
| `GR_RuinedPulper` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_RuinedRefrigeratedCoils` | Vanilla Genetics Expanded | 6x2 | Graphic_Single | 0.5 | Steel x15.0 |
| `GR_RuinedTissueGrowingVat` | Vanilla Genetics Expanded | 2x2 | Graphic_Single | 0.5 | Steel x7.5 |
| `GR_Ruined_Mechahybrid_Antenna` | Vanilla Genetics Expanded | 3x3 | Graphic_Single | 0.5 | Steel x20.0 |
| `GR_Ruined_Mechahybridizer` | Vanilla Genetics Expanded | 5x5 | Graphic_Multi | 0.5 | Steel x25.0 |
| `GR_SignA` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignB` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignC` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignD` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignE` | Vanilla Genetics Expanded | 2x1 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignF` | Vanilla Genetics Expanded | 2x1 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignG` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_SignH` | Vanilla Genetics Expanded | 1x2 | Graphic_Single | 0.5 | Steel x5.0 |
| `GR_Sink` | Vanilla Genetics Expanded | 1x1 | Graphic_Multi | 0.5 | Steel x5.0 |
| `GR_SmallBioLight` | Vanilla Genetics Expanded | 1x1 | Graphic_Single | 0.5 | Steel x1.0 |
| `GR_Toilet` | Vanilla Genetics Expanded | 1x1 | Graphic_Multi | 0.5 | Steel x5.0 |
| `RG_AncientPowerPole` | ReGrowth 2 | 1x1 | Graphic_Random | 0.5 | WoodLog x12.5 |
| `ShipChunk` | Core | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x5.5, Steel x20.0 |
| `ShipChunk_Mech` | Odyssey | 2x2 | Graphic_Random | 1.0 | Steel x40.0, GravlitePanel x15.0 |
| `ShipChunk_durasteel` | Star Wars KotOR Resources and Materials | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x5.5, Plasteel x10.0, KOTOR_AlloyDurasteel x20.0 |
| `ShuttleCrashed` | Core | 5x3 | Graphic_Single | 0.5 | Steel x20.0, Plasteel x35.0, ComponentIndustrial x5.0 |
| `ShuttleCrashed_Exitable` | Biotech | 5x3 | Graphic_Single | 0.5 | Steel x20.0, Plasteel x35.0, ComponentIndustrial x5.0 |
| `ShuttleCrashed_Exitable_Mechanitor` | Biotech | 5x3 | Graphic_Single | 0.5 | Steel x20.0, Plasteel x35.0, ComponentIndustrial x5.0 |
| `TraderShipsShipChunk` | Trader ships | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x5.5, Steel x20.0 |
| `VEE_DriftwoodChunk` | Vanilla Landmarks Expanded | 1x1 | Graphic_Random | 0.5 | WoodLog x10.0 |
| `VEE_JadeChunk` | Vanilla Landmarks Expanded | 1x1 | Graphic_Random | 0.5 | Jade x2.0 |
| `VEE_ObsidianChunk` | Vanilla Landmarks Expanded | 1x1 | Graphic_Random | 0.5 | Obsidian x2.5 |
| `VEE_ShipChunkHuman` | Vanilla Events Expanded | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x3.0, Steel x20.0 |
| `VEE_ShipChunkHuman_Cargo` | Vanilla Events Expanded | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x3.0, Steel x20.0 |
| `VEE_ShipChunkHuman_DropPod_Spawner` | Vanilla Events Expanded | 2x2 | Graphic_Single | 0.5 | ComponentIndustrial x3.0, Steel x20.0 |
| `VEE_ShipChunkHuman_Volatile_Spawner` | Vanilla Events Expanded | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x3.0, Steel x20.0 |
| `VEE_Shuttle` | Vanilla Events Expanded | 5x3 | Graphic_Single | 0.5 | Plasteel x35.0, ComponentIndustrial x6.0, Steel x20.0 |
| `VEE_Shuttle_Combat` | Vanilla Events Expanded | 5x3 | Graphic_Single | 0.5 | Plasteel x35.0, ComponentIndustrial x6.0, Steel x20.0 |
| `VEE_Shuttle_Heavy` | Vanilla Events Expanded | 5x3 | Graphic_Single | 0.5 | Plasteel x35.0, ComponentIndustrial x6.0, Steel x20.0 |
| `VFEI2_InfestedShipChunk` | Vanilla Factions Expanded - Insectoids 2 | 2x2 | Graphic_Random | 0.5 | ChunkSlagSteel x1.0, InsectJelly x5.0 |
| `VFEP_ShipChunkBattery` | Vanilla Factions Expanded - Pirates | 2x2 | Graphic_Single | 0.5 | ComponentIndustrial x5.0, Steel x40.0 |
| `VFEP_ShipChunkCryptosleepCasket` | Vanilla Factions Expanded - Pirates | 2x2 | Graphic_Single | 0.5 | ComponentIndustrial x2.0, Steel x35.0 |
| `VFEP_ShipChunkDebris` | Vanilla Factions Expanded - Pirates | 2x2 | Graphic_Random | 0.5 | ComponentIndustrial x3.0, Steel x65.0 |
| `VFEP_ShipChunkFuelTank` | Vanilla Factions Expanded - Pirates | 2x2 | Graphic_Single | 0.5 | Chemfuel x120.0, Steel x20.0 |
| `VFEP_ShipChunkGauntletTurret` | Vanilla Factions Expanded - Pirates | 3x3 | Graphic_Single | 0.5 | Steel x80.0, ComponentIndustrial x3.0, ComponentSpacer x4.0 |
| `VFEP_ShipChunkReactor` | Vanilla Factions Expanded - Pirates | 2x2 | Graphic_Single | 0.5 | Steel x60.0, ComponentIndustrial x4.0, ComponentSpacer x4.0 |
| `VFEP_ShipChunkVolatileEngine` | Vanilla Factions Expanded - Pirates | 2x2 | Graphic_Single | 0.5 | ComponentIndustrial x2.0, Steel x40.0 |
| `VGE_GravhulkEngine` | Vanilla Gravship Expanded - Chapter 1 | 5x5 | VanillaGravshipExpanded.Graphic_GravEngineSingle | 0.5 | Gravcore x2.5, GravlitePanel x100.0, ComponentSpacer x8.0, Plasteel x100.0 |
| `VME_AncientAPC` | Vanilla Ideology Expanded - Memes and Structures | 5x3 | Graphic_Single | 0.5 | VVE_CarWheel x1.5, VVE_CarSuspension x3.0, ComponentIndustrial x1.0, ChunkSlagSteel x6.0 |
| `VME_AncientBarrel` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Random | 0.5 | Chemfuel x1.5, Steel x2.5 |
| `VME_AncientCrate` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Random | 0.5 | Steel x3.5 |
| `VME_AncientDropshipEngine` | Vanilla Ideology Expanded - Memes and Structures | 3x2 | Graphic_Single | 0.5 | ChunkSlagSteel x1.5 |
| `VME_AncientFence` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Single | 0.5 | Steel x1.5 |
| `VME_AncientGenerator` | Vanilla Ideology Expanded - Memes and Structures | 2x2 | Graphic_Random | 0.5 | Chemfuel x14.5, Steel x17.5 |
| `VME_AncientGiantWheel` | Vanilla Ideology Expanded - Memes and Structures | 2x2 | Graphic_Random | 0.5 | Steel x7.5 |
| `VME_AncientJetEngine` | Vanilla Ideology Expanded - Memes and Structures | 3x2 | Graphic_Single | 0.5 | ChunkSlagSteel x3.0, ComponentIndustrial x1.0 |
| `VME_AncientMachine` | Vanilla Ideology Expanded - Memes and Structures | 5x3 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.5, Steel x17.5 |
| `VME_AncientMegaCannonBarrel` | Vanilla Ideology Expanded - Memes and Structures | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.5, Steel x10.0 |
| `VME_AncientMegaCannonTripod` | Vanilla Ideology Expanded - Memes and Structures | 3x3 | Graphic_Random | 0.5 | ChunkSlagSteel x2.5, Steel x5.0 |
| `VME_AncientMiniWarwalkerRemains` | Vanilla Ideology Expanded - Memes and Structures | 5x3 | Graphic_Single | 0.5 | ChunkSlagSteel x5.0 |
| `VME_AncientPipelineSection` | Vanilla Ideology Expanded - Memes and Structures | 2x1 | Graphic_Single | 0.5 | ChunkSlagSteel x2.5, Chemfuel x18.5, Steel x2.5 |
| `VME_AncientPipes` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Random | 0.5 | Steel x2.5, Chemfuel x2.5 |
| `VME_AncientPodCar` | Vanilla Ideology Expanded - Memes and Structures | 3x2 | Graphic_Single | 0.5 | VVE_CarSuspension x1.0, ComponentIndustrial x1.0, ChunkSlagSteel x3.0, Steel x5.0 |
| `VME_AncientRustedCar` | Vanilla Ideology Expanded - Memes and Structures | 2x4 | Graphic_Random | 0.5 | VVE_CarWheel x1.0, VVE_CarSuspension x1.0, ChunkSlagSteel x4.5, Steel x5.0 |
| `VME_AncientRustedCarFrame` | Vanilla Ideology Expanded - Memes and Structures | 2x3 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.5 |
| `VME_AncientRustedJeep` | Vanilla Ideology Expanded - Memes and Structures | 3x5 | Graphic_Multi | 0.5 | VVE_CarWheel x1.0, VVE_CarSuspension x2.5, ComponentIndustrial x1.0, ChunkSlagSteel x5.0, Steel x5.0 |
| `VME_AncientRustedTruck` | Vanilla Ideology Expanded - Memes and Structures | 2x4 | Graphic_Multi | 0.5 | VVE_CarWheel x1.5, VVE_CarSuspension x2.0, ChunkSlagSteel x4.5, ComponentIndustrial x1.0, Steel x5.0 |
| `VME_AncientSecurityTurret` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Random | 0.5 | Steel x5.0 |
| `VME_AncientShipBeacon` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Single | 0.5 | Steel x3.5 |
| `VME_AncientStorageCylinder` | Vanilla Ideology Expanded - Memes and Structures | 2x1 | Graphic_Multi | 0.5 | Steel x12.5 |
| `VME_AncientTank` | Vanilla Ideology Expanded - Memes and Structures | 5x3 | Graphic_Single | 0.5 | VVE_CarWheel x3.0, VVE_CarSuspension x4.0, ComponentIndustrial x1.0, ChunkSlagSteel x7.5 |
| `VME_AncientTankTrap` | Vanilla Ideology Expanded - Memes and Structures | 2x2 | Graphic_Random | 0.5 | Steel x3.5 |
| `VME_AncientWarspiderRemains` | Vanilla Ideology Expanded - Memes and Structures | 5x5 | Graphic_Single | 0.5 | ChunkSlagSteel x5.0 |
| `VME_AncientWarwalkerClaw` | Vanilla Ideology Expanded - Memes and Structures | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.5 |
| `VME_AncientWarwalkerFoot` | Vanilla Ideology Expanded - Memes and Structures | 2x2 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0 |
| `VME_AncientWarwalkerLeg` | Vanilla Ideology Expanded - Memes and Structures | 2x4 | Graphic_Multi | 0.5 | ChunkSlagSteel x3.0 |
| `VME_AncientWarwalkerShell` | Vanilla Ideology Expanded - Memes and Structures | 5x3 | Graphic_Single | 0.5 | VVE_CarSuspension x1.5, ChunkSlagSteel x4.0 |
| `VME_AncientWarwalkerTorso` | Vanilla Ideology Expanded - Memes and Structures | 4x6 | Graphic_Multi | 0.5 | ChunkSlagSteel x5.0 |
| `VME_AncientWheel` | Vanilla Ideology Expanded - Memes and Structures | 1x1 | Graphic_Random | 0.5 | Steel x5.0 |
| `VQEA_AncientBioBattery` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | Steel x90.0, ComponentIndustrial x4.0 |
| `VQEA_AncientBroadcastingStation_Off` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | Steel x30.0, ComponentIndustrial x1.0 |
| `VQEA_AncientChemfuelGenerator` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | Steel x30.0, ComponentIndustrial x1.5 |
| `VQEA_AncientFoosballTable` | Vanilla Quests Expanded - Ancients | 2x1 | Graphic_Multi | 0.5 | Steel x10.0, Cloth x7.5, WoodLog x6.5 |
| `VQEA_AncientGenepackCrate` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientGenepackCrate_Empty` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientGreenbed` | Vanilla Quests Expanded - Ancients | 1x2 | Graphic_Multi | 0.5 | Steel x20.0, ComponentIndustrial x1.0 |
| `VQEA_AncientHospitalArmchair` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | Steel x5.0, Synthread x4.0 |
| `VQEA_AncientHospitalBench` | Vanilla Quests Expanded - Ancients | 2x1 | Graphic_Multi | 0.5 | Steel x5.0, Synthread x2.0 |
| `VQEA_AncientHospitalCrib` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | Steel x5.0, Synthread x10.0 |
| `VQEA_AncientIVStand` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Random | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientIncubator` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientKitchenette` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientLaboratoryCasket` | Vanilla Quests Expanded - Ancients | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0, Steel x25.0, Uranium x3.0 |
| `VQEA_AncientLaboratoryCasket_Empty` | Vanilla Quests Expanded - Ancients | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0, Steel x25.0, Uranium x3.0 |
| `VQEA_AncientMedicalPartition` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0, Synthread x5.0 |
| `VQEA_AncientOfficeDesk` | Vanilla Quests Expanded - Ancients | 3x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.0 |
| `VQEA_AncientOfficePrinter` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0, ComponentIndustrial x1.0 |
| `VQEA_AncientOrganBox` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientOrganBox_Empty` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientPipelineJunction_Off` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | ChunkSlagSteel x6.0 |
| `VQEA_AncientPipelineJunction_On` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | ChunkSlagSteel x6.0 |
| `VQEA_AncientRepairBench` | Vanilla Quests Expanded - Ancients | 3x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.0 |
| `VQEA_AncientResearchCountertop` | Vanilla Quests Expanded - Ancients | 3x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.0 |
| `VQEA_AncientSink` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientStorageHeater` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientSunLamp` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Random | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientToyBox` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientVitalsMonitor` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientWaterCooler` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_AncientWonderdoc` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Multi | 1.0 | Steel x180.0, ComponentSpacer x4.0, Plasteel x20.0 |
| `VQEA_AncientWorkshop` | Vanilla Quests Expanded - Ancients | 3x1 | Graphic_Multi | 0.5 | Steel x90.0, ComponentIndustrial x4.0 |
| `VQEA_BustedAncientWonderdoc` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Multi | 1.0 | Steel x120.0, Plasteel x10.0 |
| `VQEA_BustedControlPanel` | Vanilla Quests Expanded - Ancients | 3x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.0 |
| `VQEA_DestroyedGravExtender` | Vanilla Gravship Expanded - Chapter 1 | 1x1 | Graphic_Single | 0.5 | Steel x40.0, Gravcore x1.0, GravlitePanel x15.0, ComponentIndustrial x1.0 |
| `VQEA_DestroyedLargeThruster` | Vanilla Gravship Expanded - Chapter 1 | 2x2 | Graphic_Multi | 0.5 | Steel x65.0, ComponentIndustrial x1.0, BlocksVacstone x10.0 |
| `VQEA_DestroyedSmallAstrofuelTank` | Vanilla Gravship Expanded - Chapter 1 | 2x2 | Graphic_Multi | 0.5 | Steel x60.0 |
| `VQEA_DestroyedSmallHeatsink` | Vanilla Gravship Expanded - Chapter 1 | 2x2 | Graphic_Multi | 0.5 | Steel x30.0 |
| `VQEA_DestroyedSmallOxygenTank` | Vanilla Gravship Expanded - Chapter 1 | 2x2 | Graphic_Multi | 0.5 | Steel x25.0 |
| `VQEA_DestroyedSmallThruster` | Vanilla Gravship Expanded - Chapter 1 | 1x2 | Graphic_Multi | 0.5 | Steel x45.0, ComponentIndustrial x1.0 |
| `VQEA_RuinedAberrationRedirector` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | ChunkSlagSteel x3.0 |
| `VQEA_RuinedArchitePathingArray` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | ChunkSlagSteel x3.0 |
| `VQEA_RuinedArchiteRecycler` | Vanilla Quests Expanded - Ancients | 2x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_RuinedArchogenInjector` | Vanilla Quests Expanded - Ancients | 3x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x3.0 |
| `VQEA_RuinedCognitiveRecoveryArray` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_RuinedComplexityHarmonizer` | Vanilla Quests Expanded - Ancients | 3x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x3.0 |
| `VQEA_RuinedGenomicAttenuator` | Vanilla Quests Expanded - Ancients | 2x2 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0 |
| `VQEA_RuinedMutagenInhibitorCore` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | ChunkSlagSteel x3.0 |
| `VQEA_RuinedNeurostabilizerArray` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_RuinedRapidInfusionPump` | Vanilla Quests Expanded - Ancients | 1x1 | Graphic_Single | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_RuinedRejectionBufferCoil` | Vanilla Quests Expanded - Ancients | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQEA_RuinedSpliceframeUplink` | Vanilla Quests Expanded - Ancients | 2x2 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0 |
| `VQEA_RuinedTraitSelectionPrism` | Vanilla Quests Expanded - Ancients | 3x3 | Graphic_Single | 0.5 | ChunkSlagSteel x3.0 |
| `VQEA_RustedHospitalBed` | Vanilla Quests Expanded - Ancients | 1x2 | Graphic_Multi | 0.5 | Steel x30.0, Synthread x4.0 |
| `VQE_AncientARCPart` | Vanilla Quests Expanded - The Generator | 2x2 | Graphic_Random | 0.5 | ChunkSlagSteel x1.5 |
| `VQE_AncientARCPrototype_One` | Vanilla Quests Expanded - The Generator | 6x6 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0, ComponentIndustrial x1.0, Steel x50.0 |
| `VQE_AncientARCPrototype_Three` | Vanilla Quests Expanded - The Generator | 6x6 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0, ComponentIndustrial x2.0, Steel x95.0, VQE_GenetronComponent x1.0 |
| `VQE_AncientARCPrototype_Two` | Vanilla Quests Expanded - The Generator | 6x6 | Graphic_Single | 0.5 | ChunkSlagSteel x2.0, ComponentIndustrial x2.0, Steel x70.0 |
| `VQE_AncientBlackBox_Off` | Vanilla Quests Expanded - Cryptoforge | 3x1 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0 |
| `VQE_AncientConstructionCrane` | Vanilla Quests Expanded - The Generator | 7x4 | Graphic_Single | 0.5 | ChunkSlagSteel x4.0 |
| `VQE_AncientConstructionTruck` | Vanilla Quests Expanded - The Generator | 6x3 | Graphic_Random | 0.5 | ChunkSlagSteel x3.0 |
| `VQE_AncientDigger` | Vanilla Quests Expanded - The Generator | 7x4 | Graphic_Single | 0.5 | ChunkSlagSteel x4.0 |
| `VQE_AncientGenetron` | Vanilla Quests Expanded - The Generator | 6x6 | Graphic_Single | 0.5 | Steel x220.0, ComponentIndustrial x3.0, ChunkSlagSteel x2.0, VQE_GenetronComponent x2.5 |
| `VQE_AncientGeothermalGenetron` | Vanilla Quests Expanded - The Generator | 6x6 | Graphic_Single | 0.5 | Steel x220.0, ComponentIndustrial x3.0, ChunkSlagSteel x2.0, VQE_GenetronComponent x2.5 |
| `VQE_AncientOvergrownGenetron` | Vanilla Quests Expanded - The Generator | 6x6 | Graphic_Single | 0.5 | Steel x160.0, ChunkSlagSteel x3.0, VQE_GenetronComponent x4.0 |
| `VQE_AncientShieldedTurret` | Vanilla Quests Expanded - Cryptoforge | 1x1 | Graphic_Single | 0.5 | Steel x22.0, ComponentIndustrial x1.0 |
| `VQE_AncientSpacerAutocannon` | Vanilla Quests Expanded - Cryptoforge | 2x2 | Graphic_Single | 0.5 | Steel x88.0, Plasteel x20.0, ComponentIndustrial x2.0 |
| `VQE_AncientWargamingTable` | Vanilla Quests Expanded - Cryptoforge | 2x3 | Graphic_Multi | 0.5 | Steel x40.0, Cloth x40.0, Plasteel x5.0 |
| `VQE_BlueprintsBench` | Vanilla Quests Expanded - Cryptoforge | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x2.0 |
| `VQE_FrozenEmptyCryptosleepPod` | Vanilla Quests Expanded - Cryptoforge | 1x2 | Graphic_Multi | 0.5 | ChunkSlagSteel x1.0, Steel x25.0, Uranium x3.0 |
| `VQE_RuinedHospitalBed` | Vanilla Quests Expanded - Cryptoforge | 1x2 | Graphic_Multi | 0.5 | Steel x35.0 |
| `VqEA_AncientCookingStation` | Vanilla Quests Expanded - Ancients | 3x1 | Graphic_Multi | 0.5 | Steel x50.0, ComponentIndustrial x2.0 |
| `asf_rustedtoolbox` | Adaptive Ideology Storage | 2x1 | Graphic_Multi | 0.5 | Steel x10.0 |
| `ucp_scraps` | Tabletop Decorations | 1x1 | Graphic_Single | 0.5 | Cloth x3.5 |

---

## 3. ⚠️ USABLE but returns NOTHING on deconstruct

**635 defs deconstruct for nothing and 26 more give up materials only when DESTROYED.** Over half the ruins kit is scenery, not salvage. If the campaign wants these to be strippable, this is the list to patch a `costList` onto — the established local idiom (*Salvage Rubble*, *Vanilla Vehicles Expanded*).

**Destroy-only (has `killedLeavings`):**

| defName | mod | size | yields when destroyed |
|---|---|---|---|
| `AM_AncientPipelineSection` | Ancient urban ruins | 2x1 | ChunkSlagSteel x6 |
| `AncientChemfuelCanister` | Odyssey | 1x1 | Filth_Fuel x1 |
| `AncientChemtruck` | Odyssey | 2x4 | ChunkSlagSteel x2 |
| `AncientDisplayBank` | Core | 3x1 | ChunkSlagSteel x2 |
| `AncientDrillPlatform` | Odyssey | 3x3 | ChunkSlagSteel x3 |
| `AncientEquipmentBlocks` | Core | 4x2 | ChunkSlagSteel x2 |
| `AncientExcavator` | Odyssey | 3x4 | ChunkSlagSteel x4 |
| `AncientExostriderRemains` | Biotech | 3x2 | ChunkSlagSteel x6, MechanoidTransponder x1 |
| `AncientForklift` | Odyssey | 2x4 | ChunkSlagSteel x3 |
| `AncientIndustrialTruck` | Odyssey | 2x4 | ChunkSlagSteel x3 |
| `AncientLargeContainer` | Core | 3x5 | ChunkSlagSteel x3 |
| `AncientMediumContainer` | Odyssey | 2x4 | ChunkSlagSteel x2 |
| `AncientOpenContainer` | Odyssey | 4x2 | ChunkSlagSteel x2 |
| `AncientSmallContainer` | Odyssey | 2x2 | ChunkSlagSteel x1 |
| `AncientSystemRack` | Core | 1x3 | ChunkSlagSteel x1 |
| `AncientTunnelerClaw` | Odyssey | 2x1 | ChunkSlagSteel x1 |
| `AncientTunnelerHusk` | Odyssey | 2x2 | ChunkSlagSteel x2 |
| `AncientWindTurbineBody` | Odyssey | 5x2 | ChunkSlagSteel x2 |
| `RG_AncientRustedHog` | ReGrowth 2 | 3x5 | ChunkSlagSteel x2 |
| `VFEPD_AncientSmallContainer` | Vanilla Furniture Expanded - Props and Decor | 2x2 | ChunkSlagSteel x1 |
| `VFEP_CrashedShip_Black` | Vanilla Factions Expanded - Pirates | 5x3 | Steel x120, ComponentIndustrial x6, ChunkSlagSteel x4 |
| `VFEP_CrashedShip_Green` | Vanilla Factions Expanded - Pirates | 5x3 | Steel x120, ComponentIndustrial x6, ChunkSlagSteel x4 |
| `VFEP_CrashedShip_Orange` | Vanilla Factions Expanded - Pirates | 5x3 | Steel x120, ComponentIndustrial x6, ChunkSlagSteel x4 |
| `VFEP_CrashedShip_Red` | Vanilla Factions Expanded - Pirates | 5x3 | Steel x120, ComponentIndustrial x6, ChunkSlagSteel x4 |
| `VME_AncientRustedDropship` | Vanilla Ideology Expanded - Memes and Structures | 6x5 | ChunkSlagSteel x4 |
| `VQE_GenetronJunk` | Vanilla Quests Expanded - The Generator | 1x1 | ChunkSlagSteel x2 |

**Returns nothing either way — first 40 of 635:** `AB_AncientBone`, `AB_AncientBrokenBone`, `AB_AncientGallatrossSkull`, `AB_AncientVerticalBone`, `AB_DerelictArchonexusCore`, `AB_DerelictArchotechTower`, `AB_DerelictBeachUmbrella`, `AB_DerelictMajorArchotechStructure`, `AB_DerelictPoolLadder`, `AB_DerelictRecliner`, `AB_DerelictSwimmingPool`, `AB_Mech_RuinedMortar_Full`, `AB_Mech_RuinedMortar_Single`, `AB_Mech_RuinedShield`, `AB_Mech_RuinedTurret_Full`, `AB_Mech_RuinedTurret_Single`, `AB_RustedWall`, `AG_AncientCorpse`, `AG_AncientShelf`, `AG_RaidSpawner`, `AG_RustedWall`, `AM_AVendingMachine`, `AM_AncientATM`, `AM_AncientAirConditioner`, `AM_AncientBarrel`, `AM_AncientBed`, `AM_AncientCashRegister`, `AM_AncientContainer`, `AM_AncientCrate`, `AM_AncientDisplayBank`, `AM_AncientDoubleBed`, `AM_AncientEquipmentBlocks`, `AM_AncientFence`, `AM_AncientFuelNode`, `AM_AncientGenerator`, `AM_AncientHydrant`, `AM_AncientKitchenSink`, `AM_AncientLockerBank`, `AM_AncientMachine`, `AM_AncientMicrowave`


---

## 4. Does it read as BROKEN at sprite scale?

🔴 **This cannot be answered offline for the vanilla kit, and that is a finding rather than a gap.** `Data/*/Textures` **does not exist for any DLC** — Core, Royalty, Ideology, Biotech, Anomaly and Odyssey all pack their art into `AssetBundles`. Zero loose PNGs ship with the base game.

- **679** usable wreck defs have a loose PNG on disk (workshop mods) and CAN be rendered offline.
- **297** are packed and cannot. For those the routes are a Unity bundle extraction, or an in-game screenshot over the live bridge — which is cheap and needs no reload.

**Free proxy in the meantime: footprint.** A prop's smallest on-screen dimension at ordinary play zoom is `min(size) x 22 px`. Below ~44 px the silhouette is carrying the entire read and interior detail is wasted (as per the trap file). Usable defs at or below that threshold:

- **784 of 976** usable defs are 1x1 or 2x wide, i.e. **44 px or less** on screen. Place these in CLUSTERS, never singly — one 22 px prop is noise, nine are a debris field.

**The props big enough to read on their own** (>= 3 cells on the short side, so >= 66 px at play zoom) — these are the ones that carry a wreck:

| defName | mod | size | px at play zoom | bucket |
|---|---|---|---|---|
| `AB_DerelictArchonexusCore` | Alpha Biomes | 11x11 | 242 | USABLE-EMPTY |
| `VFEPD_AB_DerelictArchonexusCore` | Vanilla Furniture Expanded - Props and Decor | 11x11 | 242 | USABLE-EMPTY |
| `BreadMoAM_AncientGiantRockExcavator` | Ancient mining industry | 9x9 | 198 | USABLE-YIELDS |
| `VFEPD_AncientGiantRockExcavator` | Vanilla Furniture Expanded - Props and Decor | 9x9 | 198 | USABLE-EMPTY |
| `AB_DerelictMajorArchotechStructure` | Alpha Biomes | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AB_AncientFreezingVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AB_AncientGreyPallVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AB_AncientBloodRainVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AB_AncientDeathPallVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AB_DerelictMajorArchotechStructure` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_CerebrexCore_Destroyed` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AncientSmokeVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AncientToxVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_AncientHeatVent` | Vanilla Furniture Expanded - Props and Decor | 7x7 | 154 | USABLE-EMPTY |
| `VFEPD_RuinedArchotechPlatform` | Vanilla Furniture Expanded - Props and Decor | 7x6 | 132 | USABLE-EMPTY |
| `VFEPD_RuinedHexagelPlant` | Vanilla Furniture Expanded - Props and Decor | 6x6 | 132 | USABLE-EMPTY |
| `VFEPD_AncientGeothermalPlant` | Vanilla Furniture Expanded - Props and Decor | 6x6 | 132 | USABLE-EMPTY |
| `VQE_AncientARCPrototype_One` | Vanilla Quests Expanded - The Generator | 6x6 | 132 | USABLE-YIELDS |
| `VQE_AncientARCPrototype_Two` | Vanilla Quests Expanded - The Generator | 6x6 | 132 | USABLE-YIELDS |
| `VQE_AncientARCPrototype_Three` | Vanilla Quests Expanded - The Generator | 6x6 | 132 | USABLE-YIELDS |
| `VQE_AncientGenetron` | Vanilla Quests Expanded - The Generator | 6x6 | 132 | USABLE-YIELDS |
| `VQE_AncientGeothermalGenetron` | Vanilla Quests Expanded - The Generator | 6x6 | 132 | USABLE-YIELDS |
| `VQE_AncientOvergrownGenetron` | Vanilla Quests Expanded - The Generator | 6x6 | 132 | USABLE-YIELDS |
| `GR_RuinedArchotechPlatform` | Vanilla Genetics Expanded | 7x6 | 132 | USABLE-YIELDS |
| `GR_RuinedHexagelPlant` | Vanilla Genetics Expanded | 6x6 | 132 | USABLE-YIELDS |
