<!-- modledger view, generated: never edit (python3 src/RimMandrake/rimflow/modledger.py views --mod ExplosiveKnockback) reducer=1 shards={"BACKFILL":302988,"DISPATCH":14103,"HOLDER.run-1794813483":1382,"HOLDER.run-1794824768":1788,"HOLDER.run-1794830532":2304,"HOLDER.run-1794860741":975,"HOLDER.run-1794865314":728,"HOLDER.run-1794895533":983,"JUDGE.judge-1794890427":18837,"OWNER":1207} body_sha256=f4da5876b7943623d23955f00af2f026740a5bba12d6be7ff3a4fd0a55e1ffed -->
# ExplosiveKnockback — mod ledger packet
version 0.1.0 · stage blind_challenge · 496 events in 10 shards · reducer 1
holder lease run-1794895533, token 10, last active 2026-11-17T06:20:39Z
holder session 25001256-a0ed-4605-85e3-e0c7442bec90, context 94977 of ceiling 400000

## Last checkpoint (HOLDER.run-1794865314, 2026-11-16T21:43:27Z)
- done: advanced ExplosiveKnockback from offline_build to blind_challenge: every Stage 3 exit test passed; cover-break REAL MISS closed at a9eedde493 (tests added only, no assertion weakened); certificate rerun 81519824c0
- next: Run blind cycle 1 of this visit (Stages 4 and 5, tests first) on the files changed since the last cycle, cover break included
- ruled out: any not-met reason to sort: maturation.py next listed none

