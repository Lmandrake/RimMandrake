# FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES

Owner ruling 2026-10-11 #4: *"Our tanks should go where other storage tanks go. Our pipes/hoses/wires/conduit should go
where those normally go. Only ask me this if there is ambiguity."*

## evidence (workshop defs read 2026-10-11)
- Vanilla: no liquid pipes or tanks.
- Vanilla Chemfuel Expanded (2792917473), Vanilla Helixien Gas Expanded (2877699803), Vanilla Nutrient Paste Expanded
  (2920385763): pipes, valves AND tanks (PS_ChemfuelTank, VNPE_NutrientPasteVat) all in `VCHE_PipeNetworks`
  ("pipe networks"), a DesignationCategoryDef each of them ships identically.
- Dubs Bad Hygiene: its plumbing and water tanks in its own `Hygiene` tab (water/sewage only).
- Alpha Biomes propane pipe: `Furniture` (outlier). Rimefeller: its own `Rimefeller` tab.

## done (830f2c8d0)
FlowWorks ships the same `VCHE_PipeNetworks` def (`Defs/Machinery/RM_PipeNetworksTab.xml`); `RM_UniversalPipe`,
`RM_LiquidTank`, `RM_UniversalCargoTank`, `RM_HoseReel` and both pipe adapters moved there; pumps, stills, works stay in
Production. Pinned by SelfTest case `BuildMenu_pipes_and_tanks_in_the_pipe_networks_tab`.

## open question (card-ready)
DBH puts water tanks in Hygiene; VE puts every tank in "pipe networks". Default taken: pipe networks for all FlowWorks
tanks (they hold any liquid). Ask only if he wants water-only tanks beside DBH's.

## criteria
- A1 L0: SelfTest case `BuildMenu_pipes_and_tanks_in_the_pipe_networks_tab` ok (830f2c8d0).
- A2 L2: in game, the "pipe networks" tab lists universal pipe, liquid tank, universal cargo tank, hose reel (and the adapters with VCHE / Alpha Biomes); no duplicate-def error for VCHE_PipeNetworks in Player.log with a VE pipe mod loaded.
