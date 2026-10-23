# Art-eval pilot — GPT vs Opus blind race (2026-10-23)

Status: **BUNDLE BUILT, no reviewer run yet.** Builder (committed):
`src/RimMandrake/Utils/art_eval/build_pilot_bundle.py` (re-run: ~20 s; `--dry-run` prints the reconstruction).

Owner, 2026-10-23: *"Please make a review sheet for one biome with flora and fauna shown. Write prompts on how to
evaluate flora and fauna types … Then provide it a sheet with each item's description and associated art. Then
race GPT vs. Opus 5.5."*

| path | what |
|---|---|
| `bundle/items/NN_<defName>/` | per subject: `card.md` + `card.json`, `page_facings.png` (candidates × facings), `page_flight.png` (flyer frames), `<L>_<facing>.png` full-res pictures, `<L>_scale_full.png` true-scale panel per candidate |
| `bundle/contact/<class>_pN.png` | one contact sheet per class (most frontal facing of every candidate) |
| `bundle/manifest.json` | items, class, candidate letters, biome intent text |
| `prompts/` | `00_preamble.md` (conventions, style law, verdicts, reason codes, JSON output) + 8 class prompts + `README.md` (assembly table) |
| `answer_key.json` | **HIDDEN** ground truth — never hand to a reviewer |

Pinned in git: this README, prompts, answer key, manifest and every card. The PNGs (42 MB) are derived and live
only in the BENCH clone; rebuild them anywhere with the builder above.

## Biome chosen and why
**RM_WeepingStones** (sheet `weepingstones_sheet_2026-10-05`, owner sitting 2026-10-10 07:06–07:50 PDT).
- 47 of its 51 rows carry an owner `at` stamp from that sitting (the other 4 — Bantha, Dewback, Eopie, Jamel —
  were "already ruled on another sheet" and are excluded). 38 rows carry an owner note; the notes are mostly about
  the ART ("Image is too cute…", "less recognizably camel", "crest-fan isn't rotating with the creature
  properly", "Old Flyer art must be removed").
- Covers ground cover, bushes, a tree, hanging growth, walkers, pack animals, swimmers, amphibians, flyers (one with
  a flight flip-book), and catch items.
- Rejected: `rot_flora_fauna_review_2026-09-18` (55 rows, owner-ruled, but 46/55 are "regen … rename" on donor
  art — provenance + naming, little art signal); `therot_sheet_2026-10-05` (notes mostly names/descriptions);
  pick-one sheets still in `prefill` state (no owner ruling); `deeps_flora_fauna_review` (16 rows).

## Item count by class (47 subjects, 141 candidate pictures-sets)

| class | n | owner verdicts |
|---|---|---|
| flora/ground_cover | 3 | KEEP 3 |
| flora/bush | 8 | KEEP 7, REDO 1 |
| flora/tree | 1 | KEEP 1 |
| flora/special (hanging) | 1 | KEEP 1 |
| fauna/walker | 7 | KEEP 5, REDO 2 |
| fauna/walker_pack | 2 | KEEP 1, REDO 1 |
| fauna/flyer | 3 | KEEP 1, REDO 1, CUT 1 |
| fauna/swimmer | 7 | KEEP 2, REDO 5 |
| fauna/amphibious | 2 | KEEP 2 |
| item/catch | 13 | KEEP 5, REDO 8 |
| **total** | **47** | **KEEP 28, REDO 18, CUT 1** |

Flora 13, fauna 21, catch items 13. Candidate status mix in the key: pick 27, keep_variant 10, keep_other_slot 7,
retained_as_reference 26, not_chosen 46, purged 18, rejected 7.

## Ground truth (answer_key.json)
Per subject: `verdict` (KEEP/REDO/CUT), `pick`, per-candidate status, his notes verbatim, `art_judgeable`,
`caveats`, provenance (decisions file + art-ledger event ids). Built from
`Transient/biome_ffar/weepingstones_sheet_2026-10-05.decisions.json` (per-row owner `at` stamps; `notes_followed`
keep his original words) and the art ledger's `by: owner` events for this sheet (exact shas per letter, purges).
Caveats flagged on 8 rows: 6 reconstructed letterings (below), Tirbak (pick A has no surviving picture), Mirrik
(CUT for a roster reason — exclude from art scoring), Dactillion (his "remove F" note vs a ledger keep on F).

Suggested scoring: row verdict agreement (KEEP/REDO/CUT) as the headline; pick agreement on KEEP rows; delete-set
vs his `purged`+`rejected`; and a human read of whether each reviewer's `note` names the defect his note names.

## How images were obtained
- **No game, no capture.** Every picture is a texture file: the sheet he ruled lists, per candidate and facing,
  the sha256 of the PNG; bytes come from the content-addressed artstore (`D:\ClaudeWork\rimmandrake\artstore`,
  via `artledger.store_get`) — 273 pictures at full resolution.
- **17 pictures (4 rows: Boma, Fanback, Ollopom, Dactillion) are sheet thumbnails from git** — he purged them,
  so the artstore dropped the bytes; the sheet's own `img/*.webp` at commit `01b5cdb299` survives. Their
  `card.md` says "reduced resolution".
- **Which sheet he saw:** the last committed build before his sitting is `01b5cdb299` (2026-10-09). Renders
  landed between that build and his sitting, so 6 rows (Boma, Dactillion, Fanback, Ollopom, Dewshrooms,
  MurrinCatch) were relettered/extended from the art ledger's owner events, which record the exact shas under
  each letter he ruled. The other 41 rows match the committed sheet exactly.
- **True-scale panels** are rendered per candidate by the sheet's own `scale_panel.render_panel` (vanilla human +
  rat, max zoom, 32 px/cell, 18 px/cell), sizes from the live def dump recorded in the sheet. The owner's sheet
  showed ONE panel per row (the prefill candidate); the bundle gives one per candidate.
