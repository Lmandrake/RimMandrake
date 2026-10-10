# CREATURE_BEHAVIORS_CONFIGERRORS_1 — CB-6: CreatureBehaviors: content naming a missing food, item or hediff reports a red error at load via ConfigErrors

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row CB-6 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Add ConfigErrors to the CompProperties / HediffCompProperties / DefModExtension classes that lack it, starting with those resolving defs by string name: RM_CompProperties_VerminBreeder (breedFoodThingDefNames), RM_ParentalEnrageExtension (guardedThingDefNames), RM_CompProperties_DungSeeder, RM_CompProperties_DrumLure. Re-measure the 17-of-63 count first (python over Source/, not grep -c). Report only; never change behaviour.

The row:

| CB-6 | *(code hygiene)* Content that names a missing food, item or hediff should report a red error at load instead of quietly doing nothing. | Add `ConfigErrors` to the property and extension classes that lack it, starting with those that resolve defs by string name. | M | none | CreatureBehaviors | 63 CompProperties/HediffCompProperties/DefModExtension classes, only 17 files define ConfigErrors; e.g. `RM_CompProperties_VerminBreeder` (breedFoodThingDefNames via GetNamedSilentFail), `RM_ParentalEnrageExtension` (guardedThingDefNames), `RM_CompProperties_DungSeeder`, `RM_CompProperties_DrumLure` have none |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: CreatureBehaviors builds; a selftest or validate pass feeds a def naming a missing thing and the class reports exactly one config error; no shipped def newly errors on the full list.
