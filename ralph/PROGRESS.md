# GSS Ralph: where the last pass got to

Pass 16. Retired on the context gate, offline the whole pass (the game was not touched). **Deployed on Steve = still 249698eeec.** Everything below is committed, built in the lab, **not deployed, not seen in game**. The heap spill (493e472932) is still undeployed too.

## What this pass did: the bar's measure, and the lay fixed to it
The one open bar is never_taut_straight_cord, under the Conductor's 1:18 AM pass rule (RATCHET.md). Its measure did not exist, so I built it, then worked the lay down against it in the shape lab (`Transient/lab/ba/worlds/*.json`, the four played colonies dumped from the game).

- **The measure** (`CordShapeAudit.Bends`, `Why`, `BendTally`): a bend = the heading turns past 90 deg within 1 cell of cord (signed sum, so an S does not count), whole cord, ends included. Classes: `loop` (comes round >= 300 deg at mean radius >= 0.45: the north star's own loops, not a fault), `hidden` (under a wall or the plugged machine's art), `wall`/`building` (apex within 0.3 of an unwalkable cell, another machine or furniture), `door` (within 0.6), `socket` (within 0.75 of a junction arm / strip socket / wall plate / pile port / cut end when the course is >= 90 deg off the fitting's facing), `limp` (dead end's curl), else `unforced`. A machine plug is never a socket: we choose its side. Live: probe `bends`, row `M2c_no_sharp_bends` (renamed from M2c_no_folded_cords in validation.py and the core row list), PASS = 0 unforced. Lab: printed per world, `ralph/live/lab_bends_sum.py OUTDIR` sums by piece kind.
- **Unforced count, lab, HEAD before this pass**: Modern 56, Scrapper 83, Industrial 85, Futuristic 89. **Now: 27, 42, 42, 41** (it reached 21/35/33/28 with cut-end cords faired too, which broke the cut-end art).
- **Fixes** (all behind `LayParams.FairBends`, on in GSS's `CordBuilder.Lay`, off for FlowWorks):
  1. `CordShape.Fair`: the last shaping of every floor strand (LayEdge, LayDiving, heap strands). Every bend tighter than 0.7 cell (3-point radius over +-0.3 cell) on open floor is drawn toward its chord until none is left; broad loops and 0.2 cell at each end (cut ends: 0.6 live / 1.0 dead) stay; a point never moves into walls, furniture, doors, other machines, or nearer a wall. A loop too tight to be broad is cut out whole at its crossing.
  2. `CordShape.ArriveRound` (Dubins paths, radii 0.78 to 0.3): every end except a cut end comes round to its fitting at a bounded radius, cut back along the cord where the path turns least. This replaced the old `CordLayer.Approach` hook in the last half cell (the lamp hook, the strip-socket hooks, the "<" class).
  3. A one-cell machine (in game a standing lamp is a Consumer) takes its plug on whichever side the cord comes round to with clearly less turn (`SideSwitchGain` 0.35 rad). Lab: the bedroom lamp hook is gone (`Transient/lab/p16/lamp_ba.png`). In game: unseen.
  4. Loops: `RoundLoopMinR` 0.36 -> 0.5, `RoundFig8MinR` 0.5 -> 0.65 (GSS only), knot loops 0.5; heaps use `LooseHeap` turns >= 0.5 instead of the tight reversing `Heap` spring. Heaps still read as a dense tangle in the lab (`Transient/lab/p16/heap_Scrapper_ba.png`), rounder; outline still squarish.

## Self-tests: 1176/1178 (aerial 166/166)
Fixed on the way: cut ends (and the whole cord to a cut end) keep the old lay and approach, like ShortBow: the live run, limp curl and whip tails are break_live_and_dead_ends_differ's art, and fairing them broke nodal/downed/whip and made `determinism F33-35` differ on the terminal|battery cord. The "detached ends" check accepts a one-cell machine's plug on any side. A heap's broad coil that would leave the heap's ground is left out (a strip lost a cable: B13, pile look rule 1). Round lays try the 0.5 loop last (long-run end heaps).
Still red, first job next pass:
- `cord-shape: 24 folds in 123 strands` (old `CordShape.Kinks`, bar 1 in 20; was within it before this pass). Room() + PileWorld scenes, `CordShapeChecks.cs:~105`. Print where the folds are (piece names): heap strands (Fair inside a heap is held to its ground by `within`; a stuck point can leave a V) or end joins. With loop cuts in heaps on it was 159, off it is 24.
- `sustained change: the start did not settle equal to one unbudgeted Build (675 cords, pending 0)`: the budgeted/sliced lay path disagrees with one plain Build. Something in Fair/ArriveRound depends on more than the lay key covers (ArriveClear looks 4 cells round the target for machines; the corridor hash covers 3 round the path), or on order.
- Perf: the slice line reads "worst 11.1 ms (budget 8 ms)"; check whether it was over before this pass (git stash is not allowed: build HEAD~ in a worktree).
Lab now (cords to cut ends left unfaired): **Modern 27, Scrapper 42, Industrial 42, Futuristic 41** unforced.

## Do next, in order
1. Self-tests green (above). Then the rest of the lab's unforced bends: by kind it is heap mid/end ~10-17, junction->consumer mid 3-6, machine-end 2-4. Make sheets: `ralph/live/lab_bends_rows.py OUT.json SHARP.json` then `ralph/live/lab_sharp_sheet.py WORLD LAID SHARP OUT.png --skip-tangle` (or `--tangle-only`). Re-dump the worlds from the game first if you can (`dump_worlds.py`): the lab worlds have no furniture.
2. Deploy, then live: probe `bends` on each look's save (`gss_ba_<Look>`), four numbers; shoot `p12_look.py p16 --frames drop,span,dense --tiles` and look at the lamp, the heap and the mast foot in every look (the 12 shots the ratchet wants). If a live count is not 0, its rows say where.
3. Braiding (owner asked), bedroom_reno.py, proof core, GPT leads 4 and 7, a broaden call: see RATCHET.md 6-8.

## Steve this pass
Not used. No dead game, no dropped ssh, no reboot.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true (on 249698eeec; the new lay is broader-looped but unseen, recheck the slack census once deployed)
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true on the deployed build; the new heap is unseen in game
- break_live_and_dead_ends_differ: true (cut ends deliberately left on the old approach)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (lab unforced sharp bends 27/42/42/41 per look; the bar wants 0 in game)
- never_cord_across_impassable: true
