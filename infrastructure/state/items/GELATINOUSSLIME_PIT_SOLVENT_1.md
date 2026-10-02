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
3. Campaign: the Rot's finest as an input (the gourmet chain), patched in from `src/RimUtinni/`.

## criteria

- `jawa/get_defs` on each new RecipeDef: `foundCount` matches; live, one toxic input becomes safe output.
