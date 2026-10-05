# Graffiti north-star trial plan — the pipeline pilot

Mod: `src/RimMandrake/Graffiti` (`mandrake.rm.graffiti`). Walk:
`design/validation_walks/RimMandrake/Graffiti.md`. Suite: `src/RimMandrake/Graffiti/validation.py`.
Parent item: `GRAFFITI_NORTHSTAR_TRIAL_1`. Rung items: `GRAFFITI_NORTHSTAR_WIRED_1`,
`GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1`, `GRAFFITI_NORTHSTAR_GREEN_FULL_1`, `GRAFFITI_NORTHSTAR_SHIP_1`.

Owner, typed 2026-09-30: *"Yes. Write out comprehensive northatar plans for all three and ticket
them out as trials for full completion. Use gpt reviews for their validation plan especially site
preparation that's often overlooked before a proper test setup. I'd like this to go very well. Then
use ultra fast python to drive the bridge to validate. Make it happen!"*

Graffiti is the **first mod meant to reach GREEN** under the north-star system. No mod can be GREEN
today. MEASURED 2026-09-30: `shows=` appears in 0 of 57 `validation.py` files. Nothing here has been
run, so every live claim below is UNMEASURED until a trial records it.

---

## 1. Current state, rung by rung

| rung | state | evidence |
|---|---|---|
| DRAFT → **VALIDATED** | ✅ **done** | MEASURED 2026-09-30, `modcheck floor --all`: `Graffiti VALIDATED 8 must / 0 covered / 8 uncovered → REFUSED (uncovered)`. Hash `335bccf3…` matches. Owner's words: *"Validate now, all 10 lines"* (2026-09-16). |
| VALIDATED → **WIRED** | ❌ not started | MEASURED: 0 of 8 must-show ids and 0 of 2 cannot-show ids are claimed by any `shows=` in `validation.py`. |
| WIRED → **GREEN (minimal)** | ❌ blocked | A run is REFUSED until WIRED. It is also blocked on art (§5): 11 punk marks and 27 meme glyphs ship **with no texture** (MEASURED below). Two bars fail today by design (`never_real_world_english`, `mark_carries_no_earth_signage`). |
| GREEN (minimal) → **GREEN (full)** | ❌ | `modcheck run` only produces `min+<mod>` configs (MEASURED from `runner.run`). A full-list run is a separate driver path (§6). |
| → **SHIPPED** | ❌ | Code review: **19 of 19** `Source/*.cs` + `validation.py` are CLEAN (MEASURED 2026-09-30, `code_review_status.py check`). Deploy: "in sync (28 files)" (MEASURED 2026-09-30, `deploy_custom_mods.py --mod Graffiti` dry run). The DLL has **no `.srchash` sidecar** (MEASURED: 43 sidecars exist under `src/`, and Graffiti has none). It was last built 2026-09-24 (`8d5434e5c`), which is before the stamp guard. There are 6 settings. Art is incomplete. |

### Facts measured this pass that change the plan

1. **The spree no longer paints only `RM_Graffiti_Vandal`.** `JobDriver_PaintGraffiti` calls
   `GraffitiPool.PickForSpree(pawn)`, which takes a weighted pick over every def with a
   `ModExtension_Graffiti` whose form is Scrawl, Tag, ThrowUp or Glyph. That is Vandal (weight 3),
   Tag_A/B/C (weight 2 each), ThrowUp_A/B (1 each), Scratches, TallyMarks and WarningGlyph (1 each),
   plus any meme glyph whose meme the painter's ideo holds. **`validation.py` counts only
   `RM_Graffiti_Vandal`.** A spree that paints six Tags therefore reads as "no mark". That is a
   **false-fail** in the shipped suite.
2. **38 mark defs point at texture folders that do not exist.** MEASURED (glob over every
   `texPath`/`sigilFrameTexPath` in `Defs/`): only Vandal (6 files), Scratches (3), TallyMarks (3) and
   WarningGlyph (4) have PNGs. The rest have none: Tag_A/B/C, ThrowUp_A/B, CrossOut,
   Stencil_Crown/Gear/Fist, Paste_Flyer/Wanted, SigilFrame_Halo, and all 27 `RM_Graffiti_Glyph_*`. The
   deployed copy matches, with the same 4 folders. **The art exists but is not wired.** It sits in
   `infrastructure/artpipe/_artsrc/` (63 graffiti/glyph job folders, untracked), and the matching
   `done/*.manifest.json` files read `status: ok`. That includes `graffiti_vandal_regen_v1_0..5`, the
   regen that `never_real_world_english` is waiting on. Per the 2026-09-20 ruling, look for an owner
   ruling on that art before regenerating any of it.
3. **The walk has false lines outside the hashed section.** They say "`thingClass` = `Filth`" (it is
   now `RimMandrake.Graffiti.Filth_Mark`) and "nothing reads `ModExtension_Graffiti` yet" (GraffitiPool,
   Filth_Mark, RaidExitTagger and AutoCleanProtection all read it). The `validation.py` docstring
   claims "none of the four shipped ThingDefs carries a `<modExtensions>` block" and "four real
   settings", but **6** toggles exist. These are corrected in `GRAFFITI_NORTHSTAR_WIRED_1`, and none of
   them is in the hashed section.
4. **Two settings toggles are not covered by the suite.** `suite.toggles` lists 4. The code has 6:
   `raidExitTaggingEnabled` and `autoCleanProtectionEnabled` are missing. That is a floor gap.
5. **Painted marks land on the standable floor cell beside the wall, not in the wall.**
   `GraffitiJobUtility.TryFindWallMarkCell` picks a standable cell that has a full-fillage edifice
   cardinal to it. The graphic is an unlinked `Graphic_Random` that draws the whole motif on that floor cell
   (the old `CornerFiller` wall link drew a 3.5% atlas crop and was removed by GRAFFITI_LINKED_MARK_FIX_1). So
   `mark_sits_on_the_wall` tests the mark's cell, not a wall-face draw.
