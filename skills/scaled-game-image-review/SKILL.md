---
name: scaled-game-image-review
description: >-
  Build a review sheet for art that will be SEEN IN THE GAME — creature, plant, building or
  item sprites — where the owner picks, rejects or asks for a redo per row, and every picture is
  also shown at its true in-game size beside a vanilla human on the biome's own ground. A
  RimWorld-specific variant of the general `review-sheets` skill. Use whenever you build, rebuild,
  re-serve or ingest a biome art sheet or any per-row art comparison; whenever the owner reports a
  sheet is "missing the scaled portrayal", shows only donor art, repeats rows he already ruled, or
  loses his picks; and before handing him any page of game art to judge. Not for live in-game
  staging (that is `rimworld-live-review`) or for text/def curation sheets (plain `review-sheets`).
---

# Scaled game image review

A plain review sheet asks "which picture?". A game-art sheet must also answer **"how will it
look in the game?"** — and a picture judged at thumbnail size, on white, with no human beside it,
answers that wrongly. This skill is the contract every in-game art sheet meets. It was set by the
owner across the 2026-10-04/05 biome sittings; the Abyss / Blue Desert / Long Shade / Stillsand
sheets of that morning are the reference build.

**Base skill:** read `review-sheets` (`~/.claude/skills/review-sheets/SKILL.md`) first — the
sidecar server, decisions-as-data, prefill-vs-human, `check_sheet.py`. Everything there holds.
This file adds what game art needs on top.

**The tool already does all of it:** `src/RimMandrake/Utils/art/art_sheet.py --biome <RM_X>`
(built from the art ledger), `scale_panel.py` (the true-scale panel), `refresh_sheets.py` (rebuild
as renders land, URLs stable). Do not hand-roll a sheet. If the tool fails one of the requirements
below, fix the tool and add a selftest — never patch one HTML file.

## The requirements (each one is an owner ruling)

