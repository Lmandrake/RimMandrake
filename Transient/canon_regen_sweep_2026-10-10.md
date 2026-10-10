# Canon creature regen sweep 2026-10-10

Owner order 2026-10-10: every canon creature still in the game gets at least one realistic painterly, canon-faithful render. Extends `CANON_CREATURE_REGEN_1` (waves 1-4 sheets); ids `canonregen_<defname>_v1`.

## Method and caveats
- Census = the 120 `kind creature` rows of `design/RimStarWars/canon_references/INDEX.md`; 3 are plants (bloddle, chak_root, tooke_trap_plant) and hubba_gourd is a plant too, so excluded from creature counts. 98 of 120 have a def in `src/`; the rest (fambaa, hawkbat, kinrath, etc.) match by RSW_ prefix; insectomorph, silooth, snoruuk, tauntaun, tibidee, vaapad, wyyyschokk, wampa-class donor names are referenced in rosters/patches but defined in the donor mod. Not checked for Cherry Picker cuts.
- COVERED = a done (output file present, sha not in the art-ledger purge/rejected sets) or pending/active artpipe job whose target/slug matches, with no black-outline clause, citing canon (target_canon, canon_reference, or canon text). This accepts biome-sheet renders (leaningscrub_, miasma_canon_ etc.) as canon-faithful; their per-render Must-show grade is not re-judged here.
- OWED = no such job, or only outline-era (Sept 2026 `canon_*_v1`, retired black-outline house style), purged/rejected, or output file missing from `_artsrc` (unverifiable, treated as owed; mudhorn, womprat, nuna, gizka, insectomorph, dalgo).
- Sanity probes: dewback has 8 name-matched renders and is COVERED; Wookieepedia search probe Mynock/Dewback returned hits.
- Non-library canon names found in rosters/defs: RSW_Screecher (title match "Screecher", not a library entry; unresolved whether it is the SW creature), RSW_FeralNerf (variant of nerf, covered), RSW_OpeeSeaKillerJuv / Faa-Laa-Mee Juv / YobshrimpJuv (juveniles of library species), RSW_StormSando / RSW_ElderSando (variants of sandoaquamonster). No new canon-creature species outside the library were confirmed.

## Totals
- creatures in library: 115; COVERED 92; OWED 23
- jobs filed: 69 (23 creatures x east/south/north), priority 0, ids `canonregen_*_v1`, item CANON_CREATURE_REGEN_1; job spec `Transient/canon_regen_sweep_2026-10-10.jobs.json`.
- wyyyschokk filed with a hand-written prompt (its `## Visual brief` header carries a suffix the filer cannot parse).

