# Pyrelands 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `237b79116781821545f7ac58c23ed40bfc0250c4` (origin/main, 2026-11-13).

## The locked files

| file | git blob at the lock | role |
|---|---|---|
| `design/concepts/Pyrelands/tree.json` | `3e69f701e1c346a36924a7611069962bbc665d1e` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/Pyrelands/sheet.md` | `a8ffd7ef042caea500e8164caa4b55ff27b9d731` | his plain-words sheet: does, does not, his words |
| `design/concepts/Pyrelands/scenes.json` | `ac9f25e61bd2d8025513f8a39520a21e452a7ac6` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/Pyrelands/floor.json` | `e2d58b07a62b036530ff175022a51ec732a55537` | the quality floor lines every mod meets |
| `design/concepts/Pyrelands/exam.json` | `6793f3c53ff73f8f9f13b7d131a1579f29343a94` | the Cold Reader exam of tree and sheet |
| `design/concepts/Pyrelands/record.json` | `9c82b9770af208b61d92a0fba53f504ba3a80714` | the inventory of built capabilities (checklist rows too); re-pinned 2026-11-14 for the bar his card added, `inv_firehawk_hunt_rewards` (journal, kind bar-added) |
| `design/concepts/Pyrelands/plan.md` | `b33e7b97b1396e4a92b45046b30df5518449d4b8` | the build and proof plan |
| `design/concepts/Pyrelands/stage.json` | `3db94065beaee5d3c634042a2655b2420fb92ae6` | the Designer's stage, budget and judge rounds (state, not a bar) |

**Re-pinned 2026-11-14 (Stage 3, the Conductor's steward decision: test-text corrections are re-pinned, a changed bar never is).**
`tree.json`, `scenes.json`, `sheet.md` and `record.json` now carry their post-correction blobs; their lock blobs were
`3c3e252e28`, `a30b299bc2`, `73d2aeb66c`, `19dddf23d7`. Measured field by field against the lock blobs: in `tree.json` only
leaf `oracle_proposed` and `scenario` moved (every `experience`, `red` and id identical); in `record.json` the
`inv_ash_field` evidence list, the `d_worldgen_outside_promise` text (g5) and the `inv_ullai_herd_giant` sentence about
the cut migration's text (g12: it said the description still promised migration, which was false) moved, no row added or
removed; `scenes.json` holds tests; `sheet.md` lost the false lines g5, g12 and g13 named.

**`plan.md` re-pinned 2026-11-14 (owner by card, about 2:10 PM PST: "Keep anywhere on the map").** Commit `82d9247595`
(2026-11-13 19:42, after the lock) changed the fire-hawk's ember reach from eighteen cells to anywhere on the map, carried
to the largest unburnt fuel it can see. He kept that as Pyrelands 0.1.0, so `plan.md`'s lock blob `0d8be55bbc` is replaced
by its current blob; no other locked file moved for it (no bar or check text said eighteen cells).

**Re-pinned 2026-11-14 (owner by card, about 2:20 PM PST: "Drop the sentence").** The root's sentence that ordinary
paving (a strip two cells wide) stops the ground fire is deleted, with every line that still promised it: `record.json`
(root text, `d_firebreak_cut`, `d_root_ending`, the `inv_firebreak_firefoam` note), `tree.json` (the walk leaf's "a paved
ring protects the colony"), `scenes.json` (`sc_walk`'s paved-ring start), `sheet.md` (the delegated firebreak line) and
`plan.md` (owed change 2, the `paved_strip` entry point). Blobs before: `e600b1386c` (tree), `57c653bbd4`
(scenes), `3486c02215` (sheet), `f478008aa8` (record), `dd3ec4b45d` (plan); the table carries the new ones. No leaf or
row was added or removed and no `experience` or `red` moved. `exam.json` is a run record and stays as it ran (its scenario
e9 still names the deleted leaf); the exam is rerun at stage 4 (VERSION.json caveat).

Tree hash (`concept_tree.py hash`): `3ffd15d1aa89521618cd9b2c595684e582a864c7ccf14793717e1e2314c87107`; sheet hash: `2935f04bef8d7f632c3fc00707120d06694c664cb67e90709c2a32614fba46a1`
(measured 2026-11-14 after this re-pin; before it they measured `def968a06e` and `85f40d772f`, not the `6dd32c14a9` and `4f77fad249` this line had said).

## Counts at the lock

- Bars (the coverage checklist): **42** = 21 inventory rows + 21 tree leaves (41 at the lock; `inv_firehawk_hunt_rewards` added by his card 2026-11-14).
- Floor lines: 23 (23 applicable).
- Exam: 22 of 22 scenarios right (against an earlier tree and sheet; see VERSION.json caveats).
- Waived lines: 0.

## The leaves (ids only; the text is in tree.json)

- `burn_line_walks` (experience)
- `ash_ground_and_blowing_ash` (experience)
- `ash_fertile_when_watered` (experience)
- `fresh_burn_compounds_with_black_rain` (experience)
- `grass_carpets_and_regreens` (experience)
- `scorchfruit_born_of_fire` (experience)
- `populations_are_the_biomes_own` (experience)
- `ruins_stand_blackened` (experience)
- `firehawk_lights_ahead` (experience)
- `furnacebeast_warms` (experience)
- `ashwallow_dives_unharmed` (experience)
- `ullai_graze_old_burns` (experience)
- `three_skies` (experience)
- `no_ordinary_rain` (experience)
- `ash_fertility_probe` (instrument)
- `walk_season_on_the_pyre` (walk)
- `firefoam_sprayer_reaches_the_fruit` (experience)
- `sand_shovel_yields_glass_sand` (experience)
- `fire_rite_hook_silent_alone` (experience)
- `biome_text_says_engineered` (experience)
- `flamefang_bite_carries_venom` (experience)

## The inventory rows (ids only; the text is in record.json)

- `inv_biome_self_contained`
- `inv_plant_roster`
- `inv_embergrass_regrow`
- `inv_animal_roster`
- `inv_ash_field`
- `inv_burn_line_fire_clock`
- `inv_scorchfruit`
- `inv_ruins_scorched`
- `inv_firehawk_ember`
- `inv_furnacebeast`
- `inv_burrowers_heat_dome`
- `inv_ullai_herd_giant`
- `inv_weather`
- `inv_firebreak_firefoam`
- `inv_firefoam_sprayer`
- `inv_sand_shovel`
- `inv_lightning_breaker`
- `inv_fire_rite_hook`
- `inv_settings_gate`
- `inv_art_and_text`
- `inv_firehawk_hunt_rewards` (added 2026-11-14, his card)
