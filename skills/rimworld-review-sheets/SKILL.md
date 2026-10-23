---
name: rimworld-review-sheets
description: >-
  Use before building, serving, refreshing, enacting or retiring any RimMandrake review sheet, and before
  showing the owner ANY game art to judge — creature, plant, building, item, junk, gear or icon sprites, artpipe
  renders, reskins. The RimWorld layer over the general `review-sheets` skill: every picture with a real
  in-game size is shown at true scale beside a vanilla human (enforced in code at serve, commit and phone),
  sheets are built and gated by art_sheet.py, served by serve_gated.py, and his rulings are carried out by
  `art.py enact`. Also use when a sheet is "missing the scaled portrayal", repeats rows he already ruled,
  loses or moves his picks, re-fires a note he already had followed, is invisible in RimPulse, or a
  sheet tool refuses. Not for live in-game staging (rimworld-live-review).
---

# RimWorld review sheets

The general `review-sheets` skill (`~/.claude/skills/review-sheets/SKILL.md`) covers the page itself:
prefill, posture, decisions-as-data, the sidecar, `check_sheet.py`. Read it once. This skill is what
RimMandrake adds on top, and where it is stricter, it wins.

## Rule 1 — game art is shown at its true in-game size. The tools enforce it.

Owner, 2026-10-04: *"I also need to know the cell size for each of these flora and fauna too, with a
realistic game human for scale. It's the only way I can judge the art quality/resolution."* A skill alone
failed within an hour (2026-10-05), so this is code now: `game_art.py` decides from the PICTURES whether a
sheet shows game art, and such a sheet is refused unless the scaled-review gate stamped it — when served
(`serve_gated.py`), committed (`infrastructure/githooks/pre-commit`) or published to the phone
(`sheet_to_artifact.py`). **Declaring a sheet non-art does not exempt it.** Only the builders below can
produce a stamp, so: never hand-roll a generator for game art. If a builder cannot do what you need, fix
the builder and add a selftest.

## Which builder

| the sheet shows | build it with |
|---|---|
| one biome's flora and fauna | `python3 src/RimMandrake/Utils/art/art_sheet.py --biome RM_<X>` |
| any other game art: buildings, items, junk, gear, creatures, plants, UI defs, a batch of renders | `python3 src/RimMandrake/Utils/art/art_sheet.py --subjects <defName>... [--jobs <artpipe job id>...] --name <lower_snake> [--label "Title"]` |
| no game art (code triage, text/def curation, numbers) | the general template, then `python3 src/RimMandrake/Utils/art/nonart_sheet.py declare <html>` |

Both art modes write `Transient/biome_ffar/<name>_sheet_<date>.html`, build to a temp file, run
`scaled_review_gate.py` (14 requirements) and move the sheet into place stamped only on a pass; a failure
exits 3, names the rows and requirement, and leaves the last good sheet alone. Sizes come from the live def
dump through `scale_panel.py`: animals (adult drawSize), plants (drawSize × visualSize, mesh count),
buildings and items (drawSize on the `size` footprint, south facing, footprint outlined). A def the game
draws only in the UI (a ResearchProjectDef, a ThingDef with no graphicData) is measured "no world size" —
the resolver, re-asked by the gate, is the only thing that exempts a row from a panel.

## The lifecycle

1. **Build** (above). **Check** any sheet: `scaled_review_gate.py check <html>`; game art or not:
   `game_art.py classify <html>`.
2. **Read it first** (owner, 2026-10-22: *"Read it first and see if it's obviously broken, malfunctioning, or
   problematic before wasting a human's time to tell that to you."*). Look at every row — yourself, or a naive judge
   (a fresh Opus that did not make it; `gpt_consult.py` for a big sheet): does it render, is it recognisable as what
   it is, does it repeat a ruling, does it contradict its spec? Fix it or rebuild without it (never hand-edit the
   sheet), then `prereview.py init <sheet> --by seat:<SEAT>|judge:<model>` and fill each row OK / FIXED / FLAG + note,
   `caught`, `dropped`. `serve_gated.py`, `review_queue.py` and `sheet_to_artifact.py` refuse a sheet without it
   (exit 4); a row whose pictures change afterwards needs a fresh look (`init` resets only it).
3. **Serve** — `serve_gated.py` only, its output in `<sheet>.serve.log` beside the sheet, or RimPulse cannot
   list it. Give him the URL and the full native path.
4. **Refresh** as renders land — `refresh_sheets.py` keeps URLs stable, rebuilds only changed sheets, and
   prints an `UNPUBLISHED:` publish command for a rebuilt sheet only if it is pinned (tracked). Run it.
5. **Remap** after any rebuild of a sheet he has touched — `remap_decisions.py` (dry run, then `--apply`), so
   every letter he picked still names the same pictures.
6. **Enact** when he says a sheet is done — `art.py enact <decisions.json>` (dry run), then `--apply`;
   `--hold <subject>` for rows awaiting a sitting, `--mark-done <row>` once a def half of a note is done.
   One pass, at most one batched card for conflicts (owner, 2026-10-08).
7. **Audit** the enact with a fresh read of the ledger and artpipe — never the enact's own summary.
8. **Clear followed notes** — enact moves a followed note into `notes_followed`; never act on a raw note
   without checking it was not already followed (owner, 2026-10-08: *"You shouldn't leave my notes AFTER you
   follow the notes... it can produce accidental multiple firings."*).

Commands, flags, files and the RimPulse hand-off: `references/lifecycle.md`. The 14 rulings, verbatim, and
which tool refuses what: `references/art_requirements.md`. Failures that have actually happened, each with
its check: `references/traps.md`.

## Before he sees a sheet

- [ ] every row read by the seat or a naive judge, broken rows fixed or dropped; `prereview.py check <html>` OK, and
      the one-line `caught` goes to him with the link
- [ ] built by `art_sheet.py`; `scaled_review_gate.py check` PASS; `game_art.py deliver <html>` OK
- [ ] a scale panel on every row whose def has a world size; FALLBACK sizes flagged on the row
- [ ] donor-only rows = 0, or each has a pending render job and the count is shown to him
- [ ] served via `serve_gated.py` into `<sheet>.serve.log`; the URL answers 200
- [ ] for a sheet he has touched: `remap_decisions.py` reports 0 orphaned, and `letter_mismatches` = 0
- [ ] the full native path of the serving clone (`\\wsl.localhost\Ubuntu\home\mandrake\rm\<seat>\Transient\biome_ffar\…`; Transient is untracked since 2026-10-18, so `D:\` has only pinned sheets) beside the link
