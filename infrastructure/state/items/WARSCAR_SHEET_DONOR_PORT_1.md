# WARSCAR_SHEET_DONOR_PORT_1 — Warscar donor rows whose ruled art has no owned path

Source: owner's Warscar sheet, ruled 2026-10-05 (`Transient/biome_ffar/warscar_sheet_2026-10-05.decisions.json`; progress
`Transient/biome_ffar/warscar_close_progress_2026-10-05.md`). Same shape as `ABYSS_SHEET_DONOR_PORT_1`; machinery `DONOR_DEFS_PORT_TO_OURS_1`.

His picks on donor defs (no owned texture path, so NOT installed; labels/descriptions are already patched in
`src/RimUtinni/UtinniPatches/Patches/Warscar_Rename.xml`):
- `AA_Helixien` B (render `gapall_AA_Helixien_v1`), "Rename to Bileworm" — label/description patched.
- `SW_Juggernautbeetles` B (`gapall_SW_Juggernautbeetles_v1`), "Redo description" — description patched.
- `SW_Electricgryllotalpa` B (`gapall_SW_Electricgryllotalpa_v1`), `SW_Electrictick` B (`gapall_SW_Electrictick_v1`) — art picks only.
- `RG_Rimclaw` A with the in-game RimclawArtOverride picture, "redo description" — description patched; art already live.

When these port to owned `RM_`/`RSW_` defs (Insectoids 2 / Alpha Animals have no owned path), install those picks with `art.py install`.
