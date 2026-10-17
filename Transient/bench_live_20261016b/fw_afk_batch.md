# FlowWorks AFK batch, 2026-10-16/17 (BENCH helper, owner AFK), ratchet_pilot tier, review map RM_FW_walk_20261016, DLL 31f335066b

Method: paused `step_game_ticks`, state reads only (excavation_rect, flowworks_body_report, engine_state, static_call). Scripts: `Transient/bench_live_20261016b/{s11,s8b,s9*,s1e,s12b,mc,door,lac}.py`, helper `afk_lib.py`.
Pawn safety each run: `fix_afk.py` (pit hediffs cleared, superdeep pawns moved 3 out, drafted), `feed()` after the colony starved (GovernorStop) and a hive (GlowPod/Hive at 200,144) was destroyed after a GovernorStop threat_structure.
Setup faults hit and fixed (HARNESS, mine): `companion_profile.json` expired 23:00Z so `jawa/static_call` was REFUSED as CAMPAIGN; renewed +3 h, same keys (backup `companion_profile.before.json`). A plain `load_game` over a live game kills the game (teardown NRE, Steam/keepalive relaunched it on RM_TestSite_calm_v1); loads go through `go_to_main_menu` first (`loadwalk.py`).
All settings I touched are restored and read back (refillRateMultiplier 1, slimeSlipEnabled True, edgeSinksEnabled True, weather Clear). Final state: RM_FW_walk_20261016 reloaded (tick 14011), 462 labels, station 1 framed, paused. Any pawn undrafted there is as the save holds it.

## 1. Station 11 canyon flood - PASS (state), eyes owed for "runs"
`RM_BiomeMapControls.FireFloodTrigger("74,214|false")` -> `OK flooding 14 cells from (74,0,214) until tick 31909`. Report: reach=14, raisedFillCells=14, activeFloodCells=0, phase Flooding, still Flooding after 1000 ticks (6 reads at +0/10/60/250/500/1000). Wet cells 14 at +0, x 75..88, vol 28 (full). Nothing wet outside the station: 100x70 window around it read 127 wet cells before and after (other stations, unchanged).
Observation: the canal is raised all 14 cells at once at the press, not seen entering west and running east; the end state is "whole canal, nowhere else". The progressive look is the owner's.

## 2. Stations 8 / 9
- Station 8 (refill waits): no muffalo exists on the loaded map (calm sweep), so SITE; spawned one at (206,234). Rain alone at refillRateMultiplier 1 refilled nothing in 2500 ticks (rate = 0.13 x cells x (1+3 x rain) per DAY: ~1.5 units/day for this pond). Compressed (multiplier 500, restored): with the muffalo held on (206,234) 600 ticks and then free, (206,235) refilled at +1100 while the muffalo still stood on (206,234); (206,234) stayed Lakebed_Deep until the muffalo left (+1350) and was water at +1600; all 4 cells water by +1850. PASS: never over the occupant, refills after it leaves. Side effect: the 500x multiplier also filled station 9's pond, so I reloaded.
- Station 9 (fill-in sends water home): SITE FAULT. The far-end fill-in cells x 240..242 are within `NoBuildEdgeWidth` (10) of the east map edge (x>=240), so `IsSinkCell` is true: the pond pays out off-map (sinkTransferredTotal 98 -> 133, pond stock 20.1 -> 0.3) before any fill happens. Re-run with `edgeSinksEnabled` OFF (restored): pond+canal stays conserved (3.23+17 -> 2.24+18, overflowDestroyed 0, sink 0); with Mining skill raised (a skill-2 colonist needs >8000 ticks for 3200 work) cell (242,234) went d 2 -> 1 and the displaced water stayed in the canal (neighbours), the pond did NOT gain. So "that water runs back into the pond" is NOT shown: UNMEASURED/SITE (station 9 must move west of x=240 and the pond must have headroom); conservation itself PASS.

