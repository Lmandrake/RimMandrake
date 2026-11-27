# WB-item-RIMMANDRAKE-READ-FIX-74DFF4C5BC-WITH-FRESH-EYES-20261127-075245

## Done
- `RIMMANDRAKE_READ_FIX_74DFF4C5BC_WITH_FRESH_EYES`: fresh read of `src/RimMandrake/CreatureBehaviors/live_direct_sun_angle.py`
  (fix 74dff4c5bc). No Problem: the child is vanished by `jawa/pawn_force_incapacitate action=vanish`, which calls
  `Destroy(DestroyMode.Vanish)` and reports `destroyedAfter`, and FindPawn takes the id that spawn_pawn returns.
  Polish in 4a5bba7b7d: the weather unlock moved into a `finally`, because a COULD NOT LOOK left the map locked Clear
  against the contract's `end`. The check is a fake session in
  `/mnt/d/ClaudeWork/scratch/fresh_read_74dff/fake_check.py`: unlock calls are 0 on the parent and 1 on the fix.
  Also: the `forbidden` line names RM_PlanetSunGeometry, as the code does; the forbidden_since docstring no longer
  promises a tuple; the unused `forge_restore` is gone. mark-clean at 4a5bba7b7d. `fresh_reader.py holds` exits 0.

## Next
- Nothing. The bundle has one member.
