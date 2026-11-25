# WB-mod-ExplosiveKnockback-20261125-180401

System: mod ExplosiveKnockback (Design Version 0.2.0, at offline_build on its road back after in-game visit 1). Seven members.

## Done

| member | class | outcome | commits | live reading |
|---|---|---|---|---|
| RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC | ALREADY FIXED | closed | 07a4bca605 | sc_pawn_arc_carried_thing real 7/7, plant FAIL (visit 1) |
| RIMMANDRAKE_FOLD_KNOCKBACK_POLISH_LINES_INTO_ZERO_TWO_THREE_JUDGED_IN | ALREADY FIXED | closed | 07a4bca605, 7dab94c3b7 | sandbag 8/8, gas cover 10/10, rebound legs 13/13, each plant FAIL (visit 1) |
| RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS | REAL (scene wrong) | closed | 608e5aabf2, d172734c75, 370fdfe5f4 | storeroom pit real 4/4 SUCCESS, plant MOD FAILURE (ArchSmall 10:57 PST) |

## Open, in order

1. RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN with RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES: one group
   (the landing-on-pawn bruise half has no live check; container across an open pit; sc_lookup lanes b-h).
2. RIMMANDRAKE_EXPLAIN_KNOCKBACK_PALE_CLOUD_OVER_EMP_PAD: a live probe (EMP alone, show on and off).
3. RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS: kind C hunt.

## Learned

- ArchSmall runs tier explosiveknockback_visit with mandrake.rm.patches (25 mods); the storeroom fixture is copied there.
- Scenes that write settings must name the session's driver (`driver=s.id`) and read the reply; scene_storeroom_pit did not.
- Machine load ~31: python.exe from WSL fails now and then with vsock timeouts; a rerun passes.
- Context: 230k after group 1 (three members).
