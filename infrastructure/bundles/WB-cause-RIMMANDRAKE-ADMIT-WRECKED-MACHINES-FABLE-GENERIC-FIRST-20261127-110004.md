# WB-cause-RIMMANDRAKE-ADMIT-WRECKED-MACHINES-FABLE-GENERIC-FIRST-20261127-110004

State: complete (2026-11-27 4:55 AM PST); the member closed at 7a5dcdbc883f.

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
- e3dc3bb854: the 4 rows added at stage 5 and the 5 rows it changed; designations by rect (jawa/designate_batch takes a
  rect, not an id). `selftest_wm_scenes.py`: red on the parent (23 unregistered), 7 plants red, PASS on 27 scenes.
- sc_text_names_no_setting runs offline today and is red on 11 true hits in the mod's own texts ("ship", "Repaired"):
  the build's work under bar no_setting_named, not this item's.

## Live

- ArchBig and ArchSmall were held all run by BENCH pid 1505240 (Pyrelands 0.2.0 live checks), so the live proof ran on the
  SteveDesktop lane as live proof A1 (`infrastructure/state/live_proofs/RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL.txt`).
- J20261127T120855Z-8d675c: INVALID LOAD, VFE Factory was not installed on SteveDesktop (environment); copied to both Steve
  games with `sync_test_mods.py --only VanillaExpanded.VFEFactory`.
- J20261127T122224Z-2e3f85: 18 PASS, 3 FAIL. reach_edge with a digging mode read "cannot get out" from inside walls: the
  engine walks regions and a wall has none, so the mode is now refused (the tool's text was wrong). The fill rows found no
  process to pick (a fresh processor has no bill): processor_fill now reports available[], and the scenes read a level's
  offer from it.
- J20261127T123954Z-cc3eed (7a5dcdbc88): 22 PASS, 0 FAIL, companion FRESH. Not exercised live: caravan_form_load's forming
  path (only its refusal); the sc_caravan_wreck_home scene exercises it at the visit.
- The scenes' behaviour is read at the mod's first in-game visit (the item's verify), scene by scene.
- Fresh reader filed: RIMMANDRAKE_READ_FIX_E3DC3BB854_WITH_FRESH_EYES.

## Not recordable now

- `maturation.py red-seen` refuses: the mod has no `version/test_table.json` yet (a later stage builds it). The red runs
  are in the commit messages above.
