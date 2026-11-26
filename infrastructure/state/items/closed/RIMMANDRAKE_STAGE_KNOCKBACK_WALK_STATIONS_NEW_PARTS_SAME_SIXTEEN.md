# RIMMANDRAKE_STAGE_KNOCKBACK_WALK_STATIONS_NEW_PARTS_SAME_SIXTEEN

## spec

The Explosive Knockback 0.2.0 walk save `EK_V020_VISIT3_WALK_20261126` (ArchBig) holds the same 16 stations that the
owner walked for 0.1.0 on 2026-11-24 (`STATIONS` in
`design/concepts/ExplosiveKnockback/version/in_game/visit_3/scripts/walk_save.py`). No station shows:
- a carried thing that flies on its own arc (`carried_thing_own_arc`);
- an unequal-size bruise: a colonist thrown onto a small animal and onto a large one (`collision_bruise_by_size`);
- a sandbag that stops a throw before it reaches a pawn (`no_impact_without_contact`);
- a person on an intact pit cover shoved by burning gas (`gas_shoves_pawn_on_pit_cover`).
The blast show shows only as aftermath (scars and soot). Add one START/AFTER station for each of the four, staged as the
0.2.0 scenes stage them (`sc_pawn_arc_carried_thing`, `sc_pawn_arc_bruise_sizes` / `sc_pawn_land_on_pawn_sizes`,
`sc_pawn_arc_sandbag_no_contact`, `sc_gas_chain_pawn_on_cover`), record the save's look cells with
`look_changed_labels.record`, and restage the walk save on a free game. Recommended class: current version (a Problem of
the walk save; no bar moves).

## refs
file: design/concepts/ExplosiveKnockback/version/in_game/visit_3/scripts/walk_save.py
file: design/concepts/ExplosiveKnockback/look_cells/EK_V020_VISIT3_WALK_20261126.json
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs

## verify

The ledger `--effect` command: a look_cells file of the mod names a carried-thing cell and a bruise cell. Red now (rc 1,
seen 2026-11-26); green on a planted look_cells file holding both cells (rc 0, seen 2026-11-26, file removed after).

## criteria

- The new walk save has a START/AFTER station for each of the four bars above, each with its sign.
- `walk_twins.py check` reads ok on the new save.
- The walk brief names the new save.
