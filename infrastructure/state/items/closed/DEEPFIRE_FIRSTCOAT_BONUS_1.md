## Spec row (verbatim, deepfire_luminous_pigment_spec.md §10 step 7)

| # | build | proof |
|---|---|---|
| 7 | First-coat bonus: quality bump + `RM_StatPart_Deepfire` on Beauty | quicktest: Normal sculpture → Good after one coat, unchanged after the second; Legendary stays Legendary; chair Beauty stat card shows the part line with the right number; remove + reapply does not re-bump |

## What already exists to build on

`CompDeepfire.coats` ships (`DEEPFIRE_PAINT_LIVE_VERIFY_1`, step 5, closed).
It does NOT yet carry a `bonusApplied` flag — add one (Scribed) so
removal-and-reapply cannot farm the bonus, per spec §3.5's own requirement
("Scribed so removal-and-reapply cannot farm it").

## Build (spec §3.5)

- **Art items** (`CompArt` present): on first coat only,
  `CompQuality.SetQuality(q + 1, ArtGenerationContext.Colony)`, capped at
  Legendary (stays Legendary, coat still charged). Stacks split before the
  bump (`AllowStackWith` needs equal quality).
- **Everything else** (walls, furniture, apparel, weapons — floors are
  `DEEPFIRE_FLOOR_PAINT_1`'s own three-way bonus, not this item's):
  `RM_StatPart_Deepfire` on `Beauty` (`StatDef[defName="Beauty"]/parts` XML
  patch) returning `beautyFlat × sizeFactor + beautyPct × baseBeauty` where
  `sizeFactor = min(area, 4)`. Defaults flat 3, pct 25% (not yet Mod
  Settings — `DEEPFIRE_MOD_SETTINGS_1` wires the sliders; ship plain
  constants here, matching step 5's own `DeepfirePaintDefaults` precedent).

## Needs

`bridge` — the quicktest proof above.
