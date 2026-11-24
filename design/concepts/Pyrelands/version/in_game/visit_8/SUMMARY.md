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
