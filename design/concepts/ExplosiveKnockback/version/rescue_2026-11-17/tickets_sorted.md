# Explosive Knockback: the 51 open ledger items that name it, sorted (2026-11-17, the Fable Rescue)

Source: `open_tickets_census.txt`. One line each; the class says what 0.1.0 needs of it.

## CLOSED BY THIS RESCUE (2)

fixed and proved live, closed with ffc3937ee7.

- `RIMMANDRAKE_FILL_HEAVY_LOCKER_REAL_MASS_ESTIMATE_FELL_SHORT`: ExplosiveKnockback proof: sc_closed_containers' heavy locker is filled by estimated gun mass and can stop short of 76 kg (INVALID once in visit 3: 74.
- `RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE`: Explosive Knockback: prove goods thrown into a pit stay retrievable (a colonist fetches one from the pit floor down the ladder)

## 0.1.0, OPEN: NEEDS THE FULL LIST (5)

live-only on the 316-mod list; Stage 6 reruns it.

- `RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN`: ExplosiveKnockback walk save: dark blotches and haze lie over the four stations east of gas_chain (open_storage, heavy_knock, spared_states, goods_obs  **Rescue:** Visit 3 read it as explosion smoke gone 1500 ticks later (measured there); close on that.
- `RIMMANDRAKE_FIX_KNOCKBACK_RAID_NULL_PAWN_STORM_780_TICKS`: ExplosiveKnockback raid walk throws two NRE storms: 780x 'Exception ticking Levin' in vanilla Pawn.Tick+0x60 at (246,0,36) and 447x root Update NRE in  **Rescue:** Read its log: both storms start right after a game LOAD, on a pawn at the map edge (246,0,36); the ticket's "left with a null map by a knockback" is a guess. Not reproduced on the 34-mod list: a pawn saved in mid-flight and reloaded lands and logs 0 such lines (proof/pawn_flight_saveload.py, 5 of 5).
- `RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST`: ExplosiveKnockback spared_states: on the owner's full list the staged sleeper is not in its bed at the blast (INVALID), though it passes on the minima
- `RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF`: Explosive Knockback: prove all-fly (no overflow cap) holds at most 50 ms per frame on a mortar barrage and a long gas chain on Archmagi; owns the walk  **Rescue:** The wall bounce puts more stacks in the air in a walled room: sc_barrage_perf on the full list is UNRUN on this build.
- `RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES`: Explosive Knockback: stage and prove sc_blast_kinds' Outer Rim sonic and plasma grenade lanes

## 0.1.0, OPEN: RECORD-KEEPING (4)

the pipeline's own records of this mod; not the mod's behaviour.

- `RIMMANDRAKE_ADMIT_TEN_WORD_FAULT_ID_INTO_KNOCKBACK_LEDGER`: Explosive Knockback's 10-word blind fault id fails the finding namecheck, so the standard backfill leaves it out. Acceptance test: modledger_backfill.
- `RIMMANDRAKE_MIRROR_KNOCKBACK_STAGE_LEDGER_SAYS_OFFLINE_BUILD`: ExplosiveKnockback's mod ledger says stage offline_build while its stage record says in_game, so its backfill acceptance fails and pilot_ledger() is f
- `RIMMANDRAKE_RESTORE_EK_FUZZ_MUTANTS_TWO_TARGETS_VANISHED`: mutate_explosiveknockback_fuzz.py: mutants 'budget never resets' and 'budget allows cap + 1' print MUTATION TARGET NOT FOUND (their kernel lines are g
- `RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF`: ExplosiveKnockback: retake the Stage 4 Cold Reader exam against the re-certified tree (barrage p99 rewording); repin left stage 4 stale by its own rul

## POLISH (listed, not built) (8)

a judge or the filer sorted it Polish; the move to the Polish list is his to confirm.

- `RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME`: Polish, EK: RM_Patch_PawnFlyer_KnockbackLanding.Hauling is a static Dictionary<Pawn,Job>, never cleared on game load and not saved; a pawn dying mid-f  **Rescue:** Half done: the thrown-by memory is saved with the map now; the haul memory is still a static.
- `RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST`: ExplosiveKnockback container jolt draws a second copy of the graphic at the offset over the unmoved original (MapComponentUpdate b.Graphic.Draw), so a
- `RIMMANDRAKE_NOTE_KNOCKBACK_CALLER_MUTANTS_OWED_TO_STAGE_SIX`: ExplosiveKnockback Polish (the_spared): 10 planted faults in game-side callers survived offline, as expected for Verse code: PF_MC_GRID_IGNORES_PAWNS,  **Rescue:** Smaller now: the in-bed skip, the rebound and the landing cover break are plan rules the map plants and sees (30 of 30). Still game-side reads: the grid's pawn read, inventory mass, no-redirect, the landing door, the unpatched percent; the live agreement set (115 of 115) is the check that reads the first two.
- `RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF`: ExplosiveKnockback sc_closed_containers jolt rows print drawnOffset=UNMEASURED (RM_KnockbackProof_StageThree.cs) though the jolt is drawn since 587529
- `RIMMANDRAKE_SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS`: ExplosiveKnockback Polish (gas_goes_clump_by_clump): RM_MapComponent_Knockback.PawnSkipReason and Execute skip anything on a superdeep cell as in_pit
- `RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT`: Polish (ExplosiveKnockback 0.1.0, blind cycle 4): RM_KnockbackMath.Resolve: a pawn thrown over a sandbag cell straight into a pawn, wall or door backs
- `RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED`: Polish, EK: RM_KnockbackMath.JoltOffset's doc promises a decaying shake; a planted no-decay passed T_KERNEL and lane 1 (only the bound is tested). No
- `RIMMANDRAKE_TEST_WALK_FRAME_JUDGE_OFFLINE_TWO_MUTANTS_LIVED`: ExplosiveKnockback Polish (walk_storeroom_raid): PF_V_FRAME_OVER_LOOSE (10% -> 50%) and PF_V_FRAME_ROW_ALWAYS_PASS in validation.py survived every off

## BUILT, STILL OPEN ON PAPER (11)

the part ships in 0.1.0 and its scene passes live (visit 3, and again 2026-11-17 in rescue_2026-11-17/live/all_scenes_300_ticks.txt); the Conductor closes it on that evidence.

- `RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER`: Explosive Knockback: a creature mass limit (150 kg, Mod Setting) replaces the body-size 2.5 cutoff; throw force = type force x this blast's damage / t
- `RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN`: Explosive Knockback 0.1.0 Stage 3: build the checks for the 11 bars that are not runnable, offline
- `RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS`: Explosive Knockback: flammable gas goes off clump by clump, each clump scattering goods and shoving people 1 cell (no damage, once per 2 s, never brea
- `RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN`: Explosive Knockback: review the 5 DIRTY files, then deploy so the game copy loses the closed-tag patch on Cold Storage lockers
- `RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD`: Explosive Knockback: thrown goods truly fly (wild): arc, fast spin, rebound off walls until spent at ~70%; replaces the despawn-and-replace teleport a
- `RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS`: Explosive Knockback: a flying heavy stack that hits a person gives a small blunt hit and a stagger; light goods pass through
- `RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED`: Explosive Knockback: drop the every-storage exemption (RM_MapComponent_Knockback.cs:399); only closed containers keep contents, and the container itse
- `RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE`: Explosive Knockback: re-prove closed containers live with LWM's Deep Storage weapons locker, no shelf or hopper tagged closed; delete or restage the t
- `RIMMANDRAKE_READ_WALK_TICK_COST_RUNNING_PAUSED_READ_ZERO`: ExplosiveKnockback walk: CARRIER_TICK_COST scored PASS on 0.0/0.0 ms in all 9 runs on record; jawa/time_perf reads 0 on a paused clock
- `RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS`: Explosive Knockback: rewrite the proof scenes so each asserts its start and runs a real control (17-row script audit)
- `RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING`: ExplosiveKnockback sc_settings_sweep: decide the kernel-side settings offline as a table test (default vs each changed setting over the lane, diff = o

## PIPELINE RECORD OF A PAST STAGE (5)

a stage or cycle that has since run; nothing of the mod waits on it.

- `RIMMANDRAKE_CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED`: Explosive Knockback 0.1.0: blind challenge cycle 2
- `RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST`: ExplosiveKnockback 0.1.0 Stage 6: in-game acceptance visit 1 (56 stage-6 checks), live driver via maturation.py launch, record in design/concepts/Expl
- `RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_THREE`: ExplosiveKnockback Stages 4 and 5: blind challenge cycle 3, tests first, offline (launched by the Dispatch step)
- `RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE`: Explosive Knockback 0.1.0: run the blind offline challenge (Stages 4 and 5, tests first) by hand, one cycle, and write down its record format
- `RIMMANDRAKE_RESCUE_KNOCKBACK_AFTER_SLACK_FABLE_ENDS`: Launch a Fable Rescue on ExplosiveKnockback (roles/fable_rescue.md; proposal rp-explosiveknockback-1794898236, declined last night, re-decided by his

## LATER VERSION (3)

its own title says 0.2.0, or it adds a part the 0.1.0 vision does not hold (his call at filing).

- `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`: Explosive Knockback: absorb Extra Explosion Effects' idea, our own blast flecks, smoke, debris and big-blast shockwave
- `RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN`: Explosive Knockback 0.2.0: a thrown pawn landing on a pawn bruises both, scaled by its weight
- `RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC`: Explosive Knockback 0.2.0: a thrown pawn's carried thing flies its own trajectory

## NOT THIS MOD (13)

Explosive Growth, FlowWorks, a plot event or the pipeline itself: the census matched a word.

- `CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL`: Canal overflow (built 3cf4fdf12f, CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED) does not yet feed Explosive Growth or leave wet ground: (1) wire the shee
- `EXPLOSIVE_GROWTH_FIRST_SCRIPT_1`: First north-star script: ExplosiveGrowth
- `EXPLOSIVE_GROWTH_MERGE_COMES_HOME`: Fold ExplosiveGrowth into Baroque Biomes (mandrake.rm.biomes) as a composed member; native soak only for Baroque Biomes plants, Mod Settings option (d
- `EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS`: ExplosiveGrowth deep dive: what it is configured to do now, the original design, and where to take it (owner has serious concerns)
- `EXPLOSIVE_PLANT_GROWTH_1`: World mechanic: water-soaked plants grow VISIBLY on screen; design the terminal moment (what happens at the top), then custom mod actions so players e
- `FLOOD_WITNESS_EVENT_1`: Plot event: the player witnesses a Cracked Lands flood (chimes, wall of water, explosive growth) at least once — organized as part of the plot, since
- `RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT`: Maturation Pipeline: take FlowWorks 0.1.0 (locked) through the offline stages by hand beside the Explosive Knockback pilot, to stage 5 at most; no gam
- `RIMMANDRAKE_DESIGN_MATURATION_PIPELINE_WHOLE_MOD_IS_THE_UNIT`: Design the Maturation Pipeline: work unit is a whole versioned mod, intake then 8 stages (Designer, preflight, offline build, blind offline challenge
- `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD`: The game freezes for 50-100 ms at moments that do not depend on the mod under test (Explosive Knockback walk runs 4-7: most freezes land at the same m
- `RIMMANDRAKE_KEEP_CUT_BEASTS_OFF_TEST_TIERS`: Test tiers load the creatures the full list cuts (Thrumbo in the Knockback scene)
- `RIMMANDRAKE_REBUILD_REQUIRED_CHECKS_MANIFEST_SIX_MODS_STALE`: required_checks.json is stale on main: a rebuild rewrites the rows of six mods besides ExplosiveKnockback and KineticArms (DeepDrill, FlowWorks, Gimme
- `RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE`: Test queue: a proof-build job route (build -p:RmProofs=true and deploy it on SteveDesktop); Explosive Knockback's live scenes cannot run without it
- `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS`: The Dispatch tick left ExplosiveKnockback (blind cycle 5) and Pyrelands (blind cycle 3) waiting over six hours with the game free: find why, fix it, a

