# SCALD_FOLD_INTO_HEAT_1 — Scald protection folds into vanilla heat protection

Decision taken by question card 2026-10-08 on `SCALD_HEAT_RULING_QUESTION_1`: fold Scald
protection (the `RM_ScaldArmor` armor category and the `RM_ScaldProtection` stat) into vanilla
heat protection, per the one-kind-of-heat ruling (CLAUDE.md "One kind of heat";
`SOLAR_HEAT_EXPOSURE_1`, `SHADE_GEAR_FAMILY_1`).

## spec

A steam burn is an injury, so the vanilla stat that answers it is **`ArmorRating_Heat`**, never
`Insulation_Heat` (that one answers air temperature).

1. **Damage.** `RUT_Scald` (TerminalBiomes DamageDef) takes `armorCategory` **`Heat`**, the vanilla
   category that `Flame` and `Burn` use. `RM_ScaldArmor` (DamageArmorCategoryDef) and
   `RM_ArmorRating_Scald` (StatDef) are deleted, so a steam devil's hit is blocked by the same heat
   armor that blocks fire.
2. **Exposure clock.** `RUT_ScaldExposure`'s `protectionStat` becomes `ArmorRating_Heat`. The comp
   still sums the stat over worn apparel, clamps the sum to 1 and floors the clock at 8%
   (`minDriveFactor`), so Ban 3 still holds and nothing reaches immunity. `RM_ScaldProtection` is
   deleted.
3. **Gear.** Each garment keeps its old clock strength as heat armor: the scald wrap goes to
   `ArmorRating_Heat` 0.45 and the boil-suit to 0.85. That is the larger of the two old stats in
   each case. `VacsuitScaldProtection.xml` is deleted because vanilla already gives the vacsuit and
   its helmet `ArmorRating_Heat` 0.66 each. ⚠️ Consequence: the full vacsuit set now sums past 1
   and sits on the 8% floor, so it beats the boil-suit alone. The old rule that the boil-suit stays
   best does not survive one-kind-of-heat. Any heat-armored gear (devilstrand, marine armor) now
   slows the clock too, and that is the point of the ruling.
4. **AI scoring.** `RM_Patch_HazardApparelScoring` adds `ArmorRating_Heat` to the apparel score in
   place of `RM_ScaldProtection`. The vanilla scorer reads only Sharp/Blunt armor, so a boil-suit
   would otherwise lose the preference that `HAZARD_PROTECTION_STATS_UNSEEN_BY_AI_1` gave it.
5. Unchanged: the wading burn (already vanilla Heat), the roof and still-day gates, native
   immunity, every exposure number.

## criteria

- A1 L0: no def, patch, C# or validation.py in src/ names RM_ScaldArmor, RM_ArmorRating_Scald or RM_ScaldProtection; validate_patch is clean and the selftests pass
- A2 L0: the EnvironmentalHazards DLL rebuilds with ArmorRating_Heat in the apparel scorer
- A3 L2: on the live full tier, Player.log has no cross-reference error naming RM_ScaldArmor, RM_ArmorRating_Scald or RM_ScaldProtection after deploying (the deleted files must also be gone from the deployed mod folder)
- A4 L2: live, a pawn under RUT_ScaldSteam wearing a boil-suit gains RUT_ScaldExposure at about 15% of the unprotected rate, read off hediff severity
- A5 L2: live, a RUT_Scald hit on a pawn in heat armor shows heat-armor deflection, read off the combat log or the damage result
