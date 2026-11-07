# GSS Ralph: where the last pass got to

Pass 6. Retired on the context guard, with one live lead open (first item below). Selftest 1119/1119. **The proof has NOT been run on this code**: expect red rows that read old geometry (B3, M15, M20, shock contacts, anything counting battery or generator hookups).

## Look at this first: a real cut showed no ends
`lived_in.py blast` destroyed conduit at local (26,8..10) (rubble read on the cells; conduit count went 107 to 104). Both sides are 2-cell spurs off a T. The probes then read `ends` empty, live and dead floor ends both 0, whipTails 0, even after a forced `rebuild`. So on this map a cut made in play drew no spark and no limp end, as far as the probes say. **Not explained, and the cause is not known to be the mod.** The save was not kept; rebuild with the commands below. Check first: are short spurs pruned or merged in the graph (`CordGraph.cs:656-660` makes terminals), does a longer spur give ends, and what does a tight shot of the gap show? Until this is explained `break_live_and_dead_ends_differ` stays false. It also blocked the floor half of the motion evidence, because `motion_frames.py` found no live floor end here.

## What changed
- **Fallen wires** (`AerialMath.LayFallen`, `AddCoil`): uneven bends, a wander, a hook at the end, uneven single or double coils, each wire falling to its own side with a rounder turn at touchdown. A tip no longer lands exactly on the break. Offline look: `ralph/live/fallen_preview.py` draws the SelfTest exe's `--fallen-dump` JSON, no game needed.
- **Writhe** (`CordMotion`): the bend now runs out along the tail, so it snakes. Tail and swing are longer (floor 0.95/0.24, wire 1.3/0.3). `WhipRoom` stops an end swinging onto a wall.
- **One cord per run into a battery or generator** (`HookupPick.PickCarrier`, new selftests). Biggest real find: 7 cords into one solar panel, the owner's complaint again. In `ralph/QUESTIONS.md`.
- Selftest bars I moved to fit, so re-judge them by eye: whip length 0.7-1.15, tip within 2.6 of the break, tips 0.5 apart, cable length under 2.4x, deviation at least 0.5.

## Seen, Modern unless stated (shots folder, `p6*`)
- `p6L_*`: temperate forest, before the hookup fix. `p6M_*` and `p6N_*`: tropical rainforest, after it, played about 5,500 ticks at speed, then a real explosion (`p6N`). No staged ground. Zones and stockpile items were sent, but I did not open the `stock` or `work` shots. Colonists were free, none downed.
- `p6N_Modern_cutspan`: a blast-cut span reads as loose cut wires, live side sparking, dead side not. Best evidence yet for `downed_span_lies_on_ground`.
- `p6a_fallen_sheet`: all four looks, one build BEFORE the rounder touchdown, which showed a pointed corner there. **The other three looks are unseen on the final shape.**
- `p6N_Modern_yard`: one cord at panels and batteries. My own colony plan leaves the third solar panel unconnected: that is the harness, give it conduit.
- Grass draws over cords as dashes. Left as is, question filed.
- Spark: `p6m_wire_00..11` and `p6m_wire_sheet` were captured, and the probe's wire tips move between frames, by up to about 0.3 cell in the rows I read. **I never opened the sheet.** Look at it before claiming anything. `motion_frames.py` now parks the camera on the end; its zoom call is unproved for the floor case.

## Do next, in order
1. The no-ends lead above.
2. Fallen and house shots in all four looks on the final DLL. `colony_scene.py --build --fresh-map --shots TAG` takes about 5 min. Steve's save `GSS_colony_p6` holds that colony from an earlier build of this pass, which saves the rebuild.
3. Floor-end motion frames, then a GIF or sheet for the owner.
4. Run the proof by block, then core, and fix rows that read old geometry.
5. Junction before and after: **not started**. Plan: build the DLL from a worktree at `903ba19f5d` (last commit before pass 1), shoot the same colony, pair the shots. Check that commit's probes can run `colony_scene.py` first.
6. `lived_in.py` in the other three looks, plus a pawn under a span (still no shot of one).
7. Judge's smaller items: Modern rock sawtooth, sharp kinks, plug hook tails, crossarm squiggles, rock-room socket tip, knot under the mast (recheck). Open items and scenes: unchecked this pass.

Colony run on Steve: `python.exe ralph/live/lived_in.py build --look Modern --fresh-map`, then `play --ticks 4000`, `shots TAG --frames all,house,yard,work,stock`, `blast`. Fetch `D:\ClaudeWork\rimmandrake\ralph_gss\shots` from Steve.

## Steve
No fault this pass: `bad_cpus=[]` on every status read, last at 0.8 h, and the machine was still running at about 55 min. That is far past the 13 min, with turbo off, on one boot. No dead game or dropped ssh. No reboots; game restarted on purpose for deploys. Bridge up in 16-22 s on the small list.

Gate note: `game_gate.py` refuses a plain grep naming the proof script or the bridge's skill folder. It also refuses a whole command while the context guard fires, so a heredoc in that command is not written: rerun it.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true
- break_live_and_dead_ends_differ: false
- overhead_span_above_everything: unseen
- downed_span_lies_on_ground: unseen
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: unseen
- never_cord_across_impassable: true
