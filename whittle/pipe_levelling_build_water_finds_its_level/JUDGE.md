# Judge: PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL (blind, 2026-11-12)

I read STATEMENT.md, NOTES.md and the item's criteria (`infrastructure/state/items/closed/PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL.md`, which holds the full text of the truncated lines). I looked at every evidence image I relied on and parsed the JSON files myself. I re-ran the offline selftest. I did not read DONE.md or BROADEN.md.
Scratch from my own run: `D:\ClaudeWork\rimmandrake\judge_levelling\` (selftest.txt, crops, flattened JSON).

## Per line

- **A1: true.** I ran `selftest_flowworks_stock.py --only 'LEVELLING_*'` myself on HEAD 210514fedb plus the working tree: **11/11 passed**, exit 0. The fuzz printed "300 scenes, 300 reached a fixed point". `LevellingChecks.cs` asserts the gates on every cycle of every scene, not only at the end (l.57-92): exact volume including the limitless net, energy never rising, the two-body gap never growing or changing sign, no link reversing, no liquid changing. There is one named case for each L1 item: 1-square vs 100-square basin, ten parallel links, same-body loop, siphon, exposed intake, water/oil, dry receiver, sea to brim. The recorded `A1_A2_selftest_LEVELLING.txt` agrees (17/17, including the outflow/hose-text cases). One caveat on provenance: I tested HEAD, not the named baa270b9e8+0ac23150a2. That makes my run stronger evidence, not weaker.
- **A2: true.** The budget case has exactly the stated shape: 200 bodies, 40 of them `Flat(40000, 8)`, 199+201 = 400 links, `maxLinks = 64` (l.232-260). It measured 82.8 us per cycle in my run and 80.5 us in the recorded file, against the statement's 89 us. Those are stopwatch numbers that vary from machine to machine, and all of them are well under budget. The design doc has `### Levelling feasibility` at l.19. It names the solver calls (`PondSurfaceHeight`, `SurfaceHeightOf`, `TryTakeDl`/`TryPourDl`) and the bounded transfer.
- **A3: true.** `A3_perf_timed_200_links_40000_basins.json` is live, mode=live:
  - mapSize 325x325, links 200/200, layFailures 0.
  - `A3_perf_phases.json` shows two basins of 125x320, each with cells=dug=filled=40000.
  - LEVELPERF: msAvg 6.63, msMax 51.9, 0.0265 ms per tick, allocKBAvg 330, 0 GCs.
  - The tick breakdown shows the first cycle after the topology change at 73 ms (46 ms of it resolving links). That is a real one-off hitch, and it was recorded honestly.

  The line only asks for the tick time and allocations to be recorded, and they were.
- **A4: true.** Three independent live rigs show the claim.
  - **walk_gaps PONDS_HOSE_LEVEL** (two 3x3 pits, equal floors, 360000 vs 90000 dL):
    - It ends at 225234 / 224766, and the total of 450000 is conserved.
    - The gap is 52 dL per square, about 0.26 cm at the game's 2000 L per metre per square. That is within 1 cm.
    - moves=18; `RM_Levelling.Moves` is the same counter HoseNetProbe exposes as `levelMoves` (HoseNetProbe.cs:117).
    - The reel's inspect read "Levelling: flowing (no pump; ...)" at tick 250 and "Levelling: level." at tick 4750.
  - **Rig M** (3x3 hole 3 m full vs 5x5 hole 1 m half full):
    - The total is 790000 -> 790000.
    - Surfaces finish at -0.365 and -0.369 m (I recomputed them from PITWATER dL).
    - The reel went flowing -> level at 2750. So the solver levels by surface, not by volume.
  - **Rig N** (a natural pond, 25 cells at 90%, vs a 3x3 pit in a 2 m hole):
    - Surfaces finish at -0.467 and -0.471 m.
    - The pond's loss (18.369) plus the control pond's refill drift (+0.150) equals the pit's gain (18.519) to the last digit.
  - **Images.** The panes show "flowing" and "level" on the live reel (`lev_a4_refilled_flowing_pane.png`, `lev_a4_relevelled_pane.png`).
  - **Refill, save/load and roles.** The refill re-levels (`A4_A5_look_ponds.json`). Save/reload mid-flow replays exactly, with the total conserved (`broaden_saveload_roles.json`). Role swaps level too, and capping stops the flow.
- **A5: true.** PONDS_DIFFERENT_LIQUIDS_NO_MIX: a water pit (360000 dL) and an oil pit (90000 dL), linked=True with both ends coupled. moves=0 and both dL are unchanged over 6 cycles. The receiver is the lower one, so a mixing bug would have shown as flow. Both reels read "Levelling: stopped, different liquids never mix." (`lev_a5_nomix_pane.png`, `lev_a5_nomix_outflow_pane.png`). The run JSON does not record the pit's fluid def, so I checked that it was oil and not the earlier chemfuel. The script at HEAD uses `RM_Fluid_Oil`. In `lev_a5_nomix_desktop.jpg`, cropped, the pit is dark brown with an oily sheen. That matches the oil fill colour (70,52,24) and not chemfuel's lighter amber (150,118,58).

## Staged or flattering

- **Calm site.** The live rigs are tidy best cases: storyteller off, threat scale 0, wildlife and hives removed, and the FlowWorks-tier mod list (12 mods) rather than the owner's full list. The A3 basins sat at the map edge with edge sinks switched off for the run.
- **Interpolated line on the A4 chart.** The walk_gaps trail keeps only the last 8 cycles (ticks 3000-4750). The left panel of `A4_A5_levels_over_time.png` draws a straight line from tick 0 to tick 3000, and that line is interpolation, not readings. Rigs M and N do have every 250-tick reading, and they fill the gap.
- **Stills.** The desktop stills cannot show motion or a few centimetres of level difference. The level claim rests on the dL readings, not on the pictures.
- **The main rig's pits.** It uses two equal-floor 3x3 pits. Rig M (different depth and area) and rig N (a natural pond) answer that.
- **What "a hose with two open ends" means here.** The rig is a reel, a universal pipe, then a reel: one network with an open end in each body. That is the design's definition of a link.

## Observed, outside the statement (not counted against it)

- **Uneven surface inside a pit while it flows.** During flow, each cycle's withdrawal and pour land on one cell. Rig M's per-pit surface spread reads up to 0.50 m mid-flow, against 0.0001 m once level. The builder's design doc lists this as risk 3. It did not show up visibly at the stills' zoom.
- **Readout right after a reload.** Just after the reload, both reels read "Free end: lying free ... checked on the next cycle" for one cycle.
- **Large basins are under-counted.** A3 walked about 80,000 squares a cycle. A 40,000-square basin is walked as capped runs of 20,000 (design risk 2: under-counting slows levelling, but it cannot overshoot).

would show: yes
