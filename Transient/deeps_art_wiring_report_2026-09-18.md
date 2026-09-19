# Lantern Deeps art wiring report — 2026-09-18

## Pipeline state

Daemon alive: `python3 src/RimMandrake/Utils/artpipe/artpiped.py` (pid 458), actively
working the queue during this session — `yumbulbs_b_v1` moved pending -> active ->
done while this report was being written. Last `throughput.jsonl` entries (all
`status: ok`) show Codex meter at ~5% primary / ~82% secondary used, healthy.

By the end of this session, all 51 Lantern Deeps texture slots named in
`ART_JOBS.md` have resolved:

| status | count |
|---|---|
| rendered, facts PASS | 48 |
| FAILED (job ran, no usable image) | 1 — `lanternstonemedium_a_v1`: tool returned 1254x1254 opaque unrelated art twice instead of the requested 256x256 isolated sprite; `out: null`, nothing saved |
| UNSERVED (no artpipe job exists) | 2 — the two 2048x2048 wall atlases (`lanternstone_wall_atlas`, `smoothedlanternstone_wall_atlas`) |

The "pending 4" (nuitae_a/b, yumbulbs_a/b) all landed PASS during this session.
Each PASS PNG lives at `infrastructure/artpipe/_artsrc/<job_id>/<job_id>.png`;
"facts PASS" = the manifest's `"facts": "PASS"` key (checks canvas size, alpha,
transparent corners — a technical gate, not an art-quality judgement).

Terrain check: `lanternstoneterrain_v1.png` is 1024x1024, mode RGB (opaque by
design — terrain never needs alpha), mean RGB (20, 27, 36), std (15, 22, 31),
~46,500 unique colours. **This is real facet texture, not the flat opaque
`#05070d` a stale handoff note warned about** — that note is outdated.

Two stray done renders exist and are intentionally excluded from wiring:
`arpeau_v1` and `nuitae_v1` (pre-facts-gate single-variant renders, superseded
by the current `_a`/`_b` pairs).

## Mapping

`ART_JOBS.md` documents 51 individual PNG files across 23 numbered rows (its
own count, confirmed by measurement). A plain `grep "<texPath>"` over
`Defs/` only catches 19 in-mod paths (plus 2 unrelated donor paths,
`CaveEntranceA`/`PitGate`, not part of this build) — the other 5 texture
fields use different XML tags: `<texturePath>` (terrain, ×2 identical),
`<uiIconPath>` (wall icon), and `<immatureGraphicPath>`/`<leaflessGraphicPath>`
(Dulcis and GreyLady's immature/harvested stages). Together that's 24 distinct
def-referenced paths, all captured in the full 26-job/51-file table now baked
into `wire_art.py` and `build_art_sheet.py`.

**Fully served (24 of 26 jobs / 48 of 51 files):** everything except
LanternstoneMedium and the two wall atlases.

**Partially served (1 of 26):** `Crystals/LanternstoneMedium` — variants B/C
PASS, variant A FAILED. The folder currently ships 2 of 3 variants; the
sowable's grown stage reuses this same folder, so it inherits the gap too.

**Unserved (1 of 26, 2 of 51 files):** `Things/Natural/Linked/lanternstone_wall_atlas`
and `smoothedlanternstone_wall_atlas` — no artpipe job filed for either.
`RUT_LanternDeeps/Things/Item/Crops/Dulcis` (`dulciscropitem_v1`, rendered PASS)
is a curiosity: no Def in this mod currently references that texPath at all —
flagged in the sheet, not wired to anything, not blocking.

## Script

`src/RimUtinni/LanternDeeps/wire_art.py` — the one-command post-review step.
Reads a review-sheets-format decisions JSON, copies only "keep" rows from
`_artsrc/<job>/<job>.png` to their `Textures/` destination (folder member for
`Graphic_Random`/`Graphic_StackCount` paths, single file for
`Graphic_Single`/terrain/icon paths). Dry run by default (prints the plan,
writes nothing); `--apply` copies; `--all-pass` ignores the decisions file and
treats every facts-PASS render as kept, for a quick preview build.
`python3 -m py_compile` clean. Verified both modes live: `--all-pass` plans 47
keeps (2 unserved excluded, matching every currently-servable texPath); plain
dry run with no decisions file plans 0 keeps / 47 skips, as the whitelist
posture requires. **No PNGs have been copied into `Textures/`** — wiring has
not run.

## Sheet

All 4 pending renders landed during this session, so the sheet was built now,
not deferred: `python3 src/RimUtinni/LanternDeeps/build_art_sheet.py --apply`.

- Sheet: `Transient/deeps_art_review_2026-09-18.html`
- Thumbnails: `Transient/deeps_art_thumbs_2026-09-18/*.png` (48 files)
- Decisions file: `Transient/deeps_art_review_2026-09-18.decisions.json`

51 rows, grouped by def/texPath (26 groups), pre-filled `keep` for every
facts-PASS render and `regen` for the 1 failed + 2 unserved rows (nothing to
keep there). `check_sheet.py` passes clean: **0 FAIL, 1 WARN, 33 ok** — the
one WARN is expected (the decisions file starts empty; the page seeds the
pre-fill into it client-side on first load, per the skill's design).

To review: run the skill's sidecar so it opens in a real browser —
`python3 /home/mandrake/.claude/skills/review-sheets/assets/serve_sheet.py --sheet Transient/deeps_art_review_2026-09-18.html --decisions Transient/deeps_art_review_2026-09-18.decisions.json`
— never hand over the bare file path per the skill's ruled default.

## Open

- **2 texPaths need an artpipe job filed before anything can be reviewed**: the
  natural and smoothed lanternstone wall atlases (2048x2048 each).
- **LanternstoneMedium variant A needs a re-render** — the tool's known
  size-ignoring failure mode, not a def or pipeline bug.
- **`Things/Item/Crops/Dulcis` has a PASS render with no Def wiring it up** —
  worth a question to whoever owns the Defs (not touched here, out of scope).
- Wiring (`wire_art.py --apply`) is one command away and untouched, waiting on
  the owner's decisions file.
