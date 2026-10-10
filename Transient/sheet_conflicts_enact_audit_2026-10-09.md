# Sheet conflicts enact audit 2026-10-09

Rows audited: 66 of 66; PASS 66, FAIL 0

| id | kind | choice | expected | evidence | result |
|---|---|---|---|---|---|
| RM_Abyss/Night Mule/del | del | B click | del:B | a25f9 gone from src; turret png sha 649c6108 == RUT_AncientShieldedTurret_v2 render; in row purge + ledger purge; def RUT_AncientSecurityAndUtility.xml:50 texPath Things/Building/Ancient/RUT_AncientShieldedTurret | PASS |
| RM_Abyss/Aveluthia/del | del | B click | del:B | same as Night Mule (shared turret sha) | PASS |
| RM_BlueDesert/Vhaulk/del | del | B click | del:B | same as Night Mule (shared turret sha) | PASS |
| RM_Greentide/Fambaa/del | del | B click | del:B | 3 shas not live, in row purge, ledger purge each | PASS |
| RM_Greentide/Gelagrub/del | del | B click | del:B | 3 shas not live, in row purge, ledger purge each | PASS |
| RM_Greentide/Mott/del | del | B click | del:B | 3 shas not live, in row purge, ledger purge each | PASS |
| RM_Greentide/Hawkbat/del | del | B click | del:B | f3d9,66bc gone+ledger purge; Hawkbat_j_east/south == regen_gt_canon_hawkbat_juv_v1 renders (4f305f11,121ba8b4); j_north 0a1878e6 still live (row purge only) allowed; job regen_gt_canon_hawkbat_juv_v2_north now in done/; def RSW_Hawkbat.xml:213 texPath swanimals/Hawkbat/Hawkbat_j | PASS |
| RM_Greentide/Peko Peko/del | del | B click | del:B | m_{east,north,south} (6e10195a,bc1c95fc,b64f05d7) still live, allowed pending; jobs conflict_pekopeko_m_v2_east/north in done/, _south in failed/ (not yet installed, south render may be missing); def RSW_PekoPeko.xml:214 texPath swanimals/PekoPeko/PekoPeko_m | PASS |
| RM_TheScald/Noohm/del | del | B click | del:B | 92592a78 not live, row purge+ledger purge;  | PASS |
| RM_TheScald/Shulla/del | del | B click | del:B | 92592a78 not live, row purge+ledger purge;  | PASS |
| RM_TwilightSea/Loohn/del | del | B click | del:B | 92592a78 not live, row purge+ledger purge | PASS |
| RM_TwilightSea/Noolim/del | del | B click | del:B | 92592a78 not live, row purge+ledger purge | PASS |
| RM_TwilightSea/Weloon/del | del | B click | del:B | 92592a78 not live, row purge+ledger purge | PASS |
| RM_TwilightSea/Hollu/del | del | B click | del:B | 3 shas gone+ledger purge; RM_Hollu_{e,n,s} == twilightsea_hollu_redo_v3 renders; RM_TwilightSeaFloorLife.xml:469 texPath Things/Pawn/Animal/RM_Hollu/RM_Hollu | PASS |
| RM_TwilightSea/Lunoowa/del | del | B click | del:B | 4 shas gone+ledger purge; RM_Lunoowa_{e,n,s} == twilightsea_lunoowa_redo_v1 renders; RM_TwilightSeaFauna.xml:370 texPath | PASS |
| RM_Stillsand/Vozzik/del | del | A default | del:A | 3 lines: files on disk w/ named sha, none in row purge; conflictSheet=[('A', 'default')] purge=0 | PASS |
| RM_RustCathedral/Vozzik/del | del | A default | del:A | 3 lines: files on disk w/ named sha, none in row purge; conflictSheet=[('A', 'default')] purge=0 | PASS |
| RM_Greentide/Diggerpede/del | del | A default | del:A | 6 lines: files on disk w/ named sha, none in row purge; conflictSheet=[('A', 'default')] purge=0 | PASS |
| RM_TheSump/Dredgel/del | del | A default | del:A | 1 lines: files on disk w/ named sha, none in row purge; conflictSheet=[('A', 'default')] purge=2 | PASS |
| RM_Abyss/Nightling/amb | amb | A click | amb:A | RM_Sesserith_{e,n,s} == abyss_sesserith_v3 renders (16cafa5c,5e587c3b,bdb434d1); RM_Sesserith.xml:164 texPath RM_Abyss/Things/Pawn/Animal/RM_Sesserith/RM_Sesserith | PASS |
| RM_LongShade/Nerf/amb | amb | A click | amb:A | SWBestiary Nerf_f_east.png == desert snapshot col E east effceaee; conflictSheet A recorded; RSW_Nerf.xml:258 texPath swanimals/Nerf/Nerf_f | PASS |
| RM_Greentide/Peko Peko/amb | amb | A click | amb:A | PekoPeko_f_{e,n,s} == greentide snapshot col N (e07a381f,23724d92,4d18fec8); RSW_PekoPeko.xml:218 texPath swanimals/PekoPeko/PekoPeko_f | PASS |
| RM_Abyss/Shadow Charger/amb | amb | other click ("broken?") | row decision cut; not in wildAnimals | decision='cut'; AA_ShadowCharger in wildAnimals=False (15 elements) | PASS |
| RM_Abyss/Giant Fibre Stalk/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; RM_GiantFibreStalk.png byte-identical to 43f354a44 (single-file) | PASS |
| RM_Abyss/Glowing Grass/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Abyss/Nevarithia/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Abyss/Sickly Glow Mushroom/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; RM_SicklyGlowMushroom.png byte-identical to 43f354a44 (single-file) | PASS |
| RM_Greentide/Beldon/stale | stale | other click | stale:other | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_LeaningScrub/Durrok/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_LeaningScrub/Mullgoth/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_TwilightSea/Dancing Skresh/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_TwilightSea/Gripping Terror/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Warscar/Bileworm/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Warscar/Electric Gryllotalpa/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Warscar/Electric Tick/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Warscar/Juggernaut Beetle/stale | stale | B click | stale:B | decision/picks/variants empty, stale_letters_dropped kept; live art files (3-28 png by name) all byte-identical to 43f354a44 | PASS |
| RM_Abyss/Crepuscular Beetle/noslot | noslot | A default | noslot:A | picks->reference_picks=True; RM_Moravatha_{e,n,s} == abyss_moravatha_v3 renders (1dfb21ab,82ca2653,d27738dd); defs: Abyss RM_ port xml texPath (Sesserith/Moravatha etc. under src/RimMandrake/Abyss/Defs/ThingDefs_Races) | PASS |
| RM_Abyss/Dark Vandal/noslot | noslot | A default | noslot:A | picks->reference_picks=True; RM_Ossumatha_east == abyss_ossumatha_v3_east render (4b0d197f); north/south files DO NOT EXIST in src (never installed before either); jobs abyss_ossumatha_v5_north/south exist in done/ (renders fa4473d5,18bd0b2b) but not installed yet. Def RM_Ossumatha.xml:123 texPath RM_Abyss/Things/Pawn/Animal/RM_Ossumatha/RM_Ossumatha; defs: Abyss RM_ port xml texPath (Sesserith/Moravatha etc. under src/RimMandrake/Abyss/Defs/ThingDefs_Races) | PASS |
| RM_Abyss/Dusk Prowler/noslot | noslot | A default | noslot:A | picks->reference_picks=True; RM_Ysvaltha_{e,n,s} == abyss_ysvaltha_v3 renders; defs: Abyss RM_ port xml texPath (Sesserith/Moravatha etc. under src/RimMandrake/Abyss/Defs/ThingDefs_Races) | PASS |
| RM_Abyss/Murkling/noslot | noslot | A default | noslot:A | picks->reference_picks=True; RM_Lirrith_{e,n,s} == abyss_lirrith_v3 renders; defs: Abyss RM_ port xml texPath (Sesserith/Moravatha etc. under src/RimMandrake/Abyss/Defs/ThingDefs_Races) | PASS |
| RM_Abyss/Night Ram/noslot | noslot | A default | noslot:A | picks->reference_picks=True; RM_Olumetha_east/north == v3 renders; south b5d0d52f == abyss_olumetha_v4_south render; defs: Abyss RM_ port xml texPath (Sesserith/Moravatha etc. under src/RimMandrake/Abyss/Defs/ThingDefs_Races) | PASS |
| RM_Abyss/Glowing Grass/noslot | noslot | A default | noslot:A | picks->reference_picks=True; RM_GlowingGrass_{a,b,c} == abyss_glowinggrass_{a_tint_v1,b_tint_v2,c_tint_v1} renders; defs: Abyss RM_ port xml texPath (Sesserith/Moravatha etc. under src/RimMandrake/Abyss/Defs/ThingDefs_Races) | PASS |
| RM_LeaningScrub/Hoard Venomvine/noslot | noslot | A default | noslot:A | RM_HoardVenomvine_b.png == snapshot col J (de347c79); RM_VenomvineSixForms.xml:168 def uses texPath Things/Plant/RM_HoardVenomvine Graphic_Random; decision J retained | PASS |
| RM_Miasma/Mantrap/noslot | noslot | A default | noslot:A | AA_Mantrap_{e,n,s}.png each == snapshot col E (7da23619); donor Alpha Animals def texPath Things/Pawn/Animal/AA_Mantrap/AA_Mantrap (snapshot graphic_of); lastvine jobs filed | PASS |
| RM_BlueDesert/Dovvik/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_e3e8ae91_dovvik_v1* match (states ['done', 'pending']) | PASS |
| RM_BlueDesert/Murrek/note | note | A default | job target_def=row & owner_note verbatim | 3/5 jobs enact_069e4d4b_murrek_v1* match (states ['active', 'done']) | PASS |
| RM_BlueDesert/Utikka/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_d67b8fd8_utikka_v1* match (states ['active', 'done', 'pending']) | PASS |
| RM_BlueDesert/Vrisk/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_b3c6f3d3_vrisk_v1* match (states ['active', 'done']) | PASS |
| RM_Contagion/Doublemaw/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_9b51ef78_doublemaw_v1* match (states ['done']) | PASS |
| RM_Contagion/Eyestinger/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_ffe79056_eyestinger_v1* match (states ['done']) | PASS |
| RM_Contagion/Gawpsack/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_712dc596_gawpsack_v1* match (states ['failed']) | PASS |
| RM_Contagion/Sparkleech/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_c6a3f569_sparkleech_v1* match (states ['done']) | PASS |
| RM_GelatinousSlime/Dwommo/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_5673ffda_dwommo_v1* match (states ['pending']) | PASS |
| RM_GreySea/Corrik/note | note | A default | job target_def=row & owner_note verbatim | 3/3 jobs enact_c0132bf3_corrik_v1* match (states ['pending']) | PASS |
| RM_Contagion/Contagion Ikee/note | note | A default | enact_done event, no new ikee job | enact_done event 1312a918e6dc (RM_ContagionIkee, "keep his restored ikee art; no redraw"); no ikee job created after 2026-10-05 (latest RM_Ikee_* 09-28, stillsand_regen_RSW_Ikee_v2 10-05) | PASS |
| RM_Contagion/Contagion Ikee/kept | kept | A click | kept:A | RM_ContagionIkee_{e,n,s}.png byte-identical to 43f354a44; decision/picks empty, pick moved to reference_picks | PASS |
| RM_Stillsand/Kreetle/kept | kept | A default | kept:A | Kreetle_* (8 png) byte-identical to 43f354a44; decision empty, I moved to reference_picks (note: j pick F remains, row purge list of 7 shas untouched) | PASS |
| RM_FeverWood/Halquin/kept | kept | B click | kept:B | RM_Halquin_a.png sha 39b96825 == snapshot col B (render feverwood_plant_halquin) | PASS |
| RM_FeverWood/Maulith/kept | kept | other click | job enact_449ef76f_maulith_v1 | job enact_449ef76f_maulith_v1 in pending/, target_def RM_Maulith, owner_note "regen, not quality enough" | PASS |
| RM_GelatinousSlime/Bellows/purgedpick | purgedpick | A click | purgedpick:A | row decision now B; col B sha 4c2f39c6 live at src/RimMandrake/GelatinousSlime/Textures/Things/Plant/RM_Bellows/RM_Bellows/RM_Bellows_a.png; SlimeFlora.xml:71 texPath Things/Plant/RM_Bellows/RM_Bellows (note path doubles RM_Bellows/RM_Bellows - Graphic_Random folder) | PASS |
| RM_GelatinousSlime/Readerbloom/purgedpick | purgedpick | other click | job w/ owner_note | job enact_a78ae7bb_plant_readerbloom_v1 pending, target_def RM_Plant_Readerbloom, owner_note "regen for low quality"; row decision redo | PASS |
| RM_Stillsand/Krayt Dragon/failed | failed | A click | job w/ HARD REQUIREMENT | stillsand_s3_RSW_KraytDragon_v4_south exists (state failed/), prompt has HARD REQUIREMENT | PASS |
| RM_Miasma/Blixus/failed | failed | A default | jobs w/ HARD REQUIREMENT | miasma_canon_blixus_v2_north (done), v2b_south (failed), v2_swim_east (failed) all exist with HARD REQUIREMENT | PASS |
| RM_Miasma/Opee Sea Killer Juv/failed | failed | A default | job w/ HARD REQUIREMENT | miasma_canon_opeejuv_v3_south exists (state failed/), HARD REQUIREMENT present | PASS |
| RM_Webwork/Tooke Trap  Wild/failed | failed | A default | job w/ HARD REQUIREMENT | webwork_tooketrap_redo_v3 exists (done), HARD REQUIREMENT present | PASS |
| RM_LongShade/Great Devourer/tier | tier | A default (question) | unchanged except conflictSheet; RM_Gulloth exists | row diff vs adf9fc7be~1 = [conflictSheet] only; RM_Gulloth defined in src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fauna.xml with textures | PASS |

## FAILS

(No FAILs.)

## Observations (not failures)
- PekoPeko_m south replacement job conflict_pekopeko_m_v2_south is in failed/ (east/north done/); Hawkbat j_north job regen_gt_canon_hawkbat_juv_v2_north is done/ but not yet installed.
- RM_Ossumatha north/south png do not exist in src (east only); abyss_ossumatha_v5_{north,south} done/ but uninstalled; def would load a missing facing.
- Note jobs for Gawpsack (failed/), Krayt v4_south, Blixus v2b_south/v2_swim_east, Opee juv v3_south (failed/) exist but did not render.
- Orphans: RM_Ossik_north, RSW_Ossik_north, RM_Sorruth absent and no def texPath names them. Shared sha 92592a78 absent from src.

## Dry-run residue (art.py enact, no --apply)
- twilightsea: CONFLICTS 0, TODO 0. thescald: CONFLICTS 0, TODO 0.
- greentide: CONFLICTS 4: RSW_Hawkbat Hawkbat_j_north (0a1878e64116 live), RSW_PekoPeko PekoPeko_m_{south b64f05d78665, east 6e10195a6185, north bc1c95fc5e39} live. TODO 0.
- Desert sheet (Great Devourer tier question) not re-run.
