## Spec row (verbatim, deepfire_luminous_pigment_spec.md §10 step 9)

| # | build | proof |
|---|---|---|
| 9 | Status engine + thoughts | quicktest with Royalty: titled pawn wearing 2 coats shows `RM_WearingDeepfire` stage 1; a commoner with 2 coats → titled pawn's opinion −15 and the −3 mood; no DLC → only the wearer's thought |

## What already exists to build on

- `StatusGoodExtension`/`SumptuaryUtility` (`SumptuaryEngine.cs`) already
  compute a pawn's display score generically from any def carrying the
  extension (`DEEPFIRE_PAINT_STATUS_CUISINE_1`, closed).
  `RM_WearsAboveStation`/`RM_WearingDeepfireTitled`/`RM_WearingDeepfireCommon`/
  `RM_SawCommonerInDeepfire` thoughts already ship.
- Now that `CompDeepfire` exists (`DEEPFIRE_PAINT_LIVE_VERIFY_1`, step 5,
  closed), add the branch `SumptuaryUtility` needs to read
  `CompDeepfire.coats` directly (spec §4.1: "Deepfire is detected by comp,
  not by extension") — the item that shipped the generic engine explicitly
  deferred this exact branch to here, calling it "a small addition, not a
  redesign."
- `RM_DeepfireBedroom` and `RM_ImpressedByDeepfire` (spec §4.1) still need a
  room-stat hook over painted furniture — not yet built anywhere. This needs
  `DEEPFIRE_FLOOR_PAINT_1`'s floor grid/beauty-hook infrastructure to exist
  first if it counts coated FLOOR tiles toward the room condition; check the
  spec's exact §4.1 wording for whether it is floor-scoped or
  any-coated-furniture-scoped before assuming the dependency.

## Build

Wire the comp-based detection branch into `SumptuaryUtility`'s display-score
computation, then the two still-missing room-stat thoughts. The Royalty-gated
titled-pawn reaction thoughts already exist and should just start firing
once real coated apparel exists to trigger them (step 5 + step 8's worn-item
work make that possible — verify whether this item can close on step 5 alone
via loose worn apparel, or needs step 8's true "worn while equipped" case).

## Needs

`bridge` — the quicktest proof above (Royalty titles, DLC-present/absent).
