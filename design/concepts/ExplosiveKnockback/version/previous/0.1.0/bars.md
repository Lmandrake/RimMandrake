# ExplosiveKnockback 0.1.0: the bars, locked as they stood on 2026-11-13

Owner, by card 2026-11-13: *"Lock today's bars as 0.1.0"*. Nothing here edits a bar: this file points at the bars and pins their bytes. State: locked, pending his read.

Lock commit: `237b79116781821545f7ac58c23ed40bfc0250c4` (origin/main, 2026-11-13).

## The locked files

| file | git blob at the lock | role |
|---|---|---|
| `design/concepts/ExplosiveKnockback/tree.json` | `5fed74b534506f5874d9a0e0a5a89a814f83fd47` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/ExplosiveKnockback/sheet.md` | `0cd48ce7a8e382cb968064990c5d49eabc4a4014` | his plain-words sheet: does, does not, his words |
| `design/concepts/ExplosiveKnockback/scenes.json` | `fd275c0130c8bb3d3e67e78451b83232ccb53597` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/ExplosiveKnockback/floor.json` | `a322de650cb13e4bf77f91c24828ea008fe0ddf8` | the quality floor lines every mod meets |
| `design/concepts/ExplosiveKnockback/exam.json` | `5a8f2e579bed5cb0c8f7e95ee823162eb6b25538` | the Cold Reader exam of tree and sheet |
| `design/concepts/ExplosiveKnockback/record.json` | `2e37e67adcf6fca2ae7f9b359d333bf050ee215f` | the inventory of built capabilities (checklist rows too) |
| `design/concepts/ExplosiveKnockback/plan.md` | `ff3f108cd33b2026cef013ee52fafad55fb43a79` | the build and proof plan |
| `design/concepts/ExplosiveKnockback/stage.json` | `c7cc57934f18939dea2777b4b33b1209b470af54` | the Designer's stage, budget and judge rounds (state, not a bar) |

