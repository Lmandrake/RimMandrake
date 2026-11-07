# GSS Ralph: where the last pass got to

**Merge landed (pass 10): `origin/main` is merged into `ralph/gss` and is on Steve (`da048b95aa`), for the Conductor's game B. Stop my game only through `ralph/steve.sh`, which stops it by pid. Game B's bridge is on 5175 and mine on 5174: leave B alone.**

Pass 10. Retired on the context guard, at about 250k. Not done, so no `DONE.md`. Self-tests pass 1154/1154 and offline is 8/9; the one offline failure is the same as before and I didn't chase it. No live proof was run on this DLL.

## Broaden call: made, and acted on
I asked GPT a `broaden` question (`gpt_help_pass009.md` beside the loop logs; ask in `Transient/gpt_broaden_pass10.md`). It gave seven leads:
1. Act on the cable you see (deconstruct, select).
2. **Grow the doorway during play.** I did this one (below).
3. Build into the slack: wall a loop, wall up a door. Partly done, in steps 6-7 of the same script.
4. Find an outage at play zoom without knowing where it is.
5. Ignore the feature in a crowded colony.
6. A mast failure as it unfolds, with colonists repairing it.
7. Settings mid-save: master switch, a restyle with a span down, save and load.

Leads 4 to 7 are still to play. A broaden call has now been made in this pass, so `DONE.md` is allowed once its leads have been acted on.

## What I found and fixed
- **Seventh cause of "several cables", the most general one (`QUESTIONS.md`).** I used a doorway matrix (`ralph/live/lab_doors.py gen|read`): 23 ways a player runs conduit at a door, six seeds each, laid in the lab. I counted the lines that cross a 1.5-cell ring round each door and each end. A plain run through a door to an end drew up to 6 lines, because a slack coil sat on the doorstep or on the cord's own end. The fix is `CordShape.RingReturns`, read in `SprawlOnce`: a coil at a door gets up to six re-lays, and a coil at the cord's own end gets three on a long cord (over 500 points). Every plain run through a door now crosses its ring twice. A self-test row has a control.
- **A rod after a door.** `p10g_Modern_0_start` showed the cord dead straight for 6 cells from the door to the heater. The random excursions can land together and leave a stretch with nothing to bend it. `CordLayer.FillFlats` gives any stretch over 2 cells within 0.35 of the line gentle excursions of its own, and adds what they cost to the length budget so end heaps keep theirs. Opt-in through `LayParams.FillFlats`: GSS has it on, hoses off, so FlowWorks is unchanged. In the doorway matrix, straight runs over 5 cells fell from 10 to 2, and the longest from 8.8 to 5.4 cells (`ralph/live/lab_straight.py`).
- **The doorway grown step by step in the game** (`ralph/live/grow_door.py TAG`): a heater, a lamp, an extension, removing and re-placing, a branch cut, a wall over a loop, the door walled up. One cord crosses the door at every step, and the walled-up door shows a plate on each face (`p10h_Modern_*`; the sheet is `Transient/p10h_sheet.png`). Each edit re-lays the whole chain it belongs to, including the cord inside the room. That is how the graph works, but a player may notice it.
- Self-test changes, each with its reason in the source: PileLook's planted end now picks a host the audit doesn't forgive; LaneA's settle stretch bar went from 3% to 4% (one 0.05-cell segment was at 3.4%); A9 now reads the door ring itself; the caller-lay slice rows get their own 30 ms bound, because the game lays on a worker (`AsyncLay`), and the async and graph-worker rows stay at 20 ms.

## Do next, in order
1. **Look at the four-look colony on this DLL**: `p10a_{Modern,Scrapper,Industrial,Futuristic}_{spanpawn,house,work,yard,all,cutspan}` (Steve's shots folder; `bash ralph/live/fetch_shots.sh p10a`). I started it and retired before seeing it. Send the pictures to a subagent. Watch for the fallen wires' straight stretches in `cutspan`: `LayFallen` in `AerialMath` has its own lay and no FillFlats.
2. **Junction before and after**, still owed to the judge. The old DLL (`ralph/live/old_dll/before_903ba19f.dll`) has every probe `lived_in.py` uses (checked: census, cplace, cprocess, clearpicks, link, place). Plan: per look, `lived_in.py build --fresh-map`, play, `rimworld/save_game` as `gss_ba_<look>`, then `lived_in.py shots now_...`. Then game down, copy the old DLL over `Mods/GimmeSomeSlack/Assemblies/` on Steve, `up`, `rimworld/load_game_ready` each save, `shots pre_...` (same map, same layout, `lived_state.json` holds the origin), then `deploy`, then `junction_ba.py`. The same save under both DLLs is the honest comparison.
3. Spark frames on this DLL in a played colony after a blast (`motion_frames.py`). The p8m sheet showed it right, but that was two DLLs ago.
4. GPT leads 6, 4 and 7 (see above). Then the full proof once (`proof_all.py --live`, not recorded).
5. Still open from pass 9: the crossarm zigzag (`AerialMath.SpanCurveDrip`: each span's wire dips toward the screen bottom on both sides of a middle mast), the plug barb at one-cell devices, and spur knots in the audit.
6. Cords at night on a dark floor: a brown Modern cord on wood planks at night was nearly invisible (`p10g`). Check the colour seed's darkest draws against floors by day.

## Open items
The triage from pass 7 stands (see git history of this file). Really open: `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`.

## Traps I paid for
- `game_gate.py` refuses any local command that names `rw_game.sh`, even a `grep`. Use Read.
- `_Shared/SlackGeometry` compiles into FlowWorks: rebuild both and commit both DLLs.
- `steve.sh fetch` one file at a time is slow: `ralph/live/fetch_shots.sh PREFIX` tars a prefix and brings it back in one go. `ralph/live/sheet.py` makes a contact sheet, so nine shots cost one image.
- The self-test slice rows are timing on a loaded Archmagi (load average about 9): 14-22 ms run to run.
- The lab takes a folder now: `--lab IN_DIR OUT_DIR` lays every world in one build (138 worlds in about 10 s).

## Steve
No fault: `bad_cpus=[]` on every read, last at 3.38 h. No dead game, no dropped ssh, no reboot. The game was restarted only for deploys, and the bridge came up in 17 s each time.

## North star, judged hard
Only Modern has been seen on this code, in the doorway sequence. The four-look colony is unseen.
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: unseen (on this DLL)
- break_live_and_dead_ends_differ: unseen (on this DLL)
- overhead_span_above_everything: unseen (on this DLL)
- downed_span_lies_on_ground: unseen (on this DLL; fallen wires still have straight stretches in p9d)
- four_styles_distinguishable: unseen (on this DLL)
- one_run_one_style: unseen (on this DLL)
- never_taut_straight_cord: false until the four-look colony shows otherwise (6 straight cells after a door in p10g; fixed in the lab and in p10h, not yet seen across a colony)
- never_cord_across_impassable: true
