# Pyrelands 0.1.0: in-game acceptance, visit 8 (Archmagi, ArchBig)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_EIGHT. Started 2026-11-23 18:55 PST.

## Progress

- 18:57 skeleton written; item claimed; ArchBig bridge taken (free, at the main menu on a 15-mod list).
- 19:20 ArchBig: Huge Things and MandrakePatches deployed (drift), companion rebuilt and deployed, tier pyrelands (18 mods), launched pid 43680. Gate A every row PASS but loadavg 13.7 (other agents).
- 19:24 site NS_Pyrelands_site_1_417df172fdb5_visit8 (tile 178, 52.8 C), gate B CLEAN. P_furnace_room PASS (beast room 81.8 C, control 56.0, 0 open roof cells). burn_line running.
- 19:40 sc_walk part walk_master_bed_fire_resumes (UNMEASURED by design in visit 5: it waited for a chance sleeper) rewritten to stage its own sleeper, master off then on; planted switches PYRE_PLANT_BED_MASTER=left_off|left_on; selftest_pyrelands_walk_bed_resume 0/18 on the parent, 18/18.
- 19:38 burn_line run 1: burn_line_present and the 24-hour watch PASS; burn_line_burned_share spoiled on day 4 (a wild barbslinger downed a wild fire wasp; safe_advance stopped). Shield added (05d3da7407). wind_burn_live 9/9 PASS. 19:42 two runners overlapped for a minute (my queue error), both killed; burn_line rerun from a reloaded site.
- 20:16 the game hung since 19:41 (two runners loading at once; my error, 30 min lost); ArchBig stopped and relaunched on the tier; the runner now stops on a failed reload.
- 20:37 burn_line2 (reloaded site, shield): 4/4 PASS.
- 20:42 bed-fire part on the tier: real PASS (off 11250 ticks no fire, on lit), planted left_on FAIL, planted left_off FAIL. 20:48 walk_gate_off_then_on on the tier: real FAIL, 236 fires after a gate-off day; planted GATE_IGNORED read PASS (its plant cannot fire on a map whose burn is quiet). 20:55 first-fire probe: 500 ticks after "Mod enabled" off a fire-hawk already carrying dropped its ember and lit grass: MOD. Fixed in the sitting (JobDriver_RUT_FireHawkCarryEmber fails every toil once the gate or its switch is off; settings sweep fact job_ends_off red on the parent, 3 mutants red).
- 21:04 fire-hawk fix live: before (parent DLL) a fire at 500 ticks after "Mod enabled" off; after (4a9d62cae0) no fire in 60,000 ticks (evidence/script_gate_off_source.log, script_gate_off_source_fixed.log). Deployed to ArchBig. The relation names 7 more checks touched by the walk edits (their settings name matches); queued on the tier, then his full list and sc_walk.
- 21:22 tier5 reruns: burrowers, scorchfruit (plant_census), fire_tick_effects, furnace_warmth, letter PASS. firehawk far_hawk_seeks_the_burn FAIL: SITE (the thirsty hawk took RM_DrinkFromTerrain, flew from 104 to 44 cells to water inside the ember reach, so the carry took over; repaired: it starts watered and fed). fresh_burn_bonus spoiled (a barbslinger downed a fire-hawk on day 1; shield applied to the two long ground chains). Reruns queued with the NO_SEEK plant.
- 21:50 tier rehearsal of the walk's later parts on the hawk-fixed build: gate, roster, roof, thirst, bed fire PASS; walk_master_off_then_on FAIL "back on, no front walked over the day": HARNESS (the standing burn relights after two quiet days, the on spell was one; its net-ash rule read decay). Repaired: both spells run the relight window, hour-by-hour ash; gate and roster off spells run it too, with planted switches for each. rerun_relation read defName strings as row ids (RIMMANDRAKE_RELATE_CHECKS_BY_ROW_ID_NOT_CREATURE_NAME): fixed.
- 22:49 regrow2 5/5 PASS, fresh_burn_bonus2 2/2 PASS, firehawk2 3/3 PASS (NO_SEEK plant FAIL). tier9 (planted walk parts, burn_line3) running.
- 23:10 walk_master_off_then_on on the tier: real PASS; planted left_on FAIL, left_off FAIL. walk_gate_off_then_on planted (gate ignored) FAIL. Roster plant and burn_line3 running.
- 23:40 tier9: roster plant FAIL, animal_census PASS, burn_line3 4/4 PASS. 23:45 his full list (315 active, restore-full) on ArchBig, launching.
- 00:20 full list up (bridge after ~18 min under load; ArchBig pid 47988), full-list site NS_Pyrelands_site_1_417df172fdb5_visit8full (tile 193); gate B above; sc_walk started.
- 00:33 sc_walk run 1 on his full list: every part UNMEASURED: SITE. The full-list site (tile 193) holds no water cell at all (evidence/script_need_peek.log), so colonists died of Dubs Bad Hygiene dehydration and one of a bite. Site rebuilt with water required.
- 00:45 site NS_Pyrelands_site_1_417df172fdb5_visit8full2 (tile 23589, 58 shallow water cells), gate B above; sc_walk run 2 started.
- 01:10 sc_walk run 2 still in its first week.
- 01:47 sc_walk run 2: walk_reload_keeps_the_state PASS, walk_second_pass_and_switches PASS (two weeks, 3 colonists alive); walk_gate/roster/roof UNMEASURED: colonist Gutierrez went down twice from GR_FeatherdustAddiction and heart artery blockage he was generated with (SITE); later parts still running. Scene repair: the walk's colonists start with no generated ailment.
