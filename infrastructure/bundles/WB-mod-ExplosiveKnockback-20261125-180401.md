# WB-mod-ExplosiveKnockback-20261125-180401

System: mod ExplosiveKnockback (Design Version 0.2.0, at offline_build on its road back after in-game visit 1). Seven members.
State: 5 closed, 2 open. Saved at 2026-11-25 12:00 PST for a restart.

## Done

| member | class | outcome | commits | live reading |
|---|---|---|---|---|
| RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC | ALREADY FIXED | closed | 07a4bca605 | sc_pawn_arc_carried_thing real 7/7, plant FAIL (visit 1) |
| RIMMANDRAKE_FOLD_KNOCKBACK_POLISH_LINES_INTO_ZERO_TWO_THREE_JUDGED_IN | ALREADY FIXED | closed | 07a4bca605, 7dab94c3b7 | sandbag 8/8, gas cover 10/10, rebound legs 13/13, each plant FAIL (visit 1) |
| RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS | REAL (scene wrong) | closed | 608e5aabf2, d172734c75, 370fdfe5f4 | storeroom pit real 4/4 SUCCESS, plant knockback_off MOD FAILURE (ArchSmall 10:57 PST) |
| RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN | REAL (landing half unchecked) | closed | be795bc515, 85748bcfc6 | landing scene 11/11 PASS; plant no_bruise 6 FAIL; planted build swap 3 FAIL (ArchSmall 11:26-11:35 PST) |
| RIMMANDRAKE_EXPLAIN_KNOCKBACK_PALE_CLOUD_OVER_EMP_PAD | explained, not the mod's | closed | 50f8ad1b01 | the cloud comes with every Knockback switch off (ArchSmall 11:48 PST) |

## Open, in order

1. RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES. Parts (1) landing and (2) container are settled (see its
   PROGRESS note: (2) is an equivalent mutant). Left: (3) the sc_lookup weapon-source and damage-type-source lanes.
   - No bridge tool fires an explosion with a weapon or projectile def, or adds a DefModExtension at runtime. Build generic
     ones first (the CLAUDE.md bridge rule; the rimbridge-companion skill): `jawa/explosion_at` gains `weapon=` and
     `projectile=` ThingDef names (GenExplosion.DoExplosion takes both); a session-scoped tool adds or removes an
     RM_KnockbackExtension-like DefModExtension by type name and fields on a named def.
   - Then a Python scene `src/RimMandrake/ExplosiveKnockback/proof/scene_lookup_sources.py` on ArchSmall: weapon source
     (ext on a weapon def only -> request line source "weapon"), projectile beats weapon, damage-type source (a Flame blast:
     source "damageDef", half the cells of Bomb); cells read against the kernel. Plant: no weapon ext. Add its row to
     version/test_table.json and .md as a decider of per_weapon_tuning and inv_weapon_ext_fields.
   - Close with every part's sha.
2. RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS (kind C). Its PROGRESS note holds the plan: a long batch
   on the proof build with a settings read before and after each process. If no sighting in that batch, write the count of
   opportunities on the item and leave the hunt open with a dated wait; a hunt is never a bar.

## Learned

- ArchSmall now runs tier explosiveknockback_visit with mandrake.rm.patches (25 mods; modset_builder.py changed at
  608e5aabf2). The storeroom-pit fixture is copied into ArchSmall's Saves. ArchSmall holds the release DLL ddbf5e27c549.
- Scenes that write settings must name the session's driver (`driver=s.id`) and read the reply.
- The scene library refuses a DLL that is not committed for every mod named in `needs["mods"]`; a planted build's red reading
  runs by hand from a scratch copy with `needs["mods"]` empty (scratch: D:\ClaudeWork\rimmandrake\scratch\ek_bundle_wb1804).
- `s.act.job(..., cell=)` puts the cell in targetB; a Goto reads targetA, so a walk order goes raw through jawa/ordered_job.
- A colonist one cell from a force-1 Bomb, with maxThrowCells 2, lands exactly 2 cells on; the flyer's minimum flight is 18
  ticks, so a walker ordered 2 ticks before the blast is landed on.
- Machine load near 31 makes python.exe fail now and then with WSL vsock timeouts; a rerun passes.
- Context: 262k after group 1 (three members); 400k after group 2 (bruise, landing lane, EMP cloud).

## Not tested

- The lookup weapon and damage-type lanes (no tool yet; above).
- The hunt batch (above).
