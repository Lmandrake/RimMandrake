<!-- modledger view, generated: never edit (python3 src/RimMandrake/rimflow/modledger.py views --mod ExplosiveKnockback) reducer=1 shards={"BACKFILL":300611,"DISPATCH":4023,"HOLDER.run-1794813483":1382,"HOLDER.run-1794824768":580} body_sha256=489f4dd3336ea18c2c715e327b110a5874ce32cd17d4e5e6fc55d01cf3bb55e2 -->
# ExplosiveKnockback — mod ledger packet
version 0.1.0 · stage in_game · 432 events in 4 shards · reducer 1
holder lease run-1794824768, token 4, last active 2026-11-16T11:18:02Z
holder session 4b1a2409-4e0e-4572-b1d6-89ca03762637, context 177606 of ceiling 400000

## Last checkpoint (HOLDER.run-1794813483, 2026-11-16T07:33:24Z)
- done: 3 road-back items LEFT OPEN (live tests only); pipeline fixes 0c763edd9f (grant lands before launch) and 0ed7ae5001 (door tests drop holder env)
- next: on the next game-up visit run the 3 live acceptance commands named in the item notes and fix what answers false
- ruled out: RM_PitPathing TryPlan/OutsiderBarredFromFloor and portable-ladder Reaches as the dry-pit cause (read)

