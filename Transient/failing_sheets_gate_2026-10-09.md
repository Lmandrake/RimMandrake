# Failing sheets gate 2026-10-09

Before: 15 pass / 12 fail of 27 (biome_ffar). After: 27/27 pass. All 12 were class (a) STALE; no tool defect, no missing data.
Cause per sheet (requirement): reqs 6/7/14 drifted because ledger purges, other sheets' rulings and canon-gate records changed after the sheet was built.
- abyss 6 (Olumetha B badged but gate says pass) | deep_desert 6 (Soorrak E) | twilightsea 6 (Mee B)
- desert 6 (Nerf F badged-but-passed; Shyrack G failed canon, unbadged) | greentide 6 (PekoPeko N unbadged)
- cauldron 7+14 | pyrelands 7+14 | theforge 7+14 | therot 7+14 (rows ruled on greentide/miasma shown live; purged pics still columns)
- floodedcanyon 14 | wasteland 14 | weepingstones 14 (purged pictures still shown)
Fix: `refresh_sheets.py --force --only <base>` x12 (substring also rebuilt blue_desert, which already passed). Gate-then-replace; all 13 rebuilt.

Decisions files: code (refresh_sheets -> art_sheet.generate_biome) rebuilds HTML only when a sheet has saved decisions (sheet_only) and never overwrites a ruled file.
sha1 before/after: 7 files byte-identical (abyss, blue_desert, deep_desert, desert, greentide, pyrelands, twilightsea: "NOT rewritten" warning, letters may be stale).
6 rewritten: cauldron, floodedcanyon, theforge, therot, wasteland, weepingstones. Verified from HEAD copies: all machine PREFILL only
(reviewStatus.state=prefill, 0 `at` stamps, decision==prefill on every row, 0 notes) so no human ruling lost; letters/snapshotId re-derived for the new columns.

enact PREVIEW (never applied) after rebuild, NEW stale-letter conflicts ("clicked before the sheet's columns were rebuilt"):
- abyss: RM_GiantFibreStalk A, RM_GlowingGrass E, RM_Nevarithia A, RM_SicklyGlowMushroom A
- greentide: RSW_Beldon H,J
- twilightsea: RM_DancingSkresh A, RM_GrippingTerror A
- none on blue_desert, cauldron, deep_desert, desert, floodedcanyon, pyrelands, theforge, therot, wasteland, weepingstones.
These are correct (the guard); owner must re-confirm those rows. Other pre-existing conflicts (not-purged, by-name picks, tier) unchanged in kind.
