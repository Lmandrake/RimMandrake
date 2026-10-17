# Credited rerun 2026-10-17 (BENCH)

## Git
HEAD == origin/main == 8cdc885d99 at start (no fetch needed). FlowWorks DLL sha256 05fabdc5.
## Close + modlist
Game closed (Stop-Process), log -> credited/Player.before.log. ModsConfig held 548; walk_modlist.py --apply -> 20 active (backup PRE_WALK_20261017T153348.xml).
## Deploy
deploy_custom_mods --mod FlowWorks --apply: DLL + srchash + Pit_Hediffs.xml, VERIFIED; game DLL sha == repo 05fabdc5.
## Launch/load
22:34Z Steam -applaunch ignored (no process after 4 min; Steam up since 10-13); second -applaunch started it at once. Bridge ~2 min. load calm CLEAN. Load log 2877 lines, provider Own; 275 Exception lines are the calm save's plants (SaveableFromNode NRE x55 etc.), none naming thirst.
## thirst_live full
`credited/thirst_full.txt` -> northstar/thirst_live_result_20261017T153651.json (mod_hash 8b8aa4a2, assembly 05fabdc5): 24 PASS, T1 UNMEASURED HARNESS (one list of three), T18 UNMEASURED SITE (no Dubs). T25 PASS (melt 5,000). Then --only T15R: PASS (`credited/thirst_t15r.txt`). Took ~17 min; governor stops (Wander_Sad, a Berserk) handled by the driver.
## sprinkler_live full
Try 1 on the post-thirst map died on clockgate.GovernorStop (TargetedInsultingSpree from the thirst run's leftover pawns; `credited/sprinkler_full_try1_governorstop.txt`) - HARNESS/SITE. Reloaded calm; try 2 (`credited/sprinkler_full.txt`): all 9 rows PASS.
## validation.py
driver_rows_at(mod_hash 8b8aa4a2, dll 05fabdc5): THIRST_LIVE 26 PASS (credited), 2 UNMEASURED (T1, T18: list-limited); SPRINKLER_LIVE 7 PASS, 3 UNMEASURED with no driver (liquid_key, vfe_boost_skipped, vfe_valve: not driven by design).
## End state
FlowWorks moved on origin DURING the run: bf1e344d10 + 6fb91887a9 (DLL rebuilt, RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS), so after a pull these credits read UNMEASURED again at the new hash. Game RUNNING on the 20-mod walk list, RM_walk_20261017_creatures loaded (AridShrubland), paused. Bridge released.
