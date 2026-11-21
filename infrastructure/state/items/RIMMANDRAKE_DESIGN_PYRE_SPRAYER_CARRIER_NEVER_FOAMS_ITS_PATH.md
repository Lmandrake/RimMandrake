## spec
Pyrelands 0.1.0, MOD fault from in-game visit 3 (game b, 2026-11-21). Bar `firefoam_sprayer_reaches_the_fruit`: the
colonist who carries the firefoam sprayer into a live burn for scorch-fruit foams a way through, takes the fruit and
comes back unburned. Measured: in 3 of 3 sprayer runs on build 6ea9314ad1 the carrier laid 0 `Filth_FireFoam`; its jobs
were Harvest, `RM_PyreStepAwayFromFire` and GoSwimming. `RM_FE_FirefoamSprayer` is a `Verb_Shoot` gun, and no mod code
makes a carrier use it on fire in its way (only `RM_FirefoamAimProof` aims it). The earlier PASSes were chance.
The fix is not known: when a carrier foams (on its own on a job's path, or player-ordered) is undesigned. The Designer
rules first, within the bar's words; then the build. Also SITE (same owner): the control's 2-cell grass ring did not stop
a bare colonist (s3 crossed it unburned), so the control needs a ring a bare colonist cannot cross unburned.
Evidence: `design/concepts/Pyrelands/version/in_game/visit_3/SUMMARY.md`, `design/concepts/Pyrelands/version/in_game/visit_3/evidence/run_firefoam_sprayer_s3.log`.

## verify
Stage 6 (game-up: the fault is a pawn's job choice in the engine, which no fake map models). In-game check
`sc_firefoam_sprayer`: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains firefoam_sprayer` on a free game, tier pyrelands, site reloaded.

## criteria
- `sprayer_reaches_the_fruit` PASS: `Filth_FireFoam` > 0 in the 9x9 burn, fruit taken, no burn injury.
- `without_sprayer_fire_stops_or_burns` PASS, and FAIL with `PYRE_PLANT_RING_GAP=1` (the ring left open).

## Acceptance test
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains firefoam_sprayer`: both components PASS; red now (`design/concepts/Pyrelands/version/in_game/visit_3/evidence/run_firefoam_sprayer_s3.log`).
