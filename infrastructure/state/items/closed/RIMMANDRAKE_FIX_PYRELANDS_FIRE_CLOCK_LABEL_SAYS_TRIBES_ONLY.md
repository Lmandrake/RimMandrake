# RIMMANDRAKE_FIX_PYRELANDS_FIRE_CLOCK_LABEL_SAYS_TRIBES_ONLY

## spec
Pyrelands 0.1.0 (the biome alone) Problem found 2026-11-13 [measured by reading source]: the setting
`RM_PyrelandsSettings.fireClockEnabled` is labelled "Fire clock (flame harvest / fire raid / fire rite)" with tooltip
"Off: those incidents never fire" (`src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:508`). It also gates the biome's own
scheduled fronts and the opening "yesterday fire" (`PyrelandsFireFront.cs:101,215`), which are 0.1.0 bars. A player turning off
the Tribes would lose the biome's burn. Fix the label and tooltip to say it stops the biome's own fires too (or split the
switch; builder's choice, say which). Acceptance: label/tooltip text names the biome fires; selftest_settings_screens green.
The Tribes themselves are out of scope: by card 2026-11-13 ~9:30 PM, "Own mod, own version, later" (see
RIMMANDRAKE_ADOPT_MOD_DESIGN_VERSIONS_SO_JUDGE_CAN_PASS).
