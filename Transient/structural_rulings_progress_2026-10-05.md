# LONGSHADE_SHEET_STRUCTURAL_RULINGS_1 progress (2026-10-05)

Sources: Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json (Long Shade), deep_desert_sheet_2026-10-04.decisions.json (Stillsand).

## Calls
- CALL: "our custom extreme desert biome" = the Stillsand (RM_Stillsand, mandrake.rm.stillsand). evidence: biome_mod_architecture.md §1 row 1 maps RUT_ExtremeDesert -> the Stillsand; design/validation_walks/RimMandrake/Stillsand.md status-hint "the Extreme Desert biome". No other RM biome describes itself as the extreme desert.
- CALL: "the biome with all the Fuzz (Leaning?)" = RM_LeaningScrub. evidence: RM_LeaningScrub_Biome.xml casts RM_Fuzzrunner 1.0 + RM_Fuzzviper 0.3 and RM_Fuzz flora.
- CALL: RM_Ultracactus is NOT cut — it is the existing RM twin and becomes the Ultriss Pad; RSW_Ultracactus is the twin retired.
- CALL: tier move where an RM_ twin exists = RM_ def stays the one cast; RSW_ def deleted from SWBestiary; RUT_ twin biomes (RUT_Desert/RUT_ExtremeDesert, still carried by the save) recast onto the RM_ def (MayRequire mandrake.rm.biomes) rather than left empty. RSW texture files are left on disk (not purged): the owner kept several of them on the sheet, and purge is an owner rejection.

## Units
- Khorrak tier move: DONE — RUT_Desert recast RSW_Khorrak -> RM_Khorrak; RSW_Khorrak def KEPT UNCAST (sole carrier of C# CompMetalEater + its validation proof; deleting would silently kill a built mechanic). Follow-up: port steel diet to RM or rule it dropped.
