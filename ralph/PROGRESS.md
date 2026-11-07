# GSS Ralph: where the last pass got to

**Merge landed (pass 10): `origin/main` is merged into `ralph/gss`. Stop my game only through `ralph/steve.sh` (it stops by pid). Game B's bridge is 5175, mine 5174: leave B alone.**

Pass 11. Retired on the context guard (about 270k). Not done, so no `DONE.md`. Self-tests 1155/1155. No live proof run on this DLL.

## Settled this pass
- **Sparks follow the moving end: the owner certified it by eye** (relayed 2026-11-07 14:30: "I can certify by eye that the sparks now follow the moving broken wires. Good job!"). Don't re-prove it. If a later DLL touches `CordMotion`, `TipSparks`, `DrawFallenTails`/`DrawFallenGlow` or `ThrowTipSpark`, say so here so his look can be repeated. My frames, for the record: `p11m_floor_ride.png` and `p11m_wire_*` in the shots folder (12 frames each, the spark on the tip in every one; `spark_measure.py`: spark travel 0.41-0.42 cell against tip travel 0.41-0.47).
- **Open items triaged against the code** (subagent, read-only): 11 of 17 fixed in code, `CORD_ADAPTER_FIX_NO_LAMP_GEOMETRY` false (by design: lamps keep the centroid look he walked), the rest proof-only or paperwork under `infrastructure/state/` (not mine). Two harness gaps fixed here: M15e now names `RM_RestringSpan`, PT_A3_goodwill_day names `theftGoodwill`, so `mod_completion` can credit them. `plan.md`'s "Modern junctions draw the long power strip" is BUILT (`CordBuilder.cs` PoseStrip); the cord-shape instrument is BUILT (`CordShape.Table`, probe `shapetable`). Scenes: 10 of 23 built with a control, 9 without a control, 4 missing (rewire_cost, four_looks, gravship, walk): `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL` is the one really open item.

