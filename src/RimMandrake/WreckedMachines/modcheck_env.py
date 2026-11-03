"""modcheck test environment for Wrecked Machines (mandrake.rm.wreckedmachines) -- MODCHECK_DONOR_ENVIRONMENTS_1.

The packageIds `modcheck run WreckedMachines` composes onto the MINIMAL list, read as data (ast, never imported)
by `src/RimMandrake/Utils/modset_builder.py` into TIERS["wreckedmachines"] (`modcheck_closure`). It is the
dependency CLOSURE of this mod's About.xml `<modDependencies>`, resolved from the installed About.xml files on
2026-11-02; `selftest_modcheck_donor_envs.py` re-checks it.

No other Vanilla Expanded mod is needed. The 2026-09-13 wave blamed VFEFactory's auto-process generator for a
`RecipeDefGenerator.SetIngredients` NRE and asked for a bisection of VE siblings. The decompiled prefix
(VanillaFurnitureExpandedFactory_DefGenerator_GenerateImpliedDefs_PreResolve_Patch.GenerateAutoProcesses,
ilspycmd 2026-11-02) reads only vanilla DefOfs and VFEFactory's own InternalDefOf defs, and SetIngredients is
vanilla code run after the prefix. Harmony prints the prefix in the patched frame of the stack trace, which is
why it was blamed. That NRE comes from a def with an unresolved cost, like the MW2-eaten Armoury defs on the same
wave, not from a missing VE sibling. The live clause (infrastructure/state/live_proofs/MODCHECK_DONOR_ENVIRONMENTS_1.txt)
is what proves the list loads clean.
"""

EXTRA_IDS = [
    "mandrake.rm.gimmesomeslack",                   # JawaBench get_defs TypeLoad-fails without it (MEASURED 2026-10-07)
    "oskarpotocki.vanillafactionsexpanded.core",
    "vanillaexpanded.vfefactory",
    "mandrake.rm.wreckedmachines",
]

FORBID = []
