# Work bundle WB-item-RIMMANDRAKE-BUILD-MUTANTS-BY-OVERLAY-AUTHOR-DOES-NOT-CHOOSE-20261125-113229

System: item RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE (Bridge v2 mutants by overlay).

## Members

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE | REAL (live half owed) | offline done; live open | 3e94cc7c27 |

## What is known

- Offline: selftest_scene_mutants 16/16 green at 2026-11-25 03:37 PST; parts offline_rules, knockback_list hold.
- Left: patch_switch_live (`python.exe src\RimMandrake\bridgetools\prove_patch_switch.py`, hardcoded to ArchSmall,
  needs the companion with jawa/patch_switch deployed) and both_ways_live (`scene.py both-ways
  src\RimMandrake\ExplosiveKnockback\proof\scene_storeroom_pit.py`, on ArchBig).
- 03:37 PST: ArchBig held (Knockback sc_save_in_air bundle), ArchSmall held (calm profile live proof).

## Next, in order

1. Wait for a free Archmagi game; PROGRESS note each 30 min.
2. Deploy companion from origin/main, run prove_patch_switch.py.
3. Run scene.py both-ways on ArchBig; read `scene_mutants.py history ExplosiveKnockback --killed`.
4. Close with list_shape holds.

## Context size after each group

- start: 98674 of 1000000
