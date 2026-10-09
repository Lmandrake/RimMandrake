# ART_SUBJECT_RESOLVER_1 status 2026-10-09
Spec: design/RimMandrake/art_resolution_rootcause_2026-10-04.md (item file absent; spec §5).
Criteria:
- 5.1 subject.py with bound/name-matched/none + Searched record: MET (9f6c5d948, 39d25dd42, c6e6be2c0)
- 5.1 census (biome_census), sheet (art_sheet, refresh_sheets, scaled_review_gate) use it for art+canon: MET
- 5.2 fill_queue requires target_def, canon default reference, canon_check uses resolve_canon: MET
- 5.2 backfill.step_artpipe reads target_def/install_to: NOT MET (backfill has no target_def read)
- 5.3 backfill of 2,860 renders (bind steps 1-3): NOT MET (unverified/none found)
- 5.4 one-liners (folder-word alias, right boundary, has_art counts name joins, variant-stripped canon): MET
- Retire name logic: artpipe_state.find (substring on names+prompts), make_verdict_sheet.creature_of, art_sheet.canon_entry/_canon_dirname, canon_state: NOT MET
Migrated tonight: biome_census.canon_index -> World.canon_index (265 == 265, identical); art_sheet.canon_base variant vocab -> S.VARIANT_WORDS/S.words. Diff over 958 census keys: 1 change, RSW_GreaterKraytDragon -> kraytdragon (subject lists greater/lesser as variant words; correct, base species entry). Selftests GREEN 282/349.
