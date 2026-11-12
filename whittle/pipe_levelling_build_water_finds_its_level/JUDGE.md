# Judge: PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL

Judged 2026-11-12 by a blind judge on the STEVEDESKTOP FWLIVE clone (repo HEAD c7eea3291b, dirty working tree). I read
STATEMENT.md, NOTES.md, the item's full criteria (`infrastructure/state/items/closed/PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL.md`,
because STATEMENT.md cuts every line short), every file in `evidence/`, and the parts of `LevellingChecks.cs` and
`northstar/walk_gaps_proof.py` that the verdicts depend on. I did not read DONE.md or BROADEN.md.
I opened both charts, two desktop captures (A4 refilled-flowing, A5 no-mix) and two inspect panes (A4 level, A5 outflow).
I re-ran the offline selftest myself:
`selftest_flowworks_stock.py --only 'LEVELLING_*'` gave 11/11 ok, exit 0. Output:
`D:\ClaudeWork\rimmandrake\judge_levelling\selftest_run.txt`.

## A1 (L0): true
I re-ran the selftest and all 11 LEVELLING_* cases pass (the evidence copy shows 17/17, which includes 6 Outflow and HoseText
cases). I read `LevellingChecks.cs` to see what it checks. `Drive()` runs these checks on every cycle:
- the finite total plus the limitless net stays exactly constant;
- energy never rises;
- in a two-body scene the gap never grows and never changes sign;
- no link reverses;
- liquids never move into a different liquid.

Each case the criterion names exists by name and passes: 1-square vs 100-square, ten parallel links, same-body loop, siphon,
exposed intake, water/oil, dry receiver, sea to brim, and the 300-scene fuzz (300/300 reached a fixed point).

I could not check the two shas the line names (baa270b9e8+0ac23150a2) because git was off-limits. The tests pass on the
current tree, which is the stronger result.

## A2 (L0): false
The budget case is as stated in the source: 200 bodies, the first 40 of them `Flat(40000, 8)`, 199 chain links plus 201
random links (400 in all), and a budget of 64 links per cycle. Its cost is small: 84.5 µs per cycle in the evidence copy and
77.5 µs in my run.

The line also names a written feasibility section, `### Levelling feasibility` in the design doc. The evidence copy,
`A2_feasibility_section.md`, matches the doc word for word. That section states a live result the evidence contradicts.
- **The section says:** "a water pit and a chemfuel pit joined the same way exchange nothing".
- **The evidence shows:** the A5 run used `RM_Fluid_Oil` (label "oil"). See `walk_gaps_proof.py` `OIL_FLUID`, the
  `A4_A5_levels_over_time.png` panel title, and `A4_A5_look_ponds.json`. No evidence file shows a chemfuel run.

So the write-up the owner would read misreports what was tested. Two smaller problems in the same section:
- It quotes the kernel as "89 µs (MEASURED by the selftest)". No file in the evidence shows 89 µs.
- Its "Live" paragraph covers only the equal-pit rig. It leaves out the rigs with unequal depth and area and the natural pond.

Fixing this is a text edit. It needs no new run.

## A3 (L1): true
`A3_perf_timed_200_links_40000_basins.json` records:
- **Setup:** a live run on a 325x325 map, with two basins of 125x320 squares each. Both are 40,000 squares dug and 40,000
  filled, with 0 fills refused.
- **Links:** 200 of 200 wanted, with 0 lay failures.
- **Timing:** `RM_Levelling.Tick` over 60 timed cycles: msAvg 5.41, msMax 33.8, 0.022 ms per tick.
- **Allocation:** 306 KB per cycle, gcs 0.

`A3_levelling_tick_breakdown.txt` covers 62 calls. It splits the time into walk, links, plan and moves, and gives the
largest cycle as 88 ms: 47 ms of link rebuild on the first cycle after the topology changed. `A3_perf_phases.json` shows the
200 rigs laid in five slices before the timed phase.

What makes it flattering:
- It ran on the 12-mod FlowWorks tier list, not the owner's full list.
- Edge sinks were switched off for the run.
- The colony was calmed, with storyteller off and threats 0.
- The 40,000-square basins are walked as two capped 20,000-square runs (walked=79,748).
- The 34-88 ms first-cycle hitch after a topology change is real and would show as a frame hitch.

The line asks only that tick time and allocations be recorded, and they are.

## A4 (L2): true
`A4_A5_walk_gaps_ponds.json`, row PONDS_HOSE_LEVEL (PASS), shows:
- **Start:** two 3x3 pools, 4 notches deep, holding 360,000 and 90,000 dL.
- **End:** 225,234 and 224,766 dL. The total is conserved at 450,000.
- **Gap:** 52 dL per square. A square is 2 m² (the mouse-over reads 6,000 L for 3 m), so 52 dL is about 0.26 cm, inside 1 cm.
- **Moves:** 18. They come from ProofLevelLink, which reads the same `RM_Levelling.Moves` counter that HoseNetProbe's
  `levelMoves` reports.
- **Reel text:** "Levelling: flowing (no pump; the higher water runs to the lower)." at tick 250, then "Levelling: level." at
  tick 4750.

The `lev_a4_level_pane.png` capture shows "Levelling: level." in the player's own pane. The `lev_a4_refilled_flowing`
capture shows the reel going back to "flowing" after a top-up, and `A4_A5_levels_over_time.png` shows it levelling again.

The headline rig is the easy case: identical pits on the same floor. `A4_mixed_rigs_depths_and_natural_pond.json` covers the
harder ones.
- **Rig M (a 3x3 pit with a 3 m hole against a 5x5 pit with a 1 m hole):** level at tick 2750 at -0.365 / -0.369 m. The total
  stays exactly 790,000 dL.
- **Rig N (a natural 5x5 pond against a 3x3 pit with a 2 m hole):** level at tick 5750, about 0.47 cm apart. Conservation
  closes exactly once an unlinked control pond's natural refill (+0.3887 stock) is counted. That is an honest control.

Caveats:
- The A4 chart draws a straight line from tick 0 to 3000 because the proof keeps only the last 8 cycles. The chart labels this.
- The desktop stills cannot show the levels: both pits render the same blue, so the pane text carries the evidence.
- The mixed-rig JSON has no manifest, mod hash or wall-clock stamp, so I cannot tie it to a build.

## A5 (L2): true
Row PONDS_DIFFERENT_LIQUIDS_NO_MIX (PASS) shows a water pit at 360,000 dL linked to an oil pit at 90,000 dL. Over 6 cycles
(1,500 ticks):
- both volumes are unchanged;
- moves are 0;
- the link was formed (linked=True, coupling 1/1 from each reel), so this is not an idle rig;
- both reels' inspect panes read "Levelling: stopped, different liquids never mix.", which the desktop and pane captures
  show.

The water was set higher than the oil, so a leak would have shown within the first cycle at the 10,000 dL per cycle rate.

## Side observation (not a statement line)
In the mixed-rig JSON, both freshly laid reels read "Role: Intake. Intake needs a working pump on this network." at tick 0,
before the first levelling cycle (link state None). On a passive levelling rig this tells the player a pump is needed when
none is. I cannot tell from the evidence whether that run used the build in which this text was said to be fixed.

## What would turn this to yes
- Correct the `### Levelling feasibility` section, and its evidence copy, to say oil (`RM_Fluid_Oil`), not chemfuel.
- Quote the kernel time that the evidence actually shows, or attach the run that measured 89 µs.

would show: no
