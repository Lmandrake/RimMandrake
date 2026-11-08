# GSS Ralph: where the last pass got to

Pass 19. **Deployed on Steve (game b): HEAD** (teardrop spur), seen live in p19b. Shots: `D:\ClaudeWork\rimmandrake\ralph_gss\p19\` and `shots\p19a_*` (all tiles, dense, drop, span), `shots\p19b_*_spur`.

## What this pass did
1. **The blind judge's p18b "worse, still live" list is fixed live** (`p19\judge_spots_p18a_p18b_p19a.png`, one row per spot, p18a | p18b | p19a): no ring at the mast box over the wires, no figure-8, no socket X under the strip, no cord through the post, no hump, no circle into the solar panel. The cause was one thing: SmoothBends and HopWhole could lay any Dubins path on clear ground, so they found whole rings and loops far from the old cord. Now a re-laid bend (CordBuilder.SmoothBends):
   - stays within 0.8 cell of the cord it replaces (`PtGrid`, `SmoothStray`);
   - turns no further than the old stretch did + 0.45 pi (or 1.3 pi), and no single arc comes round more than 1.3 pi (`SmoothArcMax`);
   - adds no crossing of itself (`CrossingsOf`);
   - never lies in the cell above a standing lamp (`UnderLampArt`).
2. **Fittings too close to come round between** (a mast's pole box and its wall plate, two boxes half a cell apart): no path at the bar's radius joins them without a loop, which is why SmoothBends threw rings there. `FitCorner` lays one clean small turn or a lazy S (radius 0.6 down to 0.32). The audit calls such a turn forced ("socket") only when it is round (no more than 45 degrees within 0.1 cell of the apex), turns no further than the two facings ask + 25 degrees, and the two fittings really are too close (`CordShapeAudit.FittingsForce`: every Dubins path at 0.64 turns more than 1.5 pi). A kink is never forced.
3. **Spur spare cord**: was a 0.22 curl that read as a J-hook live and counted in every look. Now `SpurHank`: a dropped teardrop of cord out of a side of the box no cord leaves by, legs crossing at the box, kept 0.6 off other boxes and machines; on a Modern power strip, nothing (the empty socket is the spur). Live: `p19\spur_p18a_vs_p19b.png`. No bend of it is counted.
4. **Lab = live now.** The world dump carries furniture and path costs, and `LabWorld.Read` reads them. The lab's unforced list matches the live probe cord for cord in all four looks (p19a). The lab worlds in `Transient/lab/ba/worlds/` are the new dumps (old ones in `worlds_p18/`). `bash ralph/live/lab4.sh DIR` is the 9-second loop.
5. Tools: `lab_look.py DIR...` counts the judge's classes on a lab lay (self-crossings off heaps, cords crossing near their shared box, cords over another box, tight full rings, cords under a lamp's art) and diffs two lays per cord; `lab_changed.py A B OUT` sheets every cord two lays disagree on; `judge_spots.py OUT TAG...` crops the judge's spots across shoots; `p12_look.py --dump` dumps the world for the lab in the same run.

Self-tests 1178/1178; worst sliced cold frame 13.6 ms (pass 18: 14.3).

## never_taut_straight_cord: live unforced 7/7/8/5 (Modern/Scrapper/Industrial/Futuristic, p19a/p19b)
Pass 18's 6/8/8/3 was lower because the rings hid bends. The 27 left, lab and live alike:
- **Cut-end cords** (`|terminal:`; Modern 0, Scrapper 2, Industrial 1, Futuristic 2): a V mid-cord and a hook 0.25 from the box. They keep the old lay (no Fair, no HopWhole) for the limp curl; SmoothBends finds no U whose legs fit within the stray limit (`HOP smooth ... turn/len`).
- **Heap plugs** (`tangle:`; Modern 1, Scrapper 2, Industrial 3): HeapWalk's plug bends. SmoothBends does not run on heap pieces.
- **Lamp/consumer leads** (Modern `166,105`, `146,105|consumer:143,105`, Industrial `66,65`, Scrapper `104,83`): a hook into the machine's side.
- **Box to battery a cell apart** (Scrapper `116,72`, Futuristic `141,152`): a 94-degree bump, sharp only 46: lower the bow or let FitCorner handle machine ends.
- **Long cords** with a tight pretzel or a hook at the far end (stub_wall to source in Scrapper, Industrial, Futuristic; Industrial `80,62|tangle`, Modern `180,102|tangle`, `160,107|stub_wall`, Industrial `46,65|53,65`, Futuristic `96,165|103,165`).
- Modern strip sockets `166,113|stub_wall:167,113` and `173,105|175,105` (a kink 0.1 from the socket).
- Not counted but seen: Modern strip "<" hooks at sockets (the audit calls them "socket"), e.g. `shots\p19a_Modern_t00` (845,352) beside the bed. Now the lab has the bed, `lab_render.py` on Modern 147,111,7,4 should show them.

## Do next, in order
1. Work the count down in the lab (`lab4.sh`, `lab_look.py` against `Transient/lab/p19/g7` to see that no look fault comes back). The biggest groups are cut-end cords and long-cord pretzels (SmoothBends windows) and heap plugs. Then the lamp/battery leads.
2. The Modern strip "<" hooks: judge by the shot, not the count.
3. Before DONE: a GPT `broaden` call (none made this pass), and RATCHET 5-8 (12 look shots, braiding, bedroom_reno, proof_all core, leads 4/7).

## Steve this pass
`status` showed bad_cpus=[], then [4], then [2]. Three deploys. One `up` failed ("the game did not come up"): weather, and the retry started it. No dropped ssh, no reboot. Two `p12_look.py` runs (8 save loads) with world dumps.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true. The spur's spare cord is now a loose loop; the rest of the lay is pass 17's except where SmoothBends or FitCorner re-lays a bend.
- cord_meets_wall_at_its_face: true (FitCorner ends at the plate's face along its facing, PastFace as before)
- dense_grid_reads_as_tangle: true on 249698eeec. The round heaps owe the owner's look (QUESTIONS), and the Industrial heap reads as a solid mass.
- break_live_and_dead_ends_differ: true (cut end's last 1.6 cells never re-laid; spark code untouched)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (live 7/7/8/5 unforced; the judge's p18b regressions are fixed)
- never_cord_across_impassable: true (re-lays check walkable ground)
