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

## Built 2026-10-14 night (BENCH) — owner's three sheet rules, stale sheets rebuilt

- **Stale-serve override removed** (owner, by card 2026-10-14): no flag, no banner path (56e5d0deab).
- **Owner rules of 2026-10-12** (97e90a394a; design doc § "The owner's three other sheet rules"):
  - retire + replace in ONE pass: `✕ retire` + `use this` in one slot both stand, either order; `enact.retire_replaced`
    retires the leftover live copies in the same enact as the pick's install;
  - no "accept unchanged" control: an unanswered slot is kept on return; `decisions_v2.py <file> --returned "<his
    words>" --apply` stamps the return and ingest records the slots he left alone as his keep;
  - "decided" is only his: a seeded prefill reads "agent prefill X — not your answer"; `decisions_v2.owner_view`
    blanks it for enact and ingest.
  - Selftests: `selftest_sheet_slots.py`, `selftest_sheet_owner_rules.py`.
- **Sheets** (53c4d60425): the 16 stale sheets were rebuilt and are fresh. The rebuild also covered cauldron, which went
  stale mid-pass, and three sheets whose fingerprint had changed. His decisions files are byte-identical; the
  flowworks owner-walk file was regenerated because it was still an untouched prefill. remap: 0 remapped, 0 orphaned.
  `art.py backfill disk` was needed first, because FlowWorks' ledger `live` events lagged disk.
  - The 3 UNMEASURED sheets: `icon_outline_batch4_sheet_20261010` was replaced by a gated
    `biome_ffar/icon_outline_batch4_sheet_2026-10-14`. `sluice_panning_warden_sheet_20261010` was retired, superseded
    by the gated 2026-10-11 sheet. `art_verdict_sheet_2026-09-12` was retired: it is past shelf life, and its desert
    verdict was re-done on the 2026-10-04 biome sheets. None had a decisions file.
  - Scan after: 37 sheets, 37 fresh.
- `refresh_sheets.py` rebuilds `--subjects`/`--textures` sheets from their own census. It no longer restarts a server
  per sheet unless `--restart-servers`: 27 left-behind servers cost 5.1 GB and 2 OOM kills at 20:37.

**Remains (open):**
- `ART_SHEET_REDESIGN_FRESH_OR_REFUSE` — all four parts built; NEXT: owner checks the next sheet he returns (no accept
  button; retire + use-this in one pass), then close.
- Not covered by the guarantee:
  - the deployed game copy;
  - donor/vanilla rows' texPaths and IN GAME bytes;
  - flip-book frames;
  - re-deriving the load-order winner.
  - The sidecar's `decidedCount` field (in the shared review-sheets skill) still counts seeded letters. Nothing here
    reads it.
