# Desert gap-fill, 2026-10-04 (BIOME_FLORAFAUNA_ART_REVIEW_1)

Sheet source: `Transient/desert_sittings_plan_2026-10-04.md` (17 no-graphic rows). Queue: priority 10 (default 100, lower claims first), 3 facings each, job ids `desert_gap_<X>_v1_{east,south,north}`. Spec: `Transient/biome_ffar/desert_gapfill_jobs_2026-10-04.json`. ETA about 90 s per job, 21 jobs, roughly 30 to 40 min behind the 3 active.

Result: 17 candidates -> 10 already had art, 7 genuine gaps queued (droids). Note the droids do have a DONOR sprite (greyscale, outlined, tinted by def) in `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/`; the ledger holds it LIVE but the sheet builder did not resolve it. The regens are fresh versions, not replacements.

| row | defName | status | where / job | canon entry |
|---|---|---|---|---|
| DUM Repair Droid | RSW_OuterRim_DUMDroid | QUEUED | desert_gap_DUM_v1_* ; donor: OuterRim/Droid/DUM | droid_dum_pit |
| fx-7 medical droid | RSW_OuterRim_FX7Droid | QUEUED | desert_gap_FX7_v1_* | droid_fx7 |
| GNK Power Droid | RSW_OuterRim_GNKDroid | QUEUED | desert_gap_GNK_v1_* | droid_gnk |
| MSE Repair Droid | RSW_OuterRim_MSEDroid | QUEUED | desert_gap_MSE_v1_* | droid_mse |
| Destroyer Droid | RSW_OuterRim_DestroyerDroid | QUEUED | desert_gap_Destroyer_v1_* | droid_droideka (deployed form) |
| Muckraker Crab Droid | RSW_OuterRim_MuckrakerDroid | QUEUED | desert_gap_Muckraker_v1_* | none exists; brief from donor silhouette only |
| salvage assist droid | RSW_OuterRim_SalvageAssistDroid | QUEUED | desert_gap_SalvageAssist_v1_* | none exists; brief from donor silhouette only |
| terrorworm | RSW_Ashworm | HAD ART | artpipe done/RSW_Ashworm_{east,north,south}, 3 renders each | |
| fuelmite | RSW_Cindermite | HAD ART | artpipe done/RSW_Cindermite_{east,north,south} | |
| creep stern | RSW_Starvine | HAD ART | artpipe done/RSW_Starvine (3 renders), also creepstern_v1 | |
| crimson cushion | RSW_EmberCarpet | HAD ART | done/RSW_EmberCarpet (3), crimsoncushion_v1 | |
| dervish | RSW_Whirlbloom | HAD ART | done/RSW_Whirlbloom (3), dervish_v1 | |
| dessert tree | RSW_SweetbarkTree | HAD ART | done/RSW_SweetbarkTree | |
| hardy grass | RSW_Dunegrass | HAD ART | done/RSW_Dunegrass, hardygrass_v1 | |
| low shrubs | RSW_Plant_ShrubLow | HAD ART | done/shrublow_v1 | |
| ripthorn | RSW_Plant_Ripthorn | HAD ART | done/ripthorn_v1 | |
| rat | RSW_Rat | NOT A ROW | live desert share 0, no RSW_Rat def of ours (donor casting only); vanilla Rat art applies | |

## Roster re-check (frozen `RUT_Desert.xml`, 61 rows) vs assignment
13 inline rows are absent from the assignment JSON; none is a no-art gap:
- Own art on disk: RSW_SurraGrass and RSW_DommoTree (`SWBestiary/Textures/Things/Plant/...`, ledger shows 0 variants, not indexed); RSW_WraidAlpha (shares swanimals/Wraid); RSW_ShadeWhale (shares Horax art); RSW_Bokka (Dessicated_Iguana).
- artpipe renders exist: RM_TruffleMole, RM_GreatDevourer, RM_Groundrunner, RM_MatureFleshbeast, RM_Qorrax, RM_Leachmoss, RSW_Ultracactus, RM_Venomvine variants.
- Caveat: RUT_Desert is FROZEN and superseded by `RM_LongShade`; the sheet's "Desert" is the donor-family set. Whether these 13 belong on the sheet is a sheet-builder decision.
- Nysillin (on sheet, zero picture sets): not queued, left undecided per the plan.
