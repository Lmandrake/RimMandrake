# Graffiti 0.1.0: the bars, locked as they stood on 2026-11-15

Owner, by question card Sun 2026-11-15 11:33 AM PST: "Lock as 0.1.0 now" (the option he picked). Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked.

Lock commit: `9c13eeab55600faa1716147d216e85060e34a9b0` (origin/main when the version was entered, after his card answer). The Graffiti concept folder is unchanged from it.

## The locked files

| file | git blob at the lock commit | role |
|---|---|---|
| `design/concepts/Graffiti/tree.json` | `c998ae8d68789695a67155e1e67085a4ac1ecc59` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/Graffiti/sheet.md` | `701164233b3e77ba5a155d84edc6e8e24109ffda` | his plain-words sheet: does, does not, his words |
| `design/concepts/Graffiti/scenes.json` | `31ef2c4933f100020258f33200c2828fd512770c` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/Graffiti/floor.json` | `feb11a00b4875596c90cf3b4b57b111ffd9759db` | the quality floor lines every mod meets |
| `design/concepts/Graffiti/exam.json` | `a5b671a4fac30e79e317af7af408cb59d580782a` | the Cold Reader exam of tree and sheet (82/82) |
| `design/concepts/Graffiti/record.json` | `888c874efb9dc9d99937bcf4f39fb129f7b68653` | the inventory of built capabilities (checklist rows too) and the root he approved |
| `design/concepts/Graffiti/plan.md` | `49a46ae0c9ab475e160d1e072bdb9492d38107a5` | the build and proof plan |
| `design/concepts/Graffiti/stage.json` | `49b3ee9060f92f1ff33f75d7a3d7ca0c813c8e83` | the Designer's stage, budget and judge rounds (state, not a bar): locked, stage 5 |
| `design/concepts/Graffiti/coverage_verdict.json` | `e4127cab13a72f5a3affe3a673be96ff353feac2` | the coverage verdict rm-coverage-judge-1794753924, covered |

Tree hash (`concept_tree.py hash`): `a6eedf8713c0085ee36ebea1c3ce9eddc2b79a853b25c384d86e80f9f873340d`, the hash the coverage judge signed (tree.json coverage, 2026-11-15T14:47:37Z).

## Counts at the lock

- Bars (the coverage checklist, `coverage_judge.required_ids()`): **47** = 19 inventory rows + 28 tree leaves, none in both. The ids the later stages are held to are in `locked_bars.json` (`maturation.py lock-bars`).
- Met: 47 of 47 checklist rows ok in verdict `rm-coverage-judge-1794753924` (covered, 0 gaps).
- Floor lines: 23 (21 applicable; not applicable: motion, biome_scope).
- Exam: 82 of 82 frozen scenarios matched by both Readers (`exam.json` result).
- Waived lines: 0.
- Open defect kept in 0.1.0 (his card named it): `RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL` (sits_on_wall's far-side clause; `inv_mark_on_wall`).

## The leaves (ids only; the text is in tree.json)

- `mark_appears`
- `reads_at_play_zoom`
- `sits_on_wall`
- `marks_various`
- `ideo_sigil`
- `punk_register`
- `no_english`
- `not_dirt`
- `ugliness_visible`
- `art_skill`
- `own_fun`
- `rereads_daily`
- `mockery`
- `tribute_memorial`
- `answer_wall`
- `scrub_protection`
- `player_orders`
- `raid_mark_troubles`
- `going_over`
- `raider_pressure`
- `visitors`
- `fights_reasons`
- `temperament`
- `stands_alone_settings`
- `stories_not_tax`
- `paint_dies_with_wall`
- `weathering_bounds_marks`
- `walk_lived_in`

## The inventory rows (ids only; the text is in record.json)

- `inv_mark_on_wall`
- `inv_mark_art_set`
- `inv_beauty_and_craft`
- `inv_ideo_sigils`
- `inv_spree`
- `inv_joy_and_idle_tag`
- `inv_player_orders`
- `inv_viewer_mood`
- `inv_social_layer`
- `inv_visitors`
- `inv_raid_marks`
- `inv_breach_bias`
- `inv_scrub_protection`
- `inv_temperament`
- `inv_wall_loss`
- `inv_settings`
- `inv_standalone`
- `inv_raider_future_marks`
- `inv_weathering`
