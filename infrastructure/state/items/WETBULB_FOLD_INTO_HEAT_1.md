# WETBULB_FOLD_INTO_HEAT_1 — the Greentide's wet-bulb heat folds into vanilla heat

Decision taken by question card 2026-10-08: fold the wet-bulb mechanic into vanilla heat, per the
one-kind-of-heat ruling (CLAUDE.md "One kind of heat"; `SOLAR_HEAT_EXPOSURE_1`,
`SHADE_GEAR_FAMILY_1`), same shape as `SCALD_FOLD_INTO_HEAT_1`.

## spec

1. **Deleted outright.** GameConditionDef `RM_GreentideWetBulbLock`, HediffDef
   `RM_WetBulbOverwhelm`, StatDef `RM_WetBulbProtection`, C# `RM_GameCondition_WetBulb`,
   `RM_WetBulbExtension`, `RM_MapComponent_DryRooms`, and the Mod Settings toggle
   `wetBulbOverwhelmEnabled`. There is no wet-bulb clock, hediff or protection stat.
2. **Heat.** The Greentide's `RM_SunHeatExtension` heat kind is `ambient`. It raises a pawn's felt
   temperature by `heatOffsetC` 12 C (PROVISIONAL; was 8, the wet-bulb share is folded into it) and
   vanilla Heatstroke does the rest. Ambient kind: shade and roofs do nothing outdoors, an enclosed
   room takes no felt-heat offset, and heat insulation answers it.
3. **Gear.** Vanilla `StuffEffectMultiplierInsulation_Heat` (PROVISIONAL): sealed suit 1.4, wicking
   wrap 0.8, dry-hood 0.5 (old wet-bulb protection 0.6 / 0.3 / 0.2, order kept).
4. **AI scoring.** `RM_Patch_HazardApparelScoring` adds `Insulation_Heat`/40 in place of the
   deleted stat.
5. **Dry-air blower.** No longer dries rooms (that existed only for the wet-bulb clock). It keeps
   plant-growth suppression and the wild-animal repel over its doorway arc; its XML field is now
   `suppressHoldTicks`.
6. **Breaklight.** No longer pauses anything wet-bulb; its +12 C simply adds vanilla heat.
7. **Saves.** A saved wet-bulb hediff (`RUT_` or `RM_WetBulbOverwhelm`) loads as vanilla Heatstroke
   via the alias def.

## criteria

- A1 L0: no def, patch, C# or validation.py in src/ names RM_WetBulbOverwhelm, RM_WetBulbProtection, RM_GreentideWetBulbLock or RM_GameCondition_WetBulb (the alias def's from-names excepted); EnvironmentalHazards, Greentide and Warcasket DLLs rebuild; selftests pass
- A2 L2: on the live full tier, Player.log has no cross-reference or config error naming the deleted defs after deploying (deleted files also gone from the deployed mod folders)
- A3 L2: live, an unprotected colonist outdoors on a Greentide map gains vanilla Heatstroke, and one in an enclosed room does not
- A4 L2: live, the sealed suit raises the wearer's ComfyTemperatureMax by roughly 1.4x the stuff's heat insulation
- H1 L4: the owner judges the 12 C offset and the gear values in a sitting (PROVISIONAL until then)
Answered: the blower's heat push is gone; it is a room cooler that never heats (`BLOWER_ROOM_COOLER_1`).