- Class needs: plants and catches = one `single` picture; creatures = south/east/north; amphibians add a swimming
  lane; Dactillion adds 12 flight frames (4 × 3 directions, own page). No class needed an in-game capture.
- Image limit: every PNG ≤ 2000 px on the long side (`gpt_consult.py` has no limit of its own; codex/OpenAI vision
  and Claude many-image requests both downscale past ~2000). Bundle 42 MB.

## Time to build
05:07:39 → ~05:20 PDT by the wall clock (`date`), of which the build script runs ~20 s. Most of the time went to
choosing the biome and reconstructing which sheet he actually saw.

## What was hard (feeds the design doc)
1. **The sheet he ruled is not on disk.** Sheet HTML is rebuilt after enactment and was untracked from
   2026-10-18; the ruled version had to be rebuilt from git (`01b5cdb299`) plus ledger shas, and 6 rows had
   drifted letters. Fix: snapshot the sheet's ITEMS JSON (shas per letter) into the decisions file at save time.
2. **The verdicts are pick-one, not KEEP/REDO per picture.** His sheet asks "which letter", so per-picture truth
   is derived (pick / variant / purged / not chosen). "Not chosen" is not "bad"; scoring must not treat it as REDO.
3. **Purged art loses its bytes.** The artstore drops purged pictures; only thumbnails survive. A grading corpus
   needs the rejected art kept (rejects are the most informative examples).
4. **Notes mix art and non-art.** Many of his notes are about names/descriptions ("Improve description", "Rename
   to …"); a few verdicts are design calls (Mirrik CUT: "no longer needed"). The key flags these.
5. **Ledger self-contradictions** (Dactillion F; Tirbak's pick A with no shas) — flagged as caveats, not resolved.
6. **Prompt leakage.** Owner quotes in the prompts are taken only from OTHER sheets (and dated sources); quotes
   from this sitting appear only in the answer key. Several cited quotes postdate 2026-10-10 — they are his
   standing taste, equally available to both racers.
