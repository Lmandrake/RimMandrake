---
name: rimworld-review-sheets
description: >-
  Use before building, serving, refreshing, enacting or retiring any RimMandrake review sheet, and before
  showing the owner ANY game art to judge — creature, plant, building, item, junk, gear or icon sprites, artpipe
  renders, reskins. The RimWorld layer over the general `review-sheets` skill: every picture with a real
  in-game size is shown at true scale beside a vanilla human (enforced in code at serve, commit and phone),
  sheets are built and gated by art_sheet.py, served by serve_gated.py, and his rulings are carried out by
  `art.py enact`. Also use when a sheet is "missing the scaled portrayal", repeats rows he already ruled,
  loses or moves his picks, re-fires a note he already had followed, is not listed where the owner looks, or a
  sheet tool refuses. Not for live in-game staging (rimworld-live-review).
---

# RimWorld review sheets

The general `review-sheets` skill (`~/.claude/skills/review-sheets/SKILL.md`) covers the page itself. The
general skill covers the prefill, the posture, the decisions as data, the sidecar and `check_sheet.py`. Read the general skill once. This skill
holds what RimMandrake adds. Where this skill is stricter than the general skill, obey this skill.

Four terms in this file:

- **The sidecar** is the server process of one sheet. The sidecar writes each click of the owner to the sheet's
  `.decisions.json`.
- **A stamp** is the `scaled-review-gate` tag that the gate puts in the HTML of a sheet that passed. The stamp holds a
  hash of the HTML. So a hand edit after the gate makes the stamp invalid.
- **A letter** is the name of one column of pictures on a sheet. His picks are letters.
- **Donor art** is art from a mod that is not ours. Vanilla art counts as donor art too.

## Rule 1 — game art is shown at its true in-game size. The tools enforce it.

Owner, 2026-10-04: *"I also need to know the cell size for each of these flora and fauna too, with a
realistic game human for scale. It's the only way I can judge the art quality/resolution."*

- A skill alone failed within an hour (2026-10-05). So code now enforces this rule.
- `game_art.py` decides from the PICTURES whether a sheet shows game art.
- A sheet with game art is refused unless the scaled-review gate stamped it. Three places refuse the sheet:
  - when the sheet is served (`serve_gated.py`);
  - when the sheet is committed (`infrastructure/githooks/pre-commit`);
  - when the sheet is published to the phone (`sheet_to_artifact.py`).
- **Declaring a sheet non-art does not exempt it.**
- Only the builders below can make a sheet that earns a stamp. The gate fails a sheet that has no snapshot from a
  builder.
- Never hand-roll a generator for game art.
- If a builder cannot do what you need, fix the builder and add a selftest.

## Which builder

| the sheet shows | build it with |
|---|---|
| one biome's flora and fauna | `python3 src/RimMandrake/Utils/art/art_sheet.py --biome RM_<X>` |
| any other game art: buildings, items, junk, gear, creatures, plants, UI defs, a batch of renders | `python3 src/RimMandrake/Utils/art/art_sheet.py --subjects <defName>... [--jobs <artpipe job id>...] --name <lower_snake> [--label "Title"]` |
| no game art (code triage, text/def curation, numbers) | the general template, then `python3 src/RimMandrake/Utils/art/nonart_sheet.py declare <html>` |

- Both art modes write `Transient/biome_ffar/<name>_sheet_<date>.html`.
- Both art modes build to a temp file and run `scaled_review_gate.py` (16 requirements) on that file. Only a pass
  stamps the sheet. Only a pass moves the sheet into place, except with `--allow-failing` (`references/lifecycle.md`).
- A failure exits 3 and names the rows and the requirement. A failure leaves the last good sheet alone.
- `scale_panel.py` reads each size from the live def dump:
  - animals: the adult drawSize;
  - plants: drawSize × visualSize, with the mesh count;
  - buildings and items: drawSize on the `size` footprint. The thing faces south. The panel outlines the footprint.
- The game draws some defs only in the UI (a ResearchProjectDef, a ThingDef with no graphicData). The resolver
  (`Resolver` in `scale_panel.py`) measures such a def as "no world size".
- The gate asks the resolver again. Only the resolver can exempt a row from a scale panel.

## The lifecycle

