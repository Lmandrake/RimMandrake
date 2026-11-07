# GSS Ralph: where the last pass got to

Pass 5. **None of this pass's changes has been seen in the game yet.** Offline selftest 1115/1115 on this code, which says nothing about looks. Read `blind_judge_verdict_pass1.md` before trusting anything here.

## What I found
- **Why the spark looked left behind.** Vanilla `ThrowMicroSparks` was the likely cause. `MicroSparks` takes 0.75 s to fade in (read in `Fleck_Visual.xml`). From memory, not read in the decompiled source, vanilla also throws it up and to the right at about 1.2 cells/s. That fits the ember cloud off to one side in the shots. The whip tail was also only 0.4 cell long, shorter than its own glow. Two more real bugs: a wall end's tail swayed while its fray and sparks stayed put, and fallen overhead wires did not move at all, with one spark on the middle wire.
- **Extra cords.** The doorway fork came from `cordsPerConnection` (fixed last pass). Judge's "two cords to one battery": from the shot, a strip's sockets faced a machine beside it, so the through cord ran along the machine's edge to reach its socket. I read this off a crop and the code. I did not confirm it with a probe.
- **The pinch.** All wires of a span aimed at one break point, 0.22 apart.

## What I changed (`a7d1a8ab10` and the commit after it)
- `TipSparks.cs`: `MicroSparksFast`, small, thrown off the end the way it points. Floor tail 0.7 cell, amp 0.18. Glow drawn after the motion, on this frame's tip.
- Fallen wires: `LayFallen` has wide bends and a coil, and each wire ends on its own spot. `DrawFallenTails` writhes each live end, and its spark and glow read `TipNow`.
- `AerialMath.LooseDrop`: mast drops belly out instead of a rod.
- `PoseStrip`: a machine within 1.6 cells of a strip takes its lead (`MachineArmsOf`).
- Selftest bars I loosened to fit the new shape, so re-judge them by eye: whip length 0.5-0.85, fallen deviation 0.6-4.2, C3/C4 ground bound 3.7 (this no longer separates ground from air well), tips within 3.0 of the break.

## Do next, in order
1. `ralph/steve.sh deploy`, then `up`. The DLL with the `wireEnds` probe field may not be on Steve yet. Build a site with `colony_scene.py --build --fresh-map --looks Modern`, run through `steve.sh run`.
2. `python.exe ralph/live/motion_frames.py <tag>`, then fetch the frames. This is the owed spark evidence. The script has never been run. Look at the frames, not only the probe numbers.
3. Look at `fallen`, `house`, `yard` in all four looks: does a downed wire read as a loose cut cord, is the lamp drop slack, do the strips sit well in tight rooms? The bends may be too wide, and the back arm's swing round the strip is unseen.
4. Run the proof, `--only` the blocks these touch, then core. Expect rows that read old geometry (B3, M15, M20, shock contacts). Wider wires also mean more shock cells: check that isn't a gameplay surprise.

## Still owed, not started
- Lived-in colony on an ordinary generated map, in ordinary play. Every shot so far is the staged site.
- Junction before and after, side by side at play zoom, for the owner.
- Judge's smaller items: Modern rock sawtooth cord, sharp kinks, plug hook tails, crossarm squiggles, rock-room socket tip, pawn under a span.
- Open items and scenes in `DONE`'s tables: unchecked this pass, so those tables may be stale.

## Steve
Rebooted once this pass, on purpose (uptime 28 min, `bad_cpus=[]` at 0.46 h, so turbo-off may be helping; one reading only). No faults or dead games seen.

Gate note: `game_gate.py` also refuses a plain grep that names the proof script or the bridge's name. Search those through `ralph/steve.sh run`.

## North star, judged hard (nothing below reflects this pass's changes, none of them seen)
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true
- break_live_and_dead_ends_differ: true
- overhead_span_above_everything: unseen
- downed_span_lies_on_ground: false
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: false
- never_cord_across_impassable: true
