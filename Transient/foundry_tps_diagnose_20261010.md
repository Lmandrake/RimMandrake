# FOUNDRY full-list TPS diagnosis 2026-10-10

Ticket: FULL_LIST_TPS_DIAGNOSE_EIGHT_NOT_SIXTY

## Log
- 14:30 start
- 14:31 TPS record read: every run window 14:05-14:40 top=mapComp 85-97% (not tl:Normal; that 83% was a mixed window); same signature as ROT ticket. ~230 map components on the map. Suspect #1 RM_MapComponent_AcceleratedRot.
- 14:34 Stage ms/tick over 64 run windows (3247 ticks): tick 93.6, mapComp 88.4 (94%), tl:Normal 3.1, world 0.9, mapPre 0.7, rest <0.2. Only Harmony patches on MapComponentUtility.MapComponentTick are our own profiler -> cost is inside component overrides. GC: 135 collections in 634 s running (1 per 4.7 s; heap ~5.0 GB managed), gapMax 350-780 ms/window. Private 30.6 GB, commit headroom 24 GB, avail phys 9 GB: no paging evidence. Map 250x250 RM_TheRot, 36.3k things, 19 pawns.
- 14:34 No per-component instrument exists -> wrote jawa/map_comp_timing (JawaBenchMapCompTiming.cs, test-only), built OK. Restarting game to deploy (pid 1568).
- 14:35 companion deployed (63447a6db650 + map_comp_timing); relaunch via launch_ready.py --profile full
- 14:44 loading (pid 27132)
- 14:53 still loading
- 14:55 READY pid 27132 (1225 s); starting quicktest
- 14:59 map_comp_timing 304 ticks: MapComponent_HugeFootprints (mandrake.rm.hugethings) 70.0 ms/tick of 70.9 summed (99%), max 457 ms; next AcceleratedRot 0.13
- 15:02 cause: HugeFootprints whole-map RealizePending on any plant refresh (2811 giants, 7400 blockers, ~1315 refused pending cells). Fix f3774dd15 (refreshed owners only + phase-spread retry + roots cache, no per-tick SortedSet walk) built, pushed, deployed to Mods; NOT live-proven (running game loaded the old DLL).

## Result
Ranked (Rot quicktest, 550 list, Normal):
1. MapComponent_HugeFootprints (mandrake.rm.hugethings): 70.0 ms/tick (99% of mapComp; mapComp = 88.4 of 93.6 ms/tick in the TPS record). Whole-map RealizePending on any plant refresh. Fix f3774dd15 (deploy blocked by the locked DLL: re-run with game down).
2. Rot giant density: 2811 footprint giants, 7400 blockers (~12% of cells), ~1315 refused claims -> the workload behind #1 (ROT_GIANTS_DENSITY_JUDGE_TWELVE_PCT_BLOCKED).
3. GC: 12.8 collections/min running vs 5.3 paused on a ~5 GB managed heap; gapMax 350-780 ms/window. Likely the per-owner Flags dictionaries of #1 (hypothesis; check in the proof run).
Everything else: tl:Normal 3.1, world 0.9, mapPre 0.7, other components <0.15 ms/tick each.
Memory: 30.6 GB private, ~5 GB managed, 24 GB commit headroom: not the TPS cause (FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE).
Recorder: the always-on record localized it to the mapComp stage unaided; naming the component needed one new one-off tool (jawa/map_comp_timing, by design out of the always-on path).