## Fixed this pass
- **The rod through a doorway** (`never_taut_straight_cord`). Cause: a cord was held to its planned line 0.55 cell either side of the door cell, then let go with a jump to half its bend, so 2-4 cells ran dead straight through every door. Now (`LayParams.SoftPins`, GSS only, cords of 2.5 cells and up) the hold is the door cell plus 0.15, the release is a smoothstep over 0.7 cell, and a flat stretch running off a door's hold is filled from 0.8 cell (was 2). Loops still root 0.55+ clear of doors (they use the old ramp), so the doorway ring count did not rise. Measured offline on the 138-doorway matrix (`ralph/live/lab_doorrod.py IN OUT`, new): straight run through a door max 4.8 -> 2.4 cells, over 2.5 cells 6 -> 0; the remaining 2.2-2.4 are a terminal one cell past a door (nothing to bend). `lab_doors.py read`: plain runs through a door still 2 lines everywhere; along_branch/outside_tee a little better. FlowWorks rebuilt, hoses unchanged (SoftPins off). Commit 92c832da6d. **Seen in the game**: `junction_saves.py now` on this DLL (four fresh generated maps, played ~1800 ticks): the house's bottom door in every look now bends through or just past the door, no rod (`p11_door_now_sheet.png`, against `judge_p10a/door_bottom.png`).
- **Fallen wires beside a rock or wall** (`AerialMath.LayFallen`): when a bend would cross an unwalkable cell, the wire now tries the same bends mirrored before halving its slack, so it stays loose instead of going rod-straight. New self-test row with a can-fail: beside a wall, 31/40 seeds still bend 0.6+ cell off their line (halving only: 16/40; bar 28). Built, **not deployed** (Steve still runs 92c832da6d's DLL): deploy and look at a cut span beside rocks.
- Trap found on the way: a soft pin on a 1.4-cell hop frees a bump that the junction's arm fitting (`AttachEnd`) then cuts off, leaving a straight 0.9 stub and a too-short whip tail (selftest `whip: tails outside 0.7-1.15`). Hence the 2.5-cell floor on soft pins.

## Do next, in order
1. `deploy` + `up` (the fallen-wire mirror is built but not on Steve).
2. **Junction before and after**, owed to the owner. The saves exist: `gss_ba_{Modern,Scrapper,Industrial,Futuristic}` on Steve, made on DLL 92c832da6d, with `ba_now_*_{house,yard,work,strips}` shots (fetched here; `ralph/live/ba_state.json` on Steve holds the origins). Game down, copy `ralph/live/old_dll/before_903ba19f.dll` over `Mods/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll` on Steve (check `old_dll/` reached Steve's clone: it is untracked here), `up`, `junction_saves.py pre`, `deploy` + `up` to restore, then `python3 ralph/live/junction_ba.py <shots> ba_pre ba_now ba_sheet`.
3. **`dense_grid_reads_as_tangle` is false**: load each `gss_ba_*` save and shoot the `dense` frame (lived_in FRAMES, 24x12 cells; `lived_in.py rect` or `shots TAG --frames dense` with that save's origin) at play zoom, and look hard. The p10a judge: the Modern heap shows no strips, Industrial/Futuristic heaps read as straight spokes (a star).
4. **Scrapper vs Industrial cords**: `Strand_Jawa` (mean rgb 39,32,27) and Industrial's `Strand_BlackRubber` (32,30,29) are nearly the same texture; the other two Industrial kinds are ribbed. Only the fittings tell those looks apart. My idea: give Scrapper two or three scavenged-junk strand variants (rusty brown, faded olive with tape patches) as ADDED variants, leaving `Strand_Jawa` as one of them; the variant plumbing is `ConduitStyles` (`IndustrialKinds`, count per look) and `CordMaterials.StrandPathOf`.
5. Futuristic fallen wires: on the ground they lie loose (loops, hooks; crop of `p10a_Futuristic_cutspan` 330-900,250-600). What reads as a rod is the hanging drop from the crossarm (`AerialMath.LayFallen`, s < s0): a straight line straight down. Judge on fresh shots before changing anything. Also `LayFallen` halves its slack whole when one bend would hit an unwalkable cell; mirroring the bends first would keep cords loose beside rocks.
6. GPT broaden leads 4, 6, 7 from pass 10 (outage at play zoom without knowing where; a mast failure with colonists repairing; settings mid-save). Then the full proof once (`proof_all.py --live`, not recorded). A broaden call was made in pass 10, so DONE.md is allowed once its leads are acted on.
7. Still open from pass 9: the crossarm zigzag (`AerialMath.SpanCurveDrip`), the plug barb at one-cell devices, spur knots in the audit, and cords at night on a dark floor.

## Traps I paid for
- `game_gate.py` refuses any local command that names `rw_game.sh`, even a `grep`.
- `_Shared/SlackGeometry` compiles into FlowWorks: rebuild both and commit both DLLs.
- The self-test log from `dotnet.exe` has bytes that make plain `grep` silent: use `grep -a`.
- To pass an env var into the Windows `dotnet.exe` from WSL: `WSLENV=NAME NAME=1 python3 ...`.
- The shape lab: `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --lab Transient/lab/doors/in OUTDIR` (138 worlds, ~10 s). `lab_render.py WORLD LAID OUT x,z,w,h` draws one; `lab_audit_sum.py OUTDIR` sums the shape audit. The audit's "rod" metric over-counts (it skips points that come back near the start), so don't chase its totals.
- `steve.sh fetch` one file at a time is slow: `ralph/live/fetch_shots.sh PREFIX` tars a prefix in one go; `ralph/live/sheet.py` makes a contact sheet.

## Steve
`bad_cpus=[]` at 4.21 h uptime. No dead game, no dropped ssh, no reboot. The game was restarted once, for the deploy; the bridge came up in 23 s. Four fresh maps in a row in `junction_saves.py now` without a fault.

## North star, judged hard
Seen on the pass-10 DLL (p10a colony, p10h doorway), and the doors on this pass's DLL (`ba_now_*`).
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: false (seen only far off; Industrial and Futuristic heaps read as spokes, the Modern heap shows no strips)
- break_live_and_dead_ends_differ: true
- overhead_span_above_everything: unseen for buildings (true for pawns, `p10a_Futuristic_spanpawn`)
- downed_span_lies_on_ground: false for Futuristic (the crossarm drops read as rods), true for the other three
- four_styles_distinguishable: false (Scrapper and Industrial cords are the same dark texture; only the fittings differ)
- one_run_one_style: true
- never_taut_straight_cord: true at the doors that were rods (`p11_door_now_sheet.png`, all four looks); not yet re-judged across a whole colony on this DLL
- never_cord_across_impassable: true
