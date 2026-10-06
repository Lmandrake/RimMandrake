# Rust Cathedral sheet close — progress 2026-10-05
## Part B ingest
- B1 DONE: decisions stamped ruled (owner typed "rust cathedral sheet done."); `art.py ingest --redo-jobs`: 6 rulings, 0 unresolved. 3 purge refusals: the RM_Vozzik C set is live in Stillsand (`src/RimMandrake/Stillsand/.../RM_Vozzik`), so its purge waits for a replacement there; RSW_Vozzik is a separate def.
- B2 DONE: RM_LivingBolt redo, 3 artpipe jobs (rustcathedral_livingbolt_v1 east/south/north), his note verbatim as owner_note, no facing words. File: rustcathedral_redo_jobs_2026-10-05.json.
- B3 DONE: RSW_Vozzik B installed (east/north/south) in src/RimStarWars/SWBestiary under ruling 87b6d699d0b1cd1502b2.
- B4 DONE: RM_CoolantEelCatch A: nothing to copy, the def's texPath is vanilla Things/Item/Fish/Dogfish, which A is. Ruling recorded.
- B5 DONE: RM_CathedralRoach A kept (already live). drawSize 0.55 -> 0.4 and baseBodySize 0.22 -> 0.15 in RM_ and RUT_ defs (Core Rat: drawSize 1.25, baseBodySize 0.2).
- B6 DONE: RM_LivingBolt drawSize 0.45 -> 0.1 (body and corpse). scale_panel cells = max(adult PawnKindDef lifeStage drawSize), so the sheet will read 0.1.
- B7 DONE: GR_Mecharat cut from RM_RustCathedral and RUT_RustCathedral wildAnimals; About.xml and comments corrected.
- B8 DONE: no wall-crawl/flit mechanism in src/. Filed RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1 (FOUNDRY), not built. Art/size item: RUSTCATHEDRAL_SHEET_ART_REDO_1.
- Pre-existing, untouched: validate_patch flags RM_LivingBoltCorpse texPath missing (placeholder art).
- Sheet rebuild: NOT run (art_sheet.py is another agent's).
