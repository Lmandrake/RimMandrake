# Pond-chain code review — BENCH night helper, 2026-10-13

Scope: FlowWorks files changed by a9ecaad78dcb, cd10284be668, 51ef726e1653. Offline only.

| file | lines | findings | state |
|---|---|---|---|
| Source/RM_Volume.cs | 90 | none | CLEAN |
| Source/FluidDef.cs | 225 | none (field deletion complete; no XML in src/ still sets it) | CLEAN |
| Source/LiquidTypes/Building_LiquidTank.cs | 187 | doc comment of the tank sat on RM_LiquidTankExtension (moved); overfull tank handled by every plan (Take/FillOrder skip room <= 0) | fixed, CLEAN |
| Source/RM_LiquidBody.cs | 115 | none | CLEAN |
| Source/RM_LiquidStock.cs | 843 | F2 lives in RM_StockMath (caller unchanged) | CLEAN |
| Source/RM_StockMath.cs | 615 | F2 fixed here; only the pond-chain functions were reviewed, not the whole file | fixed, DIRTY |
| Source/RM_PumpMath.cs | 146 | none | CLEAN |
| Source/RM_MapComponent_Excavation.cs | 1903 | F1 | fixed, CLEAN |
| Source/RimMandrakeFlowWorksMod.cs | 1323 | diff only: 3 new toggles default on, scribed, in the section's reset list; labels correct | DIRTY (whole file not read) |
| Source/Debug/FlowWorksDebugActions.cs | 147 | none | CLEAN |
| Source/LiquidTypes/Building_LiquidPump.cs | 563 | none (pond draw/return both 1 level = vpt fill-units = 5 tank units; undo is a whole level) | CLEAN |
| Source/Machinery/RM_LiquidNet.cs | 1057 | diff only (OutletLeg / WholeLevels swap): correct, DumpTake gives exactly one level for Body | DIRTY (whole file not read) |
| Source/Machinery/RM_LiquidSpill.cs | 184 | none | CLEAN |
| python (northstar/*, validation.py, selftest_hose_port.py) | ~9000 | diffs only: fakegame bed rule matches vanilla deep names; counts updated | DIRTY (not read whole) |

## Findings

- **F1 (L0 ledger double count).** `TryTakeLevel` (pump draw from a channel) went through `BurnOffLevel`, which since
  cd10284 also adds to `burnedLevelsTotal`. Every pumped level then showed in the tank AND as a "burned" exit, so the
  L0 before/after row could not balance. Fixed: shared `TakeLevelCore`; only `BurnOffLevel` counts the exit.
  Selftest `Pond_truncated_index_persists_and_ledger_probe_exists` (failed before, passes after).
- **F2 (pond dies at capacity 0).** `CapacityWithoutBed` on the LAST bed square (bed == bedSum) set capacity 0, and
  `CapacityWithBed(0, bed, 0)` cannot invert it: a one-square seep (or a fully dried pond dug out square by square) came
  back from fill-in with capacity 0 and never refilled or re-wetted. Fixed: the last square keeps the capacity (any
  stock stays with the pond, so nothing is destroyed). Selftest `Pond_dug_bed_leaves_and_returns_exactly` (failed
  before, passes after).
- Checked and fine: volume-model migration (new maps start at 2, absent key loads 1, runs once before RebuildBedGrid,
  fraction kept, limitless untouched); tanks keep units and refuse input when overfull; bedGrid set/cleared at every
  writer; detach/reattach bed reads are symmetric (both read the recorded water terrain); return leg conserves (CanReturn
  then CreditLevels, whole level, fluid checked); per-pulse cost only (no tick-path work added); new settings default on.

Selftests: flowworks_stock 292/292, conservation 13/13, run_selftests GREEN (325 pass, 0 fail).
