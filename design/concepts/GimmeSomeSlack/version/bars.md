# GimmeSomeSlack 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `bf33322d7754bb3a9e504924bc062dc7fb65fea3` (origin/main, 2026-11-13 15:40 PST, the commit recording his lock word). Re-pinned 2026-11-14 by the
steward's decision (Conductor, delegated): the first pin, `237b79116781821545f7ac58c23ed40bfc0250c4` (13:58 PST), predated the
Designer's five gap fixes (`910f69411e`, 15:13 PST), which stood when he said "lock". Journal, 2026-11-14 Stage 3.

## The locked files

| file | git blob at his lock word | role |
|---|---|---|
| `design/concepts/GimmeSomeSlack/tree.json` | `bf46f92b734b4434c3f62cc540fd42f9225185fe` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/GimmeSomeSlack/sheet.md` | `2ed09a26157d1dd9047fc3a2f941301cb8da5151` | his plain-words sheet: does, does not, his words |
| `design/concepts/GimmeSomeSlack/scenes.json` | `bdf8d41bedf0dd3a2b99470bacc882db57dae417` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/GimmeSomeSlack/floor.json` | `c1d425ed7da4dd6f54a6f8eb296bda78e8d2cd4e` | the quality floor lines every mod meets |
| `design/concepts/GimmeSomeSlack/exam.json` | `a73f3abf604a93035ed90bb9cbea7dc9b7b6de72` | the Cold Reader exam of tree and sheet |
| `design/concepts/GimmeSomeSlack/record.json` | `f7147298065739a42e89d6e22a476b74e09c617c` | the inventory of built capabilities (checklist rows too) |
| `design/concepts/GimmeSomeSlack/plan.md` | `2021a347392bfbb57a37820a7963249446820983` | the build and proof plan |
| `design/concepts/GimmeSomeSlack/stage.json` | `263894e52e1fe23dce1d9b3163d4867214fae118` | the Designer's stage, budget and judge rounds (state, not a bar) |

Tree hash (`concept_tree.py hash`): `5e3aa0d412bb46c241b983d847b4062e574714088d2c8942dc1a7584035e712d`; sheet hash: `33b1cddc183d184ca4e68fdf603440e64fc2422a4cf79c8dc6590c770b6de57a`.

## Counts at the lock

- Bars (the coverage checklist): **47** = 22 inventory rows + 26 tree leaves.
- Floor lines: 23 (21 applicable; not applicable: biome_scope, flight).
- Exam: 26 of 26 scenarios right (tree `5e3aa0d4`, sheet `33b1cddc`: the pinned text).
- Waived lines: 1.

## The leaves (ids only; the text is in tree.json)

- `conduit_invisible` (experience)
- `cords_lie_slack` (experience)
- `no_unforced_sharp_turn` (experience)
- `cords_meet_walls_at_face` (experience)
- `strip_at_every_junction` (experience)
- `dense_block_tangle` (experience)
- `cord_shape_variation_probe` (instrument)
- `cords_never_repeat` (experience)
- `drawing_true_to_grid` (experience)
- `cut_live_and_dead_ends` (experience)
- `floor_end_shocks_crossers` (experience)
- `no_stall_on_rewire` (constraint)
- `spans_above_everything` (experience)
- `fallen_span_on_ground` (experience)
- `fallen_wire_shocks_crossers` (experience)
- `shock_reach_setting` (experience)
- `restring_cut_span` (experience)
- `live_wire_lights_fuel` (experience)
- `tap_steals_and_costs_goodwill` (experience)
- `four_looks_one_run` (experience)
- `settings_switch_cleanly` (experience)
- `gravship_keeps_connections` (experience)
- `owner_change_coils_wires` (experience)
- `statics_clear_between_games` (experience)
- `no_hose_in_gss` (experience)
- `walk_scavenger_base` (walk)

## The inventory rows (ids only; the text is in record.json)

- `invisible_conduit`
- `cord_slack_lay`
- `junction_strips`
- `connectivity_truth`
- `break_ends_live_dead`
- `rebuild_cost`
- `overhead_spans`
- `downed_spans`
- `fallen_wire_shock`
- `wire_down_alert`
- `restring_job`
- `power_theft`
- `four_styles`
- `mod_settings`
- `pipe_pole_switch`
- `gravship_connectivity`
- `owner_change_cut`
- `game_statics_reset`
- `uninstall_clean`
- `no_hose`
- `floor_end_shock`
- `shock_reach_setting`
