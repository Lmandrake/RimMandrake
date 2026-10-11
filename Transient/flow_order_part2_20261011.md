# FLOW_ORDER_EXTERNAL_INPUT_1 part 2 — networks over the component cap (2026-10-11)

## Problem
`RM_FlowKernel.maxComponentCells` (6000) splits a bigger connected network into capped partitions. Seeds are
sorted, so the seams fell on the same cells every pulse and liquid never crossed them (GPT review #11).

## Design
Engineering call recorded in `Transient/backlog_big_questions_20261009.md` ("raise the cap behind the setting
after one in-game timing"). Built the offline half:
- Moving seams (`networkSeamsMoveEnabled`, default on): when a capped walk hits the cap, the kernel walks the
  whole network once, computes ONE network-wide flow order (sources, driver inputs, sinks), then resolves capped
  partitions whose first start cell is `sorted[(pulse % n) * 7919 % n]`; the rest follow in cell-index order.
  Each partition keeps its own balanced ledger; the order is static per pulse and identical whichever way the
  seams fall (FLOWWORKS_CHANNEL_OSCILLATION_1). A per-partition order failed: an off-source partition saw every
  key equal and never spread (49/200, same as fixed seams).
- Cap is a slider (`maxNetworkCells`, 1000–50000, step 500, default 6000 = shipped). Raising the default is owed
  to the live timing.
- Networks within the cap take the old path untouched (control: pulse-for-pulse identical, 0 rotations).

## Build
`RM_FlowKernel.cs` (ResolveRotatedNetwork, ResolveComponent networkOrder), `RM_MapComponent_Excavation.cs`
(adapter sets both each pulse), `RimMandrakeFlowWorksMod.cs` (setting, Scribe, screen), `northstar/site_spec.py`
+ toggle count 99. winbuild FlowWorks: 0 errors.

## Proof
SelfTest 139/139 (staged on D:). Case `FLOW_ORDER_EXTERNAL_INPUT_1_part2_oversized_network_exchanges_across_seams`:
200-cell channel cap 50 — fixed seams 49/200 wet (control bites), moving 200/200 after 3000 pulses, settled,
ledger balanced; after 400 pulses moving 136 vs one uncapped piece 200 (moving seams are slower).

## Owed live
- L-live: pulse cost on a >6000-cell network in game; decides whether the default cap rises.
- L-live: a real oversized network wets end to end in game.
