# Art daemon failure triage, 2026-10-05

Window: failed manifests modified in the last 24h (171 total: master_failed 59, worker_error 54, failed_canon 43, bad_job_file 15). State dir `D:\Luke\dev\_artpipe`.

## Causes

- **worker_error (all 54): codex `response-schema channel mismatch`.** The worker exits 1 with notes like 'Cannot call imagegen after response-schema channel mismatch' / 'tool invocation unavailable due mistaken schema response'; no image, ~8k tokens. Intermittent (about 3-6 per hour at all hours), not auth (the refresh-token errors in failed/ date from 09-16 and 09-26). The daemon's 2 attempts do not clear it. Requeueing as-is works.
- **master_failed (59) is a cascade.** One failed east master permanently fails its north and south siblings; nothing requeues them when the master is requeued. Roughly 35 of these trace to a worker_error master (recoverable), the rest to failed_canon masters.
- **bad_job_file (15):** the phrase 'all three facings' in the Vrekka prompt (`common._FACING_CONTRADICTIONS`). The other 12 (Landopus, Dakkra, Gennok, Gloomcast, scaldwalker) were already fixed and requeued by another pass before this triage.
- **failed_canon (43):** every one already had the daemon's in-claim corrected retry (`canon_retry`, two renders), so none is requeued. 35 are in scope and left failed; they can still go on a sheet. Concentrated in `longshade_rsw_*` creature masters (Gorg, FrilledGorg, Bantha, Sketto, Teemuss, Voorpak, Nerf, Falumpaset, Dewback) and `stillsand_regen_*` swimming sets.

## Requeued (moved failed/ to pending/, manifest parked in `_requeued_manifests/`)

- bad_job_file, prompt fixed ('Same individual in all three facings.' replaced by 'Same individual as its sibling views.'; also fixed in `Transient/biome_ffar/longshade_rm_regen_jobs_2026-10-04.json`, 7 places): 3
- worker_error, as-is: 24
- master_failed, master is requeued or already done (derive_from waits for the master verdict, `artpiped._derive_master_resolved`): 34

Every move:

- bad_job_file: `ls_regen_RM_Vrekka_v1_east`
- bad_job_file: `ls_regen_RM_Vrekka_v1_north`
- bad_job_file: `ls_regen_RM_Vrekka_v1_south`
- worker_error: `bluedesert_AA_Thunderbeast_v1_east`
- worker_error: `bluedesert_Ossivel_v2_east`
- worker_error: `bluedesert_Thunderbeast_v2_north`
- worker_error: `desert_gap_DUM_v1_south`
- worker_error: `desert_gap_Destroyer_v1_north`
- worker_error: `desert_gap_Muckraker_v1_north`
- worker_error: `desert_gap_SalvageAssist_v1_east`
- worker_error: `longshade_rsw_frilledgorg_v1_south`
- worker_error: `longshade_rsw_jakobeast_v1_east`
- worker_error: `longshade_rsw_runyip_v1_north`
- worker_error: `longshade_rsw_vellarabloom_v2`
- worker_error: `longshade_rsw_wraidalpha_v1_east`
- worker_error: `ls_regen_RM_Dewfringe_c_v1`
- worker_error: `ls_regen_RM_Gloomcast_v1_north`
- worker_error: `ls_regen_RM_Leachmoss_v1`
- worker_error: `ls_regen_RM_Pavecrust_e_v1`
- worker_error: `stillsand_regen_RM_Oommok_v2_east`
- worker_error: `stillsand_regen_RM_Soorrak_v2_north`
- worker_error: `stillsand_regen_RSW_Ollim_v1`
- worker_error: `stillsand_regen_RSW_Plant_Bloddle_var4`
- worker_error: `stillsand_regen_RSW_Scurrier_v2_north`
- worker_error: `twilightsea_niim_v2_south`
- worker_error: `twilightsea_oobo_v2_east`
- worker_error: `twilightsea_tikkarr_v2_east`
- master_failed: `bluedesert_AA_Thunderbeast_v1_north`
- master_failed: `bluedesert_AA_Thunderbeast_v1_south`
- master_failed: `bluedesert_Ossivel_v2_north`
- master_failed: `bluedesert_Ossivel_v2_south`
- master_failed: `bluedesert_Thunderbeast_v3_north`
- master_failed: `bluedesert_Thunderbeast_v3_south`
- master_failed: `desert_gap_SalvageAssist_v1_north`
- master_failed: `desert_gap_SalvageAssist_v1_south`
- master_failed: `longshade_rsw_frilledgorg_v6_north`
- master_failed: `longshade_rsw_frilledgorg_v6_south`
- master_failed: `longshade_rsw_gorg_swim_v1_north`
- master_failed: `longshade_rsw_gorg_swim_v1_south`
- master_failed: `longshade_rsw_gorg_v2_north`
- master_failed: `longshade_rsw_gorg_v2_south`
- master_failed: `longshade_rsw_jakobeast_v1_north`
- master_failed: `longshade_rsw_jakobeast_v1_south`
- master_failed: `longshade_rsw_ronto_v1_north`
- master_failed: `longshade_rsw_ronto_v1_south`
- master_failed: `longshade_rsw_ulgga_v1_north`
- master_failed: `longshade_rsw_ulgga_v1_south`
- master_failed: `longshade_rsw_wraidalpha_v1_north`
- master_failed: `longshade_rsw_wraidalpha_v1_south`
- master_failed: `ls_regen_JOE_Landopus_swim_v1_north`
- master_failed: `ls_regen_JOE_Landopus_swim_v1_south`
- master_failed: `ls_regen_JOE_Landopus_v1_north`
- master_failed: `ls_regen_JOE_Landopus_v1_south`
- master_failed: `ls_regen_RM_Dakkra_down_v1_north`
- master_failed: `ls_regen_RM_Dakkra_down_v1_south`
- master_failed: `ls_regen_RM_Dakkra_rest_v1_north`
- master_failed: `ls_regen_RM_Dakkra_rest_v1_south`
- master_failed: `twilightsea_oobo_v2_north`
- master_failed: `twilightsea_oobo_v2_south`
- master_failed: `twilightsea_tikkarr_v2_north`
- master_failed: `twilightsea_tikkarr_v2_south`

