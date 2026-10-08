# Leaning Scrub after review — 2026-10-08

Sheet `leaningscrub_sheet_2026-10-05` (RM_LeaningScrub), 86 rows. Decisions read from
`D:\Luke\dev\RimMandrake\Transient\biome_ffar\leaningscrub_sheet_2026-10-05.decisions.json`. The sidecar writes this file on every
click (savedAt 08:07:45 today, writeCount 646), so what is on disk is what the server holds.

## Your question: "waiting on graphics likely?"

**Partly.** 33 rows are not done:
- **9 are waiting on renders that are already queued** (artpipe pending, nothing running yet).
- **8 are waiting on renders that are NOT queued.** Nobody has filed a regen job for your note.
- **8 are venomvine rows**, held for the in-game sitting.
- **5 need something other than art**: a def edit or an install.
- **3 are cuts.**

The other 53 are done: the picked column is what the game shows. That was checked against the art ledger's live shas, not against the sheet labels.

## Cuts enacted

- **Needlepost** (`RM_Skorra` row, formerly `RSW_Skorra`. The game def is `AA_Needlepost`, from Alpha Animals). Removed from
  `RM_LeaningScrub` wildAnimals in `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml`.
  The def is a donor's, so nothing was deleted. It stays in the Greentide (`WildAnimals_Greentide.xml`) and in the frozen
  `RUT_AridShrubland`/`RUT_Greentide`, all untouched. An earlier close pass (2026-10-05) recorded "Skorra is not in the LS roster". That was wrong:
  it searched by the port name, but the row is the needlepost.
- **Imperial toad** (`RSW_ImperialToad`). Already out of the roster since 2026-10-05, so there was nothing left to cut.

## Rulings recorded

- Permanent copy refreshed: `infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json`.
- Art ledger: `art.py ingest`'s logic, run with `--defer-redo-jobs`, appended **63 new ruling events + 1 rejected** to
  `infrastructure/state/art/events/BENCH.jsonl`. These are this morning's changed picks and notes, recorded as decisions taken by sheet.
  Every keep, pick, variant and redo note is now in the ledger for when the renders land.
- **Purges NOT executed.** Ingest would have run the ✕ purges on your pictures, and that release-keep step is destructive. It also
  includes 2 on `RM_HoardVenomvine`, which you said to keep. Those ✕ marks are still in the decisions file. They are for the close step
  (`art.py purge`) once the replacements are in.

## Venomvine

Filed `LEANINGSCRUB_VENOMVINE_SITTING_1` (for BENCH, needs owner + game up). It quotes your sentence and lists all 8 sheet rows. It also lists
3 roster forms that have no sheet row at all (Walking, Sworn, Shedding). Prose:
`infrastructure/state/items/LEANINGSCRUB_VENOMVINE_SITTING_1.md`.

## Rows not done: what each waits on

