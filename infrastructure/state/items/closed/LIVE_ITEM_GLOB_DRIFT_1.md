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

## RESOLVED 2026-09-21 (FOUNDRY)

**Root cause, found in `src/RimMandrake/rimflow/cli.py`:** `cmd_close`, and the
shared `_simple()` runner behind `drop`/`supersede`, only ever wrote the ledger
event. Nothing in the codebase ever moved the prose file — no `git mv`, no
`shutil.move`, no `os.rename` anywhere in `cli.py` or `model.py`. The
2026-09-19 move of 581/730 files was a one-time manual sweep; CHARTER.md's
"on close/drop/supersede the prose moves to items/closed/<ID>.md" describes a
*convention* every closing seat was expected to perform by hand and routinely
didn't. This is a real bug (a documented invariant nothing enforced), not a
deliberate skip on some path — fixed by making the move automatic.

**Fix:** `_move_prose_to_closed(iid)` (`cli.py`) now runs after every
`close`/`drop`/`supersede`, renaming `items/<ID>.md` -> `items/closed/<ID>.md`
on disk (plain `os.rename`, not `git mv` — this tree is shared live by several
concurrent agents and a git subprocess here would take an index lock for a
rename the caller is about to commit anyway). It prints
`prose moved: <old> -> <new> — stage BOTH paths in your commit.` so the
closing seat's own commit picks up the rename. No-op when the item never had
prose, or when `items/closed/<ID>.md` already exists (never clobbers).
⚠️ Also fixed a latent landmine this exposed: `_bind_paths()` rebound
`model.ITEMS` from `RIMFLOW_ITEMS` for tests but never `model.CLOSED` (computed
once from `ITEMS` at import) — without also rebinding `CLOSED`, `selftest_cli.py`
driving `close`/`drop`/`supersede` would have moved its own scratch prose files
into the REAL repo's `items/closed/`. Fixed alongside; `selftest_cli.py` 43/43
still passes and its own `the_real_ledger_was_never_touched` case confirms
isolation held.

**Fresh measurement 2026-09-21 (the 2026-09-20 count was stale, as expected —
several agents closed more items same-day):**

- 270 files were in `items/` at measurement time (up from 181 the day before).
- **79** were `done`/`dropped`/`superseded` with prose never moved (not 24) —
  git-mv'd to `items/closed/` in this pass, with inbound path citations fixed
  in the same change (11 real citations found and fixed, across
  `infrastructure/state/items/*.md`, `design/**`, `src/RimUtinni/**`; citations
  in `infrastructure/state/derived/queue_preview/*.md` were left alone —
  untracked, rendered, regenerate correctly on their own — and citations
  inside `infrastructure/state/handoffs/*.md` and `events.jsonl` were left
  alone too: they are timestamped historical records of past state, not live
  pointers, and the ledger is never hand-edited).
- **8** had no ledger row. Triaged individually:
  - `LANDMARK_NAMING_PASS_1.names` — not an item; a rename-table data file
    cited by the still-open, still-`doing` `LANDMARK_NAMING_PASS_1.md`. Left
    exactly where it is. The new selftest recognises this shape generically
    (a `<live-item-id>.<suffix>.md` companion), not by hardcoding this one name.
  - `CANON_REINTEGRATION_EXECUTION_1` — a 2026-09-04 BENCH reboot-continuity
    note ("written at the owner's 'prepare for agent reboot'"), not an item at
    all. Moved to `infrastructure/state/handoffs/`. No inbound citations found.
  - `DIRTY_CODE_REVIEW_LOOP_RESTART_16` and `_17` — wave-completion notes in
    the same numbered series as `DIRTY_CODE_REVIEW_LOOP_RESTART_2`..`15`,
    which are ALL already filed-and-closed in `items/closed/`. These two were
    simply never filed at the time their waves ran. Filed and closed to match
    the sibling convention (16 superseded by 17; 17 is itself a finished
    retrospective, the loop is separately paused until 2026-09-23 per the
    owner).
  - `RIMTHEMES_VBE_BACKGROUND_CONFLICT_1` — titled "RESOLVED" in its own
    heading; a fully fixed and live-verified bug from 2026-09-05, never filed.
    Filed and closed as `done`.
  - `GOD_ART_LOCAL_HARDWARE_PARKED_1` — the exact same 2026-09-05 owner ruling
    (local imagegen/rembg OOM stop) already covered by the filed-and-closed
    `LOCAL_IMAGEGEN_TRACK_PARKED_1`, but with unique detail the other item
    lacks (the precise per-file god-art inventory frozen mid-pipeline). Filed,
    then `supersede`d by `LOCAL_IMAGEGEN_TRACK_PARKED_1` so the detail survives
    in `items/closed/` rather than being duplicated as live or deleted.
  - `WORLDMAP_REDO_RUN_SHEET_2026-09-07` — a bridge run sheet with 0 of 13
    steps ever run in two weeks. Filed, then `drop`ped: superseded by the
    later doctrine that the planet is repainted ONCE, at the end, after every
    biome is its own mod, and that world remake is the last step — an
    incremental live-bridge worldmap redo from this old freeze-rulings doc is
    exactly the migration tax that ruling says to stop paying.
  - `FURNACEBEAST_WORLD_MIGRATION_1` — a real, still-unbuilt spec (the
    off-map world-scale leg of the furnace-beast thermal cycle, split from the
    already-shipped map leg `FURNACEBEAST_THERMAL_CYCLE_1`). Filed as
    `proposed`, kept live.

**Reverse check (not measured 2026-09-20): 18 ledger rows are live
(`proposed`/`ready`/`doing`) with no prose file in `items/` at all** —
`BACTA_REVIVAL_MECHANIC_1`, `BACTA_SIDE_ITEMS_1`, `BACTA_TANK_ART_1`,
`BIOME_LANDMARK_REFINEMENT_1`, `DEEPS_FAUNA_REPOPULATION_1`,
`EVENT_TRACE_PROPS_LIBRARY_1`, `KOTOR_CRYSTAL_GENSTEP_DRIFT_1`,
`MORNING_RULING_BATCH_1`, `MYCOID_COLOSSUS_LIVE_LOOK_1`,
`NARRATIVE_DICTIONARY_PILOT_1`, `NORTH_STAR_ATMOSPHERIC_TBD_1`,
`OFFBIOME_SHEET_RERENDERS_1`, `PYRELANDS_GRASS_SATURATION_1`,
`REACTIVE_SHIP_LIGHTING_1`, `ROT_FAUNA_KIN_WIRING_1`,
`TWILEK_TROPE_GENES_MOVE_1`, `WORLDMAP_DOCS_PASS_1`,
`XENOTYPE_NONCOSMETIC_FIXES_1`. This is not a defect the same way the other
direction is — an item can legitimately be filed with no prose yet (`file`
itself warns "no ## spec ... yet" and still offers it) — but it means these
18 are invisible to anyone reading `items/` prose rather than asking
`rimflow`. **Out of scope for this item** (backfilling 18 items' worth of
prose is real work, not a glob fix); flagged here for whoever picks it up
next.

**Regression guard:** `src/RimMandrake/rimflow/selftest_items_glob_live.py`,
collected by `run_selftests.py` (glob `selftest*.py` under `src/`). Reads the
real ledger (read-only — never writes) and the real `items/` glob, fails on
any file whose id is terminal or has no ledger row (companion-file exception
as above), and separately proves on a throwaway directory that it (a) catches
a deliberately reintroduced drifted file and (b) does not false-positive on a
live item's own prose. 3/3 passing.