**Re-pinned 2026-11-14 (Stage 3, by the steward's rule: a locked file changed only by test-text corrections or record-keeping is re-pinned; a changed bar never is).** `tree.json`: only the `coverage` key (the owner-certify stamp); the leaves are unchanged. `scenes.json`: test text only, in sc_spared, sc_mass_and_power (judge gap g4: the colonist back to 64 to 76 kg, pinned there by a test-only proof hook) and sc_settings_sweep. `record.json`: only the `decisions` log; the inventory rows (bars) are unchanged. The blobs at the lock were tree `06e6a1ff44`, scenes `e4a97d710a`, record `14e3015936`.

**Re-pinned again 2026-11-14 (Stage 5, same rule; journal interventions of that date).** `scenes.json`: test text only, in sc_pawn_arc (it checks the colonist still holds its stack, as built and as the owner kept for 0.1.0, journal question 7; it had said the stack was dropped at takeoff) and sc_settings_sweep (its lane and action now name every saved setting, question 6). `record.json`: bookkeeping only, questions 3 and 9: `impl` absent to present with evidence on inv_creature_mass_limit and inv_blast_power_damage, and inv_big_corpse_spared's skip reason too_big to too_heavy (the body-size limit was replaced by the mass limit; the bar, a corpse of body size 2.5 or more is never thrown, is unchanged). The blobs before were scenes `267627ebab`, record `e608b943b3`.

**Re-pinned 2026-11-15 (blind challenge, after cycle 2; journal interventions of that date).** `scenes.json`: test text only. sc_storeroom_mortar: the per-good wild-to-kernel ratio 1.3 to 2.0, which whole cells make unattainable for a correct build, is replaced by the whole-cell band 1.6 allows from each good's kernel cells (neutral fixer; refusal record `version/criterion_repairs/sc_storeroom_mortar_2026-11-15/refusal.json`), and its "request line" is the move line, where the code journals both cells; the bar, goods fly about 1.6 times the kernel throw, is unchanged. sc_closed_containers, sc_settings_sweep and sc_storeroom_bomb_pit: a closed container "slid one cell" now reads "thrown a short way", the test following the owner's card of 2026-11-14 (OWNER:1794721689897638306); the bar's own words in `tree.json` and `sheet.md` are not changed here, they wait on his re-certification (RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING). `record.json`: the decisions log only (dc_container_thrown_short_way added, dl_container_shove points at it). The blobs before were scenes `61ba1ba6fa`, record `94a35620ff`.

**Re-pinned 2026-11-15 (his re-certification; RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING).** He answered the card "Do you certify ExplosiveKnockback's tree with the container now thrown a short way?" with "Certify, and fix the rule" (OWNER:1794748823561950419 on the concept's item). The bar's own words now follow his card of 2026-11-14 (OWNER:1794721689897638306): `tree.json` leaf closed_container_holds and `sheet.md` say a closed container is thrown a short way, no longer that it slides one cell (`version/criterion_repairs/closed_containers_thrown_2026-11-15/tree_sheet_rewording.patch`, plus sheet line 36 the patch missed). `concept_tree.py certify` re-stamped the coverage certificate on his event. `exam.json`: exam11 refroze exam10's 119 scenarios with the 15 container scenarios reworded the same way, polarity unchanged; two fresh readers scored 119 of 119, and a fresh control on the tree without heavier_flies_less missed m1, m3, m5 and m8. `designer_stage.py repin` re-pinned stages 2 to 5 (3d5eeb0e44), taking in his 2026-11-13 lock pass and the post-lock scene commits 60428da17f, 12efcb3138, 8498e2b493, 8bd7e7e715 and 709c740f76, each cited to the owner event it carried out. The blobs before were tree `23420c4193`, sheet `f60dfd5689`, exam `fe87a6930a`.

**Re-pinned 2026-11-15 7:37 PM PST (his answer on the barrage bar; RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO).** He agreed (OWNER:1794799770273329641, *"1 agree."*) that `barrage_frame_budget` reads the 99th-percentile frame inside the barrage-and-gas-chain window (0.9-8.25 s) at most 50 ms instead of the single worst frame, which the mod-off control broke on random list stalls. `scenes.json` (sc_barrage_perf expect and control), `record.json` (dl_perf_budget prose) and `plan.md` changed at `9c8c37aced`; `designer_stage.py repin` re-pinned stages 2-4 citing it and the backfilled card OWNER:1794790816821560212 (already carried out at `0774d3bc1a`). `tree.json` and `sheet.md` are unchanged: their new words are held as `version/criterion_repairs/sc_barrage_perf_2026-11-15/tree_sheet_rewording.patch` until he re-certifies the tree.

**Re-pinned 2026-11-15 8:35 PM PST (his re-certification on the barrage bar; RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_BARRAGE_P99_HELD_AGAIN).** The held patch is applied at `3aa7e5c15d`: `tree.json` leaf barrage_frame_budget and `sheet.md` say the 99th-percentile frame inside the 0.9-8.25 s window at most 50 ms (the leaf's experience leads with "at most 50 ms", the shape lint asks of a constraint). His "1 agree." (OWNER:1794799770273329641) sits on the repair item, which a refusal record of this concept (`version/criterion_repairs/sc_barrage_perf_2026-11-15/refusal.json`) ties to the mod; `concept_tree.py certify` now takes his words on an item caused by the concept's item or by one of its refusal records (the Conductor's evidence-for-ask call carrying out the "fix the rule" half of his card OWNER:1794748823561950419), and re-stamped the coverage on that event (`fab7999d8f`). `designer_stage.py repin` re-pinned stages 2, 3 and 5 and left stage 4 stale by its own rule: the Cold Reader exam is frozen against the old tree and sheet and is retaken at the next open (no exam scenario reads this leaf).

**Re-pinned 2026-11-16 (his card on the walk's frame row; RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES).** He picked "Compare to mod-off (Recommended)" (OWNER:1794834159094900561, mod-ledger question q:walk-frame-clause-list-floor-already-eighty): the walk's frame row passes when the mod-on 99th-percentile frame time is within 10% of the same colony's mod-off arm measured in the same run, and is UNMEASURED unless both arms are measured. `tree.json` leaf walk_storeroom_raid and `scenes.json` sc_walk_raid say so in place of "frame budget held", and `validation.py` judges FRAME_BUDGET that way, at `65eb8bf28a`. The 50 ms bar (barrage_frame_budget) is unchanged. `concept_tree.py certify` re-stamped the coverage on his card; `designer_stage.py repin` re-pinned stages 3 and 5, and stage 4 stays void for RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF.

Tree hash (`concept_tree.py hash`): `743e234b354db00c93dba97b007884bf113774384b7e99ac1135bea55c0fe94a`; sheet hash: `def5f528b8e8416c73147d1242ac7b23f54a34454a7c0b502077b233e6d2e3cc`.

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
