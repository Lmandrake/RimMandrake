# Work bundle WB-item-RIMMANDRAKE-BUILD-MUTANTS-BY-OVERLAY-AUTHOR-DOES-NOT-CHOOSE-20261125-113229

System: item RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE (Bridge v2 mutants by overlay).

## Members

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE | REAL (live half owed) | fixed and proven live; closing | 3e94cc7c27, 2b331a3b17, 95e27d1a25, b376cafdf3, da57610c22, e0bf13ff22, 1462bf5cb8, 19664434210f |

## What is known

- Offline: selftest_scene_mutants 16/16 green at 2026-11-25 03:37 PST; parts offline_rules, knockback_list hold.
- Left: patch_switch_live (`python.exe src\RimMandrake\bridgetools\prove_patch_switch.py`, hardcoded to ArchSmall,
  needs the companion with jawa/patch_switch deployed) and both_ways_live (`scene.py both-ways
  src\RimMandrake\ExplosiveKnockback\proof\scene_storeroom_pit.py`, on ArchBig).
- 03:37 PST: ArchBig held (Knockback sc_save_in_air bundle), ArchSmall held (calm profile live proof).

## Outcome (2026-11-25 05:50 PST)

- both_ways_live: scene.py both-ways scene_storeroom_pit on ArchBig: throw_one_cell KILLED (green SUCCESS, red MOD FAILURE on
  success, one fixture hash, one rand); history --killed exit 0, ONLY_VALUE_KILLS.
- patch_switch_live: prove_patch_switch.py --game ArchBig VERDICT PASS, 13 of 13 rows.
- Fixed on the way: scene.open answers VEF new-faction dialogs at the end of the settle; scene_judge reads cast and world
  tracks, in_tick tap rows and from/to cast links; scene_mutants._side reads first_failed; Knockback witnesses goods[i].positionInt.
- Fresh reader: nothing significant; 5 polish lines on the scene-judge and scene-library polish lists.

## Context size after each group

- start: 98674 of 1000000
- after the live pass: about 300000 of 1000000
