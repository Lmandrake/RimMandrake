<!-- modledger view, generated: never edit (python3 src/RimMandrake/rimflow/modledger.py views --mod ExplosiveKnockback) reducer=1 shards={"BACKFILL":226529,"DISPATCH":2028,"HOLDER.run-1794813483":1382} body_sha256=74d78300a89dee26f2687c8925986119d41b778d4f8e6f67f7720161b7c213f7 -->
# ExplosiveKnockback — mod ledger packet
version 0.1.0 · stage offline_build · 334 events in 3 shards · reducer 1
holder lease run-1794816017, token 2, last active 2026-11-16T08:00:20Z
holder session 4b1a2409-4e0e-4572-b1d6-89ca03762637, context 177606 of ceiling 400000

## Last checkpoint (HOLDER.run-1794813483, 2026-11-16T07:33:24Z)
- done: 3 road-back items LEFT OPEN (live tests only); pipeline fixes 0c763edd9f (grant lands before launch) and 0ed7ae5001 (door tests drop holder env)
- next: on the next game-up visit run the 3 live acceptance commands named in the item notes and fix what answers false
- ruled out: RM_PitPathing TryPlan/OutsiderBarredFromFloor and portable-ladder Reaches as the dry-pit cause (read)

## Open findings (76)
- finding:RIMMANDRAKE_RETIRE_UNUSED_CONTAINER_SHOVE_KERNEL [open, polish] by BACKFILL, 2026-11-16T06:51:52Z · bars closed_container_holds: RM_KnockbackMath.ContainerShove (slide-or-jolt, parameter named lightMassLimit) is called by no game code; ThrowContainer throws the container ThrowCells cells with its own loop [measured, grep]
  proposed fix: wait for question 12; then either call ContainerShove from ThrowContainer or delete it and kernel-test the throw
  accept: the kernel is the tested rule as shipped (RM_KnockbackMath.cs header)
- finding:RIMMANDRAKE_STAGE_KERNEL_SELFTEST_COPY_INSIDE_LOCK [open, polish] by BACKFILL, 2026-11-16T06:51:52Z: selftest_explosiveknockback_kernel.py copies RM_KnockbackMath.cs into the machine-wide D:\ClaudeWork\rimmandrake\build\ExplosiveKnockbackSelfTest BEFORE taking its flock; […]
  proposed fix: move the shutil.copy2 calls inside the `with open(...lock)` block
  accept: a selftest's verdict is about the clone that ran it
- finding:RIMMANDRAKE_RECORD_FULL_LAST_LINE_IN_TEST_TABLE_RUNS [open, polish] by BACKFILL, 2026-11-16T06:51:52Z: test_table.json runs_today.last is truncated at 200 characters (T_FW_COVER) and, for T_RESTORE, is a Python SyntaxWarning from stderr rather than the verdict line [measured, reruns.jsonl]
  proposed fix: the steward's recorder keeps stdout's last line whole; the comparer here treats a recorded prefix as a match
  accept: a recorded run can be compared with a rerun
- finding:RIMMANDRAKE_ASK_GOODS_WILD_FACTOR_BECOME_A_SLIDER [open, polish] by BACKFILL, 2026-11-16T06:51:52Z: the wild factor shipped as a constant 1.6 because adding a saved setting turns T_STAGE3_SCENES red until sc_settings_sweep's locked action text names it [measured: F1/F2 failed with goodsThrowWild saved]
  proposed fix: Conductor: allow the scene action text to name goodsThrowWild (a bar text change), then the four code lines
  accept: Every mod ships superb Mod Settings: tuning where a number is the experience (CLAUDE.md); sc_settings_sweep's action must name every saved setting (T_STAGE3_SCENES F1/F2)
- finding:RIMMANDRAKE_REPAIR_WILD_RATIO_BAND_FOR_INTEGER_CELLS [open, problem] by BACKFILL, 2026-11-16T06:51:52Z: integer cells: a good whose kernel raw is 1.5 cells throws 2 kernel cells and round(2.4) = 2 wild cells (ratio 1.0); a 1-cell rim good gets 1 or 2; any good at the blast's maximum gets ratio 1.0. Any correct build fails the band per good [measured: arithmetic of RM_KnockbackMath.Cells; […]
  proposed fix: neutral fixer rewrites the scene check; no code change
  accept: scenes.json sc_storeroom_mortar: 'every wild-to-kernel ratio between 1.3 and 2.0'
- finding:RIMMANDRAKE_READ_WILD_CELLS_FROM_ITEM_MOVE_NOT_REQUEST [open, polish] by BACKFILL, 2026-11-16T06:51:52Z: the request line is written at Enqueue, before the good's mass and throw are known; the fix journals kernelCells and wildCells on item_move (and too_weak skips carry dist and mass) [measured, read]
  proposed fix: scene text: request line -> item_move line
  accept: scenes.json: 'each good's request line carries its kernel cells and its wild cells'
- finding:RIMMANDRAKE_WIDEN_RESTORE_CHECK_VARIABLE_SETTINGS_ARGS_SLIP_PAST [open, polish] by BACKFILL, 2026-11-16T06:51:52Z · bars inv_proof_scenes: storeroom_pit_proof.py arm(): Settings(args=kv) is invisible (py_poke_kind falls back to the tool name)
  proposed fix: in py_poke_kind fall back to call.args[-1] only when no args= keyword exists
  accept: proof_restore_check sees every settings poke
- finding:RIMMANDRAKE_RESTORE_PUMP_TANK_SETTINGS_PRIOR_VARARG_HIDES_SETTER [open, polish] by BACKFILL, 2026-11-16T06:51:52Z: pump_outflow_live.py:174, tank_theft_live.py:80
  proposed fix: restore liquidPumpEnabled to its prior; make the wrapper visible
  accept: T_RESTORE baseline
