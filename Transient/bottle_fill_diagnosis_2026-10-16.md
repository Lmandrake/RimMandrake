# LIQUID_BOTTLE_LOOP_1 — "fill job never produces a filled bottle": diagnosis 2026-10-16

**Verdict: the BLOCKED reason is stale. Cause found and fixed 2026-10-05; the fill has since passed live twice.** No new fix made.

## Cause (confidence: high, already confirmed live)
`FailOnDespawnedNullOrForbidden(TargetIndex.A)` on the carried container. `Toils_Haul.StartCarryThing` despawns
the bottle when the pawn picks it up, so every fill/wash/pour/draw job ended the tick after pickup and the pawn
dropped the bottle. This matches the 2026-09-25 observation exactly (job accepted, pawn reaches the bottle and the
water, job ends, empty bottle back on the floor, no exception logged). Fixed at `cf1e75d26`: all four drivers in
`src/RimMandrake/FlowWorks/Source/LiquidTypes/` (`JobDriver_FillBottle.cs`, `JobDriver_WashBottle.cs`,
`JobDriver_FillBottleFromTank.cs`, `JobDriver_EmptyBottleIntoTank.cs`) now use `FailOnDestroyedNullOrForbidden` on A.
The `FailOnDespawned…(B)` still in the two tank drivers targets the tank, which stays spawned, so it is correct.

## Evidence that it is fixed
- `Transient/bench_live_20261015_l1/step4/fw_bottles.json` (BENCH L1, 2026-10-15): `bottle_loop_on` PASS. That row
  (`src/RimMandrake/FlowWorks/northstar/extensions.py:1716`) spawns an `RM_BottleEmpty` and only waits; it passes
  when the WorkGiver fills the bottle by itself (empty 0, `RM_Bottle_FreshWater` > 0). Also PASS: `bottle_loop_off`,
  `bottle_dirty_on`, `bottle_wash_returns_clean`, `revert_off_holds`, `boiling_bottle_reverts_to_fresh`.
- Ledger note 2026-10-15T14:48: `toggle_bottle_loop` 2/2 live PASS on 2026-10-13.

## Other candidates considered, ruled out by the live PASS
WorkGiver never offers the job; filled ThingDef missing or MayRequire-gated; product spawned then despawned; stack
merge; reservation. The fill produces `RM_Bottle_FreshWater` in the live game, so none of these blocks it.

## What still stands between this item and close (not the fill)
- `bottle_dirty_off` FAIL 2026-10-15. The harness docstring (`extensions.py` `_drink`) puts it down to the drinker
  walking off the plot, so his clean empty landed off the census. That makes it UNMEASURED, not a mod defect. Re-run it.
- Tank half (`tank_loop_on`/`tank_loop_pour_in`/`tank_loop_off`, `extensions.py:1882`): no live result seen in this pass.
- A2 blood rot: still owner-blocked (no designed fill source for bottled blood).

## Live check that would close the fill question (already passed; re-run only to refresh)
`python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --chains toggle_bottle_loop,toggle_bottle_dirty,bottle_revert`
— the `bottle_loop_on` row PASS, i.e. `RM_Bottle_FreshWater` appears on the plot within 3000 ticks with no order given.
Add the tank chain to the same run to cover the drain half.

## Ledger action owed (not taken: this pass is read-only on rimflow)
Replace the BLOCKED reason on LIQUID_BOTTLE_LOOP_1. The fill now works; what remains is the bottle_dirty_off re-run,
the tank live rows, and the owner's ruling on blood.
