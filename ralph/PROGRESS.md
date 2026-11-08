# GSS Ralph: where the last pass got to

Pass 15. Retired on the context gate. Game on SteveDesktop, 11 mods (GSS, FW, bridge, camera, all DLC). **Deployed on Steve = 249698eeec**. The heap spill (below) is committed after it, built, **not deployed and not seen**. Self-tests 1178/1178, aerial 166/166.

## The owner's two asks, this pass
- **Spark on the writhing end**: certified by the owner by eye on pass 11; the spark code (`TipSparks`, `DrawFallenTails/Glow`, `CordMotion`) is untouched since. Re-shot on the current DLL in a played colony after a blast: `p15s_close_sheet.png`, `p15s_play_sheet.png` (+ `.gif`), Modern; `p15t_*`, Scrapper. `spark_measure.py`: spark in 10/10 frames each, mean 0.16 cell from the probe's moving tip. Dead half lies dark beside it. Writhe travel is small (0.24-0.51 cell).
- **Several cables into one outlet**: a ninth form found and fixed. A strip right beside a wall outlet faced its sockets at the wall, so the cords to its other arms plugged in beside the outlet: three cables into one tab (`p15/ba_Modern_t01_r.png`, before left). Now the strip's own lead goes into the outlet and it stands 0.3 back (`CordGraph.WallArmsOf`, `PoseStrip`). Not yet written into QUESTIONS.md for the owner: **do that first**.

## Done this pass (committed, seen in game unless said)
- Strip beside a wall outlet plugged in by its lead (above). Seen, Modern kitchen.
- **Loops** (`LayParams.RoundLoops`, GSS only): no loop under 0.36 cell (left out, not shrunk), figure-8 only from 0.5, a spare-cord pile is 2-3 loose turns wound one way (`CordLayer.LooseHeap`), loops/piles keep 1.6 cell from the cord's own ends. The heater "bird-nest" the judge found in every look is a loose coil now (`p15/ba_Modern_t01_r.png`); Scrapper and Industrial bedroom knots gone (`p15/ba_lamp_t00.png`). Ring returns at ends 0/79 (was up to 7).
- **Short hops bow** (`LayParams.ShortBow`): a hop under 2.5 cells is a lazy C (height <= 0.35 L + 0.3), not one tall bump; cords to a cut end keep the old lay (whip tail needs the length). The workshop "washing line" of V's is gone (`p15/ba_Modern_work_dense.png` top).
- **Modern heap**: a strip every 4 cells (was 7): reads as a tangle now (same sheet, bottom).
- **Heap spill** (NOT deployed): heap cables may lie a cell past the conduit block on open floor (`PileGround`), stops jitter x2: the square outline the judge flagged in every look. Lab only (`Transient/lab/p15/dense_g.png`).
- FlowWorks DLL rebuilt twice for the shared lay (its options are off there; the push guard needs it).
- Cut span at play zoom: three wires per side lie loose on the ground with separate ends, no pinch (`p15sa1_Modern_cutspan.png`). Battery drained -> live half dead; recharged -> live; colonists re-strung both halves in ~5,200 ticks (`p15ta2..4_Scrapper_*`, `span_life.py`).
- A real player's colony was tried: Steve's own 2023 saves (The Omega Team, 473 conduit) are 1.4 with ~290 mods; a copy with its mod list rewritten still fails to load (message box at the menu). Copy deleted. No usable real colony on Steve.

## Tried and reverted
- **Lamp hairpin** (judge: every look, bedroom 1, `p15/ba_lamp_t00_d.png`): in game lamps are Consumers (adapter, owner-walked), plug side = side facing vanilla's hookup cell; the slack is laid first, so the cord goes round the lamp and hooks back in. My `LampEntry` (Kind==Lamp only) never fires in game; it is harmless and left in. A rule "plug a one-cell device where the cord first comes within 0.85 of it, trim the wrap" failed 4 self-tests (nodal end, slideunder midpoints/diagonal, folds). Next try: use `CordGraph.PlugPoint(m, FacingCell(m, tip), g.Slides(m))` for the side (keeps the slide rule), trim only when the cut-off wrap is >= 0.9 cell. I had this written when the gate stopped me.

## Blind judge p15a (before this pass's changes): `D:\ClaudeWork\rimmandrake\ralph_gss\judge_p15a\report.md`
Counts a/b/c/d/e/f: Modern 17/2/10/0/0/9, Scrapper 15/4/1/2/0/4, Industrial 27/4/2/4/0/13, Futuristic 30/8/1/4/0/15. "Mostly yes ... what breaks the illusion most is tight curls, figure-8s and stacked coils." Then: repeated motifs (arm U-dips, washing-line V's, lamp hairpins, "<" at mast feet), Modern "plugged in twice", squared heaps.

## Do next
1. Deploy, shoot `p12_look.py p15e --frames drop,span,dense --tiles`, send p15e to the same judge format (fresh subagent, brief like p15a's) and compare counts with p15a.
2. Lamp hairpin (above).
3. Modern "plugged in twice": at a T on a through line, the free-arm cord and the stem cord leave adjacent sockets on the same side and run parallel ~1 cell (`p15/z_m11_mid.png`). Idea: free-arm SwingIn turns toward the free end sooner and over a longer stretch (`SwingIn` j-radius 0.85 -> ~1.2).
4. `bedroom_reno.py TAG Modern Futuristic` is written, never run (GPT pass-13 lead 1, still owed before DONE).
5. Owner's answer in QUESTIONS.md for the ninth cause; then `proof_all.py --live --only core` (expect 47/47) and a broaden call with the new shots.

## Steve this pass
bad_cpus [1] then [2]. No dead game, no dropped ssh, no reboot. 4 deploy + restart cycles, bridge up in 34-41 s. One failed save load (the 1.4 colony), cleared by closing the dialog. The night step of `span_life.py --night` did nothing: `jawa/time_clock` has no hour field.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true for the junction looks and the new Modern heap in game; square outline fix unseen
- break_live_and_dead_ends_differ: true (`p15s_close_sheet.png`)
- overhead_span_above_everything: true (pass 13)
- downed_span_lies_on_ground: true (`p15sa1_Modern_cutspan.png`)
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (lamp hairpins and some straight legs remain; not re-judged blind since the fixes)
- never_cord_across_impassable: true
