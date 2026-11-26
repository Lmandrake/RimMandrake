<!-- modledger view, generated: never edit (python3 src/RimMandrake/rimflow/modledger.py views --mod ExplosiveKnockback) reducer=1 shards={"BACKFILL":348917,"DISPATCH":47046,"HOLDER.run-1794813483":1382,"HOLDER.run-1794824768":1788,"HOLDER.run-1794830532":2304,"HOLDER.run-1794860741":975,"HOLDER.run-1794865314":728,"HOLDER.run-1794895533":1780,"HOLDER.run-1795435910":630,"HOLDER.run-1795441975":2951,"HOLDER.run-1795448832":5159,"HOLDER.run-1795461416":958,"HOLDER.run-1795464425":3294,"HOLDER.run-1795478277":3184,"HOLDER.run-1795485747":1414,"HOLDER.run-1795487290":2197,"HOLDER.run-1795510833":4164,"HOLDER.run-1795525975":3126,"HOLDER.run-1795538786":1751,"HOLDER.run-1795548573":1024,"HOLDER.run-1795560492":1077,"HOLDER.run-1795660419":2599,"JUDGE.judge-1794890427":18837,"JUDGE.judge-1795437145":6544,"OWNER":1207} body_sha256=705a731749e04a47f9e4d286d357bf8c0efaaeaa807d90e5e5842b803e9e3067 -->
# ExplosiveKnockback — mod ledger packet
version 0.2.0 · stage offline_build · 748 events in 25 shards · reducer 1
holder lease run-1795660419, token 29, last active 2026-11-26T02:51:47Z
holder session 64d86561-8d37-4975-a838-3b61b865666a, context 228835 of ceiling 400000

## Last checkpoint (HOLDER.run-1795660419, 2026-11-26T02:51:47Z)
- done: T_RESTORE green: proof_restore_check finds setter wrappers by shape (9f285a25b6), joins ./publish checks; certificate --to blind_challenge exits 0 (796986d64f)
- next: Enter the blind challenge (Stages 4 and 5) for 0.2.0
- ruled out: No settings leak in the nine EK scenes: every put() call sits in a try whose finally writes the read prior back; the red was the checker missing a wrapper named put

