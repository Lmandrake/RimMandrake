# Ladder toggle progress (FLOWWORKS_LADDER_RAISE_LOWER_1)

- 22:05 started; read item.
- 22:10 code: setting ladderRaiseLowerEnabled, RM_CompLadder SetRaised/gizmo keyed Ladder up/down, RM_Building_Ladder raised graphic hook, outsider entry reachability veto; SelfTest 110/110 incl Ladder_raise_lower_usable_and_entry
- 22:12 game was running idle (pid 241704, log idle since 21:36) - killed it to deploy; bridge taken
- 22:13 deployed GSS (stale deployed DLL broke JawaBench build), JawaBench, FlowWorks; tier flowworks (10 mods); launching
- 22:18 playtest_start threw TypeLoadException (GSS LaidPiece) without GSS loaded: JawaBenchTerrainTools lambda cache shares GSS types; added mandrake.rm.gimmesomeslack to flowworks tier (11 mods), relaunching
- 22:21 (a) full: 9 PASS incl pit_ladder_release/pit_fall_forced/pit_ladder_toggle; depth_fill/fire/sluice FAIL (not ladder); haul+raised_hold INVALID (no pit site: fog) -> added fog-lift fallback to QBuildPit; save_reload_b PASS, pond body 37.043/45/2 saved==loaded on this quicktest map (43.006 figure was round-2 map), branchesEqual
- 22:23 (b) loaded RM_pitlip_muffalo_bug_20261006 (tick 15380, Muffalo24734 at 172,135 by list_things), screenshot Screenshots\pitlip_muffalo_fixcheck_20261006.png: body STILL covered by a ground quad -> PIT_LIP_OCCLUDES_OUTSIDE_1 NOT fixed by 391127ff6
- 22:24 (b) detail: flowworks_excavation_rect says 172,135 is D4 (RM_Channel_Superdeep, the pit's SW cell) - the Muffalo is IN the pit, drawn sunk south over the lip, and the lip cover hides its right half; left half drawn. Not whole -> FAIL; item title's 'outside' is the sink offset's illusion
- 22:25 (c) fresh quicktest, JawaBench rebuilt: pit_ladder_release/toggle/haul/raised_hold all PASS (fwpt_20261007T052523_s1). haul: raised canReach=false canAutoHaul=false item stayed; lowered: Hero went down the ladder (downByLadder), steel in stockpile in 815 ticks
