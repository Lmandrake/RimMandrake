# ART_SHEET_REDESIGN_FRESH_OR_REFUSE

**Owner, 2026-10-12 (verbatim):** "We need to deeply reconsider how the art sheets are handled. Even in this reduced
setting of the Experiment, it's failing. I'm not sure what to do about it yet, but it needs some kind of hook or
ensurance that it's not serving stale information. By construction, by design, by hashes, by hooks, I'm not sure. But it
must be improved in freshness guarantee. File this for post-Wednesday. I don't want to spent tokens on it right now, but
it's a very high priority for Wednesday night."

**When:** Wednesday 2026-10-14 night, after the 16:00 PDT account reset. Spend no tokens on it before then.

**Triggering incident (2026-10-12):** the GSS owner-walk art sheet of 2026-10-11 (built 3c5e33d5c7, 14:56 PDT) showed
the pre-v3 power-tap clamp as "what the game shows now": the image was a 2026-10-03 render keyed on the pre-rename
texPath `RimMandrake/MessyConduit/Aerial/TapClamp` plus a 2026-10-04 def dump. The owner's v3 pick C was installed
3 h after the build (737b796e6f), so the sheet served a superseded, already-ruled row. Its header also reported
"4 decided" while 3 of the 4 were agent prefills. The sheet passed the existing scaled_review_gate stamp anyway — the
gate checks the sheet's form, not the freshness of its images. A same-day point fix to the generator (BENCH subagent,
2026-10-12) is not this redesign.

**Design space to weigh (not decided):** a content hash of every displayed image's source (texture on disk, def
texPath, def-dump fingerprint) stamped into the sheet; refuse to serve when any hash no longer matches (serve_gated.py
checks on every page load); a hook on `art install` that invalidates or rebuilds every sheet citing that def; rows
already ruled leave the to-decide set automatically; "decided" counts only owner provenance, never prefill.

**Owner requirements added 2026-10-12 (verbatim):** "I need to be able to Retire the currently used art as well as long
as I select another with "use this." Right now it requires TWO passes to retire art currently in use. Inefficient and
forces repeat cycles." · "I also HATE the "accept unchanged." I never return a sheet without reviewing every item, so
please assume "accept unchanged" is true if I didn't change anything."
- Retiring the in-use art and picking its replacement happen in ONE pass.
- Remove the "accept unchanged" control: a returned sheet means every unchanged row is accepted as-is.

## Built 2026-10-14 (BENCH, 850c6b0cdf) — freshness half DONE

Design: `design/RimMandrake/art_sheet_freshness_design_2026-10-14.md`. Tool: `src/RimMandrake/Utils/art/sheet_freshness.py`
(selftest `selftest_sheet_freshness.py`).
- **Invariant**, re-measured from disk on every use, never cached:
  - every picture labelled installed is the sha256 of a file our mods hold now;
  - every installed file for a shown texPath is shown as installed;
  - every texPath our defs draw (src XML) that has art of ours is on the row;
  - thumbnails and inputs are unchanged.
- **Enforced in four places:**
  - gate req 15 (a stale-at-birth sheet is never written; `refresh_sheets.py` rebuilds one that went stale);
  - `serve_gated.py` refuses to start (exit 5) and re-checks on every page load, serving a refusal page. No override:
    the stale-serve escape hatch was removed (owner, by card 2026-10-14), so a stale sheet is only ever rebuilt;
  - `generate_biome` re-resolves every census row (creatures and plants) from src XML at build;
  - `art.py install` and `enact --apply` print the sheets they just made stale.
- **Retrofit:** old sheets are verified from their own ITEMS block. Scan at build: 20 FRESH, 16 STALE (incl. Pyrelands
  2026-10-14, 9/9 rows), 3 UNMEASURED (no ITEMS). Stale sheets refuse to serve until rebuilt.

**Remains (open):**
- `ART_SHEET_REDESIGN_FRESH_OR_REFUSE` — freshness built; NEXT: rebuild the 16 stale sheets (`refresh_sheets.py`
  for biome sheets; re-run `art_sheet.py --textures/--subjects` for the others), then build the three owner sheet
  requirements:
  - retire and replace in one pass;
  - drop "accept unchanged";
  - "decided" counts only owner provenance.
- Not covered by the guarantee:
  - the deployed game copy;
  - donor/vanilla rows' texPaths and IN GAME bytes;
  - flip-book frames;
  - re-deriving the load-order winner.
