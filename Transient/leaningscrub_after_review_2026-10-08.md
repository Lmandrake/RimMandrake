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

## Follow-ups 2026-10-08

**Art queued at priority 0** (via `fill_queue.py`, rows in `Transient/leaningscrub_ls3_jobs_2026-10-08.json`; each carries his sheet note verbatim as `owner_note`, the picked column's art as `canon_reference`, canon entry where one exists). 19 job files:
- `ls3_fuzz_{a,b}_v1`, `ls3_tanglefuzz_{a,b}_v1`, `ls3_whipfuzz_{a,b}_v1` (variations of the picked look)
- `ls3_wildhealroot_{a,b}_v1` (more realistic and special, variations)
- `ls3_nysyllin_{a,b}_v1` (realistic, two variants, canon `nysillin`)
- `ls3_pufferpig_v1_{east,south,north}`, `ls3_qormot_v1_{east,south,north}` (more realistic, canon entries)
- `ls3_ronto_v1_{east,south,north}` (one variant, canon `ronto`)

**Def edits**
- `RSW_Kreetle` (our SWBestiary def): all three life stages' drawSize scaled to 0.15 / 0.22 / 0.30 (adult 1.0 -> 0.3, body and dessicated). The report said adult was 0.75; that is the juvenile stage, the adult was 1.0.
- `RM_Durrok` description rewritten to the image (low barrel body, no hump, no visible head, glossy hair ropes, lichen mats): `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml`.
- `RM_Dustflutter` wildGroupSize 8~20 -> 40~100 ("great numbers"; its description already says a hundred): `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml`. drawSize 0.3 was already done.

**Not done: `RSW_Scurrier` install.** The ruling is contradictory on the sheet: row pick C, but the per-graphic picks keep E for the female (live, PROTECTED owner-kept `Scurrier_f`) and B for the male. Installing C would overwrite a protected owner-kept picture, so nothing was installed. Needs his answer: is C meant to replace E?

## Purges 2026-10-08

Decision taken by question card (a click, not an owner quote): run every ✕ except the 2 on `RM_HoardVenomvine`.
`art.py purge` takes one sha and has no dry-run or exclusion flag, so a filtered loop over the decisions file called `artledger.purge` directly with `release_keep=False`.
- 296 marks: 195 already purged earlier, **82 purged now**, 2 HoardVenomvine held (both pictures still on disk; wait for `LEANINGSCRUB_VENOMVINE_SITTING_1`), **17 refused and left alone**.
- The 17 are live in a mod or carry an owner keep: RSW_Eopie 6 (3 live, 3 kept), RSW_Lothcat 2 (live), RSW_Scurrier 6 (kept), RSW_Strill 3 (kept). Ingest would have released those keeps; that was not done. They need his word.

**Scurrier male installed 2026-10-08** (decision taken by question card, a click): B installed as `Scurrier_m_{east,north,south}.png` via `art.py install` (ruling 9bef29092ae5f0d40665, sheet's per-graphic B pick); female `Scurrier_f` (E) untouched, C not used. Not deployed.