## Open findings (56)
(claimed fixes, awaiting a judge, on one line each with the oldest 20 open findings, named without their 'finding:': `modledger.py show --mod ExplosiveKnockback finding:<NAME>`)
- RIMMANDRAKE_FLING_GOODS_WILD_FACTOR_NEVER_SHIPPED on 81392aea384e9105a92263aea39b2d08c844c1f4
- RIMMANDRAKE_UNCOUPLE_GAS_GOODS_CAP_FROM_WEAPON_SCALE on 81392aea384e9105a92263aea39b2d08c844c1f4
- RIMMANDRAKE_CORRECT_REBOUND_ALWAYS_RUNS_OUT_COMMENT on 81392aea384e9105a92263aea39b2d08c844c1f4
- RIMMANDRAKE_RETIRE_UNUSED_CONTAINER_SHOVE_KERNEL [open, polish · bars closed_container_holds]: RM_KnockbackMath.ContainerShove (slide-or-jolt, parameter lightMassLimit) is called by no game code; ThrowContainer thr…
- RIMMANDRAKE_STAGE_KERNEL_SELFTEST_COPY_INSIDE_LOCK [open, polish · bars inv_kernel]: selftest_explosiveknockback_kernel.py copies RM_KnockbackMath.cs into the machine-wide build/ExplosiveKnockbackSelfTest…
- RIMMANDRAKE_RECORD_FULL_LAST_LINE_IN_TEST_TABLE_RUNS [open, polish]: test_table.json runs_today.last is truncated at 200 characters (T_FW_COVER), and for T_RESTORE it holds a Python Syntax…
- RIMMANDRAKE_ASK_GOODS_WILD_FACTOR_BECOME_A_SLIDER [open, polish · bars settings_scale_and_switch, goods_arc_spin_rebound]: The goods wild factor ships as a constant 1.6. Adding a saved setting goodsThrowWild turns T_STAGE3_SCENES red (F1/F2 f…
- RIMMANDRAKE_REPAIR_WILD_RATIO_BAND_FOR_INTEGER_CELLS [open, problem · bars goods_arc_spin_rebound]: scenes.json sc_storeroom_mortar requires every wild-to-kernel ratio between 1.3 and 2.0, but integer cells make any cor…
- RIMMANDRAKE_READ_WILD_CELLS_FROM_ITEM_MOVE_NOT_REQUEST [open, polish · bars goods_arc_spin_rebound]: Scene text says each good's request line carries its kernel cells and wild cells, but the request line is written at En…
- RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS on 587529cee173
- RIMMANDRAKE_SKIP_GOODS_WHEN_FLIGHT_OFF_OLD_HOP_LINGERED on 587529cee173
- RIMMANDRAKE_BUILD_CLOSED_GUARD_FIRE_HALF_SWITCHES_SHEET_NAMED on 587529cee173
- RIMMANDRAKE_DRAW_CONTAINER_JOLT_DUST_PUFF_WAS_ALL on 587529cee173
- RIMMANDRAKE_DELETE_DEAD_CONTAINER_SHOVE_KERNEL_TESTED_75_KG on 587529cee173
- RIMMANDRAKE_PIN_KNOCKBACK_NONPUSH_FORCES_IN_LINT_TABLE on 587529cee173
- RIMMANDRAKE_CORRECT_FLYING_OFF_WALK_ROW_TO_ITS_BAR on 587529cee173
- RIMMANDRAKE_DECIDE_RIM_THROW_BY_KERNEL_NOT_WILD_FACTOR on 587529cee173
- RIMMANDRAKE_COVER_WILD_GAS_CAP_IN_KERNEL_DECIDER on 04bb4c93faca
- RIMMANDRAKE_WIRE_CHECKS_SIX_PLANTED_FAULTS_PASSED_OFFLINE on 04bb4c93faca
- RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST [open, polish · bars inv_proof_scenes]: proof_restore_check.py does not see a proof's static_call Settings with a variable args= (storeroom_pit_proof.py arm():…
- RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER [open, polish]: FlowWorks pump_outflow_live.py:174 and tank_theft_live.py:80 write settings through setting(typ, field, *value); the ch…
- RIMMANDRAKE_SWITCH_ELECTRICAL_BURN_WITH_FIRE_HALF_FLAME_HEIR on bace1c29cc
- RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN on f181d3b6ea
- RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST on f181d3b6ea
- RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN [open, polish · bars inv_proof_scenes]: Five weakened live verdict expressions in the proof scenes (flying_off skip, goods wall position, deep water, container…
- RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME [open, polish · bars pawn_flight_arc]: RM_Patch_PawnFlyer_KnockbackLanding.Hauling is a static Dictionary<Pawn,Job>, set at every launch, removed only at a kn…
- RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED [open, polish · bars closed_container_holds]: RM_KnockbackMath.JoltOffset's doc promises a decaying shake, but only the bound is tested; a planted no-decay passed T_…
- RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT [open, polish · bars pawn_hits_pawn_stops, inv_kernel]: RM_KnockbackMath.Resolve: a pawn thrown over a sandbag straight into a pawn, wall or door backs off the sandbag (often…
- RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS [open, problem]: Task: Explosive Knockback must draw its own bigger blasts (debris, smoke, soot, sparks, big-blast shockwave and quake)…
- RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY [open, problem · bars thrown_into_pit_falls]: sc_storeroom_bomb_pit expects the stack aimed at a covered pit cell to fall through with one descent and destroy the co…
- RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN [open, problem]: In 0.1.0 a thrown pawn landing on a pawn that walked onto its landing cell mid-flight only writes land_on_pawn in the j…
- RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN [open, problem · bars closed_container_holds]: Task: build offline checks for the 11 Stage 3 bars that maturation.py next refuses as not runnable. Separately, the loc…
- RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS [open, problem · bars gas_goes_clump_by_clump, our_gases_burn]: Flammable gas should go off clump by clump. Each clump scatters goods (at most 2 cells) and shoves people 1 cell with n…
- RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN [open, problem]: Game copy still has Patches/RM_Knockback_ClosedContainers.xml, which the repo deleted after the owner's open-storage ru…
- RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC [open, problem · bars pawn_flight_arc, hose_drops_at_takeoff]: For 0.2.0: when a blast throws a pawn carrying something, the carried thing must leave its hands and fly its own trajec…
- RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD [open, problem · bars goods_arc_spin_rebound, no_teleport, inv_goods_fly, no_careless_fall]: Thrown goods were despawned and replaced (a teleport) at RM_MapComponent_Knockback.cs:474. They must instead fly an arc…
- finding:RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION [open, problem] by BACKFILL, 2026-11-16T08:26:04Z: The live half of the holder kill-and-resume check was never run: no pilot mod had a session.id at close. A killed resumed EK holder run must reconcile and resume on the next launch.
  proposed fix: When 'modledger.py resume-plan --mod ExplosiveKnockback' says action resume, let the dispatcher launch with --resume <sid>, systemctl --user kill that unit mid-stage, then run 'maturation_dispatch.py tick --apply'.
  accept: none, a live systemd run (offline twin: python3 src/RimMandrake/rimflow/selftest_holder_resume.py, ALL PASS).
- finding:RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars heavy_stack_knocks, inv_heavy_knock: A flying stack of 10 kg or more (dl_heavy_threshold) that hits a person must give a small blunt hit and a stagger; light goods pass through. A setting turns it off.
  proposed fix: In the carrier's Tick, when the ground cell changes and a pawn stands there with a stack >=10 kg, deal 2-5 Blunt and about 0.5 s stun, then land the stack there; add a setting and a proof row.
  accept: none filed as a command; proof row: heavy stack vs light stack past one colonist with a shared control (heavy_knock).
- finding:RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars open_shelf_scatters, closed_container_holds, inv_closed_guard, inv_shelf_skip: The every-storage exemption (RM_MapComponent_Knockback.cs:399) kept goods on shelves. Only closed containers should keep contents, and the container itself gets a small shove.
  proposed fix: Replace InStorage with HeldReason: open storage throws, closed (hidden-contents comp or showContents=false) holds; add ShoveContainer; flip walk row to light_things.item_on_an_open_shelf_scatters.
  accept: none, no command filed; proof rows: storeroom_pit_proof --storage (SA_OPEN_SHELF_THROWN, SA_NO_IN_STORAGE_SKIP, SA_CONTAINER_SURVIVES) and runner scene closed_container.
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars barrage_frame_budget, frame_time_probe, every_good_moves, walk_storeroom_raid, inv_perf_all_fly: Proof that all-fly (no overflow cap) holds at most 50 ms per frame on a mortar barrage and a long gas chain on Archmagi is incomplete. Measured on the 13-mod list only: passes at Normal speed, fails at Superfast (vanilla also fails). Gas chain, full list and sc_walk_raid are owed.
  proposed fix: Build the frame_time_probe instrument first, then run the barrage and a long gas chain on the full list on Archmagi, and stage the walk scene sc_walk_raid (reload, repeat, second order). Also stage showcase sc_storeroom_bomb_pit.
  accept: none, no command filed; bar is 'no frame over 50 ms' on the barrage and gas chain on Archmagi, after a sanity probe shows the instrument sees a slow frame.
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars closed_container_holds, inv_closed_guard, inv_shelf_skip, open_shelf_scatters: The live closed-container proof was staged with a ShelfSmall tagged closed by the removed CloseStorage, which contradicts the owner's ruling that anything drawing its contents is open. It must be re-proved with LWM's Deep Storage weapons locker and no tagged shelf or hopper.
  proposed fix: Build a proof DLL (winbuild.py ExplosiveKnockback -- -p:RmProofs=true), run storeroom_pit_proof.py --storage with LWM_WeaponsLocker, run the four scenes, and delete or restage the two misleading saves with inbound references.
  accept: storeroom_pit_proof.py --storage on the minimal list plus lwm.deepstorage, then scenes sc_closed_containers, sc_storeroom_bomb_pit, sc_settings_sweep, sc_open_storage; row NAME_CONTAINER_CLOSED reads CLOSED with no tag.
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars inv_which_blasts, per_weapon_tuning, inv_weapon_ext_fields: Scene sc_blast_kinds does not exist in RM_KnockbackProof.cs (not in SceneNames), so the Outer Rim sonic and plasma grenade lanes cannot be proved until the scene, verdict and mutation are built.
  proposed fix: Build the blast_kinds scene staging OuterRim_SonicGrenadeProj and OuterRim_PlasmaGrenadeProj (reading each damage type back from loaded defs), then prove it live with a proof build.
  accept: Live: Flame 50 (not 25) and untuned 50 at unpatchedHarmfulPercent 50; modded lane 100 at 100; control at 0 throws nothing.
- finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars pit_goods_fetched, inv_pit_floor_haul: The owner's rule that goods thrown into a pit stay retrievable is unproven by a scripted row. Only an owner live look showed a pawn hauling an item from the pit to a storage zone outside it.
  proposed fix: Stage scene sc_pit_fetch: a colonist fetches a good from the pit floor down the ladder, as a scripted proof row. If haulers cannot reach the floor by the lowered ladder, the fix belongs to FlowWorks.
  accept: none, no command filed; a colonist fetches one good from the pit floor down the ladder (scene sc_pit_fetch).
- finding:RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars closed_container_holds: sc_closed_containers jolt rows print drawnOffset=UNMEASURED although the jolt has been drawn since 587529cee1. The only counters, RM_MapComponent_Knockback JoltFrames/JoltMaxOffset, are map-wide statics updated per drawn frame, not per container or tick.
  proposed fix: Add a per-container read (container id -> max drawn offset while its jolt lasts), replace UNMEASURED with the measured value, and make the row pass only when above zero. Watch it fail on a planted break first.
  accept: sc_closed_containers jolt rows report a measured drawnOffset above zero on a live run, and at or below zero under the planted break (jolt drawn at zero).
- finding:RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS [open, problem] by BACKFILL, 2026-11-16T08:26:04Z · bars inv_proof_scenes: Existing proof scenes in RM_KnockbackProof.cs lack start assertions and real controls (17-row script_audit in record.json).
  proposed fix: Rewrite each scene to assert its start (INVALID otherwise) and run the control named in scenes.json, following the script_audit mapping. Rewrite or remove caps, tick_cap, shelf and items.
  accept: none, no acceptance test filed.
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER [open, problem] by BACKFILL, 2026-11-16T08:26:05Z · bars inv_creature_mass_limit, inv_blast_power_damage: Task: a creature mass limit (150 kg, Mod Setting) replaces the body-size 2.5 cutoff. Throw force becomes type force x this blast's damage / the type's defaultDamage (blastPowerFromDamage, on).
  proposed fix: Implement from conductor/ek_mass_20261113/DEFAULTS.md and plan.md item 5a: the mass limit setting, the damage-ratio force rule with its switch and reference percent, kernel tests, and proof scene sc_mass_and_power.
  accept: none filed as a command. The oracle is live scene sc_mass_and_power (rat/colonist/muffalo/thrumbo 5/3/2/0 at damage 50, 6/5/4/0 at 100) plus a builder-written kernel selftest.
- finding:RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST [open, problem] by BACKFILL, 2026-11-16T08:26:05Z · bars closed_container_holds: The container jolt draws a second copy of the graphic at the offset over the unmoved original (MapComponentUpdate b.Graphic.Draw), so a paused frame shows a doubled outline (t8 panel doubled ~0.1 cell). Whether it reads as a shake in motion is unjudged.
  proposed fix: Draw the jolt as a moved container rather than a ghost copy over the unmoved original.
  accept: none, a visual judgement in motion (owner or a judge on a short capture).
- finding:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST [open, problem] by BACKFILL, 2026-11-16T08:26:05Z · bars inv_gas_chain, inv_pit_floor_haul, barrage_frame_budget, closed_container_holds: Task: run Stage 6 in-game acceptance visit 1 (56 checks) for ExplosiveKnockback 0.1.0 and record it. Result: 47 pass, 4 fail, 5 unmeasured; exit not met.
  proposed fix: Fix the failing and unmeasured checks: write the three absent scenes (storeroom_bomb_pit, gas_into_pit, goods_obstacles), make the heavy-locker lane stageable, address the vent-gas chain and the pit-fetch control, then rerun the rows.
  accept: none filed beyond the 56 stage-6 checks; exit block must read exit_met true (it read 47 pass, 4 fail, 5 unmeasured, exit_met false).
- finding:RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED [open, problem] by BACKFILL, 2026-11-16T08:26:05Z · bars walk_storeroom_raid, barrage_frame_budget, frame_time_probe: walk_storeroom_raid's FRAME_BUDGET row is UNMEASURED by construction: RM_FrameProbe.Begin/Stop are internal and jawa/static_call reaches only public static, so the walk can never PASS.
  proposed fix: Add public static string Frame("begin|stop") on RM_KnockbackProof giving RM_FrameProbe a bridge read; proof-only code. Needs a C# rebuild (winbuild.py, proof and release) with its .srchash.
  accept: grep -c 'public static string Frame(' src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs prints >=1 (0 on 3d1f9ae2ca); selftest_explosiveknockback_walk_raid.py W0 expects every row PASS when fake Frame stop is under 50 ms
- finding:RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN [open, problem] by BACKFILL, 2026-11-16T08:26:05Z: In the ExplosiveKnockback walk save EK_VISIT2_WALK_20261115, dark blotches and haze lie over the four stations east of gas_chain (open_storage, heavy_knock, spared_states, goods_obstacles).
  proposed fix: Look at the save and take a vent-gas density read to confirm whether leftover Cauldron vent gas or its burn drifting from the gas_chain station (162,12) is the cause.
  accept: none, needs a look at the save and a vent-gas density read
- finding:RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST [open, problem] by BACKFILL, 2026-11-16T08:26:05Z · bars the_spared: On the owner's full mod list the staged sleeper is not in its bed at the blast, so spared_states is INVALID. It passes on the minimal list since a987289bca.
  proposed fix: Trace the sleeper with set_colonist_job_logging to find which full-list mod gets it up or stops LayDown, and keep it in bed.
  accept: none, live staging.
- finding:RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE [open, problem] by BACKFILL, 2026-11-16T08:26:06Z · bars inv_proof_scenes: Run the blind offline challenge (Stages 4 and 5, tests first) by hand on Explosive Knockback 0.1.0, one cycle, and write down its record format.
  proposed fix: Run lane 1 (rows), lane 2 (code review, planted faults, reruns), fix Problems red-first, then rule on the NOTED_FOR_CONDUCTOR faults and start cycle 2.
  accept: none, the exit condition is: inv_proof_scenes green and no Problems found.
- finding:RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF [open, problem] by BACKFILL, 2026-11-16T08:26:06Z: The Stage 4 Cold Reader exam is stale against the re-certified tree (barrage p99 rewording): the repin left stage 4 voided by its own rule (stale_from 4). No exam scenario mentions barrage or frame (grep 0).
  proposed fix: Refreeze the exam with fresh Claude readers (the exam11 route, 3d5eeb0e44) against the re-certified tree.
  accept: python3 src/RimMandrake/rimflow/designer_stage.py status design/concepts/ExplosiveKnockback | grep -c '"stale_from": null' prints 1 (watched failing: prints 0, stale_from 4).
- finding:RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING [open, problem] by BACKFILL, 2026-11-16T08:26:06Z · bars settings_scale_and_switch, inv_settings: sc_settings_sweep decides kernel-side settings live; they should be decided offline as a table test, with only game-side wiring left live.
  proposed fix: (1) Add a kernel selftest beside selftest_explosiveknockback_kernel.py running the sweep lane at default and per kernel-side setting, asserting each changes only its own outcomes, red on a coupling mutant
  accept: (1) selftest asserts each setting changes only its own row and a coupled-settings mutant (strength also scaling the cap) turns it red
- finding:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES [open, problem] by BACKFILL, 2026-11-16T10:13:56Z · bars walk_storeroom_raid, gas_goes_clump_by_clump, barrage_frame_budget, frame_time_probe: sc_walk_raid failed 6 rows at visit 2: A_RELOAD_NO_DUP_LOST (11 before save, 7 after reload), A/B_COVER_BROKEN_ONE_DESCENT (0 descents), A/B_GAS_CLUMP_BY_CLUMP (cells burst twice in 900 ticks), B_REQUESTS_MATCH_PLAN (Human38765 no outcome). FRAME_BUDGET is unmeasured by construction.
  proposed fix: Build the frame probe bridge read (RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED) so RM_FrameProbe can be read, then rerun the sc_walk_raid row command with --save EK_WALK_RAID_BASE_20261115T173148.
  accept: Live: the sc_walk_raid row command in design/concepts/ExplosiveKnockback/version/in_game/visit_2/rows.jsonl exits 0 (exit 1 on 61567a7b75); each MOD cause also gets an offline selftest red before its fix.
- finding:RIMMANDRAKE_ORDER_REMINE_LINES_KNOCKBACK_STAGE_READ_BACKWARDS [open, problem] by BACKFILL, 2026-11-16T10:19:31Z: modledger re-mine leaves lines out of plan order: Explosive Knockback's ledger stage read offline_build over its stage.enter in_game (lines written now stayed in front of kept lines re-appended after them), and Gimme Some Slack lint REFUSED finding on 2 kept causes left before their re-written finding.
  proposed fix: not written by its filer: read item:RIMMANDRAKE_ORDER_REMINE_LINES_KNOCKBACK_STAGE_READ_BACKWARDS
  accept: python3 src/RimMandrake/rimflow/selftest_modledger_backfill.py, its 3 're-mine order' checks red at 4455fcf7d7c5 (mining_samples/miner_round3_order_red_at_4455fcf7d7c5.txt), green after

## Traps (95) — what a reader would otherwise get wrong
- trap:judge-round-count-has-three-answers (design/concepts/ExplosiveKnockback/journal.md:58): Judge round count has three answers (12 / 13 / 19); not reconciled (spec §10).
- trap:97-2-million-tokens (version/VERSION.json): 97.2 million tokens were charged to the Designer stage, 86.5 million of them estimates (`version/VERSION.json`).
- trap:proof-build-versus-release-build (RM_KnockbackProof.cs): Proof build versus release build. Most live scenes exist only in the proof build (`RM_KnockbackProof.cs`, `proof_build_gate.py`); the test queue cannot deploy a proof build today (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
- trap:the-scene-ids-in-scenes-json-are-not (scenes.json): The scene ids in `scenes.json` are not the scene names in the proof code. `scenes.json` entry points name 35 scenes by proof method; `RM_KnockbackProof.Names` holds 41 older names, and only some of the 35 are among them (measured in Stage 2 below).
- trap:the-check-script-s-green-side-is-unproven (src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py): The check script's green side is unproven because no build exists to pass it. It only watched failing on c20328a876 (A1, A3, A4, A5). It does not judge the look; that is the art judge's call plus a live blast with Forge loaded.
- trap:widening-spandeck-s-load-to-count-items-would (FlowWorks Pits/Building_SpanDeck.cs ~256): Widening SpanDeck's load to count items would change FlowWorks for every item dropped on a deck, so fix it on the Knockback landing side.
- trap:this-is-for-design-version-0-2-0 (sc_pawn_arc; design/concepts/ExplosiveKnockback/version/next_version/README.md): This is for Design Version 0.2.0, not 0.1.0. In 0.1.0 as built, landing on a pawn deals no damage, and sc_pawn_arc asks only for the impact line.
- trap:the-in-game-test-checks-exactly-one-cell (closed-container scene and locked bar): The in-game test checks exactly one cell and fails the shipped code until the bar and test are reworded to 'thrown a short way'.
- trap:perf-of-a-long-gas-chain-40-cell (gas clump chain): Perf of a long gas chain (40-cell) is UNMEASURED.
- trap:mayrequire-on-a-top-level-operation-is-ignored (gas tagging patches): MayRequire on a top-level Operation is ignored. Tag other mods' gases through PatchOperationFindMod.
- trap:the-stevedesktop-live-proof-cannot-run-the-test (testq; RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE): The SteveDesktop live proof cannot run: the test queue deploys only the release DLL, and every Explosive Knockback scene exists only in the proof build.
- trap:patches-rm-knockback-hiddenstorage-xml-armoury-s-four (Patches/RM_Knockback_HiddenStorage.xml): Patches/RM_Knockback_HiddenStorage.xml (Armoury's four hidden smuggling panels closed) is checked offline only, not seen in game.
- trap:proof-code-is-fenced-behind-rm-proofs-csproj (csproj RmProofs=true; winbuild.py ExplosiveKnockback -- -p:RmProofs=true): Proof code is fenced behind RM_PROOFS (csproj RmProofs=true); the committed/deployed DLL must be release. Proof scripts exit 3 'PROOF BUILD REQUIRED' on a release DLL. The proof DLL was deployed and is uncommitted in ek4, so release must be rebuilt and redeployed.
- trap:this-build-lacks-the-1-6x-goods-distance (RM_MapComponent_Knockback.cs): This build lacks the 1.6x goods distance. The old per-tick overflow cap was still live at this ticket's last note; the caps were removed later under RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE (0808c553030c).
- trap:the-failures-sa-closed-goods-stay-sa-container (item:RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED): The failures SA_CLOSED_GOODS_STAY, SA_CONTAINER_RULE, SC_OFF_SHELF_GOODS_STILL and SC_OFF_CONTAINER_STILL were staging, not the rule: the 25-HE-shell blast destroys the steel Hopper in r6 and both wood shelves even with knockback off.
- trap:the-frame-histogram-instrument-had-read-bugs-filed (jawa/health tps.frame-hist): The frame-histogram instrument had read bugs (filed as RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG); a blind frame budget is a query bug until a sanity probe shows it sees a slow frame (a 1,095 ms SpinWait read 1094.963).
- trap:saves-ek-sitting-station5-container-survives-20261112-shelfsmall (saves EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112, EK_SITTING_STATION1_STORAGE_20261112): Saves EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112 (ShelfSmall tagged closed) and EK_SITTING_STATION1_STORAGE_20261112 (Hopper as the closed container) stage the old, invalid rule; the earlier 10/10 Station 5 pass does not prove the current rule.
- trap:the-ticket-s-premise-that-rm-knockbackproof-blast (item:RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES): The ticket's premise that RM_KnockbackProof blast_kinds already stages the lanes is false: grep finds no blast_kinds scene and SceneNames lacks it.
- trap:outerrim-sonicgrenadeproj-has-damagedef-outerrim-sonic-harmshealth-true (defs.sqlite 2026-11-12T08:10Z; design/RimMandrake/explosion_mods_characterized_2026-11-12.md): OuterRim_SonicGrenadeProj has damageDef OuterRim_Sonic (harmsHealth true, DamageWorker_AddInjury, no knockback extension), so it throws at unpatchedHarmfulPercent; OuterRim_PlasmaGrenadeProj has damageDef Flame (our 0.5). Both radius 4.9.
- trap:the-live-run-needs-a-proof-build-the (test queue): The live run needs a proof build the test queue cannot deploy (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
- trap:rm-pitpathing-cs-routes-non-held-pawns-around (RM_PitPathing.cs; save EK_SITTING_STATION1_STOREROOM_PIT_20261112): RM_PitPathing.cs routes non-held pawns around open pit cells, so haulers may not reach the pit floor; the owner's manual haul worked on a FlowWorks pit 4 deep with a ladder (13-mod list), but that is not the scripted proof.
- trap:joltframes-joltmaxoffset-are-map-wide-so-they-cannot (RM_MapComponent_Knockback.cs; RM_KnockbackProof_StageThree.cs): JoltFrames/JoltMaxOffset are map-wide, so they cannot show that a given container's jolt was drawn; the doubled-outline look is a separate item (RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST).
- trap:caps-tick-cap-shelf-and-items-assert-behaviour (RM_KnockbackProof.cs scenes caps, tick_cap, shelf, items): caps, tick_cap, shelf and items assert behaviour the owner's answers reversed (d_c_all_fly, d_c_wild, d_goods_fly); keeping them green is wrong.
- trap:the-airborne-spared-case-spared-states-must-force (RM_KnockbackProof.cs spared_states): The airborne-spared case (spared_states) must force the flying state with a test hook and read it; never launch a live flight.
- trap:forge-is-a-postfix-on-explosion-startexplosion-that (Dynamic Effects Forge, Explosion.StartExplosion Postfix): Forge is a Postfix on Explosion.StartExplosion that only sets doVisualEffects=false and draws its own effect; knockback receives the same blast. Read in code, not run live.
- trap:concept-tree-py-certify-refuses-an-owner-card (src/RimMandrake/rimflow/concept_tree.py:745): concept_tree.py certify refuses an owner card recorded on this item; it only accepts a card on the concept's own item (RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH, concept_tree.py:745), newer than the coverage judge verdict.
- trap:the-wording-card-is-not-a-certificate-an (design/concepts/ExplosiveKnockback tree.json coverage stamp): The wording card is not a certificate; an agent re-stamping the tree would forge the owner's pass.
- trap:exam-json-container-scenarios-expecting-a-one-cell (design/concepts/ExplosiveKnockback/exam.json): exam.json container scenarios expecting a one-cell slide or shove (e20, c4, c10, y5, w3, w4, w7, m13, m14, m15, m19, m20, v6, v7, v11) become wrong once the tree reads 'thrown a short way' and must be re-authored.
- trap:a-damagedefs-patch-matching-nothing-logs-nothing-verify (RM_Knockback_DamageDefs.xml patch): A DamageDefs patch matching nothing logs nothing; verify it landed against the live def dump (fire_half checks Flame force 0.5 vs Bomb 1.0).
- trap:the-100-hp-ancient-safe-dies-to-any (EK_LOOK_CONTAINER_MATRIX_20261112 ancient safe): The 100 HP ancient safe dies to any HE in reach (vanilla) and spills its contents; that is not a knockback failure.
- trap:a-pre-look-judge-saw-contents-drawn-spilled (conductor/ek_round2_20261112/prelook_open/VERDICT.md): A pre-look judge saw contents drawn spilled outside the closed stasis locker after the throw (container r5); the owner passed it and did not raise it, recorded only.
- trap:the-first-live-run-s-6-6-invalid (item:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER): The first live run's 6/6 INVALID was a harness fault, not a mod fault: the proof colonist band 64-76 kg was wrong, since measured Mass minus inventory was 48.75/60.75 and worn clothes add nothing. Band widened to 45-76 kg and the rerun passed.
- trap:the-proof-blast-helper-stages-damage-1-which (RM_KnockbackProof.cs ~588): The proof Blast helper stages damage 1, which under blastPowerFromDamage throws at 1/50 force. Scenes must stage the projectile's real damage and absorb the injury with a test hook.
- trap:the-scene-colonist-band-is-45-76-kg (sc_mass_and_power): The scene colonist band is 45-76 kg, superseding the earlier 64-76 note. Over 76.9 kg throws 2 cells at a mortar. A 63 kg colonist ties the capped rat, so 250_x2 reads statedTable=False.
- trap:staging-all-six-lanes-before-verdicts-leaks-lane (sc_mass_and_power live runs): Staging all six lanes before verdicts leaks lane settings (4 FAIL). A fallen VoidMonolith blocked lane 6 on the first map.
- trap:vanilla-rockets-deal-24-so-they-now-throw (blast power rule; proof scene and settings text): Vanilla rockets deal 24, so they now throw 1 cell instead of 3 (0.48 of force). The proof scene and settings text name the vanilla Thrumbo.
- trap:several-fix-rows-were-recorded-inverted-rc-0 (cycle_2 fixes.jsonl rows; maturation.py): Several fix rows were recorded inverted (rc 0 when the fix was missing) or held a <parent Source> placeholder or an uncommitted worktree, so their red/green proved nothing. Redone red on the parent, green at the fix; maturation.py now refuses placeholders. rc 0 means the fix holds.
- trap:the-container-bar-s-wording-in-tree-json (tree.json, sheet.md): The container bar's wording in tree.json and sheet.md was not changed: the owner certificate is hash-bound and rewording flips the gate PASS to REFUSED. It is held for RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING.
- trap:the-finding-was-read-from-code-not-run (RM_PawnFlyerPatches.cs Hauling): The finding was read from code, not run; no test shows the leak or the lost resume.
- trap:k-14-passed-while-testing-a-dead-function (K-14 kernel test; ContainerShove/KbShove): K-14 passed while testing a dead function at the 75 kg goods limit; the game's container limit is 250 kg.
- trap:locked-status-does-not-mean-the-coverage-judge (design/concepts/ExplosiveKnockback/stage.json; concept_tree.py gate): Locked status does not mean the coverage judge passed. The judge verdict stays not_covered; the lock rests on an owner-certified stamp, and the gate's only refusal reason is the missing judge signature.
- trap:the-certificate-hashes-tree-sheet-changed-on-2026 (owner-certified notes for design/concepts/ExplosiveKnockback): The certificate hashes (tree/sheet) changed on 2026-11-15 and 2026-11-16 after rewording; the earlier stamps' hashes are stale.
- trap:a-gas-shove-onto-an-open-pit-drops (dl_gas_shove_open_pit scene): A gas shove onto an open pit drops the pawn in (dl_gas_shove_open_pit), although the owner's card said to align with the sheet where a gas shove is not a throw. The owner confirmed it stands.
- trap:the-screenshots-show-a-doubled-outline-but-that (design/concepts/ExplosiveKnockback/version/in_game/visit_1/screenshots/jolt_*.jpg): The screenshots show a doubled outline, but that is a paused frame; it is not judged whether the jolt looks like a shake in motion.
- trap:the-original-judge-s-red-command-held-the (fix_demos/jj_red.txt): The original judge's red command held the placeholder <parent Source> and ran on an uncommitted worktree; the red was re-demonstrated with named paths in scratch clone ek_c2_fixdemo.
- trap:the-vent-gas-chain-sometimes-burning-only-one (item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST): The vent-gas chain sometimes burning only one clump (5 of 17 runs) was attributed to the Cauldron's fire spread, not ExplosiveKnockback.
- trap:the-spared-states-and-settings-sweep-failures-were (item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST): The spared_states and settings_sweep failures were diagnosed as harness faults, not mod faults.
- trap:sc-barrage-perf-passes-worst-frame-46-8 (sc_barrage_perf): sc_barrage_perf passes (worst frame 46.8 ms vs the 50 ms bar) on one run only, a thin margin.
- trap:the-heavy-locker-lane-cannot-be-staged-because (closed_containers heavy lane): The heavy-locker lane cannot be staged because no closed LWM container weighs 76-249 kg; heavy locker caps at 58 kg.
- trap:the-first-32-rows-were-25-pass-2 (visit_1 notes): The first 32 rows were 25 PASS, 2 FAIL, 5 UNMEASURED; the earlier 22/8 count was wrong.
- trap:the-container-jolt-draws-a-ghost-copy-over (MapComponentUpdate b.Graphic.Draw): The container jolt draws a ghost copy over the unmoved container rather than moving it.
- trap:frame-budget-reads-unmeasured-by-design-not-because (validation.py walk_storeroom_raid row FRAME_BUDGET (3d1f9ae2ca)): FRAME_BUDGET reads UNMEASURED by design, not because the budget is met or missed; the walk cannot reach all-PASS until the probe has a public static bridge read.
- trap:the-cause-leftover-cauldron-vent-gas-or-its (design/concepts/ExplosiveKnockback/version/in_game/visit_2/screenshots/walk_save_stations.jpg): The cause (leftover Cauldron vent gas or its burn drifting from gas_chain) is only presumed, unproven; do not treat it as established.
- trap:the-failing-run-signature-is-bursts-1-burstticks (RimSage Fire.DoComplexCalcs; RM_MapComponent_VentGas.Ignite): The failing-run signature is bursts=1 burstTicks=1: the spark's Fire sits on a fuel-less cell, vanilla destroys a Fire with flammabilityMax<0.01 at its first 150-tick check, which can precede the 30-tick BurnScan that only used live Fires as sparks.
- trap:old-check-k5-counted-1-to-6-cells (selftest_explosiveknockback_storeroom_bomb_pit.py K5 vs P0-P4): Old check K5 counted 1 to 6 cells freely, so it passed while the game failed; selftest P0-P4 uses the kernel's real throw length with constants read from source.
- trap:cycle-1-exit-is-not-met-inv-proof (design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_1/): Cycle 1 exit is NOT met: inv_proof_scenes is red (T_RESTORE known red) and Problems were found. One scene criterion, sc_storeroom_mortar's per-good 1.3-2.0 ratio, is impossible in whole cells. Planted faults caught 39 of 43 by builder offline tests.
- trap:the-judge-s-original-check-ran-with-the (cycle_2/lane2/plant_faults.py --expect-caught): The judge's original check ran with the failing direction as rc 0. It was rerun as a test whose rc 0 means the fix holds: red on ecd0b23322, green on 587529cee1.
- trap:the-green-run-s-clone-carried-uncommitted-k (cycle_3/lane2/fix_evidence/ek_c3_green_gate.jsonl): The green run's clone carried uncommitted K-23 kernel edits in other files (T_KERNEL was red in that baseline); the catching suite is T_PROOFGATE.
- trap:the-held-patch-failed-lint-as-written-because (ExplosiveKnockback tree.json barrage leaf; selftest_explosiveknockback_barrage_p99.py): The held patch failed lint as written because a constraint leaf must start with its limit; the leaf now reads 'at most 50 ms for the 99th-percentile frame ... on Archmagi', and the acceptance test checks the three facts in any order.
- trap:the-ticket-title-names-rm-knockbackproof-cs-755 (RM_KnockbackProof.cs; storeroom_pit_proof.py:258/94/148): The ticket title names RM_KnockbackProof.cs:755 and :1285, but those line numbers were stale and the leaks are not in that file.
- trap:the-restore-check-ok-annotation-on-storeroom-pit (storeroom_pit_proof.py resets; T_RESTORE scanner): The 'restore-check: ok' annotation on storeroom_pit_proof.py's resets is taken on trust by the scanner and proves nothing about restoration.
- trap:the-judge-s-original-red-command-held-the (fix_demos/jj_red.txt; ecd0b23322): The judge's original red command held the placeholder <parent Source> and ran on an uncommitted worktree; the red was re-demonstrated with named paths using Source at ecd0b23322 in scratch clone ek_c2_fixdemo.
- trap:acceptance-names-a-settings-field-landingstun-but-rm (RM_KnockbackMod.cs): Acceptance names a settings field 'landingStun', but RM_KnockbackMod.cs has landingStunMin and landingStunMax.
- trap:a-newly-built-lwm-weapons-locker-accepts-nothing (LWM_WeaponsLocker defaultStorageSettings): A newly built LWM weapons locker accepts nothing until its storage filter is set, so a fill loop silently places nothing.
- trap:a-hopper-dies-to-any-he-blast-bomb (Station 5 storage proof (st5_storage_proof2.json)): A Hopper dies to any HE blast (Bomb x2 vs passable buildings = 100 dmg = Hopper HP), so Hopper cannot show container survival at any shell count. The Station 5 storage proof ran on the proof build one review fix earlier than bb195048ac51.
- trap:the-live-firehalf-lane-reads-only-damagedefof-flame (live fireHalf lane; T_KERNEL K-23): The live fireHalf lane reads only DamageDefOf.Flame's force, and offline suites missed the fault; only K-23 covers ElectricalBurn.
- trap:fx-jolt-bounded-tests-only-the-bound-so (fx_jolt_bounded in T_KERNEL / lane 1): fx_jolt_bounded tests only the bound, so a green T_KERNEL/lane 1 does not show the jolt decays.
- trap:the-judge-s-original-row-ran-the-check (plant_faults.py --expect-caught; fix_demos/six_red.txt, six_green.txt): The judge's original row ran the check with the failing direction as rc 0, so it was not a valid test; the fix was re-demonstrated as a test whose rc 0 means the fix holds, red on parent 57e61fef0b, green at 04bb4c93fa.
- trap:three-bar-sets-exist (design/validation_walks/RimMandrake/ExplosiveKnockback.md): Three bar sets exist. The 59 coverage checklist rows are the bars of 0.1.0, and Stage 6 reports against them. The 16 "north-star bars" (his card 2026-11-12, "Approve as written") and the 49 "must be true" rows of `design/validation_walks/RimMandrake/ExplosiveKnockback.md` (measured 2026-11-14
- trap:the-locked-files-moved-after-the-lock (version/bars.md): The locked files moved after the lock. `version/bars.md` pins blobs at `237b791167`; since then `scenes.json` (sc_spared, sc_mass_and_power, sc_settings_sweep), `record.json` (decisions) and `tree.json` (the owner-certify stamp only) changed. The scene edits are test text (creatures chosen by mass, never named
- trap:the-owner-s-no-test-needed-covers-only (RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS spec): The owner's 'no test needed' covers only the look of the KEPT mods (Better Explosions, Dynamic Effects Forge).
- trap:his-awesome-pass-covered-the-container-shelf-grid (EK_LOOK_GAS_CLUMPS_MATRIX_20261112): His 'AWESOME' pass covered the container/shelf grid, not this save, so do not treat gas clumps as look-passed.
- trap:the-hose-end-rule-carrier-s-takeoff-cell (RM_MapComponent_Knockback.cs; scene sc_pawn_arc): The hose-end rule (carrier's takeoff cell drop) is a separate bar and stays.
- trap:scripted-proof-rows-flying-goods-5-5-goods (D:\ClaudeWork\rimmandrake\conductor\ek_sitting_20261112\runner_flying.txt): Scripted proof rows (flying_goods 5/5, goods_flight_saveload 4/4) passed but are not recorded as closing rows.
- trap:his-container-shelf-grid-pass-does-not-name (EK_LOOK_HEAVY_GOODS_MATRIX_20261112): His container/shelf grid pass does not name this save.
- trap:the-station-5-closed-rule-proven-pass-staged (EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112; storage proof 10/10): The Station 5 'closed rule proven' pass staged ShelfSmall tagged closed. Under the owner's ruling (anything that draws its contents is open, a shelf is open) it no longer proves the closed rule.
- trap:concept-edits-make-coverage-verdict-json-s-sheet (RM_Knockback_ClosedContainers.xml; coverage_verdict.json): Concept edits make coverage_verdict.json's sheet and tree hashes stale.
- trap:the-50-ms-pass-was-measured-on-the (evidence perf.jsonl, scene EK_PERF_BARRAGE_BASE_20261112): The 50 ms pass was measured on the 13-mod list, not the full list. It holds at Normal speed only; at Superfast KB OFF already reaches 40-67 ms, so the bar fails there with vanilla too.
- trap:the-test-queue-cannot-deploy-a-proof-build (src/RimMandrake/ExplosiveKnockback/proof/storeroom_pit_proof.py; worker.py/testq.py/deploy_custom_mods.py): The test queue cannot deploy a proof build (no RmProofs route), and EK scenes refuse the release DLL by design.
- trap:the-t-restore-red-was-not-from-the (T_RESTORE): The T_RESTORE red was not from the two leaks the brief named in RM_KnockbackProof.cs; those were already gone (since af61b9c206). The red came from 7 other hits.
- trap:the-settings-screen-test-16th-offline-decider-read (offline deciders; lane 1 rows): The settings-screen test (16th offline decider) read 855/856 and counted as known red until part C closed it at 856/856.
- trap:refile-if-any-run-reads-bursts-1 (gas_chain, gas_census, gas_clumps live scenes; d1817022db35): Refile if any run reads bursts=1.
- trap:frame-budget-is-unmeasured-by-construction-filed-rimmandrake (validation.py --live walk_storeroom_raid --storeroom x,z,w,h --cover x,z --gas x,z [--save NAME]): FRAME_BUDGET is unmeasured by construction (filed RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED). Closing does not mean the raid passed.
- trap:the-scene-and-the-16-bars-change-only (RM_KnockbackMod.cs Scribe_Values; scene sc_settings_sweep): The scene and the 16 bars change only via a Designer stage-3 edit.
- trap:do-not-read-it-as-proven-in-game (sc_closed_containers heavy lane, visit 2): Do not read it as proven in game; the 7c910364ce clone work was bundled as an orphan and not on a remote.
- trap:rm-ladderportable-never-reads-raised-so-writing-its (RM_KnockbackProof.cs control staging; RM_CompLadder.EffectivelyRaised): RM_LadderPortable never reads raised, so writing its raised field does nothing; a control built with it is an open pit.
- trap:flowworks-journals-pit-descents-for-pawns-only-so (RM_KnockbackProof_StoreroomBombPit.cs; FlowWorks journal): FlowWorks journals pit descents for pawns only, so goods falls and despawn-spawn pairs come from the scene's own trace. The cover row is expected to FAIL as MOD because no code breaks a pit cover under a landing stack.
- trap:run-1-of-the-acceptance-command-failed-corpse (knockback_runner.py --scenes pit_goods_fetch, run 1): Run 1 of the acceptance command FAILED (corpse out=False, first scene on a fresh map) with unread cause; PASS is 4 of 5, not 5 of 5.
- trap:the-visit-2-earlier-passes-were-not-descents (design/concepts/ExplosiveKnockback/version/in_game/visit_2/rows.jsonl sc_pit_fetch): The visit-2 'earlier passes' were not descents of the ladder (title says swims); with pits dry a pass must show the hauler in the pit.
- trap:reload-loss-was-not-a-mod-defect-the (item:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES): Reload loss was not a mod defect: the census compared a pre-save tick with one a tick after load (PauseOnLoad runs one DoSingleTick) while shell 1's wave was spreading; later, things born after the save take id, cell and count from the RNG.
- trap:cover-breaks-with-0-descents-were-not-the (item:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES): Cover breaks with 0 descents were not the mod: the first storeroom shell broke the cover and dropped its rider before the grenade (site design).
- trap:frame-budget-reads-unmeasured-by-construction-until-rm (sc_walk_raid row, FRAME_BUDGET): FRAME_BUDGET reads UNMEASURED by construction until RM_FrameProbe has a bridge read, so the walk cannot exit 0 even when all 17 judged rows pass.
- trap:a-corpse-never-descends-building-pitcover-despawn-takes (validation.py walk_storeroom_raid, ev.grenade): A corpse never descends (Building_PitCover.DeSpawn takes Pawn things only); a cover row with no living rider or a rider killed by the grenade is SITE UNMEASURED, not a mod pass.
- trap:a-blast-killed-pawn-is-requested-by-name (validation.py B_REQUESTS_MATCH_PLAN): A blast-killed pawn is requested by name but executed as its corpse (Corpse_<race><id>), so it looks like a missing outcome unless paired via ev.killed_by_blast.
- trap:under-the-old-layout-corpse-out-true-did (RM_KnockbackProof.cs pit_goods_fetch, Pit(O(2,-1),3,3)): Under the old layout 'corpse out=True' did not show the hauler descended; the corpse was reachable from the surface rim.

## Causes refuted (13) — do not chase these again
- cause:colonist-at-60-63-kg-was-not-a: Colonist at 60-63 kg was not a valid band for the rat-tie scene: it throws 6 cells at damage 100 and ties the capped rat, so the band is 64-76 kg. (on 1a5234227788cf3e9479d4ccbcf98ac2ca712b3d, depends on src/RimMandrake/ExplosiveKnockback)
- cause:the-5-unfixed-gaps-in-judge-run-1794599960: The 5 'unfixed' gaps in judge run 1794599960 were not unfixed in the design: the judge's own reasons said they look fixed; they were carried only because coverage_fixes.json held no claim. (on 1a5234227788cf3e9479d4ccbcf98ac2ca712b3d, depends on src/RimMandrake/ExplosiveKnockback)
- cause:rm-knockbackproof-cs-755-and-1285-do-not: RM_KnockbackProof.cs:755 and :1285 do not restore on throw: refuted. Stage/Verdict already restore on throw; none of the 7 new hits is in RM_KnockbackProof.cs (checker fix af61b9c206). (on af61b9c206f0, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs)
- cause:the-58-kg-lwm-cap-was-not-the: The 58 kg LWM cap was not the sole cause of the 9.4 kg reading: it was mostly the locker's empty storage filter refusing every gun (9.4 = locker 8 kg plus one revolver placed without the check). (on 7c910364ce62, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof_StageThree.cs)
- cause:the-container-s-movement-was-not-the-mod: The container's movement was not the mod: the SC journal was empty, so it was vanilla building destruction. (on bb195048ac51, depends on src/RimMandrake/ExplosiveKnockback)
- cause:no-escape-bug-in-the-mod-the-control: No escape bug in the mod: the control used RM_LadderPortable, and FlowWorks' RM_CompLadder.EffectivelyRaised = raised && !Props.portable && setting, so a portable ladder never reads raised and the control pit stayed open. The fault was in the test setup. (on 7c17ebc62201, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs)
- cause:portable-ladder-misplaced-rm-building-ladder-spawnsetup-re: Portable ladder misplaced: RM_Building_Ladder.SpawnSetup re-hangs it on the wall with the biggest drop, so the ladder at O(2,0) faces the rim O(1,0) and LadderReaches(4,0,6) is true. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:stale-reachability-masks-spawn-and-despawn-bump-the: Stale reachability masks: spawn and despawn bump the climb generation, push a cell delta and clear reachability. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:stale-stateversion-from-spawnsetup-per-tick-ladder-join: Stale StateVersion from SpawnSetup: per-tick ladder-join caches (LadderJoinsFor, LadderEdgesOwned) reset every tick, so staleness lasts one tick at most. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:ladder-closed-to-colonists-or-pit-goods-forbidden: Ladder closed to colonists or pit goods forbidden: ClosedLaddersFor returns null for player colonists and neither mod forbids pit goods. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:reach-veto-rm-superdeeptrap-relativeveto-or-work-giver: Reach veto (RM_SuperdeepTrap.RelativeVeto) or work giver never offering the job as the cause: the hauler's live job log showed the haul was offered and went wrong via vanilla duplicate pickup retargeting to the control pit's stack. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:corpse-out-true-was-read-as-proof-of: 'corpse out=True' was read as proof of descent; the corpse sat on the pit's edge row, so a rim hauler could touch it without descending. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:mod-caused-frame-spikes-the-visit-s-153: Mod-caused frame spikes: the visit's 153.9/65.3/155.2 ms barrage worst frames all fall outside the barrage window; mod-on in-window worst was 28.9/25.8/75.3 ms. (on 2a202dda96, depends on design/concepts/ExplosiveKnockback/version/criterion_repairs/sc_barrage_perf_2026-11-15/FINDINGS.md)

## His answers (20)
- decision:version: Yes, fix it like that, and then please record this as an actual Pass.
- decision:q:you-can-t-fall-in-by: You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall.
- decision:q:1-1-totally-even-better-if: 1:1 totally. Even better if they can bounce inelastically off walls and rotate while they fly.
- decision:q:1-but-the-closed-containers-may: (1) but the closed containers may themselves get shoved a bit · 2 and remember the gas in the Cauldron
- decision:q:just-put-a-bomb-into-a: Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well.
- decision:q:1-anything-that-draws-its-contents: 1: Anything that draws its contents is open. … 4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly. No blockers.
- decision:q:we-really-shouldn-t-blow-back: We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it should fly. That should also be a function of the explosive damage itself as well. · with a single scene we can check ALL these things together · Melee shove is a great idea, but it belongs in FlowWorks, not here.
- decision:q:can-t-we-actually-simulate-that: can't we actually simulate that settings check offline? That seems a gratuitous use of the game, unless that's actually a very fast check?
- decision:finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE: Hauling an item from within pit to storage zone out of pit worked!
- decision:finding:RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE: Shelf did survive, but I was expecting the container to be moved while surviving. I had envisioned that if they put things in a steel crate or chest, the whole crate/chest would go flying a bit, but their contents would remain inside and protected due to its enclosed nature.
- decision:finding:RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB: Better Explosions and Dynamic Effects Forge -> Keep both for good; Custom Gas Types -> Keep it as a separate mod
- decision:finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER: It's fine. This doesn't need a human review. Just accept it as a pass and go on.
- decision:finding:RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN: Thrown pawn lands on another pawn → Bruise in the next version
- decision:finding:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN: Closed container near a blast: slide one cell as the locked bar says, or thrown as built? → Throw it, as built; the locked bar's wording changes by his word from 'slides one cell' to 'thrown a short way', and the test follows
- decision:finding:RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC: For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories.
- decision:finding:RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH: EK 5 gaps → fix the 5 gaps then one more judge; gas shove onto an open pit drops the pawn in → yes, it stands
- decision:finding:RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER: I agree with the 2nd option though, pending tuning, and worse damage if they then hit a solid object.
- decision:finding:RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: Tuning looks good.
- decision:finding:RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS: Test 1: looks great! Full pass.
- decision:finding:RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE: No caps please.

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
- bar:inv_pit_floor_haul [locked] verdict FAIL: inventory bar from record.json, proves at stage 6
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
- closed findings: 22, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- tests: 64, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- claimed fixes in brief: 16 on one line (name and sha), their claim, test and fix by `show`
- open findings in brief: the oldest 20 on one line, their fix and accept by `modledger.py show --mod ExplosiveKnockback <subject>`
- the full history: 432 events (views/history.md; never read whole)

cursor: t=2026-11-16T11:18:02Z.1794827882468988549 (modledger.py since --mod ExplosiveKnockback t=2026-11-16T11:18:02Z.1794827882468988549 prints what changed after this packet)