- finding:RIMMANDRAKE_GUARD_PROOF_VERDICTS_FIVE_WEAKENED_STAYED_GREEN [open, polish] by BACKFILL, 2026-11-16T06:51:52Z · bars inv_proof_scenes: PF_PROOF_FLYOFF_SKIP_UNCHECKED, PF_GO_WALL_POSITION_UNCHECKED, PF_GO_WATER_UNCHECKED, PF_ST3_CONTAINER_ZERO_CELLS_OK, PF_ST3_FIREHALF_LANE_NOOP: missed offline
  proposed fix: extend validation.py --mock with one wrong-journal case per scene
  accept: the proof scenes' live verdicts check what their scenes promise
- finding:RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME [open, polish] by BACKFILL, 2026-11-16T06:51:52Z · bars pawn_flight_arc: RM_PawnFlyerPatches.cs: static Dictionary<Pawn,Job> Hauling, set at every launch, removed only at a knockback landing; never cleared on load, not saved
  proposed fix: clear Hauling in a GameComponent's FinalizeInit, or key it by thingIDNumber
  accept: a colonist thrown mid-haul goes back to its haul
- finding:RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED [open, polish] by BACKFILL, 2026-11-16T06:51:52Z · bars closed_container_holds: planted PF_MATH_JOLT_NO_DECAY passed T_KERNEL and lane 1 (fx_jolt_bounded tests only the bound)
  proposed fix: one T_KERNEL check
  accept: JoltOffset's own doc: a decaying shake (no bar requires decay)
- finding:RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT [open, polish] by BACKFILL, 2026-11-16T06:51:52Z · bars pawn_hits_pawn_stops: lane-1 row L1_PATH_RANDOM_CONSERVATION (lane1/lane1_rows.jsonl): FAIL, 42 of 30000 random grids, seed 20261115, one violation kind: 'pawn stop without the hit pawn next to it'
  proposed fix: in Resolve, after the back-off: if the backed-off cell is not adjacent to the hit cell, clear hitOther/hitDoor and the impact and report stop Distance (or None at 0 cells); a design call on what a blocked vault should do, hence Polish
  accept: A thrown person stops at another pawn in the way and takes an impact hit, as at a wall (sheet leaf pawn_hits_pawn_stops); inv_kernel: the path walk goes over sandbags
