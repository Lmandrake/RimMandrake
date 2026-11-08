# GSS Ralph: where the last pass got to

Pass 14. Retired on the context gate (about 255k). **Game A is mine** (`ralph/GAME` = a since 20:49, GAME_SWITCH). Game A runs the FlowWorks list, which includes GSS (11 mods: GSS, FW, bridge, camera, all DLC). `steve.sh up` tried to put my tier on and refused: "swap marker names before-copy ... missing or changed; recover the owner's list by hand". I left it alone, since GSS loads on that list. **Deployed on A = HEAD a410bd2df4** (all of the work below). Self-tests 1178/1178, aerial 166/166, offline 9/9.

## Done this pass (all committed, all seen in game unless said)
- **Round loops finished**, after the builder's work in pass 13. The red `nodal` row: a dead end whose cord bends into it against the limp curl now takes the other curl, or one that turns over nearer the tip (`CordLayer.LimpTail`, only when the plain curl turns under 50°). **Hops under 2.5 cells keep the old lay** (`RoundMinLen`): on a lamp's 1.88-cell lead the round lobe laid a V pressed against the obstacle beside it. That was the live proof's M2c fold FAIL and 13 of 24 new kinks. Kinks over the four played worlds: 44 before round loops, 56 with them, **37 now**. Doors matrix unchanged; straight runs over 2.5 cells 36 → 21.
- **Lamp-mast drop**: the ground run wandered up-screen behind the pole and under the wires, then curled into the lamp, so in all four looks it read as strung from the crossarm (`p14a_drop_sheet.png`). Now it may rise at most 0.35 cell above its touchdown or the lamp (`AerialMath.LayDrop`, `DropRise`), and LooseRun refuses draws under 1.32x. After: `p14b_drop_sheet.png`, the cord hangs down the pole and lies to the lamp. Self-test rows with a can-fail.
- **Eighth cause, fixed** (QUESTIONS.md updated): `CordPlanner.ShortDive` (GSS only). The cord dives through the wall when walking round is at least 6 cells and 1.8x longer. In each played world exactly that one cord changed, from 17.8 to 4.4 cells: `p14cd_Modern_lamp8_ba.png`. Self-test rows D8.
- **Cords under beds** (the judge flagged beds threaded in every look): furniture (passable buildings of 2+ cells) is marked per cell in `CordWorld` from `CordWorldAdapter`. It has a route cost of 3, excursions' reach stops at it, a pass 0.2 cell deep counts as a stray and is re-laid, and the corridor hash includes it. Before: top of `p14ae_Modern_beds_ba.png`. After: `p14f_beds_sheet.png`, three bedrooms per look, no cord under a bed. One Futuristic cord still runs along a bed's foot edge.
- **Modern tangle**: strip-pile cables swirl (`CordBuilder.Swirl`) instead of strokes between far sockets: `p14ag_Modern_heap_ba.png`. Junction piles are unchanged. It's still less dense than the junction heaps.
- **ST2 row was stale**: Scrapper's overhead line is `Strand_Jawa` by design (f3be8bcd3a); `ralph/live/st2_probe.py` shows the span follows every switch. I fixed the row in `validation.py`. **Live proof core on a410bd2df4: 46/47**: M2c PASS, ST2 FAIL only on the stale expectation, now fixed but not re-run. Not recorded on the ledger.
- Blind tile judge (subagent) on `p14a_*_t??.png` (shot BEFORE the drop, bed and short-hop fixes): its report is in `D:\ClaudeWork\rimmandrake\ralph_gss\judge_p14a\` (zoom crops `z_*.png`). Still open from it:
  - tight 2-3-turn coils, figure-8s and knots on open floor (AddLoops/Heap; the owner prefers slow loops);
  - plug cords leaving a strip's socket sideways and hooking back;
  - a cord's U-lobe touching a floor item so it looks plugged in;
  - a solar panel leg with cords in and out.

## Broaden call (made this pass): `D:\ClaudeWork\rimmandrake\ralph_gss\gpt_help_pass013.md`
I asked with the drop, bed, eighth-cause and heap shots attached. It said: the bedrooms still show small loops; the revised Modern heap still has long diagonal stretches; static shots don't show transitions. Of its 7 leads, two are the most revealing for this pass's changes and are **not yet acted on**. Do them first:
1. Remodel a powered bedroom while watching: move a bed across a cord, add furniture at its foot, wall off a passage and remove it. Watch for clipping, extra feeds and abrupt route changes. This tests the new furniture re-lay and corridor hash live.
2. Cut a span while powered, cut its supply, restore it, repair it; watch at play zoom, also at night. The spark must stay on the moving tip on the current build (last measured on pass 12's DLL, 12/12 frames; `ralph/live/motion_frames.py`, `spark_measure.py`).
Others worth a look: a cramped starter base against rock built piecemeal (#6); a busy workshop with clutter, where lobes touch items (#5).

## Do next
1. The two GPT leads above (live), then re-run `proof_all.py --live --only core`: expect 47/47.
2. Re-shoot the tiles (`python.exe ralph/live/p12_look.py TAG --frames drop,span,dense --tiles`). Send them to a fresh blind judge subagent, without my verdicts, against the p14a list.
3. Tight coils: AddLoops/Heap loops of 0.2-0.4 cell radius stack into 2-3-turn springs. Consider one loop per spot and a radius of at least 0.35. That changes an approved look, so judge it before and after side by side.
4. Strip plug hooks: a strip at a junction faces its sockets toward one side, so cords leave and hook back.
5. Modern heap density (more strips or cables), and braiding (owner 7:07) if it still reads thin.

## Steve this pass
bad_cpus seen [6], [10], [4]. No dead game, no dropped ssh, no reboot. 8 deploy + restart cycles of game A, bridge up in 34-35 s each. ST2's surprise failed again after a game restart and turned out to be a stale row, not weather.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: false (Modern now swirls, but GPT still sees long diagonal stretches and it is thinner than the other looks; not re-judged blind)
- break_live_and_dead_ends_differ: true (pass 13 `p13m_*_sheet.png`; the spark code was untouched)
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true (`p13acut_Modern_cutspan.png`)
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false (drop and short-hop V's fixed and seen; the judge's sharp plug hooks and tight coils are still open; not re-judged blind)
- never_cord_across_impassable: true
