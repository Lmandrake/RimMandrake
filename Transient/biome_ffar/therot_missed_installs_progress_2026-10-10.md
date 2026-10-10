# Rot missed installs — progress (2026-10-10)

Fixes the gaps found by `therot_newcols_verify_2026-10-10.md`. Script: `therot_missed_installs_2026-10-10.py`
(log `therot_missed_installs_apply_2026-10-10.log`). Every install went through `artledger.install` on his keep
ruling for that row/letter/sha. No notes acted on, no label/description edits.

## 1. AA_AngelMoth (C) — DONE
- C = east+north of `gapall_AA_AngelMoth_v1`, installed at `RotSpecies/AngelMoth/AngelMoth_{east,north}.png` (TheRot).
- **C has no south.** B's south (e42e8d35) is ✕'d and purged. The only south left was the Alpha Animals donor south
  (column A, c531ad6e), so it is installed as `AngelMoth_south.png` (mechanical `script:` reason, provenance
  donor-fallback). His note on the row asks for a new south ("Regenerate S"); that is not queued here.
- Patch in `RotSpecies_NamesAndSizes.xml` moves `PawnKindDef AA_AngelMoth` texPath
  `Things/Pawn/Animal/AA_AngelMoth/AA_AngelMoth` to `RotSpecies/AngelMoth/AngelMoth`. Two nodes match: the lifeStage
  body graphic and alternateGraphics li[1].
- **Still donor:** the donor kind has `alternateGraphicChance 1` with three alternates. AA_AngelMoth2 and AA_AngelMoth3
  (sheet D/E, not picked and not ✕'d) still draw the donor moth, so ours shows on about 1 in 3 moths. The larva and
  dessicated graphics are the donor's too.

## 2. MortalMorel D, PaleTree B/C, GreyLady C/D — DONE
MortalMorel_d, PaleTree_b, PaleTree_c, GreyLadyGrown_c and GreyLadyGrown_d are installed in their Graphic_Random folders.

## 3. AB_WitchesOyster B/C — DONE
- The `RotSpecies/WitchesOyster/` folder holds WitchesOyster_A (his existing pick, 780e2288), _b and _c. The single
  `RotSpecies/WitchesOyster.png` was retired through the ledger.
- A patch sets graphicClass to `Graphic_Random`. The donor (Alpha Biomes) declares Graphic_Single explicitly. The
  texPath patch was already in place.
- No other def uses the texPath. `RotGiants_HugeFootprint.xml` measured-variant `<texture>WitchesOyster</texture>` is now
  `WitchesOyster_A`. b/c have no measurements yet, so they use the union footprint fallback.

## 4. BlastpodShroom grown = E and F only — DONE (decision taken by question card)
`BoomshroomGrown_A.png` was retired through the ledger. C was already retired. The grown folder holds exactly _e and _f
in both src and the game copy, pixel-equal to sheet E/F.

## 5. Young-plant redraws queued — DONE (decision taken by question card)
- `rotimmature_blastpodshroom_v1`: reference is grown pick E (00c49ae5). Target is `.../Boomshroom/BoomshroomImmature`.
- `rotimmature_greylady_v1`: reference is grown pick B (0ec42b4a, GreyLadyGrown_A). Target is `.../GreyLady/GreyLadyImmature`.
- Neither job references the rejected young pictures. Rows: `therot_young_jobs_2026-10-10.json`.
- **The rejected young pictures stay live** (`BoomshroomImmature.png`, `GreyLadyImmature_a.png`) until the new ones are
  approved on the sheet. Each is the only young picture its plant has.

## Validation / pixel checks
- validate_patch (full mod set FULL.LATEST): 0 errors. One new warning: the AngelMoth op matches 2 nodes, which is
  intended.
- All 13 installed images are pixel-equal to the sheet candidate sha in both src and the deployed game copy (26 of 26).

## Deploy
`deploy_custom_mods.py --compose biomes --apply --prune`: 16 changes, VERIFIED in sync. No DLL in the plan, nothing
refused. Needs a game restart.

## Landing
See commit (pushed by literal sha to origin/main).