## Left failed

### failed_canon after its in-claim retry (not requeued; owner may look)

- `abyss_glowinggrass_b_v1`
- `longshade_rsw_bantha_v4_north`
- `longshade_rsw_dewback_v1_east`
- `longshade_rsw_eopie_v1_south`
- `longshade_rsw_falumpaset_v1_east`
- `longshade_rsw_frilledgorg_v1_north`
- `longshade_rsw_frilledgorg_v2_east`
- `longshade_rsw_frilledgorg_v4_south`
- `longshade_rsw_frilledgorg_v5_east`
- `longshade_rsw_gorg_v1_north`
- `longshade_rsw_gorg_v4_north`
- `longshade_rsw_gorg_v4_south`
- `longshade_rsw_gorg_v5_east`
- `longshade_rsw_gorg_v6_north`
- `longshade_rsw_gorg_v6_south`
- `longshade_rsw_hrumph_v1_north`
- `longshade_rsw_longtailgorg_swim_v1_south`
- `longshade_rsw_longtailgorg_v4_north`
- `longshade_rsw_nerf_v1_east`
- `longshade_rsw_sketto_v1_east`
- `longshade_rsw_teemuss_v1_east`
- `longshade_rsw_uvak_v1_south`
- `longshade_rsw_voorpak_v1_east`
- `longshade_rsw_wraid_v1_south`
- `ls_regen_RM_Dewfringe_e_v1`
- `stillsand_regen_RM_Drazzik_swimming_v1_north`
- `stillsand_regen_RM_Drazzik_swimming_v1_south`
- `stillsand_regen_RM_Duumma_corpse_v1_north`
- `stillsand_regen_RM_Duumma_corpse_v1_south`
- `stillsand_regen_RM_Glasscrust_var2`
- `stillsand_regen_RM_Glasscrust_var5`
- `stillsand_regen_RM_Qorrax_swimming_v1_east`
- `stillsand_regen_RM_Qorrax_swimming_v1_north`
- `stillsand_regen_RM_Qorrax_swimming_v1_south`
- `stillsand_regen_RSW_KraytDragon_v2_east`

### master_failed whose master failed canon (cannot land until the master does)

