# LIVE_ITEM_GLOB_DRIFT_1 — the live-item glob is 18% not-live

## what is wrong

CLAUDE.md documents the invariant:

> `items/<ID>.md` — LIVE item prose only — this glob is the live set
> `items/closed/` — prose of done/dropped/superseded items (moved on close)

MEASURED 2026-09-20 by globbing `infrastructure/state/items/*.md` and asking
`rimflow show` for each id's state:

- **181 prose files sit in `items/`.**
- **24 are `done`, `dropped` or `superseded` in the ledger** — closed, but the
  prose never moved.
- **8 have no ledger row at all.**
- **32 of 181 — 18% — are therefore not live items.**

Closed-but-present: `ANIMAL_TOLERANCES_JOIN_BROKEN_1`, `BIOME_CAST_PATCH_DEAD_NAMES_1`,
`BRIDGETOOLS_TILE_LAYER_DROPPED_1`, `CANONICAL_SAVE_MODLIST_DIVERGENCE_1`,
`CANONICAL_SAVE_SCENARIO_MISMATCH_1`, `CAVERNS_PARITY_BUILD_1`,
`COLONY_VISIBILITY_BUILD_1`, `DEEPS_FAUNA_VERDICTS_1`, `DESERT_PORT_DUPLICATE_DEFS_1`,
`DESIGNATE_BATCH_OVER_DESIGNATES_1`, `DRILL_IMPASSABLE_FILLPERCENT_1`,
`GIDDYUP_NULLKEY_COLD_READING_1`, `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1`,
`LIQUID_SINK_DRAINAGE_1`, `MODLIST_RULED_CUTS_1`, `NAME_PATCH_ZERO_MATCH_1`,
`OWNER_SAID_PROVENANCE_GUARD_1`, `PIT_TRAP_VISUAL_REDESIGN_1` (superseded),
`ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`, `ROT_ART_WAVE_1`,
`ROT_FLORA_FAUNA_VERDICTS_1`, `SLIME_STREAM_ROWS_1`, `VAPOR_EMITTER_PLACEMENT_1`,
`WORLDMAP_FINAL_REVIEW_1`.

No ledger row: `CANON_REINTEGRATION_EXECUTION_1`, `DIRTY_CODE_REVIEW_LOOP_RESTART_16`,
`DIRTY_CODE_REVIEW_LOOP_RESTART_17`, `FURNACEBEAST_WORLD_MIGRATION_1`,
`GOD_ART_LOCAL_HARDWARE_PARKED_1`, `LANDMARK_NAMING_PASS_1.names`,
`RIMTHEMES_VBE_BACKGROUND_CONFLICT_1`, `WORLDMAP_REDO_RUN_SHEET_2026-09-07`.

## why it matters

🔑 **Anyone answering "what is still open?" by globbing this directory — which is
what CLAUDE.md tells them to do — gets 18% noise.** A seat waking up, a decay
sweep, a handoff's "filed and still open" list, and the owner's own *"what needs
me?"* all read this glob. Work already finished reads as outstanding, and eight
files describe work the ledger has never heard of.

Observed directly: `rimflow close DESERT_PORT_DUPLICATE_DEFS_1` recorded `done`
at a commit and left the prose in `items/`. **586 files already sit in
`items/closed/`**, so the move normally happens — this is drift, not an absent
feature. Whether `close` stopped moving prose, or these 24 were closed by a path
that skips the move, is the thing to find out.

## the fix

1. **Find out why.** Read `rimflow`'s `close`/`drop`/`supersede` and see whether
   the move is conditional, recently broken, or skipped on some paths. Fix the
   cause before moving anything, or the drift returns.
2. **Move the 24** to `items/closed/` with `git mv`.
   ⚠️ **Fix inbound citations in the same change** — some are cited by path and
   will break. MEASURED on a sample of five: `PIT_TRAP_VISUAL_REDESIGN_1` has 3
   inbound citations, `ANIMAL_TOLERANCES_JOIN_BROKEN_1` 2,
   `WORLDMAP_FINAL_REVIEW_1` 1, and `CAVERNS_PARITY_BUILD_1` / `ROT_ART_WAVE_1`
   none. Sweep all 24, do not assume.
3. **Triage the 8 with no ledger row individually** — each is a different
   question. Some are probably notes that were never items (`LANDMARK_NAMING_PASS_1.names`
   is not even an ID shape; `WORLDMAP_REDO_RUN_SHEET_2026-09-07` is a run sheet).
   Either file the real ones or move them out of `items/`. ⛔ Do not bulk-delete.
4. **Add a selftest** to `run_selftests.py` that fails when a file in `items/`
   has a closed ledger state or no row. That is the only part that stops this
   recurring.

## Watch out

- ⚠️ **Do not hand-edit the ledger.** It is written only through `rimflow`.
- ⚠️ A file in `items/` with no ledger row is not automatically junk — it may be
  prose written before the item was filed, or an item filed under a different id.
  Check before moving.
- 🔑 The reverse direction is worth one check too: a ledger row that is `open`
  with **no** prose file in `items/`. This item did not measure that.

## verify

Every `*.md` directly in `infrastructure/state/items/` has a ledger row whose
state is live. A selftest asserts it and is in the `run_selftests.py` N/N.

## criteria

Globbing `infrastructure/state/items/*.md` answers "what is open" correctly.
