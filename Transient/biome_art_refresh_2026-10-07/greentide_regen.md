# Greentide regen — 2026-10-07 (BENCH helper)

Source: `Transient/biome_ffar/greentide_sheet_2026-10-05.decisions.json` (human rows = those with `at`; re-read before filing, unchanged: savedAt 2026-10-07T21:56:31-0700, writeCount 167).
Method copied from `feverwood_regen.md`. Built by `build_greentide_regen_jobs.py` -> `greentide_regen_jobs.json` (89 rows -> **177 jobs**).

## Status
- [x] decisions read, canon images read (looked at them), defs read (drawSize, texPaths, flight prefixes)
- [x] existing-art search (listing of `_artpipe/done`, sanity probe `korrum` = hit; `artpipe_state.py find` costs ~25 s per term so the sweep read the done/ listing once)
- [x] Beldon: `wookieepedia_woswfg.webp` downloaded into `design/RimStarWars/canon_references/beldon/` (the wiki serves WebP), listed in Candidate images, ruling line appended with his note verbatim
- [x] jobs filed at priority 0, ids `regen_gt_*` -> pending positions **152–328** of 340 (Miasma and Feverwood ahead, 12 priority-100 jobs behind); daemon claims by (priority, filename)

## Canon (canon image as `canon_reference`, never `reference`; `canon` folds Visual brief + Must show)
- **RSW_Beldon** `regen_gt_canon_beldon_v1` (3, 512px, drawSize 4): canon_reference = `beldon/wookieepedia_woswfg.webp` first, in-game donor east (column A) second as concept. The purple `beldon_wookieepedia_1.jpg` NOT attached. Flight: `regen_gt_beldon_flying_{1..3}_v1` (9 jobs, frame count 3 from the PawnKindDef, prefix `swanimals/Beldon/Beldon_Flying_`) derived from the new east.
- **RSW_Dragonsnake** `regen_gt_canon_dragonsnake_v1` (3, 512): `dragonsnake/wookieepedia_mandalorianandgrogu.jpg` (the middle one of three, pale snake on black; ours is transparent). `..._v1_swim` (3) derived -> `Dragonsnake_Swimming`.
- **RSW_Hawkbat** `regen_gt_canon_hawkbat_v1` (3, 256): `hawkbat/wookieepedia_legends_infobox.jpg` (purple and tan; "NOT a bird" in prompt). `..._juv_v1` (3) -> `Hawkbat_j`; flight `regen_gt_hawkbat_flying_{1..4}_v1` (12, prefix `Hawkbat_Flying_`, 4 frames) and `hawkbat_flying_j_{1..4}_v1` (12, prefix `Hawkbat_j_Flying_`, derived from the juvenile east; I added these so the juvenile flight does not keep old art).
- **RSW_Kinrath** `regen_gt_canon_kinrath_v1` (3, 512): `kinrath/wookieepedia_legends_infobox_viperkinrath.png` (mantis shape, gold) + donor original east (column D) as geometry guidance.
- **RSW_Klorslug** `regen_gt_canon_klorslug_v1` (3, 512): `klorslug/wookieepedia_legends_1.webp` (red body, white claw spines); `..._juv_v1` (3) -> `Klorslug_j`.
- **RSW_Lylek** `regen_gt_canon_lylek_v1` (3, 512): `lylek/wookieepedia_canon_1.webp`.
- **RSW_Mott** `regen_gt_canon_mott_f_v1` (3, 256): `mott/wookieepedia_canon_1.webp`; derived `mott_m_v1` -> `Mott_m`, `mott_f_swim_v1` -> `Mott_f_Swimming`, `mott_m_swim_v1` -> `Mott_m_Swimming` (9).
- **RSW_PekoPeko** `regen_gt_canon_pekopeko_f_v1` (3, 512): `pekopeko/wookieepedia_fieldguide.jpg`; male `..._m_v1` derived; flight `pekopeko_flying_f_{1..4}_v1` (prefix `PekoPeko_f_Flying_`) from the female east and `pekopeko_flying_m_{1..4}_v1` (prefix `PekoPeko_m_Flying_`) from the male east (24 jobs; frame count 4 from the PawnKindDef).
- **RSW_ShiroTrap** `regen_gt_canon_shirotrap_v1` (3, 256): `shirotrap/wookieepedia_canon_1.webp` (turtle with trap plant) + in-game Shiro east (RSW_Shiro column A) as concept; `_i_v1`, `_j_v1` (6) derived. The tooke trap-plant entry images were not attached (one canon image only).

