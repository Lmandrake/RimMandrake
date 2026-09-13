
## spec
Two mature mods could not join the min16 modcheck environment (2026-09-13
wave, MODCHECK_MATURE_WAVE_1):
1. **Armoury**: on the trimmed list its ModularWeapons2-comp'd defs are
   DISCARDED (missing donor type eats the def) and a surviving
   recipeMaker def then NREs vanilla `RecipeDefGenerator.SetIngredients`
   → RimWorld's corrupted-mods recovery reset. Confirmed by removal
   (16-mod list clean). Its environment needs ModularWeapons2 + the KotOR
   sound donor (kotorsound_* SoundDefs) composed in — find their packageIds
   from the full list.
2. **WreckedMachines**: hard-depends on VanillaExpanded.VFEFactory, but
   VFEFactory ITSELF NREs the same recipe generator on minimal+VE-Core
   (its auto-process generator expects more VE ecosystem than the trimmed
   list has) — first reset of the wave, stack shows its
   GenerateAutoProcesses prefix. Its environment needs whatever VFEFactory
   actually requires (bisect VE siblings from the full list).
Build each mod's composed sub-list, prove it loads (Bridge token, no
recovery reset), then run its suite and record the verify event against
MODCHECK_MATURE_WAVE_1's successor.

## verify
Both mods' suites produce a real verify event on a list that loaded clean.

## criteria
No mature mod is unvalidatable because its test environment was never
composed; the per-mod extra-ids list is recorded next to its validation.py.
