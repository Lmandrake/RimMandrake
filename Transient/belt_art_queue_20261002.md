# BELT art queue 2026-10-02
Source: Transient/belt_art_census_20261002.md NEEDS_REGEN (51 rows) + TOLLUK_CAP_ART_REGEN_1. Filed with fill_queue.py (no reference=), 24 subjects = 34 job files, 3 batches (14 / 13 / 7). Job lists: scratchpad b1/b2/b3.json.

## Skipped
- 9 `_Flying_` flip-book rows (Uvak, Porg, 5 PustuleHornet variants, SmogMoth, Sacapillar): optional.
- Art found already (artpipe done/ or src Textures): RUT_YearningFruitHarvested (rutyearningfruit_v1), RUT_Fuzz (rutfuzz_v1), RUT_GreentideAntSoldier (rut_greentideant_body_*), RSW_RawBloddle/Chakroot/HubbaGourd/Nysyllin (*_v1), RSW_Ikee (RM_Ikee_*), RM_AblationEmergence (RM_AblationSilhouette), RM_IlbareenDead (miasma_ilbareen_dead), RUT_AncientShieldedTurret_Gun, RM_SolarOvenCrest (RM_SolarOven); on disk already: RM_RawDorvel/RawSkelver/KorvethPitch, RUT_AncientSpacerAutocannon_Gun, RM_LensGlass.
- Design call: RUT_GreentideAntCarapaceWall (linked-atlas building; needs atlas spec).
- RM_SweetlineWool + RUT_SweetlineWool: one render (rut_sweetlinewool_v1) serves both.

## Queued (id -> def)
Batch 1 (14): rut_dyingcreep_v1, rut_deadcreep_v1, rut_metalsaltbezoar_v1, rut_sweetlinewool_v1, rsw_surragrass_v1, rsw_dommotree_v1, rm_coldwax_v1, rm_deltasalt_v1, rm_deltasilt_v1, rm_cindercrust_v1 (item FORGE_MISSING_ART_1), rm_finesand_v1, rm_greatbolehardwood_v1, rut_filth_mousetrack_v1, glyph_bloodfeeding_v2 (refile of failed glyph_bloodfeeding, a rate-meter failure).
Batch 2 (13): rut_dryairblower_v1, rm_oasismaker_v1, rut_beastbulge_v1, rut_moatfusepost_v1, rut_ventsmelter_v1/ventforge_v1/ventkiln_v1 each east+south+north.
Batch 3 (7): rsw_zhakka_v1 and rut_livingbolt_v1 (east+south+north each), rot_agarilux_v3 (tolluk cap; item TOLLUK_CAP_ART_REGEN_1; target "rot_agarilux" so only it is replaced; current Agarilux_A.png untouched as interim).
Other items: ART_PIPELINE_DAEMON_1. Canon_references: none of these subjects has an entry.

## Daemon
rm-artpiped running, 3 workers; it was also busy with other work (RM_Fexxil, Harrovaq, ...), so these sit in the queue behind it. Batch 1 pickup confirmed (pending -> active). Finished art is NOT wired.
