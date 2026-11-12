<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: **A1 (L0):** offline built baa270b9e8+0ac23150a2: SelfTest LEVELLING_* (Source/SelfTest/LevellingChecks.cs) green: exact volume incl. limitless net, energy never rises, two- | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A1_A2_selftest_LEVELLING.txt`
- true: **A2 (L0):** budget case: 200 bodies (40 of 40,000 squares), 400 links, 64 links per cycle: kernel 89 us per 250-tick cycle; feasibility written in the design doc's ### Leve | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A1_A2_selftest_LEVELLING.txt` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A2_feasibility_section.md`
- true: **A3 (L1):** 325x325 map, two 40,000-cell basins, 200 links: live tick time and allocations of RM_Levelling.Tick (the dug-run walk is unmeasured offline). | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A3_perf_timed_final_dll.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A3_perf_phases.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A3_levelling_tick_breakdown.txt`
- true: **A4 (L2):** two ponds of unequal height joined by a hose with two open ends level out (HoseNetProbe levelMoves > 0, surfaces within 1 cm), the hose reads "Levelling: flowin | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_walk_gaps_ponds.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_levels_over_time.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a4_refilled_flowing_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a4_relevelled_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a4_relevelled_outflow_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_look_ponds.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/broaden_saveload_roles.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_mixed_rigs_surfaces.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_mixed_rigs_depths_and_natural_pond.json`
- true: **A5 (L2):** a water pond and an oil pit joined the same way exchange nothing; the hose reads "different liquids never mix". | evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_walk_gaps_ponds.json` `whittle/pipe_levelling_build_water_finds_its_level/evidence/A4_A5_levels_over_time.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a5_nomix_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a5_nomix_outflow_pane.png` `whittle/pipe_levelling_build_water_finds_its_level/evidence/lev_a5_nomix_desktop.jpg`

## What each piece shows (all re-run on the final source and DLL, 7eff26d38e)
- A1/A2: the C# SelfTest: LEVELLING_* 11/11 (17/17 with the Outflow_* and HoseText_* text pins); 300 fuzz scenes all reach a
  fixed point; the budget case (200 bodies, 400 links, 64 per cycle) reads 81.2 us per cycle (77.5-88.9 us across today's
  runs; the criterion's 89 us). The design doc's "Levelling feasibility" section (excerpt) carries the live results, the walk
  caps as the code has them (20,000 squares per run, 120,000 per cycle) and the measured kernel range.
- A3: a fresh 325x325 map (tile 83862, Desert), two 125x320 basins of exactly 40,000 squares each (dug and filled 40,000 of
  40,000, `A3_perf_phases.json` staged), edge sinks held off for every phase so the basins' edge rows do not drain off the
  map (`--basins edge --sinks-off`), 200 rigs laid with 0 failures, links=200 of 200, 60 timed cycles: RM_Levelling.Tick
  6.48 ms per 250-tick cycle on average, 0.026 ms per tick, ~309 KB managed-heap growth per cycle, one GC in 60 cycles; worst
  timed cycle 34.1 ms. The breakdown (`A3_levelling_tick_breakdown.txt`, ProofTiming, which also counts the cycle before
  the timing) puts the worst cycle, 58.6 ms, at the first one after the network changed: 200 components built and the hose
  links rebuilt, 45 ms of it in link resolution. Two earlier runs on other maps read 6.63 and 5.41 ms (the design doc cites
  those; `evidence/A3_perf_timed_200_links_40000_basins.json` is the 5.41 ms one).
- A4: two 3x3 pits, 4 notches deep, 360,000 vs 90,000 dL, joined by two reels on one pipe run (Intake / Outflow). The reel's
  own inspect pane reads "Levelling: flowing (no pump; the higher water runs to the lower)." from tick 250 and "Levelling:
  level." at tick 4750, the pits at 225,234 / 224,766 dL (52 dL per square apart, under 1 cm), total conserved. Topping one
  pit back up made it flow again cycle by cycle and re-level (`A4_A5_levels_over_time.png`, middle panel). Save/reload
  mid-flow replays exactly; roles swapped or both Intake still level, Capped stops it. Two more rigs
  (`A4_mixed_rigs_surfaces.png`): a 3x3 pit 3 m deep against a 5x5 pit 1 m deep levels to equal SURFACES (-0.36 / -0.37 m
  by the mouse-over depth text) with very different water per square (52,703 vs 12,626 dL), total 790,000 dL before and
  after; and a natural 5x5 shallow pond at 90% runs down into a 3x3 pit 2 m deep until both stand at -0.47 m, where pond
  loss plus the pond's own natural refill (an unlinked control pond, +389 L over the run) equals the pit's gain to 0.0 L.
- A5: water F=4 vs oil (RM_Fluid_Oil) F=1 on the same rig: 0 moves over 1,500 ticks, both pits' dL unchanged, both reels'
  panes read "Levelling: stopped, different liquids never mix." (the oil pit is dark in the desktop capture).

## What I changed this round
- The reel's inspect pane contradicted itself ("Intake needs a working pump on this network." above "Levelling: flowing (no
  pump ...)"; the outflow said "Nothing drains here ..."), carried the "(taking water in needs a pump: set this end to Intake)"
  hint on ends levelling was filling, and the extra lines pushed the Levelling line below the pane's fold. An end in a
  levelling link now drops those lines; a lip end that levelling draws through reads "lying at the water's edge"; and until
  a levelling cycle has seen the network since its pipes or hoses last changed (after a load, after laying a hose) an open
  end reads "Levelling: checked on the next cycle." and makes no pump claim. A dry-ground control rig in the mixed run shows
  that line settles to "Intake needs a working pump" after one cycle (`dryRigVerdict` in the mixed-rig json).
- walk_gaps_proof PONDS_* require what the player reads ("flowing" then "level"; "different liquids never mix" as inspect
  text) and A5 uses RM_Fluid_Oil, as the line says.
- pipe_levelling_perf_proof: driver_stamp, abandoned at 15 s, made bridge calls mid-run and desynced the socket; now waited
  on up to the per-call cap or the run is refused (lesson filed).

## What I'm least sure about
- A3's bars are provisional (no owner number). Steady cycles are 5-7 ms per 250 ticks at 200 links, a stress case far past an
  ordinary base; the first cycle after the network changes costs ~35-90 ms, a one-off hitch a player could notice when
  building or cutting a pipe on a very large levelling network.
- The ledger moved the item to done itself when the last owed criterion passed (rimflow verify at 60bbc5b684), before this
  DONE.md and the judge; I did not run a close.
- The stills cannot show water moving; the charts are the motion record (the A4 proof chart's line from tick 0 to 3000 is
  drawn between two readings; the other panels read every cycle).

## What I did not test
- A river or a limitless sea end live (offline A1 covers sea to brim and dry receiver); a pump switched on mid-flow (owner
  ruling: off while pumping, resumes after); a third open end; freezing; rain filling a pit mid-link; deconstructing a reel
  mid-flow; the owner's full mod list (all runs: FlowWorks tier, all five DLC, SteveDesktop game A).

## Landing
All code landed on origin/main by 7eff26d38e. This final evidence is committed in this clone but not published: ./publish
pulls other seats' commits, which re-dates project files and would make the evidence read as older than the project again.
The wrap-up publishes it.
