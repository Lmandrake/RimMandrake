# GREEN-MIN live runs, batch 2 (FOUNDRY helper, 2026-10-07, 13:03-14:10 PDT)

Method: tier `acc_green_min2` (added to `src/RimMandrake/Utils/modset_builder.py`, uncommitted; biomes + patches + swbestiary + gimmesomeslack + luminouspigment + ninefold + pyrelandsmechanics + donors), game killed/relaunched via Steam, then `modcheck run <Mod>` per mod with MODCHECK_SKIP_DEPLOY=1, each on a FRESH quicktest map (`rimworld/go_to_main_menu` first) so no cross-run contamination. Driver logs: `Transient/green_min_runs2_20261007.log`, `..._runs2b_...log`. Classes: harness | site | mod | unmeasured.

## PyrelandsMechanics (PYRELANDS_MECHANICS_FIRST_SCRIPT_1 A2/A3)
- result: `/home/mandrake/rm/foundry/Transient/modcheck/PyrelandsMechanics_20261007T202903Z.json` (7 PASS, offline-half only) and, after adding two explicit UNMEASURED rows for the unproven bars, the latest `PyrelandsMechanics_20261007T2042*Z.json` (7 PASS / 0 FAIL / 2 UNMEASURED).
- UNMEASURED (A3, recorded in the results rows): arson_debt_past_threshold_fires_fireraid, flameharvest_needs_flameHarvestMinFires. Reason: no bridge tool reads/sets the arson debt tally or lists fires for a threshold sweep. Script change: `src/RimUtinni/PyrelandsMechanics/validation.py` (new chain `unproven_bars`).

## Greentide (GREENTIDE_FIRST_SCRIPT_1 A3)
- result: `/home/mandrake/rm/foundry/Transient/modcheck/Greentide_20261007T203123Z.json`, 57 PASS / 0 FAIL / 7 UNMEASURED. All seven classified UNMEASURED (capability gaps, not mod verdicts): fever_mark_earned_by_surviving_the_coma (needs seeded collapse-stage hediff + tend), ambient_frenzy_incident (dry-run is no instrument), churnmud_seeded_once_on_a_fresh_non_greentide_map and roil_lock_absent_on_a_new_map_with_roil_off (WORLDGEN-AFFECTING, need a freshly generated map), stench_smoke_radius_follows_multiplier (no smoke-cloud reader), krannock_spawn_gate (deliberate no-op until rostered), fruitfall_spawns_grubs_near_a_live_bole (needs generated Greentide map + forced event).

## CreatureBehaviors (CREATURE_BEHAVIORS_FIRST_SCRIPT_1 A3)
- result: `/home/mandrake/rm/foundry/Transient/modcheck/CreatureBehaviors_20261007T203753Z.json`, 87 PASS / 0 FAIL / 1 UNMEASURED.
- track_grid/walker_lays_prints UNMEASURED -> HARNESS: `_regen` polled `rimbridge/get_bridge_status` for a `currentMapReady` key that the bridge never reports (state keys: programState, currentMapId, longEventPending, automationReady, visualReady, tick). Fixed in `src/RimMandrake/CreatureBehaviors/validation.py` (accepts automationReady+currentMapId+!longEventPending); same fix in `src/RimMandrake/NightsideIce/validation.py` and Stillsand. NOT re-run after the fix (6.5 min).

