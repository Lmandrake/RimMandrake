# Rich-screenshot art pre-review — the contact board (2026-10-06)

Status: DRAFT design. Offline half built and selftested at `src/RimMandrake/Utils/artboard/`
(26/26 on synthetic boards); first real trial in §12. The live half needs the bridge tools in §11.
Authorized by the owner 2026-10-06: *"Pre-working some art review before the human's check is pretty
important. And there it feels like taking very rich screenshots that can test MANY items at once and be
segmented down into individual checks MIGHT be a way forward."*

## 1. The method in brief

Stage MANY subjects on a grid at **known cells** in one scene (every FlowWorks depth × fill × liquid state;
every creature of a biome roster in all four facings; every plant at each growth stage), capture **one**
high-resolution frame (or a few tiles) with fixed camera, zoom, light and weather, then **cut it into
per-subject crops by the known cell geometry**. Each crop goes through three tiers, each cheaper per item
than the one after it:

- **(a) deterministic pixel checks** — milliseconds, no model: missing texture, empty cell, displaced
  subject, wrong colour family, draws outside its cells, cut-off texture, alpha hole, two states that must
  differ rendering the same, drift from an owner-approved reference crop.
- **(b) ONE batched vision read** of a labelled mosaic holding only the crops that passed (a), with a
  narrow per-tile question. One image read covers dozens of subjects.
- **(c) the owner** sees only what (a)/(b) flagged plus the genuinely subjective calls, as a labelled board
  with Accept / Change / Unclear — **and walks the same scene in game** (saved as a keeper), because
  visuals are reviewed in game, not in browser sheets.

## 2. Why

