# FlowWorks playtest pilot timings — 2026-10-06

Started Tue Oct  6 10:40:15 PDT 2026

## Restart + deploy

- 10:40 game killed (taskkill, debug map) + `./game down`: 13 s.
- Mod list: live ModsConfig was ALREADY the `flowworks` tier (10 mods, all five DLCs, RimBridgeServer, FlowWorks) — no swap needed, no write.
- JawaBench `build.py --gm --apply`: 4 s, deployed (game copy was e5f4f08c3bef, now fd96b35bfc22).
- FlowWorks: game DLL == HEAD DLL (md5 03491c17). The worktree DLL differs — it is an UNCOMMITTED build of another
  writer's in-progress refactor (RM_FlowKernel.cs untracked, RM_LiquidStock.cs/RM_MapComponent_Excavation.cs modified 10:30–10:33).
  NOT deployed. Only `northstar/player_missions_spec.json` copied in (needed for Approach C).
- `--compose biomes --apply` (DivingInteraction density fix, all committed): deployed; Biomes mod not in this list, so inert this load.

## Approach A — pilot batch

- launch via Steam (launch_and_wait.sh) → bridge up: 29 s; quicktest map (start_debug_game_ready): 4 s.

```
run fwpt_20261006T174502_s1  scenarios=fluids,dig,pit  mode=batch  driver=monobehaviour
  fluids   FAIL       0.02s      0 ticks  touching water and tar merged into one body carrying one fluid (expected two bodies, own fluids) - see cases
  dig      PASS       5.34s  10861 ticks  designated dig taken and completed by Shield (Human91), fill-in by Shield (Human91); original terrain restored
  pit      FAIL       1.57s   3300 ticks  friendly did NOT get out by the lowered ladder within 1500 ticks

scenario   status  wall s  ticks  frames  setup s  exec s  observe s  ticks/s
---------  ------  ------  -----  ------  -------  ------  ---------  -------
fluids     FAIL    0.02    0      0       0.01     0.00    0.00       0      
dig        PASS    5.34    10861  97      0.01     5.33    0.00       2036   
pit        FAIL    1.57    3300   28      0.10     1.46    0.01       2254   
RUN TOTAL  done    6.98    14161  126     0.12     6.80    0.01       2083   
tick mode batch (Paused+DoSingleTick), frame budget 50 ms, runner overhead 0.05 s, Ultrafast multiplier 150
launcher: 8.66 s wall start->collect, 6 bridge calls

VERDICT FAIL  (5 records)  journal C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios\JawaBench\playtest\fwpt_20261006T174502_s1.jsonl  copy \\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\flowworks_playtest\fwpt_20261006T174502_s1.jsonl
```

## Approach A — pilot speed

```
run fwpt_20261006T174517_s1  scenarios=fluids,dig,pit  mode=speed  driver=monobehaviour
  fluids   FAIL       0.01s      0 ticks  touching water and tar merged into one body carrying one fluid (expected two bodies, own fluids) - see cases
  dig      PASS       2.68s   5220 ticks  designated dig taken and completed by Rhea (Human97), fill-in by Shield (Human91); original terrain restored
  pit      FAIL       1.80s   3602 ticks  friendly did NOT get out by the lowered ladder within 1500 ticks

scenario   status  wall s  ticks  frames  setup s  exec s  observe s  ticks/s
---------  ------  ------  -----  ------  -------  ------  ---------  -------
fluids     FAIL    0.01    0      0       0.01     0.00    0.00       0      
dig        PASS    2.68    5220   46      0.00     2.68    0.00       1950   
pit        FAIL    1.80    3602   31      0.25     1.54    0.01       2345   
RUN TOTAL  done    4.56    8919   77      0.26     4.21    0.01       2094   
tick mode speed (Ultrafast), frame budget 50 ms, runner overhead 0.07 s, Ultrafast multiplier 150
launcher: 6.55 s wall start->collect, 5 bridge calls

VERDICT FAIL  (5 records)  journal C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios\JawaBench\playtest\fwpt_20261006T174517_s1.jsonl  copy \\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\flowworks_playtest\fwpt_20261006T174517_s1.jsonl
```

## Approach A — fluids,inject

