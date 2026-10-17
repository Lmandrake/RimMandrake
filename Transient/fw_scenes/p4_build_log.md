# P4 build log — LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD, then P8 data side (FOUNDRY offline builder, 2026-10-17)

Base: origin/main a54be1db6 (P3 exact-level engine 7b2fbe7a0). No bridge, no game.

## Stage (a) — RM_Volume constants (SquareAreaM2, MetresPerNotch, derived litres), glossary; Python reads C#
- status: DONE
- `RM_Volume`: `SquareAreaM2 = 2`, `CentimetresPerNotch = 50`, `LitresPerNotch` = their product (old names
  `LitresPerLevel`/`MetresPerLevel` alias it), glossary (notch / square / yardstick / level / litres); lakebed thresholds
  in metres (`DeepBedMetres 2`, `AbyssBedMetres 4`).
- Python reads C#: `level_water.METRES_PER_NOTCH`/`SQUARE_AREA_M2`, `pond_pump.UNITS_PER_LEVEL`, `liquid_checks.LEVEL`/
  `UNITS_PER_LITRE`, `selftest_conservation_roundtrip` (via `level_water._volume_const`, which resolves products).
- Tests: SelfTest 496/496 (+`Volume_one_ruler_scheme_A`); level_water, pond_pump, liquid_checks, conservation 13/13 PASS.

## Stage (b) — FillTier by metres of water; labels in metres; LiquidLooks tier map
- status: pending

## Stage (c) — "five" deleted; sourceBudgetMultiplier deleted (+migration); one burn rate; bed settings in metres (cap to 125 m)
- status: pending

## Stage (d) — whole-notch readers re-pointed to dL (pump intake, burn, drowning, heat, mouseover)
- status: pending

## Stage (e) — P8 data side: readout string + limitless mark
- status: pending

## Tests
- pending

## NEXT pointers
- pending
