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
