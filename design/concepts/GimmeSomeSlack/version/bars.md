# GimmeSomeSlack 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `237b79116781821545f7ac58c23ed40bfc0250c4` (origin/main, 2026-11-13).

## The locked files

| file | git blob at the lock | role |
|---|---|---|
| `design/concepts/GimmeSomeSlack/tree.json` | `9371b2d41f7385e5239183194f7776ada4c53b9c` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/GimmeSomeSlack/sheet.md` | `5984716283af393ad724c6e27a44826fd6b77cbd` | his plain-words sheet: does, does not, his words |
| `design/concepts/GimmeSomeSlack/scenes.json` | `e5fe80ca3bc85947595a03395d0f097e36173cb8` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/GimmeSomeSlack/floor.json` | `c1d425ed7da4dd6f54a6f8eb296bda78e8d2cd4e` | the quality floor lines every mod meets |
| `design/concepts/GimmeSomeSlack/exam.json` | `dedc0e755756e69b3b97bb87e3a6d29e5b48b615` | the Cold Reader exam of tree and sheet |
| `design/concepts/GimmeSomeSlack/record.json` | `32fc2b258928a0b029692472b746106f79380740` | the inventory of built capabilities (checklist rows too) |
| `design/concepts/GimmeSomeSlack/plan.md` | `2021a347392bfbb57a37820a7963249446820983` | the build and proof plan |
| `design/concepts/GimmeSomeSlack/stage.json` | `f1aa438344d37135cd4258435553b1e6d88070a7` | the Designer's stage, budget and judge rounds (state, not a bar) |

Tree hash (`concept_tree.py hash`): `eb1981b88959b758a00f6984241c719cf574c0fa185a26884940b817b905c1e3`; sheet hash: `3a7d223aa9c261d04fe4c11c955ee287623b532dae07d7502853d6c286cd20f1`.

## Counts at the lock

- Bars (the coverage checklist): **47** = 22 inventory rows + 26 tree leaves.
- Floor lines: 23 (21 applicable; not applicable: biome_scope, flight).
- Exam: 26 of 26 scenarios right (against an earlier tree and sheet; see VERSION.json caveats).
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
