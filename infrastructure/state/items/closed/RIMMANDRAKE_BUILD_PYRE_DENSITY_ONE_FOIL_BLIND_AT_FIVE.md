## spec
Pyrelands 0.1.0, in-game visit 5 (ArchBig, tier pyrelands, 2026-11-22, build e63595716c). Check `sc_grass_regreens`
(bars `grass_carpets_and_regreens`, `inv_embergrass_regrow`). Class HARNESS, unrepaired: the part
`plant_density_one_control_map` (src/RimMandrake/Pyrelands/validation.py) reads UNMEASURED by construction, because no
bridge tool regenerates the site's seed and tile with plantDensity 1.0 before generation. Every other part of the check
PASSed live on visit 5 (embergrass_regrows, regrow_dry_watered_vanilla, grass_census_first, grass_chokes_ground:
design/concepts/Pyrelands/version/in_game/visit_5/SUMMARY.md). The bar's oracle says the cover census is "thicker than the
same seed at plantDensity 1.0", so the bar stays undecided until this part reads.

Build the read: a bridge tool (or a public probe) that generates a second map on the site's tile and seed with
RM_Pyrelands' plantDensity held at 1.0 through generation, reads it with the same cover census, then drops it. Skill:
`rimbridge-companion`.

This item supersedes RIMMANDRAKE_BUILD_PYRE_GRASS_FOIL_SAME_SEED_DENSITY_ONE (filed 2026-11-21 under
RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN). The visit-5 row named that item only as `owner`, so the
visit-5 road back did not cite it; this filing puts the work on that road back.

## launch-checks
must-fail: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_scene_controls.py --strict

## verify
Offline: the launch check above reads 0 of 40 checks failed, and its KNOWN_OPEN entry for plant_density_one_control_map
is deleted. Live, Stage 6, tier pyrelands, on a reloaded site:
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains grass_cover,embergrass_regrow` (the test table's sc_grass_regreens command)
gives `plant_density_one_control_map` PASS or FAIL, never UNMEASURED for a missing tool. If the fixer closes on the
offline test, it records the live check UNRUN with `maturation.py unrun`.

## criteria
- The same-seed map at plantDensity 1.0 is generated, read by the grass census, and dropped. The site is untouched.
- No row of the Pyrelands scenes is UNMEASURED by construction (`--strict` above).
- The repaired part is seen to FAIL on a planted state (a control census that is thicker than the site's) and PASS on
  the real build, in one sitting.

## Acceptance test
`python3 src/RimMandrake/Pyrelands/selftest_pyrelands_scene_controls.py --strict`: red now, watched 2026-11-22 by the
visit-5 steward run (exit 1, "1 of 40 checks failed"). Green: exit 0, 0 of 40 failed.

## refs
file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/selftest_pyrelands_scene_controls.py
file: design/concepts/Pyrelands/scenes.json
