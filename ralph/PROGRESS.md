# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 6 (2026-11-08, ~09:25-10:25Z): his story three more times; three things break it before a rescue can
Weather: 2 native Mono crashes of game A (one at load, one mid-staging in `HoseRelayIndex` JIT; `bad_cpus=[2]` all pass),
1 bridge reset during quick-test map generation, 0 dropped ssh. Retired on the context gate (251k).

**The zoom the bar names changes the verdicts.** CLAUDE.md: play zoom is ~64 px a cell. Steve's game window is ~920 px high,
so that is **root 7.2** (s7 at root 7.5 measured 916 x 855 px for 15 x 14 cells = 61 px). Every earlier pass judged "play
zoom" at root 20 (~23 px, a third of the bar's resolution). `story1.py`/`story3.sh` now take `FW_ROOT=7.2`; `bars3.py` adds
`_r7` frames. Re-judge every look bar at root 7.2.
- **`pit_covered_invisible` is false at 61 px**: the cover's SOUTH row is a dark brown band, the north row passes for soil
  (`shots\pass6\s7_cover_south_row_dark_61px_x2.png`, undug left, covered right). Not the seam (`SeamMat` alphas 0.07/0.42/0.16
  are hairlines) and not the faces layer (skips lidded squares). Note `SeamStrength` gives 0.9 at ANY root <= 13 (the bridge
  widens the camera's min size to 0.5). Untested suspects: spikes drawn sunk under the lid, the near-lip occlusion band, a
  shadow pass. `ralph/live/cover6.py` (written, never run) stages undug / covered / spiked+covered side by side and can flip
  settings fields: run it, then fix.
- At 61 px the open pit reads as a hole (dark floor, lit far face), and a raider in the spiked pit reads as down in it with
  the archers above on the lip (`s7_raider_in_pit_archers_on_lip_61px.png`).

**Story runs** (`FW_SPAWN=gx,0 FW_ARCHERS=5 FW_ADZ=2 FW_ROOT=7.2 bash ralph/live/story3.sh 400 TribeRoughNeanderthal sN`;
logs on Steve `Transient/ralph_fw/{stage,raid,watch}_sN.out`):
- s7 (pass-5 build): the count spawn put one archer OUTSIDE the compound; the raid walked round to him, downed and kidnapped
  him. One raider (Bilen) fell, then **meleed the archer standing on the lip above him from 2 m down**, and the drafted archers
  shot him dead point blank before any rescuer came. One raider chopped a pine for a ladder, then the raid left (KidnapCover).
- s8: `rimworld/set_draft` did not draft the archers; they wandered off and were downed outside. Fixed: each archer is spawned on
  its own spot and drafted with `jawa/order_pawn draft=True waitTicks=0`; the passage floor is cleared of trees (s7 had
  pines standing in it, drawn over the pit).
- s9 (this build): four of five raiders fell in, but **the pit was full of water** (pit report `fillRaw` 3-4 of depth 4, about
  an hour of game time after it was dug), so they were not held (`held:false`, CanReach to the archers true) and walked out
  and meleed the archers (ProofThink: `JobGiver_AIFightEnemies`, `JobGiver_ReactToCloseMeleeThreat`). Likely rain: the model
  adds a notch (0.5 m) per 10 pulses at RainRate 1 (`rainFillPerPulse` 0.1, `RainLevelsNow`). Pass 5 saw rain fill the
  story pit too (s4). Not yet confirmed: the weather and the fluid at the time. QUESTIONS 4.

**Built this pass (in the commit with this file; built, deployed except the last, partly seen):**
1. `Superdeep/RM_CliffMelee.cs` (PIT_STORY_FIX_MELEE_ACROSS_THE_LIP): no melee, trash or blocker-bash between squares a cliff
   apart (the shooting rule's 2 m), either way (melee target finder, `TrashUtility.ShouldTrashBuilding/Plant`,
   `DigUtility.PassBlockerJob`); a pawn HELD in a pit is no auto-target threat to a searcher a cliff above it unless it engaged
   in the last 360 ticks (`Pawn.ThreatDisabled` postfix). Live in s9: `refused=338 threatsDisabled=9`. Not yet seen in a run
   where the pit stays dry. Probe: `RM_CliffMelee.ProofCliffMelee` (the watch logs it).
2. Pass 5's `isTrap` on the covers made vanilla log "Config error ... isTrap but is not edifice. Code will break." x6: removed;
   instead the same trash postfix never trashes or torches a cover that has not given way. s9 showed no job on the cover.
3. `Superdeep/RM_RaidLeavesTrapped.cs` + key `RMFlow_RaidLeftTrapped`: when a hostile raid's lord turns to leaving with members
   held in a pit, one message names them and points at the capture from the edge. **Built, not deployed, never seen.**
4. `RM_TakenByLand.ProofReturnedGrace` (mark/read) and `four.py` steps: mark, save, reload, read, +2500 ticks. Deployed, not run.
5. Hung suspension bridge: a builder subagent wrote NO code (stopped at my retire); its design, with every edit pinned by
   file and line, is `D:\ClaudeWork\rimmandrake\ralph_flowworks\hung_bridge_pass6\PROGRESS.md` (new `RM_SuspensionHang.cs`;
   treatments 0 suspension, 1 rope walk, 2 cable-stayed, switched by `jawa/static_call` `RimMandrake.FlowWorks.Pits.RM_SuspensionHang`
   `SetTreatment` "0"/"1"/"2"; sagged deck, posts, cables, floor shadow; the deck redrawn over a pawn on the floor beneath it;
   deck walkers lowered by the sag; rope-walk sag capped at 0.2 of a segment so a 3-cell N-S span does not fold). Its empty
   worktree `.claude/worktrees/agent-ae9f8185dff1939c2` can be removed.
C# self-test on the first build of this pass: 2 FAIL, `PitCapture_follows_a_held_pawn_that_moves` (known red) and `LW1 a lay
depends on the world's content only` (hose lay world, not touched here; check whether it is red on HEAD~ before blaming).
Rerun it on this commit with the output kept whole (the background tail cut the summary).

## Next (in order)
1. Deploy this commit; `ralph/steve.sh status`. Settle the flooded pit FIRST: on a fresh map dig the story pit, read
   `jawa/map_info` weather and the pit report's fill every 250 ticks for a game day. If rain fills 2 m in hours, rule on
   QUESTIONS 4 (recommendation there) and build it; the story cannot play while the pit floods.
2. Story s10, same command, on a dry pit: watch for no melee across the lip, archers shooting the rescuers not the trapped,
   the rescue ladder SEEN going in (near wall), the raid driven off, the new message, then right-click capture from the edge.
   If the rescue still never completes, stage it so it does (owner's ruling: stage it to complete, don't replay for luck).
3. `cover6.py stage` then `shots`, find the dark south row, fix, re-shoot at root 7.2 before/after.
4. Depth sheet at root 7.2: `FW_... bash ralph/live/bars3.sh p6 1`, then judge the depth/pawn-height bars at 64 px.
5. Hand the bridge design (`hung_bridge_pass6\PROGRESS.md`, its "Next" line) to a fresh builder while the game runs the story;
   shoot the three treatments side by side at root 7.2 into `ralph/LOOK.md` as a contrast sheet.
6. `four.py` (grace across a reload, cover scan, cliff timing, two maps) on this build.
7. GPT broaden call (none made this pass or last; needed before DONE.md), with the root-7.2 shots.
Earlier owed items stand (PROGRESS of pass 5): trench cage staging, pawn lowers/rises walk, portable-ladder too-tall control,
no-gear wall control, jump exits, dig fill + raiders carrying fill.

## Running count (seen in game; look bars now judged at ~64 px a cell where re-shot)
- pit_depth_ladder_legible: false (pass 3 at r20); unjudged at 64 px
- pawn_height_ladder_legible: false (pass 3 at r20); unjudged at 64 px
- pawn_lowers_on_deeper_cell: unseen
- pawn_rises_on_shallower_cell: unseen
- pit_reads_as_hole: true (s7 open pit at 61 px)
- pit_walls_have_visible_depth: true
- pit_not_vanilla_trap: true
- pit_reads_at_size: true
- pit_occupant_below_floor: false (true at 2 m; the 4 m 3x3 case drew on the south lip, pass 2)
- pit_occupied_distinguishable: true
- pit_trapped_reads_as_trapped: unseen
- pit_covered_invisible: false (s7 at 61 px: the south row is a dark band)
- pit_covered_seam_at_max_zoom: true
- ladder_state_legible: false (south fix unseen)
- sluice_gate_state_legible: true (Conductor ruling 1:23)
- spikes_read_distinct: true
- trench_wall_cover_shown: true
- raiders_never_shelter_in_a_cage: unseen
- wall_ladder_rides_on_rails: false
- portable_ladder_leans_on_its_wall: false (stronger lean unseen)
- climbing_gear_reads_as_kit: false (ground kit)
- geared_pawn_climbs_out: true (Conductor ruling 1:23)
- jump_into_pit_lands_unhurt: unseen (one clause owed)
- geared_pawn_scales_built_wall: unseen (no-gear control owed)
- suspension_bridge_reads_hung: false (designed, not built)
- pawn_walks_under_deck: false (draw order; designed, not built)
- pit_cover_unlike_bridge: true (Conductor ruling 1:23)
- digging_takes_hours: unseen (fill + raiders carrying fill owed)
- never_snared_standing (cannot): true
- never_reads_as_building (cannot): true

Count: 13 true, 10 false, 7 unseen (of 30).

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | the story pit floods within about an hour; the fallen float out | s9 pit report fill 3-4/4, held:false | weather + fill per 250 ticks on a fresh map (Next 1) |
| blocker | his story has never reached "driven off, prisoners in a tidy prison" | s7 kidnap, s8 staging, s9 flood | s10 on a dry pit |
| regression | covered pit visible at play zoom (south row dark) | s7 61 px crop | cover6.py at root 7.2 |
| unknown | cliff-melee rule in a held pit | s9 counters only | s10 job log: no AttackMelee across the lip |
| unknown | the withdrawing-raid message | built, not deployed | s10 messages |
| blocker | bridge reads flat | design only (hung_bridge_pass6) | build it, root 7.2 shots |
| decision | rain fill rate vs pit traps | QUESTIONS 4 | his card |
| decision | play zoom is root 7.2 on Steve (64 px) | CLAUDE.md, s7 clip | re-judge the look bars there |
