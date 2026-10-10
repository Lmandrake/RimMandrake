# Ollopom outdoor beauty — progress 2026-10-10

## Mechanism (measured, RimSage decompiled 1.6)
- `Need_Beauty.CurrentInstantBeauty` -> `BeautyUtility.AverageBeautyPerceptible(pawn.PositionHeld, map)`: mean of
  `CellBeauty` over the ~250 unfogged cells within 8.9 that are in/adjacent to the pawn's room (`FillBeautyRelevantCells`).
- `BeautyUtility.CellBeauty` sums `Thing.GetBeauty(outdoors)` only for categories passing `BeautyRelevant`
  (Building/Item/Plant/Filth) — **pawns never count**. Outdoors flag = `c.GetRoom(map)?.PsychologicallyOutdoors ?? true`.
- `PawnBeauty` is read only by `ThoughtWorker_Pretty/Ugly` (gated `other.RaceProps.Humanlike`) and
  `PriceUtility.PawnQualityPriceFactor` (+0.2 price factor per point). On an animal: no beauty, +20% market value.

## Design
- `RM_PerceivedBeautyExtension` (beautyOutdoors, default 8; rose = 14) on any creature def.
- Harmony postfix on `BeautyUtility.CellBeauty` (`RM_PerceivedBeautyPatches.cs`): live opted-in pawn on the cell,
  cell psychologically outdoors -> add beautyOutdoors x multiplier. Dedupes via countedThings. Not patched at all if no def opts in.
- Rule in `RM_PerceivedBeautyMath.cs` (pure, selftested). Bridge probe `RM_PerceivedBeautyPatches.Probe(pawnId)`.
- Settings group "Pretty creatures outdoors": `perceivedBeautyEnabled`, `perceivedBeautyMultiplier` (0-300%).
- RSW_Ollopom: PawnBeauty 1 REMOVED (misleading); extension added, `MayRequire="mandrake.rm.biomes"`
  (CreatureBehaviors ships folded into RimMandrake.Biomes; its own packageId never loads at runtime).

## Build/test
- winbuild OK (0 warnings). selftest_sun_heat.py 51/51 incl. new perceived-beauty case.
- validation.py: new `perceived_beauty` chain (ollopom vs muffalo control, on/off arms) + MECHANICS row. Not run live.
- run_selftests: 361/367; 4 FAILs unrelated (hugethings masks, ledger lint, one_path_seam, tool_metadata).

## Deploy
- RimMandrake.Biomes compose: DLL LOCKED by running game, NOT deployed (srchash was written). Redeploy after game exit:
  `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply` then `--mod SWBestiary --apply`.
- SWBestiary RSW_Ollopom.xml was deployed then hand-REVERTED in the game folder to the HEAD copy, so a launch before the
  DLL lands cannot meet an unresolvable modExtension Class.
