# ExplosiveKnockback 0.2.0 — in-game acceptance, visit 2

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO_RUN_TWO, started 2026-11-25 21:20 PST, on
ArchBig. Skeleton: in progress.

## Progress
- 21:25 PST: claimed, synced, precondition `in_game 0.2.0` holds, bridge taken on ArchBig.
- 21:44 PST: batch 1 (54 knockback_runner checks, proof build of b9ee5b5fb8, 26-mod tier explosiveknockback_visit): 53 PASS;
  sc_barrage_perf ENVIRONMENT FAULT (the mod-off arm itself 54.5 ms p99 over the 50 ms budget; mod-on 53.0 ms).
- 21:48 PST: sc_save_in_air APPARATUS FAULT (census counted a leftover component); repaired 685fe7bb73, real PASS 5/5,
  plant lose_heavy FAIL.