- `longshade_rsw_dewback_v1_north`  (master longshade_rsw_dewback_v1_east)
- `longshade_rsw_dewback_v1_south`  (master longshade_rsw_dewback_v1_east)
- `longshade_rsw_falumpaset_v1_north`  (master longshade_rsw_falumpaset_v1_east)
- `longshade_rsw_falumpaset_v1_south`  (master longshade_rsw_falumpaset_v1_east)
- `longshade_rsw_frilledgorg_v2_north`  (master longshade_rsw_frilledgorg_v2_east)
- `longshade_rsw_frilledgorg_v2_south`  (master longshade_rsw_frilledgorg_v2_east)
- `longshade_rsw_frilledgorg_v5_north`  (master longshade_rsw_frilledgorg_v5_east)
- `longshade_rsw_frilledgorg_v5_south`  (master longshade_rsw_frilledgorg_v5_east)
- `longshade_rsw_gorg_v5_north`  (master longshade_rsw_gorg_v5_east)
- `longshade_rsw_gorg_v5_south`  (master longshade_rsw_gorg_v5_east)
- `longshade_rsw_nerf_v1_north`  (master longshade_rsw_nerf_v1_east)
- `longshade_rsw_nerf_v1_south`  (master longshade_rsw_nerf_v1_east)
- `longshade_rsw_sketto_v1_north`  (master longshade_rsw_sketto_v1_east)
- `longshade_rsw_sketto_v1_south`  (master longshade_rsw_sketto_v1_east)
- `longshade_rsw_teemuss_v1_north`  (master longshade_rsw_teemuss_v1_east)
- `longshade_rsw_teemuss_v1_south`  (master longshade_rsw_teemuss_v1_east)
- `longshade_rsw_voorpak_v1_north`  (master longshade_rsw_voorpak_v1_east)
- `longshade_rsw_voorpak_v1_south`  (master longshade_rsw_voorpak_v1_east)
- `stillsand_regen_RSW_KraytDragon_v2_north`  (master stillsand_regen_RSW_KraytDragon_v2_east)
- `stillsand_regen_RSW_KraytDragon_v2_south`  (master stillsand_regen_RSW_KraytDragon_v2_east)

### Out of scope, untouched (not in the current review sets)

- `RSW_Junk_AncientJetEngine_04_v2`
- `RSW_Junk_AncientMegaCannonTripod_04_v2`
- `RSW_Junk_AncientMegaCannonTripod_05_v2`
- `RSW_Junk_AncientPodCar_07_v2`
- `RSW_Junk_AncientRustedCarFrame_04_v2`
- `RSW_Junk_AncientRustedCarFrame_05_v2`
- `RSW_Junk_AncientRustedCar_08_v2`
- `RSW_Junk_AncientRustedDropship_06_v2`
- `RSW_Junk_AncientRustedJeep_05_v2`
- `RSW_Junk_AncientWarspiderRemains_07_v2`
- `RSW_Junk_AncientWarwalkerFoot_02_v2`
- `RSW_Junk_AncientWarwalkerLeg_04_v2`
- `RSW_Junk_AncientWheel_07_v2`
- `doubles_redo_bantha_wj_v1_east`
- `doubles_redo_bantha_wj_v1_north`
- `doubles_redo_bantha_wj_v1_south`
- `messyconduit_bracket_modern_v1_east`
- `messyconduit_bracket_modern_v1_north`
- `messyconduit_bracket_modern_v1_south`
- `scaldwalker_v2_east`
- `scaldwalker_v2_north`
- `scaldwalker_v2_south`

### Skipped because already done or queued

- `RM_Lisqueth_var1`
- `RM_Vhaulk_v3_east`
- `bluedesert_Dovvik_v2_north`
- `bluedesert_Ossivel_v3_south`
- `bluedesert_Thunderbeast_v2_south`
- `bluedesert_Vrisk_v2_east`
- `bluedesert_Vrisk_v2_north`
- `bluedesert_Vrisk_v2_south`
- `desert_gap_Destroyer_v1_south`
- `longshade_rsw_bantha_v1_south`
- `longshade_rsw_bantha_v2_north`
- `longshade_rsw_bantha_v3_north`
- `longshade_rsw_bantha_v3_south`
- `longshade_rsw_bolotaur_v1_north`
- `longshade_rsw_bolotaur_v1_south`
- `longshade_rsw_frilledgorg_v6_east`
- `longshade_rsw_gorg_swim_v1_east`
- `longshade_rsw_gorg_v2_east`
- `longshade_rsw_gorg_v3_south`
- `longshade_rsw_hrumph_v1_south`
- `longshade_rsw_iridonianreek_v1_north`
- `longshade_rsw_ronto_v1_east`
- `longshade_rsw_skalder_v1_south`
- `longshade_rsw_ulgga_v1_east`
- `ls_regen_JOE_Landopus_swim_v1_east`
- `ls_regen_JOE_Landopus_v1_east`
- `ls_regen_RM_Dakkra_down_v1_east`
- `ls_regen_RM_Dakkra_rest_v1_east`
- `ls_regen_RM_Gennok_v1_east`
- `ls_regen_RM_Gennok_v1_north`
- `ls_regen_RM_Gennok_v1_south`
- `ls_regen_RM_Gloomcast_v1_east`
- `ls_regen_RM_Gloomcast_v1_south`

No job appeared in a `*.decisions.json` file, so none was withheld for an owner ruling. The canon gate was not touched.
