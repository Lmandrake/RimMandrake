# The Rot sheet — fix pass 2026-10-10

Sources: therot_verify_2026-10-10.md (independent check), therot_enact_progress_2026-10-10.md.
Ground truth: therot_sheet_2026-10-05.decisions.json + sheet HTML.

## 1. Brightbell ✕'d picture + Rot-wide decoded-pixel sweep — DONE
- `Brightbell_p3a.png` (99e967d0, pixel-identical to ✕'d B 465c0328) retired via `artledger.retire`, and its bytes purged under the same sheet ruling.
- Sweep: all 9,399 PNGs under `src/`, decoded RGBA hash vs the 22 Rot ✕'d pictures (18 had source pixels from `_artpipe/_artsrc` or git; all 22 by dhash from `phash_cache.json`). Exact pixel hits: **1** (Brightbell_p3a, now gone). Near (dhash ≤12): LanternDeeps `NurrikGill/A,B` and `VellokReed/B`, mean pixel diff 4.8/6.9/3.1 vs the ✕'d Nuitae D/E and Arpeau E. These are separate Lantern Deeps redraws installed at 67623b0fb, not copies; left alone.
- Ledger bug found and fixed: `Index._fold_live` dropped a retire when another seat's older install of the same slot folded later (shards fold one seat after another), so a retired slot read as live again. Retires now leave a tombstone (`artledger.py`). Art selftests all pass.
- ⚠️ A concurrent `git pull --rebase --autostash` in this clone (naming-sheet commit 4f3056e31, 09:07:55) reverted the first 6 retires mid-run; redone.
## 2. VioletWimple / Wrinklecap variant jobs re-filed
pending
## 3. Pusmelon / Sagecrust B retired — DONE
- `BMT_PusmelonB.png` (569cc808), `BMT_SagecrustB.png` (94760ef0) retired via the ledger. Pusmelon draws only his pick B (`Pusmelon_A.png`), Sagecrust only his pick C (`Sagecrust_A.png`).
## 4. Duplicate installs removed — DONE
- Retired the pre-sheet `_p3a/_p3b` copies whose pixels already ship under the sheet's names: Arpeau_p3a/p3b (= Arpeau_C/B resized), Nuitae_p3a/p3b (= B/C), ShinecapGrown_p3a/p3b (= b/c), ShinecapImmature_p3a/p3b (= d/e), Brightbell_p3b (= Brightbell_A, his pick C), MortalMorel_p3a (= MortalMorel_A, his pick B). No pixel duplicates remain in any Rot plant folder.
- `RotGiants_HugeFootprint.xml` regenerated (Arpeau now A/B/C); `selftest_hugethings_footprint.py` expectations updated, 16/16 PASS.
- MortalMorel_p3b (his default-ticked C) left live — a default tick, not a duplicate.
## 5. Unshown folders — owner question
pending
## 6. Pluur'va dessicated drawSize — DONE
- `RotSpecies_NamesAndSizes.xml`: `dessicatedBodyGraphicData/drawSize` on AA_AnimaColossus lifeStages 1-3 now 12/15/18 (donor 4/5/6 ×3), matching the body. validate_patch OK.
## 7. RM_ThozzikSpawned deleted; Thozzik B ✕s; queens kept — DONE
- Decision taken by question card 2026-10-10: delete RM_ThozzikSpawned. Removed its ThingDef + PawnKindDef (`RM_TheRot_Fauna_ThingDefs_Races.xml`) and its 0.2 row in `RM_TheRot_Biome.xml`; dropped it from `TheRot/validation.py` CAST and `port_fauna.py` maps. References checked: no hive spawner, PawnKindDef, patch or C# names it (acoustic-payload lists name only Colony/ColonyQueen/Queen); nothing to repoint. TheRot validation STATIC PASS.
- His 3 ✕s on RM_Thozzik render B (b2ec037d/1f3992e7/93971b55) purged; the only keep on those bytes was RM_ThozzikSpawned's default variant tick, released with it.
- Decision taken by question card 2026-10-10: keep BOTH RM_ThozzikQueen (wild hive queen) and RM_ThozzikColonyQueen (tame colony queen).
## 8. Variant-job grading fix
pending
## 9. Prune
pending
## Re-verify (43 rows)
pending
