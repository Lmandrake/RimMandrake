# Harness cleanups 2026-10-12 (BENCH subagent, offline)

Evidence: Transient/bench_live_20261012b/SITTING.md. All four fixes are harness-only; north star bars untouched.

1. plant_distribution_correct: probe now plants the first allowlisted roster plant from live wildPlants (`probe_plant`),
   not Plant_Grass; failure text quotes the set_plants reply. Prove: `northstar_driver run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains plant_census`.
2. Driver keeps full text: rows carry `evidenceFull` beside the 300-char `evidence` (bars.rollup_components, cli.functional_rows).
   ground_ash_ladder records every ignition attempt (`_GEN["ignitions"]`, noted per cycle) and a refusal quotes all of them.
   Prove: `... --chains ground_ash_ladder`, read `evidenceFull` in the out JSON.
3. embergrass_regrow: after the burn, counts ORIGINAL plants still standing; if >50% survive (`burn_cleared`, a harness
   precondition, not a calibration bar) the row is UNMEASURED with that number. Calibration thresholds untouched.
   Prove: `... --chains embergrass_regrow` (16 min).
4. river_site.py: orders river tiles by biome fish (live BiomeDef maxFishPopulation/fishTypes via get_defs, XML fallback),
   drops known-fishless biomes and prints them. Offline XML already reads RM_TheRot = fishless.
   Prove: `python.exe src/RimMandrake/FlowWorks/northstar/river_site.py` then `extension_proof --live --site river`.

Selftests: Pyrelands/selftest_pyrelands_site.py, Utils/northstar_driver/selftest_record_status.py, FlowWorks/northstar/selftest_river_site.py.
run_selftests: 346/414 pass, only known red selftest_art_checks.py.