## Invented
- **RM_CanopySwinger** (ookala) `regen_gt_ookala_v2` (3, 256): anchored on in-game east. The def already says ookala.
- **RM_Tuun** `regen_gt_tuun_v2{a,b,c}` (3 single-image jobs, 256, texPath `Things/Item/Fish/RM_Tuun`): anchored on column B `phreg_RM_Tuun_v1`.
- **RSW_Diggerpede** (gristle) `regen_gt_gristle_v2` (3, 256): no canon entry exists (checked the canon_references listing and src); anchored on in-game east for pose.
- **VFEI2_Swarmling** (saluksis) `regen_gt_saluksis_v2` (3, 256): anchored on column B east. **Overlap:** the Miasma helper's `miasma_swarmling_green_v1_{east,north,south}` recolours of `rot_swarmling_v2` of the same def are still queued and untouched.

## Variants (chosen render attached as `canon_reference`; canvas = max visualSizeRange x 128, next power of two, ceiling 1024)
- 1 new variant (`_varb_v1`): Brakkel (A, 512), Cundral (A, 256), Gorbeleth (A, 512), Maddrick (A, 512).
- 2 realistic variants (`_varb_v1`, `_varc_v1`): Plant_Grass (B, 256), Plant_TallGrass (B, 256), Ghemmel, Illurin, Kaddrath, Mourvel, Nemmer, Sarnstilt, Tumbel, Veluthar, Zhorrel (1024; Greatbole 1024 is the ceiling for a 12-16 cell giant, recorded in `oversize_reason`), Mirrelbole, Phorrik, Quathis, Sarquin, Thalquith (B), Wollick (512), YearningFruit (B, 256).

## Flyer
- **RM_Yammeth** `regen_gt_yammeth_flying_{1..4}_v1` (12 jobs, 256): derived from the finished job `RM_Yammeth_east` (same image as the in-game east, sha 3601ff82...). The PawnKindDef has NO flyingAnimationFrameCount, so 4 frames is the default; the def still needs `flyingAnimationFramePathPrefix` = `Things/Pawn/Animal/RM_Yammeth/RM_Yammeth_Flying_` + count 4 + `MaxFlightTime` is already set.

## Not filed
- No art asked: BloodShrimp (rename Zrrik, description), Dhollock (rename), Thurrock (description), Sytheclaw (hold), the six fish and Dubbol/Karrun/Lozh/Saava/Uvva/Zeev B-picks (installed), Dalgo, Shiro, Fambaa, Gelagrub (see Feverwood sheet).
- Not regenerated though the same def: `BeldonC` and `BeldonC_Flying_` (the second Beldon texture set, which he picked C/D in-game on that row), `Mott` and `PekoPeko` picks he kept (replaced by the derived set per the brief). If the C set should match the new east, file it from `regen_gt_canon_beldon_v1_east`.
- Tuun and plants are single images (no facings).

## Already generated (did not replace the new jobs)
- Beldon `canon_beldon_v1` (column B), Dragonsnake `dragonsnake_v1`, Hawkbat `hawkbat_v1`/`canon_hawkbat_v1`/`gapbs_RSW_Hawkbat_juv_v1`, Kinrath `kinrath_v1`/`canon_kinrath_v1`, PekoPeko `pekopeko_v1`/`gapbs_RSW_PekoPeko_male_v1`, Shiro `shiro_v1`/`canon_shiro_v1`, Tuun `phreg_RM_Tuun_v1`, Swarmling `rot_swarmling_v2`.
- Plants: `rm_<name>_v1` and `gapfin_RM_<name>_v1` for Cundral, Gorbeleth, Mirrelbole, Mourvel, Phorrik, Quathis, Sarnstilt, Sarquin, Thalquith, Tumbel, Wollick, Zhorrel; `rm_brakkel_v1`, `rm_maddrick_v1`, `rm_kaddrath_v1`, `rm_greatbole_v1`, `gapall_RM_YearningFruit_v1`.
- No finished art by name for: Klorslug, Lylek, Mott, ShiroTrap, Diggerpede, Ghemmel, Illurin, Nemmer, Veluthar (their sheet renders carry other job names).
