# THIRST_RULES_BUILD_SALT_OFF_THE_MENU — build progress (BENCH AFK, 2026-10-17)

## Status
slice 1 published; working slice 2 (slime/toxic last resort + effects)

## Slice 1: rule breaks in today's code — DONE `037fbdf94d`
- per-row `useClass` on LiquidDef (generator USE_CLASS table, refuses an unclassified row): Potable fresh/icy/5 coloured;
  BreakOnly salt+brine; LastResort toxic+4 slimes; Never boiling/acid/liquor/tar/propane/chemfuel/lava.
- auto-fill and fill-from-tank take Potable only unless the job is forced (an order).
- every drink search (bottle, tank, terrain, caravan, administer) gates through RM_ThirstMath.MayDrink and ranks
  use class > quality > distance. Salt never outside the break; LastResort only at need 0 (vanilla desperate rule).
- animals: any potable; terrible water only when on the map biome's wild-animal roster, no consequences.
- setting `lastResortDrinking`; selftests Thirst_use_class_gate_ruled, Thirst_autofill_potable_only_in_source;
  validation rows Tu/Ta offline, T11-T14 live (owed).
- pre-existing reds NOT mine: selftest_hose_port P9 (RM_LiquidBath credit site), selftest_review_map (RM_WaterThin.png uncovered).

## Slice 2+: ruled design
pending

## Owed deploys / live rows
pending