```
run fwpt_20261006T174529_s1  scenarios=fluids,inject  mode=batch  driver=monobehaviour
  fluids   FAIL       0.01s      0 ticks  touching water and tar merged into one body carrying one fluid (expected two bodies, own fluids) - see cases
  inject   ERROR      0.00s      1 ticks  System.InvalidOperationException: injected failure (recipe token 'inject')
[Ref 20AE685E]
  at JawaBench.BridgeTools.JawaBenchTerrainTools+<ScnInject>d__166.MoveNext () [0x0004e] in <26887feb69fd4314986a0dd0fcc7b823>:0 
  at JawaBench.BridgeTools.JawaBenchTerrainTools+PlayRun.Frame () [0x001eb] in <26887feb69fd4314986a0dd0fcc7b823>:0 

scenario   status   wall s  ticks  frames  setup s  exec s  observe s  ticks/s
---------  -------  ------  -----  ------  -------  ------  ---------  -------
fluids     FAIL     0.01    0      0       0.01     0.00    0.00       0      
inject     ERROR    0.00    1      0       0.00     0.00    0.00       1072   
RUN TOTAL  ABORTED  0.04    1      0       0.01     0.00    0.00       1000   
tick mode batch (Paused+DoSingleTick), frame budget 50 ms, runner overhead 0.02 s, Ultrafast multiplier 150
launcher: 2.19 s wall start->collect, 3 bridge calls

VERDICT INCOMPLETE  (4 records)  journal C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios\JawaBench\playtest\fwpt_20261006T174529_s1.jsonl  copy \\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\flowworks_playtest\fwpt_20261006T174529_s1.jsonl
```

### A — reading

- batch vs speed: 2083 vs 2094 ticks/s achieved over waits (RUN TOTAL) — no measurable difference at a 50 ms frame budget;
  speed reports Ultrafast multiplier 150. Launcher wall 8.66 s (6 bridge calls) vs 6.55 s (5 calls).
- fluids: REPRODUCED the water/tar merge in all three runs (one body, one fluid) — expected source finding (`RM_LiquidStock.cs:157,168`).
- dig: PASS both modes (colonist took RM_DigCanalJob unforced; fill-in restored terrain).
- pit: FAIL both modes on `friendly_with_ladder` only. Hostile held with and without ladder (correct); friendly held without ladder (correct).
  With the lowered ladder at (pit.CenterCell.x, pit.maxZ) — INSIDE the pit, top row — `CanReach` turns TRUE but the friendly never
  leaves its spawn corner (cellsVisited 1, 12 order re-issues, job ends as Wait). Reading the code: the path-follower floor
  (`RM_Patch_PathFollower_SuperdeepFloor`) blocks any step from a HELD cell to D<4, and the pather does not route via the ladder cell,
  so the Goto path is vetoed and `Notify_PatherFailed` fires. Hypothesis (NOT live-proven): reachability and the pather disagree —
  reachability credits the ladder, the path does not go through it. Not a runner bug as far as read; not chased further.
- fluids,inject: VERDICT INCOMPLETE (run_end ABORTED, fluids record kept) — as designed.

## Approach C — mission 1 canal

Moves: found "Dig canal" under Architect > Orders (8 list reads, the first few wasted by my own output filtering), designated a
15-cell feeder from the pond (z=124, x=115..129) and an 11-cell N-S canal across the band (x=130, z=119..129), set Mining priority 1
on all three colonists, then advanced time. Water filled the channel behind the diggers (25 of 26 dug cells filled, depth 1).
Overran the 60k-tick deadline (66,918 ticks) because play_for overshoots; the report still prints PASS — the driver does not
apply the tick deadline to the verdict. `step_game_ticks` timed out at 601/2000 ticks; three play_for calls returned
"busy with a long event" yet advanced time (logged as failed_action friction — transport, not mod).

