# WB-item-RIMMANDRAKE-READ-FIX-11FFFBF13B-WITH-FRESH-EYES-20261127-145006

State: done (2026-11-27).

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_READ_FIX_11FFFBF13B_WITH_FRESH_EYES | REAL (a read) | closed: nothing significant; the 3 files are mark-clean | 3c23aeab37 (review record), close 032e60e9d9 |

- Files read against the locked bars pawn_flight_arc and carried_thing_own_arc: RM_PawnFlyerPatches.cs, RM_ThingFlyer_Knockback.cs (read by the worker), RM_KnockbackProof.cs (read whole by one Opus cold reader).
- The one candidate (fire_half could read FAIL if the Flame-hit colonist burns and runs) did not stand up: about 100 recorded live runs of fire_half read PASS with flameCells=1.
- Nothing is next.
