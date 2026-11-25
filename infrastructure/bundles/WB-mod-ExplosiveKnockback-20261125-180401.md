# WB-mod-ExplosiveKnockback-20261125-180401

System: mod ExplosiveKnockback (Design Version 0.2.0, at offline_build on its road back after in-game visit 1). Seven members.
State: 6 closed, 1 on a dated wait (a kind C hunt). Ended 2026-11-25 15:52 PST, restart 1.

## Done

| member | class | outcome | commits | live reading |
|---|---|---|---|---|
| RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC | ALREADY FIXED | closed | 07a4bca605 | sc_pawn_arc_carried_thing real 7/7, plant FAIL (visit 1) |
| RIMMANDRAKE_FOLD_KNOCKBACK_POLISH_LINES_INTO_ZERO_TWO_THREE_JUDGED_IN | ALREADY FIXED | closed | 07a4bca605, 7dab94c3b7 | sandbag 8/8, gas cover 10/10, rebound legs 13/13, each plant FAIL (visit 1) |
| RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS | REAL (scene wrong) | closed | 608e5aabf2, d172734c75, 370fdfe5f4 | storeroom pit real 4/4 SUCCESS, plant knockback_off MOD FAILURE (ArchSmall 10:57 PST) |
| RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN | REAL (landing half unchecked) | closed | be795bc515, 85748bcfc6 | landing scene 11/11 PASS; plant no_bruise 6 FAIL; planted build swap 3 FAIL (ArchSmall 11:26-11:35 PST) |
| RIMMANDRAKE_EXPLAIN_KNOCKBACK_PALE_CLOUD_OVER_EMP_PAD | explained, not the mod's | closed | 50f8ad1b01 | the cloud comes with every Knockback switch off (ArchSmall 11:48 PST) |
| RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES | REAL (three bar halves unseen) | closed | be795bc515, 85748bcfc6, b545b14026, 5b7a026ba6 | (1) landing lane as above; (2) equivalent mutant; (3) new bridge tools + scene_lookup_sources real 5/5 PASS, plant no_weapon_ext 2 FAIL, plant fire_off 1 FAIL (ArchSmall 12:41-12:45 PST) |
| RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS | kind C hunt | dated wait 2026-12-02 | cee212dff6, 2429a0d894, bedd128cf7, 38749cda78 | 3 long batches + 20 repeats: 2 sightings, settings never off defaults (runner restore ruled out); fate/input lines print on the next sighting |

## Open, in order

None. The hunt waits for the next long proof-build batch (its note holds the command).

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
- Context: 262k after group 1 (three members); 400k after group 2 (bruise, landing lane, EMP cloud). Restart 1: 210k after
  the lookup lanes; about 330k at the end of the hunt.
- New generic bridge tools: jawa/explosion_at weapon= and projectile=; jawa/def_mod_extension (list/add/remove, put back
  when the scene session is released). The deployed companion on ArchSmall carries them (b545b14026).
- scene.py accept runs under python.exe from the WSL clone (cwd), never the D: mirror (no git there).
- ArchSmall's launcher often reads a WSL vsock timeout or DEADLINE_ALIVE while the game comes up; poll the bridge instead.
  Steam had closed once: start "C:\Program Files (x86)\Steam\steam.exe" -silent, then launch.

## Not tested

- The staging placement guard of bedd128cf7 has not been seen to catch a real placement fault: no planted case exists, because
  Prepare clears the patch first. Batch 3 shows it gives no false INVALID.
- The gone() and WantWhy() lines have not printed yet: no sighting came after they were deployed.
