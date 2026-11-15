# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 1

Started 2026-11-15 05:21 PST (detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST).

## Progress

- 05:22 skeleton written; precondition `in_game 0.1.0` [measured].
- 05:36 proof build (source 545e930429, DLL md5 76e4e00b) deployed; minimal+EK list 34 mods up (env_minimal.json); quicktest map AridShrubland 250x250; batch driver Transient/ek_visit1/batch.py; first 3 checks PASS.
- 05:50 batch 2: 14 checks; spared_states FAIL (diagnosed HARNESS: skipped pawns walk in the 240 ticks before the read; carrier's carry dropped before the blast), pawn_arc INVALID (walker 3 cells away cannot reach the landing cell inside a ~25-tick flight), closed_containers INVALID (no closed LWM container can reach 76-249 kg: WeaponsLocker 8 kg + maxTotalMass 50), storeroom_bomb_pit unknown scene.