6. **Marks are filth, and colonists clean filth.** Cleaning, rain wash (`rainWashes=true`) and
   going-over (`Filth_Mark.MakeMark` destroys a rival def at the same cell) can all remove evidence
   between paint and shutter. This is a site-prep problem (§3).

---

## 2. The bars and their bindings

The **judge** (`modcheck/judge.py`) grades **the LAST screenshot of each component** against each id
in that component's `shows=`. It asks `claude -p` a narrow yes/no question, and UNJUDGEABLE counts as
a fail. So each visual bar needs a component whose final screenshot is framed for exactly that
question. Several ids can share a component only if one image answers all of them.

The floor (`runner.visual_floor`) refuses only **uncovered must-show** ids. Cannot-show ids are not
enforced. **This plan claims both cannot-show ids anyway**, because a GREEN that never photographed the
English-text defect would be a false pass. The driver pre-flight refuses if either cannot-show id is
unclaimed (§6).

Every visual component **also** carries a state predicate. A screenshot cannot be the only evidence
that the subject is in frame (judge rule: *"Do NOT answer YES because the mechanics probably work"*).
The reverse also holds: the state alone is not GREEN.

**Def sets, all resolved live, never hard-coded** (GPT #3/#4). Class tests use `IsAssignableFrom(Filth_Mark)`, never equality:
- **M_base**: visual mark defs whose `modContentPack.PackageId` = `mandrake.rm.graffiti`. This is the
  domain of every *appearance* bar.
- **M_pool(ideo)**: what `GraffitiPool.PickForSpree` can actually return for the test ideo. That is
  the domain of the *painting* state predicates.
- **M_desig**: `designatorEligible`.
- **M_all**: every `Filth_Mark`-derived def from any mod. That is the domain of cleanup and of "no
  stray marks".

On the full list, foreign members (SacredGraffiti, GraffitiImperial) are judged in separately reported
**compatibility** components that are not bound to Graffiti's bars. A sacred mark can correctly fail
"punk/urban".

**Variant coverage is exact, not sampled** (GPT #8/#55). Every appearance bar is judged over **every
live `Graphic_Random` subgraphic of every M_base def**. The list is enumerated from the running game
(§6.7), not from a PNG count. Each variant is placed through a variant-pinning fixture. If a variant
cannot be pinned, the component returns REFUSED, never a partial judgement.

**Galleries are paged grids** (GPT #9). M_base is 15 own defs + 27 glyphs today, × variants. Each page
is 4 short wall runs × 4 slots, which fits one screen at play zoom. Each page is its own component
claiming the same ids. **MEASURED from `judge.judge_run`/`visual_all_green`:** every claim's result is
flattened and passed through `all()`, so a bar claimed by N pages passes only if **all N pass**. That
AND is built in (GPT #54).

**Captures are transactional** (GPT #47/#52):
1. pause;
2. frame;
3. clear UI;
4. re-run the component's full state/layout predicate;
5. capture;
6. record the hash plus camera, map and tick metadata;
7. run a post-capture identity check;
8. crop to the playfield ROI (UI English cannot trip `never_real_world_english`).

The driver burns a slot-map caption (which slot is a mark and which a control, with coordinates) into
a margin, so the judge's narrow question has a referent.

| # | bar id (polarity) | component (chain) | state predicate (pass ⇔) | `shows=` screenshot framing | live? |
|---|---|---|---|---|---|
| 1 | `mark_actually_appears` (must) | `spree_paints_marks` (chain `spree_wall`) | **each painter has its own wall lane**, separated by more than the 12-cell search radius (GPT #5/#6). For each lane, ≥ 1 **M_pool** thing whose `Filth_Mark.maker` = that painter, on a cell with a cardinal full-fillage wall. The mark must be **naturally rendered**: no `map_commit` after painting (GPT #51) | one lane at play zoom: the wall plus its marks, with the painter despawned first (a mentally broken pawn cannot be drafted, GPT #26) | yes |
| 2 | `marks_visibly_various` (must) | `spree_variety` (same chain) | across lanes, **≥ 3 distinct resolved textures from ≥ 2 forms** (GPT #49). Measured as a count of placements, not elapsed ticks: run until ≥ 18 placements or the deadline (GPT #7). The histogram goes in the sheet | all lanes framed on one screen at play zoom, or paged with AND | yes |
| 3 | `mark_reads_at_play_zoom` (must) | `gallery_page_<k>` (chain `gallery`, one component per page) | **every variant of every M_base def** (GPT #10) sits in its pinned slot, read back by ID, cell and resolved texture path | page at calibrated play zoom (**1 cell ≈ 64 px**, measured on the PNG, §3.9) | yes |
| 4 | `mark_reads_as_deliberate` (must) | `gallery_play_zoom` | as #3 | same image as #3 | yes |
| 5 | `mark_register_is_punk_urban` (must) | `gallery_play_zoom` | as #3 | same image as #3 | yes |
| 6 | `mark_carries_no_earth_signage` (must) | `gallery_page_<k>` (every page, GPT #12) | as #3 | as #3. **Expected FAIL today** on WarningGlyph (`GRAFFITI_WARNGLYPH_INUNIVERSE_1`) | yes |
| 7 | `mark_sits_on_the_wall` (must) | `wall_closeup` (chain `spree_wall`) | the exact painted mark IDs (≥ 1) on cells cardinal to one straight wall run, with nothing else on those cells, and all inside the viewport with margin (GPT #48). The shot promises only what the predicate proves | that run at `rootSize` ~14 | yes |
| 8 | `mark_ugliness_is_visible` (must) | `beauty_pair` (chain `gallery`) | `jawa/thing_stats` Beauty is read from the spawned things: Vandal **= −15** (left slot) and TallyMarks **= −3** (right slot), one predetermined variant each (GPT #50) | the pair at play zoom, captioned left/right | yes |
| 9 | `never_real_world_english` (cannot) | `closeup_page_<k>` (chain `gallery`) | **every variant of every M_base def** (GPT #11) in pinned slots. Judged 3× and unanimity required (GPT #53) | close-up pages at `rootSize` ~12, cropped to the playfield. **Expected FAIL today** ("TARTE" in `vandal_0.png`) | yes |
| 10 | `never_reads_as_dirt` (cannot) | `dirt_page_<k>` (chain `gallery`) | **every M_base variant** (GPT #13), each paired with a vanilla `Filth_Dirt`/`Filth_Trash` control slot at known coordinates. Judged 3× and unanimity required | pages at play zoom, captioned mark/control | yes |

### State-only components (no `shows=`; required for the floor and the toggles)

| component | asserts | binding | live? |
|---|---|---|---|
| `defs_load_clean` (walk step 1) | `Player.log` since this load has no `Config error` naming `mandrake.rm.graffiti` and no XML error naming any `Defs/*Graffiti*.xml` | log read through `jawa/drain_log` from the load's start offset. Fail = any match | yes (log) |
| `defs_resolve` (walk steps 2–6) | `RM_Graffiti_Vandal` exists, its `thingClass` is **`RimMandrake.Graffiti.Filth_Mark`**, `placementMask` ⊇ Unnatural, and `ModExtension_Graffiti` is non-null. `RM_PaintGraffitiJob.driverClass` is `JobDriver_PaintGraffiti`. `RM_PaintGraffitiJoy` → `RM_PaintGraffitiJob`. The `RM_GraffitiPaintingSpreeBreak` worker resolves | `jawa/get_defs defs="ThingDef/RM_Graffiti_Vandal"` (a STRING; a list raises `InvalidCastException`). Read `success`/`foundCount`/`notFound`, and treat a failed call as UNMEASURED, never ABSENT | yes, read-only |
| `textures_resolve` | every def in **M** has a non-error graphic (no `BaseContent.BadTex`/magenta) | new driver read: the thing's resolved `Graphic.MatSingle.mainTexture.name` ≠ `"BadTex"` (§6). Offline mirror: a glob of each `texPath` in the deployed folder | yes + offline |
| `terrain_accepts` (new, GPT #17/#18) | the chosen floor's `TerrainDef.filthAcceptanceMask` ⊇ Unnatural, read directly. A matched **rejecting** control cell gets the same placement path and **0** marks, while the accepting cell gets ≥ 1 | `get_defs TerrainDef/<floor>` + `ordered_job` | yes |
| `paints_mark_at_interval` (existing) | `jawa/ordered_job RM_PaintGraffitiJob` at a wall-adjacent cell leaves ≥ 1 new **M_pool** thing, polling the milestone up to a generous deadline (GPT #56) | existing chain. **Fix:** count M_pool, and spawn a wall | yes |
| `joy_path_paints` (new, GPT #19) | a pawn with recreation at 0.2, a Joy timetable slot, and a wall nearby takes `RM_PaintGraffitiJob` **through `JoyGiver_PaintGraffiti`**. Joy rises, the joy kind is Meditative, and a mark appears | `pawn_need`, `timetable`, `pawn_get` | yes |
| `spree_paints_repeatedly` (new, GPT #20) | inside one continuous `RM_GraffitiPaintingSpreeState`, ≥ 2 placements by the same maker, separated in `placedTick` | `Filth_Mark.maker`/`placedTick` read | yes |
| `paint_interval_cadence` (new, GPT #23) | at `paintIntervalTicks` = 60 and = 1000, one painter's `placedTick` spacing tracks the setting | `mod_settings_field` + `placedTick` | yes |
| `mental_break_assigns_paint_job` (existing) | the forced break starts `RM_GraffitiPaintingSpreeState`, and the pawn's job is `RM_PaintGraffitiJob` within 300 ticks | `pawn_force_mental_break` → `pawn_mental` + `pawn_get` | yes |
| `painting_toggle_blocks` (new, GPT #22) | same prepared pawn and lane: an **enabled positive control first** (≥ 1 mark); then disabled (no paint job is given, and 0 marks); then the order reversed on a fresh lane | `mod_settings_field` + `pawn_get` job + mark count | yes |
| `viewer_reaction_setting_flips`, `breach_bias_setting_flips` (existing) | setting write + read-back | `jawa/mod_settings_field` | yes |
| `raid_exit_tag_setting_flips`, `auto_clean_protection_setting_flips` (new) | setting write + read-back; closes the floor gap (§1 fact 4) | `jawa/mod_settings_field` | yes |
| raid-exit and auto-clean behavioural A/B (new, GPT #21, **diagnostic, not a GREEN gate**) | an exiting raider tags when the setting is on and does not when it is off. A protected mark draws no cleaning job when the setting is on | `lord_*`, `prioritized_work` | yes |

Only the def-existence half of `defs_resolve` and the texture glob have an offline mirror, and the
mirror is a pre-flight aid. It never replaces the live read (def dumps drop fields: no statBases).

---

## 3. Site preparation — everything true before the first assertion

`prep_site()` runs once per session and `preflight()` runs **before every chain**. Each line below
is an assertion that refuses the run with a named reason. **A dirty site aborts the run. It is never
"warned and continued".**

### 3.1 Mod list (tier)
- **Minimal rung:** `ModsConfig.MINIMAL.xml` plus `mandrake.rm.graffiti`, appended by
  `runner.compose_test_list`. MEASURED 2026-09-30: MINIMAL already carries all five DLCs (Royalty,
  Ideology, Biotech, Anomaly, Odyssey), Harmony and `brrainz.rimbridgeserver`.
  ⚠️ **Do not use the `modset_builder.py graffiti` tier as written.** It adds
  `mandrake.rm.sacredgraffiti`, which inherits `RM_BaseGraffiti` and adds `RM_SacredMark_Ishko` into
  **M**. That changes the pool and the gallery. Graffiti's GREEN must be Graffiti alone. SacredGraffiti
  gets its own trial.
- **Assert after load:** parse the live `ModsConfig.xml` (ElementTree, never a `<li>` grep), and also
  `jawa/dlc_status` for all 5 DLCs **active in the running game**. ModsConfig names only the NEXT load.
  Also assert that the JawaBench companion answers a tool call (`jawa/map_info`).
- **Full rung:** `ModsConfig.FULL.LATEST.xml` as the owner's real list. Record the active count
  (parse it; ~630). Also record which other mods add **M** members (GraffitiImperial, SacredGraffiti)
  and whether any mod cleans or hides filth. These change the pool, so they are allowed. The gallery
  takes **M** live and does not hard-code it.
- `modcheck run` REWRITES the live `ModsConfig.xml` and restores FULL from a `finally`. This trial
  is the first live exercise of the fixed `swap_to_test_list`/`restore_full` path. **Back up
  `ModsConfig.xml` to `infrastructure/state/modlists/` before the run, and diff it after the restore.**

### 3.2 Deploy freshness
- `deploy_custom_mods.py --mod Graffiti` must print `in sync`. Its plan output is the fingerprint.
  Never use folder mtime.
- **DLL provenance:** rebuild `Graffiti.csproj` so that `src/Directory.Build.targets` writes
  `RimMandrakeGraffiti.dll.srchash`. Then `dll_source_stamp.py check` must pass for it. **Byte-compare**
  the deployed DLL to the repo DLL (sha256).
- The deployed `Textures/` tree must equal the repo tree file for file. This matters most after the
  art wiring (§5).
- A DLL can only be deployed while the game is DOWN. Order: deploy, then launch.

### 3.3 Mod Settings state
- Read all 6 fields through `jawa/mod_settings_field`. Assert they equal the shipped defaults:
  `paintingEnabled=true`, `paintIntervalTicks=250`, `viewerReactionEnabled=true`,
  `breachBiasEnabled=true`, `raidExitTaggingEnabled=true`, `autoCleanProtectionEnabled=true`.
- Every toggle component **restores the default in a `finally`**, and the next pre-flight re-reads
  all six. A run that flips `paintingEnabled` off and crashes would otherwise false-fail every later
  chain.
- Write settings with `persist=False`, so the owner's `Config/Mod_*` file is never touched.

### 3.4 Save/map choice
- **Quicktest debug game** (`rimworld/start_debug_game_ready`; VERIFIED on the full list
  2026-09-27). Never the canonical start save: map state is disposable, and the save must stay
  pristine.
- **Biome: temperate forest** or any biome whose map has open soil. Assert through `jawa/map_info`
  that the biome is not ice sheet, sea ice or an extreme desert with sand-heavy terrain.
- **Map size:** assert both axes ≥ 150. The anchor is the map centre (`runner._default_anchor`), never
  a constant (`(500,500)` was out of bounds on a 174² map).
- **Test site:** one 40×40 rect at the anchor (cleared), plus a **13-cell exclusion margin** (≥ the 12-cell `TryFindWallMarkCell` radius + 1, GPT #2. No full-fillage edifice may exist anywhere in a painter's search area except our walls. The site is 66×66 in total, and the 52×52 figures below scale to it) in which
  nothing is allowed to exist. That is 52×52 in total.
  - `jawa/clear_area`/`destroy_batch categories=All` across the full 52×52.
  - **Terrain:** `jawa/set_terrain_batch` to one known constructed floor (proposal: `Concrete`) over
    the whole 52×52. Mountain, water, marsh, rich soil and sand are removed as variables.
    **Calibrate once:** `paints_mark_at_interval` runs first. If it paints nothing, the terrain does not
    accept `Unnatural`, and the run aborts with "terrain rejects placementMask". That is an
    environment fault, not a mod fail (§1 of the walk: on a non-accepting terrain, producing nothing is
    correct).
  - Assert through `jawa/get_terrain_batch` that every cell in the rect has the chosen terrain.
  - **Walls:** `Wall` stuff `Steel`. Use straight runs only (no corners) so that `CornerFiller`
    linking is predictable. The spree wall is 20 long on row `z0`, and the gallery walls are separate
    rows ≥ 4 cells apart.
  - Assert **every cell adjacent to a wall is Standable and empty**: no plants, chunks, filth, items
    or corpses. `jawa/list_things` over the rect returns only our walls.
  - **Pre-existing filth:** assert 0 things of category Filth in the rect. A stray `Filth_Dirt` would
    poison `never_reads_as_dirt`.
- `jawa/map_commit` after the terrain and wall writes (stale-mesh trap from the live-review skill).
  Assert the frame is not pure black by checking the PNG's mean luminance after the first shot.

### 3.5 Fog, roof, light, temperature, weather, time, season
- `jawa/set_fog unfog` over the rect. Assert it through a cell read.
- **No roof** over the rect (`jawa/get_roof_batch` = none). Unroofed cells get sky light. A roofed
  test area photographs dark.
- **Time:** step to **12:00 ± 1 h** (`jawa/time_clock` read, `time_set_ticks`). Re-check before
  **every** screenshot, because a 3000-tick spree moves the clock ~1.2 h. If daylight leaves 10:00–14:00,
  re-pin before the shutter.
- **Weather:** `jawa/weather_set Clear lockWeather=true`. Rain washes marks (`rainWashes=true`), and
  fog or snow changes the read. Assert `jawa/weather_get` = Clear before every chain.
- **Season/snow:** pick a quicktest date in summer, or assert snow depth 0 over the rect. Snow drawn
  over the floor hides filth.
- **Temperature:** the cell temperature (`jawa/cell_temperature`) must be 10–30 °C. Painters must not
  break from heatstroke or hypothermia mid-spree.

### 3.6 Research, god mode, dev mode
- No research is needed (filth, walls and jobs have no research gate). Walls are spawned, not built.
- **God mode off** during behavioural chains (painting is a real job). The gallery spawns through
  the bridge, which does not need god mode.
- Dev mode is on (the bridge needs it). **Close the debug log window**
  (`jawa/window_list_close typeName=EditWindow_Log`) and call `jawa/clear_ui` before every shot.
  `rimworld/clear_log` does not close the window.

### 3.7 Pawns
- **Painters:** 6 fresh `Colonist`s, player faction, spawned at walk distance ≤ 3 from the wall.
- **Before each behavioural component:**
  - `jawa/pawn_health healAll`.
  - All needs at 1.0 (`jawa/pawn_need`, `pawn_refresh_needs`). The spree think tree places
    food/rest **before** the paint giver.
  - Artistic skill fixed at **8** (`jawa/set_pawn_skill`), so `SkillGateAllows` is the same for
    every painter.
  - Remove any trait that blocks the break or the mental state (the break may need `canBeAttemptedBy`).
    Assert `pawn_force_mental_break` returns `started=true`.
- **Ideo:** assign every painter one fixed ideo through `jawa/set_pawn_ideo`.
  - Option A (state determinism): an ideo with **no** meme in any glyph's `requiresAnyMeme`, so the
    pool is exactly the 9 ungated marks.
  - Option B (variety realism): the player ideo as generated.
  - **Plan:** A for `spree_paints_marks`; then B for one extra component that records which meme
    glyphs appeared, unbound.
- **Undrafted.** Assert `set_draft false`.
- **Cleaning off:** `jawa/set_work_priority Cleaning 0` on **every** colonist on the map, including
  the quicktest's own starting colonists. Also exclude the test rect from the Home area
  (`jawa/paint_area` remove), because cleaning only runs in Home. Assert both.
- **No hostiles or wildlife:** destroy every non-player pawn within 60 cells. Disable the storyteller
  for the session if a tool exists (otherwise accept it and re-check before each chain).
- **Bystanders:** move the quicktest starting colonists ≥ 30 cells away, or despawn them. They
  must not walk through the frame or clean.
- **Before the shutter:** draft the painters and move them out of frame, or despawn them. Their
  bodies must not occlude the marks. Never photograph mid-paint.

### 3.8 Stale modals, letters, messages
- Before every chain: `jawa/clear_ui`, close every `Dialog_*`/`Window`, and dismiss all letters. A
  stale modal blocks every later call silently (memory: five runs lost to one).
- `jawa/log_autoopen_suppress` on, so an error does not pop the log over the frame.

### 3.9 Camera and zoom (the play-zoom bars depend on it)
- **"Play zoom ≈ 64 px per cell" is a measurement on the PNG, not a camera setting.** Calibrate once
  per session:
  - spawn two walls exactly 10 cells apart;
  - set `rootSize` R;
  - screenshot and measure the pixel distance between the wall centres.
  - Adjust R until 640 ± 32 px per 10 cells. Record R and the screen resolution in the run sheet.
- Every visual component calls `rimworld/jump_camera_to_cell` to the **subject rect's centre**, not the
  anchor. Then `frame_cell_rect` or the calibrated R, then `get_camera_state` read-back, then the
  shot. `take_screenshot` ignores `x/z/zoom`. Today's `TestContext.screenshot()` jumps to the anchor,
  which is wrong for every bar here.
- **Screenshot path must be judge-readable.** The judge runs `claude -p` with its Read tool, and
  the bridge returns a Windows path. Copy each shot into
  `Transient/modcheck/graffiti/<run_id>/<component>.png` and hand the judge that path in the form its
  own interpreter can open. Pre-flight: run `claude --version` from **the same interpreter that will
  run the judge** (python.exe under the runner, so this is UNMEASURED today).

### 3.10 Game speed, pausing, tick budget
- **Paused between chains.** Advance only through bounded tick steps (`t.wait_ticks` in ≤ 2000
  chunks), so the frame at the shutter is the frame asserted on.
- Budgets:
  - `paints_mark_at_interval`: 600 ticks.
  - Spree: 3000 ticks (≥ 12 paint intervals × 6 painters).
  - Toggle-off negative: 1500 ticks.
  - Gallery: 60 ticks (settle only).
  - Total ≈ 8–10 k ticks.
- **Timeouts and low TPS are REFUSED/INFRA, never bar RED** (GPT #56). Poll milestones with generous tick deadlines plus a wall-clock watchdog.
- **Abort** if TPS falls under 60 for 30 s (`jawa/time_perf`). A stalled game counted as "no
  marks" is a false fail.

### 3.11 RNG — spawn many
- `GraffitiPool` is a weighted random draw. `TryFindWallMarkCell` picks a random cell from up to 12.
  `Graphic_Random` picks a variant per thing.
- One painter's result is anecdote. **6 painters** is the minimum.
- `marks_visibly_various` is asserted on the state first (≥ 3 distinct defs). If 6 × 3000 ticks
  gives < 3 distinct defs, that is a **real** finding about the pool, not bad luck to retry. Record
  the per-def histogram in the run sheet.
- Record `Rand` seed state / the map seed in the sheet, for replay.

### 3.12 Cleanup between bars
- 🔴 **`sweep`/`destroy_batch categories=All` also destroys the test WALLS** (GPT #1). Every chain therefore builds and verifies **its own fixtures** (terrain, walls, lanes) at its start. Nothing relies on `prep_site` having run once.
- Every chain ends with `session.sweep()`, which already runs in `finally`. It also
  `destroy_batch`es the whole 52×52 for Filth, Pawn and Building, then asserts 0 **M** things in the
  rect before the next chain's pre-flight.
- Painters still in `RM_GraffitiPaintingSpreeState` are despawned, not left to wander. The spree lasts
  25–45 k ticks.
- Restore Mod Settings defaults (§3.3) and weather, time and work priorities if a chain changed
  them.

### 3.14 Additional preconditions (from the GPT review; these override anything above that conflicts)

**Load and provenance**
- **Live mod list.** Compare the running game's `LoadedModManager.RunningModsListForReading` (ids and
  order) to the intended manifest. Also record the game PID and session nonce. Parsing ModsConfig is
  not enough, because it names the next load (GPT #37).
- **Live assembly.** Read the loaded `RimMandrakeGraffiti` assembly's location and MVID. Assert that
  the location is the deployed folder and that its sha matches the stamped repo DLL. A workshop or
  duplicate copy must not be the one loaded (GPT #36).
- **`defs_load_clean` reads `Player.log` from the launch byte offset**, captured before the launch by
  the driver. It does not read from the bridge's first call: XML errors precede the bridge (GPT #38).
  Search for: the assembly name, every `RM_Graffiti*` def name, the XML file names, texture-load
  errors, and exceptions whose stack contains `RimMandrake.Graffiti`.

**Every RPC fails closed** (GPT #41)
- Check `success`, schema, map ID, the returned/expected cell counts and pagination.
- A failed or truncated read is UNMEASURED, and that refuses the run. "Zero marks", "no roof" and
  "no cleaners" are only accepted from a complete, successful read.
- Run a capability/schema pre-flight of every tool the run will use **before the map is touched**.

**Map identity** (GPT #42)
- Every spawn, read, camera and screenshot call carries an explicit map ID, verified against the one
  quicktest map.
- Assert `ProgramState.Playing` and not world view.

**Non-Thing residue** (GPT #33/#34/#35)
- Batch-read **every** site cell for fog, roof, snow, terrain, blueprints/frames, designations,
  zones, fire, gas and pollution.
- The roof is cleared **before** any support is removed. Wait for collapse processing, then clear
  and re-verify.

**Cleaners** (GPT #27)
- Before the first tick, turn off auto-home, cancel every active cleaning job and reservation, and
  despawn every non-test pawn and mech map-wide, plus every modded cleaner.
- Assert that no pawn has a job target in the site immediately before and after every tick advance.

**Incidents** (GPT #28)
- Disable the storyteller and incidents (dev setting or companion tool). Clear queued incidents and
  map conditions.
- No unrelated pawn anywhere on the map: not merely beyond 60 cells.

**Light** (GPT #29/#31)
- Assert zero light-altering map conditions (eclipse, darkness, volcanic winter, modded), weather
  transition complete, and rain rate 0.
- Read `GameGlowAt` on each subject cell immediately before the shot, inside a recorded band.
- Time only ever moves **forward**, between chains and before pawns spawn. It is never re-pinned
  backwards mid-chain.

**Pawns** (GPT #24/#25/#32)
- Use a **fixed pawn template**: baseliner adult, no work-disabling backstory or trait, Artistic
  enabled, capacities ≥ 0.9.
- Assert path and reservation for each painter's own lane target before ticking. Record the
  job-failure reason if a toil ends early.
- Assert that the site temperature is inside each painter's comfortable range, and that no
  temperature hediff appears during the run.

**Mod settings files** (GPT #39)
- Hash and back up `Config/Mod_*Graffiti*.xml` before launch. Compare after the game is **down**,
  and restore on any difference.

**Order of operations at the end** (GPT #40/#58)
1. Stop the game and verify the process is gone.
2. Restore the FULL `ModsConfig.xml` atomically and hash-compare it with the backup.

The full rung is a **fresh launch** on the restored list, with a fresh map and a fresh site. It is
never a continuation of the minimal session.

**Mesh** (GPT #51)
- `map_commit` is called only after **fixture** writes (terrain, walls, spawned gallery). It is
  never called after natural painting.
- Bar 1's image must show marks as the game rendered them unaided. A forced commit is diagnostic
  only.

**Frame validity** (GPT #43/#44/#45)
- Wait for render settlement after a camera move (≥ 2 frames, or a camera-lerp-done read).
- Validate that the image dimensions are as expected and that the file is fresh (hash and time).
- Assert the subject ROI shows the wall's pixels at the projected coordinates.
- Calibrate px/cell from **high-contrast markers on both axes**, and re-check it after every
  framing change.

**Judge canary** (GPT #46)
- Before the run, the exact judge command line, interpreter and cwd must read a freshly generated PNG
  carrying a nonce, and return the nonce.
- `claude --version` is not enough.

**Diagnostic controls** (GPT #30, unbound)
- One gallery page is repeated inside a roofed room under a fixed lamp, and one on a contrasting
  wall stuff (wood). They are reported, not gated. The bars are the owner's.

### 3.13 Pre-flight script
`src/RimMandrake/Utils/northstar_driver/` is the shared driver (§6). Graffiti's own site file is
`src/RimMandrake/Graffiti/northstar_site.py`, which the driver imports. It exposes `prep_site(s)`
and `preflight(s) -> list[str]`. A non-empty list refuses the chain and prints every failed
precondition. Each precondition listed in §3.1–3.12 is one named check, and each check's result is
written to the run sheet, so a GREEN carries its own site report.

---

## 4. Run sequence and expected wall-clock

| step | what | wall-clock (UNMEASURED unless noted) |
|---|---|---|
| 0 | `bridge who` → take, "for GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1" | s |
| 1 | game DOWN: rebuild DLL (srchash), deploy (`--apply`), confirm "in sync" | ~1 min |
| 2 | back up ModsConfig; swap to MINIMAL + graffiti; read back | s |
| 3 | launch via Steam; poll `Bridge token:` in Player.log | minimal list: 22 s on a 13–14 mod list (MEASURED in the load-round skill). MINIMAL is now 26 mods → est. 1–2 min |
| 4 | `start_debug_game_ready`; `prep_site`; zoom calibration | ~90 s + ~30 s |
| 5 | state chains: `defs_load_clean`, `defs_resolve`, `textures_resolve`, `paints_mark_at_interval` (terrain calibration) | < 30 s |
| 6 | chain `spree_wall`: bars 1, 2, 7 + `mental_break_assigns_paint_job` | ~3000 ticks: ~1 min at max speed |
| 7 | chain `gallery`: bars 3–6, 8, 9, 10. Pages: est. ~100 variants after the art wiring ÷ 16 slots ≈ 7 pages × 3 page kinds (gallery, close-up, dirt) | ~3–5 min (UNMEASURED) |
| 8 | toggle chains (6 settings, plus the `paintingEnabled` negative) | < 1 min |
| 9 | judge: ≈ 7×4 gallery ids + 7×3 close-up + 7×3 dirt (unanimity ×3) + ~5 others ≈ 75 `claude -p` calls, ≤ 180 s each, 8 in parallel | ~10–20 min (UNMEASURED) |
| 10 | write sheet; `emit_verify`; release bridge; **stop the game, verify the process is gone, then** restore FULL ModsConfig and hash-compare it with the backup; compare the Mod settings files | ~1 min |
| 11 | owner reads the sheet → `modcheck review Graffiti --owner-said "…"` (needed once before the first GREEN; status reads PENDING-OWNER-REVIEW until then) | his time |

**Minimal rung total: ≈ 25–35 min of machine time, mostly judging (UNMEASURED).** The full rung is a **fresh launch** on the restored list, with a ~15 min cold load (MEASURED 2026-09-07, 599 mods), a fresh map and a fresh site, so ≈ 45 min. The full rung needs the driver's full-list mode (§6.8).
2026-09-07 on 599 mods), so ≈ 25 min.

---

## 5. Gaps that block SHIPPED

1. **Art wiring.** 38 defs have no texture (§1 fact 2). The art is in `_artsrc` with `status: ok`
   manifests.
   - Check for owner rulings (`Transient/*.decisions.json`, review sheets) before wiring or
     regenerating anything.
   - Bars `never_real_world_english` and `mark_reads_at_play_zoom` need `graffiti_vandal_regen_v1_*`
     wired (`GRAFFITI_VANDAL_ART_REGEN_1`).
   - `mark_carries_no_earth_signage` needs `GRAFFITI_WARNGLYPH_INUNIVERSE_1`.
   - **Until then, a run's correct outcome is RED on those bars.** The trial must record that RED
     honestly, not route around it.
   - Per GPT #16, the first execution before the art wiring is labelled a **diagnostic RED**:
     `textures_resolve` fails on 38 defs, and the pages holding them come back UNJUDGEABLE or NO. Its
     sheet lists the expected failures up front, so an unexpected one stands out.
2. **Variant counts.** Vandal has 6 variants against 3 for Scratches and Tally and 4 for WarningGlyph
   (`GRAFFITI_VARIANT_COUNTS_1`). This is content, not a bar.
3. **Mod Settings "superb"** (ruling 2026-09-12). The 6 toggles exist and the slider is 60–1000.
   - Owed: tooltip/description on each, and a worldgen-affecting label (none apply).
   - Owed: confirm that all-off degrades gracefully (painting off also stops raid tagging?), plus a
     reset-to-defaults button.
   - `viewerReactionEnabled` gates a ThoughtWorker that the walk calls dead code. Re-measure
     (SacredGraffiti ships `ThoughtDefs_SacredMarks.xml`). If it is still dead in Graffiti alone, the
     setting misleads.
4. **Code review.** All 19 `.cs` + `validation.py` are CLEAN today (MEASURED). **WIRED edits
   `validation.py` and adds `northstar_site.py`, so both become DIRTY** and need a full review +
   `mark-clean` before SHIPPED.
5. **Deploy.** It is in sync now, but the DLL is unstamped. Rebuild to stamp it, then redeploy
   after the art wiring.
6. **Walk prose** outside the hashed section was false (§1 fact 3). The walk's false lines are **corrected in the same commit as this plan**: `thingClass` is now `Filth_Mark`, the extension is now read, the break is a MentalBreakDef, and step 8 counts every mark def. `modcheck floor` still reads VALIDATED with the hash matching. The `validation.py` docstring is corrected in WIRED.
7. **Hashed-section prose is now stale. Re-validation is needed (owner's word).** "Two of the four
   shipped marks fail it" and "`RM_Graffiti_TallyMarks` and `RM_Graffiti_Scratches` pass … the
   mod's best art" describe a mod that has since grown to 15 own mark defs plus 27 glyphs. That is
   state-dependent prose inside the hash, which the ruling says to correct and then re-validate in the
   same sitting. **Proposed replacement** for the `### what this checklist refuses today, and why that
   is correct` subsection (bars unchanged, ids unchanged):

   > ### known defects this checklist exists to catch
   > `RM_Graffiti_Vandal`'s donor art carried a legible third-party English tag ("TARTE") and read as
   > pixel mush at play zoom (→ `GRAFFITI_VANDAL_ART_REGEN_1`); `RM_Graffiti_WarningGlyph` drew an ISO
   > hazard triangle (→ `GRAFFITI_WARNGLYPH_INUNIVERSE_1`). A mark def whose art is replaced is judged
   > afresh by the run; nothing here records which marks currently pass.

   **No bar text changes are proposed.** The 10 lines stand as validated.

---

## 6. Requirements on the shared fast driver (`src/RimMandrake/Utils/northstar_driver/`)

Graffiti needs these from the driver. Graffiti does not build them.

1. **Session control:**
   - Persistent python.exe bridge connection, batched calls.
   - Pause and `wait_ticks(n)` in bounded chunks.
   - `start_debug_game_ready`.
   - A TPS monitor.
2. **Pre-flight harness:** run a mod's `preflight()` before each chain. Refuse on any failure. Write
   every check's result into the sheet.
3. **Site primitives:**
   - `clear_rect(rect, margin)`.
   - `set_terrain_rect(def)` + verify.
   - `spawn_wall_run(x, z, len, stuff)` + verify.
   - `unfog/unroof` + verify.
   - `weather_lock(Clear)`.
   - `pin_time(hour)` with re-pin before a shot.
   - `ensure_season/snow0`.
   - `map_commit`.
4. **Pawn primitives:**
   - spawn N colonists near a cell;
   - heal, fill needs, set skill, set ideo;
   - `set_work_priority(type, 0)` for **all** colonists;
   - remove a rect from Home;
   - despawn or relocate bystanders;
   - draft and move out of frame.
5. **Camera:**
   - zoom calibration to px-per-cell (measured on the PNG);
   - frame a rect at a calibrated R;
   - `get_camera_state` read-back;
   - `clear_ui` + close the log window;
   - copy the shot to a judge-readable repo path;
   - black-frame / luminance guard.
6. **Reads:**
   - `list_things` by a **set of defs** (or by `thingClass`) in a rect;
   - `get_defs` with `success`/`notFound` handling;
   - `thing_stats` (Beauty);
   - `mod_settings_field` read/write with `finally`-restore;
   - `drain_log` from the load offset;
   - `dlc_status`.
7. **New bridge read (companion tool, if absent):** for a spawned thing, its resolved graphic
   texture name, so BadTex/magenta is detectable. Also its `Graphic_Random` variant path, so a
   cannot-show bar can be shown to have photographed every variant.
8. **Full-list mode:** run a suite against the **current** list without `modlist_swap`, and record the
   config as `full`, not `min+<mod>` (`runner.run` cannot do this today).
9. **Judge plumbing:** `claude -p` must be reachable from the driver's interpreter (checked in
   pre-flight). Run judgements in parallel. UNJUDGEABLE = fail.
10. **Cannot-show enforcement:** refuse if a VALIDATED walk has a cannot-show id that no component
    claims. That is stricter than the floor today, and it should become the floor.
11. **Judge hardening:**
    - pin the model and record the prompt hash on every verdict;
    - retain the full responses;
    - N-fold repeat with unanimity on cannot-show ids;
    - optional known-good and known-bad calibration panels. A `judge.py` change, GPT #53.
12. **Variant pinning:** spawn a `Graphic_Random` thing showing variant k. The companion tool either
    sets the graphic's subgraphic, or rerolls the thingID until the resolved path matches, with a cap.
    It returns the resolved texture path.
13. **Log offset:** record the `Player.log` byte offset before launch, and read from it after.
14. **Live provenance reads:**
    - `RunningModsListForReading` (ids and order);
    - loaded assembly location and MVID;
    - `GameGlowAt(cell)`;
    - active map conditions;
    - every pawn's current job target;
    - auto-home on or off;
    - storyteller and incident disable.
15. **Image tooling:**
    - crop to the playfield ROI;
    - burn in a caption margin;
    - px/cell calibration from markers on both axes;
    - project subject cells to pixels;
    - nonce canary for the judge.

---

## 7. GPT review

Prompt: `Transient/northstar_trials_gpt/graffiti.prompt.md`. Answer: `Transient/northstar_trials_gpt/graffiti.answer.md`.
Codex CLI, read-only sandbox, 2026-09-30. 59 findings.

**Accepted and folded in**

| GPT # | folded into |
|---|---|
| 1, 2 | §3.4, §3.12 |
| 3, 4, 8, 9, 10, 11, 12, 13, 47, 52, 54, 55 | §2 preamble + bar table |
| 5, 6, 7, 48, 49, 50 | bars 1, 2, 7, 8 |
| 14 | bar 1 must come from natural painting, and gallery pages are joined to natural marks by a resolved-texture match |
| 15 | §6.7: traverse every subgraphic and link mask |
| 16 | §5.1: the first run is a diagnostic RED, with expected failures listed |
| 17, 18 | `terrain_accepts` |
| 19 | `joy_path_paints` |
| 20 | `spree_paints_repeatedly` |
| 22 | `painting_toggle_blocks` |
| 23 | `paint_interval_cadence` |
| 24–29, 31–46 | §3.14 |
| 51 | mesh rule |
| 53 | unanimity ×3 on cannot-show bars, plus pinned judge model and prompt hash in the sheet |
| 56 | INFRA vs RED |
| 57 | walk corrections in WIRED, plus an offline `ParentName` structural check |
| 58 | fresh launch for the full rung |

**Accepted in part**

- **#21 (behavioural A/B for every setting).** Added for raid-exit tagging and auto-clean protection
  as **diagnostic** components only. Viewer reactions and breach bias still have no consuming content in
  Graffiti alone (the `validation.py` docstring, to be re-measured in WIRED), and the floor rule is
  toggle *coverage*. Making them GREEN gates would add a bar the owner did not validate.
- **#30 (roofed/lamp and contrasting-wall controls).** Added as unbound diagnostics. They are not
  gates, because the 10 bars are the owner's and do not name lighting conditions.
- **#53 (known-good/known-bad calibration panels in every judgement).** This needs a `judge.py`
  change. It is filed as a driver requirement (§6.11) and is not assumed.

**Rejected**

- **#39, the "isolated config root" half.** Relaunching RimWorld under a separate save-data folder
  changes the very environment under test. Hash, back up and restore instead.
- **#40's premise.** It assumes the game rewrites `ModsConfig.xml` on shutdown. The CLAUDE.md record
  is that RimWorld does NOT rewrite it on exit. The prescribed ordering (stop, then restore, then
  compare) is still adopted, because it costs nothing.
- **#59 (invalidate the owner review on any hash change).** The one-time review is the owner's own
  rule (spec §5.5, `status.record_owner_review`). Changing when it lapses is his call. It is
  **proposed to him** as an open question on the parent item, not implemented.
