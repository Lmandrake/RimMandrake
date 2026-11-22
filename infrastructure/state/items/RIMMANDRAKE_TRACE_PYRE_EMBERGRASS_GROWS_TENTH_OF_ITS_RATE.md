## spec
Pyrelands 0.1.0, class MOD (presumed, unproven), from in-game visit 4 (game a, 2026-11-22). Check `sc_grass_regreens`
(bars `grass_carpets_and_regreens`, `inv_embergrass_regrow`). With the regrow reader repaired (it now reads '70% grown'),
the first numbers ever read: ember grass sown at 0.05 on the regrow scene's ground grew +0.054 a day (0.05, 0.10, 0.16,
0.21, 0.26, 0.32), dry and watered alike, while vanilla Plant_Grass sown beside it grew +0.118 a day. EmberGrass.xml says
growDays 0.8 (Plant_Grass 2.5), so at the vanilla formula it should outgrow the grass several times over (the row wants
>= 0.369 a day); its own description says it "regrows on burned ground in a day or two"; at +0.054 it takes about 18 days.
`embergrass_regrows` also FAILed (green share 0.23 on day 3, 0.42 on day 7; visit 3 on game b read 0.38 and 0.73, PASS).
Not yet traced: which factor holds ember grass to about a tenth of its rate (fertility, the temperature curve at the
biome's 56 C, a mod mechanic, or the reading of growDays). That run laid RM_FE_Ground_Soil (a SITE fault, repaired in
4fff1aa5e7: the scene now lays deep ash, as scenes.json asks); the deep-ash rerun was not run (the visit's bound).
Evidence: design/concepts/Pyrelands/version/in_game/visit_4/evidence/run_embergrass_regrow.log (daily growth note), design/concepts/Pyrelands/version/in_game/visit_4/evidence/script_inspect_probe.log.

## verify
Stage 6 (game-up). `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains grass_cover,embergrass_regrow` on a reloaded tier-pyrelands site: read the daily series on deep
ash first; if ember grass still grows near +0.05 a day, trace the factor live (Plant.GrowthRate's parts at noon on an
ember-grass cell beside a Plant_Grass cell), then fix the mod (or the check, if its vanilla-rate formula is wrong).

## criteria
- regrow_dry_watered_vanilla and embergrass_regrows PASS on the build, with the scene on deep ash.
- The cause is named (MOD or HARNESS), and the fix is tested red on the parent.

## Acceptance test
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains grass_cover,embergrass_regrow`: components regrow_dry_watered_vanilla and embergrass_regrows PASS. Red now
(visit 4: both FAIL, design/concepts/Pyrelands/version/in_game/visit_4/evidence/pv4_embergrass_regrow.json).

## refs
file: src/RimMandrake/Pyrelands/Defs/ThingDefs_Plants/EmberGrass.xml
file: src/RimMandrake/Pyrelands/validation.py
