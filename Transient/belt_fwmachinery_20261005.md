# FlowWorks machinery build — 2026-10-05

Owner (verbatim): "Build the distillation and other associated machinery for liquids part of this mod. Build all flowworks components."

## Progress

## NEW ROWS NEEDED

## Art owed

## Blocked
- 1 registry: LiquidConversion gains process/inputUnits/outputUnits/productThing; generator LIQUID_CONVERSIONS emits 12 PROVISIONAL steps (salt, brine, boiling, icy, toxic, acid -> fresh; tar -> chemfuel)
- 2 C#: Source/Machinery/ (RM_LiquidNet hoses, RM_MachinerySettings, RM_ConversionMath, CompLiquidConverter, CompLiquidPipeAdapter, RM_LiquidWorksRuins); pump uses the net + RM_PumpExtension; tank RM_LiquidTankExtension
- 3 defs: Defs/Machinery/{RM_LiquidLogistics (hose, universal cargo tank), RM_LiquidStills (solar still, drip filter, fueled still), RM_IndustrialLiquidWorks (desal/detox/refinery x wrecked/kludged/repaired), RM_PumpingStation (3 tiers), RM_LiquidWorksScatter (4 GenStepDefs, shared scatterer)}; Patches/Machinery/{RM_LiquidWorksScatter_Register, RM_PipeNetAdapters (VCHE chemfuel, AB propane)}; WreckedMachines/Patches/WreckedMachines_DistillationModule.xml (3 tiers, FindMod FlowWorks)

## NEW ROWS NEEDED (for the FlowWorks walk / validation owner — this builder does not edit northstar/*.py)

site_spec SETTINGS owed (defaults as shipped): "liquidHosesEnabled": True, "converterRateMultiplier": 1.0,
"liquidWorksRuinsEnabled": True, "liquidWorksRuinStockEnabled": True, "industrialWorksBuildAnywhere": False,
"pipeAdaptersEnabled": True, plus the list "disabledLiquidMachines": [] (per-machine switches, keyed by
RM_MachineToggleExtension.key or defName: RM_SunPanStill, RM_DripFilter, RM_FueledStill, RM_DesalPlant,
RM_DetoxWorks, RM_TarRefinery, RM_PumpingStation, RM_WM_Distillation, RM_PipeAdapter_Chemfuel, RM_PipeAdapter_Propane).

### Hoses (RM_LiquidHose) — Phase 8 slice 2
- assert live: pump at a water channel, 6-cell hose run, RM_LiquidTank at the far end (not touching the pump) -> after 750 ticks the far tank holds RM_Liquid_FreshWater 15; cut one hose cell -> tank stops gaining. settings: liquidHosesEnabled off -> far tank gains nothing, a touching tank still fills.
### Universal cargo tank (RM_UniversalCargoTank)
- assert live: Capacity == 600 x tankCapacityMultiplier; fill 100 tar, uninstall (MinifiedThing), reinstall elsewhere -> still 100 tar; also pump (RM_LiquidPump) is now minifiable. settings: tankCapacityMultiplier.
### Converters (CompLiquidConverter) — the reusable kit
- sun-pan still (RM_SunPanStill; Stillsand ships the item-tray RM_SolarStill, a different machine): tank A salt water 50 + empty tank B touching it, open sky at noon, step 2500 ticks -> A down by 2n, B fresh n (n>0, 30 input/day); roofed or night -> no change, inspect "Needs open sky in daylight". Boiling water in A -> fresh 1:1. settings: disabledLiquidMachines RM_SunPanStill, converterRateMultiplier.
- drip filter: toxic water 30 in A -> fresh in B at 3:1; salt water in A -> refused (inspect "Cannot process salt water" + one RejectInput message). settings: RM_DripFilter.
- fueled still: no fuel -> "Out of fuel"; 40 wood -> brine 4:1, salt 2:1, toxic 3:1 to fresh; fuel falls ~12/day while working only. settings: RM_FueledStill.
- desal/detox/refinery repaired (powered): salt 3:2 / toxic 2:1 / acid 3:1 / brine 3:1 to fresh at 600/400 per day; refinery tar 4:1 -> chemfuel into a tank, or vanilla Chemfuel items beside it when no tank takes RM_Liquid_Chemfuel; kludged = half rate; unpowered -> nothing. settings: RM_DesalPlant/RM_DetoxWorks/RM_TarRefinery.
### Found works (LIQUID_INDUSTRY_SETPIECES_1)
- assert live: generate a map with RM_WaterBrineShallow/WaterOceanShallow present and EnvironmentalHazards loaded -> one RM_DesalPlant_Wrecked within 10 cells of it, plus RM_LiquidPump (25-60% HP) and RM_LiquidTank holding salt water or brine beside it (list things, not the placement log). Build menu: RM_DesalPlant_Kludged refuses placement except exactly over the wreck ("Must be raised over a wrecked desal plant"); built over it -> the wreck is replaced. settings: liquidWorksRuinsEnabled off -> no ruins on a new map; liquidWorksRuinStockEnabled off -> bare ruin; industrialWorksBuildAnywhere on -> placeable anywhere.
- pumping station repaired: draws 4 levels/cycle from water up to 4 cells off into every tank on its hose line. settings: RM_PumpingStation.
### Ship distillation module (WRECKED_DISTILLATION_MODULE_1, WreckedMachines patch, needs FlowWorks)
- assert live: RM_WM_Distillation_Kludged powered, tank A salt water + tank B -> fresh at 2:1, 60/day; Repaired 240/day; tank A tar -> nothing produced + "Cannot process tar" + one RejectInput message. Kludged builds over the wreck via replaceTags. settings: RM_WM_Distillation.
### Pipe-net adapters (VE PipeSystem; only with Vanilla Chemfuel Expanded / Alpha Biomes active)
- assert live: RM_PipeAdapter_Chemfuel on a VCHE chemfuel pipe with a PS_ChemfuelTank, plus a FlowWorks tank holding RM_Liquid_Chemfuel 50 touching it; feed mode -> PS tank gains, FlowWorks tank falls 10/rare tick; draw mode -> reverse. No reflection error in Player.log ("lacks AmountStored..."). settings: pipeAdaptersEnabled, RM_PipeAdapter_Chemfuel.

## Art owed (placeholders are vanilla; nothing queued — no decided concept exists for any of these)
RM_LiquidHose (atlas), RM_UniversalCargoTank (shares the scavenger tank render), RM_SunPanStill, RM_DripFilter,
RM_FueledStill, RM_DesalPlant x3 tiers, RM_DetoxWorks x3, RM_TarRefinery x3, RM_PumpingStation x3,
RM_WM_Distillation x3, RM_PipeAdapter_Chemfuel/Propane. RM_LiquidPump still borrows MoisturePump.

## Blocked
- Blood-bottle rot row (LIQUID_BOTTLE_LOOP_1): no FILL SOURCE for bottled blood is designed (item-only, no terrain, no extraction route), so a blood bottle could never exist in play — owner must say where bottled blood comes from; then it is one generator row + CompRottable + a household hemopack recipe.
- River items (sluice box + panning, levee flood check, order-stake breaks, ferry rope): taken by the RiverWorks->FlowWorks merge agent (coordinator, 2026-10-05).

- DONE: machinery 3e473f37c; docs+ledger b4ffc8db7 (pushed via plumbing merge e9626a29c). Closed: none (every verify bar is live). Blocked: blood rot (no fill source).
