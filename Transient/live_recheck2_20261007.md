# Live recheck 2 on acc_harness-31, 2026-10-07 ~12:50-13:05 PDT (nothing committed; no rimflow verify recorded)
Raw results: Transient/l2sweep_<Mod>.json (previous run kept as .prev.json), Transient/rc2_FallLineArrivals.json (identical rerun),
Transient/rc2_TitanicCreatures_patched.json (Titanic with a TEMP copy of validation.py at Transient/rc2_titanic/validation.py).
Summarise any of them with `python3 Transient/l2sum2.py <json> [width]`. One-off probes: rc2_call.py, rc2_wake.py, rc2_menu.py, rc2_dbg.py.

## TitanicCreatures
| component | result | evidence | class |
|---|---|---|---|
| Player.log "is not a Def type" | PASS | 0 occurrences of "is not a Def type" / "RM_CrushRuleDef" in the fresh log | - |
| RM_CrushRuleDef / RM_TitanicTierDef defs load | PASS (direct) | get_defs with the NAMESPACED type `RimMandrake.TitanicCreatures.RM_CrushRuleDef/RM_Crush_Buildings` -> crushable true, minTier T2; `...RM_TitanicTierDef/RM_TitanicTiers_Default` -> 4.0/8.0/20.0 | - |
| tier_ladder, crush_rules (as shipped) | FAIL/UNMEASURED | validation.py asks for bare `RM_CrushRuleDef/..`: get_defs answers "No def TYPE named 'RM_CrushRuleDef'" (GenTypes lookup by bare name misses a namespaced class) | HARNESS (3 literals in validation.py: lines ~249, ~272 need the namespaced type) |
| same two with namespaced names (temp copy) | PASS, PASS | thresholds match XML and ascend; rules read back as the XML says | - |
| wake: t1_beast_trails_rubble_and_tramples_plants | PASS (temp copy, lane spacing 14) | Elephant left rubble and destroyed the 6 5-HP plants, Rat control clean. As shipped: UNMEASURED - beast_plants 0 of 6 (trampled) but control Rat lane showed ctl_filth 2 | HARNESS: control lane only 6 cells from the beast, the Elephant wanders after Goto and rubbles it; ambient tiered creatures (298 races auto-tiered) also scatter Filth_RubbleRock map-wide, and clear_area does not clear Filth |
| wake_off_leaves_no_trail | FAIL (flaky) | 1 rubble in the beast rect with wakeEnabled=false, plants intact 6/6. Direct repro (filth wiped, wake off, lone Elephant, 800 ticks): 0 filth, 6/6 plants. Source: only TitanicWakeProcessor makes Filth_RubbleRock and it returns first when wakeEnabled is off | HARNESS (stray rubble from ambient wanderers in a 16x3 rect) |
| crush_damage_multiplier_scales_the_blow | UNMEASURED | upstream failed in the temp copy; as shipped the contaminated lane | HARNESS |
| harmony x4, settings_roundtrip x13, defs_resolve | PASS | |  |
| not_driven x5 (T2/T3, yield curve, roof, footprint) | UNMEASURED | no bodySize>=8 race in a vanilla list; unchanged | LIST ARTIFACT |
Proposal (not applied): namespaced type in the two get_defs calls; lane spacing >=14 and a Filth sweep (destroy_batch categories=Filth) before each _run; make wake_off compare against a wake-ON delta or read a bigger rect-free signal (plants intact) instead of any filth.

## FallLineArrivals chain gate: PASS (all 11 components of the suite PASS)
off_fall_line_refused, anywhere_allows, wrecks_toggle_off_refuses all PASS; ProofGate gets args 'x' (Session.call logged params). NOTE: my first sweep appeared to FAIL with "ProofGate with 0 params" only because I had edited the sweep script to write rc2_*.json, so I was re-reading the stale l2sweep json. Real rerun = PASS.

## WreckedMachines: PASS on all targets (0 FAIL; 3 UNMEASURED by design)
allowDonorSmelter and allowFullRestoration rewrite+restore PASS (designationCategory null reads as {} -> VFEFactory_Factories when on). wreckedRatio PASS: power_net on RM_WM_PowerCell_Wrecked connected, gain 1.67e-05 at 0.001 -> 1.67e-04 at 0.01 (10x), restored. The three spawns_and_inspects_clean now PASS. UNMEASURED (unchanged): requireLowerGradeUnderneath, enableSalvagedEmanators (play-time reads), replace_tags_build_over_live (no blueprint tool).

## Droidworks protocol_droid_shifts_prices: UNMEASURED (retries ran; not a mod verdict)
Fired with worker pick, OutlanderCivil x2, TribeCivil; OutlanderRough/TribeRough do not exist in this world. All: canFireNow=True, fired=False. Player.log: "Faction Homestead Defense League of def OutlanderCivil has no usable PawnGroupMakers for parms groupKind=Trader, tile=71566,0 ... points=597" (same for TribeCivil). Core OutlanderCivil Trader group has Town_Trader + carriers, so the cause is the quicktest tile/biome (carrier/pack-animal check), not Droidworks. Class: LIST ARTIFACT / HARNESS (quicktest world). Fix idea: a trader-capable fixture (spawn a trader pawn directly or a tile whose biome allows pack animals). Other Droidworks results in this run, not in scope and NOT re-triaged: head_drops_with_identity FAIL (no Head_Battle in blast area), mood_penalty_nearby FAIL (no RSW_DW_NearBoltedDroid thought on bystander), ion_overload FAIL (no RSW_JawaIon_Stun: Ion mod absent, expected LIST ARTIFACT).

## UnfinishedLine: PASS (all components PASS, all_green True)
volunteer_offered PASS with the Enclaves (RUT_Jawa_FreeDroidEnclaves) ally fixture; the three downstream components ran PASS. Side effect: Player<->Enclaves left at Ally on this map (disposable).

## LuminousPigment
| component | result | evidence |
|---|---|---|
| settings_apply.glowtank_toggle | PASS | also press_unbuildable, cuisine_recipes_toggle, apply_reaches_defs PASS |
| build menu really refreshes | PASS (measured) | existing tool rimworld/list_architect_designators categoryId=architect-category:production: default 83 designators incl. architect-designator:production:build-rm-glowtank; glowTankEnabled=False + Mod Settings open/close -> 82, no glowtank; restored True + apply -> 83 with glowtank. Probe: Transient/rc2_menu.py |
Still failing (unchanged class from L2 triage, not re-triaged): patches_applied (designators read as 'RuntimeType'), mat_alive_control, unlocked_after_sighting (RM_Crowncarpet cannot grow on the quicktest terrain - LIST ARTIFACT), press_is_a_powered_bench (W vs per-tick unit - HARNESS), wall_beauty_bonus (NoSuchThingId), light_follows_the_walker, styling_station_lacquers_a_parka, titled_pawn_in_two_coats (RM_SawCommonerInDeepfire active before wearing), a_gods_own_idol_moves_it_by_fifteen; gods x5 UNMEASURED because mandrake.rm.ninefold is not in the list (LIST ARTIFACT); press_buildable_finishes_research and painting_enabled_blocks_ai UNMEASURED.

## Settings
Each suite restores its own fields; spot-checked wakeEnabled=True (Titanic) and glowTankEnabled=True (LuminousPigment). Game left running, bridge not released.
rimflow verify: none recorded. TITANIC_CREATURES_FIRST_SCRIPT_1 criteria are whole-run GREEN-MIN wording, not a single chain component.
