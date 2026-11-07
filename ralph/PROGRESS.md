# GSS Ralph: where the last pass got to

Pass 8. Retired on the context guard. Not done, so no `DONE.md`. Selftest 1139/1139 and offline gate 0 red, both on the final source.

**Whole proof on the final DLL: 150 rows, 150 PASS** (`proof_all_20261107T112409.json` on Steve), mode `partial`, `certifiable` False, because `--skip-offline` keeps the offline gate on this machine. Not recorded on the ledger, as told. The run before it, on the door-fix DLL, was 151 PASS and 3 FAIL. All three were rows reading old assumptions, and I corrected the rows, not the mod: MX_F42 (oracle now knows one cord per run into a carrier), M15d (required a fallen wire's tip on the break, the pinch the judge rejected), SL3 (compared exact lay across a load, which the owner struck on 2026-10-22; now compares which cords exist and reports relays: 1 of 19 edges relaid). **Those rows passing is not evidence for the open bug below; no row catches it.** The whole proof needs `design_spec.py --out /mnt/d/RimTest/data/scratch/gss_proof/scenes_design.json`, run on Steve with `python3`, because the offline gate writes the catalog on this machine only. Redo it after any change to `scenes.py`.

**Telemetry (owner's note, end of `ralph/PROMPT.md`), arrived as I retired, so barely used.** I opened the newest raw record under `JawaBench/tps` on Steve (157 files, this one 897 records). Its records have no top-level numeric `worst`, so my quick read found nothing about stalls, and that says nothing either way. Next pass: read `.claude/skills/telemetry/SKILL.md` first for the field layout, then read it during `rewire_cost.py`, which reads only slices and no frame time.

## What I found and fixed
- **Fifth cause of "cables out of a doorway": a cord's slack wandered under a door and back.** Seen at the kitchen door in `p7f_Modern_house`. Excursions and the settle treated doors as floor. `CordShape.DoorStrays`, re-lay in `CordBuilder.SprawlOnce`, probe `doorstrays`, selftest with a can-fail control (plain draw 7 strays, laid 0 in 77 strands). Live: 0 in 66 strands, door clean in `p8a_Modern_house`. In `QUESTIONS.md`. Modern only so far.
- `LayDiving` now goes through the same re-lay.
- **Spark, final DLL:** `p8m_wire_sheet`, `p8m_floor_sheet` and GIFs, opened and judged by eye: sparks stay on the moving tips in 12 of 12 frames. `spark_measure.py` window fixed to the spark nearest the tip. Floor: mean 0.11 cell from the tip. Wire: mean 0.21, worst 0.39, measuring the first wire only.
- **Whip zigzag:** none on `p7g_wire_sheet` or `p8m_wire_sheet`. It was on the older `p7e`.
- **Crossarm squiggle:** drip loops were a 6-sample sine with a sharp peak on the insulator. Now level at the insulator, 12 samples. `p8a_Modern_cutspan` looks calmer at normal zoom. **I did not re-crop it close up.**
- **Strip hooks:** a cord heading away from its socket turned in the last half cell. `Approach(..., roomy)` takes 1.2 cells to come round, `StripWrap` 0.45. **Built and deployed, not re-cropped close up, so unseen.**
- `lived_in.py` now has a dense block and a second run in another look (`p8a_Modern_dense`): the block reads as a real heap with strips in it.
- **`rewire_cost.py`, a partial sc_rewire_cost:** worst slice 5.6 ms against the 20 ms bar, nothing left pending. Gaps: the base reached 1209 conduit cells of the 1984 placed, not 2000. The two "wall beside" actions caused no rebuild, so they measured nothing. Slices only, no frame time, and no skipped-rebuild control. Don't count the scene as done.

## Do next, in order
1. **Open bug, unfixed: the second run's battery draws no cord** (`p8a_Modern_dense`, battery centre bottom). Conduit runs from cell (50,-8), touching the battery at (49,-9), with a lamp's hookup on the next cell (51,-8). The census has `junction|consumer` to the lamp and no battery edge at all, though `PickCarrier` should hook (50,-8). My guess, untested: a one-cell hop from a lamp's hookup to the battery gets dropped or pruned. Reproduce it offline in a selftest, then fix it. `second_probe.py` reads it live. Check that the lamps' no-power bolts there are only the empty battery; that run has no generator.
2. **Junction before and after: still not started**, and the judge asked for it. `ralph/live/old_dll/before_903ba19f.dll` is the pre-pass-1 build. Game down, copy it over `Mods/GimmeSomeSlack/Assemblies/` on Steve (`D:\SteamLibrary\steamapps\common\RimWorld\Mods`), `up`, `colony_scene.py --build --fresh-map --shots pre`, then `deploy` to restore. Check first that the old DLL takes the probes that script calls. `ralph/live/junction_ba.py` makes the side-by-side sheets.
3. Close crops of strips and crossarm on the final DLL. Then the other looks on it: `bash ralph/live/four_looks.sh TAG Scrapper Industrial Futuristic`.
4. Lamp-mast drop: the judge's taut rod. `LooseDrop` is built, but no shot this pass has a device on a drop (`lived_in.py` doesn't stage one; `colony_scene.py`'s `hut_lamp` does). Look before calling `never_taut_straight_cord` true.
5. Judge's smaller items, none looked at this pass: rock-room socket tip (`colony_scene.py --hard`), Scrapper arm tails, flat-topped excursions.
6. Finish `rewire_cost.py` (why only 1209 cells, walls that really touch a cord) or say plainly it's partial. `sc_walk` and the `sc_true_to_grid` controls are still unbuilt.

## Open items
Triage from pass 7 stands; I did not redo it. None is a bug a player sees. Already fixed: BATCHED_LINK, COLOUR_SEED, CORD_AUDIT, CORD_SWAY_TAME, FRESH_BUILD_ORACLE, FUZZ_ONLY, MULTILINK, POWER_THEFT (small gap: the theft window's owner is not saved), RESTRING_FIX, STRIP_LED, STYLED_WINNER. False: CORD_ADAPTER_NO_LAMP. Conductor's paperwork in `infrastructure/state/`: SWAY_PROVE, RESTRING_PROVE, RECOLOR_CHECK. Needs a live run: SWITCHES_PROVE, WATER_STUB (fw_gss list). Really open: `GSS_SCENES_BUILD_EVERY_CORD_A_FOIL`. A helper did that triage, and only `FacesGap` was re-checked by hand.

## Traps I paid for
- `game_gate.py` matches the proof script's filename anywhere in a local command, including a `grep`, a heredoc or a `git add`. Use Read and Edit for that file, and `git add -u` for its path.
- `_Shared/SlackGeometry` compiles into FlowWorks too. Touch it and FlowWorks' DLL must be rebuilt, or the pre-push guard refuses and `deploy` stops at the push. **Read deploy's first line:** the game can then come up on the old DLL. It cost me one colony.
- Commit the DLL and its `.srchash` together, built from committed source.
- Fetch shots one file at a time from `D:\ClaudeWork\...\shots` on Steve.
- `pending` and `builds` are on the `motion` probe, not `census`.

## Steve
No fault: `bad_cpus=[]` on every read, last at 1.21 h. No dead game, no dropped ssh, no reboot. Game restarted only for deploys, bridge up in 16-23 s. No surprising result needed a restart check.

## North star, judged hard
Only the Modern look was re-shot on this code. The other three were last seen in pass 7.
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true
- break_live_and_dead_ends_differ: true
- overhead_span_above_everything: true
- downed_span_lies_on_ground: true
- four_styles_distinguishable: true
- one_run_one_style: true
- never_taut_straight_cord: unseen
- never_cord_across_impassable: true