Measured 2026-10-06 (`flowworks_playtest_automation_2026-10-06.md`, "Where live-testing time actually
goes"): across 49 h of live sessions, **model deliberation between tool calls is 65.9%** of the time;
screenshots are 0.9%, image reads 0.2%, interpreting an image 0.8% (298 interpretations, median 3.7 s).
So the expensive thing is not the picture, it is **an agent deciding per item**. Today's FlowWorks visual
board (`src/RimMandrake/FlowWorks/review_map_visuals.py`) is 34 stations and ~700 bridge calls, and each
station's look is judged one at a time — by the owner walking it, or by an agent reading one shot per
station. A contact board moves the per-item work into code: the agent's deliberation is spent once per
**board**, on the few things code could not decide.

It is also a **problem-discovery** instrument, not just a speed-up: a grid that shows every legal state
side by side exposes whole-family defects (a liquid that renders identically at fill 1 and 3; a facing
that is missing for six creatures) that a station-by-station walk misses because no two are ever
adjacent. (It would also have made `review_map_visuals.py`'s depth-fill coupling — finding 8, fill is
always `max(1, D-1)` — visible as a missing column.)

## 3. Staging a board

A **board recipe** (JSON, committed, deterministic) is the unit. It names:

- **subjects**: `{id, cell:[x,z], size:[w,h], expect:{…}, differs_from:[ids], question, canon}` — the
  exact format `artboard/run.py` reads. Ids are art-ledger slot ids where one exists
  (`RSW_Nuna#juvenile/body/south`), so a finding lands on the slot it is about.
- **pitch**: the cell spacing. Rule: pitch ≥ subject size + 2 × pad, pad ≥ the subject's overhang
  (`drawSize` beyond its footprint) + 0.5 cell of plain ground. Creatures: drawSize/1 cell + 2. Pits:
  the station plot (6×5) + 2. Plants: 1 + 2 (trees: drawSize, often 3+).
- **ground**: ONE flat, mid-value terrain under the whole board (not the biome's busy floor), chosen to
  contrast with the subjects. The owner's "biome's own ground colour" rule is for the TRUE-SCALE judgement
  and stays a separate row in (c); detection wants plain ground. Where the biome ground matters to the
  look (pits cut into dirt vs granite), the ground is part of the subject and the board uses a **plate**.
- **conditions**: time of day (noon), weather locked clear, no roof, unfogged, game paused, pawns
  rotation-locked, no hostiles (sweep at build), all names/labels hidden (`jawa/screenshot_mode`).
- **classes** of grid, each its own board:

| board | axes | subjects | expect fields that matter |
|---|---|---|---|
| FlowWorks pit states | depth 1–4 × fill 0..D × liquid (water, tar, oil, slime, …) × ground (dirt, stone) + dry + scorched | ~100+ cells, **every legal pair** — fill decoupled from depth (fixes finding 8) | `organic:false`, `differs_from` along every axis, colour family per liquid |
| creature roster | species × facing (S, E, N; W mirrors E) × life stage × gender where graphics differ | 20 species → ~60–120 | colour family from the roster/canon brief, `differs_from` between facings |
| plant growth | species × growth (0.15, 0.5, 1.0) × leafless/harvestable | 3–4 per species | `differs_from` across stages, `may_overflow` for trees |
| apparel / xenotype | pawn × item or xenotype, naked + dressed, facing S | per sitting | `holes_ok` false, skin colour family |

## 4. Cell→pixel mapping

RimWorld's map view is orthographic and top-down, so the mapping is an **axis-aligned affine per axis**:
`u = ax·X + bx`, `v = az·Z + bz` with `az < 0` (world Z up, image v down), X/Z continuous cell coordinates
(`artboard/geometry.py`). Three ways to get it, best first:

1. **From the capture tool itself (exact).** The `artboard_capture` tool (§11) renders a given cell rect
   to a fixed-size texture and returns `{ppc, origin_px, frame:[W,H]}`. No inference at all. Preferred.
2. **From markers in the scene (robust, tool-free).** Place ≥3 high-contrast markers at known cells at the
   board corners (a vivid terrain patch, or a subject whose position is certain), read their centres in the
   frame, fit by least squares per axis (`geometry.fit_markers`). The fit reports a **residual**; a marker
   off by one cell shows ≥ ppc/3 residual and the board refuses rather than absorbing it (selftested).
   Automatic marker detection (find the marker colour's blobs) is a small follow-up, not built.
3. **From `get_camera_state` + screen size (fallback).** Camera position and `rootSize` give the visible
   rect, but the relation between `rootSize` and pixels-per-cell must be measured from the engine
   (`CameraDriver`, via RimSage) before it is trusted — UNMEASURED here, so markers or (1) win.

Segmentation then takes each subject's cells, adds the allowed **overhang** (sprite drawn past the
footprint) to make the **core**, adds the **pad** to make the **crop**; the ring between them should be
plain ground. A better source than cell rects is the thing's real **draw rect** (`DrawPos` ± `drawSize/2`)
returned by the staging tool; the board format accepts it as `size`/`overhang` per subject.

**Resolution per class** (the owner plays with enhanced zoom; never down-resolve):

| class | px/cell target | why |
|---|---|---|
| pits, terrain, fluids | 48–64 | surface texture, shimmer, face rims are a few px tall at 32 |
| creatures, pawns, apparel | 96–128 | facial/marking detail; matches the true-scale panels' 128–256 |
| plants | 64–96 | leaf/fruit read |
| overview tier-(a) only | 24–32 | enough for EMPTY / MISSING_TEXTURE / OFF_CELL on a whole map |

A 1920×1080 frame at 96 px/cell holds 20×11 cells, so a 60-subject roster board is 3–6 **tiles** — each
tile its own capture with its own exact mapping; segmentation is per tile and indifferent to how many.

## 5. Tier (a) deterministic checks (built)

`artboard/checks.py`. Foreground = pixels that differ from the ground: per-pixel against a **clean plate**
(the same rect captured before staging — exact) or, without a plate, distance from the ring's median
colour (good on flat ground, weaker on busy ground; the report says which mode ran).

| check | fires when | catches |
|---|---|---|
| `OUT_OF_FRAME` | the crop leaves the frame | camera or geometry wrong — the board is invalid, not the art |
| `MISSING_TEXTURE` | ≥15% of the core is pure magenta | unresolved texPath (RimWorld's missing-texture colour) |
| `EMPTY` | ≤2% of the core differs from ground | invisible/unspawned subject; the detail says if the ring holds it (displaced) |
| `OFF_CELL` | foreground centroid > 0.3 cell from the core centre | stager moved the subject, or a wrong drawOffset |
| `WRONG_COLOUR` | expected colour family < 20% of foreground | swapped textures, wrong mask/tint, wrong liquid |
| `OVERFLOW` | > 4% of the ring is foreground | sprite drawn outside its cells (drawSize), or an intruder |
| `TRUNCATED` | a ruler-straight solid bbox side on an `organic` sprite, not at the crop edge | texture cut off at its draw rect / bad atlas |
| `HOLE` | enclosed ground-coloured pixels ≥ 6% of the silhouette | alpha holes, missing layer; in ring mode also a body coloured like the ground (detail says so) |
| `IDENTICAL` | two `differs_from` crops differ by < 6 mean | two states/facings/stages render the same |
| `REF_DRIFT` | > 10% of core pixels changed vs the approved reference | anything changed since the owner accepted it |

Every check reports what it measured (`metrics` per row: fg shares, colour histogram, centroid offset,
edge solidity, hole share, ref change). Thresholds live in `checks.DEFAULTS`, overridable per board.
**Each check is proven both ways** by `artboard/selftest.py`: it fires on its planted defect (magenta
cell, empty cell, swapped pair, cut sprite, oversize sprite, identical state pair, holed sprite, off-frame
camera, mis-placed marker) and the clean board and untouched controls produce **zero** findings — in ring
and plate mode.

## 6. Tier (b) batched vision pass (inputs built; the read is an agent's)

`run.py` writes `vision_mosaic.png` (only crops that passed (a), labelled `#1…#n`, upscaled NEAREST,
never blurred), `vision_key.json` (tile → subject id, question, canon path, tile rect) and
`vision_prompt.md`. One agent read of the mosaic answers every tile `PASS` / `FAIL <why>` / `UNSURE
<why>`. Rules:

- **Narrow questions** from the recipe ("is this one creature facing south, head and body both drawn?",
  "is the liquid surface visibly different from the fill-1 tile beside it?"), never "is this good art".
- ≤ ~48 tiles per mosaic so each tile stays ≥ 160 px; split by class, never mix pits with creatures.
- Canon subjects: the mosaic is per-subject paired with the canon entry's `## Must show` text in the
  prompt; the **reference images** go to the owner's board (§7), since the vision pass checks
  presence of listed features, not likeness.
- A model's FAIL is **evidence, not a verdict** (as with subagent verdicts): it routes the tile to the
  owner with the model's sentence attached; it never rejects art on its own.

## 7. Tier (c) what the owner sees

- **In game, first:** the board is saved as a keeper savegame (one map, all options, grid key — the
  2026-09-02 ruling) and he walks it at his own zoom. The board's grid key IS the recipe.
- **Beside it, a short flagged list** (`owner_board.png` + the report): only subjects flagged by (a) or
  FAIL/UNSURE in (b), plus rows that are subjective by nature (style, canon likeness). Each row: the crop,
  the finding sentence, the canon reference images and `## Must show` when the subject has a canon entry,
  and Accept / Change / Unclear — recorded through the existing review-sheet machinery
  (decisions-as-data, `review-sheets` skill), never a hand-rolled page.
- He never sees the passes. A count line says how many were checked and passed, by which tier.
- **Never fullscreen or steal focus** to capture: the capture tool renders off-screen (§11). The
  system-screenshot route stays for the case where the bridge cannot render.

## 8. References: approval and storage

- A reference is a **core crop** the owner Accepted, captured under a fixed **board recipe fingerprint**
  (zoom px/cell, ground, light, weather, mod-set fingerprint). A reference is only compared against crops
  with the same fingerprint — a crop at another zoom is not comparable and the check reports UNMEASURED.
- `run.approve(out, ids, ref_dir)` copies Accepted crops; it must be called **only** on an owner Accept
  or an art-ledger owner ruling — an agent's own pass never creates a reference (that would let an agent
  approve its own art).
- Storage: pixels in the content-addressed store beside the art ledger's (`D:\Luke\dev\_artstore\`), not
  git. Proposed art-ledger event (for the ledger's owner to accept or reshape):
  `render_ref {slot, set, recipe_fp, crop_sha, said, via}` — the reference is bound to the **set version**
  the owner kept, so installing a new set invalidates it automatically rather than drifting silently.
  The owner's rulings stay in `infrastructure/state/art_rulings/`.

## 9. What it cannot decide

- **Taste and canon likeness.** Whether a Nuna looks like a Nuna is the owner's (and the canon gate's);
  (a) checks presence and integrity, (b) checks listed features, neither rules on style.
- **Motion.** Shimmer, wakes, flight cycles, Spastic wiggles are temporal; one frame cannot show them. A
  short frame-burst of the same rect could (diff between frames = "is it animated at all"), but flyers
  are never live-tested unattended (owner, said three times) — flight stays a state read + a joint session.
- **Depth/occlusion semantics** (is the pawn hidden *below the near lip* for the right reason) — a mask
  can say "less of the pawn is visible at D4 than D1" (a monotonic check, feasible), not why.
- **Busy ground without a plate.** Ring mode on textured biome floor gives false HOLE/OVERFLOW (seen in
  the trial, §12). Plate mode is the answer, not tighter thresholds.
- **Lighting-dependent colour.** Colour family is measured under the recipe's noon light only.
- **Overlap by design** (a tree canopy over the next cell) — declare `may_overflow`, or widen the pitch.

## 10. Cost model

Per board, compared with today's 34-station FlowWorks visual board:

| | today (34 stations) | contact board (all ~100+ pit states) |
|---|---|---|
| staging | ~700 bridge calls (`station_ops`, one per cell op) ≈ 5–14 s bridge time at 6–20 ms/call | 1 `artboard_stage` call (§11), or ~40 batch calls with today's tools |
| capture | 1 shot per station if an agent reviews (34 framings + shots) | 1 plate + 1 board capture per tile; ~3–6 tiles at 48–64 px/cell |
| per-item decision | an agent interpretation per station (median 3.7 s each, plus deliberation — the 66%) or the owner per station | tier (a): < 1 s for the whole board, no model |
| model image reads | 34 | 1–3 mosaics |
| owner attention | every station | flagged + subjective rows only, plus a walk of the keeper save |

The dominant saving is the agent turns, not the bridge: one deliberation per board instead of per item.
Measured offline: the 13-subject trial (§12) segmented and checked in well under a second.

## 11. Bridge tools needed (spec for the runner owner — no C# written here)

1. **`jawa/artboard_stage`** — one call stages a whole recipe. Input: the recipe's subjects
   (`{id, kind: pawn|thing|plant|terrain|pit, def, cell, rot, lockRotation, growth, stuff, strip,
   fluid, fill, depth}`), ground terrain + rect, `clearRect:true`, `killHostiles:true`. Output per subject:
   `{id, thingId, actualCell, drawRect:{x,z,w,h} in world units, ok, error}`. **Refuses to relocate**: if
   the cell is blocked it reports `ok:false` instead of silently picking a neighbour (the trial shows that
   fallback breaks geometry — `stage_xenotype_grid.py` does it today).
2. **`jawa/artboard_capture`** — renders a world rect to an off-screen RenderTexture at a requested
   px/cell, with UI, labels, selection boxes and overlays suppressed, **without resizing, focusing or
   fullscreening the window**. Input `{x, z, w, h, ppc, fileName, plateFirst:bool}`. Output
   `{path, platePath, ppc, origin_px, frame:[W,H], cameraState}`. `plateFirst` hides the staged subjects
   for one render (or the runner captures the plate before staging). This makes §4 exact.
3. Optional **`jawa/thing_screen_rects`** — for things already on a map (a review map someone else
   built), return each thing's draw rect in pixel coordinates of the last capture, so an existing scene
   can be segmented without a recipe.

Until they exist, the method runs with today's tools: batch terrain/spawn ops, `jawa/screenshot_mode`,
`rimworld/frame_cell_rect` + `jawa/take_screenshot`, and **markers** for the mapping.

## 12. First real trial — 2026-10-06

Subject: `Transient\xenotype_review\xeno_grid_v2.png` (1298×950), staged 2026-10-02 by
`stage_xenotype_grid.py` — 13 naked xenotypes, 5 columns, spread 7. No geometry was saved with the shot,
so the mapping was **fitted from three pawns used as markers** (25.0 px/cell). Board:
`src/RimMandrake/Utils/artboard/trials/xeno_grid_v2.board.json`; output (report, crops, both mosaics):
`Transient\artboard_trial_2026-10-06\`.

Result: 13 crops, all landing on the intended pawns; **8 passed (a), 5 flagged**:

- **Real staging defects caught (3):** `Pam` EMPTY and `Zihao` OFF_CELL + OVERFLOW — both sit one cell
  east of their declared cell; `Nails` OFF_CELL — one cell south. The stager's "pick the nearest open cell"
  fallback moved them silently. Harmless for a human glance, fatal for any per-cell automation — hence
  §11's refuse-to-relocate rule. The frame also holds **three pawns that are not on the grid** (Kena,
  Philip, Reid), i.e. leftovers from an earlier stage; a board-level "foreground outside every crop"
  check would catch those (follow-up).
- **False positives (2):** `Noob` and `Ems` HOLE — their tan bodies are the ground's own colour, so in
  ring mode only the dark outline counts as foreground and it encloses "ground". This is exactly the
  busy/matching-ground limit of §9; the HOLE detail now says so, and a plate removes it. (It is still a
  legibility observation worth one line to the owner: those two skins vanish on this ground.)
- **Pawn name labels** sit inside every crop's ring and partly in the core; they must be suppressed at
  capture (`screenshot_mode`). They did not trip OVERFLOW here, but they would on a tighter pitch.
- **Tier (b) on the 8 survivors, one read** (this agent, as the vision pass): all eight are single
  south-facing figures; `Sophie` is a thin dark sprite barely distinguishable from the ground (UNSURE —
  possible missing body layer), and `Fernandez`, `Nails`, `Sayuri`, `McCann` read grey/white — for a
  **skin** review that is UNSURE (default/unset skin vs a genuinely grey species needs the canon entry).
  That is 5 owner rows out of 13, from one image read.

Not trialled: `Transient\pyre_artgrid.png` (Pyrelands creatures scattered on ember grass, alerts panel
over the right third) — no grid, no recorded cells, so it cannot be segmented; it is the counter-example
that motivates staging to a recipe and clearing the UI.
