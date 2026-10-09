# HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1 — EH-5: hazard code reads tar terrains from FlowWorks liquid defs, not literals

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row EH-5 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| EH-5 | **Generic hazard code stops hard-coding campaign terrain (hygiene).** The tar beast, the tar-pit belch and the Sump living map name `"RM_TarDeep"`/`"RM_TarShallow"` as literal strings. Read the tar terrains from FlowWorks' `RM_Liquid_Tar` entry, or from a def field, so a second tar liquid or a renamed terrain cannot silently break them. | small refactor | S | low | EnvironmentalHazards, FlowWorks (read-only) | `RM_CompTarBeast.cs:140`, `RUT_IncidentWorker_TarPitBelch.cs:98`, `RM_MapComponent_SumpLivingMap.cs:96`; `FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:324` already maps tar to `RM_TarShallow` |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
