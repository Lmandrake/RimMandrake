# WARSCAR_MARK_TRADE_BUILD_1 — the Warscar mark, its lock, its trade and no stacking

Split from `WARSCAR_SNAP_MARK_1` (spec items 3, 4, 5, 7 and the mark settings). Siblings:
`WARSCAR_CHATRAK_SNAP_BUILD_1` (spec 1-2), `WARSCAR_LOOSENED_PANEL_BUILD_1` (spec 6).

## built

- `RM_WarscarMark` (Scarlands/Defs/HediffDefs): the twin's four stages, franchise-free label, tag
  `RM_WarscarMarkFamily`, -0.1/day fade, per-stage pay (HackingSpeed +15/25/35%, ButcheryMechanoidSpeed
  +10/20/30%, SmeltingSpeed +10% from deepening). `RM_WarscarMarkThought` (ThoughtWorker_Hediff, -2/-4/-6).
- The lock is `RM_MapComponent_WarscarMark` in Warscar's own C#, not EnvironmentalHazards'
  `GameCondition_EnvironmentalWeather` the spec named: mandrake.rm.warscar does not depend on that mod.
  Same numbers: 0.0125 per 2,500 ticks (setting `markAccrualPerDay` 0.3 gross), roofed or not, humanlikes.
- Floor: `RM_HediffComp_WarscarMarkFloor` (past 0.5, never under 0.25; setting `markFloorEnabled`).
- No stacking: the lock skips a pawn carrying another family-tagged hediff or `RUT_ScarlandsMark`.
  ⚠️ One-directional: the frozen twin's lock (EnvironmentalHazards) does not yet skip `RM_WarscarMark`.
- Settings `markEnabled`, `markAccrualPerDay`, `markFloorEnabled`, `markTradeBonusesEnabled` (restart);
  the Warscar settings screen now scrolls.
- Chain `warscar_mark` via `RM_WarscarMark.ProofAccrue current|<hours>`.

## verify (live, owed)

- A pawn with eight days on a Warscar map reaches the floor; its stat tooltip lists the trade bonuses.