## Open findings (43)
(claimed fixes, awaiting a judge, on one line each with the oldest 41 open findings, named without their 'finding:': `modledger.py show --mod ExplosiveKnockback finding:<NAME>`)
- RIMMANDRAKE_RETIRE_UNUSED_CONTAINER_SHOVE_KERNEL [open, polish · bars closed_container_holds]: RM_KnockbackMath.ContainerShove (slide-or-jolt, parameter lightMassLimit) is called by no game code; ThrowContainer thr…
- RIMMANDRAKE_STAGE_KERNEL_SELFTEST_COPY_INSIDE_LOCK [open, polish · bars inv_kernel]: selftest_explosiveknockback_kernel.py copies RM_KnockbackMath.cs into the machine-wide ExplosiveKnockbackSelfTest build…
- RIMMANDRAKE_ASK_GOODS_WILD_FACTOR_BECOME_A_SLIDER [open, polish · bars settings_scale_and_switch, goods_arc_spin_rebound]: The goods wild factor ships as a constant 1.6 because adding a saved setting (goodsThrowWild) turns T_STAGE3_SCENES red…
- RIMMANDRAKE_REPAIR_WILD_RATIO_BAND_FOR_INTEGER_CELLS [open, problem · bars goods_arc_spin_rebound]: scenes.json sc_storeroom_mortar requires every wild-to-kernel ratio between 1.3 and 2.0, but integer cells make any cor…
- RIMMANDRAKE_READ_WILD_CELLS_FROM_ITEM_MOVE_NOT_REQUEST [open, polish · bars goods_arc_spin_rebound]: scenes.json says each good's request line carries its kernel cells and wild cells, but the request line is written at E…
- RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST [open, polish · bars inv_proof_scenes]: proof_restore_check.py does not see a proof's static_call Settings with a variable args= (storeroom_pit_proof.py arm():…
- RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER [open, polish]: setting(typ, field, *value) writes settings through a vararg wrapper the restore checker misses, and liquidPumpEnabled…
- RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME [open, polish · bars pawn_flight_arc]: RM_PawnFlyerPatches.cs holds a static Dictionary<Pawn,Job> Hauling, set at every launch and removed only at a knockback…
- RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED [open, polish · bars closed_container_holds]: RM_KnockbackMath.JoltOffset's doc promises a decaying shake, but only the bound is tested; a planted no-decay (PF_MATH_…
- RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT [open, polish · bars pawn_hits_pawn_stops]: In RM_KnockbackMath.Resolve, a pawn thrown over a sandbag into a pawn, wall or door backs off the sandbag (often to 0 c…
- RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS [open, problem]: Task: Explosive Knockback draws its own bigger blasts (own RM_KnockbackBlast* FleckDefs for debris, smoke, soot, sparks…
- RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS [open, problem · bars gas_goes_clump_by_clump, our_gases_burn, inv_gas_chain, inv_gas_tags]: Flammable gas should go off clump by clump, each clump scattering goods and shoving people 1 cell (no damage, once per…
- RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN [open, problem]: The game copy still had Patches/RM_Knockback_ClosedContainers.xml, which tags Cold Storage lockers (RM_AncientStasisLoc…
- RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS [open, problem · bars heavy_stack_knocks]: RM_ThingFlyer_Knockback never checked pawns on its path, so a flying heavy stack (>= 10 kg, dl_heavy_threshold) did not…
- RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED [open, problem · bars open_shelf_scatters, closed_container_holds, inv_closed_guard, inv_container_shove, inv_shelf_skip]: The knockback flush exempted every storage building's contents (InStorage, RM_MapComponent_Knockback.cs:399), so goods…
- RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF [open, problem · bars barrage_frame_budget, frame_time_probe, every_good_moves, walk_storeroom_raid]: Task: prove all-fly (no overflow cap) holds at most 50 ms per frame on a mortar barrage and a long gas chain on Archmag…
- RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE [open, problem · bars closed_container_holds, open_shelf_scatters, inv_closed_guard]: Closed-container rule must be re-proved live with LWM_WeaponsLocker, no shelf or hopper tagged closed; the earlier pass…
- RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES [open, problem · bars inv_which_blasts]: Task: stage and prove sc_blast_kinds' Outer Rim lanes live: Flame 50 (not 25) and untuned 50 at unpatchedHarmfulPercent…
- RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF [open, problem · bars inv_container_shove]: sc_closed_containers jolt rows print drawnOffset=UNMEASURED in RM_KnockbackProof_StageThree.cs though the jolt has been…
- RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS [open, problem · bars inv_proof_scenes]: Existing scenes in RM_KnockbackProof.cs lack start assertions and real controls, per the 17-row script_audit in record.…
- RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST [open, problem · bars closed_container_holds]: The container jolt draws a second copy of the graphic at the offset over the unmoved original (MapComponentUpdate b.Gra…
- RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST [open, problem · bars inv_gas_chain, closed_container_holds, inv_pits_receive, inv_proof_scenes, barrage_frame_budget, inv_recovery]: Task: run Stage 6 in-game acceptance visit 1 (56 checks) for ExplosiveKnockback 0.1.0 through the live driver (maturati…
- RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST [open, problem · bars the_spared]: On the owner's full list the staged sleeper in spared_states is not in its bed at the blast (label INVALID), though it…
- RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE [open, problem · bars inv_proof_scenes]: Task: run the blind offline challenge (Stages 4 and 5, tests first) on Explosive Knockback 0.1.0 by hand for one cycle…
- RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF [open, problem]: designer_stage repin voided stage 4 (Cold Reader exam) after the barrage p99 rewording re-certified the tree; no exam s…
- RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING [open, problem]: sc_settings_sweep decides kernel-side settings only in a live run; there is no offline table test showing each setting…
- RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN [open, problem]: In 0.1.0 a thrown pawn landing on a pawn that walked onto its landing cell mid-flight only writes a land_on_pawn journa…
- RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN [open, problem · bars closed_container_holds, hose_drops_at_takeoff, frame_time_probe, barrage_frame_budget, inv_proof_scenes]: 11 of 59 bars had no runnable check, so maturation.py next refused every_bar_has_a_check_that_runs. Also, shipped code…
- RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC [open, problem · bars hose_drops_at_takeoff]: In 0.1.0 a thrown pawn flies holding its carried thing (MakeFlyer with flyWithCarriedThing: true); the carried stack ha…
- RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD [open, problem · bars goods_arc_spin_rebound, no_teleport]: Thrown goods were despawned and replaced (teleport at RM_MapComponent_Knockback.cs:474) instead of flying; they need an…
- RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER [open, problem · bars inv_creature_mass_limit, inv_blast_power_damage]: Creature throwing used a body-size 2.5 cutoff and a fixed force regardless of blast damage. Needed: a creature mass lim…
- RIMMANDRAKE_READ_WALK_TICK_COST_RUNNING_PAUSED_READ_ZERO [open, problem · bars walk_storeroom_raid]: Walk row CARRIER_TICK_COST scored PASS on 0.0/0.0 ms in all 9 runs on record because jawa/time_perf reads 0 on a paused…
- RIMMANDRAKE_COVER_FOUR_GAME_SIDE_FAULTS_NO_OFFLINE_TEST_SEES [open, polish · bars closed_container_holds, the_spared, every_harmful_blast_throws]: 4 of 43 planted faults pass the builder's offline tests: PF_CLOSED_GUARD_OFF, PF_CONTAINER_IGNORES_LIMIT, PF_GOODS_IN_P…
- RIMMANDRAKE_PIN_KNOCKBACK_PROOF_VERDICTS_NINE_MUTANTS_UNSEEN [open, problem · bars inv_proof_scenes]: 9 planted faults in the proof scenes' verdict and planning code survived every offline suite and lane 1; T_SCRIPT only…
- RIMMANDRAKE_SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS [open, polish · bars gas_goes_clump_by_clump]: RM_MapComponent_Knockback.PawnSkipReason and Execute skip anything on a superdeep cell as in_pit; IsSuperdeep is true u…
- RIMMANDRAKE_NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX [open, polish · bars the_spared]: 10 planted faults in game-side Verse callers (MC grid/sleeper/pawn mass, TF rebound/heavy knock/landing cover, PF redir…
- RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS [open, problem]: The shared scene runner's first slice (fd8e514b76) is proven offline only; it is unproven live that scene_runner.py giv…
- RIMMANDRAKE_REPOINT_EK_JOURNAL_JOLT_CHECKS_AFTER_PLAN_MOVE [open, problem]: selftest_explosiveknockback_journal_jolt.py greps RM_MapComponent_Knockback.cs for throw rules that ffc3937ee7 moved in…
- RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX [open, problem]: Explosive Knockback 0.1.0 was stuck at Stages 4+5 with blind cycle 6 unrun and paused at its stage spend ceiling. Live…
- RIMMANDRAKE_FIX_KNOCKBACK_RAID_NULL_PAWN_STORM_780_TICKS [open, problem]: The raid walk logs 780x 'Exception ticking Levin' (vanilla Pawn.Tick+0x60 at (246,0,36)) and 447x root Update NRE in Pa…
- RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN [open, problem · bars gas_goes_clump_by_clump]: RM_MapComponent_Knockback.GasBurst queues every pawn, corpse and good within gasBurstRadius by GenRadial alone, with no…
- RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES on fa2de6ee4b
- RIMMANDRAKE_SCOPE_KNOCKBACK_RESTORE_DECIDER_RED_ON_FLOWWORKS on 9f285a25b6942e960604b0f34b0b80ffa4b50a5d

## Traps (65) — what a reader would otherwise get wrong
- trap:judge-round-count-has-three-answers (design/concepts/ExplosiveKnockback/journal.md:58): Judge round count has three answers (12 / 13 / 19); not reconciled (spec §10).
- trap:97-2-million-tokens (version/VERSION.json): 97.2 million tokens were charged to the Designer stage, 86.5 million of them estimates (`version/VERSION.json`).
- trap:proof-build-versus-release-build (RM_KnockbackProof.cs): Proof build versus release build. Most live scenes exist only in the proof build (`RM_KnockbackProof.cs`, `proof_build_gate.py`); the test queue cannot deploy a proof build today (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
- trap:the-scene-ids-in-scenes-json-are-not (scenes.json): The scene ids in `scenes.json` are not the scene names in the proof code. `scenes.json` entry points name 35 scenes by proof method; `RM_KnockbackProof.Names` holds 41 older names, and only some of the 35 are among them (measured in Stage 2 below).
- trap:three-bar-sets-exist (design/validation_walks/RimMandrake/ExplosiveKnockback.md): Three bar sets exist. The 59 coverage checklist rows are the bars of 0.1.0, and Stage 6 reports against them. The 16 "north-star bars" (his card 2026-11-12, "Approve as written") and the 49 "must be true" rows of `design/validation_walks/RimMandrake/ExplosiveKnockback.md` (measured 2026-11-14
- trap:the-locked-files-moved-after-the-lock (version/bars.md): The locked files moved after the lock. `version/bars.md` pins blobs at `237b791167`; since then `scenes.json` (sc_spared, sc_mass_and_power, sc_settings_sweep), `record.json` (decisions) and `tree.json` (the owner-certify stamp only) changed. The scene edits are test text (creatures chosen by mass, never named
- trap:the-check-script-s-green-side-is-unproven (src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py): The check script's green side is unproven (no build exists to pass it). It does not judge the look: that is a judge agent's call plus a live blast, so a pass would not certify the art.
- trap:forge-sets-dovisualeffects-false-and-draws-its-own (design/RimMandrake/explosion_mods_characterized_2026-11-12.md; Dynamic Effects Forge): Forge sets doVisualEffects=false and draws its own, so our show must not double it.
- trap:0-1-0-as-built-and-kept-the (design/concepts/ExplosiveKnockback/version/next_version/README.md; sc_pawn_arc): 0.1.0 as built and kept: the pawn lands with no damage, and sc_pawn_arc asks only for the impact line. The bruise belongs to 0.2.0, not 0.1.0.
- trap:the-hidden-panel-tag-fix-is-checked-offline (RM_Knockback_HiddenStorage.xml; testq): The hidden-panel tag fix is checked offline only, and the SteveDesktop live proof never ran because the test queue deploys only the release DLL, not the proof build.
- trap:proof-scripts-exit-3-proof-build-required-on (csproj RmProofs=true; validation.py proof scripts): Proof scripts exit 3 'PROOF BUILD REQUIRED' on the release DLL; proof code is fenced behind RM_PROOFS, and the proof DLL deployed was uncommitted, so release must be rebuilt and redeployed.
- trap:flying-goods-are-not-the-frame-cost-flying (item:RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF): Flying goods are not the frame cost: flying ON and OFF showed no measurable difference at Normal; knockback adds about one bucket at Superfast, where vanilla alone already reaches 50-67 ms.
- trap:the-jolt-rows-drawnoffset-unmeasured-is-not-a (RM_KnockbackProof_StageThree.cs jolt rows.Add(...)): The jolt rows' drawnOffset=UNMEASURED is not a failure of the jolt: it is drawn since 587529cee1; only the instrument reads nothing per container.
- trap:code-reading-forge-is-a-postfix-on-explosion (Dynamic Effects Forge Postfix on Explosion.StartExplosion): Code reading: Forge is a Postfix on Explosion.StartExplosion that only sets doVisualEffects=false and draws its own effect, so knockback receives the same blast. This was read, not run live.
- trap:his-wording-card-is-not-a-certificate-an (design/concepts/ExplosiveKnockback coverage stamp (signed_by: owner)): His wording card is not a certificate; an agent re-stamping or treating the card as one would forge his pass.
- trap:a-damagedefs-patch-matching-nothing-logs-nothing-verify (RM_Knockback_DamageDefs.xml): A DamageDefs patch matching nothing logs nothing; verify the patch landed against the live def dump (fire_half read Flame force 0.5 vs Bomb 1.0).
- trap:a-pre-look-judge-saw-contents-drawn-spilled (conductor/ek_round2_20261112/prelook_open/VERDICT.md, container r5): A pre-look judge saw contents drawn spilled outside the closed stasis locker after the throw (container r5). The owner passed the scene and did not raise it; recorded only, no new work.
- trap:the-100-hp-ancient-safe-dies-to-any (container look matrix, ancient safe): The 100 HP ancient safe dies to any HE in reach (vanilla behaviour), so a destroyed container spilling its contents is expected, not a throw failure.
- trap:staging-all-six-scenes-before-verdicts-leaks-lane (sc_mass_and_power lanes): Staging all six scenes before verdicts leaks lane settings (4 FAIL); a fallen VoidMonolith blocked lane 6 on the first map.
- trap:the-brief-s-named-cause-of-the-red (T_RESTORE): The brief's named cause of the red T_RESTORE, the leaks in RM_KnockbackProof.cs, was not the cause: they were already gone since af61b9c206. The red came from 7 other hits: 3 resets in the storeroom proof, 2 files in other mods, and 2 in FlowWorks.
- trap:whether-the-doubled-outline-reads-as-a-shake (design/concepts/ExplosiveKnockback/version/in_game/visit_1/screenshots/jolt_*.jpg): Whether the doubled outline reads as a shake in motion is unjudged; a paused frame shows a doubled outline.
- trap:the-vent-gas-chain-burning-one-clump-and (item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST): The vent-gas chain burning one clump and stopping (5 of 17 runs) is attributed to the Cauldron's fire spread, not ExplosiveKnockback.
- trap:the-spared-states-and-settings-sweep-fails-were (item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST): The spared_states and settings_sweep FAILs were diagnosed as HARNESS faults, not mod faults.
- trap:the-container-jolt-is-visible-but-draws-a (MapComponentUpdate b.Graphic.Draw): The container jolt is visible but draws a ghost copy over the unmoved container rather than moving it.
- trap:cauldron-must-be-deployed-deploy-custom-mods-py (knockback_runner.py --scenes gas_chain,gas_census,gas_clumps): Cauldron must be deployed (deploy_custom_mods.py --mod Cauldron --apply, game down) first; refile if any run reads bursts=1.
- trap:earlier-passes-of-sc-pit-fetch-were-swims (RM_KnockbackProof.cs pit_goods_fetch): Earlier passes of sc_pit_fetch were swims; also the corpse sat on the pit's edge row so a rim hauler could touch it, so corpse out=True said nothing about descent.
- trap:the-old-selftest-check-k5-counted-1-to (selftest_explosiveknockback_storeroom_bomb_pit.py K5 vs P0-P4): The old selftest check K5 counted 1 to 6 cells freely, so it passed while the game failed; the new P0-P4 use the kernel's real throw length.
- trap:the-green-baseline-clone-carried-uncommitted-k-23 (cycle_3/lane2/fix_evidence/ek_c3_green_gate.jsonl): The green baseline clone carried uncommitted K-23 kernel edits in other files (T_KERNEL red there); the catching suite is T_PROOFGATE.
- trap:the-held-patch-failed-lint-as-written-because (tree.json barrage leaf; selftest_explosiveknockback_barrage_p99.py): The held patch failed lint as written, because a constraint leaf must start with its limit; the leaf now reads 'at most 50 ms for the 99th-percentile frame ... on Archmagi', and the acceptance test checks the three facts in any order.
- trap:the-mod-off-control-also-exceeds-50-ms (sc_barrage_perf; FINDINGS.md): The mod-off control also exceeds 50 ms in-window on worst frame (151.3/54.4/100.8 ms) in 3 of 3 runs; the list stalls over 50 ms about 0.13 times a second, so ~60% of 7 s windows hold one by chance and a worst-frame bar is unfit.
- trap:the-p99-bar-tolerates-one-200-ms-stall (selftest_explosiveknockback_barrage_p99.py): The p99 bar tolerates one 200 ms stall; planted 1.5 s at 75 ms and 2 s at 55 ms stalls fail.
- trap:the-acceptance-names-a-settings-field-landingstun-but (RM_KnockbackMod.cs; design/concepts/ExplosiveKnockback/version/test_table.json T_SETTINGS_SWEEP_OFFLINE): The acceptance names a settings field 'landingStun', but RM_KnockbackMod.cs has landingStunMin and landingStunMax.
- trap:the-detached-run-s-clone-holds-work-no (/home/mandrake/rm/relentless/store/orphans/bundles/20261115T165440Z-RIMMANDRAKE_STAGE_HEAVY_LOCKER_LANE_LWM_CAPS_AT_58KG.det): The detached run's clone holds work no remote had and is bundled in orphans, to be restored if wanted.
- trap:the-hopper-dies-to-any-he-blast-bomb (Station 5 / storage proof): The Hopper dies to any HE blast (Bomb x2 vs passable buildings = 100 damage = Hopper HP), so it cannot serve as the surviving container.
- trap:the-planted-faults-pf-dw-isfire-flame-only (live fireHalf lane; offline suites): The planted faults PF_DW_ISFIRE_FLAME_ONLY and PF_DW_FIRE_SWITCHES_PROJECTILE_TUNING were missed by every offline suite; the live fireHalf lane reads only DamageDefOf.Flame's force, so it cannot see inherited defs.
- trap:fx-jolt-bounded-tests-only-the-bound-so (T_KERNEL fx_jolt_bounded; RM_KnockbackMath.JoltOffset): fx_jolt_bounded tests only the bound, so green T_KERNEL and lane 1 do not show the jolt decays. No bar requires decay.
- trap:the-control-s-raised-field-write-on-rm (RM_KnockbackProof.cs sc_pit_fetch control; RM_LadderPortable): The control's `raised` field write on RM_LadderPortable did nothing: FlowWorks never counts a portable ladder as raised, so the control looked raised but was open. The live rerun has not been run.
- trap:the-detached-run-s-work-was-bundled-as (RM_KnockbackProof gas_into_pit; run knockback_runner.py --scenes gas_into_pit,gas_into_pit_off --ticks 300): The detached run's work was bundled as an orphan (not on a remote).
- trap:carrier-tick-cost-pass-in-all-9-recorded (walk_storeroom_raid row CARRIER_TICK_COST; jawa/time_perf): CARRIER_TICK_COST PASS in all 9 recorded walk runs was green for the wrong reason: it compared 0.0 to 0.0 ms because jawa/time_perf returns 0 on a paused clock; real reading at speed 1 was 4.29 ms.
- trap:t-restore-scans-whole-repo (src/RimMandrake/Utils/selftest_proof_restore_check.py (T_RESTORE)): T_RESTORE scans the whole repo: another mod's commit can turn EK's inv_proof_scenes decider red (Pyrelands wind_burn_live.py:56, 49e11870b4, a checker false positive fixed under RIMMANDRAKE_TEACH_RESTORE_CHECK_CLOSURES_PYRELANDS_TRIPPED_EK). Read the failing row's path before blaming the mod.
- trap:the-runner-s-outside-row-haulables-on-pit (src/RimMandrake/Utils/scene_runner.py; JawaBenchSceneRunnerTools.cs): The runner's Outside row (haulables on pit rows >= 1, a vanilla count) disagreeing with the main lane's verdict is a finding about one of them, not a reason to edit the count; the JawaBench companion with jawa/run_scenes needs a game restart to load.
- trap:the-flipping-live-checks-gas-chain-cauldron-gas (item:RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX): The flipping live checks (gas_chain, cauldron_gas, pit_fall, pit_enemy, barrage) were not faults in the mod; the record reads them as SITE or HARNESS faults.
- trap:three-text-checks-gas-clumps-settings-sweep-validation (gas_clumps, settings_sweep, validation.py static; steward_handoff/three_checks_follow_the_plan_v2.patch): Three text checks (gas_clumps, settings_sweep, validation.py static) read the old file's text for rules moved into the plan, so they went red on the change by location only. The steward's v2 patch repaired them; v1 had missed a planted new KbRules() at Execute/HeldReason/ItemWillBeThrown.
- trap:the-changed-source-files-read-dirty-to-code (code_review_status.py): The changed source files read DIRTY to code_review_status.py because no non-author has reviewed the full files.
- trap:the-launch-check-must-fail-grep-q-cover (src/RimMandrake/ExplosiveKnockback/Source/RM_ThingFlyer_Knockback.cs): The launch-check 'must-fail: grep -q Cover RM_ThingFlyer_Knockback.cs' is only a launch guard (the flyer had no cover code at filing), not the oracle.
- trap:old-selftest-k-08-cover-is-ground-and (cycle_5/tests_edited.json; Source/SelfTest/Program.cs): Old selftest K-08 'cover is ground' and K-24 'a pawn's landing doesn't break covers' pinned the opposite behaviour and were flipped; the reason is logged for the next blind judge.
- trap:no-finding-claimed-fixed-went-into-the-mod (EK mod ledger): No finding.claimed_fixed went into the mod ledger because the holder lease was fenced; the finding's subject is the old id RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND.
- trap:the-50-ms-barrage-bar-cannot-judge-the (validation.py FRAME_BUDGET; design/concepts/ExplosiveKnockback/version/in_game/visit_4/rows.jsonl): The 50 ms barrage bar cannot judge the walk: the 316-mod colony is 80.2 ms p99 with the mod off (83.1 on). The walk's frame row is judged against its own mod-off arm within 10%, and the frame comparison runs on the 34-mod EK tier list; the full-list walk reads that result via --frame-evidence.
- trap:a-rider-killed-by-the-grenade-is-a (validation.py walk_storeroom_raid cover rows): A rider killed by the grenade is a corpse, which never descends (Building_PitCover.DeSpawn takes Pawn things only), so a missing descent is SITE UNMEASURED, not a mod failure.
- trap:text-checks-that-read-the-moved-lines-had (selftest_explosiveknockback_journal_jolt, goods_obstacles G1, cycle_1 check_fix_wiring): Text checks that read the moved lines had to follow the move (journal_jolt, goods_obstacles G1, cycle_1 check_fix_wiring, stage3 hose needle); the verdict file must stay out of the release DLL, which proofgate checks.
- trap:registered-supports-journal-jolt-and-blind-cycle1-are (test_table.json T_JOURNAL_JOLT_OFFLINE, T_BLIND_CYCLE1_OFFLINE): Registered supports journal_jolt and blind_cycle1 are red on stale text checks (filed as RIMMANDRAKE_REPOINT_EK_JOURNAL_JOLT_CHECKS_AFTER_PLAN_MOVE), so their red shows on certificate runs despite the table being complete.
- trap:melee-shove-into-pit-contest-is-out-of (sc_pit_fall / dl_gas_shove_open_pit): Melee shove-into-pit contest is out of this mod (belongs to FlowWorks); a gas shove onto an open pit drops the pawn in.
- trap:the-title-lists-the-last-two-faults-truncated (lane2/faults.json, blind fault record evidence): The title lists the last two faults truncated (PF_DW_UNPATCHED_PER); the full ids are PF_DW_UNPATCHED_PERCENT_IGNORED and PF_DW_FIRE_SWITCH_IGNORED.
- trap:the-repin-left-stage-4-cold-reader-exam (designer_stage repin; RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF): The repin left stage 4 (Cold Reader exam) void by its own rule, so the exam is stale until retaken; selftest_concept_tree 'Designer row exists, off, no slots' was already red on base.
- trap:the-acceptance-case-has-not-been-watched-fail (map_agreement.py case c:wall:1:0;c:wall:0:1;t:a:steel2:1:1;b:gas:1.9): The acceptance case has not been watched fail; the claim that the game moves the stack today is read from the source, not measured live.
- trap:the-planted-fault-pf-mc-grid-ignores-pawns (RM_MapComponent_Knockback.cs RM_MapKbGrid.At): The planted fault PF_MC_GRID_IGNORES_PAWNS (the grid never reports a pawn) survived all 13 offline suites and lane 1, because the grid had no offline test; green offline suites did not cover this.
- trap:flowworks-journals-pawn-descents-only-so-goods-descents (RM_KnockbackProof_StoreroomBombPit.cs; knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control --ticks 900): FlowWorks journals pawn descents only, so goods descents come from the scene's own per-tick thing trace.
- trap:the-250-x2-lane-statedtable-false-only-because (sc_mass_and_power 250_x2): The 250_x2 lane statedTable=False only, because a 63 kg colonist ties the capped rat.
- trap:sc-pit-fetch-failed-once-the-main-lane (sc_pit_fetch control pit): sc_pit_fetch failed once: the main lane passed, but the stack in the control pit (ladder raised) also got out.
- trap:killed-blind-judge-leaves-preliminary-exit-block (blind_challenge/cycle_6/SUMMARY.md ## Exit): A killed blind judge leaves its preliminary Exit block (written with lane 1, before its fixes) reading red; cycle 6 read red that way. The steward reruns the deciders at HEAD and sets the block from those reruns, never from the report.
- trap:frame-arms-need-a-held-frame-rate (RM_FrameProbe; validation.py --frame-evidence): Vsync does not hold a covered window: frame arms ran at 517 to 2678 window frames; the probe now holds 60 fps. Deploy the proof DLL with its .srchash: the evidence matches on sources; a bare dll copy loses it.
- trap:load-tick-lands-after-playing (validation.py wait_settled; saveload_triplet): After a load the PauseOnLoad tick can land after the game reads Playing: a step then ends short (visit 4) or one over (visit 5). Wait for a still clock before the first step.
- trap:gas-bursts-never-break-pit-covers-ignore-shield (src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackCompat.cs:88): Gas bursts never break pit covers, ignore shield belts and shove a person at most once per 2 s. Only the Cauldron's vent gas joins the chain: its Ignite is patched in C#; no gas carries a tag.
- trap:short-frame-runs-on-the-same-build-swung (design/concepts/ExplosiveKnockback/version/in_game/visit_3/pilot_walk_raid_20261116/evidence/ek_frames_small_DECISIVE_21.json): Short frame runs on the same build swung from -1% to +19%; mod-off arms alone spread 38-51 ms, so 3 pairs flip pass/fail. Only the pre-registered 21-pair cold run is decisive (+3.1%).
- trap:restore-check-setter-wrapper-name (src/RimMandrake/Utils/proof_restore_check.py check_py setter discovery): proof_restore_check judged a settings wrapper at its call sites only when its name held set|poke|flip|toggle, so a put(s, field, value) wrapper read as one leak per scene (nine, 2026-11-25). Since 9f285a25b6 a module-level wrapper is found by shape; a waived or self-guarded one keeps its place.

## Causes refuted (13) — do not chase these again
- cause:portable-ladder-placement-is-not-the-cause-rm: Portable ladder placement is not the cause: RM_Building_Ladder.SpawnSetup re-hangs it toward the rim O(1,0) and LadderReaches(4,0,6) is true. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:stale-pathing-masks-are-not-the-cause-spawn: Stale pathing masks are not the cause: spawn/despawn bump the climb generation and clear reachability, and per-tick ladder-join caches reset every tick. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:forbidden-pit-goods-or-closed-ladders-are-not: Forbidden pit goods or closed ladders are not the cause: ClosedLaddersFor returns null for player colonists and neither mod forbids pit goods. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:the-flowworks-reach-veto-relativeveto-or-the-job: The FlowWorks reach veto (RelativeVeto) or the job never being offered was suspected but not the cause; the live job log showed the duplicate-pickup retarget instead. (on f03d8d4f4a, depends on src/RimMandrake/ExplosiveKnockback)
- cause:the-visit-2-barrage-failure-was-not-caused: The visit-2 barrage failure was not caused by the mod's barrage: the three 'barrage worst' frames (153.9/65.3/155.2 ms) all fall outside the 0.9-8.25 s window; mod-on in-window worst was 28.9/25.8/75.3 ms. (on 2a202dda96, depends on design/concepts/ExplosiveKnockback/version/criterion_repairs/sc_barrage_perf_2026-11-15/FINDINGS.md)
- cause:the-ticket-s-named-lines-rm-knockbackproof-cs: The ticket's named lines RM_KnockbackProof.cs:755 and :1285 are not leaks: Stage/Verdict already restore on throw (checker fix af61b9c206); the 7 new hits were none in RM_KnockbackProof.cs. (on af61b9c206f0, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs)
- cause:the-9-4-kg-reading-was-not-the: The 9.4 kg reading was not the locker's real capacity: it was the empty storage filter refusing guns (8 kg locker plus one revolver); LWM's 58 kg cap applies only once the filter is fixed. (on 7c910364ce62, depends on src/RimMandrake/ExplosiveKnockback)
- cause:container-movement-in-the-25-shell-storeroom-was: Container movement in the 25-shell storeroom was not mod knockback: with KB off the SC journal was empty, so it was vanilla building destruction. (on 357453e609ee, depends on src/RimMandrake/ExplosiveKnockback)
- cause:suspected-escape-bug-in-the-mod-a-colonist: Suspected escape bug in the mod (a colonist lowering the control ladder, a pawn climbing a raised ladder, or a hauler reaching the floor another way): the fault was in the test setup, a portable ladder cannot be raised; ExplosiveKnockback behaved correctly. (on 7c17ebc62201, depends on src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs)
- cause:reload-row-11-before-vs-7-after-was: Reload row 11 before vs 7 after was not the mod losing things: the census before the save and after the load were taken a tick apart while shell 1's wave was still spreading (harness defect). (on 773b9baea39f, depends on src/RimMandrake/ExplosiveKnockback)
- cause:cover-rows-were-not-a-mod-fault-the: Cover rows were not a mod fault: the first storeroom shell broke the cover and dropped its rider before the grenade (SITE staging fault). (on 773b9baea39f, depends on src/RimMandrake/ExplosiveKnockback)
- cause:mod-frame-cost-was-not-request-flush-1: Mod frame cost was not request flush (1-3 ms warm, 8-18 ms first throw only), journal (in memory), flyer drawing (0.1-3.6 ms), map mesh (0.1 ms), or job searches at the blast (same in both arms, equal totals). (on 773b9baea39f, depends on src/RimMandrake/ExplosiveKnockback)
- cause:run-5-fail-91-3-vs-37-1: Run 5 FAIL 91.3 vs 37.1 ms was a harness artifact, not mod cost: the off arm ran uncapped (863 vs 498 window rows), diluting p99 by frame rate. (on 773b9baea39f, depends on design/concepts/ExplosiveKnockback/version/in_game/visit_3/SUMMARY.md)

## His answers (22) (each cut to 160 chars, a decision named without its 'decision:': `modledger.py show`)
- version: Yes, fix it like that, and then please record this as an actual Pass.
- q:you-can-t-fall-in-by: You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall.
- q:1-1-totally-even-better-if: 1:1 totally. Even better if they can bounce inelastically off walls and rotate while they fly.
- q:1-but-the-closed-containers-may: (1) but the closed containers may themselves get shoved a bit · 2 and remember the gas in the Cauldron
- q:just-put-a-bomb-into-a: Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well.
- q:1-anything-that-draws-its-contents: 1: Anything that draws its contents is open. … 4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene i…
- q:we-really-shouldn-t-blow-back: We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it should fly. That should also be a function of the expl…
- q:can-t-we-actually-simulate-that: can't we actually simulate that settings check offline? That seems a gratuitous use of the game, unless that's actually a very fast check?
- finding:RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER: I agree with the 2nd option though, pending tuning, and worse damage if they then hit a solid object.
- finding:RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: Tuning looks good.
- finding:RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS: Test 1: looks great! Full pass.
- finding:RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE: Shelf did survive, but I was expecting the container to be moved while surviving. I had envisioned that if they put things in a steel crate or chest, the whole…
- finding:RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE: No caps please.
- finding:RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB: Better Explosions and Dynamic Effects Forge -> Keep both for good; Custom Gas Types -> Keep it as a separate mod
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER: It's fine. This doesn't need a human review. Just accept it as a pass and go on.
- finding:RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC: For today have them hold it. Next version it should go flying independently of the person holding it. Different trajectories.
- finding:RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN: Thrown pawn lands on another pawn → Bruise in the next version
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN: Closed container near a blast: slide one cell as the locked bar says, or thrown as built? → Throw it, as built; the locked bar's wording changes by his word fr…
- q:walk-frame-clause-list-floor-already-eighty (Q: Walk frame clause: on the walk colony the mod-off arm alone is p99 80.2 ms (mod on 83.1, visit 3 run 4), over the 50 ms barrage bar the harness uses, so FRAME_BUDGET is UNMEASURED and the walk never exits 0. Judge it against its own mod-off arm with a margin, or lighten the walk colony?): Compare to mod-off (Recommended): Why: the question is what the mod costs, not what 316 mods cost. Pass if mod-on is within 10% of the same colony's mod-off ru…
- finding:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES: The game pause has been a consistent issue well beyond this mod. While it's laudable to try and figure it out, it really is different than getting this mod to…
- finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE: Hauling an item from within pit to storage zone out of pit worked!
- finding:RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH: EK 5 gaps → fix the 5 gaps then one more judge; gas shove onto an open pit drops the pawn in → yes, it stands

## Open questions (0)

## Bars (73)
- bar:barrage_frame_budget [locked] verdict none: constraint bar from tree.json, proves at stage 6
- bar:blast_breaks_pit_cover [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:blast_show_air_ripple [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_crater_scar [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_fire_and_flash [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_scales_with_damage [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_screen_shake [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_smoke [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_soot_on_pawns [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_soot_on_things [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:blast_show_switches_off_clean [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:carried_thing_own_arc [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:closed_container_holds [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:collision_bruise_by_size [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:doors_and_deep_water_stop [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:every_good_moves [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:every_harmful_blast_throws [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:frame_time_probe [locked] verdict PASS: instrument bar from tree.json, proves at stage 6
- bar:gas_goes_clump_by_clump [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:gas_shoves_pawn_on_pit_cover [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
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
- bar:inv_perf_all_fly [locked] verdict PASS: inventory bar from record.json, proves at stage 6
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
- bar:no_impact_without_contact [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:no_teleport [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:only_explosions_throw [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:open_shelf_scatters [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:our_gases_burn [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:pawn_flight_arc [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:pawn_hits_pawn_stops [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:people_thrown_three_cells [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:per_weapon_tuning [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:pit_goods_fetched [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:rebound_goes_shorter [locked] verdict none: locked for 0.2.0 in version/locked_bars.json (record 2 of 2…
- bar:recovery_immunity [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:settings_scale_and_switch [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:shield_belt_holds [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:the_spared [locked] verdict none: experience bar from tree.json, proves at stage 6
- bar:thrown_into_pit_falls [locked] verdict PASS: experience bar from tree.json, proves at stage 6
- bar:walk_storeroom_raid [locked] verdict UNMEASURED: walk bar from tree.json, proves at stage 8
- bar:wall_stops_dead [locked] verdict none: experience bar from tree.json, proves at stage 6

spend recorded: USD 178.61, 171672717 tokens

## Left out
- decisions: 3, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- closed findings: 53, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- tests: 106, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- claimed fixes in brief: 2 on one line (name and sha), their claim, test and fix by `show`
- open findings in brief: the oldest 41 on one line, their fix and accept by `modledger.py show --mod ExplosiveKnockback <subject>`
- his answers and the bars' texts in brief (cut at 160 and 60 chars)
- the full history: 748 events (views/history.md; never read whole)

cursor: t=2026-11-26T02:51:47Z.1795661507558163713 (modledger.py since --mod ExplosiveKnockback t=2026-11-26T02:51:47Z.1795661507558163713 prints what changed after this packet)
