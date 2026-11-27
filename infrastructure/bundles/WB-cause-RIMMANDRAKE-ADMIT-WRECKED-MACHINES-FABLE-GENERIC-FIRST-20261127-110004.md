# WB-cause-RIMMANDRAKE-ADMIT-WRECKED-MACHINES-FABLE-GENERIC-FIRST-20261127-110004

One member: RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL (Wrecked Machines 0.1.0, the scene entry points and
the generic bridge functions they name). Class: REAL (acceptance red on 4f6c3feade, `missing 23`).

## Group 1: the bridge functions (done)

- 16d9d38315: jawa/thing_set_sample, install_blueprint, study_record, processor_fill. Rules in the Verse-free
  `JawaBenchWreckReadsCore.cs`; `selftest_wreck_reads.py` red with no game half (4 wirings), every plant red, PASS after.
  `jawa/container_fill` cannot reach PipeSystem's processor: its inputs are counts on ThingAndResourceOwner (read from
  PipeSystem.dll metadata), so processor_fill is owed and built.
- 626876a561: jawa/caravan_mass, caravan_form_load, reach_edge, for the rows the Designer's stage 5 added (89b10e6f1a).
  Red on the committed tools file (3 undeclared); PASS 20 units, 20 plants, 7 wirings.

## Group 2: the scenes (done offline)

- d8f8bd53b3: the 23 scenes of the stage-3 scenes.json, in validation.py, through one proof-type contract
  (RimMandrake.WreckedMachines.RM_WreckedMachinesProof, written above the scenes). The 3 spawn-and-inspect chains and the
  4 UNMEASURED play-time rows are gone; the 10 settings rows and alloy_forge_gated stay.
- Next commit: the 4 rows added at stage 5 and the 5 rows it changed; designations by rect (jawa/designate_batch takes a
  rect, not an id). `selftest_wm_scenes.py`: red on the parent (23 unregistered), 7 plants red, PASS on 27 scenes.
- sc_text_names_no_setting runs offline today and is red on 11 true hits in the mod's own texts ("ship", "Repaired"):
  the build's work under bar no_setting_named, not this item's.

## Live

- prove_wreck_reads.py reads the 7 tools against the game. ArchBig and ArchSmall were held all run by BENCH pid 1505240
  (Pyrelands 0.2.0 live checks). Asked of the SteveDesktop lane as live proof A1
  (`infrastructure/state/live_proofs/RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL.txt`).
- The scenes' behaviour is read at the mod's first in-game visit (the item's verify), scene by scene.

## Not recordable now

- `maturation.py red-seen` refuses: the mod has no `version/test_table.json` yet (a later stage builds it). The red runs
  are in the commit messages above.
