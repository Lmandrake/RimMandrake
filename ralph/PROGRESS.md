# GSS Ralph: where the last pass got to

Pass 18. Game A came free, so pass 17's build was deployed and measured first, then this pass's lay was built, deployed and measured. **Deployed on Steve (game b): eb80963c48** (this pass's lay, plus everything since 249698eeec: pass 16 fairing, heap spill, heap walk).

## What this pass did
1. **Pass 17's build seen live** (p18a): the probe `bends` read 17/26/24/24 unforced (Modern/Scrapper/Industrial/Futuristic), the lab's 17/26/26/24. The lab predicts live well, except where furniture matters (see 5).
2. **Unforced sharp bends cut** (CordBuilder.cs, all GSS-only via FairBends). Live on eb80963c48 (p18b): **Modern 5, Scrapper 7, Industrial 7, Futuristic 2** (lab, no furniture: 4/7/5/1).
   - `BoxNub`: a junction box whose arm points at a machine 0-1.6 cells away plugs straight in, with a smooth sin² bow on longer gaps, then on under the art to the centroid. Was: a 140° V beside every lamp-over-box and battery-on-run (the "142.1° in 0.26 cell" rows, 6-9 per look). `p18\ba_scrapper_beds.png`.
   - `HopWhole`: a cord whose planned path is at most 4.5 cells and that the bar counts against is laid again from fitting pose to fitting pose (Dubins at radius 0.72-1.0, plus a C or lazy-S bow for slack, aimed at 1.2-1.4x the gap; rods and length under 1.15x cost). It is kept only if the bar counts it clean; cords that pass keep their lay.
   - `SmoothBends`: every bend still counted is re-laid as a Dubins window round it, between the cord's own poses either side. A hairpin becomes a round loop, the north star's own shape. A window may start at a fitting (a plug point heading in, an arm's straight bit) but never touches a cut end's last 1.6 cells.
   - The spur's spare-cord pigtail (radius 0.22 on the box) became a broad loop (r 0.5-0.55) on clear floor beside it.
   - Re-lays keep 0.55 off other boxes, plates and cut ends. To keep incremental == fresh, those nodes are read off the graph alone (`CordGraph.NodesNear`, within 4 cells of the edge's chain) and ride in the edge's key.
   - Self-tests **1178/1178**. Cost: the worst sliced cold frame went from 13.4 to 14.3 ms; the all-reused Build is 0.18 ms.
3. **Heap before/after at play zoom**, owed since pass 17: `p18\heap_before_after_play_zoom.png` (before = p15d). The heaps are round and loopy now. The Industrial heap reads as an almost solid black mass with its boxes hard to see. That is in QUESTIONS.md for the owner, along with the short-lead change.
4. **Harness**: `steve.sh sync` now keeps Steve's tier before-copy across its `git checkout -f`. It is a tracked file: the checkout put the committed copy back, its md5 no longer matched the swap marker, and `up` started the game on Graffiti's mod list with GSS absent. That happened once this pass and was fixed by hand: the live list was the before-copy, md5 4fc23fae. **steve.sh is left uncommitted like the Conductor's other edits there**, but sync carries it. `p12_look.py --bends` prints and saves the probe. `ralph/live/lab4.sh OUTDIR` lays all four lab worlds, `lab_ba.py` renders lab before/after, and `lab_unforced_sheet.sh` makes a crop sheet.
5. **The lab has no furniture**: `worlddump` writes no furniture field and `LabWorld.Read` reads none, so 1-3 bends per look show live and not in the lab (e.g. Modern `junction:146,105|consumer:143,105`, laid clean in the lab but still counted live).

## Judge (blind, this pass's shots p18a vs p18b)
(see below, filled in when it returned)

## Left on never_taut_straight_cord, live p18b (21 bends)
- Borderline 90-97° within one cell (about 8): box-to-box or box-to-plate corners one cell apart (`junction:46,65|junction:53,65` start, `junction:116,72|battery:115,72`), where the fittings face across a 90° corner with no room for radius 0.64. The honest fix is the strip or box pose (which arm leads where), not the measure.
- Heap cables, `tangle:` (Scrapper 2, Industrial 3, Modern 1): HeapWalk's plug bends. SmoothBends is not run on heap pieces.
- Cut-end cords `junction:85,87|terminal:87,87` (Scrapper): the hook at the box end, 0.25 from it. The window guard reaches it, but no clear Dubins path was found.
- Industrial `stub_wall:75,73|source:83,73` and Modern `junction:180,102|tangle:184,93`: long cords fixed in the lab but not live, so furniture is involved.

## Do next, in order
1. Add furniture to `worlddump` (GimmeSomeSlackProbe.WorldDump) and to `LabWorld.Read`, re-dump with `ralph/live/dump_worlds.py`, and confirm the lab equals live (5/7/7/2).
2. Run SmoothBends on heap cables with the heap's own ground (`onGround` from TanglePiece), and give the cut-end box end a wider radius list.
3. For the 90° corners between fittings a cell apart: pick the box's (strip's) arm or pose toward where its lead goes, or let a box lead leave on the arm it bends toward.
4. Owner-facing look shots per look (the ratchet's 12: lamp, heap, mast foot), then RATCHET 6-8: braiding, bedroom_reno.py, proof core, the GPT leads, a broaden call.

## Steve this pass
`status` once: bad_cpus=[2], game b running on someone's list. A deploy, then `up`, started the game on Graffiti's list (the swap-marker trap above): fixed by hand, after which tier and up worked. Two deploy+up cycles, two `p12_look.py` runs (8 save loads) and one world dump. No dead game, no dropped ssh, no reboot.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true. Hops aim at 1.2-1.4x and SmoothBends adds loops. The slack census is not re-run on eb80963c48.
- cord_meets_wall_at_its_face: true (plates untouched; SmoothBends windows stop at the face)
- dense_grid_reads_as_tangle: true on 249698eeec. The new round heaps are seen live (p18a/p18b dense) but owe the owner's look, and Industrial reads as a solid mass.
- break_live_and_dead_ends_differ: true (a cut end's last 1.6 cells are never re-laid; spark code untouched)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (live 5/7/7/2 unforced; the bar wants 0)
- never_cord_across_impassable: true (re-lays check walkable ground; not re-censused on eb80963c48)