```
MISSION canal    verdict PASS
evidence: {"band": "129,117,3,16", "filledCanalCells": 12, "needed": 10}

TIMING
  mission_wall_s       129.921
  fixture_s            0.84
  think_s              88.887
  bridge_s             40.417
  overhead_s           0.599
  ticks_by_actions     66918
  ticks_during_think   0
  screenshots          0
  screenshot_s         0.0
  actions              20
  observes             6
  refused              0
  internal_reads       0
  class          n  bridge_s   think_s    ticks
  designate      2      0.11     18.11        0
  order          3      0.27     19.57        0
  read          10      0.62     25.62        0
  time           5     38.20     17.41    66918

FRICTION (4)
  #16  act     rimworld/step_game_ticks               failed_action                      Timed out after advancing 601 of 2000 requested tick(s).
  #18  act     rimworld/play_for                      failed_action                      RimWorld is busy with a long event.
  #22  act     rimworld/play_for                      failed_action                      RimWorld is busy with a long event.
  #24  act     rimworld/play_for                      failed_action                      RimWorld is busy with a long event.

TRACE
  #0   observe  observe                                think    6.6s bridge     278ms ticks+0     OK 
  #1   act      rimworld/list_architect_categories     think    4.6s bridge      34ms ticks+0     OK find where digging/water tools live
  #2   act      rimworld/list_architect_designators    think    4.7s bridge     106ms ticks+0     OK browse orders for dig/canal tools
  #3   act      rimworld/list_architect_designators    think    0.4s bridge      53ms ticks+0     OK browse structure for dig/canal tools
  #4   act      rimworld/list_architect_designators    think    0.4s bridge      52ms ticks+0     OK browse misc for dig/canal tools
  #5   act      rimworld/list_architect_designators    think    3.1s bridge      52ms ticks+0     OK browse orders for dig tools
  #6   act      rimworld/list_architect_designators    think    5.6s bridge      52ms ticks+0     OK browse orders for dig/canal/water tools
  #7   act      rimworld/list_architect_designators    think    0.5s bridge      69ms ticks+0     OK browse structure for dig/canal/water tools
  #8   act      rimworld/list_architect_designators    think    0.6s bridge      69ms ticks+0     OK browse misc for dig/canal/water tools
  #9   act      rimworld/list_architect_designators    think    0.4s bridge      52ms ticks+0     OK browse zone for dig/canal/water tools
  #10  act      rimworld/list_architect_designators    think    5.3s bridge      85ms ticks+0     OK re-read orders labels for a dig order
  #11  act      rimworld/apply_architect_designator    think   17.8s bridge      63ms ticks+0     OK dig feeder channel from pond east edge to the goal band along z=124
  #12  act      rimworld/apply_architect_designator    think    0.3s bridge      52ms ticks+0     OK dig the defensive canal north-south across the goal band at x=130
  #13  act      jawa/set_work_priority                 think   18.9s bridge      87ms ticks+0     OK Work tab: make Arnold prioritise mining so the canal gets dug
  #14  act      jawa/set_work_priority                 think    0.4s bridge     100ms ticks+0     OK Work tab: make Rhea prioritise mining so the canal gets dug
  #15  act      jawa/set_work_priority                 think    0.3s bridge      83ms ticks+0     OK Work tab: make Shield prioritise mining so the canal gets dug
  #16  act      rimworld/step_game_ticks               think    0.3s bridge   10085ms ticks+601   NO let colonists dig
  #17  observe  observe                                think    0.3s bridge     194ms ticks+0     OK 
  #18  act      rimworld/play_for                      think   10.2s bridge    3422ms ticks+6317  NO run time at ultrafast so the canal gets dug
  #19  observe  observe                                think    0.3s bridge     170ms ticks+0     OK 
  #20  act      rimworld/play_for                      think    6.3s bridge   12183ms ticks+32288 OK keep time moving while the canal is dug
  #21  observe  observe                                think    0.3s bridge     188ms ticks+0     OK 
  #22  act      rimworld/play_for                      think    0.3s bridge    5650ms ticks+12712 NO keep time moving while the canal is dug
  #23  observe  observe                                think    0.3s bridge     189ms ticks+0     OK 
  #24  act      rimworld/play_for                      think    0.3s bridge    6859ms ticks+15000 NO keep time moving while the canal is dug
  #25  observe  observe                                think    0.3s bridge     192ms ticks+0     OK 

report.json: \\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\player_missions\canal_20261006T105024\report.json
```

## Blockers

- Second `start_debug_game_ready` from an already-Playing game timed out (entry scene readiness); mission ran on the A map instead.
- FlowWorks worktree DLL is an uncommitted in-progress build by another writer — deliberately NOT deployed; game runs HEAD's DLL.
- pit/friendly_with_ladder FAIL — open question (reachability vs pather), see A reading.

## Final state

Game UP on the 10-mod `flowworks` tier (NOT restored to the full list — deliberately left minimal), quicktest map with A fixtures + canal mission. Bridge released.

- 10:50 second quicktest from a Playing game FAILED ("Timed out waiting for RimWorld entry scene readiness"); mission started on the Approach-A map (site 109,117 is clear of the pit at 66,116). `start canal`: 2 s, fixture 4 ops 0.8 s, checkpoint save PM_canal_start_20261006T105024. Operator note: the player is me, and I had read FlowWorks C# for the pit diagnosis — not a naive player.
