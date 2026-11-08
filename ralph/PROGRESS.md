# GSS Ralph: where the last pass got to

Pass 18. Game A came free, so pass 17's build was deployed and measured first, then this pass's lay was built, deployed and measured. **Deployed on Steve (game b): HEAD** (eb80963c48's lay with the broad spur loop reverted, plus everything since 249698eeec: pass 16 fairing, heap spill, heap walk).

## What this pass did
1. **Pass 17's build seen live** (p18a): the probe `bends` read 17/26/24/24 unforced (Modern/Scrapper/Industrial/Futuristic), the lab's 17/26/26/24. The lab predicts live well, except where furniture matters (see 5).
2. **Unforced sharp bends cut** (CordBuilder.cs, all GSS-only via FairBends). Live on eb80963c48 (p18b): Modern 5, Scrapper 7, Industrial 7, Futuristic 2 (lab, no furniture: 4/7/5/1). **With the spur curl restored (deployed, p18c): 6/8/8/3.**
   - `BoxNub`: a junction box whose arm points at a machine 0-1.6 cells away plugs straight in, with a smooth sin² bow on longer gaps, then on under the art to the centroid. Was: a 140° V beside every lamp-over-box and battery-on-run (the "142.1° in 0.26 cell" rows, 6-9 per look). `p18\ba_scrapper_beds.png`.
   - `HopWhole`: a cord whose planned path is at most 4.5 cells and that the bar counts against is laid again from fitting pose to fitting pose (Dubins at radius 0.72-1.0, plus a C or lazy-S bow for slack, aimed at 1.2-1.4x the gap; rods and length under 1.15x cost). It is kept only if the bar counts it clean; cords that pass keep their lay.
   - `SmoothBends`: every bend still counted is re-laid as a Dubins window round it, between the cord's own poses either side. A hairpin becomes a round loop, the north star's own shape. A window may start at a fitting (a plug point heading in, an arm's straight bit) but never touches a cut end's last 1.6 cells.
   - The spur's pigtail (radius 0.22 on the box) became a broad loop (r 0.5-0.55), then was **reverted**: the blind judge found its ring hanging out of the box in every look, lying across a neighbouring strip or box and sharing the box's fitting with a real lead. `SpurLoop` is still in the code, unused. It needs to leave by a free arm and keep off other fittings first.
   - Re-lays keep 0.55 off other boxes, plates and cut ends. To keep incremental == fresh, those nodes are read off the graph alone (`CordGraph.NodesNear`, within 4 cells of the edge's chain) and ride in the edge's key.
   - Self-tests **1178/1178**. Cost: the worst sliced cold frame went from 13.4 to 14.3 ms; the all-reused Build is 0.18 ms.
3. **Heap before/after at play zoom**, owed since pass 17: `p18\heap_before_after_play_zoom.png` (before = p15d). The heaps are round and loopy now. The Industrial heap reads as an almost solid black mass with its boxes hard to see. That is in QUESTIONS.md for the owner, along with the short-lead change.
4. **Harness**: `steve.sh sync` now keeps Steve's tier before-copy across its `git checkout -f`. It is a tracked file: the checkout put the committed copy back, its md5 no longer matched the swap marker, and `up` started the game on Graffiti's mod list with GSS absent. That happened once this pass and was fixed by hand: the live list was the before-copy, md5 4fc23fae. **steve.sh is left uncommitted like the Conductor's other edits there**, but sync carries it. `p12_look.py --bends` prints and saves the probe. `ralph/live/lab4.sh OUTDIR` lays all four lab worlds, `lab_ba.py` renders lab before/after, and `lab_unforced_sheet.sh` makes a crop sheet.
5. **The lab has no furniture**: `worlddump` writes no furniture field and `LabWorld.Read` reads none, so 1-3 bends per look show live and not in the lab (e.g. Modern `junction:146,105|consumer:143,105`, laid clean in the lab but still counted live).

## Judge (blind rm-judge, p18a vs p18b, every tile of all four looks): "AFTER is not acceptable yet"
Sheet: `p18\judge_p18b_findings.png`; per-frame notes: `p18\judge_p18b_progress.md`. Coordinates are in the p18b image.
- Worse, spur ring: t21 lower mast box, t31 by the battery (all looks), Modern_t31 (890,358) across a strip, Scrapper_t31 (900,360) under the next box. **Fixed by the revert above** (p18c_<Look>_spur: gone).
- **Worse, still live**:
  - t21 upper mast box (Industrial 241,135; Futuristic 229,140; Modern 190-250,125-165): the box's lead arcs up over the overhead wire bundle to the insulator.
  - Futuristic_t11 (232,159): a V became a figure-8, a circle plus a self-crossing plus a U under a standing post; Industrial_t11 (336,84) the same, milder. That is SmoothBends' loop with nothing stopping it crossing the rest of the cord or going round a post.
  - Modern_t11 (1064,216): two socket cords cross in an X under the strip, then knot.
  - Scrapper/Futuristic_t01 (621,271): the lamp's plug end sticks out right of the lamp with a hooked tip.
  - Modern_t11 (350,150): a cord to the cut end goes in at a lamp post's foot and out at its top.
  - Futuristic_t10 (654,347): a tight hump on a 1-cell box-to-plate hop.
  - Scrapper_t20 (436,386): a circle running into the solar panel's corner.
- Still there in both builds:
  - Modern strip "<" hooks: t00 (845,352), (850,372), (1095,372); t10 (845,373), (420,360), (35,360); t11 (1175,154), (1175,179).
  - The left-bedroom lamp V, running under the bed foot (Modern, Industrial, Futuristic t00).
  - Stacked perfect-circle coils: Futuristic_t31 (1011,521), Industrial_t21 (300-400,600-690), Modern_t20, Scrapper_t20, Scrapper_dense.
  - Overhead wires zigzag over the crossarm: Modern_t31 (640-720,150), Industrial_drop.
- Better: the box-to-lamp V is gone (Scrapper_t00 862,320), and a lot of machine leads are now one sweep (Industrial/Futuristic_t11, Futuristic_t01, the dense-frame lamps, Industrial_dense battery). The p18b bend count does not see any of the "worse" list: **the bar's count is not the look.**

## Left on never_taut_straight_cord, live p18b (21 bends)
- Borderline 90-97° within one cell (about 8): box-to-box or box-to-plate corners one cell apart (`junction:46,65|junction:53,65` start, `junction:116,72|battery:115,72`), where the fittings face across a 90° corner with no room for radius 0.64. The honest fix is the strip or box pose (which arm leads where), not the measure.
- Heap cables, `tangle:` (Scrapper 2, Industrial 3, Modern 1): HeapWalk's plug bends. SmoothBends is not run on heap pieces.
- Cut-end cords `junction:85,87|terminal:87,87` (Scrapper): the hook at the box end, 0.25 from it. The window guard reaches it, but no clear Dubins path was found.
- Industrial `stub_wall:75,73|source:83,73` and Modern `junction:180,102|tangle:184,93`: long cords fixed in the lab but not live, so furniture is involved.

## Do next, in order
1. **The judge's "worse, still live" list first** (it is a regression on looks the owner approved). The likely cause for most of it: HopWhole and SmoothBends check only the ground. Give their candidates:
   - no crossing of the rest of the cord, except a whole loop's own base;
   - no crossing of another cord's fitting or plug (other pieces' ends are not known at lay time, so use the nodes, as OtherBoxes does, and the mast's footprint and wire line);
   - nothing under a standing lamp or post.

   Then re-shoot the judge's frames and have a fresh judge compare them with p18a. Shoot with `p12_look.py TAG --tiles --frames dense,drop,span`.
2. The Modern strip "<" hooks (8 in Modern alone, in both builds): the bar mostly calls them "socket". They are what the owner sees, so judge by the shot, not the count.
3. Add furniture to `worlddump` (GimmeSomeSlackProbe.WorldDump) and `LabWorld.Read`, so the lab equals live and catches the bed cases.
4. Then: the 90° corners between fittings a cell apart (box or strip pose), heap plug bends, and RATCHET 5-8.

## Steve this pass
`status` once: bad_cpus=[2], game b running on someone's list. A deploy, then `up`, started the game on Graffiti's list (the swap-marker trap above): fixed by hand, after which tier and up worked. Three deploy+up cycles, three `p12_look.py` runs (12 save loads) and one world dump. No dead game, no dropped ssh, no reboot.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true. Hops aim at 1.2-1.4x. The slack census is not re-run. The judge saw stacked perfect-circle coils, which were already there in p18a.
- cord_meets_wall_at_its_face: true (plates untouched; SmoothBends windows stop at the face)
- dense_grid_reads_as_tangle: true on 249698eeec. The new round heaps are seen live (p18a/p18b dense) but owe the owner's look, and Industrial reads as a solid mass.
- break_live_and_dead_ends_differ: true (a cut end's last 1.6 cells are never re-laid; spark code untouched)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (live 6/8/8/3 unforced, and the judge's list of new hooks, figure-8s and crossings that the count does not see)
- never_cord_across_impassable: true (re-lays check walkable ground; not re-censused on eb80963c48)
