# GSS Ralph: where the last pass got to

**Merge landed (pass 10): `origin/main` is merged into `ralph/gss` and on Steve (`da048b95aa`), for the Conductor's game B. Stop my game only through `ralph/steve.sh`, by pid. Game B's bridge is 5175, mine 5174: leave B alone.**

Pass 9. Retired on the context guard. Not done, so no `DONE.md`. **New from the owner: a broaden call to GPT is required before `DONE.md` (Phone for help in `ralph/PROMPT.md`). Not used yet.** Owner ruled by card: cords under grass stay, "grass hides the cord"; taken out of `QUESTIONS.md`.

Final DLL: selftest 1149/1149, live `core` 47/47 PASS (`proof_all_20261107T125417.json` on Steve; not recorded). Offline 9/9 and the offline gate were last run one commit before the final one, which added only machine strays. The whole proof was not run on this DLL. **Those rows passing did not see what I fixed: M2c read clean while 55 of 70 strands had a sharp corner.**

## The new tool: use it first
**The shape lab.** Cord shape needs no game now. `B.probe("worlddump:NAME")` writes a live map's cord world to `$RM_GAME_USERDATA/GssWorlds/NAME.json`. Then, here:
```
python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --lab Transient/lab/NAME.json Transient/lab/NAME.out.json
python3 ralph/live/lab_render.py Transient/lab/NAME.json Transient/lab/NAME.out.json OUT.png x,z,w,h --ppc 100 [--no-marks]
python3 ralph/live/lab_classify.py Transient/lab/NAME.json Transient/lab/NAME.out.json
```
Same builder as the game, a minute a turn, and the audit matched the live `shapeaudit` probe within 1 corner. `Transient/lab/modern1.json` is a played Modern colony. Red rings are sharp corners, magenta squares are rods. Copy a dump to `D:\ClaudeWork\...` on Steve to `fetch` it. Also new: probes `shapeaudit`, `strandsnear:x,z,r`; `lived_in.py rect TAG name:x,z,w,h`.

## What I found and fixed
- **"Open bug" of pass 8, the second run's battery with no cord: not a mod bug.** `lived_in.py` cleared a 2x2 of Buildings for a battery, which took the conduit cell beside it. The mod drew the truth. Fixed the script; the edge exists now.
- **Polish (`CordShape.Polish`, inside `Unfold`):** a 0.1-cell blur plus a local retract of needles on every laid strand, ends left point for point. Takes the settle's sawtooth and the corners off; the lay and the loops stay. Polish runs before fold rounding, because the other order made 150 folds.
- **Strip beside a machine:** its lead is now one short nub with a slight belly (`StripNub`), not a flat hook round the strip's end. This is the judge's "two short cords to one machine" at close range. `p9c_Modern_work` against `p9a_Modern_work`.
- **Needle at a socket:** a cord arriving against its socket had both Bézier handles on one line. `Approach` now swings out in a U when given `roomy`, strips only. Shared file, so the FlowWorks DLL is rebuilt with it; hoses never pass `roomy`, so hoses are unchanged.
- **Sixth cause of "multiple cables", in `QUESTIONS.md`:** a through cord's slack ran under a pass-through machine and back out, reading as extra cables into it. `CordShape.MachineStrays`, re-lay in `SprawlOnce`, selftest with a planted pass and a route control. Smithy has one cord: `p9e_Scrapper_work` against `p9d_Scrapper_work`. Unlike doors, there is no live probe of this count yet.
- Lamp on a mast drop: looked at it. `LooseDrop` is not a rod (`p9a_Modern_drop`). Its last half cell hides under grass, which the owner's ruling covers.
- Spark: opened `p8m_wire_sheet` and `p8m_floor_sheet` myself. Sparks ride the moving tips. No change.

