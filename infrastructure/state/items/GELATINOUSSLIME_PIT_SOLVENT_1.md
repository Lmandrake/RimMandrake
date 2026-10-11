# GELATINOUSSLIME_PIT_SOLVENT_1 — the slime pit renders toxic or indigestible food safe

**Free tier** (+ one campaign recipe). Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 ruled-unbuilt 2, §4 row 0c, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying ruling: sheet `the_slime.md` §7 (*"used to render down an ingredient — the indigestible, the
toxic, the dangerous… the Rot's finest included… The gourmet chain now spans three biomes"*).

## What exists

`RM_SlimePit` (`Defs/ThingDefs_Buildings/SlimeWorks.xml`): one recipe, raw slime → a simple meal. Nothing is
rendered down.

## spec

1. Free: recipes at the pit taking vanilla toxic or indigestible inputs (e.g. toxic-buildup food, insect
   jelly-class oddities, raw items carrying food poisoning risk) and yielding a safe ingredient or meal.
   Pick inputs from the def dump, never guessed defNames.
2. The glurro carcass → salve concentrate recipe lands here or in `GELATINOUSSLIME_GLURRO_SALVE_1`, whichever
   builds first.
3. The Rot's finest as an input (the gourmet chain). **Ruled: option A of
   `design/RimMandrake/pit_solvent_options_20261011.md`, decision taken by question card 2026-10-11** — a luxury
   dish from `RM_AmbrosyxShroom` with its addiction removed, in the FREE tier (both defs ship in
   `mandrake.rm.biomes`; no RimUtinni patch).

## Built (spec 1 `d1cdebec5`; spec 3 2026-10-11)

- `SlimePitSolvent.xml`: `RM_Render_Toxipotato`, `RM_Render_TwistedMeat`, and `RM_Render_Ambrosyx`
  (1.0 nutrition of ambrosyx = 5 shrooms → one `RM_Meal_SlimeAmbrosyx`, Cooking 8, work 800).
  `RM_Meal_SlimeAmbrosyx` inherits Core `MealLavishBase` (MealLavish preferability, AteLavishMeal, rots in 4 d),
  MarketValue 90 (invented). It is no drug: no drugCategory, no `CompProperties_Drug`, no outcomeDoers.
- Ban 4 (`the_rot.md` §6) holds: ambrosyx is a storable plant product (Sellable, Rottable 30 d, no
  live-prep extension or ruin/lifespan comps), not a tea or symbiont.
- Toggle: `PitSolvent.cs` `Recipes` lists all three, so `pitSolvent` covers the new bill.
- Validation: `pit_solvent_defs` (`validation.py` `pit_solvent_findings`) — exact input/product per recipe, the
  dish is no drug, every XML recipe is in the toggle list; live, all recipes + the dish resolve.
  `selftest_slime_suite.py` plants five defects (dish drugCategory / CompProperties_Drug / outcomeDoers, recipe
  dropped from the toggle, wrong input) plus two mock `nodef:` faults; all go red.

## Owed

- Art: render `RM_Meal_SlimeAmbrosyx_v1` queued (artpipe pending); texPath is the vanilla lavish meal until it
  is installed.
- **Supply gap:** no plant yields `RM_AmbrosyxShroom` (MEASURED 2026-10-11 against the live dump: 0 of 491
  plants with a harvestedThingDef). The donor `BMT_AmbrosyxFungus` yields `BMT_AmbrosyxShroom`, not ours. The
  bill is legal but cannot be started until the Rot gets an ambrosyx source.
- Live: bill appears on `RM_SlimePit` and disappears with `pitSolvent` off; one bill turns ambrosyx into the
  dish; a pawn eating it gets no Ambrosia hediff.

## criteria

- `jawa/get_defs` on each new RecipeDef: `foundCount` matches; live, one toxic input becomes safe output.
