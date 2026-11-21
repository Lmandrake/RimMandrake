## spec
Pyrelands 0.1.0, HARNESS, unrepaired in in-game visit 3 (game b, 2026-11-21). Check `sc_grass_regreens` (bars
`grass_carpets_and_regreens`, `inv_embergrass_regrow`, both undecided without it). `regrow_dry_watered_vanilla`
(`_ten_embergrass_regrow_growth`, jawa/inspect_string "Growth: N%" over each 4x4 patch) read None for dry, watered and
vanilla on all 6 days; cause not found (the run log truncates the component's evidence). Also owed on the same check:
`grass_census_first` needs grass_cover in the same driver run; `plant_density_one_control_map` has no bridge tool.
`embergrass_regrows` PASS. Evidence: `design/concepts/Pyrelands/version/in_game/visit_3/evidence/run_embergrass_regrow.log`.

## verify
Stage 6 (game-up: the cause is unknown until a live read). In-game check `sc_grass_regreens`:
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains grass_cover,embergrass_regrow`, tier pyrelands, site reloaded.

## criteria
- `regrow_dry_watered_vanilla` reads a number for every patch and day (PASS or FAIL, not UNMEASURED).
- `grass_census_first` is not UNMEASURED.
- A repaired read is seen FAIL on a state known bad and PASS on the real build.

## Acceptance test
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains grass_cover,embergrass_regrow`: the two rows above read a verdict; red now (UNMEASURED).
