# XENO_HEADS_VERIFY_BALD_AND_BLUSHING live results (2026-10-20, helper run)

Overall: PASS on every measurable bullet; skin-colour state read UNMEASURED directly (no bridge tool reads story.SkinColor), checked via genes + pixels.

## Step 1 harvest (menu-stage log playerlog_menu.txt)
- `MEASURE_ALLOW_SCAN=1 grep -n` for Mimbanese_Head, Ortolan_Head, RSW_Mimbanese_Head, RSW_Ortolan_Head, DefModExt_HeadTypeStuff: 0 lines. PASS (no error/texture-miss naming them; heads then drew live).

## Step 2 spawn
Map_0 (RM_Stillsand 250x250), tick 15002, 12 PM, Clear, paused. Site x44..74, z72 (cleared, SterileTile). Fresh pawns: 2 Baseliner, 4 Lasat (2 female; one made female with set_pawn_gender, hair stayed Bald), 3 Nelvaanian, 3 Mimbanese, 2 Ortolan (Hulk + Fat via set_pawn_appearance). Apparel stripped, drafted. Ids Human689068..689120. FA ignore list held (our heads draw, humans keep anime face).

## Step 3 state reads (jawa/pawn_get + jawa/pawn_genes list)
| species | n | hair | headType | bodyType | removed genes present | Ears_Human | skin genes |
|---|---|---|---|---|---|---|---|
| Lasat | 4 (2F) | Bald x4 PASS | RSW_Lasat_Head | Male/Female/Hulk | none (RSW_FacialRidges_bumpy kept as designed) | yes x4 | Lasat roll unchanged |
| Nelvaanian | 3 | Bald x3 PASS | RSW_Nelvaanian_Head | Female/Male | none | yes x3 | RSW_Skin_SlateBlue |
| Mimbanese | 3 | Bald | RSW_Mimbanese_Head x3 PASS | Thin | none; no ridges/eyes/brow genes | no (not required) | Skin_DeepRed only (no Brown/MidGray) |
| Ortolan | 2 | Bald | RSW_Ortolan_Head | Hulk, Fat | none | yes x2 | Outland_Skin_DeepAzure only (no Blue/PaleAzure) |
- Skin colour numeric (0.59,0.24,0.24)/(0.29,0.42,0.65): UNMEASURED directly; the sole skin-override gene per species is the intended one (PASS by genes). Pixel check below.

## Step 4 pictures (zoom 13, 4 facings)
- Lasat/Nelvaanian no hair mesh over head, all facings: PASS. (Nelvaanian black mane in east/north/west is the painted head, matches Nelvaanian_Head_east.png.)
- Mimbanese body red, head same red family, not darkened: PASS. Pixels (south, 12px sample): head 128,63,56 vs body 131,60,58; painting mean 140,76,71. East/north fine.
- Ortolan east/west head height same as south, north unchanged: PASS (visual).
- Ortolan head painted blue, not darker than body: PASS. Head sample 104,142,184 / 128,166,209 vs body 75,101,144 (head lighter; painting mean 64,108,169). Matches painting by eye.
- No second ears / extra eyes, no ridge overlay on Mimbanese: PASS (only painted features visible).
- Lasat RSW_FacialRidges_bumpy overlay (kept): reads as the painted forehead stripes, not wrong. Lasat bodies are pale grey vs dark-purple-grey heads (skin-tinted body vs painted head) - note for owner, not a defect of this item.
- Note: Lasat head draws darker/larger Hulk body on one pawn; all fine.

## Screenshots (C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\)
- xeno_heads_v3_{south,east,north,west}.png (whole line-up, frame cuts off ends)
- xeno_heads_v3A_{south,east,north,west}.png (humans, Lasat, Nelvaanian) and xeno_heads_v3B_{south,east,north,west}.png (Nelvaanian, Mimbanese, Ortolan) - best ones
- xeno_heads_v3_Lasat_*.png, xeno_heads_v3_Nelv_*.png (camera min zoom 11, not closer)
- Scratch crops/bands: D:\ClaudeWork\rimmandrake\scratch\xeno\

## Defects
None in the four heads. Tooling gap: no bridge read for skin colour. Test pawns left on map (save untouched, not saved).
