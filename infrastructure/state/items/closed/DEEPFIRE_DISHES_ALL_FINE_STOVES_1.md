# DEEPFIRE_DISHES_ALL_FINE_STOVES_1 — LP-1: deepfire dishes at every fine-meal stove, found at startup

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row LP-1 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| LP-1 | Deepfire dishes can be cooked at **every** stove that makes fine meals, not just the two vanilla stoves — today the Stillsand solar oven makes fine meals but never offers a deepfire dish. Find the benches at startup instead of naming two. | C# change to `ApplyCuisineRecipeVisibility` (bench = any ThingDef whose recipes hold CookMealFine); drop the 2-stove XML patch | S | low | LuminousPigment (Stillsand benefits passively) | `Patches/DeepfireMealsOnStoves.xml` + `LuminousPigmentMod.cs` name only ElectricStove/FueledStove; spec `deepfire_luminous_pigment_spec.md` l.527 says "At any stove"; `Stillsand/Defs/ThingDefs_Buildings/RM_GlassChain_Buildings.xml` RM_SolarOven carries CookMealFine; no item |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
