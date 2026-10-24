## spec
found-by: BENCH bridge run 1, driver 6 (§4 looks map, 2026-10-23). Class: HARNESS (all three), in
`src/RimMandrake/FlowWorks/northstar/owner_review_stage.py`.

1. **bars_* rows off the map on a 250 map.** The bars site sits at origin+150 (x 250-312); on a 250x250 quicktest
   (RM_TheRot, `--any-biome`) every bars_* row is placed off-map and nothing checks the map size first.
   Evidence: `Transient/bridge_run_1_20261023/captures/br1f/ors_rot.log`, `ors_rot_sum.txt`. `--origin 30,100` would fit.
   Done when: the stage reads map size and either fits the layout or refuses with a reason before staging anything.
2. **The held-open gates read shut.** On the TemperateForest 325 map (`ors_van.log`), the held-open RM_Sluice (130,119)
   and RM_SecurityGrateDoor (130,128) read `open=False` (`captures/br1f/gate_probe.json`) after the stage's
   `water_scenes_walk.gate_open`. By hand on the same map, Hold open + a colonist teleported 2 S and ordered in opens the sluice
   (`open=True seals=False`), and it stays open after the colonist walks away (`captures/br1f/gate_diag4.json`). So the mod
   is fine and the stage's walk is what fails. The label truncates gate_open's report to 60 chars, which hides its
   `[button pressed|NOT PRESSED]` / `[walked|NO COLONIST]` detail. Done when: the stage reads the door state after
   gate_open and prints the full report, and the held gate reads open=True in the stage's own log.
3. **The bars_trench shooter is unarmed** (`ors_van.log`: "shooter has no ranged verb"). Done when: the shooter is given
   a ranged weapon or the row says it cannot be.
