# WB-item-RIMMANDRAKE-SHRINK-KNOCKBACK-SCENES-ONE-SAVE-IN-AIR-20261125-080228

System: item RIMMANDRAKE_SHRINK_KNOCKBACK_SCENES_ONE_SAVE_IN_AIR (Explosive Knockback scenes). One member.

## Done

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_SHRINK_KNOCKBACK_SCENES_ONE_SAVE_IN_AIR | REAL | built; acceptance test PASS (red before: 5 lines) | 961525597213 |

## Learned

- His frame-row card of 2026-11-16 (OWNER:1794834159094900561) is kept: `sc_walk_frames` decides that clause of
  walk_storeroom_raid until the Conductor rules on RIMMANDRAKE_DECIDE_KNOCKBACK_FRAME_ROW_HIS_CARD_SET_IT (noted there).
- The proof DLL with the new pit_goods_fetch code: `D:\ClaudeWork\scratch\ek_save_in_air\` (never commit it). The pit
  scene needs a restart of the game onto that DLL; sc_save_in_air needs no new C# (any proof build of 0.2.0).
- Context after the build group: 264k of 1M.

## Next, in order

1. The fresh reader's findings (code_review.md), fixed test first if significant.
2. Live: `scene_save_in_air.py`, then `--plant lose_heavy` (must FAIL SA_EACH_ONCE and SA_LANDED); then
   `knockback_runner.py --scenes pit_goods_fetch --ticks 5000` on the new proof DLL. ArchBig and ArchSmall were both held at 00:21 PST.
3. Close the member with the commit and the live readings.
