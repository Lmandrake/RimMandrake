# Pyrelands 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `237b79116781821545f7ac58c23ed40bfc0250c4` (origin/main, 2026-11-13).

## The locked files

| file | git blob at the lock | role |
|---|---|---|
| `design/concepts/Pyrelands/tree.json` | `8f04b41d9901f292b149f56032510343e1b1907d` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/Pyrelands/sheet.md` | `067f4a63982ed9c1cd5afc3974120332c48b5db1` | his plain-words sheet: does, does not, his words |
| `design/concepts/Pyrelands/scenes.json` | `4385a72f6fe51547673cb09a2ab836cc0a02cf1d` | the acceptance scenes and showcases the leaves are proven by |
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

**Re-pinned 2026-11-16 (owner, about 9:22 PM PST, his words: "And modify the bar so that it's not so finicky about "the line."
Sometimes poetry is simply that. I just wanted a natural grassfire feel.").** Leaf `burn_line_walks` keeps its id; its
`experience` now reads "grass fire moving across the deep ash like a natural grass fire, with a black scorched trail behind it
that regreens ... never out for long", and what it must not read as is a flood that takes the whole map and its grass, a fire
that does not move, a fire that burns once and is gone, or a fire that lights inside the colony. Its `oracle_proposed` and
`scenes.json` `sc_burn_line_walks` no longer ask for a contiguous front (burning ground whose centre moves, a growing scorched
area). By his second sentence the same evening (about 9:26 PM PST: "Take out the "far from buildings" we don't have
any physics to substantiate that claim.") the relight is "in open grass", with no distance from buildings in the leaf, its
scenario, its oracle or the scene. `sheet.md` carries the new sentence and his words; the root paragraph and `vision.md` keep "a line of grass fire"
as he wrote it (poetry, by his word). Same change: `scenes.json` `settings_map` gains `windCarriesFireEnabled` (the new Mod
Setting of RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE). No leaf or row added or removed. Blobs before
(origin/main 42483a7578): `91eaf9e048` (tree), `45bf69e360` (sheet), `a31005845b` (scenes); the table carries the new ones
(it had still shown the 2026-11-14 blobs for these three, which were no longer true).

Tree hash (`concept_tree.py hash`): `5abc9d2718dc9ccfd08d29370d986260c19675a198dc310be5329d34f062cf31` (measured 2026-11-16 after
this re-pin; before it, at origin/main 42483a7578, it measured `2c1e467c7e`, not the `3ffd15d1aa` this line had said).

## Counts at the lock

- Bars: **43** = 21 inventory rows + 22 tree leaves (41 at the lock; `inv_firehawk_hunt_rewards` added by his card 2026-11-14; leaf `ullai_cross_the_map_as_vanilla_herds` added by the locked change 91a7c61989, his card OWNER:1794748469904049550). The record is `version/locked_bars.json`.
- Not a bar: leaf `firehawk_hunt_rewards` (same change) states `inv_firehawk_hunt_rewards`' promise, so it is that bar's coverage; `make_test_table.py` maps it there. The coverage judge's checklist still owes it a row (44 rows).
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
- `ullai_cross_the_map_as_vanilla_herds` (experience; added 2026-11-15 by the locked change 91a7c61989, his card)
- `firehawk_hunt_rewards` (experience; coverage of `inv_firehawk_hunt_rewards`, not a bar)

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