1. **One sheet per biome. Never merge biomes into one page** (owner 2026-10-05: *"I don't want one
   huge list with all biomes. One per biome please."*). An index of links is fine; an index of rows
   is not.
2. **True scale on every row, on every sheet** (owner 2026-10-04: *"I also need to know the cell
   size for each of these flora and fauna too, with a realistic game human for scale. It's the only
   way I can judge the art quality/resolution."*; 2026-10-05: *"You also did not include the scaled
   portrayal on that sheet."*). Each row carries:
   - the size in cells **with its source** (live def dump → deployed XML → patches; anything
     unmeasured says FALLBACK);
   - a panel of the picked (else prefill) set at **max zoom, 128–256 px/cell**, beside a vanilla
     human composed as the engine does, **on the biome's own ground colour** (mean RGB of its
     dominant ground texture, measured and sourced, never guessed);
   - normal play (32 px/cell) as a small secondary, and px-per-cell for every set.
   - **Never down-resolve** (2026-10-04: *"Please don't down-resolve the imagery so badly"*) — he
     plays with enhanced zoom; vanilla's 96 px/cell ceiling does not apply.
   A sheet with zero scale panels is a failed build, not a style choice.
3. **No row may show donor art only** (2026-10-05: *"I don't want to review donor art. We're not
   keeping any."*). Every row whose art comes from a non-mandrake mod (MLIE, Alpha Animals, Alpha
   Biomes, VE, …) carries **at least one render of ours** before the sheet is his to sit. Gap-fill
   first, serve second.
4. **Donor and older art stay visible as past art** (2026-10-05: *"I DO want to see donor art in
   'past art' so I can see where something came from though, please. I just don't want it to be all
   there is."*). Column order ranks recency and runtime, never worth: live first, shadowed copies,
   renders newest first, history oldest first, donor last.
5. **Canon beside the row.** A subject with a canon entry (`design/RimStarWars/canon_references/`)
   shows the reference images and the entry's `## Must show` next to its pictures, as REFERENCE —
   never pickable. A row without one says so. A canon creature and our franchise-free stand-in are
   separate rows in one coloured band, linked both ways.
6. **Renders that failed the canon gate still appear**, badged "failed canon check", and stay
   pickable — the gate has false-failed a picture he then chose.
7. **Do not repeat what he already ruled.** A subject ruled on any other sheet renders collapsed at
   the bottom — "Already ruled on <sheet>: <pick>" — expandable, never deleted (2026-10-05: *"a lot
   of redundant creatures from other forms listed on here as well that I've already reviewed"*).
   Match subjects through `subject.py`, so a tier prefix or variant word never makes a ruled
   subject look new.
8. **His picks never move.** Column letters are append-only and stable against the RULED snapshot;
   a rebuild adds letters, never reassigns one. A decisions file he has touched is never rewritten.
   Before telling him a rebuilt sheet is safe, run `letter_mismatches` against the snapshot his
   decisions name (from git history) and report 0.
9. **The note box drives the redo.** His note is copied **verbatim** into the regen job's
   `owner_note` at ingest. Never paraphrase it into the prompt in place of the quote.
10. **Links stay put.** Re-serving keeps the same port and token (`refresh_sheets.py`); a link he
    has open must keep working through every refresh. Check every URL returns 200 before giving it.
11. **Per-picture ✕ is reject-and-purge**, honoured at ingest through the art ledger — except a
    picture still live elsewhere (the ledger refuses; say where it is live and ask).
12. **Nothing installs from the sheet.** Picks become ledger rulings via `art.py ingest`; install is
    `art install` only.

## Enforcement — what refuses, and where (2026-10-05)

The requirements above are machine-checked by `src/RimMandrake/Utils/art/scaled_review_gate.py` (selftest:
`selftest_scaled_review_gate.py`, one failing fixture per requirement). A check that cannot be measured FAILS and says
UNMEASURED. Never weaken a check to pass a sheet — fix the tool, or report the failure.

- **Build** — `art_sheet.py --biome` (and so `refresh_sheets.py`) builds to `<sheet>.gate.tmp`, runs the gate, and only a
  pass moves the stamped HTML into place and writes the snapshot. A failure exits nonzero (3), names the rows and the
  requirement number, and leaves the previous sheet, snapshot and decisions untouched. The 30-minute refresh keeps serving
  the last good sheet, retries a failing one every cycle, and re-verifies sheets it did not rebuild.
- **Serve** — `serve_gated.py` is the only server launcher; it refuses (exit 4) an HTML with no gate stamp or one edited
  after the gate. The stamp is `<meta name="scaled-review-gate" content="v1 sha256:…">`.
- **Ingest** — `art.py ingest <decisions> --redo-jobs <jobs.json>` refuses unless every regen job carries his note
  verbatim as `owner_note` (req 9); redo decisions with no `--redo-jobs` are refused unless `--defer-redo-jobs`.
- **Hook** — `.claude/hooks/block_hand_edited_sheet.py` (PreToolUse, Bash|Write|Edit|MultiEdit) refuses hand-writing or
  hand-editing `Transient/biome_ffar/*_sheet_*.html` and starting `serve_sheet.py` directly.
- **Renders for real** — req 13: the gate serves the built page through a throwaway sidecar on a copy of his decisions and loads
  it in headless Edge (`gate_browser.py`); an uncaught console error, or far fewer `<img>` than the data's rows, fails. One row
  with a null field once blanked a whole sheet. Each row also renders inside try/catch, and a sheet polls its own URL every
  60 s and shows a "rebuilt — reload (your picks are saved)" banner (never auto-reloads).
- **Override** — `art_sheet.py --allow-failing "<reason>"` (used by refresh only when the sheet being replaced is itself blank)
  writes the sheet UNSTAMPED with a red banner naming what fails; the next passing build replaces it.
- **Check any sheet** — `python3 src/RimMandrake/Utils/art/scaled_review_gate.py check <html> [--urls] [--stamp]`, or
  `all` for every sheet; `--stamp` stamps only a passing sheet.

## Before you give him a sheet — the checklist

- [ ] `check_sheet` exits 0
- [ ] the HTML holds scale panels (`scale_` images) — count > 0, and one per row with art
- [ ] donor-only rows = 0, or each remaining one has a queued job and the count is shown to him
- [ ] every URL answers 200; links are the stable ones
- [ ] rows ruled elsewhere are collapsed, not repeated
- [ ] for a sheet he has touched: `letter_mismatches` = 0
- [ ] full native path to the HTML (`D:\Luke\dev\RimMandrake\Transient\biome_ffar\…`) beside the link

## When he says "<biome> sheet done"

Ingest that sheet: stamp ruled (`art.py ingest`), install picks (`art install`), queue redos with his
verbatim note, make the plainly mechanical def edits his notes ask for (scoped to that biome), file
judgement calls on an item, commit and push. Precedent:
`Transient/biome_ffar/abyss_close_progress_2026-10-05.md`. Then ask any open question as a card.
