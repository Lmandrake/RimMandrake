# GSS Ralph: where the last pass got to

Pass 17. Offline the whole pass. **Deploy refused** (`steve.sh deploy`: "FlowWorks holds game A, which loads this DLL too"), so `ralph/NEED_GAME_A` and `ralph/NEED_GAME` are set. **Deployed on Steve = still 249698eeec.** Everything since (pass 16's fairing, the heap spill 493e472932, this pass) is built and committed, never seen in game.

## What this pass did
1. **Self-tests green: 1178/1178** (aerial 166/166, offline validation 9/9).
   - `sustained change` (sliced lay != one plain Build): `ArriveClear` compared machines by reference. A graph reduced from an earlier copy of the world holds that copy's `MachineInfo`s, so the sliced lay treated a lamp's own cell as another machine's and laid its cord round it. Now compared by footprint. Live this could also happen (worker graph adoption), so it is a real fix, not a test fix.
   - `cord-shape: 24 folds`: every one was a heap cable (the pile scene; the open room had 0). Fixed by the new heap lay below: 0 folds in 131 strands.
2. **Heaps re-laid (`HeapWalk` in CordBuilder.cs, GSS only via `FairBends`).** The old cable was a Catmull spline through 2-4 random points, which folded wherever two points lay one behind the other, drew straight strokes corner to corner, and filled the block's square. Now each cable:
   - leaves its plug by `HeapEscape`: straight or an arc at >= 0.72 cell to a roomy spot headed back into the heap; only when nothing fits, a plug bend as tight as 0.3 within 0.45 cell (the socket's forced bend);
   - runs stop to stop (3-5 roomy stops) along Dubins paths at radius 0.72-1.25. Each straight part is bowed by a sin^3 wave, flat and unbent at its ends and never tighter than a 2-cell radius. It sometimes throws a whole coil (r 0.48-0.62, a loop by the bar's own rule);
   - stays on a lumpy round ground: the heap's ground cells (plus the first cell of a conduit arm leaving it) within a per-cell reach of 0.95-1.4 from its conduit cells, or round a port's lead.
   - By construction it never turns more than ~80 deg in a cell outside a coil or a plug bend. Misses fall back to the old spline (3 cables in the self-test's 50 heap builds).
   - Lab look: `D:\ClaudeWork\rimmandrake\ralph_gss\p17\lab_heaps_walk_Scrapper_Modern.png` (before: `lab_heap_Scrapper_before_p16.png`): a dense mass of curves and coils, a round lumpy outline, far fewer straight strokes. **This changes a look the owner approved: before/after at play zoom in game is owed.**
   - Heap pieces are now cached (`TangleKey`: cells, seed, look, live, every cell 2 round). Before, a heap was re-laid on every Build, and with the walk that took a reused Build to 16.7 ms on the Scrapper colony. Now it is 0.6 ms.
3. `--shape-diag` (selftest_gimmesomeslack.py) prints FOLD rows, SLICE differences, HEAPWALK misses, Build TIME on the lab worlds, and writes `heapwalk_trace.json` into the selftest cwd. Draw it with `ralph/live/heapwalk_plot.py`.

## Lab count of unforced sharp bends (never_taut_straight_cord, played colonies, no furniture)
Modern 17, Scrapper 26, Industrial 26, Futuristic 24 (pass 16: 27/42/42/41). Heaps are now 0-3 per look. **What is left is short cords: chord under 3 cells, 10-18 per look** (`Transient/lab/p17/h4`, sheet `p17\lab_unforced_Futuristic.png`): a junction box 1-3 cells from its machine, battery or wall plate, a "<" mid-cord or a hook at the plug. Also 1 per look of `coil:` (the spur coil at a junction, `CordLayer.Loop` radius 0.22, CordBuilder ~line 650: make it 0.5 under FairBends) and 2-5 on mid-length cords.

## Do next, in order
1. **Short hops laid whole** (offline). `EndPose` is already split out of `AttachEnd` (same behaviour, self-tests green). Plan: in LayEdge, for n == 1, no cut end, chord under ~3, not a strip socket with a swing, lay the cord from A's fitting pose (`target - arrive*straight`, heading `-arrive`) to B's along two Dubins legs (radius >= 0.68) through a mid pose bowed 0.2-0.8 cell to one side for slack (length >= 1.15 x chord). For a one-cell machine without a home, try all four sides as AttachEnd does. Check every point clear (ArriveClear rules, both ends), keep the least-turning candidate, skip slack/loops/AttachEnd/Unfold/Fair, keep IntoArt/PastFace. Fall back to the old lay. Then the spur coil. Target: lab 0 unforced in all four looks.
2. When the game is free: `steve.sh deploy`, `up`, probe `bends` on each `gss_ba_<Look>` save (four numbers), then `p12_look.py p17 --frames drop,span,dense --tiles`: the lamp, the heap and the mast foot in every look (the ratchet's 12 shots), plus the heap before/after (p15 `z_sdense.png` is before).
3. Braiding (owner asked): heaps first. A pair of heap cables can share a stretch: the second follows the first's path with offsets of opposite sign, ±0.035·sin(2πs/0.7), only where the path turns under 50 deg a cell, so the bar stays clean. Then side-by-side runs.
4. Then RATCHET 7-8: bedroom_reno.py, proof core, GPT leads 4 and 7, a broaden call.

## Steve this pass
`status` once: game b stopped, `bad_cpus=[2]`. No game run. Deploy refused, because game A is held by FlowWorks. No dead game, no dropped ssh, no reboot.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true (on 249698eeec; the new lay is unseen, so recheck the slack census once deployed)
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true on the deployed build; the new heap (walked cables) is unseen in game
- break_live_and_dead_ends_differ: true (cut ends deliberately left on the old lay and approach)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (lab unforced 17/26/26/24; the bar wants 0 in game)
- never_cord_across_impassable: true
