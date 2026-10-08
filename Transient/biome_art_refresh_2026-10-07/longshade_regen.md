# Long Shade regen (2026-10-07, BENCH helper)

Source: `Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json` (re-read before filing: savedAt 2026-10-07T22:29:03-0700, writeCount 901, the 13 rows and notes unchanged). Built by `build_longshade_regen_jobs.py` -> `longshade_regen_jobs.json` (34 rows -> **63 jobs**), filed at priority 0, item BIOME_FLORAFAUNA_ART_REVIEW_1. Nothing installed into Textures, git untouched.

## Status
- [x] method read (Greentide builder/notes, fill_queue.py), defs read, picked images looked at, canon entries read
- [x] done/ + pending/ checked (no `regen_ls_*` pending; prior renders listed below)
- [x] builder written, fill_queue dry-run clean (63 jobs, 0 refused), filed (63 filed, 0 duplicate, 0 error)
- [x] positions computed

## Pending positions (rank by (priority, filename) at filing time; 388 pending in all, 376 at priority 0; claims will shift them)
Overall **314-376 of 388** (all behind miasma_*, regen_fw_*, regen_gt_*; the 12 priority-100 jobs stay behind).
- canon dewback: 3 jobs, positions 314-316
- canon falumpaset: 3 jobs, positions 317-319
- canon frilledgorg_i: 2 jobs, positions 320-321
- canon frilledgorg_k: 2 jobs, positions 322-323
- canon gorg_l: 2 jobs, positions 324-325
- canon nerf: 2 jobs, positions 326-327
- canon shyrack_flying: 12 jobs, positions 328-339
- canon sketto_flying: 12 jobs, positions 340-351
- canon sketto: 2 jobs, positions 352-353
- canon teemuss: 3 jobs, positions 354-356
- canon uvak_flying: 12 jobs, positions 357-368
- x chorn: 3 jobs, positions 369-371
- x dakkra_rest: 2 jobs, positions 372-373
- x landopus_buried: 2 jobs, positions 374-375
- x venomvine: 1 jobs, positions 376-376
overall 314-376 of 388

(the grouped ranges are alphabetical, so canon rows sort before x rows; the daemon takes them in that order.)

