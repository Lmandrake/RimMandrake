# FlowWorks 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `237b79116781821545f7ac58c23ed40bfc0250c4` (origin/main, 2026-11-13).

## The locked files

| file | git blob at the lock | role |
|---|---|---|
| `design/concepts/FlowWorks/tree.json` | `979107fb431a0db7a56a5e66f556a2d21b1126c5` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/FlowWorks/sheet.md` | `a6cf0c7750a208516787ce1e620c1a80790a4f69` | his plain-words sheet: does, does not, his words |
| `design/concepts/FlowWorks/scenes.json` | `a550df656c8bb6d5738d9fad37bfd58712707159` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/FlowWorks/floor.json` | `3900148bd1edf3363db29730f066f6b82fc69271` | the quality floor lines every mod meets |
| `design/concepts/FlowWorks/exam.json` | `b43a214ac27bbc15012422a085f9b6fa1cb905a3` | the Cold Reader exam of tree and sheet |
| `design/concepts/FlowWorks/record.json` | `95690e151854b087c7d545f459f3f080b3d3813a` | the inventory of built capabilities (checklist rows too) |
| `design/concepts/FlowWorks/plan.md` | `2c6b947a6f2ddf615cb4877241d38da30165c2fb` | the build and proof plan |
| `design/concepts/FlowWorks/stage.json` | `3af3420690554212deb6c62f32e8f2d4f9716c08` | the Designer's stage, budget and judge rounds (state, not a bar) |

Tree hash (`concept_tree.py hash`): `572198fed9a064df1898d695529f85fc343cfeb09bab2d3fe5773bc3abab149d`; sheet hash: `68f9946f8e250af1b2dd19f7ccc901be45ed82c2550693f033dd4b7b83480070`.

## Counts at the lock

- Bars (the coverage checklist): **59** = 28 inventory rows + 31 tree leaves.
- Floor lines: 23 (23 applicable).
- Exam: 17 of 17 scenarios right.
- Waived lines: 0.

## The leaves (ids only; the text is in tree.json)

- `canal_reads_as_dug` (experience)
- `fill_flows_along_canal` (experience)
- `fill_level_legible` (experience)
- `one_still_surface` (experience)
- `source_pays_and_refills` (experience)
- `canal_fire_burns_back` (experience)
- `slime_holds_the_crossing` (experience)
- `pawn_height_follows_depth` (experience)
- `pit_reads_as_hole` (experience)
- `covered_pit_springs` (experience)
- `ways_in_and_out` (experience)
- `sluice_drains_on_command` (experience)
- `hose_reads_as_hose` (experience)
- `one_liquid_network` (experience)
- `trench_gives_cover` (experience)
- `hung_bridge_spans` (experience)
- `ice_cuts_and_melts` (experience)
- `river_flows_endless` (experience)
- `moat_raid_sequence` (experience)
- `drained_hole_is_a_prison` (experience)
- `toss_flame_from_rim` (experience)
- `canal_wets_two_squares` (experience)
- `raiders_fetch_their_fallen` (experience)
- `island_bridges_trap_and_fail` (experience)
- `no_liquid_on_open_ground` (experience)
- `no_full_source_after_draw` (experience)
- `no_snared_standing` (experience)
- `no_impossible_plumbing` (experience)
- `wetting_is_not_flood` (experience)
- `wetness_probe` (instrument)
- `walk_moat_season` (walk)

## The inventory rows (ids only; the text is in record.json)

- `inv_dig_depth`
- `inv_flow_level`
- `inv_stock`
- `inv_overflow_sheet`
- `inv_irrigation`
- `inv_liquid_roster`
- `inv_fire`
- `inv_slime`
- `inv_pits`
- `inv_pit_access`
- `inv_doors`
- `inv_bridges`
- `inv_trench_cover`
- `inv_swim`
- `inv_hoses`
- `inv_liquid_net`
- `inv_converters`
- `inv_bottles_thirst`
- `inv_drilling`
- `inv_sprinklers`
- `inv_rivers`
- `inv_map_controls`
- `inv_quarry`
- `inv_settings`
- `inv_looks`
- `inv_prison_no_bed`
- `inv_toss_flame`
- `inv_raider_fetch_fallen`