## Open findings (46)
- RIMMANDRAKE_RETIRE_UNUSED_CONTAINER_SHOVE_KERNEL [open, polish · bars closed_container_holds]: RM_KnockbackMath.ContainerShove (slide-or-jolt, parameter lightMassLimit) is called by no game code; ThrowContainer thr…
- RIMMANDRAKE_STAGE_KERNEL_SELFTEST_COPY_INSIDE_LOCK [open, polish · bars inv_kernel]: selftest_explosiveknockback_kernel.py copies RM_KnockbackMath.cs into the machine-wide ExplosiveKnockbackSelfTest build…
- RIMMANDRAKE_RECORD_FULL_LAST_LINE_IN_TEST_TABLE_RUNS [open, polish]: test_table.json runs_today.last is truncated at 200 characters (T_FW_COVER) and for T_RESTORE holds a Python SyntaxWarn…
- RIMMANDRAKE_ASK_GOODS_WILD_FACTOR_BECOME_A_SLIDER [open, polish · bars settings_scale_and_switch, goods_arc_spin_rebound]: The goods wild factor ships as a constant 1.6 because adding a saved setting (goodsThrowWild) turns T_STAGE3_SCENES red…
- RIMMANDRAKE_REPAIR_WILD_RATIO_BAND_FOR_INTEGER_CELLS [open, problem · bars goods_arc_spin_rebound]: scenes.json sc_storeroom_mortar requires every wild-to-kernel ratio between 1.3 and 2.0, but integer cells make any cor…
- RIMMANDRAKE_READ_WILD_CELLS_FROM_ITEM_MOVE_NOT_REQUEST [open, polish · bars goods_arc_spin_rebound]: scenes.json says each good's request line carries its kernel cells and wild cells, but the request line is written at E…
- RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST [open, polish · bars inv_proof_scenes]: proof_restore_check.py does not see a proof's static_call Settings with a variable args= (storeroom_pit_proof.py arm():…
- RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER [open, polish]: setting(typ, field, *value) writes settings through a vararg wrapper the restore checker misses, and liquidPumpEnabled…
- RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN [open, polish · bars inv_proof_scenes]: Five proof-scene live verdicts were weakened (flying_off skip, goods wall position, deep water, container 0 cells, fire…
- RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME [open, polish · bars pawn_flight_arc]: RM_PawnFlyerPatches.cs holds a static Dictionary<Pawn,Job> Hauling, set at every launch and removed only at a knockback…
- RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED [open, polish · bars closed_container_holds]: RM_KnockbackMath.JoltOffset's doc promises a decaying shake, but only the bound is tested; a planted no-decay (PF_MATH_…
- RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT [open, polish · bars pawn_hits_pawn_stops]: In RM_KnockbackMath.Resolve, a pawn thrown over a sandbag into a pawn, wall or door backs off the sandbag (often to 0 c…
- RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS [open, problem]: Task: Explosive Knockback draws its own bigger blasts (own RM_KnockbackBlast* FleckDefs for debris, smoke, soot, sparks…
- finding:RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars thrown_into_pit_falls, inv_pits_receive: sc_storeroom_bomb_pit expects a thrown stack landing on a covered pit cell to fall through with one descent and destroy the cover, but Building_SpanDeck's load sums living walking pawns only and RM_ThingFlyer_Knockback never touches a cover.
  proposed fix: Build it where the builder chooses; the flyer's landing on a covered pit cell (Knockback side) touches the least. Widening SpanDeck's load would change FlowWorks for every item dropped on a deck.
  accept: Live cover row of knockback_runner.py --scenes storeroom_bomb_pit --ticks 900 (cover=True), plus an offline check that a stack landing on a covered cell destroys the cover and descends once; watch it fail on the base.
- finding:RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars gas_goes_clump_by_clump, our_gases_burn, inv_gas_chain, inv_gas_tags: Flammable gas should go off clump by clump, each clump scattering goods and shoving people 1 cell (no damage, once per 2 s, never breaking pit covers); needed an opt-in flammable tag on our gases including the Cauldron's.
  proposed fix: Opt-in RM_KnockbackFlammableGas DefModExtension tagged via PatchOperationFindMod, plus a hook where fire reaches a tagged gas cell firing a radius-1.9 burst per clump cell.
  accept: gas_clumps live scene PASS (red with the registration removed); owner look at save EK_LOOK_GAS_CLUMPS_MATRIX_20261112 still owed.
- finding:RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN [open, problem] by BACKFILL, 2026-11-16T11:37:18Z: The game copy still had Patches/RM_Knockback_ClosedContainers.xml, which tags Cold Storage lockers (RM_AncientStasisLocker_*, RM_EvaporativeCrock) closed although they draw their contents. The repo deleted it after the owner's open-storage ruling; 5 DIRTY files also needed full review before deploying.
  proposed fix: Review the 5 DIRTY files, then run deploy_custom_mods.py --mod ExplosiveKnockback (read the plan, expect a '-' line for that patch), then --apply.
  accept: none filed as a test; the deploy plan must show a '-' line for the ClosedContainers patch.
- finding:RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars heavy_stack_knocks: RM_ThingFlyer_Knockback never checked pawns on its path, so a flying heavy stack (>= 10 kg, dl_heavy_threshold) did not hit a person.
  proposed fix: In the carrier's Tick, when the ground cell changes and a pawn stands there with a stack >= 10 kg: 2-5 Blunt and about 0.5 s stun, then land the stack there; lighter stacks pass; a setting to turn it off.
  accept: Proof row heavy_knock: heavy stack vs light stack past one colonist, shared control; red with heavyGoodsKnock off and with heavyGoodsMinMass 0.
- finding:RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars open_shelf_scatters, closed_container_holds, inv_closed_guard, inv_container_shove, inv_shelf_skip: The knockback flush exempted every storage building's contents (InStorage, RM_MapComponent_Knockback.cs:399), so goods on open shelves never flew; the walk row light_things.item_on_a_shelf_stays asserted that old rule.
  proposed fix: Replace InStorage with HeldReason: open storage throws; closed (hidden-contents comp/showContents=false or RM_KnockbackClosedStorage tag) keeps contents and gets a small shove (ShoveContainer); flip the walk row.
  accept: storeroom_pit_proof.py --storage live: open-shelf goods thrown, closed container's goods stay, container shoves; walk row reversed to item_on_an_open_shelf_scatters.
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars barrage_frame_budget, frame_time_probe, every_good_moves, walk_storeroom_raid: Task: prove all-fly (no overflow cap) holds at most 50 ms per frame on a mortar barrage and a long gas chain on Archmagi; build the frame_time_probe first; owns walk scene walk_storeroom_raid and showcase sc_storeroom_bomb_pit.
  proposed fix: Build frame_time_probe with a sanity probe, run the full list on Archmagi, run the gas chain and sc_walk_raid (reload, repeat, second order).
  accept: none filed; measured bar 'no frame over 50 ms' is PASS at Normal speed, FAIL at Superfast (vanilla too).
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars closed_container_holds, open_shelf_scatters, inv_closed_guard: Closed-container rule must be re-proved live with LWM_WeaponsLocker, no shelf or hopper tagged closed; the earlier pass staged a ShelfSmall tagged closed, invalid under the owner ruling that anything drawing its contents is open.
  proposed fix: With a PROOF build and lwm.deepstorage, run storeroom_pit_proof.py --storage (default LWM_WeaponsLocker) and scenes sc_closed_containers, sc_storeroom_bomb_pit, sc_settings_sweep, sc_open_storage; delete or restage the two misleading saves.
  accept: storeroom_pit_proof.py --storage with NAME_CONTAINER_CLOSED reading CLOSED with no tag, plus the four scenes passing as written in scenes.json.
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars inv_which_blasts: Task: stage and prove sc_blast_kinds' Outer Rim lanes live: Flame 50 (not 25) and untuned 50 at unpatchedHarmfulPercent 50; modded lane 100 at 100; control at 0 throws nothing.
  proposed fix: Build the blast_kinds scene in RM_KnockbackProof (scene, verdict, mutation) staging OuterRim_SonicGrenadeProj and OuterRim_PlasmaGrenadeProj, then prove it live.
  accept: Live: Flame 50 and untuned 50 at unpatchedHarmfulPercent 50; modded lane 100 at 100; control at 0 throws nothing.
- finding:RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars inv_container_shove: sc_closed_containers jolt rows print drawnOffset=UNMEASURED in RM_KnockbackProof_StageThree.cs though the jolt has been drawn since 587529cee1; the only counters, JoltFrames/JoltMaxOffset, are map-wide statics updated per drawn frame, not per container or tick.
  proposed fix: Add a per-container read (container id to max drawn offset while its jolt lasts), replace UNMEASURED with the measured value, and pass the row only above zero; watch it fail on a planted break first.
  accept: Live run: sc_closed_containers jolt rows report a measured drawnOffset above zero, and at/below zero under the planted break (jolt drawn at zero).
- finding:RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS [open, problem] by BACKFILL, 2026-11-16T11:37:18Z · bars inv_proof_scenes: Existing scenes in RM_KnockbackProof.cs lack start assertions and real controls, per the 17-row script_audit in record.json; the coverage judge found scenes lacked real controls.
  proposed fix: Rewrite each scene to assert its start (INVALID otherwise) and run the control named in scenes.json, following the script_audit mapping (plan.md step 8).
  accept: none, no acceptance test filed.
- finding:RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST [open, problem] by BACKFILL, 2026-11-16T11:37:19Z · bars closed_container_holds: The container jolt draws a second copy of the graphic at the offset over the unmoved original (MapComponentUpdate b.Graphic.Draw), so a paused frame shows a doubled outline (~0.1 cell at t8).
  proposed fix: Draw the jolt as a move of the container rather than as a ghost copy over the unmoved original. The record states no concrete change beyond the title.
  accept: none, a visual judgement in motion (owner or a judge on a short capture).
- finding:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST [open, problem] by BACKFILL, 2026-11-16T11:37:19Z · bars inv_gas_chain, closed_container_holds, inv_pits_receive, inv_proof_scenes, barrage_frame_budget, inv_recovery: Task: run Stage 6 in-game acceptance visit 1 (56 checks) for ExplosiveKnockback 0.1.0 through the live driver (maturation.py launch). Result: 47 pass, 4 fail, 5 unmeasured, exit_met false.
  proposed fix: Fix the failing and unmeasured items filed from the visit: the vent-gas chain stopping at one clump, the control-pit stack escaping the raised ladder, the heavy closed locker, the three absent stage-6 scenes, and the container jolt ghost; then rerun.
  accept: Exit block of visit 1 (design/concepts/ExplosiveKnockback/version/in_game/visit_1/SUMMARY.md) must read exit_met true; maturation.py next agrees with the current block.
- finding:RIMMANDRAKE_FILL_HEAVY_LOCKER_REAL_MASS_ESTIMATE_FELL_SHORT [open, problem] by BACKFILL, 2026-11-16T11:37:19Z · bars closed_container_holds: In sc_closed_containers the heavy-locker fill loop in RM_KnockbackProof_StageThree.cs adds estimated gun mass (GetStatValueAbstract, total += gm) and never re-reads Mass(heavyBox), so the locker can stop short of 76 kg and the scene reads INVALID (74.9 kg once).
  proposed fix: After each placement set total = Mass(heavyBox) instead of accumulating the estimated gun mass.
  accept: none offline (runtime mass); live: knockback_runner.py --scenes closed_containers,closed_containers_control --ticks 300, 10 runs on a fresh minimal map, no heavy=INVALID.
- finding:RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN [open, problem] by BACKFILL, 2026-11-16T11:37:19Z: In the walk save EK_VISIT2_WALK_20261115, dark blotches and haze lie over the four stations east of gas_chain (open_storage, heavy_knock, spared_states, goods_obstacles); presumed leftover Cauldron vent gas or its burn drifting from gas_chain (162,12), unproven.
  proposed fix: Look at the save and take a vent-gas density read to confirm or refute the leftover-gas cause.
  accept: none, needs a look at the save and a vent-gas density read.
- finding:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES [open, problem] by BACKFILL, 2026-11-16T11:37:19Z · bars walk_storeroom_raid, gas_goes_clump_by_clump, blast_breaks_pit_cover: sc_walk_raid failed 6 rows at visit 2 (run 2 on 61567a7b75): reload census 11 before save vs 7 after, cover broken with 0 descents, gas cells burst twice in 900 ticks, one request (Human38765) without outcome. FRAME_BUDGET is UNMEASURED by construction.
  proposed fix: Classify each row MOD vs HARNESS; use saveload_triplet for reload, record ev.grenade and ev.gas_bursts, pair blast-killed pawn with its corpse; each MOD cause gets an offline selftest red before its fix.
  accept: Live: the sc_walk_raid row command in design/concepts/ExplosiveKnockback/version/in_game/visit_2/rows.jsonl exits 0 (exit 1 on 61567a7b75); each MOD cause also gets an offline selftest red before its fix.
- finding:RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST [open, problem] by BACKFILL, 2026-11-16T11:37:19Z · bars the_spared: On the owner's full list the staged sleeper in spared_states is not in its bed at the blast (label INVALID), though it passes on the minimal list since a987289bca. Some full-list mod gets the sleeper up or stops LayDown.
  proposed fix: Trace with set_colonist_job_logging on the sleeper to find the full-list mod that gets it up or stops LayDown.
  accept: none, live staging.
- finding:RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE [open, problem] by BACKFILL, 2026-11-16T11:37:19Z · bars inv_proof_scenes: Task: run the blind offline challenge (Stages 4 and 5, tests first) on Explosive Knockback 0.1.0 by hand for one cycle and write down its record format.
  proposed fix: Run lane 1 and lane 2 (code review, planted faults, reruns); fix Problems red-first; Conductor rules on the 4 NOTED_FOR_CONDUCTOR faults in cycle_1/lane2/faults.json, then starts blind cycle 2 on the changed files.
  accept: none, no acceptance test filed; cycle exit was NOT met (inv_proof_scenes red with T_RESTORE known red, and Problems found).
- finding:RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF [open, problem] by BACKFILL, 2026-11-16T11:37:20Z: designer_stage repin voided stage 4 (Cold Reader exam) after the barrage p99 rewording re-certified the tree; no exam scenario mentions barrage/frame, so the exam must be refrozen with fresh readers.
  proposed fix: Retake the Stage 4 Cold Reader exam against the re-certified tree with fresh Claude readers (the exam11 route, 3d5eeb0e44).
  accept: python3 src/RimMandrake/rimflow/designer_stage.py status design/concepts/ExplosiveKnockback | grep -c '"stale_from": null' prints 1 (watched failing: prints 0, stale_from 4).
- finding:RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING [open, problem] by BACKFILL, 2026-11-16T11:37:20Z: sc_settings_sweep decides kernel-side settings only in a live run; there is no offline table test showing each setting changes only its own outcomes, and RM_KnockbackMod.cs still saves immuneBodySize.
  proposed fix: Add a selftest beside selftest_explosiveknockback_kernel.py running the sweep lane at default and per kernel-side setting; add an offline Scribe_Values field check; shrink the live sweep to game-side settings plus one Kernel() read-back per setting.
  accept: A selftest where each setting changes only its own row and a coupling mutant (strength also scaling the cap) turns it red; the Scribe_Values check is expected red until the build item lands (immuneBodySize still saved).
- finding:RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN [open, problem] by BACKFILL, 2026-11-16T11:37:21Z: In 0.1.0 a thrown pawn landing on a pawn that walked onto its landing cell mid-flight only writes a land_on_pawn journal line; neither pawn takes damage.
  proposed fix: For 0.2.0, add a kernel landing-bruise function of the thrown pawn's mass (small Blunt, rising with mass, capped, 0 with no pawn on the cell); on landing apply that hit to both pawns and put the amount in the land_on_pawn line.
  accept: Kernel selftest K case: 40 kg < 70 kg < 140 kg amounts, under a stated cap, 0 with no pawn (red today). Live revised sc_pawn_arc: both take the hit, neither is downed, heavy bruises more; empty-cell control gives no hit.
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN [open, problem] by BACKFILL, 2026-11-16T11:37:21Z · bars closed_container_holds, hose_drops_at_takeoff, frame_time_probe, barrage_frame_budget, inv_proof_scenes: 11 of 59 bars had no runnable check, so maturation.py next refused every_bar_has_a_check_that_runs. Also, shipped code throws whole closed containers several cells while the locked bar and test say slide exactly one cell.
  proposed fix: Write the five missing proof scenes with control lanes, a frame probe and K-22, plus --real-seconds in the runner. Owner picked 'thrown as built': reword the bar from 'slides one cell' to 'thrown a short way' and make the test follow.
  accept: none as a single command; bars runnable 48/59 -> 58/59 by make_test_table.py, selftest_explosiveknockback_stage3_scenes.py (red 29 on base). Live commands UNRUN in version/test_table.json.
- finding:RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC [open, problem] by BACKFILL, 2026-11-16T11:37:21Z · bars hose_drops_at_takeoff: In 0.1.0 a thrown pawn flies holding its carried thing (MakeFlyer with flyWithCarriedThing: true); the carried stack has no plan of its own. Owner wants it to fly its own trajectory in 0.2.0.
  proposed fix: Stop calling MakeFlyer with flyWithCarriedThing true; plan the carried stack by its own mass and hand it to RM_ThingFlyer_Knockback; a stack over lightMassLimit drops on the takeoff cell.
  accept: Offline kernel selftest K case (70 kg pawn and 10 kg stack get separate plans, stack farther, over-limit stack no plan), static check no flyWithCarriedThing true, and revised sc_pawn_arc in game; each seen red on today's code.
- finding:RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD [open, problem] by BACKFILL, 2026-11-16T11:37:21Z · bars goods_arc_spin_rebound, no_teleport: Thrown goods were despawned and replaced (teleport at RM_MapComponent_Knockback.cs:474) instead of flying; they need an arc, fast spin and rebound off walls until spent at ~70%.
  proposed fix: Arc carrier RM_ThingFlyer_Knockback (merge, no-free-cell fallback, save/load via IThingHolder), spin, rebound chain (keep 70%, max 6 bounces), toggle and sliders, one flyer per stack.
  accept: validation.py chain flying_goods (goods_fly_midair/lands/wall/rebound/off) and proof/goods_flight_saveload.py on a proof build (RmProofs=true).
- finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE [open, problem] by BACKFILL, 2026-11-16T11:37:21Z · bars pit_goods_fetched, inv_pit_floor_haul: Task: prove goods thrown into a pit stay retrievable (a colonist fetches one from the pit floor down the ladder); if haulers cannot reach the floor by the lowered ladder, RM_PitPathing.cs routing is FlowWorks' fix.
  proposed fix: Run scene sc_pit_fetch as a scripted proof row; if haulers cannot reach the floor, file the fix to FlowWorks from the finding.
  accept: none, no command filed; scripted proof row sc_pit_fetch still owed.
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER [open, problem] by BACKFILL, 2026-11-16T11:37:21Z · bars inv_creature_mass_limit, inv_blast_power_damage: Creature throwing used a body-size 2.5 cutoff and a fixed force regardless of blast damage. Needed: a creature mass limit (150 kg Mod Setting) and throw force = type force x blast damage / the type's defaultDamage (blastPowerFromDamage).
  proposed fix: Replace the body-size cutoff with a 150 kg mass limit (grav-ram override 216) and scale force by damage/reference with a switch and a reference percent; Kinetic Arms refDamage pinned per weapon.
  accept: none as a command; oracle is live scene sc_mass_and_power (rat/colonist/muffalo/thrumbo 5/3/2/0 at damage 50, 6/5/4/0 at 100) plus a builder-written kernel selftest.
- finding:RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED [open, problem] by BACKFILL, 2026-11-16T11:45:05Z · bars walk_storeroom_raid, frame_time_probe: RM_FrameProbe.Begin/Stop are internal and jawa/static_call reaches only public static methods, so walk_storeroom_raid's FRAME_BUDGET row is UNMEASURED by construction and the walk can never PASS.
  proposed fix: Add public static string Frame("begin|stop") on RM_KnockbackProof as a bridge read of RM_FrameProbe; rebuild C# (winbuild.py, proof and release) with .srchash; edit walk selftest W0 to expect all rows PASS.
  accept: grep -c 'public static string Frame(' src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs prints >=1 (0 on 3d1f9ae2ca); selftest_explosiveknockback_walk_raid.py W0 all rows PASS with fake Frame stop under 50 ms
- finding:RIMMANDRAKE_READ_WALK_TICK_COST_RUNNING_PAUSED_READ_ZERO [open, problem] by BACKFILL, 2026-11-16T11:45:06Z · bars walk_storeroom_raid: Walk row CARRIER_TICK_COST scored PASS on 0.0/0.0 ms in all 9 runs on record because jawa/time_perf reads 0 on a paused clock (perfprobe paused 0.0, speed 1 4.29 ms).
  proposed fix: Take both readings in the frame act on a running clock; score the row UNMEASURED when the reading is 0 or none.
  accept: python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_walk_raid.py: W21 (perf always 0.0 -> CARRIER_TICK_COST UNMEASURED) FAILs on 8839d0987c (got PASS); all 22 checks PASS after.
- finding:RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER [open, problem] by JUDGE.judge-1794890427, 2026-11-17T05:49:20Z · bars pawn_hits_pawn_stops: RM_MapKbGrid.At answered CoveredPit before looking for a pawn: a thrown pawn passed through a pawn standing on a pit cover and could land on its cell (open pits already blocked). FIXED 42225e0686 red-first; miss_of 4.
  proposed fix: RM_KnockbackMath.PitCell(covered, forPawn, pawnThere) (a pawn there blocks a thrown pawn, open or covered); RM_MapKbGrid.At answers superdeep cells through it, counting only pawns not beneath the lid (RM_KnockbackCompat.IsBeneathCover); K-25 in SelfTest/Program.cs
  accept: python3 design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/check_pit_pawn.py -> rc 0 PASS 6 of 6
- finding:RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND [open, problem] by JUDGE.judge-1794890427, 2026-11-17T05:49:20Z · bars thrown_into_pit_falls: The kernel treats a covered pit as ground (K-08 pins it): a throw planned beyond a covered pit flies over it, and a thrown pawn landing on a cover never breaks it (pawns excluded; FlowWorks only springs on mass, own faction spared). sc_pit_fall's covered lane is not staged. miss_of 4.
  proposed fix: Resolve: a covered cell stops a throw IN it (wall when into-pits off); LandingBreaksCover lets a blast-thrown pawn break it; the pawn landing patch breaks the cover via BreakCoverUnder; K-08 follows; pit_colonist gains the covered lane and filled control. Full: faults.json
  accept: python3 design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/accept_covered_pit.py -> rc 0, covered pit acceptance: 6 of 6
- finding:RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN [open, problem] by JUDGE.judge-1794890427, 2026-11-17T05:49:21Z · bars inv_proof_scenes: 9 planted faults in the proof scenes' verdicts and plans (calibration any cells, hose control always passes, goods-obstacle control never fails, pit probe INVALID never, ...) survived every offline test: no offline decider runs a verdict. NOTED for a re-pin.
  proposed fix: steward re-pin: inv_proof_scenes' offline half is staging, gate and restore; verdict honesty moves to Stage 6 as a per-scene planted-break run (or lift verdict arithmetic into the kernel). Full: faults.json
  accept: after the re-pin or fix: lane2/plant_faults.py on the 9 PF_P/PF_SB/PF_GO/PF_S3/PF_PP faults -> each caught (offline) or each scene FAILs its planted break live
- finding:RIMMANDRAKE_SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS [open, polish] by JUDGE.judge-1794890427, 2026-11-17T05:49:21Z · bars gas_goes_clump_by_clump: Anything on a superdeep cell is skipped in_pit, and IsSuperdeep is true under an intact cover: a gas burst never shoves a pawn standing on a pit cover nor scatters goods on one. Blasts break the cover so it shows only for gas. miss_of 4.
  proposed fix: in_pit = IsSuperdeep && (no cover || the thing is beneath the lid, RM_KnockbackCompat.IsBeneathCover)
  accept: live sc_gas_chain variant: a pawn on a deck beside a burning clump moves one cell; goods on the deck scatter
- finding:RIMMANDRAKE_TEST_WALK_FRAME_JUDGE_OFFLINE_TWO_MUTANTS_LIVED [open, polish] by JUDGE.judge-1794890427, 2026-11-17T05:49:21Z · bars walk_storeroom_raid: validation.py's FRAME_BUDGET judge (mod-on p99 within 10% of mod-off) has no offline case: loosening 10% to 50%, or always PASS, survived every offline suite.
  proposed fix: a --selftest in validation.py (or a selftest file) that calls the FRAME_BUDGET judge with fixed arm dicts
  accept: an offline case: on/off p99 +9% PASS, +11% FAIL, a missing or unlike arm UNMEASURED; PF_V_* then caught
- finding:RIMMANDRAKE_NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX [open, polish] by JUDGE.judge-1794890427, 2026-11-17T05:49:21Z · bars the_spared, heavier_flies_less, goods_arc_spin_rebound, heavy_stack_knocks, thrown_into_pit_falls, pawn_flight_arc, every_harmful_blast_throws: 10 planted faults in game-side callers survived offline as expected for Verse code (grid pawn read, in-bed skip, inventory mass, rebound, heavy knock, landing cover break, no-redirect, landing door, unpatched percent, fire switch): hand them to Stage 6 as planted breaks.
  proposed fix: hand the 10 to Stage 6's brief as planted breaks to run live
  accept: Stage 6 runs each of the 10 as a planted break and its scene FAILs

## Traps (66) — what a reader would otherwise get wrong
- trap:judge-round-count-has-three-answers (design/concepts/ExplosiveKnockback/journal.md:58): Judge round count has three answers (12 / 13 / 19); not reconciled (spec §10).
- trap:97-2-million-tokens (version/VERSION.json): 97.2 million tokens were charged to the Designer stage, 86.5 million of them estimates (`version/VERSION.json`).
- trap:proof-build-versus-release-build (RM_KnockbackProof.cs): Proof build versus release build. Most live scenes exist only in the proof build (`RM_KnockbackProof.cs`, `proof_build_gate.py`); the test queue cannot deploy a proof build today (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
- trap:the-scene-ids-in-scenes-json-are-not (scenes.json): The scene ids in `scenes.json` are not the scene names in the proof code. `scenes.json` entry points name 35 scenes by proof method; `RM_KnockbackProof.Names` holds 41 older names, and only some of the 35 are among them (measured in Stage 2 below).
- trap:three-bar-sets-exist (design/validation_walks/RimMandrake/ExplosiveKnockback.md): Three bar sets exist. The 59 coverage checklist rows are the bars of 0.1.0, and Stage 6 reports against them. The 16 "north-star bars" (his card 2026-11-12, "Approve as written") and the 49 "must be true" rows of `design/validation_walks/RimMandrake/ExplosiveKnockback.md` (measured 2026-11-14
- trap:the-locked-files-moved-after-the-lock (version/bars.md): The locked files moved after the lock. `version/bars.md` pins blobs at `237b791167`; since then `scenes.json` (sc_spared, sc_mass_and_power, sc_settings_sweep), `record.json` (decisions) and `tree.json` (the owner-certify stamp only) changed. The scene edits are test text (creatures chosen by mass, never named
- trap:the-check-script-s-green-side-is-unproven (src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py): The check script's green side is unproven (no build exists to pass it). It does not judge the look: that is a judge agent's call plus a live blast, so a pass would not certify the art.
- trap:forge-sets-dovisualeffects-false-and-draws-its-own (design/RimMandrake/explosion_mods_characterized_2026-11-12.md; Dynamic Effects Forge): Forge sets doVisualEffects=false and draws its own, so our show must not double it.
- trap:the-scene-text-stands-and-the-code-must (design/concepts/ExplosiveKnockback/tree.json; sheet.md:44): The scene text stands and the code must change to match it: the locked certified leaf thrown_into_pit_falls says a thrown good onto a covered pit cell falls through and leaves the cover broken.
- trap:0-1-0-as-built-and-kept-the (design/concepts/ExplosiveKnockback/version/next_version/README.md; sc_pawn_arc): 0.1.0 as built and kept: the pawn lands with no damage, and sc_pawn_arc asks only for the impact line. The bruise belongs to 0.2.0, not 0.1.0.
- trap:gas-bursts-never-break-pit-covers-ignore-shield (Patches (PatchOperationFindMod)): Gas bursts never break pit covers, ignore shield belts and shove a person at most once per 2 s. MayRequire on a top-level Operation is ignored; tag other mods' gases through PatchOperationFindMod.
- trap:perf-of-a-long-gas-chain-40-cell (save EK_LOOK_GAS_CLUMPS_MATRIX_20261112): Perf of a long gas chain (40-cell) is UNMEASURED.
- trap:the-hidden-panel-tag-fix-is-checked-offline (RM_Knockback_HiddenStorage.xml; testq): The hidden-panel tag fix is checked offline only, and the SteveDesktop live proof never ran because the test queue deploys only the release DLL, not the proof build.
- trap:proof-scripts-exit-3-proof-build-required-on (csproj RmProofs=true; validation.py proof scripts): Proof scripts exit 3 'PROOF BUILD REQUIRED' on the release DLL; proof code is fenced behind RM_PROOFS, and the proof DLL deployed was uncommitted, so release must be rebuilt and redeployed.
- trap:the-live-fails-of-sa-closed-goods-stay (item:RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED): The live FAILs of SA_CLOSED_GOODS_STAY, SA_CONTAINER_RULE, SC_OFF_SHELF_GOODS_STILL and SC_OFF_CONTAINER_STILL were staging, not the rule: the 25-HE-shell blast destroys the steel Hopper anywhere in r6 and both wood shelves even with knockback off (probe_hopper3).
- trap:the-station-5-live-pass-10-10-staged (Station 5 storage proof, save EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112): The Station 5 live pass (10/10) staged ShelfSmall tagged closed via CloseStorage; under the owner ruling that anything drawing its contents is open (a shelf is open, period), it no longer proves the closed rule.
- trap:flying-goods-are-not-the-frame-cost-flying (item:RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF): Flying goods are not the frame cost: flying ON and OFF showed no measurable difference at Normal; knockback adds about one bucket at Superfast, where vanilla alone already reaches 50-67 ms.
- trap:the-item-s-premise-is-false-rm-knockbackproof (RM_KnockbackProof.cs SceneNames): The item's premise is false: RM_KnockbackProof.cs has no blast_kinds scene (SceneNames lacks it), so it must be built first. A live run also needs the proof build the queue cannot deploy.
- trap:the-jolt-rows-drawnoffset-unmeasured-is-not-a (RM_KnockbackProof_StageThree.cs jolt rows.Add(...)): The jolt rows' drawnOffset=UNMEASURED is not a failure of the jolt: it is drawn since 587529cee1; only the instrument reads nothing per container.
- trap:caps-tick-cap-shelf-and-items-assert-behaviour (RM_KnockbackProof.cs scenes caps, tick_cap, shelf, items): caps, tick_cap, shelf and items assert behaviour his answers reverse (d_c_all_fly, d_c_wild, d_goods_fly); rewrite or remove them, do not keep them green.
- trap:the-airborne-spared-case-spared-states-must-force (RM_KnockbackProof.cs spared_states): The airborne-spared case (spared_states) must force the flying state with a test hook and read it; never launch a live flight (standing ruling).
- trap:code-reading-forge-is-a-postfix-on-explosion (Dynamic Effects Forge Postfix on Explosion.StartExplosion): Code reading: Forge is a Postfix on Explosion.StartExplosion that only sets doVisualEffects=false and draws its own effect, so knockback receives the same blast. This was read, not run live.
- trap:a-first-detached-run-s-certify-was-refused (concept_tree.py:745 certify; OWNER:1794748404753740828): A first detached run's certify was refused because his card was recorded on this item, not the concept's own item (RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH); certify reads only events on the concept item, newer than the coverage judge verdict. Recording it here does not certify.
- trap:his-wording-card-is-not-a-certificate-an (design/concepts/ExplosiveKnockback coverage stamp (signed_by: owner)): His wording card is not a certificate; an agent re-stamping or treating the card as one would forge his pass.
- trap:a-damagedefs-patch-matching-nothing-logs-nothing-verify (RM_Knockback_DamageDefs.xml): A DamageDefs patch matching nothing logs nothing; verify the patch landed against the live def dump (fire_half read Flame force 0.5 vs Bomb 1.0).
- trap:a-pre-look-judge-saw-contents-drawn-spilled (conductor/ek_round2_20261112/prelook_open/VERDICT.md, container r5): A pre-look judge saw contents drawn spilled outside the closed stasis locker after the throw (container r5). The owner passed the scene and did not raise it; recorded only, no new work.
- trap:the-100-hp-ancient-safe-dies-to-any (container look matrix, ancient safe): The 100 HP ancient safe dies to any HE in reach (vanilla behaviour), so a destroyed container spilling its contents is expected, not a throw failure.
- trap:the-first-live-run-s-6-6-invalid (item:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER): The first live run's 6/6 INVALID was a harness fault, not a mod bug: the proof colonist band of 64-76 kg missed the measured colonist masses (48.75/60.75; worn clothes add nothing).
- trap:staging-all-six-scenes-before-verdicts-leaks-lane (sc_mass_and_power lanes): Staging all six scenes before verdicts leaks lane settings (4 FAIL); a fallen VoidMonolith blocked lane 6 on the first map.
- trap:vanilla-rockets-deal-24-so-they-now-throw (sc_mass_and_power 250_x2): Vanilla rockets deal 24, so they now throw a colonist 1 cell instead of 3 (0.48 factor). The 250_x2 lane statedTable=False only, because a 63 kg colonist ties the capped rat.
- trap:the-brief-s-named-cause-of-the-red (T_RESTORE): The brief's named cause of the red T_RESTORE, the leaks in RM_KnockbackProof.cs, was not the cause: they were already gone since af61b9c206. The red came from 7 other hits: 3 resets in the storeroom proof, 2 files in other mods, and 2 in FlowWorks.
- trap:fix-rows-were-first-recorded-the-wrong-way (cycle_2 fixes.jsonl; maturation.py): Fix rows were first recorded the wrong way round (rc 0 when the fix was missing) or with a <parent Source> placeholder or an uncommitted worktree, so 'not met' reasons were record gaps. maturation.py now refuses placeholders and names inverted rows; a fix's command is a test whose rc 0 means the fix holds.
- trap:a-gas-shove-onto-an-open-pit-drops (scene dl_gas_shove_open_pit): A gas shove onto an open pit drops the pawn in (dl_gas_shove_open_pit), going by the owner's earlier words 'Only if they get blown/forced in do they fall', although the card said to align the scene with the sheet; the owner confirmed it stands.
- trap:whether-the-doubled-outline-reads-as-a-shake (design/concepts/ExplosiveKnockback/version/in_game/visit_1/screenshots/jolt_*.jpg): Whether the doubled outline reads as a shake in motion is unjudged; a paused frame shows a doubled outline.
- trap:the-vent-gas-chain-burning-one-clump-and (item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST): The vent-gas chain burning one clump and stopping (5 of 17 runs) is attributed to the Cauldron's fire spread, not ExplosiveKnockback.
- trap:the-spared-states-and-settings-sweep-fails-were (item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST): The spared_states and settings_sweep FAILs were diagnosed as HARNESS faults, not mod faults.
- trap:the-container-jolt-is-visible-but-draws-a (MapComponentUpdate b.Graphic.Draw): The container jolt is visible but draws a ghost copy over the unmoved container rather than moving it.
- trap:the-invalid-in-visit-3-pass-2-was (design/concepts/ExplosiveKnockback/version/in_game/visit_3/evidence/sc_closed_containers_p2.txt): The INVALID in visit 3 pass 2 was a harness fill shortfall (74.9 kg, below 76), not a mod fault; the rerun (_p2b) PASSED.
- trap:cauldron-must-be-deployed-deploy-custom-mods-py (knockback_runner.py --scenes gas_chain,gas_census,gas_clumps): Cauldron must be deployed (deploy_custom_mods.py --mod Cauldron --apply, game down) first; refile if any run reads bursts=1.
- trap:earlier-passes-of-sc-pit-fetch-were-swims (RM_KnockbackProof.cs pit_goods_fetch): Earlier passes of sc_pit_fetch were swims; also the corpse sat on the pit's edge row so a rim hauler could touch it, so corpse out=True said nothing about descent.
- trap:the-old-selftest-check-k5-counted-1-to (selftest_explosiveknockback_storeroom_bomb_pit.py K5 vs P0-P4): The old selftest check K5 counted 1 to 6 cells freely, so it passed while the game failed; the new P0-P4 use the kernel's real throw length.
- trap:reload-row-11-before-vs-7-after-was (item:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES): Reload row 11 before vs 7 after was not the mod losing things: the census before the save and after the load were a tick apart (PauseOnLoad runs one DoSingleTick) while shell 1's wave was still spreading; also things born after the save take id, cell and count from the RNG.
- trap:cover-rows-zero-descents-were-not-a-mod (item:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES): Cover rows' zero descents were not a mod failure: the site was at fault, since the first storeroom shell broke the cover and dropped its rider before the grenade.
- trap:a-corpse-never-descends-building-pitcover-despawn-takes (validation.py walk_storeroom_raid ev.grenade): A corpse never descends (Building_PitCover.DeSpawn takes Pawn things only), so a rider killed by the grenade makes the cover row SITE UNMEASURED, not a mod failure.
- trap:a-blast-killed-pawn-is-requested-by-name (validation.py B_REQUESTS_MATCH_PLAN, ev.killed_by_blast): A blast-killed pawn is requested by name but executed as its corpse (Resolve), so its outcome names Corpse_<race><id>; unpaired it looks like a request with no outcome.
- trap:frame-budget-is-unmeasured-by-construction-filed-rimmandrake (validation.py --live walk_storeroom_raid): FRAME_BUDGET is UNMEASURED by construction (filed RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED).
- trap:the-five-weakenings-pf-proof-flyoff-skip-unchecked (proof scenes' live verdicts): The five weakenings (PF_PROOF_FLYOFF_SKIP_UNCHECKED, PF_GO_WALL_POSITION_UNCHECKED, PF_GO_WATER_UNCHECKED, PF_ST3_CONTAINER_ZERO_CELLS_OK, PF_ST3_FIREHALF_LANE_NOOP) weaken a verdict, not the mod, and were missed offline; the live run decides these bars at Stage 6.
- trap:sc-storeroom-mortar-s-per-good-1-3 (sc_storeroom_mortar): sc_storeroom_mortar's per-good 1.3-2.0 ratio criterion is impossible in whole cells; it is a scene-criterion problem, not a code fault.
- trap:the-judge-s-row-ran-the-check-with (fix_demos/lint_red.txt, lint_green.txt): The judge's row ran the check with the failing direction as rc 0; it was rerun as a test whose rc 0 means the fix holds, red on the fix's parent ecd0b23322.
- trap:the-green-baseline-clone-carried-uncommitted-k-23 (cycle_3/lane2/fix_evidence/ek_c3_green_gate.jsonl): The green baseline clone carried uncommitted K-23 kernel edits in other files (T_KERNEL red there); the catching suite is T_PROOFGATE.
- trap:the-held-patch-failed-lint-as-written-because (tree.json barrage leaf; selftest_explosiveknockback_barrage_p99.py): The held patch failed lint as written, because a constraint leaf must start with its limit; the leaf now reads 'at most 50 ms for the 99th-percentile frame ... on Archmagi', and the acceptance test checks the three facts in any order.
- trap:the-detached-run-s-work-was-bundled-as (RM_KnockbackProof_GoodsObstacles.cs): The detached run's work was bundled as an orphan.
- trap:the-judge-s-original-red-command-held-the (fix_demos/jj_red.txt; scratch clone ek_c2_fixdemo): The judge's original red command held the placeholder <parent Source> and ran on an uncommitted worktree; it was re-demonstrated with named paths in a scratch clone.
- trap:the-mod-off-control-also-exceeds-50-ms (sc_barrage_perf; FINDINGS.md): The mod-off control also exceeds 50 ms in-window on worst frame (151.3/54.4/100.8 ms) in 3 of 3 runs; the list stalls over 50 ms about 0.13 times a second, so ~60% of 7 s windows hold one by chance and a worst-frame bar is unfit.
- trap:the-p99-bar-tolerates-one-200-ms-stall (selftest_explosiveknockback_barrage_p99.py): The p99 bar tolerates one 200 ms stall; planted 1.5 s at 75 ms and 2 s at 55 ms stalls fail.
- trap:the-steward-s-line-numbers-755-1285-in (RM_KnockbackProof.cs:755, :1285): The steward's line numbers (755, 1285) in RM_KnockbackProof.cs were stale and point at no leak.
- trap:the-acceptance-names-a-settings-field-landingstun-but (RM_KnockbackMod.cs; design/concepts/ExplosiveKnockback/version/test_table.json T_SETTINGS_SWEEP_OFFLINE): The acceptance names a settings field 'landingStun', but RM_KnockbackMod.cs has landingStunMin and landingStunMax.
- trap:the-detached-run-s-clone-holds-work-no (/home/mandrake/rm/relentless/store/orphans/bundles/20261115T165440Z-RIMMANDRAKE_STAGE_HEAVY_LOCKER_LANE_LWM_CAPS_AT_58KG.det): The detached run's clone holds work no remote had and is bundled in orphans, to be restored if wanted.
- trap:the-hopper-dies-to-any-he-blast-bomb (Station 5 / storage proof): The Hopper dies to any HE blast (Bomb x2 vs passable buildings = 100 damage = Hopper HP), so it cannot serve as the surviving container.
- trap:the-planted-faults-pf-dw-isfire-flame-only (live fireHalf lane; offline suites): The planted faults PF_DW_ISFIRE_FLAME_ONLY and PF_DW_FIRE_SWITCHES_PROJECTILE_TUNING were missed by every offline suite; the live fireHalf lane reads only DamageDefOf.Flame's force, so it cannot see inherited defs.
- trap:fx-jolt-bounded-tests-only-the-bound-so (T_KERNEL fx_jolt_bounded; RM_KnockbackMath.JoltOffset): fx_jolt_bounded tests only the bound, so green T_KERNEL and lane 1 do not show the jolt decays. No bar requires decay.
- trap:the-control-s-raised-field-write-on-rm (RM_KnockbackProof.cs sc_pit_fetch control; RM_LadderPortable): The control's `raised` field write on RM_LadderPortable did nothing: FlowWorks never counts a portable ladder as raised, so the control looked raised but was open. The live rerun has not been run.
- trap:expect-the-live-cover-row-to-fail-as (RM_KnockbackProof_StoreroomBombPit.cs; knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control --ticks 900): Expect the live cover row to FAIL as MOD: no code breaks a pit cover under a landing stack (filed as RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY). FlowWorks journals pawn descents only, so goods descents come from the scene's own per-tick thing trace.
- trap:it-is-held-for-rimmandrake-recertify-knockback-tree (tree.json, sheet.md): It is held for RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING.
- trap:carrier-tick-cost-pass-in-all-9-recorded (walk_storeroom_raid row CARRIER_TICK_COST; jawa/time_perf): CARRIER_TICK_COST PASS in all 9 recorded walk runs was green for the wrong reason: it compared 0.0 to 0.0 ms because jawa/time_perf returns 0 on a paused clock; real reading at speed 1 was 4.29 ms.
- trap:t-restore-scans-whole-repo (src/RimMandrake/Utils/selftest_proof_restore_check.py (T_RESTORE)): T_RESTORE scans the whole repo: another mod's commit can turn EK's inv_proof_scenes decider red (Pyrelands wind_burn_live.py:56, 49e11870b4, a checker false positive fixed under RIMMANDRAKE_TEACH_RESTORE_CHECK_CLOSURES_PYRELANDS_TRIPPED_EK). Read the failing row's path before blaming the mod.

## Causes refuted (11) — do not chase these again
- cause:portable-ladder-placement-is-not-the-cause-rm: Portable ladder placement is not the cause: RM_Building_Ladder.SpawnSetup re-hangs it toward the rim O(1,0) and LadderReaches(4,0,6) is true. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:stale-pathing-masks-are-not-the-cause-spawn: Stale pathing masks are not the cause: spawn/despawn bump the climb generation and clear reachability, and per-tick ladder-join caches reset every tick. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:forbidden-pit-goods-or-closed-ladders-are-not: Forbidden pit goods or closed ladders are not the cause: ClosedLaddersFor returns null for player colonists and neither mod forbids pit goods. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:the-flowworks-reach-veto-relativeveto-or-the-job: The FlowWorks reach veto (RelativeVeto) or the job never being offered was suspected but not the cause; the live job log showed the duplicate-pickup retarget instead. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:the-visit-2-barrage-failure-was-not-caused: The visit-2 barrage failure was not caused by the mod's barrage: the three 'barrage worst' frames (153.9/65.3/155.2 ms) all fall outside the 0.9-8.25 s window; mod-on in-window worst was 28.9/25.8/75.3 ms. (on 2a202dda96, depends on design/concepts/ExplosiveKnockback/version/criterion_repairs/sc_barrage_perf_2026-11-15/FINDINGS.md)
- cause:the-ticket-s-named-lines-rm-knockbackproof-cs: The ticket's named lines RM_KnockbackProof.cs:755 and :1285 are not leaks: Stage/Verdict already restore on throw (checker fix af61b9c206); the 7 new hits were none in RM_KnockbackProof.cs. (on af61b9c206f0, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs)
- cause:the-9-4-kg-reading-was-not-the: The 9.4 kg reading was not the locker's real capacity: it was the empty storage filter refusing guns (8 kg locker plus one revolver); LWM's 58 kg cap applies only once the filter is fixed. (on 7c910364ce62, depends on src/RimMandrake/ExplosiveKnockback)
- cause:container-movement-in-the-25-shell-storeroom-was: Container movement in the 25-shell storeroom was not mod knockback: with KB off the SC journal was empty, so it was vanilla building destruction. (on 357453e609ee, depends on src/RimMandrake/ExplosiveKnockback)
- cause:suspected-escape-bug-in-the-mod-a-colonist: Suspected escape bug in the mod (a colonist lowering the control ladder, a pawn climbing a raised ladder, or a hauler reaching the floor another way): the fault was in the test setup, a portable ladder cannot be raised; ExplosiveKnockback behaved correctly. (on 7c17ebc62201, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs)
- cause:colonist-weight-band-60-76-kg-suggested-by: Colonist weight band 60-76 kg suggested by the judge was wrong: 60-63 kg throws 6 cells at the higher damage and ties the capped rat, so the band was set to 64-76 kg. (on 1a5234227788cf3e9479d4ccbcf98ac2ca712b3d, depends on src/RimMandrake/ExplosiveKnockback)
- cause:the-melee-shove-into-pit-contest-masses-and: The melee shove-into-pit contest (masses and melee skills) does not belong in Explosive Knockback; it goes to FlowWorks as its own item. (on 1a5234227788cf3e9479d4ccbcf98ac2ca712b3d, depends on src/RimMandrake/ExplosiveKnockback)

## His answers (21)
- decision:version: Yes, fix it like that, and then please record this as an actual Pass.
- decision:q:you-can-t-fall-in-by: You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall.
- decision:q:1-1-totally-even-better-if: 1:1 totally. Even better if they can bounce inelastically off walls and rotate while they fly.
- decision:q:1-but-the-closed-containers-may: (1) but the closed containers may themselves get shoved a bit · 2 and remember the gas in the Cauldron
- decision:q:just-put-a-bomb-into-a: Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well.
- decision:q:1-anything-that-draws-its-contents: 1: Anything that draws its contents is open. … 4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly. No blockers.
- decision:q:we-really-shouldn-t-blow-back: We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it should fly. That should also be a function of the explosive damage itself as well. · with a single scene we can check ALL these things together · Melee shove is a great idea, but it belongs in FlowWorks, not here.
- decision:q:can-t-we-actually-simulate-that: can't we actually simulate that settings check offline? That seems a gratuitous use of the game, unless that's actually a very fast check?
- decision:finding:RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH: EK 5 gaps → fix the 5 gaps then one more judge; gas shove onto an open pit drops the pawn in → yes, it stands
- decision:finding:RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER: I agree with the 2nd option though, pending tuning, and worse damage if they then hit a solid object.
- decision:finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE: Hauling an item from within pit to storage zone out of pit worked!
- decision:finding:RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: Tuning looks good.
- decision:finding:RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS: Test 1: looks great! Full pass.
- decision:finding:RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE: Shelf did survive, but I was expecting the container to be moved while surviving. I had envisioned that if they put things in a steel crate or chest, the whole crate/chest would go flying a bit, but their contents would remain inside and protected due to its enclosed nature.
- decision:finding:RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE: No caps please.
- decision:finding:RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB: Better Explosions and Dynamic Effects Forge -> Keep both for good; Custom Gas Types -> Keep it as a separate mod
- decision:finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER: It's fine. This doesn't need a human review. Just accept it as a pass and go on.
- decision:finding:RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC: For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories.
- decision:finding:RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN: Thrown pawn lands on another pawn → Bruise in the next version
- decision:finding:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN: Closed container near a blast: slide one cell as the locked bar says, or thrown as built? → Throw it, as built; the locked bar's wording changes by his word from 'slides one cell' to 'thrown a short way', and the test follows
- q:walk-frame-clause-list-floor-already-eighty (Q: Walk frame clause: on the walk colony the mod-off arm alone is p99 80.2 ms (mod on 83.1, visit 3 run 4), over the 50 ms barrage bar the harness uses, so FRAME_BUDGET is UNMEASURED and the walk never exits 0. Judge it against its own mod-off arm with a margin, or lighten the walk colony?): Compare to mod-off (Recommended): Why: the question is what the mod costs, not what 316 mods cost. Pass if mod-on is within 10% of the same colony's mod-off run (today: +3.6%). Buys an honest, passable row today with no rebuild. Costs: the bar becomes relative, so a slow colony no longer fails by itself. Recommended: it measures the thing the bar was written to protect.

## Open questions (0)

## Bars (59)
- bar:barrage_frame_budget [locked] verdict none: constraint bar from tree.json, proves at stage 6
- bar:blast_breaks_pit_cover [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:closed_container_holds [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:doors_and_deep_water_stop [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:every_good_moves [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:every_harmful_blast_throws [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:frame_time_probe [locked] verdict PASS: instrument bar from tree.json, proves at stage 6
- bar:gas_goes_clump_by_clump [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:goods_arc_spin_rebound [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:heavier_flies_less [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:heavy_stack_knocks [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:hose_drops_at_takeoff [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:inv_big_corpse_spared [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_blast_power_damage [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_caps [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_closed_guard [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_container_shove [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_creature_mass_limit [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_gas_chain [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_gas_tags [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_goods_fly [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_heavy_knock [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_hook [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_hose_drop [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_items_teleport [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_kernel [locked] verdict none: inventory bar from record.json, proves at stage 4-5
- bar:inv_killed_corpse [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_mass_limit_skip [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_pawn_flyer [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_perf_all_fly [locked] verdict FAIL: inventory bar from record.json, proves at stage 6
- bar:inv_pit_floor_goods_stay [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_pit_floor_haul [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_pits_receive [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_proof_scenes [locked] verdict none: inventory bar from record.json, proves at stage 4-5
- bar:inv_recovery [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_settings [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_shelf_skip [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_shield [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_too_weak_skip [locked] verdict none: inventory bar from record.json, proves at stage 6
- bar:inv_weapon_ext_fields [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_which_blasts [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:inv_who_is_spared [locked] verdict PASS: inventory bar from record.json, proves at stage 6
- bar:no_careless_fall [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:no_teleport [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:only_explosions_throw [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:open_shelf_scatters [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:our_gases_burn [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:pawn_flight_arc [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:pawn_hits_pawn_stops [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:people_thrown_three_cells [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:per_weapon_tuning [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:pit_goods_fetched [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:recovery_immunity [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:settings_scale_and_switch [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:shield_belt_holds [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:the_spared [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:thrown_into_pit_falls [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:walk_storeroom_raid [locked] verdict FAIL: walk bar from tree.json, proves at stage 8
- bar:wall_stops_dead [locked] verdict none: experience bar from tree.json, proves at stage 6

spend recorded: USD 98.24, 140077376 tokens

## Left out
- decisions: 3, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- closed findings: 38, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- tests: 98, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- open findings in brief: the oldest 13 on one line, their fix and accept by `modledger.py show --mod ExplosiveKnockback <subject>`
- the full history: 496 events (views/history.md; never read whole)

cursor: t=2026-11-17T06:20:39Z.1794896439494721644 (modledger.py since --mod ExplosiveKnockback t=2026-11-17T06:20:39Z.1794896439494721644 prints what changed after this packet)
