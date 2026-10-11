# The art requirements — the owner's rulings, verbatim

Moved here unchanged from the retired `scaled-game-image-review` skill (the owner commissioned it 2026-10-05 as "a subset of
the review sheet skill… for reviewing in game art"). `scaled_review_gate.py` checks every one; the numbers are the gate's
requirement numbers. Requirement 1 (one sheet per biome) governs biome sheets; a `--subjects` sheet is one sheet per subject
set and never merges biome rosters.

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
   **Placeholder art is not art of ours** (2026-10-05, Grey Sea): script-drawn flat shapes and vanilla textures borrowed for
   another subject (`placeholder_detect.py`) get a red PLACEHOLDER badge and count as no art — such a row also needs a render or a pending/active job.
   Vanilla Core/DLC art counts as donor art (owner card, 2026-10-05): a row whose only art is vanilla also needs a render of ours; vanilla stays visible as past art.
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
13. **A sheet renders** (no blank page, no uncaught console error) — gate req 13.
14. **No purged picture is rendered as a column** — except one that is still LIVE in the game today (its
    replacement is not installed yet): it appears as the IN GAME column only, badged "you purged this — still
    live until a replacement is installed", non-pickable (no pick header, no ✕, absent from the row's letters).
    A purged picture that is not live still fails the gate.

## Enforcement — what refuses, and where (2026-10-05)

The requirements above are machine-checked by `src/RimMandrake/Utils/art/scaled_review_gate.py` (selftest:
`selftest_scaled_review_gate.py`, one failing fixture per requirement). A check that cannot be measured FAILS and says
UNMEASURED. Never weaken a check to pass a sheet — fix the tool, or report the failure.

- **Build** — `art_sheet.py --biome` (and so `refresh_sheets.py`) builds to `<sheet>.gate.tmp`, runs the gate, and only a
  pass moves the stamped HTML into place and writes the snapshot. A failure exits nonzero (3), names the rows and the
  requirement number, and leaves the previous sheet, snapshot and decisions untouched. The 30-minute refresh keeps serving
  the last good sheet, retries a failing one every cycle, and re-verifies sheets it did not rebuild.
- **Placeholder** — req 3 also fails a row whose only non-donor art carries the PLACEHOLDER badge (`placeholder_detect.py`) unless a pending/active artpipe job names its subject.
- **Serve** — `serve_gated.py` is the only server launcher; it refuses (exit 4) an HTML with no gate stamp or one edited
  after the gate. The stamp is `<meta name="scaled-review-gate" content="v1 sha256:…">`.
- **Ingest** — `art.py ingest <decisions> --redo-jobs <jobs.json>` refuses unless every regen job carries his note
  verbatim as `owner_note` (req 9); redo decisions with no `--redo-jobs` are refused unless `--defer-redo-jobs`.
- **Hook** — `.claude/hooks/block_hand_edited_sheet.py` (PreToolUse, Bash|Write|Edit|MultiEdit) refuses hand-writing or
  hand-editing `Transient/biome_ffar/*_sheet_*.html`, Write of ANY review-sheet HTML whose pictures are game art, Edit of
  any gate-stamped HTML, and starting `serve_sheet.py` directly.
- **Game art anywhere** (owner card 2026-10-11) — `game_art.py` decides from the PICTURES (cut-out alpha, facing or def file
  names, `Textures/`/artpipe paths) whether a sheet shows game art. Such a sheet needs the gate stamp to be served (the non-art
  route refuses it whatever it declares), committed (`infrastructure/githooks/pre-commit`) or published to the phone
  (`sheet_to_artifact.py`, exit 4).
- **Renders for real** — req 13: the gate serves the built page through a throwaway sidecar on a copy of his decisions and loads
  it in headless Edge (`gate_browser.py`); an uncaught console error, or far fewer `<img>` than the data's rows, fails. One row
  with a null field once blanked a whole sheet. Each row also renders inside try/catch, and a sheet polls its own URL every
  60 s and shows a "rebuilt — reload (your picks are saved)" banner (never auto-reloads).
- **Override** — `art_sheet.py --allow-failing "<reason>"` (used by refresh only when the sheet being replaced is itself blank)
  writes the sheet UNSTAMPED with a red banner naming what fails; the next passing build replaces it.
- **Check any sheet** — `python3 src/RimMandrake/Utils/art/scaled_review_gate.py check <html> [--urls] [--stamp]`, or
  `all` for every sheet; `--stamp` stamps only a passing sheet.
