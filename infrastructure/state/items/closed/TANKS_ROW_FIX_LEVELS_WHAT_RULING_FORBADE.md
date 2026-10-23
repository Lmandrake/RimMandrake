## spec
found-by: BENCH bridge run (2026-10-23, run 1, walk_gaps_proof.py on d945b7bb5e, 14-mod fw_gss_sitting).
Class: HARNESS (wrong premise), not MOD.

`northstar/walk_gaps_proof.py` row `TANKS_JOINED_ONE_LEVEL` (scene D: RM_LiquidTank, RM_LiquidTankTall,
RM_UniversalCargoTank on one pipe, filled 10/40/80 %, Store mode, gap piped, 2500 ticks) EXPECTS the fill fractions to
converge. Live: fractions 0.1/0.4/0.8 before and after, total conserved 400000, net reaches all three, settles 0/0
(evidence `Transient/bridge_run_1_20261023/walk_gaps_result.json`, log `walk_gaps.log`).

That is the RULED behaviour: "Storage fill stays pump-only" (GSS ruling 3; item PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL
spec; design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md:174; RM_LiquidNetKernel.cs:788 "Store tanks only
buffer"); the walk premise was corrected 2026-10-22 evening (Transient/pile_2026-10-22/walk_tonight.md:117).

Fix: invert the row — joined Store tanks HOLD their units (a can-fail: any move is a MOD FAIL), rename it e.g.
TANKS_JOINED_STORE_HOLD; mock fault `store_only` becomes the PASS case; add a can-fail control (a Dump tank or a pump on
the same net moves units) so a dead net read cannot pass. Rerun on the next sitting's walk_gaps.
