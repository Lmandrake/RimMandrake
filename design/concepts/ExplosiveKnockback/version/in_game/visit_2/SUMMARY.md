# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 2

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO, started 2026-11-15 15:19 PST.

## Progress
- 15:30 skeleton written; bridge taken (BENCH); game up on the full list (316 mods). Next: proof build, deploy, minimal list.
- 15:42 game up on the minimal list (34 mods, env_minimal.json), quicktest BorealForest 250x250; proof DLL md5 41071264…; batch driver Transient/ek_visit2/batch.py; first row sc_mortar_throw PASS.
- 15:50 first pass, 53 rows: 47 PASS. FAIL: sc_pit_fall, sc_pit_enemy (descents=0, prior pass now fail), sc_gas_shove_into_pit (off-control colonist moved 8 cells). INVALID: sc_storeroom_bomb_pit, sc_pawn_arc, sc_goods_obstacles. Next: diagnose these; pit_fetch; gas x17; full list.
- 16:15 diagnosed: sc_pit_fall/sc_pit_enemy FAIL = SITE (a BorealForest pond left a FlowWorks bed, depth 4, under origin 12,12; pit_enemy at a clean origin passed); gas_into_pit_off FAIL = HARNESS (vanilla fire sets the control colonist alight, it runs). Fix 4a73149539 (guard selftest_explosiveknockback_stage6_visit2.py red 4/4 then green), DLL 2f74ac9094. New map AridShrubland; rerunning all minimal rows (env_minimal2.json).
- 16:45 second pass (env_minimal2, AridShrubland): 50/52 PASS; goods_obstacles and storeroom_bomb_pit INVALID = HARNESS (want measured from the scene origin on lanes S/W; cover stack planned before the cover). Fix 366bed691c; goods_obstacles PASS on it. pit_fetch FAIL again: rain filled both pits to 2 m, the hauler swam into the raised-ladder control (SITE). gas_chain 17/17 PASS (visit 1: 12/17). Next: rain-off pit_fetch + storeroom diagnostics build, then the full list.
