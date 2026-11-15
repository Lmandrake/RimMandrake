# RIMMANDRAKE_FINISH_GRAFFITI_AGAINST_TREE_BUILT_BEFORE_IT

## spec

Graffiti (mandrake.rm.graffiti) was built and far along before the Designer argued it (2026-11-14). Its concept tree is now
locked: coverage judge rm-coverage-judge-1794753924 signed it 2026-11-15 (third round: 24 gaps, then 2, then 0). This item
carries that tree to the pipeline: make every leaf of the tree provable by the mod's own script, and close what the tree
says is missing. Spec of record: `design/concepts/Graffiti/sheet.md`, `scenes.json` (four showcases: spree_corridor,
social_wall, after_the_raid, devout_wall), `floor.json`.

Build items filed before this one, which it waits on:
- RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE (the mod's script claims none of 12 validated must-show lines)
- RIMMANDRAKE_SCRIPT_GRAFFITI_CORRIDOR_WALK_AND_WALL_LOSS_SCENES and RIMMANDRAKE_SCRIPT_GRAFFITI_GAP_SCENES_TWENTY_FOUR_IN_ONE
  (scene entry points)
- RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL (inv_raider_future_marks, impl absent)
- RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL (far-side paint refusal not applied live)
- RIMMANDRAKE_CHECK_GRAFFITI_SITE_SETTINGS_SIX_OF_EIGHT (preflight checks 6 of 8 settings)
- GRAFFITI_VANDAL_REDRAW_TWO_SIGNS_GONE_LEGIT (whether shipped vandal_0/vandal_1 still carry Earth signage)

## verify

design/concepts/Graffiti/tree.json

Accepted tree hash a6eedf8713c0085ee36ebea1c3ce9eddc2b79a853b25c384d86e80f9f873340d (`concept_tree.py hash`), sheet hash
40637a736329d2a2e385acf2ec6e4f6bfa83501154fad2e50418e94d11de223c. `python3 src/RimMandrake/rimflow/concept_tree.py gate
design/concepts/Graffiti` must pass.

## criteria

A1: `concept_tree.py gate design/concepts/Graffiti` passes on the hash above (a changed tree needs a new signature).
A2: every leaf of the tree has a scene or proof row in `src/RimMandrake/Graffiti/validation.py` that `modcheck` accepts, and
a full live run records each as PASS (or an UNMEASURED row named in an item).
A3: the build items listed under spec are closed.

Acceptance test: none, live-app behaviour (A2 is a bridge run on the mod's own script).
