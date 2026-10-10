# Sheet live-variants fix — progress 2026-10-10

Goal: every picture the game can draw for a subject appears on its sheet row ("in game now, never shown").

- [x] 1. Find builder / candidate gathering
- [x] 2. Add game-drawn source + selftest
- [x] 3. Rebuild therot; dry-run all; rebuild affected
- [x] 4. Verify decisions survived; check served Rot sheet
- [x] 5. Note VioletWimple/Wrinklecap "A" ruling
- [ ] 6. Land

## Step 1-2 (builder) — DONE
- `art_sheet.random_folder_variants` + `build_row` 1a: a texPath that is a FOLDER in one of our mods puts every picture in it (masks, sub-folders excluded) on the row as its own `live` column, `random variant <name> (i of N)`; donor copies split per random variant when the ledger carries `random_variant`.
- `generate_biome`: a random-variant column is ✕-able; one whose pictures no earlier build of the row carried is labelled "in game now, never shown".
- `enact`: a ✕ on a picture that ships only inside the row's random folder retires it from the folder, then purges (never the folder's last picture, never a pick/kept one).
- `refresh_sheets.fingerprint` includes folder pictures. New `selftest_random_folder_variants.py` 8/8.
- Also: alternateGraphics (PawnKindDef) and plant immature/leafless graphics from the LIVE def dump (`gametex.def_extra_texpaths`, deftex schema 2) are added to each row as their own graphic group; `gametex ingest` now records every picture of a winning DONOR random folder (`random_variant`). Ingest run: 139 new ledger events.
- A folder picture within 2 dHash bits of one already shown is labelled "a re-encoded copy of set X", not "never shown". Baseline = the snapshot his decisions were saved against (`shown_base`, persisted as `shownBase`).

## Step 3-4 — DONE
- Rot: 13 never-shown columns on 5 rows + 9 re-encoded-copy columns; served URL (therot serve.log) answers 200 and its ITEMS carry them.
- All 27 sheets refreshed: 24 rebuilt, 3 unchanged. 16 OTHER sheets gained never-shown pictures (124 total): abyss 4, blue_desert 6, deep_desert 11, desert 19, floodedcanyon 4, gelatinousslime 6, greentide 1, lanterndeeps 33, leaningscrub 22, miasma 2, pyrelands 6, theforge 3, thescald 5, warscar 1, wasteland 1 (+ weepingstones: 2 copies only).
- Decisions: every owner-touched decisions file byte-identical in `decisions`; 0 decided letters changed by the rebuild (319 letters already absent from their ruled snapshots before — pre-existing, unchanged). theforge (never saved, prefill) got builder prefill picks for its new leafless graphics, by design.
- Selftests 360/365; the 3 FAILs are other windows' (ledger_lint FOUNDRY shard, one_path_seam l1_sweep/vanilla_beast_routes, tool_metadata DLL).
