# STICK_FOOD_INGEST_1 — measured ingest scope (BENCH, 2026-09-02)

Survey: research/Jawa/stick_food_mods_survey_2026-09-02.md. Both mods ACTIVE:
- `badoaks.meatonastick` (workshop 3435027361): MEASURED 4 defNames (1 meal
  ThingDef `MeatOnAStick`, 2 recipes, 1 MealSimple patch target), 3 PNGs.
- `badoaks.meatonastick.expansion` (workshop 3577333297): MEASURED 26 defNames
  (7 stick-food ThingDefs incl. meatless/fish/fruit/fungus/veg/blend/little,
  13 recipes incl. x4 bulk, a craftable stick `chrisb_moas_sticks` + its
  recipe, 2 ingredient-category defs, 1 thought `AteMeatlessStick`), 18 PNGs.

⇒ Ingest = ~8 ThingDefs + ~15 recipes reimplemented under RUT_ names inside
the recipe-discovery tree (cui:recipe-discovery ruling), sprites REGENERATED
in-house (no license found — do not copy BadOaks art). Then both retire.
`chrisb_` prefix inside the expansion suggests a third author's stick def is
embedded — check attribution before reusing that name shape.

## criteria
- [ ] All stick foods reachable in our own mod; both badoaks mods retired
      from the full list with a clean cold load; no cast/thought references
      left dangling.
