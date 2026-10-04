# Doubles sheet follow-up — 2026-10-04

Sheet: `D:\Luke\dev\RimMandrake\Transient\art_doubles_compare_2026-10-04.html` · decisions
`Transient/art_doubles_compare_2026-10-04.decisions.json`.

## 1. Decisions ingested (`6f7e3498f`)

- `art ingest`: 12 owner rulings + his 9 Nuna purges (history E/F, render C) executed.
- **Nuna_m** keep B added by hand: ingest's purge-only guard skipped the row (purgeTouched, no
  decidedAt) though it carries decision B + his typed "Good!".
- **Eopie A–E, Eopie_j**: his B clicks say "redundant with above" — released (not protected) and
  re-ruled as `redo` following the Eopie redo (`by: agent`, `trust: interpretation`).
- Redo rows (Bantha W / W_j, Dalgo, Eopie, Iriaz) carry his notes verbatim.

## 2. Nuna B installed

- Owning mod = `NunaArtOverride` (design §2.3: the override mod owns its art). `art install` of all six
  B shas returned `already-live` there; the six `SWBestiary` copies were archived to the art store and
  removed (`live` retire events + `owner` events).
- **Not deployed**: the game was RUNNING (bridge answers) at 08:26. FOUNDRY owes
  `deploy_custom_mods.py --mod SWBestiary` with prune (the game copy still holds the six PNGs that
  shadow Nuna B) — plan first, then `--apply`.

## 3. Redos — 16 artpipe jobs queued (pending, `D:\Luke\dev\_artpipe\pending\doubles_redo_*`)

Rows: `infrastructure/state/art/jobs/doubles_redo_2026-10-04.json`. Every row carries `canon: <slug>`, so
fill_queue appends that entry's `## Visual brief` + `## Must show`, plus the house register (realistic
painted natural-history, matte, soft painted edges, never cartoonish, no outlines). Fresh rows file
east as master and north/south `derive_from` it (the daemon waits for the east verdict). Each job has a
`job` event in the art ledger tied to his redo ruling. **Nothing is wired.** Renders come back to him on a sheet.

| creature | jobs | how the brief encodes his criteria |
|---|---|---|
| Bantha bull (`BanthaW`) | `doubles_redo_bantha_w_v1` east (generated) + north/south (derived) | The canon `## Must show` gains a line for the **very wide, flat, slit-like mouth** (from `wookieepedia_infobox.jpg`). The prompt makes the face the priority and spells the mouth out in capitals. |
| Bantha cow (`BanthaW_j`) | `doubles_redo_bantha_wj_v1` ×3 | Same species, look and slit mouth as the bull. **Short** horns curl only half a turn. ⚠️ `RSW_Bantha` uses `BanthaW_j` for the **calf** stage today, so where the female art goes is decided when it comes back. |
| Dalgo | `doubles_redo_dalgo_v1` ×3, 512 px (drawSize 3) | A **fresh render, not an edit of C**. C is a flat cartoon on a low body, which breaks both the art law and canon. The brief keeps what he liked in C (sail crest, tusked snout, rust over cream) on the canon long-legged runner body from `wookieepedia_sot_art.png`, his 2026-09-14 reference. |
| Eopie | `doubles_redo_eopie_v1` ×3 | Canon look: hairless, wrinkled pale hide, camel body on thin legs, tapir trunk, one eye set far back. The shipped B was drawn with fur, which canon does not show. |
| Eopie calf (`Eopie_j`) | `doubles_redo_eopie_j_v1` ×3 | Same body plan as the adult in foal proportions. |
| Eopie A–E | **not queued** | All five are near-identical copies of the base sprite. Once he approves the Eopie master, they take it, or tone variants derived from it. |
| Iriaz | `doubles_redo_iriaz_edit_v1_east` (**edit of B**, reference = shipped `IriazArtOverride` east) | The edit adds a matched **second ridged horn** and softens B's contour line into painted edges. It keeps the **four legs** and the **green-olive hide** with orange spots. North/south are filed only after he approves this east. The canon entry now says two horns + four legs; the old 2026-09-17 one-horn lock is superseded. |

The canon entries now carry his 2026-10-04 words in `## ruling`: `bantha`, `dalgo`, `eopie` and `iriaz`
under `design/RimStarWars/canon_references/`.

## Owed next

- FOUNDRY: deploy `SWBestiary` with prune (Nuna). Run the plan first, then `--apply`. Do it with the game down.
- When the renders land: run `art backfill artpipe` to import them as variants, then build a sheet for him.
- Iriaz north/south, and the Eopie A–E decision, come after he approves the east masters.