| row | pick | picked column | his note | waits on | detail |
|---|---|---|---|---|---|
| `RM_CrownVenomvine` | B | render gapfin_RM_CrownVenomvine_v1 |  | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_DrippingVenomvine` | B | render gapfin_RM_DrippingVenomvine_v1 |  | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_Durrok` | A | IN GAME — SWBestiary | Change the description to match the image, get inspired. | **other** | def edit owed: rewrite description to the image (his note) |
| `RM_Dustflutter` | A | IN GAME — LeaningScrub | Make this 0.3 cells wide and in great numbers | **other** | drawSize 0.3 done 2026-10-05; "in great numbers" (herd size / commonality) not verified |
| `RM_Fuzz` | B | render gapall_RM_Fuzz_v1 | variations | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RM_HoardVenomvine` | J | render 0vv_hoard_venomvine_v2 | Keep all of these for now, Venomvine is a mechanic as well as graphics | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_HollowVenomvine` | A | our deployed art (render RM_HollowVenomvine)  |  | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_QuenchVenomvine` | redo |  | STOP USING THIS GRAPHIC AND MAKE VENOMVINE! | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_RearingVenomvine` | redo |  | STOP USING THIS GRAPHIC AND MAKE VENOMVINE! | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_Skorra` | hold |  | Just cut this, not needed | **cut** | CUT now: AA_Needlepost removed from RM_LeaningScrub wildAnimals |
| `RM_Tanglefuzz` | A | our deployed art (render RM_Tanglefuzz) — Rim | variations | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RM_TwitcherVenomvine` | A | our deployed art (render RM_TwitcherVenomvine | variations | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_VenomvineThicket` | B | render ls_regen_RM_Venomvine_v1 | variations | **venomvine** | held for LEANINGSCRUB_VENOMVINE_SITTING_1 (in game, with him) |
| `RM_Whipfuzz` | A | our deployed art (render RM_Whipfuzz) — RimMa | variations | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RM_WildHealroot` | redo |  | more realistic and special, variations | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RM_Zellik` | B | IN GAME — LeaningScrub | Make this more alien | **art-queued** | waits on artpipe: 6 job file(s) pending (regen_ls2_x_zellik…) |
| `RSW_Convor` | redo |  | D is close, but please make it less cute now | **art-queued** | waits on artpipe: 6 job file(s) pending (regen_ls2_canon_convor…) |
| `RSW_Durrok` | B | render rot_wildpawn_v2 | Change the description to match the image, get inspired. | **other** | old name of RM_Durrok; picked render B is live; description rewrite still owed (see RM_Durrok) |
| `RSW_Grank` | E | render leaningscrub_grank_v1 — failed canon c | Follow canon PRECISELY, look at the parent image. Make North and South | **art-queued** | east is live; north/south: 2 job files pending (regen_ls2_canon_grank…) |
| `RSW_ImperialToad` | hold |  | no longer needed | **cut** | already out of the roster (2026-10-05); nothing left to cut |
| `RSW_Kreetle` | J | IN GAME — KreetleArtOverride | Should be only 0.3 cell | **other** | def edit owed: adult drawSize is 0.75 in RSW_Kreetle.xml, he asked 0.3 cell |
| `RSW_Kybuck` | redo |  | Almost there, but you missed the canon bone plate on top of its head m | **art-queued** | waits on artpipe: 6 job file(s) pending (regen_ls2_canon_kybuck…) |
| `RSW_Lothcat` | D | render leaningscrub_lothcat_v1 — failed canon | Now just north and south. Less cartoonish please | **art-queued** | east is live; north/south: 2 job files pending (regen_ls2_canon_lothcat…) |
| `RSW_Plant_Nysyllin_Wild` | redo |  | Ok, now make a realistic version based on this, two variants | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RSW_Pufferpig` | C | IN GAME — SWBestiary | Please make a more realistic variant now based on this version. | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RSW_Qormot` | C | IN GAME — SWBestiary | Please make a more realistic version based on this version to consider | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RSW_Ronto` | B | IN GAME — RontoArtOverride | Please make one variant based on this version and canon to consider | **art-NOT-queued** | waits on a render that is NOT queued; no pending/active artpipe job matches |
| `RSW_ScrapNestBird` | redo |  | Redo to canon very carefully. | **art-queued** | waits on artpipe: 6 job file(s) pending (regen_ls2_x_scrapnestbird…) |
| `RSW_Scurrier` | C | render stillsand_regen_RSW_Scurrier_v2 |  | **other** | picked render C is NOT live: install owed (art.py install), no new graphics needed |
| `RSW_Sketto` | B | render longshade_rsw_sketto_v1 — failed canon | Yes, now do North and South | **art-queued** | east is live; north/south he asked for: 14 job files pending (regen_ls_canon_sketto…) |
| `RSW_Skorra` | hold |  | Just cut this, not needed | **cut** | old name of RM_Skorra; same cut |
| `RSW_Urusai` | C | IN GAME — SWBestiary | Redo to canon imagery | **art-queued** | waits on artpipe: 6 job file(s) pending (regen_ls2_canon_urusai…) |
| `RSW_Whisperbird` | F | render leaningscrub_whisperbird_v1 — failed c | Good! Now north, south, and flying frames | **art-queued** | east is live; north/south + flying frames: 14 job files pending (regen_ls2_canon_whisperbird…) |