## 3. Station 1 drain - PASS
Save loaded at tick 14011; lower canal z=233 (62 dug) wet 26-27 cells, standing 1,1,0,0 puddle pairs, flat for 6000 ticks while its limited pond (x62, stock 4.9 of 72) paid 1 level per 500 ticks. Pond ran dry mid-series (stock 0.02 after the 1 level per 500 ticks run-out); the wet front then retreated 1 cell per 250 ticks (x 40 -> 9) and the lower canal reached 0 wet at t=53791 (series started at tick 30361 after the reload to 14011 and a station 9 detour). Upper canal z=237 held 7 wet cells throughout. Series in the run output (`s1e.py`).
Note: the lower canal does not read "stays empty" while its pond has stock; it drains to 0 only after the pond is spent. Stripes 0 per L7 earlier today.

## 4. Station 12 slime - state only (visual verdicts stay with the owner)
Pawns placed by me (the map's own two colonists were absent). `RM_SlimeSlip.ProofReport` counts, `jawa/order_pawn`:
1. Bank colonist ordered to the north bank: walked round the canal's east end (x range 104..112), 0 sampled cells in the slime canal, 0 slips. PASS.
2. Ordered onto a slime cell: stalled at the first slime cell for 900 ticks, 3 slips. PASS.
3. Colonist teleported mid-canal and ordered to the south bank: 900 ticks to get out (18 of 30 samples in slime), slips 3, climbSlips 0. The "Slid back" climb-out count (card) read 0 here; an earlier unclean run read climbSlips 4 once. UNMEASURED/HARNESS (teleport start, forced order, not the undrafted climb the card describes).
4. Natural slime pool (107..111,218..220): ordered in, slips 1, climbSlips 0. PASS.
5. slimeSlipEnabled OFF: wade slips 0 (9 slime samples), natural slips 0. PASS.
Slip text motes: not readable by state; owner.

## 5. B rows
- L5 (`liquid_checks.py --only L5`, current map, no fresh map): `L5_switched_off_hose_spills` PASS MOD (held 10000 -> 0, drained 10000, filth thickness [1,4], expected pieces 3). `L5_colonists_clean_spill` UNMEASURED SITE (cleaner Human46618 did not clean the filth in 3000 ticks, filth 4 -> 4). Result `src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T173458.json`.
- Map controls (`RM_MapControls.PlaceSource/PlaceSink` on station 11's dry canal, 3000 ticks): source (75,214) level 1/pulse; wet front +1 cell per pulse; sink at (88,214) drained from pulse 14; poured - drained = held volume (20 - 7 = 13) every read, overflowDestroyed 0. PASS for level moves and conservation. UNMEASURED: L0 ledger `flowSources/flowSinks`, save/reload survival.
- Door facing (`RimWorld.DoorUtility.DoorRotationAt(x,z|0|false)`): sluice on E-W canal (80,214) 1 (East), grate E-W (84,214) 1; sluice N-S (85,216) 0, grate N-S (85,217) 0; plain ground control 0. Built doors turn with the canal axis. UNMEASURED: blueprint, superdeep canal, drawn art (owner).
- Lacquer bill: debug action `Lacquer bill: round trip at cell`: recipeFound, workerOk, coats 0 -> 1, same item, hp/quality kept, deepfire destroyed, recipe cost 3 = job cost 3. PASS. UNMEASURED (needs a selected colonist / UI): right-click options, unpowered disabled reason. Note: the `lacquer_bill` chain is in `src/RimMandrake/LuminousPigment/validation.py`, not FlowWorks, so the run-sheet's "no lacquer_bill chain" is wrong.
- Litres rows: no deterministic read surface for mouseover litres or a barrel fill (the bottle loop LIQUID_BOTTLE_LOOP_1 is blocked); validation_v2 litres rows already PASS earlier today. UNMEASURED here.

## Classification of non-PASS
SITE: station 8 has no muffalo; station 9 far end inside the edge-sink strip (fix: move the station west of x=240); L5 clean-up cleaner idle. HARNESS: expired companion profile; slime climb-out start by teleport; run-sheet claim about lacquer chain. MOD: none found in this batch.
