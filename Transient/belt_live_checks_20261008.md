# Live checks 2026-10-08

(append per step)
- tier live_20261008 added to modset_builder (biomes+gss+hugethings)
- 17:xx killed game, deployed biomes compose (28 files; HugeThings already in sync), moved Scarlands stub to RimWorld/_ModsAside, tier applied (16 mods), launched via steam

## HugeThings (HUGETHINGS_TITANIC_CCTOR_THROWS_1)
- A1 PASS: Player.log line 173 "[RimMandrake.TitanicCreatures] ready: 4 patches, 98 races auto-tiered."; no "Error in static constructor" in log.
- A2 PASS: modcheck run HugeThings -> wake.t1_beast_trails_rubble_and_tramples_plants PASS, wake_off PASS, crush_damage_multiplier PASS (Transient/modcheck/HugeThings_20261008T172200Z.json).
- Unrelated FAIL in same run: trunk.full_grown_giant_gets_its_measured_footprint (RM_Nogtyl at growth 1 has 0 blockers) - giant-plant trunk, not this item; 18 not_driven rows UNMEASURED by design.
- modcheck run Wasteland (swap route) had no Wasteland map (RM_TheRot); switching to Transient/acc_biomes/batch.sh retile+run_live_suite

## Wasteland (WASTELAND_TOXIC_BUILDUP_NEVER_APPLIES_1) - retile RM_Wasteland + run_live_suite, sheet Transient/modcheck/Wasteland_20261008T175942Z.json (177 PASS / 9 FAIL / 2 UNMEASURED)
- A1 PASS: middenshell_procession.incident_is_blocked_when_the_body_is_switched_off PASS.
- A2 NOT MET (UNMEASURED): tipping_off_refuses_the_offer - ON control RM_RiteOfTipping canFireNow=False even with tipping on (fixture limit: earliestDay 8 / minRefireDays 30 per checklist); not a toggle verdict.
- A3 PASS: ash storm dose, halo/cinderwire warning-hold + begin, phases-off, Middenshell aura (ambient_aura_doses_a_pawn_beside_it) all PASS with _wait_dose.
- Still FAIL (not in these criteria, mod-side or harness): smolderback_doses_its_own_room, processor_animals x3 (sloghog off feed ground; sootgrazer unreadable), gripper x2 / brine_deposits (30 s bridge timeout, no _patient), flora_harvest x2 (Pusberry RawBerries, Wartshrub Chemfuel never yield).

## Contagion (CONTAGION_LIVE_SUITE_FAILS_ACC_BIOMES_1) - retile RM_Contagion + run_live_suite, Transient/modcheck/Contagion_20261008T180840Z.json
- A1 PASS: burn_forced.native_dives_for_roof PASS (verdict; the per-sample native_track is not serialised into the json, the check passes if any sample or the final position is under the patch).
- A2 PASS: genome.inject_starts_gestation PASS, no 30 s timeout.
- A3 NOT MET: coalescence_emits_manhunters is UNMEASURED because upstream coalescence_absorbs_and_grows_a_stage FAILED (absorbed 6 Unfinished, Coalescence reads Stage 1 mass 5, want Stage>=2 at mass>=6; 2 of 6 still alive) - fixture/mechanic, not the manhunter check. 
- A4 PASS: 20 fresh RM_TheUnfinished (Transient/belt_a4_unfinished.json): 0 downed, min Consciousness 1.0, limb hediffs only on paws/ears/eyes/nose/tail/jaw, none on brain/heart/lung.
- New FAIL: burn_forced.burn_off_means_no_harm ("a fresh exposed visitor was dosed with burnEnabled off") - not investigated.

## Ledges of Mercy (CRACKEDLANDS_LEDGES_OF_MERCY_1) - retile RM_FloodedCanyon (map 3), debug actions via Actions\<label>, scripts Transient/belt_ledges_*.py
- A5 PASS: freshly generated RM_FloodedCanyon map carries RM_MercyLedge / RM_MercyCarving / RM_ChimeLineAnchor from mapgen; no error/exception lines in Player.log across the regen.
- A1 PASS: "Carve mercy ledges now" -> ledges=3 ledgeCells=13 carvings=3 anchorsPlaced=6; "Report ledge refuge" -> ledgeDefs=1 anchorDefs=1 refugeCells=30.
- A4 PASS: drafted colonist at the ledge cell beside a carving: carvingReaders 0 -> 1, stayed 1 across 3 x 600 ticks; pawn_thoughts shows RM_ReadMercyCarving (+4) once; inspect = "Inscription: [placeholder ...]" + "Read by 1 person".
- A3 PASS: Transient/belt_ledges_a23.py: neutral Villager (faction OutlanderCivil) + trained (Obedience) Muffalo spawned ~far from ledges; at the debug-armed warning seekers=2 enRoute=2 sentTotal=2 (t+30); later onLedge=2 heldTotal=2 (state read). The harness chain ledge_refuge was UNMEASURED (site: animal spawns on the debug ledge, plus no neutral visitor spawn) so this was driven by hand.
- A2 PASS (flood measured in progress, not to recede): phase=Flooding activeFloodCells=400, refugeFlooded=0 at 5 reads over ~2500 ticks; then "Recede flood NOW". Side evidence: the visitor read a carving (carvingReaders 1 -> 2).
