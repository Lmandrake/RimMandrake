# Live checks 2 - 2026-10-08

## 1 FlowWorks live north-star
Tier `flowworks` (11 mods), FlowWorks already in sync with repo (no deploy needed). Command: validation_v2.py --live --fresh-map.
Output: `Transient/belt_fw_live_20261008.txt`; result JSON `src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261008T112703.json`.
Result: NOT GREEN, 57 PASS / 2 FAIL / 0 UNMEASURED (12128 ticks, 268 s).
- E4_engine_off FAIL: nextPulseTick moved 251->501 while the engine was OFF; no cell moved. The harness expects it frozen, but the
  mod deliberately advances it and runs liquidFire.BurnPulse when off (RM_MapComponent_Excavation.MapComponentTick, GPT review #18).
  So the pour-stops-when-off behaviour held; the row's frozen-schedule assertion is stale against that change.
- E1c_cadence_real_scheduler FAIL: gaps [0,60], lead [10,70,130]. Consequence of the same thing: the OFF pulse re-armed nextPulseTick
  at the shipped 250 interval, and E1b's pin to 60 cannot pull it earlier. Probably not an independent defect, but unproven.
Graders were not edited. No rimflow verify recorded (run is not green).

## 2 Watchers kit live checks

Tier `watchers_live` (new, in modset_builder.py: bridge + gimmesomeslack + biomes + watchers + flowworks via closure, 16 mods). Quicktest map (The Rot),
DeepSand rect painted at 100,100,20x20, piinnok only (the only member). All reads are state reads (job, hediff, sign Thing, designation).
Scripts: `Transient/belt_watchers_live_20261008.py`, `..._live2_...py`, `..._live3_...py`; raw output beside them (.txt).
Trap found: colonists cannot walk RM_DeepSand (it is water), so the colonist cue must stand on the soil edge; watchers sit on x=100.
- watches (job RM_WatcherWatch with a colonist at 12 cells): PASS. Facing (pawn.Rotation): UNMEASURED, no bridge tool reads rotation.
- flinch hide: PASS. Colonist at 5 -> RM_WatcherHidden on the pawn AND RM_WatcherSign_SandDimple on its cell, same 30-tick window; pawn stays spawned.
- re-emerge: PASS. Colonist leaves -> hediff and sign gone after 3200 ticks, job back to RM_WatcherWatch.
- stays on medium: PASS. Spawned on Soil: never RM_WatcherWatch, no hide, no sign; walked onto RM_DeepSand within 600 ticks, then watches.
- geophone: PASS. Submerged RM_Muurrok at 8 cells, no pawn within 14: hidden + sign in 30 ticks; geophone OFF: not hidden after 300 ticks, no sign.
- hunt order sinks peeker: PASS. Watching piinnok given Hunt: hidden in 40 ticks, Hunt designation removed.
- flush: PASS. Hidden piinnok, sign marked RM_WatcherFlushMark, colonist ran RM_WatcherFlush: piinnok Flee, hediff + sign gone, Hunt designation present on it.
- cues gas/heat/fire/steam/shade/buried/light (A3/A4/A5): UNMEASURED. No shipped member carries a cue and no test race was built.
- other members / one-per-biome: UNMEASURED, only the piinnok exists.
- Side finding, unverified: jawa/thing_graphic reported UI/Misc/BadTexture for the piinnok (pawn graphics may report this regardless; piinnok art is still owed).
rimflow: A1 and A2 recorded `partial` (run-1, run-2 @watchers_live); A3-A5 not recorded.
