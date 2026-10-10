# Gap art queue 2026-10-10 (ART_TEXTURE_GAPS_FOLLOWUP_1) — nothing installed

Job file (tracked): `Transient/gap_art_jobs_20261010.json`. 11 jobs filed to artpipe pending (daemon runs on the Desktop). Every job carries `install_to`/`target_texpath` = the exact missing texPath.

## Queued (11)
- KOTOR_SmallCrystal: 1 job (512, neutral white so the def colour tints it) -> Armoury `Buildings/Crystal_Formations/small_dyeable/small_dyeable_a.png` (Graphic_Random reads a FOLDER; the lint wants the folder to hold a PNG).
- Things/Filth/CrawlSmear: 1 job (128, neutral dark) -> Traces `Textures/Things/Filth/CrawlSmear.png`.
- RM_AssayFlecks Flecks_Light / Flecks_Heavy: 2 jobs (256 overlay) -> Cauldron `Things/Plant/RM_AssayFlecks/`.
- RM_Dewfall x5 (_dew): 5 jobs (256), each with `reference` = the plant's `_a.png` (same-pose validation) -> Cauldron `Things/Plant/RM_Dewfall/`.
- RM_Dakkra_rest north + south: 2 jobs derived from the finished east render.

## Already rendered (not re-queued)
- RM_Dakkra_rest east: `ls_regen_RM_Dakkra_rest_v1_east` in `D:\Luke\dev\_artpipe\_artsrc\ls_regen_RM_Dakkra_rest_v1_east\` (256, canon-check PASS 5/5). Install -> LongShade `Things/Pawn/Animal/RM_Dakkra/RM_Dakkra_rest_east.png` once north/south land.
- RM_Braskeen: owner ruled REDO ("less cartoonish", 2026-10-08, `infrastructure/state/art_rulings/2026-10-07_miasma_sheet_2026-10-05.decisions.json`); the v2 renders exist (`miasma_braskeen_open_v2`, `miasma_braskeen_closed_v2` in `_artsrc`). Awaiting his pick; nothing to queue.
