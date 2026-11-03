
## spec
Two mature mods could not join the min16 modcheck environment (2026-09-13
wave, MODCHECK_MATURE_WAVE_1):
1. **Armoury**: on the trimmed list its ModularWeapons2-comp'd defs are
   DISCARDED (missing donor type eats the def) and a surviving
   recipeMaker def then NREs vanilla `RecipeDefGenerator.SetIngredients`
   → RimWorld's corrupted-mods recovery reset. Confirmed by removal
   (16-mod list clean). Since then MW2 was cut (ARMOURY_MW2_CUT_1) and the
   KotOR sound donor absorbed (WEAPONS_DONOR_RETIREMENT_1), so neither is
   composed in; the environment is the closure of Armoury's own
   modDependencies (src/RimStarWars/Armoury/modcheck_env.py).
2. **WreckedMachines**: hard-depends on VanillaExpanded.VFEFactory. The
   wave's first reset was a vanilla `RecipeDefGenerator.SetIngredients` NRE
   whose stack listed VFEFactory's GenerateAutoProcesses prefix; the
   decompiled prefix (2026-11-02) reads only vanilla and VFEFactory's own
   defs, so no VE sibling is required. The environment is VFEFactory + VE
   Framework (src/RimMandrake/WreckedMachines/modcheck_env.py); the live
   clause A2 proves it loads clean.
Build each mod's composed sub-list, prove it loads (Bridge token, no
recovery reset), then run its suite and record the verify event against
MODCHECK_MATURE_WAVE_1's successor.

## verify
Both mods' suites produce a real verify event on a list that loaded clean.

## criteria
No mature mod is unvalidatable because its test environment was never
composed; the per-mod extra-ids list is recorded next to its validation.py.
