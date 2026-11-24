# Test pilot sitting: RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS
Host: ArchBig (archmagi), bridge taken 06:06 PST 2026-11-23. Clone: .../RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS.det
## State
- claimed, bridge held. Nothing run yet.
## Theories (false ones stay)
## Experiments
## Looks / surprises
## Evidence paths
## Next
- read harness (sc_moat_raid in FlowWorks/northstar/concept_scenes.py), visit_8 rows, Player.log first exception; arm vitals; first look.
## Look 0 (06:07 PST) — EXPECTED
- OS capture look0.png: big-pit owner-look map (BP0..BP6 labelled pits), 3 colonists, paused tick 74, Clear (WeatherController forced), 57F spring 6AM. No modal (window list: 1 ImmediateWindow). Player.log: 0 'exception' lines [measured, 82 KB log]. ModsConfig 22 active, flowworks tier.
- Brief said big pit staged: EXPECTED. My scene run reloads the calm save and replaces it (rebuild: visit_8/evidence/bigpit plan+stage, 186 s).
## Evidence read (visit 8)
- T034943 FAIL: 2 held; BOTH wardens spawned on the same lip (69,66); 2nd capture 'Allowed held=True prisoner=False' after 900 ticks, warden able.
- T042734 FAIL: 3 held, 2 wardens downed; 21181 at 61,61 lip (62,62) stalled, warden able.
- T050452 PASS trace: raider 21215 AttackMelee at 71,64 (outer ring column, no plot lip touches it) then 70,64 pinned, then AttackMelee again while warden still RM_CaptureDown.
## Theories (written before experiments)
- T1 OUTER-COLUMN: ring is 2 wide; a raider on the outer column touches no plot lip, warden waits (Repath/pause), raider unpinned -> walks in and melees the warden. Predicts: stalls/downs correlate with captive on outer column at order time.
- T2 PIN-DROPS: pin job ends (expiry / FailOn warden job flicker / damage) and resumeCurJobAfterwards puts the raider back in AttackMelee on the warden. Predicts: captive job flips Pinned->AttackMelee while warden still RM_CaptureDown, damage_log on warden names the captive.
- T3 THIRD-PARTY: a held raider that is NOT this warden's victim (own warden stalled/absent) melees a neighbouring warden; pin only covers the victim. Predicts: damage instigator != the downed warden's own victim.
- T4 WARDEN-JOB-ENDS: warden's RM_CaptureDown ends (Incompletable after repath bound, flee/self-defence override, reservation) and nothing re-orders it; harness waits 900 ticks on a dead order. Predicts: warden job != RM_CaptureDown long before 900 ticks, warden able.
- T5 SAME-LIP: two wardens spawned on one lip square (harness picks nearest plot square per raider, no dedupe) -> spawn nudges/one job fails. HARNESS. Predicts: stalls when two captives share nearest plot square.
- T6 FLAG-BACKSLIDE: CapturedBy succeeded then prisoner flag reverted (lord/faction cleanup). Predicts: prisoner=True seen then False.
## Experiments
- E1 (06:2x) full scene with trace: swim row FAIL (3 swam, exhaustion 0.0 at 5 polls, 2 reached plot, bait colonist 'Carried'), 1 held -> capture UNMEASURED. Scene variance is large. Row detail is truncated in JSON: trace must go to a top-level receipt key (TODO fix my harness edit).
- Keeper save TP_MOAT_HELD_A (Saves folder): drained 3 m moat, held 21181@63,61 and 21233@68,61, free raiders and bait vanished. Driver: exp.py (stage|cap).
- E2 baseline cap both, auto lips (adjacent): both pinned at t0, both prisoner at exactly t+180, no hits. Happy path works.
- E3 no order, wardens stand on lips: 21181 AttackMelee warden at t+15; wardens FleeAndCower but cannot leave the plot island (stay put); warden 24671 downed t+360 (3 Stab from 21181); then 21181 WALKS the ring 63,61->67,61 to melee the other warden. CONFIRMS premise of T3: any unpinned held raider melees any colonist on a lip and roams to reach one. Damage log shows 'RM_StunningSpores' from a raider's stab (ODD, to explain).
- site colonists 475/478/483 are on the map and 478 walks toward the moat (BuildRoof>73,65): possible interference, note.
- E4 capture 21233 alone: done t+180; other raider dormant in 'Wait' until t+330 after load, then walks the ring to melee the warden.
- E5 extra lordless raider beside lip: wandered off, no attack; capture done. (no information on T3)
- E6 21181 ordered AttackMelee on the capturing warden: stab landed at t+90 of the hold (Stab + RM_StunningSpores); capture STILL completed t+180. REFUTES 'a hit interrupts the warden's capture job' (T4 by hit).
- E7 21181 moved to outer row 63,60, capture ordered from plot: warden waits at 63,62; raider wakes t+90, walks in to attack, is pinned at 63,61, prisoner at t+300. T1 alone does not stall (raider comes to the warden). GiveUp exists in source after 6 repaths (~360+ ticks) if he never comes.
- E8 two captures staggered 60 ticks: both complete (t+180, t+240). REFUTES T7 (first finished capture ends the others).
- Trace T050452 (visit 8) still shows a pin ending while its warden is in CD (T2): Pin() is a no-op when victim already pinned, so a re-entered hold (after Repath) does not extend the old pin's expiry -> gap. Not yet reproduced.
- r1-r3 full scene (trace now top-level moatCaptureTrace): r1 PASS; r2,r3 only 1 held -> UNMEASURED (loop still burns 900 ticks); r3 control FAIL: 2 raiders swam with leaf down (24625, 24630), 3 crossed. Evidence r1/r2/r3.json.
- MINED visit 8 failing runs (mine.py over recorded calls): run 034943 stalled victim 21211 stood at 71,66 (OUTER column, no plot lip touches) from order t=1144 until ~1684 (540 ticks); run 042734 stalled victim 21181 at 61,60 (OUTER row) at t+60, at 61,61 only by t+480. Both wardens able. Both = warden waited at nearest lip, 6 repaths x ~60 ticks ran out (GiveUp ~t+330..370) before the raider came into touch.
- E9 (Wait order expired after 60 ticks; raider walked in, captured t+300) but warden DOWNED at t+315 by 2 stabs: one from his own victim during the walk-in before the pin, one from the OTHER unpinned raider. Fault 2 (warden downed beside held raider) reproduced; instigators named by damage_log.
- E10 *** STALL ON DEMAND ***: 21181 moved to 63,60 (outer row) and downed; capture ordered from plot lip 63,62. Warden in RM_CaptureDown t0..t+315, job gone by t+360 (GiveUp), verdict stays 'Allowed held=True prisoner=False'; no message. Other raider 21233 walks ring and stabs him (FleeAndCower, cannot leave island). Keeper save TP_MOAT_STALL_FAILING_MOMENT.rws; pictures stall_moment.png, stall_zoom.png, after30.png.
## CAUSE (measured)
- Fault A (capture stalls, warden able; 'prisoner flag backslides' symptom): CaptureDown needs the warden 8-adjacent to the victim. A held pawn on a pit square that no lip REACHABLE BY THE WARDEN touches (outer column of the 2-wide moat from the plot island; centre of a 3x3) makes the warden wait at the nearest lip; RM_PitRoomMath.CaptureRepathLimit=6 x CaptureRepathPauseTicks=60 then GiveUp, silently. MOD.
- Fault B (warden downed): any held raider not currently pinned (victim before the pin, victim of a waiting/given-up warden, a raider with no warden) melees any colonist on a lip square and walks the pit floor to reach one. 2-3 stabs down an unarmed warden. MOD design gap (melee across a >=3 m lip allowed).
## Looks
- Look 1 (06:34) failing moment: vitals no critical, hostiles 2 (1 downed), no modal (Dialog_DevPalette open, dev tool, not blocking: EXPECTED harness). ODD: raider Lips (21233) is DRAWN at ~68,61 while pawn_get/site_state/list_pawns say 64,61 and his stab landed on the warden at 63,62 (3 captures agree). Unexplained yet (theory: PawnTweener frozen while bridge steps ticks with the game paused). Revisit in exploration.
- ODD: damage_log shows RM_StunningSpores on a Mercenary_Slasher's Stab (21181). To explain.
## FIX BUILT (not yet live-tested) — uncommitted paths in the clone
- RM_PitRoomMath.cs: CaptureReach (touch OR at rim + line of sight + within Interact radius 6), MeleeAcrossLipDenied.
- Superdeep/RM_PitRooms.cs: CaptureInReach(warden,victim) replaces AdjacentTo8Way in reach+hold; CaptureGaveUp message; MeleeAcrossLipDenied(pawn,thing).
- Superdeep/RM_Patch_PitLipMelee.cs (new): prefix Pawn_MeleeVerbs.TryMeleeAttack; BestAttackTarget validator for melee searchers.
- RimMandrakeFlowWorksMod.cs: setting pitLipMeleeDeniedEnabled (default true), checkbox "No melee across a pit's edge". Keyed RMFlow_CaptureDownGaveUp.
- SelfTest/RelativeRulesChecks.cs: cases PitCapture_takes_from_the_rim_without_touching, PitLip_no_melee_across_a_pit_room_edge. RED with parent behaviour planted (2 FAIL), GREEN on fix 11/11 (`selftest_flowworks_stock.py --only 'PitCapture_*,PitLip_*'`).
- concept_scenes.py: moatCaptureTrace + moatWardenHits (top-level receipt keys), _capture_trace_line, _hits_on.
- DLL built (winbuild FlowWorks). Deploy plan: 3 drift files (dll, srchash, Keys.xml). NOT yet applied.
- Owner ruling that makes touch 'our own rule': PIT_SUPERDEEP_COLLAPSE_1 [B-item] 2026-09-17 'capture down require the warden ADJACENT to the lip'. Bars: drained_hole_is_a_prison scenario = 'two DOWNED raiders ... capture from the rim' (a downed raider on a far square is exactly E10).
## Swimmer with leaf down (RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMER_PAST_LOWERED_LEAF_AGAIN)
- Reproduced in r3 (2 swimmers). swim.py over r3 + visit-8 T034521: 3 of 3 swims are at x=67, z=60/61 = moat squares directly east of the 1-wide deck (x=66), pathCost=60, while other raiders stand on the deck/leaf head.
- ctl.py (deck-block experiment): raiders walk THROUGH each other on the deck (B at 66,61 with A at 66,61). REFUTES 'collision with a pawn on the deck forces the swim'. ctl.py's RING flag wrongly counts deck squares; raiders were not dormant so the test was not clean.
- Standing guess (~55%): 2 swim squares cost 120, inside the pathfinder's slack beside a 1-wide deck. Not proven. Leave on its item with this evidence.
## Reload
- testpilot_reload said HOLD (2 useful tests on running game); both done (swimmer probes). Next: reload rule again, deploy --apply, restart ArchBig, E10 again (expect prisoner), E3 again (expect no stabs), then 3 counted scene runs.
## AFTER THE FIX (published 1c053b325bc5; deployed ArchBig; 2 reloads by rule R3, launch 130 s and 114 s measured)
- f10: downed raider on outer row 63,60, warden at 63,62: prisoner at t+180 (was: never, job gone ~t+330). f3: wardens on the rim 600 ticks, hits [] (was: downed t+360). f3_off (setting off): raider's Stab lands again -> the switch works both ways. Setting restored True.
- jawa/harmony_patches typeName RimWorld.Pawn_MeleeVerbs (NOT Verse.) shows RM_Patch_MeleeVerbs_PitLip.Prefix. First deploy lacked it: .cs not on the csproj Compile list (now asserted in the C# selftest).
- Scene runs after the fix: c1 all rows PASS; c2 capture PASS, control FAIL (1 swimmer); c3 swim FAIL, 0 held; c4,c5,c6: 1 held each -> capture UNMEASURED, but each held raider stood on the OUTER row (68,60 / 67,60 / 67,60) and was captured from 2 squares at exactly t+180; new row MOAT_rim_wardens_not_stabbed PASS x3. Post-fix: 0 capture FAIL, 0 wardens downed in 6 runs.
- Whole-scene three-in-a-row NOT met: blockers are other faults (filed): swim row sampling, swimmer beside the lowered leaf, and fewer than 2 held at the drain (raiders cross the 2-wide moat before it drains).
## Surprises scored
- big-pit look at start: EXPECTED (brief). Dev palette window: EXPECTED (dev mode). RM_StunningSpores on a pirate's stab: ODD -> EXPLAINED (pawn_get: Human21181 wields RUT_FungalMantisScythe; RM_FungalMantisClaw tools carry extraMeleeDamages RM_StunningSpores). Raider drawn 4 squares off his logical square: ODD -> filed RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE. Warden downed at rim: ALARMING -> real bug, fixed. Colonists FleeAndCower in place on the plot island: EXPECTED (no path off the island, drawbridge raised).
## NOT DONE
- Third merged ticket (held raider read NotHeld one square out of a 4 m trench, sc_pit_trap_raid) not traced.
- Big-pit owner look not restaged on ArchBig (design/concepts/FlowWorks/version/in_game/visit_8/evidence/bigpit plan+stage).

# Continuation 1 (2026-11-23 07:48 PST): the third fault, RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_4M_TRENCH_ONCE
## State
- 07:55 PST: no game free [measured, game_lock.py query all + bridge who]: ArchBig = ExplosiveKnockback visit 4 (took it 07:50),
  ArchSmall = Pyrelands visit 7 (since 05:03), Steve1/Steve2 = testq jobs. No take made, nothing forced.
- Published 0613b8a45863: ptrCaptureTrace (30-tick trace in _pit_trap_raid's capture window) + selftest check + trench.py.
## What the old evidence says (visit_2/evidence/exp/sc_pit_trap_raid_20261121T0823_gameb_fixed.json) [measured]
- Raider Human21236 (Grenadier_Tox, PirateWaster raid of 10) fell at 63,60 tick 243, held=True at 302. Warden Human21304 ordered
  RM_CaptureDown from lip 63,61 (NORTH). At tick 1202: NotHeld at 63,59 = the SOUTH bank, the raid's side, across the 1-wide
  trench from the warden. Warden downed. The second held raider (21240) was gone from the map (reply None).
- Ladder reads (list_things RM_LadderPortable) stop at tick 302: nothing was read between 302 and 1202.
- The mod's own rule: a portable ladder spans 3 m at most (FETCH_DEPTH note in concept_scenes.py), so a fetch by ladder into a
  4 m trench should be refused. If that held on 51e9d9ce4a, a ladder fetch is NOT how he left.
## Theories (written before any experiment)
- U1 FETCH: a comrade set a ladder on the south bank and he walked out. Predicts: RM_LadderPortable at 63,59/63,60 and a free
  raider's fetch job before he moves; held=False while still in the pit (LadderLetsOut). Against: the 3 m ladder limit.
- U2 EJECTED: his square became unwalkable and vanilla moved him (Pawn_PathFollower.TryRecoverFromUnwalkablePosition), or a
  position write with no path (a carry and drop). Predicts: a jump between two reads with no ladder, job unchanged.
- U3 HOLD LAPSED IN PLACE: IsHeld went false at 63,60 (the width clause of a 1-wide trench, a lid state, a corpse or item
  changing the pocket), then he walked out by an ordinary path. Predicts: held=False at 63,60 one read before he moves.
- U4 MELEE CHASE: his attack job on someone on the bank moved him by a step the StartPath / TryEnterNextPathCell veto misses
  (now also behind pitLipMeleeDeniedEnabled, 1c053b325bc5). Predicts: job AttackMelee, held=True on the last read in the pit.
- U5 CAPTURE SIDE EFFECT: the warden's capture moved him before the warden was downed. Predicts: the warden's job active at
  the move. Against: he ended on the far bank from the warden.
## Experiment ready, not run (no game)
- python.exe -u design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench.py <out.json> <width 1|2> <ticks> [--wardens]
  (width 1 = the old 1-wide trench; the raid stays on the map; receipt keys holdTrace / holdLeft; row TP_held_stay_held).
## Next
- take a game when one is free (FlowWorks 1c053b325bc5 must be deployed on it), run trench.py 1 1500 --wardens, read holdLeft.
- U6 JUMP PACK (added 08:25 from RM_RaiderTrench.cs, before any experiment): the mod hands raiders jump packs to cross trenches
  (owner card Q7; MinClimbCellsForJumpPacks 20). A jump is a pawn flyer: no path step, so the step veto never sees it.
  Predicts: a jump job on the held raider (or a jump pack in his gear), a move of more than 0 squares between two 30-tick reads
  with held=True on the last read in the pit. The old trench was 9 squares; whether the map had 20 dug squares is unread.
- U7 CROSSING LADDER: the raid, cut off by the trench across its path (old staging), set its own crossing ladder
  (JobGiver_RM_CrossTrench) on his square; LadderLetsOut then frees him. Against: "4 m is past a 3 m ladder" (pinned).
- 08:04, 08:11, 08:20 PST polls: no Archmagi game free; ArchBig now on the ExplosiveKnockback tier (a FlowWorks run there needs
  a tier reload). Steve2 rolled to a new testq job at 08:09 (the lane refills itself).
- U8 KIDNAP (08:55, before its experiment): a held raider beside a colonist downed on the rim takes vanilla Kidnap (seen as a free raider's job in t3); the carry-and-exit walks him out. Predicts: job Kidnap on the held raider, then a place outside the pit.
## 09:25 PST *** THE FAULT ON DEMAND (Steve1, run t18) ***
- Took Steve1 08:32 (guard gen 2429), flowworks tier (12 active), FlowWorks in sync with origin. Runs t1..t17: 0 of 31 held left.
- t18: Human21277 stood on lidded pit square 60,62 (held=False, descents=0) at t=1442 and 1502; the deck gave way at 1533
  (fall=10.3, Stab from the spikes, DOWNED). t=1562 and 1592: held=True, Wait_Downed at 60,62; comrade Human21258 on the strip
  61,63 has job RM_RaiderFetchFallen>60,62; ladders=[] on every read. t=1622: 21277 lies at 62,63, held=False, still downed;
  21258 walks off. A comrade lifted a downed man out of a 4 m pit from the rim with no ladder. Evidence t18.json (scratch).
- Mechanism (source): RM_RaiderFetchFallen.TryFetch takes "CanReach(fallen.Position, OnCell)" as "a way down" and then gives the
  carry job, whose driver walks to ClosestTouch: from the strip he touches the man and picks him up. U1 was half right (a fetch,
  no ladder); U2-U8 refuted (U8 by t7: free raiders kidnapped the downed colonists, the held raiders stayed).
- Theory V1 (before the experiment): the reach answer was stale for some ticks after the lids fell (pit read as deck).
  Predicts: a held raider downed 120+ ticks after the fall is NOT lifted out. V2: CanReach says yes whenever. Predicts: lifted.
- t19, t20 (--down-held: a held raider downed 120 ticks after the fall, raid on the map, 600 ticks): no fetch job, he stayed.
  Fits V1 (the reach answer is wrong only around the lids' collapse); not proof (no read of which raiders were under fire).
- t21, t22 RED ON DEMAND (--down-held --order-fetch): the carry job RM_RaiderFetchFallen ordered on the nearest free raider;
  within 30 ticks the downed man lay outside the pit, held=False, ladders=[]. Keeper save TP_FETCH_LIFTS_FROM_RIM_4M.rws and
  picture fetch_red.png in D:\ClaudeWork\rimmandrake\testpilot_pit_capture_faults (also on Steve1's Saves folder).
- FIX (building): the rescuer walks ONTO the fallen man's square (GotoThing OnCell) and the pickup asks
  RM_RaiderTrenchMath.FetchLiftAllowed(rescuer depth, fallen depth, climb limit); a refused lift is remembered so the giver
  does not hand the job out again at once. C# case RaiderFetch_no_lift_from_the_rim_of_a_deep_pit.
- Steve1 released 09:41 PST for the lane while the build runs (machine load 35, the C# selftest stage copy is slow).
## Looks
- Look 1 (09:14 PST, Steve1 after p3): calm site restored, 3 colonists, paused tick 3, Clear (forced), 57F spring, no modal
  (ImmediateWindow + Dialog_DevPalette), no raiders. EXPECTED (scene restore; census 3 pawns).
- Player.log (Steve1): 1 NullReferenceException (duplicate stacktrace ref) after "Resolved path returned no nodes ... (60,0,60) ->
  colonist, for Arkady"; 6 such lines in ~20 runs, each beside FlowWorks' own "reach residual: CanReach said yes, A* found
  nothing" for a raider on a first-row pit square. The line is vanilla's for ANY path not found. No raider of t6 is named Arkady.
- t6 stray: free raider Human21297 (Bagdark, Thrasher) stood at the rim 60,59 to t=602, on pit square 60,60 from t=632 to 1052
  (AttackMelee on a far colonist), then walked out over the strip. Explained 2026-11-24: each stand is one 450-tick step of a
  climber in gear (vanilla MaxMoveTicks; Thrasher wears RM_ClimbingGear 8 %). gear_climber.py (ArchBig g3, ArchSmall g4): in 480, out 450, never
  held; without gear he never enters and is held if put in. His own gear in t6 was not read.
## The melee rule of this sitting was replaced (owner ruling, 2026-11-23, RIMMANDRAKE_ENACT_PIT_MELEE_REACH_EQUALS_CLIMB_SIZE_DECIDES)
- "No melee across a pit's edge" (3 m pit rooms, both ways, every size) is gone. Melee reach is now the climb criterion:
  `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.8. Capture from the rim is unchanged. Live: UNRUN.
## 10:25-11:15 PST the fix, both ways
- d15dd762b231: RM_RaiderFetchFallen walks ONTO the fallen man's square (OnCell) and lifts only when
  RM_RaiderTrenchMath.FetchLiftAllowed(rescuer depth, fallen depth, climb limit); a refused lift is not handed out for 250 ticks.
- Live, Steve1 (retaken, guard gen 2431, FlowWorks DLL deployed, restart 41 s): ordered fetch BEFORE: lifted out 2 of 2 (t21, t22);
  AFTER: 0 of 2 (g1 job ended at once, g2 job ended inside 60 ticks; the man stayed held). sc_fetch_fallen PASS 2 of 2 (3 m, ladder,
  brought out). sc_pit_trap_raid PASS 3 of 3 before the fix (p1-p3, new row) and 3 of 3 after (q1-q3). Player.log after the fix: 0
  exception lines, 0 "Resolved path returned no nodes" in 7 scene runs.
- C# case RaiderFetch_no_lift_from_the_rim_of_a_deep_pit: FAIL with "return true" planted, 11/11 on the fix
  (selftest_flowworks_stock.py --only 'RaiderFetch_*,RaiderTrench_*'). Four earlier attempts timed out waiting on the shared
  build lock (other FlowWorks runs), not on the case.
- Filed: RIMMANDRAKE_TRACE_FLOWWORKS_RAIDER_IN_OPEN_PIT_WALKED_OUT (the t6 stray raider; explained 2026-11-24, above).
- Steve1 released 10:50 PST, left UP on the flowworks tier (the lane swaps tiers itself; ModsConfig backup
  deployed/config/ModsConfig.before-tier-flowworks.xml on Steve). Keeper save TP_FETCH_LIFTS_FROM_RIM_4M.rws:
  D:\ClaudeWork\rimmandrake\testpilot_pit_capture_faults and Steve1's Saves folder.
- NOT done: the staleness theory V1 (why TryFetch's CanReach said yes right after the lids fell) is unproven; the fix does not
  depend on it. The big-pit owner look on ArchBig was not restaged (ArchBig is driven by the ExplosiveKnockback visit).
- Surprise book: biome AridShrubland (jawa/map_info, live). 1 filed, 1 real_bug, 1 explained.
