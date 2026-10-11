# FLOWWORKS_QUARRY_DIGGING_1 — River half (sluice box + panning), 2026-10-11

FOUNDRY. Design: `design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md` §2b–2c, 2f.
FlowWorks half (canal-dig finds) was built at c858125a8; this pass builds the river half.

## Scope
Sluice box + panning spot/Mining job in FlowWorks Rivers, sharing one river stock, with Mod Settings and a
first-script chain. Not deployed; no bridge used.

## Built
- `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerMath.cs` — Verse-free numbers (stock cap 2%, yearly regrowth,
  sluice 1.2/day x lane x river size, panning 12.5% hit x skill factor 0.4–1.6, 1–3 units, session 5000 ticks / MiningSpeed).
  Selftest case `Placer_stock_sluice_pan` (FlowWorks SelfTest, 140/140).
- `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerWorks.cs` — `RM_PlacerPoolDef`, `RM_PlacerDraw` (THE swap point),
  `RM_MapComponent_PlacerStock` (one stock per map, regrows, flood refill on flood onset), `RM_Building_SluiceBox`,
  `RM_PlaceWorker_SluiceBox` (1×2: one cell shallow moving river, one Light bank), `RM_PlaceWorker_PanningSpot`
  (dry bank beside shallow moving water), `RM_WorkGiver_PanForPlacer` (Mining), `JobDriver_PanForPlacer`
  (stands on the spot, faces the water, learns Mining), `RM_PlacerProof.ProofReport` (static_call:
  ""/wash/refill/drain/pan/selfcheck).
- `src/RimMandrake/FlowWorks/Defs/Rivers/RM_PlacerWorks.xml` — `RM_PlacerPool_Vanilla` (Gold, Silver, Jade, Uranium;
  RimSage-verified mineableThings), `RM_SluiceBox`, `RM_PanningSpot`, `RM_PanForPlacerJob`, WorkGiverDef `RM_PanForPlacer` (workType Mining).
- `RM_QuarrySettings` filled: sluiceBoxEnabled, panningEnabled, placerFloodRefill, placerStockPercent,
  sluiceYieldMultiplier, panningYieldMultiplier (scribed into FlowWorks' one file; already drawn by the window).
- First script: `northstar/extensions_rivers.py` chain `placer` (3 components, one per toggle); site_spec table +
  count 102; `selftest_flowworks_rivers.py` covers the quarry settings.

## Provisional / owed
- **Pool is the map's own rock** (placer minerals in its resource rock), not the registry's rivers-carry column — that
  column's numbers are unapproved (mineral_numbers_review sheet) and the registry mod (MINERALS_WHERE_THEY_BELONG_1
  R2–R5) is unbuilt. Swap `RM_PlacerDraw.Pool/PlacerUnits` when it lands. Until then gold only where hills hold gold.
- **One stock per map**, not per water body (simplification; noted in the class doc).
- **Art is placeholder**: sluice box borrows `RM_BankWeir`, panning spot vanilla `MeditationSpot`. Commission via art ledger.
- All numbers PROVISIONAL.

## Live proof rows (bridge, river quicktest map, after deploy)
- L1: `RM_SluiceBox`, `RM_PanningSpot`, `RM_PanForPlacerJob`, `RM_PanForPlacer`, `RM_PlacerPool_Vanilla` resolve; no config errors.
- L2: `RM_PlacerProof selfcheck` → got>0, drawMatches=True, inPool=True, off=sluice=off, pan=pan=*.
- L2: drain then refill → stock == cap.
- L2: a colonist with Mining enabled takes a panning job at a spot and stays on the bank cell the whole session.