| creature | defName | status | evidence |
|---|---|---|---|
| acklay | RSW_Acklay | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| anooba | RSW_Anooba | COVERED | leaningscrub_anooba_v1_east(done), leaningscrub_anooba_v1_north(done) |
| bantha | RSW_Bantha | COVERED | leaningscrub_bantha_v1_east(done), leaningscrub_bantha_v1_north(done) |
| beldon | RSW_Beldon | COVERED | regen_gt_beldon_flying_1_v1_east(done), regen_gt_beldon_flying_1_v1_south(done) |
| blarth | RSW_Blarth | COVERED | miasma_canon_blarth_v1_east(done), miasma_canon_blarth_v1_north(done) |
| blixus | RSW_Blixus | COVERED | miasma_canon_blixus_v1_east(done), miasma_canon_blixus_v1_swim_north(done) |
| bloddle | RSW_Plant_Bloddle | PLANT (excluded) | |
| blurrg | RSW_Blurrg | COVERED | rsw_blurrg_v1_east(done), rsw_blurrg_v2_east(done) |
| bogwing | RSW_Bogwing | COVERED | miasma_canon_bogwing_flying_1_v1_east(done), miasma_canon_bogwing_flying_1_v1_north(done) |
| bolotaur | RSW_Bolotaur | COVERED | longshade_rsw_bolotaur_v1_east(done), longshade_rsw_bolotaur_v1_north(done) |
| boma | RSW_Boma | OWED -> filed | canonregen_*_v1 (jobs seen: 6, none usable) |
| borcatu | RSW_Borcatu | COVERED | enact_wlborcatu_quills_v1_east(done), enact_wlborcatu_quills_v1_south(done) |
| brainworm | RSW_BrainWorm | OWED -> filed | canonregen_*_v1 (jobs seen: 0, none usable) |
| cancell | RSW_CanCell | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| cannok | RSW_Cannok | COVERED | leaningscrub_cannok_v1_east(done), leaningscrub_cannok_v1_north(done) |
| chak_root | RSW_Plant_Chakroot_Wild | PLANT (excluded) | |
| clodhopper | RSW_Clodhopper | COVERED | longshade_rsw_clodhopper_v1_east(done), longshade_rsw_clodhopper_v1_north(done) |
| coloclawfish | RSW_ColoClawFish | OWED -> filed | canonregen_*_v1 (jobs seen: 0, none usable) |
| convor | RSW_Convor | COVERED | leaningscrub_convor_v1_east(done), leaningscrub_convor_v1_north(done) |
| corinathoth | RSW_Corinathoth | COVERED | leaningscrub_corinathoth_v1_east(done), leaningscrub_corinathoth_v1_north(done) |
| dactillion | RSW_Dactillion | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| dalgo | RSW_Dalgo | OWED -> filed | canonregen_*_v1 (jobs seen: 6, none usable) |
| dewback | RSW_Dewback | COVERED | regen_ls_canon_dewback_v1_east(done), regen_ls_canon_dewback_v1_ns_north(done) |
| dianoga | RSW_Dianoga | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| dragonsnake | RSW_Dragonsnake | COVERED | regen_gt_canon_dragonsnake_v1_east(done), regen_gt_canon_dragonsnake_v1_north(done) |
| eopie | RSW_Eopie | COVERED | regen_c17_eopie_v1_east(done), regen_c17_eopie_v1_north(done) |
| faascalefish | RSW_Faa | COVERED | phfix_RSW_FaaCatch_a(done), twilightsea_faa_canon_redo_v1_east(done) |
| falumpaset | RSW_Falumpaset | COVERED | regen_ls_canon_falumpaset_v1_east(done), regen_ls_canon_falumpaset_v1_ns_north(done) |
| fambaa | Fambaa | COVERED | regen_fw_canon_fambaa_v1_east(done), regen_fw_canon_fambaa_v1_north(done) |
| fanback | Fanback | OWED -> filed | canonregen_*_v1 (jobs seen: 6, none usable) |
| gelagrub | RSW_Gelagrub | COVERED | regen_fw_canon_gelagrub_v1_east(done), regen_fw_canon_gelagrub_v1_north(done) |
| gizka | RSW_Gizka | OWED -> filed | canonregen_*_v1 (jobs seen: 14, none usable) |
| gorg | RSW_Gorg | COVERED | longshade_rsw_frilledgorg_v1_east(done), longshade_rsw_frilledgorg_v3_east(done) |
| gornt | RSW_Gornt | COVERED | enact_0ae79c6a_gornt_v1_east(done), enact_0ae79c6a_gornt_v1_north(done) |
| graniteslug | RSW_GraniteSlug | COVERED | stillsand_regen_RSW_GraniteSlug_v2_east(done), stillsand_regen_RSW_GraniteSlug_v2_north(done) |
| grank | Grank | COVERED | regen_ls2_canon_grank_v1_north(done), regen_ls2_canon_grank_v1_south(done) |
| grazer | RSW_FeralGrazer | COVERED | longshade_rsw_feralgrazer_v1_east(done), longshade_rsw_feralgrazer_v1_north(done) |
| greaterkraytdragon | RSW_GreaterKraytDragon | COVERED | stillsand_regen_RSW_GreaterKraytDragon_v2_east(done), stillsand_regen_RSW_GreaterKraytDragon_v2_north(done) |
| gutkurr | RSW_Gutkurr | COVERED | longshade_rsw_gutkurr_v1_east(done), longshade_rsw_gutkurr_v1_north(done) |
| hawkbat | Hawkbat | COVERED | gapbs_RSW_Hawkbat_juv_v1_south(done), hawkbat_fly_master_v1_east(done) |
| horax | Horax | COVERED | longshade_rsw_horax_v1_east(done), longshade_rsw_horax_v1_north(done) |
| hrumph | RSW_Hrumph | COVERED | longshade_rsw_hrumph_v1_east(done), longshade_rsw_hrumph_v1_south(done) |
| hssiss | RSW_Hssiss | COVERED | thesump_Hssiss_v2_east(done), thesump_Hssiss_v2_north(done) |
| hubba_gourd | RSW_Plant_HubbaGourd_Wild | PLANT (excluded) | |
| igitz | RSW_Igitz | COVERED | leaningscrub_igitz_v1_east(done), leaningscrub_igitz_v1_north(done) |
| insectomorph | Insectomorph | OWED -> filed | canonregen_*_v1 (jobs seen: 6, none usable) |
| iriaz | RSW_Iriaz | COVERED | regen_ls3_iriaz_h_v1_east(done), regen_ls3_iriaz_h_v1_north(done) |
| iridonianreek | RSW_IridonianReek | COVERED | longshade_rsw_iridonianreek_v1_east(done), longshade_rsw_iridonianreek_v1_north(done) |
| jakobeast | RSW_Jakobeast | COVERED | longshade_rsw_jakobeast_v1_east(done), longshade_rsw_jakobeast_v1_north(done) |
| jamel | RSW_Jamel | COVERED | longshade_rsw_jamel_v1_east(done), longshade_rsw_jamel_v1_north(done) |
| jerba | RSW_Jerba | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| jimvu | RSW_Jimvu | COVERED | longshade_rsw_jimvu_v1_east(done), longshade_rsw_jimvu_v1_north(done) |
| kinrath | Kinrath | COVERED | kinrath_netcaster_v3_east(done), kinrath_netcaster_v3_north(done) |
| klorslug | RSW_Klorslug | COVERED | regen_gt_canon_klorslug_juv_v1_east(done), regen_gt_canon_klorslug_juv_v1_south(done) |
| kowakianmonkeylizard | RSW_KowakianMonkeyLizard | COVERED | leaningscrub_kowakianmonkeylizard_v1_east(done), leaningscrub_kowakianmonkeylizard_v1_north(done) |
| kraytdragon | RSW_KraytDragon | COVERED | stillsand_regen_RSW_GreaterKraytDragon_v2_east(done), stillsand_regen_RSW_GreaterKraytDragon_v2_north(done) |
| kreetle | Kreetle | COVERED | leaningscrub_kreetle_v1_east(done), leaningscrub_kreetle_v1_south(done) |
| krykna | RSW_Krykna | COVERED | longshade_rsw_krykna_v1_east(done), longshade_rsw_krykna_v1_north(done) |
| kwi | RSW_Kwi | COVERED | longshade_rsw_kwi_v1_east(done), longshade_rsw_kwi_v1_north(done) |
| kybuck | RSW_Kybuck | COVERED | desert_swaca_kybuck_north(done), leaningscrub_kybuck_v1_east(done) |
| laascalefish | RSW_Laa | COVERED | miasma_canon_laajuv_v2_east(done), miasma_canon_laajuv_v2_north(done) |
| lavaflea | RSW_LavaFlea | OWED -> filed | canonregen_*_v1 (jobs seen: 0, none usable) |
| longtailgorg | RSW_LongtailGorg | COVERED | longshade_rsw_longtailgorg_swim_v1_east(done), longshade_rsw_longtailgorg_swim_v1_north(done) |
| lothcat | RSW_Lothcat | COVERED | regen_ls2_canon_lothcat_v1_north(done), regen_ls2_canon_lothcat_v1_south(done) |
| lylek | RSW_Lylek | COVERED | regen_gt_canon_lylek_v1_east(done), regen_gt_canon_lylek_v1_north(done) |
| marshhaunt | RSW_MarshHaunt | COVERED | miasma_canon_marshhaunt_v1_east(done), miasma_canon_marshhaunt_v1_north(done) |
| massiff | RSW_Massiff | COVERED | leaningscrub_massiff_v1_east(done) |
| meescalefish | RSW_Mee | COVERED | phfix_RSW_MeeCatch_a(done), twilightsea_mee_canon_redo_v1_east(done) |
| mott | RSW_Mott | COVERED | regen_gt_canon_mott_f_swim_v1_south(done), regen_gt_canon_mott_f_v1_north(done) |
| mudhorn | RSW_Mudhorn | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| mynock | RSW_Mynock | COVERED | warscar_Mynock_v2_east(done), warscar_Mynock_v2_north(done) |
| neebray | RSW_Neebray | COVERED | cauldronfix_neebray_v2_east(done), cauldronfix_neebray_v2_north(done) |
| nerf | RSW_Nerf | COVERED | leaningscrub_feralnerf_v1_north(done), leaningscrub_feralnerf_v1_south(done) |
| nuna | RSW_Nuna | OWED -> filed | canonregen_*_v1 (jobs seen: 9, none usable) |
| nysillin | RSW_Plant_Nysyllin_Wild | PLANT (excluded) | |
| ollopom | Ollopom | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| opeeseakiller | RSW_OpeeSeaKiller | COVERED | miasma_canon_opeejuv_v1_east(done), miasma_canon_opeejuv_v2_north(done) |
| orray | RSW_Orray | OWED -> filed | canonregen_*_v1 (jobs seen: 8, none usable) |
| paleyobshrimp | RSW_Yobshrimp | COVERED | miasma_canon_yobshrimpjuv_v1_east(done), miasma_canon_yobshrimpjuv_v1_north(done) |
| pekopeko | PekoPeko | COVERED | conflict_pekopeko_m_v2_east(done), conflict_pekopeko_m_v2_north(done) |
| pikobis | RSW_Pikobis | COVERED | leaningscrub_pikobis_v1_east(done), leaningscrub_pikobis_v1_north(done) |
| porg | RSW_Porg | COVERED | leaningscrub_porg_v1_east(done), leaningscrub_porg_v1_north(done) |
| pufferpig | RSW_Pufferpig | COVERED | leaningscrub_pufferpig_v1_east(done), leaningscrub_pufferpig_v1_north(done) |
| qormot | RSW_Qormot | COVERED | leaningscrub_qormot_v1_east(done), ls3_qormot_v1_east(done) |
| ronto | Ronto | COVERED | longshade_rsw_ronto_v1_east(done), ls3_ronto_v1_east(done) |
| runyip | RSW_Runyip | COVERED | longshade_rsw_runyip_v1_east(done), longshade_rsw_runyip_v1_north(done) |
| sandoaquamonster | RSW_SandoAquaMonster | COVERED | scald3_sandoaquamonster_east(done), scald3_sandoaquamonster_north(done) |
| scurrier | RSW_Scurrier | COVERED | desert_swaca_scurrier_south(done), regen_c17_scurrier_v1_east(done) |
| shaaks | RSW_Shaak | COVERED | longshade_rsw_shaak_v1_east(done), longshade_rsw_shaak_v1_north(done) |
| shiro | Shiro | OWED -> filed | canonregen_*_v1 (jobs seen: 6, none usable) |
| shirotrap | RSW_ShiroTrap | COVERED | regen_gt_canon_shirotrap_i_v1_east(done), regen_gt_canon_shirotrap_i_v1_north(done) |
| shyrack | RSW_Shyrack | COVERED | longshade_rsw_shyrack_v1_east(done), longshade_rsw_shyrack_v1_north(done) |
| silooth | Silooth | COVERED | cauldronfix_silooth_v5b_east(done), cauldronfix_silooth_v6_east(done) |
| sith_wyrm | RSW_WarWyrm | COVERED | stillsand_regen_RSW_WarWyrm_v2_east(done), stillsand_regen_RSW_WarWyrm_v2_north(done) |
| skalders | RSW_Skalder | COVERED | longshade_rsw_skalder_v1_south(done) |
| sketto | RSW_Sketto | COVERED | regen_ls_canon_sketto_flying_1_v1_east(done), regen_ls_canon_sketto_flying_1_v1_north(done) |
| snoruuk | Snoruuk | COVERED | gapall_Snoruuk_v1_east(done), gapall_Snoruuk_v1_north(done) |
| strill | RSW_Strill | COVERED | leaningscrub_strill_v2_north(done), leaningscrub_strill_v2_south(done) |
| tauntaun | Tauntaun | COVERED | gapall_Tauntaun_v1_east(done), gapall_Tauntaun_v1_north(done) |
| teemuss | RSW_TeeMuss | COVERED | regen_ls_canon_teemuss_v1_east(done), regen_ls_canon_teemuss_v1_ns_north(done) |
| tibidee | Tibidee | COVERED | gapall_Tibidee_v1_east(done), gapall_Tibidee_v1_north(done) |
| tooke_trap_plant | Plant_TookeTrap_Wild | PLANT (excluded) | |
| urusai | RSW_Urusai | COVERED | desert_swaca_urusai_east(done), leaningscrub_urusai_v1_east(done) |
| uvak | RSW_Uvak | COVERED | longshade_rsw_uvak_v1_east(done), longshade_rsw_uvak_v1_north(done) |
| vaapad | Vapaad | COVERED | bluedesert_Vapaad_v2_east(done), bluedesert_Vapaad_v2_north(done) |
| varactyl | RSW_Varactyl | COVERED | longshade_rsw_varactyl_v1_east(done), longshade_rsw_varactyl_v1_north(done) |
| voorpak | RSW_Voorpak | COVERED | leaningscrub_voorpak_v1_east(done), leaningscrub_voorpak_v1_north(done) |
| vornskyr | Vornskyr | COVERED | miasma_canon_vornskyr_v2_east(done), miasma_canon_vornskyr_v2_north(done) |
| vulptex | RSW_Vulptex | OWED -> filed | canonregen_*_v1 (jobs seen: 6, none usable) |
| wampa | RSW_Wampa | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| whisperbird | Whisperbird | COVERED | regen_ls2_canon_whisperbird_flying_1_v1_east(done), regen_ls2_canon_whisperbird_flying_1_v1_north(done) |
| womprat | RSW_WompRat | OWED -> filed | canonregen_*_v1 (jobs seen: 3, none usable) |
| woolamander | RSW_Woolamander | COVERED | enact_90d52757_woolamander_v1_east(done), enact_90d52757_woolamander_v1_north(done) |
| worrt | RSW_Worrt | COVERED | longshade_rsw_worrt_v1_north(done) |
| wraid | RSW_Wraid | COVERED | longshade_rsw_wraidalpha_v1_east(done), longshade_rsw_wraid_v1_east(done) |
| wyyyschokk | Wyyyschokk | OWED -> filed | canonregen_*_v1 (jobs seen: 4, none usable) |
| yobshrimp | RSW_YobshrimpLand | COVERED | miasma_canon_yobshrimpjuv_v1_east(done), miasma_canon_yobshrimpjuv_v1_north(done) |
| ysalamir | SWPotF_RaceDef_ysalamir | OWED -> filed | canonregen_*_v1 (jobs seen: 0, none usable) |
| zakkeg | Zakkeg | COVERED | miasma_canon_zakkeg_v2_east(done), miasma_canon_zakkeg_v2_north(done) |
| zeer | RSW_Zeer | COVERED | longshade_rsw_zeer_v1_east(done), longshade_rsw_zeer_v1_north(done) |
