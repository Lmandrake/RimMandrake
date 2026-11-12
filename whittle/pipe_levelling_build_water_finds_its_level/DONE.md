<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A1 (L0):** offline built baa270b9e8+0ac23150a2: SelfTest LEVELLING_* (Source/SelfTest/LevellingChecks.cs) green: exact volume incl. limitless net, energy never rises, two- | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A1_A2_selftest_LEVELLING.txt`
- true: **A2 (L0):** budget case: 200 bodies (40 of 40,000 squares), 400 links, 64 links per cycle: kernel 89 us per 250-tick cycle; feasibility written in the design doc's ### Leve | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A1_A2_selftest_LEVELLING.txt` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A2_feasibility_section.md`
- true: **A3 (L1):** 325x325 map, two 40,000-cell basins, 200 links: live tick time and allocations of RM_Levelling.Tick (the dug-run walk is unmeasured offline). | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A3_perf_timed_200_links.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A3_perf_phases.json`
- true: **A4 (L2):** two ponds of unequal height joined by a hose with two open ends level out (HoseNetProbe levelMoves > 0, surfaces within 1 cm), the hose reads "Levelling: flowin | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_walk_gaps_ponds.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a4_refilled_flowing_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a4_relevelled_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a4_relevelled_outflow_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_look_ponds.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/broaden_saveload_roles.json`
- true: **A5 (L2):** a water pond and an oil pit joined the same way exchange nothing; the hose reads "different liquids never mix". | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_walk_gaps_ponds.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a5_nomix_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a5_nomix_outflow_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a5_nomix_desktop.jpg`

## What each piece shows
- A1/A2: the C# SelfTest on the final source, LEVELLING_* 11/11 (plus the Outflow_* and HoseText_* text pins I touched, 17/17
  in all); 300 fuzz scenes all reach a fixed point; the budget case reads 81.5 us per cycle this run (88.9 us earlier today;
  the criterion's 89 us is the same order). The design doc's "Levelling feasibility" section (excerpt in the evidence) now
  carries the live results; it said "the live run is owed" and asked a pump question the owner had already ruled, both fixed.
- A3: a fresh 325x325 map (tile 47676, AridShrubland), two 125x305 basins dug 4 notches (one filled F=4, one F=1), 200 rigs laid
  in six slices with 0 failures, links=200 of 200 wanted, then 20 timed cycles: RM_Levelling.Tick msAvg 13.99 ms per 250-tick
  cycle, 0.056 ms per tick, worst 53.8 ms (the one cycle with a GC), ~460 KB managed-heap growth per cycle. Both rows PASS
  against the proof's provisional bars (<=16 ms avg, <=0.1 ms/tick, <=1024 KB).
- A4: two 3x3 pits, 4 notches deep, 360,000 vs 90,000 dL, joined by two reels on one pipe run (Intake / Outflow). The reel's own
  inspect pane (jawa/inspect_string, and desktop captures of the pane) reads "Levelling: flowing (no pump; the higher water runs
  to the lower)." from the first cycle (tick 250) and "Levelling: level." at tick 4750, when the pools stood at 225,234 /
  224,766 dL (52 dL per square apart, under 1 cm), total conserved. Topping one pool back up made it flow again and re-level,
  total conserved. Save/reload mid-flow replays exactly (BROADEN.md).
- A5: water F=4 vs chemfuel F=1 on the same rig: 0 moves over 1,500 ticks, both pools' dL unchanged, both reels' panes read
  "Levelling: stopped, different liquids never mix." (the chemfuel pit is visibly orange in the desktop capture).

## What I changed this round
- The reel's inspect pane contradicted itself ("Intake needs a working pump on this network." above "Levelling: flowing (no
  pump ...)"; the outflow said "Nothing drains here: needs a pump or a tank set to Dump.") and the extra lines pushed the
  Levelling line below the pane's fold behind a scrollbar. Now an end in a levelling link drops the pump-need line and the
  "(taking water in needs a pump: set this end to Intake)" hint, an end already set to Intake drops that hint, and just after a
  load (before the first levelling cycle) a no-pump network with two open ends makes no pump claim. Every pane now fits.
- walk_gaps_proof PONDS_* now require what the player reads: A4 needs the inspect text "Levelling: flowing" AND, after the
  pools close, "Levelling: level." (it used to stop at 1 cm and never look for "level"); A5 needs the inspect phrase, not the
  proof hook's enum word.
- pipe_levelling_perf_proof: driver_stamp, abandoned at 15 s, made bridge calls mid-run and desynced the socket ("unexpected
  response id", 2 of 2 runs); it is now waited on up to the per-call cap or the run is refused (lesson filed).

## What I'm least sure about
- A3's bars are provisional (no owner number). 14 ms average per 250-tick cycle at 200 links is close to the 16 ms bar, and a
  53.8 ms cycle is a visible hitch at 1x; 200 links is a stress case far past an ordinary base (100 links measured 6.9 ms on
  2026-10-26). The A3 run is on the 60bbc5b684 DLL; the later commits changed only inspect text and added a read-only
  RM_Levelling.HasRun, not the tick.
- The ledger moved the item to done itself when the last owed criterion passed (rimflow verify), before this DONE.md and
  the judge; I did not run a close.
- A pit whose water sits below its lip reads "Free end: lying free" at an end that levelling is drawing through (the hose
  band rule says water across a sheer wall is out of a free end's reach; levelling resolves the end square and its 8
  neighbours like a pump does). Both rulings are as built; a player may find "lying free" odd while water flows.

## What I did not test
- A pump switched on mid-flow (owner ruling: off while pumping, resumes after) live; a third open end on one network; a river
  or limitless sea end live (offline A1 covers sea to brim); freezing; rain filling a pit mid-link; deconstructing a reel
  mid-flow; the owner's full mod list (all runs are the FlowWorks tier on SteveDesktop game A, all five DLC on).
