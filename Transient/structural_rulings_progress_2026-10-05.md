# LONGSHADE_SHEET_STRUCTURAL_RULINGS_1 progress (2026-10-05)

Sources: Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json (Long Shade), deep_desert_sheet_2026-10-04.decisions.json (Stillsand).

## Calls
- CALL: "our custom extreme desert biome" = the Stillsand (RM_Stillsand, mandrake.rm.stillsand). evidence: biome_mod_architecture.md §1 row 1 maps RUT_ExtremeDesert -> the Stillsand; design/validation_walks/RimMandrake/Stillsand.md status-hint "the Extreme Desert biome". No other RM biome describes itself as the extreme desert.
- CALL: "the biome with all the Fuzz (Leaning?)" = RM_LeaningScrub. evidence: RM_LeaningScrub_Biome.xml casts RM_Fuzzrunner 1.0 + RM_Fuzzviper 0.3 and RM_Fuzz flora.
- CALL: RM_Ultracactus is NOT cut — it is the existing RM twin and becomes the Ultriss Pad; RSW_Ultracactus is the twin retired.
- CALL: tier move where an RM_ twin exists = RM_ def stays the one cast; RSW_ def deleted from SWBestiary; RUT_ twin biomes (RUT_Desert/RUT_ExtremeDesert, still carried by the save) recast onto the RM_ def (MayRequire mandrake.rm.biomes) rather than left empty. RSW texture files are left on disk (not purged): the owner kept several of them on the sheet, and purge is an owner rejection.

## Units
- Khorrak tier move: DONE — RUT_Desert recast RSW_Khorrak -> RM_Khorrak; RSW_Khorrak def KEPT UNCAST (sole carrier of C# CompMetalEater + its validation proof; deleting would silently kill a built mechanic). Follow-up: port steel diet to RM or rule it dropped.
- Drazzik tier move: DONE — RSW_Drazzik.xml + RSW_Nizzek.xml deleted (RM_Drazzik/RM_Nizzek/eggs are full copies incl. drum-lure + egg-trap comps); RUT_ExtremeDesert recast to RM_Drazzik; roster json def updated. Art: RM_Drazzik keeps its own art (owner picked A = IN GAME Stillsand); RSW textures left on disk.
- Rename JOE_Landopus -> Thraia: DONE (label+plural+description from owner's note). defName KEPT JOE_Landopus — save-safety: cast in RUT_Desert, the saved planet's biome.
- CALL (art for cuts): texture PNGs of cut creatures are LEFT on disk, unreferenced. evidence: the art ledger requires a `retire` event for any Textures deletion (block_unledgered_texture.py / pre-push guard), and art.py exposes no retire verb; `purge` is an owner REJECTION of a picture and is refused for a picture live in a mod. Cleanup owed once a retire verb exists.
- CUT Kudda: DONE — RM_Kudda (+ its RM_CactusHide/RM_CactusMeat, used by nothing else) and RSW_Kudda deleted; rows removed from RM_LongShade, RUT_Desert, RUT_ExtremeDesert; desert.json fauna row -> evictions cut:. RSW_CactusHide/Meat kept (RSW_Chikka/RSW_Skorra still use them).
- CUT MatureFleshbeast: DONE — RM_MatureFleshbeast (+RM_MatureFleshbeastBody, RM_JellyfishTentacle) and RSW_MatureFleshbeast.xml (+RSW_TentacledQuadrupedEyeless, RSW_JellyfishTentacle) deleted; rows out of RM_LongShade + RUT_Desert; desert.json AA_MatureFleshbeast -> cut:. Note: 3 artpipe jobs may still be queued for RM_MatureFleshbeast.
- CUT Ossik: DONE — RM_Ossik (+RM_EggOssik*) and RSW_Ossik (+RSW_SandstriderEgg*) deleted; rows out of RM_LongShade + RUT_Desert; desert.json AA_DesertAve -> cut:.
