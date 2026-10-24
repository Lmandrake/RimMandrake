# WORLDFACE_SHEET_FIX_WIPE_BEFORE_SOURCE

src/RimMandrake/Utils/art/world_face_variants.py `build_sheet` deletes every file in
Transient/world_faces_review_2026-10-23_img/ BEFORE it lists `<out>/sheet`. With a wrong `--out` or no prior `gen`
the listdir raises and the owner's served sheet is left with no pictures. Also the brief always embeds
`reference_september.jpg`, which `thumbs` only writes when the September screenshot exists (broken image otherwise).

Fix direction: check `<out>/sheet` and `stats.json` exist (or build into a temp dir and swap) before wiping; emit the
reference <img> only when the file was copied. Found by full-file review (FOUNDRY 2026-10-24).
