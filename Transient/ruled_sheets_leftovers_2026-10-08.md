# Ruled sheets leftovers, 2026-10-08

Six ruled sheets: FeverWood, Greentide, Miasma, Webwork, LeaningScrub, LongShade desert.

## 0. Redraws filed under a new name were missing from their rows (CanopySwinger / Ookala)
- **Cause:** the sheet attached artpipe renders to a row by matching NAME words. Jobs filed under the owner's new name (`regen_gt_ookala_v2_*` for `RM_CanopySwinger`) matched nothing. enact also counted the row as "already: 3 done", so it looked handled.
- **Fix:** `art_sheet.name_render_cols` now also attaches a render when its done job's `target_def` is one of the row's defs. enact matches jobs by `target_def` OR `target_original`.
- **Effect:** before the rebuild, 25 ruled rows had finished renders that were not on the row. After it, 22 are on their rows: Greentide CanopySwinger/Ookala, Diggerpede, Swarmling/Saluksis; Miasma Lockjaw/Siezer, Mantrap/Lastvine, PodWorm/Hellslantern, Swarmling, plus 15 variant rows.
- The 3 still missing (RM_Ulgga, RSW_Ulgga, RSW_Ultracactus → RM_UltrissPad) were moved to **RM_Stillsand**, as his notes asked. Their renders belong on a Stillsand sheet, and none exists yet.

## 1. Freshness on every sheet
- Each row shows the owner's last ruling (date, decision and note) and one of these states:
  - ✓ reflected
  - ✓ redrawn after your ruling
  - ⏳ awaiting render
  - ⏳ failed, re-filed
  - ⚠ needs your call
  - **NOT YET ACTED ON** (red)
- A banner under the title shows when the sheet was built, "X of Y prior rulings fully reflected", and lists every ruling that is not reflected.
- The state comes from `enact.ruling_status()`: the same plan `art.py enact` carries out. A ruling counts as reflected only when one of these exists: a render filed after it, a live pick, a done cut, or a note marked done with commit evidence.

## 2. enact bug fixed
- Failed jobs are re-filed: moved from failed/ back to pending/, with the old manifest parked; a job is re-filed at most 3 times. A job is skipped if it was already retried or a later job superseded it.
- Finished renders that are not installed are listed as **AWAITING OWNER PICK**.
- A pick you purged is reported as a CONFLICT.
- `--evidence "OWNER: …"` records the part of a note that is his call as a CONFLICT.
- `selftest_enact.py` has new cases and passes.
- **62 failed redraws re-filed:** FeverWood 6, Greentide 18, Miasma 9, Webwork 1, LeaningScrub 13, LongShade 15.
- No job spec was changed. Of the 62: 22 failed on worker errors, 21 failed the canon check, 18 were facings waiting on a failed master, and 1 was a run that reported OK but produced an invalid image. Lothcat v3 failed on the face line: its canon entry is already the live-action brief, so the render drifted and the spec is fine.

## 3. TODO notes (35 + 3 pick TODOs)
- 33 notes had already been carried out in earlier commits but were never marked done. They are now recorded with their commit as evidence:
  - FeverWood 4 (093caf2ca, ba560a36c)
  - Greentide 4 (ce1772c72)
  - Miasma 4 (af2b54fe2, 099966fd1)
  - LongShade 18: fd43623d8, dd54c128a, dfc35ba68, b5df5f05d, 70ec8378e, plus 3 approvals ("Nice!" / "Good!")
- Done now: the RM_SiltLampreyJuv (gillclamper) description, rewritten from pick A, and the RM_GreatDevourer label changed to "sarlacc seeker".
- Plant_Grass / Plant_TallGrass: the variant jobs are done (`regen_gt_grass_var{b,c}`, `regen_gt_tallgrass_var{b,c}`), so only his pick is left: it is a conflict (below).
- RM_HoardVenomvine: he said keep them all for now. Recorded as his deferral.

## 4. Deploys
- Every touched mod (LongShade, TerminalBiomes, FeverWood/Webwork textures) is folded into `RimMandrake.Biomes`.
- `--compose biomes` writes a DLL, and RimWorld is running, so the deploy is **SKIPPED until the next restart**.
- The LongShade enact had already deployed DewbackArtOverride, SWBestiary and UtinniPatches (6 files).

## 5. Conflicts for one owner card
1. **FeverWood: RM_Halquin and RM_Maulith.** Seven FeverWood plants (Ammeth, Cistrel, Halquin, Maulith, Nubrith, Plennith, Verrow) ship the SAME picture (25b911d827a8) as their `_a` art, which is a shared placeholder you kept as A. On Halquin and Maulith you also chose B as an extra variant.
   - Install B as a second variant (`_b`) and keep A.
   - Or: B replaces A.
   - Or: redraw all seven with art of their own.
2. **Greentide: VFEI2_Swarmling.** You ✕'d the 3 facings that the game shows today (TheRot `RotSpecies/Swarmling`).
   - Purge them and leave it without art until the Saluksis redraw (on the sheet now) is picked.
   - Or: keep them until you pick the replacement.
3. **Greentide: Plant_Grass / Plant_TallGrass.** Your pick B is a ReGrowth donor texture (`RG_Grass`) that no mod of ours ships.
   - Point vanilla grass at it, which changes grass on every biome.
   - Or: use it only as the model for the new variants (done; on the sheet).
4. **LongShade: RSW_Nerf.** Pick E is a render found by name, and the row has 3 graphics.
   - E replaces the body.
   - Or: E replaces the juvenile.
   - Or: E replaces the swimming graphic.
5. **Webwork: RM_Cravvet east.** You picked B east, but you had purged that picture (164c8ac583bc).
   - Keep the in-game east.
   - Or: un-purge and install B.
   - Or: redraw the east facing.
6. **LeaningScrub (also on the LongShade sheet): 8 live ✕.** These are Eopie ×3, Lothcat ×2 and Scurrier ×3.
   - Purge them now, and the creature shows no art until you pick the replacements: the eopie and scurrier redraws are done and on the sheets; Lothcat v3 was re-filed.
   - Or: keep them live until you pick.
7. **LongShade: GreatDevourer tier.** The RM_ row says "Lives at the RSW level"; the RSW_ row says "Not SW". It is relabelled "sarlacc seeker" and the canon link is removed.
   - RSW tier: the RM_ twin is retired.
   - Or: RimMandrake tier: it needs a name without "sarlacc", because that name is Star Wars IP.