## Do next, in order
1. Sixth cause is fixed, see below. Check the battery corners in a Modern `strips` frame, which I did not re-open after the fix.
2. **Barb at narrow one-cell devices** (heater, mast base: `p9c_Modern_hut` at 690,655 and 375,255): the cord arrives diagonal and the plug art sits square, out in the open, because the art is narrower than its cell. Don't change the arrival: the owner ruled for diagonals and `slideunder` pins it (I tried, 9 rows went red). Try the plug decal following the cord, or art insets in `CordWorldAdapter.InsetsSNEW`.
3. Crossarm squiggle: still a visible zigzag across the insulators (crop of `p9a_Modern_work`). The judge's item, and pass 8's fix is not enough. Read the drip loop code in `AerialMath`.
4. Audit still reads 34-37 of 70 strands with a corner, mostly tiny spur knots (`SpliceLoop`) and tight bends in a short cord's pinned ends. Decide by looking in the lab whether each is real or tighten the audit. A terminal strand pins 1.0 cell at both ends (`LimpSkip` takes one number), so its far end gets less polish: split it per end. Then make the audit a proof row.
5. **Junction before and after, still not started, and the judge asked for it.** `ralph/live/old_dll/before_903ba19f.dll` is the pre-pass-1 build. Game down, copy it over `Mods/GimmeSomeSlack/Assemblies/` on Steve, `up`, `colony_scene.py --build --fresh-map --shots pre`, then `deploy` to restore. Check the old DLL takes the probes that script calls. `ralph/live/junction_ba.py` makes the sheets. Do this after the junction changes settle.
6. Other looks on the final DLL: `bash ralph/live/four_looks.sh TAG Scrapper Industrial Futuristic`. This pass saw only Modern and one Scrapper colony.
7. Things no pass has looked at, for the four ways: the build menu, style picker, mast gizmos and Wire down alert as a player meets them; a mountain base, snow and water maps; telemetry during a rewire (`worst` is a list and `attr` a table in `JawaBench/tps`; the `tps_*.jsonl` sample has them, and a paused sample reads empty, which is not a measurement). `rewire_cost.py` is still partial. `sc_walk`, `sc_true_to_grid` controls unbuilt.
8. Rock-room socket tip (`colony_scene.py --hard`), Scrapper arm tails.

## Open items
Triage from pass 7 stands; not redone. Already fixed: BATCHED_LINK, COLOUR_SEED, CORD_AUDIT, CORD_SWAY_TAME, FRESH_BUILD_ORACLE, FUZZ_ONLY, MULTILINK, POWER_THEFT (small gap: the theft window's owner is not saved), RESTRING_FIX, STRIP_LED, STYLED_WINNER. False: CORD_ADAPTER_NO_LAMP. Conductor's paperwork in `infrastructure/state/`: SWAY_PROVE, RESTRING_PROVE, RECOLOR_CHECK. Needs a live run: SWITCHES_PROVE, WATER_STUB (fw_gss list). Really open: `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`; `northstar/scene_rows.py` covers 9 of the 23 scenes by name.

## Traps I paid for
- `game_gate.py` matches the playtest runner's and the proof script's filenames anywhere in a local command, including a `grep`. Use Read for those files.
- `_Shared/SlackGeometry` compiles into FlowWorks too. Commit source, then `winbuild` both, commit both DLLs and `.srchash`.
- `selftest_gimmesomeslack.py` has no `--help`: it runs the whole build.
- Images are cheap one at a time but add up: this pass hit the soft context line about 40 images and 8 big source reads in. Send source reading to a subagent; the lab lets you look at less.
- Fetch shots one file at a time from `D:\ClaudeWork\...\shots` on Steve.

## Steve
No fault: `bad_cpus=[]` on every read, last at 2.88 h. No dead game, no dropped ssh, no reboot. Game restarted only for deploys, bridge up in 16-22 s. No surprising result needed a restart check.

## North star, judged hard
Modern and one Scrapper colony on this code; Industrial and Futuristic last seen in pass 7.
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true
- break_live_and_dead_ends_differ: true
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: true
- never_cord_across_impassable: true
