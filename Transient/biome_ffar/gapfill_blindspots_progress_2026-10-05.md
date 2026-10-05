# Gapfill blind spots progress 2026-10-05 (BIOME_FLORAFAUNA_ART_REVIEW_1)

Jobs: `Transient/biome_ffar/gapfill_blindspots_jobs_2026-10-05.json` -- 12 rows, 16 jobs filed (`gapbs_*`, priority 20). Out of scope: Abyss, BlueDesert, LongShade, Stillsand.

## 2. The 121 unjoined rows, checked against what the sheets actually show
Method: parsed the ITEMS JSON of the 23 sheets (774 rows) and classified every picture column. Census `kind: donor` is ANY game copy of a texPath, including our own mod's deployed files (package `mandrake.rm.biomes`, 112 columns), so it overstates donor-only.
- 119 census donor-only rows not queued: 105 carry our own texture (mandrake.* package) or a render of ours on the sheet; 14 truly show donor art only.
- Of the 14: owner-ruled, NOT queued: RSW_Durrok (x2 sheets, ruled keep of rot art, done render rot_wildpawn_v2) and VFEI2_Swarmling (x2 sheets, owner replace ruling, done render rot_swarmling_v2). Both have finished renders the sheet join fails to show; rebuild must wire them.
- 10 flora queued fresh: Plant_Brambles, RG_Plant_CreepStern, RG_Plant_CrimsonCushion, RG_Plant_Dervish, AB_FirevineTree, Plant_MagmaCactus, AB_TinkleGrass, Plant_GrayGrass, Plant_Toxipotato, Plant_Reeds. Older done v1 renders exist (brambles_v1 etc.) but the sheets do not show them.
- CENSUS/SHEET JOIN BUG: `art_sheet.build_row` aliases renders by name using the last path part of the texPath (`wl`, line ~214), stripped only of RM_/RSW_/RUT_ tiers. Donor-prefixed textures (RG_Brambles, AB_TinkleGrass, ...) never match jobs named `brambles_v1`, so finished renders stay off the sheet. Also kind `donor` mislabels our own mandrake.* deployed art. Filed as rimflow item.

## 1. Flyers
All 28 flying rows (distinct biome/species) have ours-art on the grounded body at row level; none is donor-only. Donor-only grounded graphic variants queued (3 facings each, canon wired): RSW_Hawkbat juvenile (`Hawkbat_j`, canon hawkbat), RSW_PekoPeko male (`PekoPeko_m`, canon pekopeko). RM_Kirruk grounded graphic is vanilla Chicken but render weepingstones2_kirruk already shows on its sheet: not queued.
Flight flip-book still owed for every flyer:
- RM_Cauldron RSW_Neebray -- flight flip-book still owed
- RM_Cauldron RSW_Screecher -- flight flip-book still owed
- RM_FeverWood RSW_Convor -- flight flip-book still owed
- RM_FeverWood RSW_Urusai -- flight flip-book still owed
- RM_FeverWood RSW_Whisperbird -- flight flip-book still owed
- RM_FloodedCanyon RSW_CanCell -- flight flip-book still owed
- RM_FloodedCanyon RSW_Convor -- flight flip-book still owed
- RM_Greentide RSW_Beldon -- flight flip-book still owed
- RM_Greentide RSW_Convor -- flight flip-book still owed
- RM_Greentide RSW_Hawkbat -- flight flip-book still owed
- RM_Greentide RSW_PekoPeko -- flight flip-book still owed
- RM_Greentide RSW_Whisperbird -- flight flip-book still owed
- RM_LeaningScrub RSW_Convor -- flight flip-book still owed
- RM_LeaningScrub RSW_Porg -- flight flip-book still owed
- RM_LeaningScrub RSW_ScrapNestBird -- flight flip-book still owed
- RM_LeaningScrub RSW_Sketto -- flight flip-book still owed
- RM_LeaningScrub RSW_Strill -- flight flip-book still owed
- RM_LeaningScrub RSW_Urusai -- flight flip-book still owed
- RM_LeaningScrub RSW_Whisperbird -- flight flip-book still owed
- RM_Miasma RSW_Bogwing -- flight flip-book still owed
- RM_Miasma RSW_Whisperbird -- flight flip-book still owed
- RM_Pyrelands RM_FireHawk -- flight flip-book still owed
- RM_TheForge RSW_Beldon -- flight flip-book still owed
- RM_Wasteland RSW_BloodletterPetrel -- flight flip-book still owed
- RM_Wasteland RSW_Sacapillar -- flight flip-book still owed
- RM_Wasteland RSW_Screecher -- flight flip-book still owed
- RM_WeepingStones RM_Kirruk -- flight flip-book still owed
- RM_WeepingStones RSW_Dactillion -- flight flip-book still owed