## LuminousPigment (LUMINOUS_PIGMENT_FIRST_SCRIPT_1 A2)
- result: `/home/mandrake/rm/foundry/Transient/modcheck/LuminousPigment_20261007T204156Z.json` (fresh map, Ninefold loaded): 49 PASS / 7 FAIL / 15 UNMEASURED. (An earlier run on the dirty shared map, `LuminousPigment_20261007T200805Z.json`, was 33/11/27; the gods chain needs mandrake.rm.ninefold on the tier, now fixed.)
- FAILs:
  - defs_load/patches_applied -> HARNESS: get_defs serialises `specialDesignatorClasses` entries as the string 'RuntimeType' (all six), so the substring test for Designator_Deepfire can never pass; the script only guards "not a list".
  - research_gate/unlocked_after_sighting -> SITE: set_plants RM_Crowncarpet REJECTED "terrain or conditions cannot support" on the bland map (both runs).
  - press_refine/press_is_a_powered_bench -> HARNESS: unit mismatch. Observed -0.0025/tick = 150 W / 60000 (WattsToWattDaysPerTick); the check expects -2.5 (150/60). Constant from engine knowledge, not re-decompiled today.
  - first_coat/wall_beauty_bonus_exact_and_not_doubled -> HARNESS (likely): thing_stats got NoSuchThingId for the fixture wall in both runs (ids 104153, 58258); the id is stale after the coat step replaces/re-ids the wall. Mod defect not excluded.
  - worn_glow/light_follows_the_walker -> SITE: first sample shows tracked=true, proxy on the pawn's cell, but roofed=false; 32 of 54 samples fail the script's `roofed` + dark-cell premise, i.e. the 30-cell walk leaves the roofed strip. Mod not shown wrong.
  - styling_lacquer/styling_station_lacquers_a_parka -> SITE/HARNESS: parka reached coats=1 (the loop broke on it); the check then demands `deepfireOnMap == 0` but the count is map-wide (3 at setup, 21 later: other chains' deepfire). 
  - status/titled_pawn_in_two_coats -> SITE: RM_SawCommonerInDeepfire already active before anyone wears anything (leftover state from earlier chains on the same map; failed identically in both runs).
- 15 UNMEASURED are downstream of those or flagged inline (research_availability reports no finished flag, glowtank never accepted a seed, AI-painting control).

## Stillsand (STILLSAND_FIRST_SCRIPT_1 A2 plus the world_commit race)
- The `Collection was modified` RegenerateNow race did NOT reproduce: world_commit returned success (failedSteps 0) in three fresh attempts (map tile 46090). Prior failure stays unexplained engine/bridge flake, not recorded as reproduced.
- Attempt 1 `Stillsand_20261007T201757Z.json` (43 PASS / 0 FAIL / 63 UNMEASURED): HARNESS, `_regen` waited 300 s for the nonexistent `currentMapReady` key. Fixed in `src/RimMandrake/Stillsand/validation.py`.
- Attempt 3 (final): `/home/mandrake/rm/foundry/Transient/modcheck/Stillsand_20261007T205531Z.json`, 83 PASS / 2 FAIL / 21 UNMEASURED. (Attempt 2 was cut by my own 580 s timeout: no JSON.)
- FAILs: sun/sun_roof_cover_above_55deg: roofs verified placed (36 cells) yet shadegrid_read gives exposure 1.00 under the roof at 60.5 deg -> UNRESOLVED mod-or-harness (read happens in the same tick as set_roof_batch; ShadeGrid cache staleness not excluded). muurrok/muurrok_emergence_fires: 'A line of glare' letter sent (fire_incident fired:true, canFireNow:false) but 0 RM_Muurrok 2600 ticks later -> MOD suspected, unproven (spawn gating/pawn despawn not read).
- UNMEASURED (21): classified inline by the script: eruption needs tick>=300000, horizon vanilla trader refuses, gale permanent weather controllers shadow the gale, 4 'remainder' rows need campaign tier/other mods, glass rows not driven, get_defs custom type names unproven (`RM_PreciousCaveDef/...`), glare site left pad, log buffer near cap.

## IshkoDarkLandmarks (NORTHSTAR_ISHKO_PILOT_1 A2/A3)
- First live_session attempt: `Transient/northstar/IshkoDarkLandmarks_20261007T205638Z.json` REFUSED at preflight (game_loaded FAIL: JawaBench TypeLoadException, the `ishko` tier lacked mandrake.rm.gimmesomeslack) -> SITE/tier; fixed in modset_builder.py `ishko`.
- Second attempt: `/home/mandrake/rm/foundry/Transient/northstar/IshkoDarkLandmarks_20261007T205744Z.json` GREEN 8 PASS / 0 FAIL / 0 UNMEASURED; re-run after the script edit (the edit moved the mod hash, status read STALE): `/home/mandrake/rm/foundry/Transient/northstar/IshkoDarkLandmarks_20261007T205850Z.json` GREEN 8/0/0, recorded by the driver through status.record_run at hash 73f927b79dfb (`modcheck status`: GREEN at current hash). A2 met.
- A3: learnings written as a `LEARNED` block into `/home/mandrake/rm/foundry/src/RimUtinni/IshkoDarkLandmarks/validation.py` (docstring) and a note in `/home/mandrake/rm/foundry/src/RimUtinni/IshkoDarkLandmarks/northstar_plan.py`; the tier fix is in `/home/mandrake/rm/foundry/src/RimMandrake/Utils/modset_builder.py`.

## FlowWorks (FLOWWORKS_NORTHSTAR_BASELINE_RUN_1 / TRIAL_1)
- Live run on the `flowworks` tier (11 mods), `validation_v2.py --live --fresh-map`, 254 s wall, NOT run through `modcheck run` (its old validation.py path was REFUSED earlier for unclaimed must-show lines; validation_v2 is the recorded FlowWorks instrument, last recorded run `validation_v2_result_20261006T064707.json`).
- result: `/home/mandrake/rm/foundry/src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261007T140351.json` : 50 PASS / 9 FAIL / 0 UNMEASURED. The previous recorded run (20261006T064707, assembly 5d44e05927dc) was 59/0/0; this run's assembly is eeeba804299f (rebuilt since: `f056d3012` sluice seals when shut, FLOWWORKS_CONTAINER_MATERIALS_1 commits). Same script, same site prep, same fresh-map flow, so the delta is the DLL.
- FAILs, all classified MOD (script's own cls=MOD; regression candidates, not fixed): P3_walk_in_held, P4_ladder_frees, P4b_ladder_raised_strands, P5n_own_faction_carveout (a colonist never walks into/gets held in the pit; descents 0->0), X2_pawn_lowers_walking_in (arrived False, sink 0->0), X3_pawn_rises_walking_out, X1_pawn_height_ladder (hares at D2/D3/D4 all sink=0.5, wallOverHead 0.6/0.9/1.2 as expected but sink flat), X4_pit_wall_over_head (colonist on D=4 drawn 0 cells down), X5_slime_occupant_below_surface (D4 occupant drawn 0.5 down vs the dry D4 1.20 the script expects). Common cause not isolated: the pawn-descent/sink path. Harness/site not indicated (50 rows incl. fluid, fire, cover and settings rows pass on the same map).
- Not run: GREEN_MINIMAL_1 criteria; BASELINE_RUN_1 A2/A3 and TRIAL_1 A1/A4 NOT recorded (run is NOT GREEN, no sheet in Transient/modcheck, findings not yet filed as ledger items).

## Criteria recorded
(see below)

Recorded with `rimflow verify ... --level GREEN-MIN --criterion`: NORTHSTAR_ISHKO_PILOT_1 A2 (config ishko), A3; GREENTIDE_FIRST_SCRIPT_1 A3 (-> done); PYRELANDS_MECHANICS_FIRST_SCRIPT_1 A2 and A3 (-> done); LUMINOUS_PIGMENT_FIRST_SCRIPT_1 A2 (-> done). Config acc_green_min2 for the biomes-tier ones. Ledger writes are local, uncommitted; closed-item prose moved to items/closed/ (stage both paths).
NOT recorded: CREATURE_BEHAVIORS_FIRST_SCRIPT_1 A3 ("passes ... every non-pass classified": 87/0/1, the one UNMEASURED is a harness bug whose fix was not re-run), STILLSAND_FIRST_SCRIPT_1 A2 (two FAILs not conclusively classified), all FlowWorks criteria.
Side effects to know: PyrelandsMechanics status is now RED (two deliberate UNMEASURED rows); CreatureBehaviors/Stillsand status read STALE after the readiness fix (hash moved).

## MOD DEFECT list
1. FlowWorks pawn pit descent/sink regression since DLL eeeba804299f (9 rows above) -- likeliest suspects f056d3012 / fe20a045f (sluice door change) or the container-materials commits; needs a bisect.
2. Stillsand RM_MuurrokEmergence: letter sent, 0 RM_Muurrok after 2600 ticks (suspected, unproven).
3. Stillsand roof cover at 60 deg: exposure 1.00 under a verified roof (mod-or-ShadeGrid-cache, unresolved).
4. TitanicCreatures (from batch 1, still standing): RM_CrushRuleDef/RM_TitanicTierDef need the namespaced type in XML.
5. Warcasket About.xml dependency lacks downloadUrl/steamWorkshopUrl (cosmetic).
None found in LuminousPigment, Greentide, CreatureBehaviors, PyrelandsMechanics, Ishko.
