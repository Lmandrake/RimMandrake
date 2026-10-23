# PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES

## Ask

Owner, 2026-10-23 (walking): "We should unfortunately regen the pumps and such to have connectors that match the more
modern pipe and hose sizes. looks a bit silly." Follows PIPE_GIRTH_TUNE_HALF_AS_THICK and HOSE_GIRTH_TUNE_MUCH_THINNER.

## Current girths (cells)

- ground pipe 0.136 (RM_PipePoleMath.cs, atlas 18 of 132 displayed px)
- hose 0.18 flat / 0.23 plump (HoseMath.FlatVisible, PlumpExtra); hose coupling widest ~0.22 at a pump
  (FittingSize 0.4376 x CouplingMax 0.508), x1.5 at tank/machine ports
- hose under-coupler (C#, beneath the fixture): collar 0.3125, pipe 0.219 (UnderCouplerGeometry.cs)

## Inventory (BENCH, 2026-10-23; measured from alpha spans unless marked "est." = read off a quarter-cell grid)

| texture | look | connector width | vs line | verdict |
|---|---|---|---|---|
| RM_LiquidPump (4 hose side ports) | Scrapper/Industrial/Futuristic | flange 0.29-0.31, neck 0.21-0.23 | hose 0.18 -> 1.7x; pipe 0.136 -> 1.6x | TOO BIG -> redrawn |
| RM_LiquidPump | Modern | same as above | same | too big; Modern helper owns it |
| RM_PipeFaucet | all 4 | neck ~0.125 (est.) | pipe 0.9x | OK |
| RM_SprinklerHead | all 4 | saddle opening ~0.15 (est.) | pipe 1.1x | OK |
| RM_LiquidTank W/E ports | Scrapper/Industrial/Futuristic | 0.17 / 0.20-0.23 / 0.15-0.19 | hose 0.9-1.3x | OK |
| Tall/Cargo/XTall tank fittings | non-Modern | 0.10-0.15 (est.) | hose <= 1x | OK |
| Hose reels (Reel_PumpHookup/Deployed, redrawn 2026-10-23) | all | outlet 0.10-0.13 (est.) | hose 0.6-0.7x | OK |
| RM_PumpingStation_Kludged | - | open flanged ends 0.43, pipe body 0.33 (est.) | pipe 3.2x | TOO BIG -> PUMP_STATION_REDRAW_PLUMBED_FOR_GIANTS |
| RM_PumpingStation_Repaired / _Wrecked | - | pipework ~0.30 (est.) | pipe 2.2x | TOO BIG -> same item |
| RM_DesalPlant / DetoxWorks / TarRefinery (x3 states) | - | piping 0.08-0.15 (est.) | pipe <= 1.1x | OK |
| RM_SunPanStill, RM_FueledStill, RM_DripFilter, RM_ReactionVat | - | no pipe/hose connector drawn (vat stubs ~0.12) | - | OK |
| RM_LiquidTap, RM_LiquidDrill | - | off the pipe net | - | n/a |
| RM_PipeAdapter_Chemfuel / _Propane | - | flange 0.56, coupling 0.37 (est.) | hose 2x | TOO BIG -> PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE |
| Joins UnderCollar / UnderPipe (code-sized) | all | 0.3125 / 0.219 | new pump neck 0.15 | TOO BIG -> UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK |

## Built

Pumps (Scrapper, Industrial, Futuristic): deterministic edit, same pixels
(`src/RimMandrake/FlowWorks/art_source/PumpPorts/shrink_ports.py`): each side port's neck+flange scaled about its axis
to neck 0.15 / flange 0.205 cell, flange face kept on the footprint edge, gap to the body bridged with the neck's own
textured run. Port points unchanged. Installed with art.py install --owner-said (replaced owner-kept art; old shas
2c8722d1192d / af8a6593eca6 / b1d7b737a792 are the revert). Art commit c10fa6c815, landed in 36a4c4e650.

UnderCouplerReach.cs NOT regenerated in the tree: publish's DLL rebuild picked up peers' uncommitted FlowWorks C#
(drawbridge/river/weir), so the regen + rebuild was backed out (a8b3274100 reverted in 37938c2a0c, table restored in 36a4c4e650).
Until the table is regenerated (`art_source/UnderCouplers/under_coupler_reach.py --write`, new pump reaches 0.295-0.299)
and the DLL rebuilt clean, `selftest_hose_fittings.py` reports 1 failure (reach table vs installed art). This goes with
UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK.

Gates (with the regenerated table in the worktree): validate_sprite PASS x3; selftest_hose_fittings /
selftest_hose_ports / selftest_tank_art_edges 0 failures; all 12 pump ports: gap to edge 0.04-0.07 cell (tolerance 0.10).
Art-eval pipeline run pump_ports_20261023_r2: HOLD_INPUT x3 (machine template needs an in-game assembled capture; no
game this session). GPT (gpt-6.1-sol) before/after look: connectors read matched, accept_with_polish.

Shadow sheet (not served): Transient/pump_ports_20261023/pump_ports_sheet_2026-10-23.html (pinned).

## Owed

- Live look (also what the pipeline's held assembled panel needs).
- Regenerate UnderCouplerReach.cs and rebuild the FlowWorks DLL clean (see above).

## Criteria

- A1 L1: in game, the Scrapper/Industrial/Futuristic pump ports read matched to the pipe and hose girth, every hose coupling meeting its port (live look)
