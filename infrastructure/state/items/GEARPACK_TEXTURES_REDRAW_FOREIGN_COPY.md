# GEARPACK_TEXTURES_REDRAW_FOREIGN_COPY

Found by ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS (FOUNDRY, 2026-10-24).
Evidence: `D:\ClaudeWork\rimmandrake\foreign_copy_audit_20261024\` (scanall.txt, hits.png, wrong_installs.txt, rollouts.txt).

## What is wrong

Eight shipped textures show the same image: the FlowWorks climbing-gear belt pack, a leather pack with a rope coil and
claws. The legitimate owner of that render is `RM_ClimbingGear.png` (commit 0fb68b5091). Its source is the GLOBAL codex
cache file `C:\Users\Mandrake\.codex\generated_images\01a15228-8bce-7e10-b13d-7f2f5f7a943d\exec-4741836a-...png`,
written 2026-10-18 20:16. Donor-redraw (dregen_) workers whose image_gen returned no path copied that cache file into
place: this is the CODEX_FOREIGN_IMAGE_COPY defect, fixed in codex_image.py by 8cea1c2d5f and afaee7c244. The runner
recorded them `ok` and they were bulk-installed.

How it was matched: every one of the 11,114 tracked Textures PNGs was compared with the source on an alpha-cropped 32px
thumbnail. These eight score 0.60 to 2.04; the next nearest file scores 19.89. hits.png shows them visually.

| installed texture | job | install commit |
|---|---|---|
| src/RimStarWars/SWBestiary/Textures/swanimals/Neebray/Neebray_Dessicated.png | dregen_RSW_Neebray_NeebrayDessicated_v1 | 3b6ac41125 |
| src/RimMandrake/WeepingStones/Textures/Things/Pawn/Animal/Cobra/RM_Vhorrin/RM_Vhorrin_south.png | dregen_RM_Vhorrin_Cobra_v1_south (probable; no install_to) | 3b6ac41125 |
| src/RimStarWars/SWBestiary/Textures/swanimals/KowakianMonkeyLizard/KowakianMonkeyLizardE_south.png | dregen_RSW_KowakianMonkeyLizard_KowakianMonkeyLizardE_v1_south | 3b6ac41125 |
| src/RimStarWars/SWBestiary/Textures/swanimals/Convor/Convor_Dessicated.png | dregen_RSW_Convor_ConvorDessicated_v1 | 3b6ac41125 |
| src/RimMandrake/EnvironmentalHazards/Textures/Things/Plant/RM_Venomvine/RM_Venomvine_c.png | dregen_RM_Venomvine_RMVenomvinec_v1 | 402494376a |
| src/RimStarWars/SWBestiary/Textures/swresource/Meat_Reptavian/Meat_Reptavian_a.png | dregen_RSW_Reptavian_Meat_MeatReptaviana_v1 | 681aca61b9 |
| src/RimStarWars/SWBestiary/Textures/swresource/Meat_Reptavian/Meat_Reptavian_c.png | dregen_RSW_Reptavian_Meat_MeatReptavianc_v1 | 681aca61b9 |
| src/RimStarWars/Armoury/Textures/Things/Item/Resource/Crystal/Synthetic/crystal_pearl.png | dregen_Force_KyberCrystal_crystalpearl_v1 | b84e8ba68c |

On all eight but Neebray (which has no self-report), the worker reported `ok` and said it had generated the subject. So
neither the worker's self-report nor the runner's status catches this; only provenance does.

## To do

Re-queue these eight dregen jobs as fresh renders, now that the codex_image guard is in place, and install them over
the wrong art. `fauna_drive rows` cannot take them: it needs an art-eval run's regen_jobs.json plus a fauna spec under
`art_eval/fauna_specs`, and none of these subjects has one. The route is the dregen queue (fill_queue.py with the
original job rows from `D:\ClaudeWork\rimmandrake\artpipe\done\<job>.json`). Nothing was installed or purged by the audit.

The other cache source, `C:\Users\Mandrake\.codex\generated_images\01a0b7c0-...\exec-5dc619c6-...png` (the spiral
desert-wrap cocoon, legitimate owner `Wraps_Female_east.png`), is installed nowhere else.