1. **Build** the sheet (see "Which builder").
   - To **check** any sheet, run `scaled_review_gate.py check <html>`.
   - To see whether a sheet shows game art, run `game_art.py classify <html>`.
2. **Read it first** (owner, 2026-10-22: *"Read it first and see if it's obviously broken, malfunctioning, or
   problematic before wasting a human's time to tell that to you."*).
   - Look at every row yourself, or give every row to a naive judge. A naive judge is a fresh Opus that did not make
     the sheet. For a big sheet, use `gpt_consult.py`.
   - Ask four questions about each row:
     - Does the row render?
     - Is the picture recognisable as what it is?
     - Does the row repeat a ruling?
     - Does the row contradict its spec?
   - Fix a broken row, or rebuild the sheet without that row. Never hand-edit the sheet.
   - Then run `prereview.py init <sheet> --by seat:<SEAT>|judge:<model>`. The command writes the pre-review record.
   - In the record, fill each row with OK / FIXED / FLAG and a note. Fill `caught` and `dropped` too.
   - `serve_gated.py`, `review_queue.py` and `sheet_to_artifact.py` refuse a sheet that has no complete record. The
     refusal of `serve_gated.py` and `sheet_to_artifact.py` is exit 4.
   - If the pictures of a row change after the look, that row needs a fresh look. `init` resets only that row.
3. **Serve** the sheet with `serve_gated.py` only.
   - Send the output of `serve_gated.py` to `<sheet>.serve.log` beside the sheet. `refresh_sheets.py` and the status
     tooling find the output there.
   - RimPulse is retired. So the owner has the URL only from you. Give him the URL.
   - The page writes every click as he goes (owner, 2026-10-31).
4. **Refresh** the sheets as renders land. Run `refresh_sheets.py`.
   - `refresh_sheets.py` keeps URLs stable and rebuilds only the changed sheets.
   - For a rebuilt sheet that is pinned (tracked), `refresh_sheets.py` prints an `UNPUBLISHED:` line with a publish
     command. Run that command.
5. **Remap** after any rebuild of a sheet that he has touched. Run `remap_decisions.py` (a dry run), then run the
   command again with `--apply`. The remap keeps every letter that he picked on the same pictures. `--apply` skips a
   file with an orphaned letter. Resolve that letter first.
6. **Enact** the sheet when he says that the sheet is done. Run `art.py enact <decisions.json>` (a dry run), then run
   the command again with `--apply`.
   - `--hold <subject>` leaves out the rows that wait for a sitting with him.
   - Some notes ask for a picture and also for a change to the def. After the def half is done, pass
     `--mark-done <row>`.
   - Enact in one pass, with at most one batched card for the conflicts (owner, 2026-10-08).
7. **Audit** the enact with a fresh read of the art ledger and artpipe.
   - Never audit the enact from its own summary.
   - The art ledger is the event record in `infrastructure/state/art/events/`. Read the art ledger with
     `art.py status <subject>`.
   - artpipe is the queue that draws the pictures.
8. **Clear followed notes.** Enact moves a note that was followed into `notes_followed`.
   - Before you act on a raw note, check that the note was not already followed (owner, 2026-10-08: *"You shouldn't
     leave my notes AFTER you follow the notes... it can produce accidental multiple firings."*).

The other files of this skill:

- `references/lifecycle.md` holds the commands, the flags, the files and the hand-off.
- `references/art_requirements.md` holds the 14 rulings, verbatim, and says which tool refuses what.
- `references/traps.md` holds the failures that have actually happened, each with its check.

## Sheet behaviour he has ruled

- **Group similar rows under an expandable parent; a click never makes an item vanish** (owner, 2026-10-10): *"it should collapse similar items together "Biome sheets: 23" and when you click on it, it expands to show the sub-items that are themselves clickable. Things should NEVER just "drop off" when you click on them."*
- **No "accept unchanged" control; an untouched row on a returned sheet means accepted** (owner, 2026-10-12): *"I also HATE the "accept unchanged." I never return a sheet without reviewing every item, so please assume "accept unchanged" is true if I didn't change anything."* Retiring the current art and picking another happens in the same pass.

## Before he sees a sheet

- [ ] The seat or a naive judge read every row. No broken row is on the sheet: fix or drop it.
- [ ] `prereview.py check <html>` reads OK. The one-line `caught` goes to him with the link.
- [ ] `art_sheet.py` built the sheet. `scaled_review_gate.py check` reads PASS, and `game_art.py deliver <html>` reads OK.
- [ ] Every row whose def has a world size has a scale panel. A size that was not measured reads FALLBACK, and the row
      is flagged.
- [ ] The donor-only rows (rows whose only art is donor art) are 0. Otherwise each such row has a pending render job, and
      the count is shown to him.
- [ ] `serve_gated.py` serves the sheet into `<sheet>.serve.log`, and the URL answers 200.
- [ ] For a sheet that he has touched: `remap_decisions.py` reports 0 orphaned, and `letter_mismatches` = 0. A letter
      is orphaned when its pictures are no longer in the row.
- [ ] He gets the served `http://localhost` URL and nothing else.
  - Never give him a copy of the sheet. Never give him a `/home/`, `/mnt/` or `\\wsl.localhost` path.
  - If a sheet has no server, serve the sheet first. Do the same for a link in an owner pile. An owner
    pile is a `Transient/owner_pile…` page of work for him.
  - His device can be unable to reach that URL (a phone off the tailnet). Then export the sheet with
    `sheet_to_artifact.py`. Publish that page privately (`references/lifecycle.md`).
  - Code enforces this:
    - A page that its sidecar (its live writer) does not serve blocks picks. The page names the URL (`sheet_live_guard.py`, req 16).
    - A hook refuses a copy out of the clone, and a copy refuses to serve.
    - `owner_doc_lint.py` refuses those paths in piles, Transient docs and cards.
- **Every sheet shown must be truly new.** "Please ensure that each sheet is truly new." (owner)
  - Before a sheet reaches him by link, card or phone, prove these four things. Say them in one line:
    - You built the sheet this sitting. The sheet is not an older sheet, served again.
    - The `ruled_elsewhere` collapse of `art_sheet.py` shows 0 un-collapsed rows that he ruled on another sheet. A row
      is fine if its only new thing is a redraw that he asked for.
    - `python3 src/RimMandrake/Utils/art/sheet_freshness.py verify <html>` exits 0.
    - The `.decisions.json` of the sheet is not already finished. `review_queue.py` counts a sheet as closed when the
      file is frozen, is `returned`, or has the `reviewStatus` state `ruled`. A sheet with none of these three marks can still be finished. So also check
      that its picks are not already enacted.
  - If any check fails, rebuild or drop the sheet. Never send the sheet with a caveat.
- **One row = one decision about one thing, and he must be able to tell what he is clicking** (owner: "I have no idea what you want me to click on.").
  - Each row describes plainly what the thing is, where the thing is placed and how the thing is used.
  - Name each option for what the option DOES ("use the new art" / "keep what ships"). Never name options "Body" vs
    "No longer needed".
  - Never put four unrelated items in one choice.
  - Every candidate in a row depicts the SAME object. Split a style x content matrix (e.g. 4 tech styles x 3 liquids)
    into separate questions. Owner: "it was making me choose between different objects".
  - Before you offer the candidates, check that they differ by bytes. A "new" render was once byte-for-byte the
    current art.
  - A gated `art_sheet --subjects` sheet is built for gating and true scale. The sheet is not built for a person who
    decides. If the builder cannot give the description, ask by question card.
  - A prereview that judges the picture quality of each row does not catch this fault. Ask "are all candidates the
    same object?"
- **When candidates are per-look variants** (Scrapper / Industrial / Modern / Futuristic), the sheet lets him accept all looks together.
  - Never force one "use this" per row as if the looks were rival options (owner: "just accept the art").
- **A sheet's `.prereview.json` is a record of one clone's look, not proof the sheet is fine where it is served.**
  - One sheet was served from a clone where 18 of its untracked thumbnails (`Transient/biome_ffar/img`) never existed.
    Every row of that sheet read STALE.
  - Before you serve any sheet, run `sheet_freshness.verify_html` on the sheet in the serving clone. The
    `sheet_freshness.py verify` command calls that function.
  - If the result is `fresh False`, first rebuild the sheet (`refresh_sheets.py --force --only <slug>`).
  - After you serve the sheet, `curl` the served page.
