# GSS (Gimme Some Slack): the ratchet (Conductor, 2026-11-08 ~02:00 AM PST; counts brought up to date by pass 17)

Follows the audit (`/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_gss_2026-11-08.md`) plus the Conductor ruling 1:18 AM (OWNER_NOTE). Where PROGRESS says never_taut_straight_cord fails on "lamp hairpins and some straight legs", the ruling wins: straight legs are not a fail; only unforced SHARP bends are. One bar of 11 remains. Shots are in `D:\ClaudeWork\rimmandrake\ralph_gss\` (`p15\`, `shots\`).

## Remaining (work only on these, in this order)
Bar: never_taut_straight_cord. It passes only when ALL of this holds on the standard test colony in all four looks (Modern, Scrapper, Industrial, Futuristic). No judge verdict is needed beyond it:
1. M2c fixed to cover the WHOLE cord, ends included. DONE in code (pass 16): `CordShapeAudit.Bends`/`Why`, probe `bends`, row `M2c_no_sharp_bends` (PASS = 0 unforced). Neighbour cords are NOT counted as forcing (stricter than the ruling). Lab count of unforced bends per look, pass 17: Modern 17, Scrapper 26, Industrial 26, Futuristic 24 (pass 16 27/42/42/41; before 56/83/85/89). Self-tests 1178/1178 (pass 17). Left: short cords (chord < 3) 10-18 per look, the spur coil 1 per look. Still owed: 0 per look, read live from the probe on the four played saves.
2. Lamp lead hook (Modern, Industrial, Futuristic; Scrapper mild): cord runs past the lamp ~0.5 cell then hairpins into the top plug. Pass 16 (code, lab only): a one-cell machine plugs on the side the cord comes round to, and every end comes round on a Dubins path (`CordShape.ArriveRound`). Observation still owed: `ba_lamp_t00` right column in game, M2c count 0.
3. Mast-foot "<" in Industrial and Futuristic (short lead to the junction box), unchanged since judge p15a. Not on the loop's old list. Observation: `p15d` vs new mast-foot shot, M2c count 0.
4. Dense heap (square outline + one straight-legged hairpin): pass 17 re-laid every heap cable (`HeapWalk`: Dubins legs at >= 0.72 between roomy stops, bowed straights, whole coils, lumpy round ground; lab heap bends 0-3 per look, `p17\lab_heaps_walk_Scrapper_Modern.png`). Built, NOT deployed (deploy refused: FlowWorks holds game A). Observation: `ba_<look>_work_dense` heap shot in each look, before/after at play zoom (it changes an approved look), M2c count 0.
5. One screenshot per look of the lamp, the heap and the mast foot (12), cited beside the counts (the look half). `p12_look.py p15e --frames drop,span,dense --tiles`.
Then, owed and not bars:
6. Braiding (his ask: "random braiding would help a lot"): two or three cords twisting round each other for a stretch, on heaps and side-by-side runs. Look at photos of cord piles first. Not started.
7. Before DONE.md: `bedroom_reno.py TAG Modern Futuristic` (written, never run); `proof_all.py --live --only core` (expect 47/47); pass-10 leads 4 (damage wiring out of view, find it from the symptom, then with batteries empty) and 7 (restyle while a span is down, save, reload; master switch off while building, then on) with pass-11 #6 (join two runs in different looks) in the same run.
8. Bookkeeping: write the 7:07 PM definition into the walk bar or the judge brief; book the heap's square corners on ONE bar only (here, not also dense_grid_reads_as_tangle).
Not required: Modern "plugged in twice" at a T (`p15/z_m11_mid.png`).

## Proven (locked), 10 of 11. Build 249698eeec is deployed on Steve unless noted (heap spill 493e472932 not deployed)
- conduit_reads_invisible: PROGRESS pass 15 true; part of what the owner walked ("GimmeSomeSlack all looks great! Verified").
- cord_lies_slack_in_loops: `p15/ba_Modern_t01.png`, `p15/ba_lamp_t00.png` (slow wide curves); slack census 0 of 22 cords under 1.15 x chord (pass 3). 249698eeec.
- cord_meets_wall_at_its_face: PROGRESS pass 15 true; geometry untouched by the retune.
- dense_grid_reads_as_tangle: `p15/ba_Modern_work_dense.png`, Modern heap with a strip every 4 cells (249698eeec). Weakest TRUE: the heap spill (item 4) touches it, so look at the p15e heap once; it is not a separate stage.
- break_live_and_dead_ends_differ: `shots\p15s_close_sheet.png`; `spark_measure.py`: spark in 10 of 10 frames, mean 0.16 cell from the tip; owner certified by eye pass 11. Spark code untouched since.
- overhead_span_above_everything: `shots\p10a_Modern_spanpawn.png` (three colonists under the span, wires draw over them).
- downed_span_lies_on_ground: `shots\p15sa1_Modern_cutspan.png` (three wires per side lie loose, separate frayed ends, live ends spark).
- four_styles_distinguishable: PROGRESS pass 15 true; p15a judge saw four distinct looks.
- one_run_one_style: audit: holds; the judge's "foreign look cords" were the p15a staged second run in another look.
- never_cord_across_impassable: M2b `verticesInUnwalkable` 0 (pass-3 census); p15a judge class e zero across 44 frames. Rock "under the cord" in Industrial dense is rock chunks (walkable items).
Caveat for all look bars: the four colonies are scripted layouts; no usable real colony loads on Steve. That is staging, not a reopen.

## Rules
1. A proven bar stays proven and is not re-tested unless a change touched what it depends on; a pass does not re-prove Proven bars.
2. A bar moves back to Remaining only on a shown regression, with the evidence written beside it.
3. When never_taut_straight_cord is proven, move it to Proven with its counts and shots and the build in the same commit. When Remaining is empty, write DONE.md citing Proven ("I don't need the Judge to say it's ok. I just need it to be provably OK").
