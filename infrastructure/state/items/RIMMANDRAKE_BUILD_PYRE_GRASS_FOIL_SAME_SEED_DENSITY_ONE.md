## spec
`sc_grass_regreens` / `plant_density_one_control_map` (src/RimMandrake/Pyrelands/validation.py) reads UNMEASURED by
construction: "no bridge tool regenerates the site's seed and tile with plantDensity set to 1.0 before generation". The bar
`grass_carpets_and_regreens` needs it: its oracle says the cover census is "thicker than the same seed at plantDensity 1.0".
Build the read: a bridge tool (or a public probe) that generates a second map on the site's tile and seed with
RM_Pyrelands' plantDensity held at 1.0 through generation, read by the same cover census, then dropped. Found while
fixing RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN (its acceptance test lists this part as owned by this item).

## Acceptance test
`python3 src/RimMandrake/Pyrelands/selftest_pyrelands_scene_controls.py --strict` - fails now (1 of 40 checks failed:
the construction check names plant_density_one_control_map; seen 2026-11-21). Green: 0 of 40 checks failed, and the
KNOWN_OPEN entry in that file is deleted. The live half is the scene's live_command (Stage 6).

## verify
On a visit, `sc_grass_regreens` / `plant_density_one_control_map` reads PASS or FAIL, never UNMEASURED for a missing tool.

## criteria
- The same-seed map at plantDensity 1.0 is generated, read by the grass census, and dropped; the site is untouched.
- No row of the Pyrelands scenes is UNMEASURED by construction (`--strict` above).

## refs
file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/selftest_pyrelands_scene_controls.py
file: design/concepts/Pyrelands/scenes.json
