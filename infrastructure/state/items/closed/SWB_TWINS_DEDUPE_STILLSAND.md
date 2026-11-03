## scope
RESCOPED to RSW_SandLion -> RM_Vekka only (2026-11-03, per owner ruling LONGSHADE_SHEET_STRUCTURAL_RULINGS_1).

The title's RSW_Vozzik clause is factually wrong. RSW_Vozzik is NOT a twin of RM_Vozzik. On 2026-10-04 (Stillsand sheet) the owner gave them separate homes. RSW_Vozzik went to the Rust Cathedral: *"This should be moved to the Rust Cathedral Biome."* RM_Vozzik went to the Warscar: *"This should go into the Warscar."* Record: `design/Jawa/worldbuilding/biomes/rosters/dune_sea_deep_desert.json` lines 581-588, commit 021c81db2b. Aliasing RSW_Vozzik into RM_Vozzik would merge two creatures he kept apart.

The RSW_Vozzik tier move belongs to `VOLTMAW_TIER_MIGRATE_SPARKS_INCLUDED`: a new RM_ name, CompProperties_InnateAbility in an RM assembly, and an alias. That item takes the InnateAbility clause with it. RSW_Zhakka has no RM twin and stays.

## done (8fc80dc7dc)
- RSW_SandLion def deleted. It is aliased (ThingDef, Corpse_, PawnKindDef) to RM_Vekka.
- The Utinni refs now point at RM_Vekka: RUT_ExtremeDesert, AnimalTolerances and MegafaunaYield.
- donor_name_map now maps AA_SandLion to RM_Vekka.
- Proof: `src/RimStarWars/SWBestiary/selftest_swb_twins_dedupe.py` (needs RM_DATA_ROOT). It asserts RSW_SandLion is defined nowhere, is aliased, and appears in no element or xpath outside the alias file. It also guards that RSW_Vozzik is still defined.

## contract (reissued gen 7)
The contract was reissued with SandLion-only wording and the same proof command, run with `RM_DATA_ROOT` set. The ledger title still names RSW_Vozzik and InnateAbility because rimflow has no retitle verb: a title is set only when the item is filed. Read the title through the scope above. The work is in 8fc80dc7dc.
