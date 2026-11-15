# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 2

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO, started 2026-11-15 15:19 PST.

## Progress
- 15:30 skeleton written; bridge taken (BENCH); game up on the full list (316 mods). Next: proof build, deploy, minimal list.
- 15:42 game up on the minimal list (34 mods, env_minimal.json), quicktest BorealForest 250x250; proof DLL md5 41071264…; batch driver Transient/ek_visit2/batch.py; first row sc_mortar_throw PASS.
- 15:50 first pass, 53 rows: 47 PASS. FAIL: sc_pit_fall, sc_pit_enemy (descents=0, prior pass now fail), sc_gas_shove_into_pit (off-control colonist moved 8 cells). INVALID: sc_storeroom_bomb_pit, sc_pawn_arc, sc_goods_obstacles. Next: diagnose these; pit_fetch; gas x17; full list.
