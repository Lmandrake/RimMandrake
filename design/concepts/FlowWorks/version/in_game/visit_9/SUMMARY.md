# FlowWorks 0.1.0 — in-game acceptance, visit 9

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_NINE, ArchSmall on Archmagi.
2026-11-23: started 2:08 PM PST; ArchSmall was held by the ExplosiveKnockback run until 2:32 PM; bridge released 5:30 PM
(the 3 h bound is counted from the bridge take).

## Build and lists

- The mod moved twice mid-visit: 209d57476d at the start, then 6447d14771 (four pump looks) and f4971d58fa (tank tables). The
  relation program reads each C# change as touching every check, so all were rerun on f4971d58fa. Final rows: f4971d58fa, RimWorld 1.6.4871 rev590.
- Lists: 13-mod flowworks tier; fw_gss_sitting for sc_source_pays; evening_20261113 for OL_OWNER_LOOK_READS.
- ArchSmall runs no full list beside ArchBig: sc_walk is UNMEASURED here and owed on ArchBig. PIT_LOOK_1114_LIVE was not
  run (owed on ArchBig: the sitting save).

## Results on f4971d58fa [measured]: 27 PASS, 1 FAIL, 1 UNMEASURED of 29

- FAIL sc_moat_raid (kind A; 3 valid runs of the scene on 209d57476d and f4971d58fa: PASS, FAIL, PASS). In T161018 row
  MOAT_rim_wardens_not_stabbed FAILed: raider Human21212, read held=True, left the drained 4 m moat and cut a warden. Class
  MOD, not fixed: the cause is not read. HUNT OPENED, item RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT. The scene now
  keeps every raider's square and job each 60 ticks of the drain (b150bbd9ce). Bar moat_raid_sequence stays undecided.
- UNMEASURED sc_walk (full list; ArchBig).
- The other 27 PASS. OL_OWNER_LOOK_READS: 1629 PASS, 0 FAIL, 0 UNMEASURED, 0 BLOCKED (visit 8 had 1 BLOCKED row).

### Scenes repaired in the sitting (bc7dd578fd; no mod code touched)

- sc_moat_raid staging, class SITE: the plot's grass refused the build (14:37). Red on the parent scene, green on the fix.
- sc_ice staging, class SITE: a colonist with Mining disabled. Red on the parent, green on the fix.
- sc_pit_trap_raid, class HARNESS: an unfinished capture now names the hits on its warden. The 14:43 run's downed warden was
  not explained (it did not recur in 2 runs); the check decides no bar.

## Owed cases

- sc_garden ran on this build: PASS (the four blind-cycle Problems' scene, sheet, converter and drill rows). No planted
  fault ran in a game this visit; the plants of lane2 were not repeated (their offline reads stand).
- Road back: sc_fill_front, sc_fill_tiers, sc_garden, sc_hose_look, sc_pit_trap_raid, sc_source_pays, sc_trench_cover,
  sc_fetch_fallen, sc_geyser_tub, sc_ice, sc_hole_prison, sc_hung_bridge, sc_ways_out, sc_covered_pit, OL_OWNER_LOOK_READS:
  each PASS on this build. sc_moat_raid: the control row passed in each of 3 runs (its staging fix
  32766479e0 holds), the rim stab row did not. sc_walk and PIT_LOOK_1114_LIVE owed on ArchBig.
- The five lane-1 not_kernel rows are covered by the live scenes above only as far as the scenes read them; still
  unsettled offline (crops killed, the survey roll, FluidDef numbers).

## Beyond the checks

Screenshots looked at: hose, fill tiers, pit hole, spikes, sluice, depth ladder, the big pit (7 copies). Small copies in
`screenshots/`. Five strange things in `strange.jsonl`: one filed, four explained.

## Pipeline notes

- My modledger lease lapsed at 15:17 PST (45 minutes with no append, my miss): the closing checkpoint cannot be appended
  by this holder; the state is in this file and the item's notes.
- ArchSmall has no RM_TestSite_river save until today (copied in).

## The savegame

No new savegame; the walk save stays visit 4's (it loads with today's build; its staged scenes were not re-checked):
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`

## Items filed

RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_source_pays: pass, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: pass, sc_one_network: pass, sc_trench_cover: pass, sc_hung_bridge: pass, sc_ice: pass, sc_moat_raid: fail, sc_hole_prison: pass, sc_toss_flame: pass, sc_fetch_fallen: pass, sc_islands: pass, sc_walk: unmeasured, sc_pit_trap_raid: pass, sc_garden: pass, OL_OWNER_LOOK_READS: pass, sc_geyser_tub: pass, sc_coating_wash: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: false
```
