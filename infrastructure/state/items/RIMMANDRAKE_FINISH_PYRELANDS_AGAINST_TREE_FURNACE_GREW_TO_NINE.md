# RIMMANDRAKE_FINISH_PYRELANDS_AGAINST_TREE_FURNACE_GREW_TO_NINE

## spec

Pyrelands (mandrake.rm.pyrelands) was built and far along before the Designer argued it (2026-11-05). Its concept tree is
now locked at Design Version 0.1.0: coverage judge rm-coverage-judge-1794790345 signed it 2026-11-16 00:54Z, after the
furnace-beast's body was raised to 9 (his card 2026-11-15, OWNER:1794786804170379047) closed the last gap. This item carries
that tree to the pipeline: make every leaf of the tree provable by the mod's own script, and close what the tree says is
missing. Spec of record: `design/concepts/Pyrelands/sheet.md`, `scenes.json` (four showcases: burn_line, fire_cast,
sky_and_shelter, fire_solace; 29 scenes), `floor.json`.

Build items filed before this one, which it waits on (every scene's missing entry point, control or restoration step):
- RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED (incl. the new chains fire_sense, foreign_arrivals)
- RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN (incl. the new chains roof_withers, herd_thirst, furnace_hide_bank)
- scene items cited in `scenes.json` `entry_point_item`: PYRELANDS_SCENES_BUILD_EIGHT_JUDGE_GAPS,
  PYRELANDS_SCENES_BUILD_EVERY_FIRE_A_FOIL, PYRELANDS_SCENES_BUILD_VENOM_GIANT_DUST_DOME,
  PYRELANDS_SHOWCASES_BUILD_THREE_PYRE_FACES (filed on the ledger; no prose file under `items/`)
- PYRE_OPENING_FRONT_BUILD_SMOKE_ON_ARRIVAL (record contradiction c_opening_front_item_open: resolve by a run)

The live read sc_furnace_giant is UNRUN, its command recorded in `scenes.json`.

## verify

design/concepts/Pyrelands/tree.json

Accepted tree hash 78f3df67824adcf0582354112cf09be797e1d601c22baef269474afb8ced2f54 (`concept_tree.py hash`), sheet hash
628feeb2919d67f7f489233bc436af3131c59595a7373502d2e1669bff30fd4c. Signature: coverage judge rm-coverage-judge-1794947629
(covered, 0 gaps), certified past the root_hash restamp 47e044e556 by the Conductor's act (OWNER:1795222813980581690).
`python3 src/RimMandrake/rimflow/concept_tree.py gate design/concepts/Pyrelands` must pass.

## criteria

A1: `concept_tree.py gate design/concepts/Pyrelands` passes on the hash above (a changed tree needs a new signature).