## Method notes
- Picked east images: all 12 picks verified byte-identical (sha256) to `_artpipe/_artsrc/<job>_east/<job>_east.png`.
- **Real derive_from** (master job is in done/): Uvak and Shyrack flight (`longshade_rsw_uvak_v1_east`, `longshade_rsw_shyrack_v1_east`), Landopus N/S (`ls_regen_JOE_Landopus_swim_v1_east`), Dakkra N/S (`ls_regen_RM_Dakkra_rest_v1_east`), and N/S of TeeMuss/Falumpaset/Dewback derived from their NEW east re-render (`@..._east`, daemon holds them until it finishes).
- **canon_reference anchoring instead** (picked east's job is in failed/ because the canon gate failed, and artpiped sends any job derived from a failed master straight to failed/): Sketto N/S + flight, Nerf N/S, Gorg L and FrilledGorg I/K N/S, and the three east re-renders. The picked PNG is the FIRST canon_reference (the daemon attaches only the first existing one), the canon-library image second. Canon text (`canon` = Visual brief + Must show) is folded in for the canon subjects. This means these N/S are fresh generations conditioned on the pick, not pixel derivations; expect more identity drift than a real derive.
- Canon jobs use `biome_neutral` (keep the picked colours, no Long Shade grade); non-canon (Landopus, Dakkra, Chorn, Venomvine) carry the Long Shade register copied from the earlier `ls_regen_*` jobs.
- Owner notes copied from the decisions file (trailing space on TeeMuss kept) into `owner_note` and the prompt lead.

## Jobs filed (63)
### Canon (canon_reference image used)
- RSW_Sketto: `regen_ls_canon_sketto_v1_{south,north}` (256, -> swanimals/Sketto/Sketto) and `regen_ls_canon_sketto_flying_{1..4}_v1_{east,south,north}` (12, prefix swanimals/Sketto/Sketto_Flying_, 4 frames per PawnKindDef). Anchor: picked C east `a1f3365c...` + canon `sketto/wookieepedia_canon_1.webp` (the pale-pink prop with amber wings, which matches C; the Legends sheets were not attached).
- RSW_TeeMuss: `regen_ls_canon_teemuss_v1_east` (512 re-render; C east is 256, def adult drawSize 3.0 -> 512) + `regen_ls_canon_teemuss_v1_ns_{south,north}` derived from it. canon `teemuss/wookieepedia_canon_1.webp`.
- RSW_Falumpaset: `regen_ls_canon_falumpaset_v1_east` (512 re-render, **my addition**: owner asked only N/S, but def adult drawSize is 4.0 -> 512 while C is 256, so N/S at 256 would not match) + `..._v1_ns_{south,north}`. canon `falumpaset/wookieepedia_canon_1.webp`. Drop the east job if you want the 256 east kept.
- RSW_Nerf: `regen_ls_canon_nerf_v1_{south,north}` (256 -> swanimals/Nerf/Nerf_f; the E pick row is the `_byname` female/default graphic, def line 258 `Nerf_f`). canon `nerf/wookieepedia_canon_1.webp`.
- RSW_Dewback: `regen_ls_canon_dewback_v1_east` (512, "four cells wide", from H east which is 256) + `..._v1_ns_{south,north}`. canon image = ruled `dewback/wookieepedia_infobox.jpg`.
- RSW_Uvak: `regen_ls_canon_uvak_flying_{1..4}_v1_{east,south,north}` (12, 256, prefix swanimals/Uvak/Uvak_Flying_, 4 frames), derive_from the done C east. canon `uvak/wookieepedia_canon_1.webp` (stored on the job, ignored by the daemon for derive jobs).
- RSW_Shyrack: `regen_ls_canon_shyrack_flying_{1..4}_v1_{east,south,north}` (12, 256, prefix swanimals/Shyrack/Shyrack_Flying_, 4 frames), derive_from the done C east. canon `shyrack/wookieepedia_legends_1.webp` (only a Legends image exists).
- Variants (no canon-library entry for FrilledGorg; none attached for the Gorg variants either), NEW texPaths, N and S each, 256: `regen_ls_canon_gorg_l_v1_{south,north}` -> swanimals/Gorg/GorgV_L; `regen_ls_canon_frilledgorg_i_v1_*` -> swanimals/FrilledGorg/FrilledGorgV_I; `regen_ls_canon_frilledgorg_k_v1_*` -> .../FrilledGorgV_K. **Open: nothing wires these paths yet** (the defs' alternateGraphics use GorgA..E / FrilledGorgA..C); whether they become alternates is undecided.
### Non-canon
- JOE_Landopus (label thraia): `regen_ls_x_landopus_buried_v1_{south,north}` derive_from done `ls_regen_JOE_Landopus_swim_v1_east` (F), half-buried-in-sand look -> NEW path Things/Pawn/Animal/landopus/landopus_buried (which slot it fills is an open owner question; note the def's own swimming path is swimming_landopus).
- RM_Dakkra: `regen_ls_x_dakkra_rest_v1_{south,north}` derive_from done `ls_regen_RM_Dakkra_rest_v1_east` (C, fins flared) -> Things/Pawn/Animal/RM_Dakkra/RM_Dakkra_rest (already wired as stationaryGraphicData).
- RM_Chorn: `regen_ls_x_chorn_v2_{east,south,north}` 1024 canvas (5 cells x 128 = 640 -> next power of two), anchored on the in-game east (column A, 512 px) -> Things/Pawn/Animal/RM_Sollak/RM_Sollak. Owner note verbatim (incl. "Regenerate description", which is the parent's job, not art).
- RM_Venomvine: `regen_ls_x_venomvine_v2` single 256 -> Things/Plant/RM_Venomvine (the def reads it as a Graphic_Random FOLDER, the earlier landing was `RM_Venomvine/RM_Venomvine_a.png`). Prompt built from the def description plus the design colours (rust-umber, bone-tan thorns, no green) and says explicitly "not a pillar, arm, column or limb". Not superseded: the 11 newer `RM_*Venomvine` defs belong to Leaning Scrub; RM_Venomvine is still cast at 0.25 in `RM_LongShade.xml` line 233. RM_VenomvineThicket shares its texPath on purpose, so a new render lands on both.

## Odd findings
- **Chorn def already says five cells**: drawSize 5.0 and the description already says "five cells across"; the art was a 512 canvas, so the owner's complaint is presumably the creature not filling the 5-cell footprint. Art is sized for it; the description the owner asked to regenerate is the parent's.
- **Dewback def drawSize is already 4.0** for the adult (line 192), so "four cells wide" may only need the art to fill the frame; the 512 canvas is what makes it 4 cells at 128 px/cell. The two younger stages are 1.33 and 2.67.
- **Falumpaset/TeeMuss/Dewback/Uvak existing art is 256 px** against def drawSizes 4.0/3.0/4.0/3.5 (all want 512). Uvak C standing art being installed is 256 for a 3.5-cell creature: no job filed for it (not asked).
- **All picks marked "failed canon check"** on the sheet (Sketto, TeeMuss, Falumpaset, Nerf, Dewback, Uvak, Gorg L, FrilledGorg I/K); Shyrack C is the one that passed. The owner picked them anyway. The new daemon canon gate will grade the derived/anchored jobs too.
- **Shyrack flyer frame names**: the sheet's column D lists frames 1,2,3,**44** (a stray `Shyrack_Flying_44_*` file; frame 4 does not exist as `_4`). The PawnKindDef says prefix swanimals/Shyrack/Shyrack_Flying_, count 4, so the new frames `_1.._4` fix it; the old `_44_` files become dead. Sketto's header comment in the def records the same `_44_` slip class.
- **Venomvine tint**: the def tints the texture (112,68,48), the earlier art and this prompt are already dark rust-umber, so the in-game result may be doubly dark; a lighter/neutral render may be needed after the first look. Cannot judge before the render exists.
- **Landopus** def drawSize 0.8 (art canvas 256); the earlier `ls_regen_JOE_Landopus_swim_v1` job used drawsize 1.2 for its stamp. Mine uses 0.8 from the def.
- Existing finished art found (not replaced): `rmvenomvine_v1`, `ls_regen_RM_Venomvine_v1` (the in-game pillar-arm is `RM_PillarArmB`), `longshade_rsw_{gorg,frilledgorg}_v1..v6`, `desertportb_*`, `desert_swaca_*` for the Star Wars creatures. None was a N/S set from the picked east, so all jobs filed.