- finding:RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: absorb Extra Explosion Effects' idea, our own blast flecks, smoke, debris and big-blast shockwave
  proposed fix: Owner by card, 2026-11-12 ~4:5x PM PST (ledger note on RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB, OWNER tsn 1794530931586663595): Extra Explosion Effects -> "Absorb the idea into Knockback". The idea, not the mod: Explosive Knockback draws its own bigger, showier blasts with our own flecks and art; […]
  accept: `python3 src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py`, exit 0 with "PASS absorb blast show: 0 failing line(s)" (checks A1-A6: >= 4 own FleckDefs, textures resolve under EK, a StartExplosion/DoExplosion […]
- finding:RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY [open, problem] by BACKFILL, 2026-11-16T06:56:09Z · bars thrown_into_pit_falls: ExplosiveKnockback sc_storeroom_bomb_pit expects 'the stack aimed at the covered cell falls through it with one descent and the cover is destroyed', but no code does it: Building_SpanDeck's load sums living walking pawns only (FlowWorks Pits/Building_SpanDeck.cs ~256) and RM_ThingFlyer_Knockback never touches a […]
  proposed fix: Explosive Knockback sc_storeroom_bomb_pit expects "the stack aimed at the covered cell falls through it with one descent and the cover is destroyed". No code does it: Building_SpanDeck's load sums living walking pawns only (FlowWorks `Pits/Building_SpanDeck.cs` ~256) and `RM_ThingFlyer_Knockback` never touches a cover.
  accept: none, not written at filing
- finding:RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback 0.2.0: a thrown pawn landing on a pawn bruises both, scaled by its weight
  proposed fix: Explosive Knockback, Design Version 0.2.0 (next version; not 0.1.0). A thrown pawn that lands on a pawn standing on its landing cell (one that walked there mid-flight) gives both a small bruise, scaled by the thrown pawn's weight. […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback 0.1.0 Stage 3: build the checks for the 11 bars that are not runnable, offline
  proposed fix: not written by its filer: read item:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN
  accept: none, not written at filing
- finding:RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: flammable gas goes off clump by clump, each clump scattering goods and shoving people 1 cell (no damage, once per 2 s, never breaks pit covers); opt-in flammable tag on our gases incl. the Cauldron's
  proposed fix: Step 4 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.
  accept: none, not written at filing
- finding:RIMMANDRAKE_DEPLOY_KNOCKBACK_DRAWING_STORAGE_OPEN [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: review the 5 DIRTY files, then deploy so the game copy loses the closed-tag patch on Cold Storage lockers
  proposed fix: Deploy Explosive Knockback after the owner's 2026-11-12 open-storage ruling (OWNER:1794529787425697771). The repo deleted Patches/RM_Knockback_ClosedContainers.xml (it tagged RM_AncientStasisLocker_Kludged/_Refurbished/_Original and RM_EvaporativeCrock closed although they draw their contents); […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC [open, problem] by BACKFILL, 2026-11-16T06:56:09Z · bars hose_drops_at_takeoff: Explosive Knockback 0.2.0: a thrown pawn's carried thing flies its own trajectory
  proposed fix: Explosive Knockback, Design Version 0.2.0 (next version; not 0.1.0). When a blast throws a pawn that is carrying something, the carried thing leaves its hands and flies on its own trajectory, separate from the pawn. […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD [open, problem] by BACKFILL, 2026-11-16T06:56:09Z · bars no_careless_fall: Explosive Knockback: thrown goods truly fly (wild): arc, fast spin, rebound off walls until spent at ~70%; replaces the despawn-and-replace teleport at RM_MapComponent_Knockback.cs:474
  proposed fix: Step 1 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.
  accept: none, not written at filing
- finding:RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: a flying heavy stack that hits a person gives a small blunt hit and a stagger; light goods pass through
  proposed fix: Step 5 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.
  accept: none, not written at filing
- finding:RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: drop the every-storage exemption (RM_MapComponent_Knockback.cs:399); only closed containers keep contents, and the container itself gets a small shove; flip walk row light_things.item_on_a_shelf_stays
  proposed fix: Step 2 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.
  accept: none, not written at filing
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF [open, problem] by BACKFILL, 2026-11-16T06:56:09Z · bars frame_time_probe: Explosive Knockback: prove all-fly (no overflow cap) holds at most 50 ms per frame on a mortar barrage and a long gas chain on Archmagi; owns the walk scene walk_storeroom_raid
  proposed fix: Step 6 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.
  accept: none, not written at filing
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_HIDING_LOCKER_LIVE [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: re-prove closed containers live with LWM's Deep Storage weapons locker, no shelf or hopper tagged closed; delete or restage the two misleading sitting saves
  proposed fix: Re-prove Explosive Knockback's closed-container rule live, under the owner's 2026-11-12 ruling (OWNER:1794529787425697771): "Anything that draws its contents is open ... a shelf should be ruled as open, period. […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: stage and prove sc_blast_kinds' Outer Rim sonic and plasma grenade lanes
  proposed fix: Scene sc_blast_kinds now names its modded lanes (design/RimMandrake/explosion_mods_characterized_2026-11-12.md, section "The three unnamed lanes"): the modded damaging explosion is OuterRim_SonicGrenadeProj (damage OuterRim_Sonic, neronix17.outerrim.core); […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: prove goods thrown into a pit stay retrievable (a colonist fetches one from the pit floor down the ladder)
  proposed fix: Step 7 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.
  accept: none, not written at filing
- finding:RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: ExplosiveKnockback sc_closed_containers jolt rows print drawnOffset=UNMEASURED (RM_KnockbackProof_StageThree.cs) though the jolt is drawn since 587529cee1; the only counters (RM_MapComponent_Knockback JoltFrames/JoltMaxOffset) are map-wide and per frame: add a per-container drawn-offset read and make the row pass […]
  proposed fix: Explosive Knockback, sc_closed_containers (`design/concepts/ExplosiveKnockback/scenes.json`) expects "a drawn offset above zero on at least one tick in the thing trace" for each jolted container. The jolt is drawn since steward decision 6 of blind cycle 2 (587529cee1; […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS [open, problem] by BACKFILL, 2026-11-16T06:56:09Z: Explosive Knockback: rewrite the proof scenes so each asserts its start and runs a real control (17-row script audit)
  proposed fix: Step 8 of `design/concepts/ExplosiveKnockback/plan.md`. The 17-row `script_audit` in `design/concepts/ExplosiveKnockback/record.json` lists what each existing scene in `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` lacks and which scene in `scenes.json` it becomes. […]
  accept: none, not written at filing
- finding:RIMMANDRAKE_CENSUS_KNOCKBACK_STORAGE_OPEN_CLOSED [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: Explosive Knockback: offline census selftest, every storage def closed exactly when it hides its contents (Shelf, ShelfSmall, Hopper open)
  accept: none, not written at filing
  holder: Closed at c20328a876 by CONDUCTOR: census selftest landed and PASS at c20328a876 and dd70d7b1d0 (fingerprint updated); watched red on 6485aafec2^ and a planted Shelf tag; it found the Armoury's four hidden smuggling panels reading open, tagged closed by Patches/RM_Knockback_HiddenStorage.xml (c20328a876)
- finding:RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z · bars closed_container_holds, settings_scale_and_switch: ExplosiveKnockback: his card rewords the locked container bar to 'thrown a short way'; tree/sheet held because his coverage certificate is bound to the tree hash
  accept: `git apply design/concepts/ExplosiveKnockback/version/criterion_repairs/closed_containers_thrown_2026-11-15/tree_sheet_rewording.patch && python3 src/RimMandrake/rimflow/concept_tree.py gate design/concepts/ExplosiveKnockback | tail -1`
  holder: Closed at 0774d3bc1ac766899be71cd344fa328860f36d68 by CONDUCTOR: his card 'Certify, and fix the rule' re-recorded on the concept item (OWNER:1794748823561950419; the first recording sat on this item, which certify does not read); […] (0774d3bc1ac766899be71cd344fa328860f36d68)
- finding:RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: Explosive Knockback: every harmful explosion throws (bombs full, fire/incendiary half, other mods' damaging blasts too; not EMP/smoke/stun)
  accept: none, not written at filing
  holder: Closed at bb195048ac51 by OWNER: owner look of Station 6 incendiary passed (bb195048ac51)
- finding:RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: EK: a blast-hit closed container (crate, chest, locker) is THROWN as one unit, shorter than loose goods by mass, its contents inside and taking no blast damage; Station 5 showed the container standing still, the wrong behaviour
  accept: none, not written at filing
  holder: Closed at 0808c553030c by OWNER: no reason recorded (0808c553030c)
- finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: Explosive Knockback: a creature mass limit (150 kg, Mod Setting) replaces the body-size 2.5 cutoff; throw force = type force x this blast's damage / the type's defaultDamage (blastPowerFromDamage, on). Defaults and measured masses: D:\ClaudeWork\rimmandrake\conductor\ek_mass_20261113\DEFAULTS.md; […]
  proposed fix: not written by its filer: read item:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER
  accept: none, the oracle is the live scene sc_mass_and_power (rat/colonist/muffalo/thrumbo 5/3/2/0 at damage 50, 6/5/4/0 at 100) plus a kernel selftest the builder writes; a grep oracle would pass wrong code
- finding:RIMMANDRAKE_CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: Explosive Knockback 0.1.0: blind challenge cycle 2
  proposed fix: not written by its filer: read item:RIMMANDRAKE_CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED
  accept: none, not written at filing
- finding:RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: Explosive Knockback first-touch Designer pass (design/concepts/ExplosiveKnockback): stages 0-5 to a locked tree; owner certifies
  accept: none, not written at filing
  holder: Closed at 1a5234227788cf3e9479d4ccbcf98ac2ca712b3d by OWNER: Stage 5 locked: design/concepts/ExplosiveKnockback/stage.json status locked (landed 1a52342277), coverage passed on his word by the owner-certified stamp (concept_tree certify, eab59259ec; […] (1a5234227788cf3e9479d4ccbcf98ac2ca712b3d)
- finding:RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback container jolt draws a second copy of the graphic at the offset over the unmoved original (MapComponentUpdate b.Graphic.Draw), so a paused frame shows a doubled outline; whether it reads as a shake in motion is unjudged
  proposed fix: not written by its filer: read item:RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST
  accept: none, not written at filing
- finding:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback 0.1.0 Stage 6: in-game acceptance visit 1 (56 stage-6 checks), live driver via maturation.py launch, record in design/concepts/ExplosiveKnockback/version/in_game/visit_1
  proposed fix: not written by its filer: read item:RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST
  accept: none, not written at filing
- finding:RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED [open, problem] by BACKFILL, 2026-11-16T07:19:30Z · bars walk_storeroom_raid: ExplosiveKnockback: give RM_FrameProbe a bridge read (public static string Frame("begin|stop") on RM_KnockbackProof) so walk_storeroom_raid's FRAME_BUDGET row can be measured; today it is UNMEASURED by construction, so the walk can never PASS
  proposed fix: not written by its filer: read item:RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED
  accept: none, not written at filing
- finding:RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback walk save: dark blotches and haze lie over the four stations east of gas_chain (open_storage, heavy_knock, spared_states, goods_obstacles)
  proposed fix: not written by its filer: read item:RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN
  accept: none, not written at filing
- finding:RIMMANDRAKE_FIND_WHY_GAS_CHAIN_STOPS_FIVE_OF_SEVENTEEN [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_gas_chain, sc_cauldron_gas, P_gas_clumps FAIL at Stage 6 visit 1 (one scene): the lit Cauldron vent cloud burns one clump and stops on 5 of 17 runs, both lists; EK bursts only where the Cauldron's Ignite fires, so trace the fire scan or the seeded cloud on a failing run
  accept: none, not written at filing
  holder: Closed at d1817022db35 by CONDUCTOR: detached run: offline fix landed with its fuzz guard; live 17x rerun recorded UNRUN in the note for the next EK visit (d1817022db35)
- finding:RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_pit_fetch FAIL at visit 2: with the pits dry the hauler never climbs down the portable ladder for the stack (earlier passes were swims)
  proposed fix: not written by its filer: read item:RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT
  accept: none, not written at filing
- finding:RIMMANDRAKE_FIX_STOREROOM_COVER_STACK_PLAN_FOUR_RUNS_INVALID [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_storeroom_bomb_pit UNMEASURED at visit 2: no floor stack's plan ends on the covered near-row pit cell, even with the cover built first
  accept: none, not written at filing
  holder: Closed at ff8b4a952e08c6f7f48d54b74c01fc100caad567 by CONDUCTOR: detached run: cover-stack search fixed offline, selftest P red at base and green; live runner command UNRUN, recorded in the note (ff8b4a952e08c6f7f48d54b74c01fc100caad567)
- finding:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_walk_raid FAIL at visit 2: reload lost things, cover breaks with 0 descents, gas cells burst twice, one request has no outcome
  proposed fix: not written by its filer: read item:RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES
  accept: none, not written at filing
- finding:RIMMANDRAKE_GIVE_WALK_RAID_LIVE_MODE_STATIC_EXITS_ZERO [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z · bars walk_storeroom_raid: ExplosiveKnockback sc_walk_raid UNMEASURED at Stage 6 visit 1: its command 'validation.py --live walk_storeroom_raid' runs STATIC only and exits 0 (no --live mode, no walk_storeroom_raid leaf); write the leaf and the --live mode (full list)
  accept: none, not written at filing
  holder: Closed at 3d1f9ae2ca381ef96da719877cef395f87c118c6 by CONDUCTOR: detached run: leaf + --live mode landed; acceptance watched red on 67d5c3f318 and green after (evidence 2bff108457); live run UNRUN, recorded with its command (3d1f9ae2ca381ef96da719877cef395f87c118c6)
- finding:RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback spared_states: on the owner's full list the staged sleeper is not in its bed at the blast (INVALID), though it passes on the minimal list since a987289bca
  proposed fix: not written by its filer: read item:RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST
  accept: none, not written at filing
- finding:RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: EK: a landing knockback carrier places its stack Direct on an occupied cell, so vanilla GenSpawn shoves the resident stack aside unjournaled (and would destroy it with no free cell); land beside residents instead
  accept: none, not written at filing
  holder: Closed at 0808c553030c by CONDUCTOR: PlaceLanding never Direct onto a cell where it would shove; land_no_bump + _pit PASS, red under Plant directfirst; look save EK_LOOK_LANDING_MATRIX_20261112 (9 cells checked) (0808c553030c)
- finding:RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: Explosive Knockback still caps throws (40 per explosion, 60 item throws per map tick; RM_MapComponent_Knockback.cs:319 and :545) although plan step 1 (d_c_all_fly, his 'All of them fly') removes both caps and moves frame time to a proven bar. […]
  accept: none, not written at filing
  holder: Closed at 0808c553030c by OWNER: both caps removed (settings, code, UI); all_fly_no_cap PASS, red under Plant throwcap; perf: 25-HE blast into 195 stacks adds no slow frame at Normal speed (evidence perf2.jsonl) (0808c553030c)
- finding:RIMMANDRAKE_MOVE_PIT_FETCH_CORPSE_OFF_RIM_TOUCHED_ABOVE [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_pit_fetch: the corpse sits on the 3x3 pit's edge row, so a hauler on the rim touches it without descending; corpse out proves no ladder use
  proposed fix: not written by its filer: read item:RIMMANDRAKE_MOVE_PIT_FETCH_CORPSE_OFF_RIM_TOUCHED_ABOVE
  accept: none, not written at filing
- finding:RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_BARRAGE_P99_HELD_AGAIN [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback: re-certify the tree with the barrage bar as the p99 frame in the 0.9-8.25 s window (his '1 agree.'); tree/sheet words held as a patch because his certificate is bound to the tree hash
  accept: none, not written at filing
  holder: Closed at 0534f6c404bd93a1e2710dd66e3ea34ca1a990df by CONDUCTOR: acceptance passes (T1 today's tree 1, ALL PASS; coverage passed on the new OWNER event); rule fix 3aa7e5c15d, certify fab7999d8f, repin 5f6e2af989, evidence 0534f6c404; stage-4 exam retake filed as RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF (0534f6c404bd93a1e2710dd66e3ea34ca1a990df)
- finding:RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_barrage_perf FAIL at visit 2: the mod-off control's worst frame (104-151 ms) is itself over the 50 ms bar; neutral fixer for the criterion
  proposed fix: not written by its filer: read item:RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO
  accept: none, not written at filing
- finding:RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback: retake the Stage 4 Cold Reader exam against the re-certified tree (barrage p99 rewording); repin left stage 4 stale by its own rule
  proposed fix: not written by its filer: read item:RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF
  accept: none, not written at filing
- finding:RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: EK: goods the blast will throw take reduced blast damage (Mod Settings slider, default 25%, 100% = vanilla) so they scatter instead of being destroyed; a thrown stack stopped by a wall/door takes extra Blunt per cell of throw left (slider, default 10). […]
  accept: none, not written at filing
  holder: Closed at a593f1668f1a by CONDUCTOR: (a)+(b) built, deployed, live proof 13/13 PASS (a593f1668f1a)
- finding:RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING [open, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_settings_sweep: decide the kernel-side settings offline as a table test (default vs each changed setting over the lane, diff = only its own row), keep a thin live check for the game-side wiring only. […]
  proposed fix: not written by its filer: read item:RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING
  accept: none, not written at filing
- finding:RIMMANDRAKE_STAGE_HEAVY_LOCKER_LANE_LWM_CAPS_AT_58KG [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_closed_containers UNMEASURED at Stage 6 visit 1: its 76-249 kg closed-locker lane cannot be staged on LWM (WeaponsLocker 8 kg + 50 cap; WeaponsCabinet 8+30; Safe 500); stage a closed container on the test list that legitimately reaches the band
  accept: none, not written at filing
  holder: Closed at 7c910364ce62 by CONDUCTOR: heavy closed-locker lane now stageable at 76-249 kg on LWM (filter set, maxTotalMass raised for the scene); live proof UNRUN (7c910364ce62)
- finding:RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: Closed-container knockback cannot be shown in the 25-HE-shell storeroom: vanilla blast destroys every steel Hopper within r6 (measured d3.2-5.8, KB off) and both wood shelves; […]
  accept: none, not written at filing
  holder: Closed at bb195048ac51 by CONDUCTOR: Station 5 staged (3 HE shells, plasteel small shelf tagged closed): storage proof 10/10 incl. SA_CONTAINER_SURVIVES; SC_OFF row rewritten; save EK_SITTING_STATION5_CONTAINER_SURVIVES_20261112 (bb195048ac51)
- finding:RIMMANDRAKE_TRACE_PIT_FETCH_CONTROL_STACK_PAST_RAISED_LADDER [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_pit_fetch FAIL at Stage 6 visit 1: main lane passed (stack and corpse out by the ladder) but the raised-ladder control's stack also left its pit within 60000 ticks; find who carried it out and how (one run, cold noisy RM_TheRot map)
  accept: none, not written at filing
  holder: Closed at 7c17ebc62201 by CONDUCTOR: detached run: cause found offline. The control used RM_LadderPortable; FlowWorks' RM_CompLadder.EffectivelyRaised = raised && !Props.portable && setting, so a portable ladder never reads raised and the control pit stayed open (no escape bug in the mod). […] (7c17ebc62201)
- finding:RIMMANDRAKE_WRITE_GAS_INTO_PIT_SCENE_UNKNOWN_EVERY_BUILD [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:19:30Z: ExplosiveKnockback sc_gas_shove_into_pit UNMEASURED at Stage 6 visit 1: entry gas_into_pit is named by test_table.json but absent from RM_KnockbackProof.SceneNames ('unknown scene'); write the scene with its offline selftest
  accept: none, not written at filing
  holder: Closed at d4e34dda04ccb49c757e53ae69168be98c5596e1 by CONDUCTOR: detached run: scene and offline selftest landed; acceptance grep 2 and entry_exists true (d4e34dda04ccb49c757e53ae69168be98c5596e1)
- finding:RIMMANDRAKE_FLING_GOODS_WILD_FACTOR_NEVER_SHIPPED [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars goods_arc_spin_rebound: lane 1 L1_kernel_alone_goods_vs_person_distance: kernel and shipped settings carry no goods-distance factor; a 60 kg corpse beside a mortar flies 3 cells, a colonist 3 [measured]
  accept: sheet.md: loose goods and corpses fly wild, about 1.6 times as far as a person; tree.json advisory and scenes.json sc_storeroom_mortar: each good's request line carries its kernel cells and its wild cells, every wild-to-kernel ratio […]
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (81392aea384e9105a92263aea39b2d08c844c1f4)
- finding:RIMMANDRAKE_UNCOUPLE_GAS_GOODS_CAP_FROM_WEAPON_SCALE [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z: RM_MapComponent_Knockback.cs GasBurst builds KbConfig{ownCap = gasBurstGoodsCells}; Execute calls Kernel(cfg) -> KbLookup.Apply -> CapFor(ownCap, maxThrowCells, ownCapScale), so the 'weapons with their own maximum' scale (slider 0.25..2) rescales the gas goods cap: at 2.0 burning gas throws goods 4 cells, at 0.25 […]
  accept: sheet.md delegated: one gas clump burst throws goods at most 2 cells (gasBurstGoodsCells); settings_scale_and_switch oracle: each changed setting changes only its own outcome
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (81392aea384e9105a92263aea39b2d08c844c1f4)
- finding:RIMMANDRAKE_CORRECT_REBOUND_ALWAYS_RUNS_OUT_COMMENT [claimed_fixed, polish] by BACKFILL, 2026-11-16T07:20:06Z · bars goods_arc_spin_rebound: lane 1 L1_sweep_rebound_keep_slider_chain_ends: at goodsReboundKeepPercent 100 (slider top) ReboundCells(6,100) = 6, the kernel never ends the chain [measured]
  accept: kernel comment on ReboundCells: 'rounded DOWN so a throw always runs out'
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (81392aea384e9105a92263aea39b2d08c844c1f4)
- finding:RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars inv_proof_scenes: lane2/reruns.jsonl T_RESTORE FAIL
  accept: T_RESTORE: selftest_proof_restore_check.py prints RESULT: GREEN
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_SKIP_GOODS_WHEN_FLIGHT_OFF_OLD_HOP_LINGERED [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars settings_scale_and_switch: RM_MapComponent_Knockback.cs Execute: flyingGoods false fell through to DeSpawn + PlaceLanding (the instant move)
  accept: goods in the air off, goods unthrown, never the old hop
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_BUILD_CLOSED_GUARD_FIRE_HALF_SWITCHES_SHEET_NAMED [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars settings_scale_and_switch: RM_KnockbackMod.cs saved 46 settings, none switched either (journal questions 10, 14)
  accept: closed guard off, container goods thrown loose; fire at half off, fire throws nothing
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_DRAW_CONTAINER_JOLT_DUST_PUFF_WAS_ALL [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars closed_container_holds: ThrowContainer's !flew path: a dust puff and a journal line, nothing drawn on the container
  accept: else a jolt (sc_closed_containers: a drawn offset above zero for each jolt)
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_DELETE_DEAD_CONTAINER_SHOVE_KERNEL_TESTED_75_KG [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars closed_container_holds: ContainerShove/KbShove called by nothing in the game
  accept: the kernel tests test the rule the game runs
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_PIN_KNOCKBACK_NONPUSH_FORCES_IN_LINT_TABLE [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars every_harmful_blast_throws: T_LINT rc 0 on a copy with Flame 0.7
  accept: EMP, smoke, stun, extinguish and toxic gas at 0, fire at half
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_CORRECT_FLYING_OFF_WALK_ROW_TO_ITS_BAR [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars settings_scale_and_switch: validation.py, bar_lists_map.json, the walk's must-be-true list and required_checks.json carried off_is_the_instant_move
  accept: the walk row reports against its bar
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_DECIDE_RIM_THROW_BY_KERNEL_NOT_WILD_FACTOR [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars inv_too_weak_skip: lane1 INFO L1_rim_band_kernel_zero_wild_one: 14 of 291 distances (70 kg, r 2.9, step 0.01) had kernel 0 and wild 1
  accept: a thing at the rim whose kernel throw rounds to 0 cells is not thrown (skip too_weak); every_good_moves: reached = kernel throw >= 1
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (587529cee173)
- finding:RIMMANDRAKE_COVER_WILD_GAS_CAP_IN_KERNEL_DECIDER [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars inv_kernel: planted WildCells-ignored and scaleOwnCap-ignored passed T_KERNEL and T_FUZZ
  accept: T_KERNEL/T_FUZZ decide inv_kernel
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (04bb4c93faca)
- finding:RIMMANDRAKE_WIRE_CHECKS_SIX_PLANTED_FAULTS_PASSED_OFFLINE [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars inv_proof_scenes: 6 planted faults MISSED (planted_results.jsonl)
  accept: the offline deciders see breaks of the shipped wiring
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (04bb4c93faca)
- finding:RIMMANDRAKE_SWITCH_ELECTRICAL_BURN_WITH_FIRE_HALF_FLAME_HEIR [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars settings_scale_and_switch: Anomaly/Defs/DamageDefs/Damages_Environmental.xml: <DamageDef ParentName="Flame"> ElectricalBurn, <hediff>ElectricalBurn</hediff> (game Data, read 2026-11-15)
  accept: sheet.md: "fire at half ... the fire-half switch [is] on Mod Settings (off: fire throws nothing)"; the patch and the caller both name Anomaly's ElectricalBurn as fire
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (bace1c29cc)
- finding:RIMMANDRAKE_PROVE_PROOF_GATE_EXIT_AN_OR_PASSED_GREEN [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars inv_proof_scenes: planted PF_GATE_RELEASE_OR (and -> or) and PF_GATE_NO_EXIT (require_proof_build never exits) stayed green in all 23 offline suites (planted_results.jsonl)
  accept: inv_proof_scenes: the live scenes and the runner that drives them; T_PROOFGATE G1 claims the gate reads release vs proof answers
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (f181d3b6ea)
- finding:RIMMANDRAKE_RUN_STOREROOM_RESTORE_WAIVER_TAKEN_ON_TRUST [claimed_fixed, problem] by BACKFILL, 2026-11-16T07:20:06Z · bars inv_proof_scenes: storeroom_pit_proof.py's resets carry 'restore-check: ok', which the scanner takes on trust
  accept: T_RESTORE (decider of inv_proof_scenes): a live proof undoes every Mod Settings poke on every exit path, putting back the value it found
  holder: fixed by the blind cycle's fixer; no later judge verdict is recorded (f181d3b6ea)
- finding:RIMMANDRAKE_WRITE_GOODS_OBSTACLES_SCENE_NAMED_NEVER_BUILT [open, problem] by BACKFILL, 2026-11-16T07:20:20Z: ExplosiveKnockback sc_goods_obstacles UNMEASURED at Stage 6 visit 1: entry goods_obstacles is named by test_table.json but absent from RM_KnockbackProof.SceneNames ('unknown scene'); write the scene with its offline selftest
  proposed fix: not written by its filer: read item:RIMMANDRAKE_WRITE_GOODS_OBSTACLES_SCENE_NAMED_NEVER_BUILT
  accept: none, not written at filing
- finding:RIMMANDRAKE_WRITE_STOREROOM_BOMB_PIT_SCENE_TABLE_NAMED_FIRST [open, problem] by BACKFILL, 2026-11-16T07:20:20Z: ExplosiveKnockback sc_storeroom_bomb_pit UNMEASURED at Stage 6 visit 1: test_table.json names entry storeroom_bomb_pit in RM_KnockbackProof.cs but no such scene exists ('unknown scene' on every build); write the scene (observes per test_table) with its offline selftest
  proposed fix: not written by its filer: read item:RIMMANDRAKE_WRITE_STOREROOM_BOMB_PIT_SCENE_TABLE_NAMED_FIRST
  accept: none, not written at filing
- finding:RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE [open, problem] by BACKFILL, 2026-11-16T07:22:45Z: Explosive Knockback 0.1.0: run the blind offline challenge (Stages 4 and 5, tests first) by hand, one cycle, and write down its record format
  proposed fix: not written by its filer: read item:RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE
  accept: none, not written at filing

## Traps (6) — what a reader would otherwise get wrong
- trap:three-bar-sets-exist (design/validation_walks/RimMandrake/ExplosiveKnockback.md): Three bar sets exist. The 59 coverage checklist rows are the bars of 0.1.0, and Stage 6 reports against them. The 16 "north-star bars" (his card 2026-11-12, "Approve as written") and the 49 "must be true" rows of `design/validation_walks/RimMandrake/ExplosiveKnockback.md` (measured 2026-11-14; […]
- trap:the-locked-files-moved-after-the-lock (version/bars.md): The locked files moved after the lock. `version/bars.md` pins blobs at `237b791167`; since then `scenes.json` (sc_spared, sc_mass_and_power, sc_settings_sweep), `record.json` (decisions) and `tree.json` (the owner-certify stamp only) changed. The scene edits are test text (creatures chosen by mass, never named; […]
- trap:judge-round-count-has-three-answers (design/concepts/ExplosiveKnockback/journal.md:58): Judge round count has three answers (12 / 13 / 19); not reconciled (spec §10).
- trap:97-2-million-tokens (version/VERSION.json): 97.2 million tokens were charged to the Designer stage, 86.5 million of them estimates (`version/VERSION.json`).
- trap:proof-build-versus-release-build (RM_KnockbackProof.cs): Proof build versus release build. Most live scenes exist only in the proof build (`RM_KnockbackProof.cs`, `proof_build_gate.py`); the test queue cannot deploy a proof build today (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
- trap:the-scene-ids-in-scenes-json-are-not (scenes.json): The scene ids in `scenes.json` are not the scene names in the proof code. `scenes.json` entry points name 35 scenes by proof method; `RM_KnockbackProof.Names` holds 41 older names, and only some of the 35 are among them (measured in Stage 2 below).

## Causes refuted (0) — do not chase these again

## His answers (29)
- decision:version: Yes, fix it like that, and then please record this as an actual Pass.
- decision:q:you-can-t-fall-in-by: You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall.
- decision:q:1-1-totally-even-better-if: 1:1 totally. Even better if they can bounce inelastically off walls and rotate while they fly.
- decision:q:1-but-the-closed-containers-may: (1) but the closed containers may themselves get shoved a bit · 2 and remember the gas in the Cauldron
- decision:q:just-put-a-bomb-into-a: Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well.
- decision:q:1-anything-that-draws-its-contents: 1: Anything that draws its contents is open. … 4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly. No blockers.
- decision:q:we-really-shouldn-t-blow-back: We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it should fly. That should also be a function of the explosive damage itself as well. · with a single scene we can check ALL these things together · Melee shove is a great idea, but it belongs in FlowWorks, not here.
- decision:q:can-t-we-actually-simulate-that: can't we actually simulate that settings check offline? That seems a gratuitous use of the game, unless that's actually a very fast check?
- decision:q:rimmaster-run-codex-designer-to-questions-23-mods: 1:2 but don't invent new UI, there are already animal tools for this sort of thing 2:2 3:1
- decision:q:rimmandrake-bind-refusals-to-fixes-no-ceremony-loops: Designer fixes: loop ceiling -> twice the item's cap then park; EK certification -> show me the 4 gaps then I certify; Designer path -> light path when code exists
- decision:q:rimmandrake-design-maturation-pipeline-whole-mod-is-the-unit: Should a thrown pawn landing on another pawn hurt anyone? -> Bruise in the next version
- decision:q:rimmandrake-advance-flowworks-offline-beside-the-pilot: How many mods should advance at once? → All four now, offline only
- decision:finding:RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN: Thrown pawn lands on another pawn → Bruise in the next version
- decision:q:rimmandrake-release-stage-ceiling-per-mod-only-global-knob: Which release do you want? → Raise the limit to $100
- decision:q:rimmandrake-design-holder-pipeline-fusion-checklist-not-handoff: Anyone finding anything documents precisely how they would fix it but it goes back to the holder fully informed. Do all three side by side as a deeper test. When one reveals a needed fix to the system all three benefit. Try 400k first.
- decision:q:rimmandrake-build-mod-ledger-holders-three-pilots-at-once: I would like this tried at the same time on three mods concurrently so that we can observe different outcomes rapidly. It should roughly start where it last was in the pipeline as that is the same path it treads yes? Then start to build context and learning as it goes.
- decision:finding:RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH: EK 5 gaps → fix the 5 gaps then one more judge; gas shove onto an open pit drops the pawn in → yes, it stands
- decision:finding:RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER: I agree with the 2nd option though, pending tuning, and worse damage if they then hit a solid object.
- decision:finding:RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE: Hauling an item from within pit to storage zone out of pit worked!
- decision:finding:RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: the result was superb. Item scatter was exceptional, people and items flew into the pit, and more items survived the explosion than previously. Full pass I believe.
- decision:finding:RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS: Test 1: looks great! Full pass.
- decision:finding:RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE: I completed the requested assessment of the explosion knockback grid. It looks AWESOME. Some containers were destroyed and correctly barfed out their contents on the ground. Others were moved. Shelves lost their goods. It passed by what I knew to look for.
- decision:finding:RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE: No caps please.
- decision:finding:RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS: Confirmed, build the unbuilt items and bug.
- decision:finding:RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB: Better Explosions and Dynamic Effects Forge -> Keep both for good; Custom Gas Types -> Keep it as a separate mod
- decision:finding:RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER: It's fine. This doesn't need a human review. Just accept it as a pass and go on.
- decision:finding:RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING: Do you certify ExplosiveKnockback's tree with the container now thrown a short way? → Certify, and fix the rule
- decision:finding:RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO: 1 agree.
- decision:finding:RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN: Closed container near a blast: slide one cell as the locked bar says, or thrown as built? → Throw it, as built; the locked bar's wording changes by his word from 'slides one cell' to 'thrown a short way', and the test follows

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

spend recorded: USD 70.74, 138207197 tokens

## Closed findings (1)
- finding:RIMMANDRAKE_DECIDE_EXPLOSION_MODS_KEEP_ABSORB withdrawn (reading) c20328a876

## Tests (44, 20 older left out)
- 2026-11-16T06:51:52Z live.run bar:inv_heavy_knock: PASS on 2f74ac9094e5 visit_2 sc_heavy_knock PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_hook: PASS on 366bed691c96 visit_2 sc_mortar_throw PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_hook: PASS on ae820721648d visit_1 sc_mortar_throw PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_hose_drop: PASS on 2f74ac9094e5 visit_2 sc_hose_drop PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_items_teleport: PASS on 2f74ac9094e5 visit_2 sc_storeroom_mortar PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_items_teleport: PASS on 366bed691c96 visit_2 sc_gas_chain PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_items_teleport: PASS on ae820721648d visit_1 sc_storeroom_mortar PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_killed_corpse: PASS on 2f74ac9094e5 visit_2 sc_killed_thrown PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_pawn_flyer: PASS on 2f74ac9094e5 visit_2 sc_pawn_arc PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_pawn_flyer: PASS on 2f74ac9094e5 visit_2 sc_wall_stop PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_pawn_flyer: PASS on ae820721648d visit_1 sc_pawn_arc PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_pawn_flyer: PASS on ae820721648d visit_1 sc_wall_stop PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_perf_all_fly: FAIL on 250539584b1b visit_2 sc_barrage_perf FAIL (runner FAIL)
- 2026-11-16T06:51:52Z live.run bar:inv_pit_floor_haul: FAIL on 2d0685e9e6c5 visit_2 sc_pit_fetch FAIL (runner FAIL)
- 2026-11-16T06:51:52Z live.run bar:inv_pit_floor_haul: FAIL on ae820721648d visit_1 sc_pit_fetch FAIL (runner FAIL)
- 2026-11-16T06:51:52Z live.run bar:inv_pits_receive: PASS on 2f74ac9094e5 visit_2 sc_cover_breaks PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_pits_receive: PASS on 2f74ac9094e5 visit_2 sc_pit_fall PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_pits_receive: PASS on ae820721648d visit_1 sc_pit_fall PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_recovery: PASS on 2f74ac9094e5 visit_2 sc_recovery PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_recovery: PASS on ae820721648d visit_1 sc_recovery PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_settings: PASS on 2f74ac9094e5 visit_2 sc_settings_off PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_settings: PASS on 2f74ac9094e5 visit_2 sc_settings_sweep PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_settings: PASS on ae820721648d visit_1 sc_settings_off PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_settings: PASS on ae820721648d visit_1 sc_settings_sweep PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_shelf_skip: PASS on 2f74ac9094e5 visit_2 sc_open_storage PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_shelf_skip: PASS on ae820721648d visit_1 sc_open_storage PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_shield: PASS on 2f74ac9094e5 visit_2 sc_shield PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_shield: PASS on ae820721648d visit_1 sc_shield PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_weapon_ext_fields: PASS on 2f74ac9094e5 visit_2 sc_lookup PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_which_blasts: PASS on 2f74ac9094e5 visit_2 sc_blast_kinds PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_who_is_spared: PASS on 2f74ac9094e5 visit_2 sc_spared PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:inv_who_is_spared: PASS on ae820721648d visit_1 sc_spared PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:no_careless_fall: PASS on 2f74ac9094e5 visit_2 sc_no_careless_fall PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:no_careless_fall: PASS on ae820721648d visit_1 sc_no_careless_fall PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:only_explosions_throw: PASS on 2f74ac9094e5 visit_2 sc_only_explosions PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:only_explosions_throw: PASS on ae820721648d visit_1 sc_only_explosions PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:pawn_hits_pawn_stops: PASS on 2f74ac9094e5 visit_2 sc_pawn_hits_pawn PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:pawn_hits_pawn_stops: PASS on ae820721648d visit_1 sc_pawn_hits_pawn PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:people_thrown_three_cells: PASS on 2f74ac9094e5 visit_2 sc_over_sandbags PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:people_thrown_three_cells: PASS on ae820721648d visit_1 sc_over_sandbags PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:thrown_into_pit_falls: PASS on 2f74ac9094e5 visit_2 sc_pit_enemy PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:thrown_into_pit_falls: PASS on ae820721648d visit_1 sc_pit_enemy PASS (runner PASS)
- 2026-11-16T06:51:52Z live.run bar:walk_storeroom_raid: FAIL on 61567a7b7559 visit_2 sc_walk_raid FAIL (runner FAIL)
- 2026-11-16T06:51:52Z live.run bar:walk_storeroom_raid: UNMEASURED on 1a593788b36d visit_1 sc_walk_raid UNMEASURED (runner NO_ENTRY)

## Left out
- decisions: 3, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- tests: 20, oldest first (`modledger.py show --mod ExplosiveKnockback <subject>`)
- the full history: 334 events (views/history.md; never read whole)

cursor: t=2026-11-16T08:00:20Z.1794816020603047096 (modledger.py since --mod ExplosiveKnockback t=2026-11-16T08:00:20Z.1794816020603047096 prints what changed after this packet)
