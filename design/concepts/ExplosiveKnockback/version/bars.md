# ExplosiveKnockback 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `237b79116781821545f7ac58c23ed40bfc0250c4` (origin/main, 2026-11-13).

## The locked files

| file | git blob at the lock | role |
|---|---|---|
| `design/concepts/ExplosiveKnockback/tree.json` | `23420c4193e49209afaac9a6f4c6fb3c53828408` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/ExplosiveKnockback/sheet.md` | `f60dfd56898ef4ca5e4a671ab593336ab8ae5a19` | his plain-words sheet: does, does not, his words |
| `design/concepts/ExplosiveKnockback/scenes.json` | `61ba1ba6fa5d42b4806a48291818c9275e44bed9` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/ExplosiveKnockback/floor.json` | `a322de650cb13e4bf77f91c24828ea008fe0ddf8` | the quality floor lines every mod meets |
| `design/concepts/ExplosiveKnockback/exam.json` | `fe87a6930abe060a65af732e69f01660fdf34cff` | the Cold Reader exam of tree and sheet |
| `design/concepts/ExplosiveKnockback/record.json` | `94a35620ff4e8d77af38e7452d0c8c704b35cb99` | the inventory of built capabilities (checklist rows too) |
| `design/concepts/ExplosiveKnockback/plan.md` | `ff3f108cd33b2026cef013ee52fafad55fb43a79` | the build and proof plan |
| `design/concepts/ExplosiveKnockback/stage.json` | `a5478f4fc032dc87e731264b51af0d3f7b4bb95f` | the Designer's stage, budget and judge rounds (state, not a bar) |

**Re-pinned 2026-11-14 (Stage 3, by the steward's rule: a locked file changed only by test-text corrections or record-keeping is re-pinned; a changed bar never is).** `tree.json`: only the `coverage` key (the owner-certify stamp); the leaves are unchanged. `scenes.json`: test text only, in sc_spared, sc_mass_and_power (judge gap g4: the colonist back to 64 to 76 kg, pinned there by a test-only proof hook) and sc_settings_sweep. `record.json`: only the `decisions` log; the inventory rows (bars) are unchanged. The blobs at the lock were tree `06e6a1ff44`, scenes `e4a97d710a`, record `14e3015936`.

**Re-pinned again 2026-11-14 (Stage 5, same rule; journal interventions of that date).** `scenes.json`: test text only, in sc_pawn_arc (it checks the colonist still holds its stack, as built and as the owner kept for 0.1.0, journal question 7; it had said the stack was dropped at takeoff) and sc_settings_sweep (its lane and action now name every saved setting, question 6). `record.json`: bookkeeping only, questions 3 and 9: `impl` absent to present with evidence on inv_creature_mass_limit and inv_blast_power_damage, and inv_big_corpse_spared's skip reason too_big to too_heavy (the body-size limit was replaced by the mass limit; the bar, a corpse of body size 2.5 or more is never thrown, is unchanged). The blobs before were scenes `267627ebab`, record `e608b943b3`.

Tree hash (`concept_tree.py hash`): `02900038234b11c46790c7a09b75a68a0b877cd3270c7e57c94564ef758b15b2`; sheet hash: `234fd3c20e850bdde174efc6b3d4b20f1025dc5ddbf2c15caef766a925f0c722`.

## Counts at the lock

- Bars (the coverage checklist): **59** = 30 inventory rows + 29 tree leaves.
- Floor lines: 23 (22 applicable; not applicable: biome_scope).
- Exam: 119 of 119 scenarios right.
- Waived lines: 0.

## The leaves (ids only; the text is in tree.json)

- `people_thrown_three_cells` (experience)
- `pawn_flight_arc` (experience)
- `the_spared` (experience)
- `heavier_flies_less` (experience)
- `recovery_immunity` (experience)
- `hose_drops_at_takeoff` (experience)
- `wall_stops_dead` (experience)
- `pawn_hits_pawn_stops` (experience)
- `doors_and_deep_water_stop` (experience)
- `shield_belt_holds` (experience)
- `goods_arc_spin_rebound` (experience)
- `every_good_moves` (experience)
- `open_shelf_scatters` (experience)
- `closed_container_holds` (experience)
- `heavy_stack_knocks` (experience)
- `every_harmful_blast_throws` (experience)
- `only_explosions_throw` (experience)
- `per_weapon_tuning` (experience)
- `gas_goes_clump_by_clump` (experience)
- `our_gases_burn` (experience)
- `blast_breaks_pit_cover` (experience)
- `thrown_into_pit_falls` (experience)
- `pit_goods_fetched` (experience)
- `no_teleport` (experience)
- `no_careless_fall` (experience)
- `settings_scale_and_switch` (experience)
- `barrage_frame_budget` (constraint)
- `frame_time_probe` (instrument)
- `walk_storeroom_raid` (walk)

## The inventory rows (ids only; the text is in record.json)

- `inv_kernel`
- `inv_hook`
- `inv_pawn_flyer`
- `inv_which_blasts`
- `inv_items_teleport`
- `inv_shelf_skip`
- `inv_who_is_spared`
- `inv_shield`
- `inv_recovery`
- `inv_caps`
- `inv_settings`
- `inv_pits_receive`
- `inv_pit_floor_haul`
- `inv_hose_drop`
- `inv_proof_scenes`
- `inv_gas_chain`
- `inv_goods_fly`
- `inv_closed_guard`
- `inv_container_shove`
- `inv_heavy_knock`
- `inv_gas_tags`
- `inv_perf_all_fly`
- `inv_weapon_ext_fields`
- `inv_killed_corpse`
- `inv_pit_floor_goods_stay`
- `inv_big_corpse_spared`
- `inv_mass_limit_skip`
- `inv_too_weak_skip`
- `inv_creature_mass_limit`
- `inv_blast_power_damage`
