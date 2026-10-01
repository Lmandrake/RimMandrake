You are reviewing a validation (test) plan for a RimWorld 1.6 mod, "Graffiti", which is about to become the first mod ever to pass an automated "north star" validation pipeline. The pipeline: a deterministic Python driver talks to a live RimWorld through a bridge (RPC tool calls like jawa/spawn_pawn, jawa/list_things, rimworld/take_screenshot), runs state assertions, captures screenshots, and then an LLM judge (claude -p) answers YES/NO/UNJUDGEABLE per owner-validated visual bar on the LAST screenshot of each component. GREEN requires every state assertion AND every judged bar to pass, plus a one-time owner review.

Attack this plan hard. Priorities, in order:
1. SITE PREPARATION — what preconditions are missing, under-specified, or unassertable? What in the game world (pawns, AI, storyteller, needs, cleaning, weather, lighting, camera, UI, mod settings persistence, map generation, terrain, fog, rooms/roofs, filth mechanics, rendering/mesh staleness, time) could silently differ between runs?
2. FALSE PASS risks — ways the run can go GREEN while the player-visible experience is broken (e.g. judge charity, wrong framing, the subject not in frame, spawned-vs-painted differences, gallery hiding a pipeline defect).
3. FALSE FAIL risks — ways a correct mod reads RED (RNG, timing, cleanup leftovers, tick budgets, path/reservation failures, wrong def set counted).
4. Anything in the bar->binding mapping that does not actually test what the bar says.
5. Ordering/run-sequence and cleanup problems.

Answer as a numbered list of concrete findings. For each: severity (high/med/low), the plan section it hits, the failure mode, and the specific fix (a precondition to assert, a change of binding, or an added control). Do not restate the plan. Do not pad. Be specific to RimWorld mechanics where you can (Filth, FilthMaker.TryMakeFilth, Graphic_Random, CornerFiller link graphics, JobDriver toils, mental states, cleaning WorkGiver, Home area, rain washing filth, roofs and lighting/glow, snow, camera rootSize).

=== THE PLAN ===
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
   cardinal to it. The graphic is `CornerFiller` linked to walls. So `mark_sits_on_the_wall` is a real
   test of the art and link setup, not a formality.
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

The mark-def set **M** is every loaded `ThingDef` whose `thingClass` is `Filth_Mark`. It is resolved
live through `jawa/get_defs`, never hard-coded. State reads count **M**, not Vandal alone.

| # | bar id (polarity) | component (chain) | state predicate (pass ⇔) | `shows=` screenshot framing | live? |
|---|---|---|---|---|---|
| 1 | `mark_actually_appears` (must) | `spree_paints_marks` (chain `spree_wall`) | after the spree, the count of things in **M** within the wall rect is ≥ 1 per painter, and every one sits on a cell with a cardinal full-fillage wall | frame the wall rect at **play zoom** (§3.9). It must show the wall plus marks, with no pawn standing over them (painters despawned or moved out of frame before the shutter) | yes |
| 2 | `marks_visibly_various` (must) | `spree_variety` (same chain, second component, same frame after more ticks) | the marks in the rect cover **≥ 3 distinct defNames** from **M** (spawn-many: 6 painters × ≥ 3000 ticks; §3.11) | same wall at play zoom | yes |
| 3 | `mark_reads_at_play_zoom` (must) | `gallery_play_zoom` (chain `gallery`) | each spree-eligible def in **M** has one instance spawned, one per cell, along a 1×N wall (`jawa/spawn_batch`), and `list_things` reads them all back | the whole gallery at play zoom: camera `rootSize` set so that **1 cell ≈ 64 px** in the capture, measured from the PNG (§3.9) | yes |
| 4 | `mark_reads_as_deliberate` (must) | `gallery_play_zoom` | as #3 | same image as #3 | yes |
| 5 | `mark_register_is_punk_urban` (must) | `gallery_play_zoom` | as #3 | same image as #3 | yes |
| 6 | `mark_carries_no_earth_signage` (must) | `gallery_designator_set` (chain `gallery`) | every **designator-eligible** def (Scratches, Tally, WarningGlyph, CrossOut, Stencils) has one instance on the wall | gallery 2 at play zoom. **Expected FAIL today** on WarningGlyph (`GRAFFITI_WARNGLYPH_INUNIVERSE_1`) | yes |
| 7 | `mark_sits_on_the_wall` (must) | `wall_closeup` (chain `spree_wall`) | ≥ 1 painted mark, one cell off a straight 7-cell wall run, with no other thing on that cell | one wall run with 3 painted marks, framed at `rootSize` ~14 (closer than play zoom, so alignment can be judged), with a straight wall and an unbroken floor | yes |
| 8 | `mark_ugliness_is_visible` (must) | `beauty_pair` (chain `gallery`) | `jawa/thing_stats` Beauty: Vandal **= −15**, TallyMarks **= −3** (read from the spawned things, not the def) | Vandal and Tally side by side on one wall at play zoom, nothing else in frame | yes |
| 9 | `never_real_world_english` (cannot) | `vandal_closeup` (chain `gallery`) | each of Vandal's N variants spawned (N = PNG count on disk; `Graphic_Random` is pinned per instance by thingID, so spawn ≥ 4·N and read `graphic` paths back, or use a variant-index tool, §6) | Vandal row at `rootSize` ~12, so text would be legible. **Expected FAIL today** ("TARTE" in `vandal_0.png`) until the regen is wired | yes |
| 10 | `never_reads_as_dirt` (cannot) | `dirt_control` (chain `gallery`) | one Vandal, one Tag_A and one TallyMarks spawned beside vanilla `Filth_Dirt` and `Filth_Trash` controls on the same wall | that row at play zoom. The control is what makes the question answerable | yes |

### State-only components (no `shows=`; required for the floor and the toggles)

| component | asserts | binding | live? |
|---|---|---|---|
| `defs_load_clean` (walk step 1) | `Player.log` since this load has no `Config error` naming `mandrake.rm.graffiti` and no XML error naming any `Defs/*Graffiti*.xml` | log read through `jawa/drain_log` from the load's start offset. Fail = any match | yes (log) |
| `defs_resolve` (walk steps 2–6) | `RM_Graffiti_Vandal` exists, its `thingClass` is **`RimMandrake.Graffiti.Filth_Mark`**, `placementMask` ⊇ Unnatural, and `ModExtension_Graffiti` is non-null. `RM_PaintGraffitiJob.driverClass` is `JobDriver_PaintGraffiti`. `RM_PaintGraffitiJoy` → `RM_PaintGraffitiJob`. The `RM_GraffitiPaintingSpreeBreak` worker resolves | `jawa/get_defs defs="ThingDef/RM_Graffiti_Vandal"` (a STRING; a list raises `InvalidCastException`). Read `success`/`foundCount`/`notFound`, and treat a failed call as UNMEASURED, never ABSENT | yes, read-only |
| `textures_resolve` | every def in **M** has a non-error graphic (no `BaseContent.BadTex`/magenta) | new driver read: the thing's resolved `Graphic.MatSingle.mainTexture.name` ≠ `"BadTex"` (§6). Offline mirror: a glob of each `texPath` in the deployed folder | yes + offline |
| `paints_mark_at_interval` (existing) | `jawa/ordered_job RM_PaintGraffitiJob` on a wall-adjacent cell leaves ≥ 1 new **M** thing within `waitTicks` = 2 × `paintIntervalTicks` + goto | existing chain. **Fix:** count **M**, and spawn a wall | yes |
| `mental_break_assigns_paint_job` (existing) | the forced break starts `RM_GraffitiPaintingSpreeState`, and the pawn's job is `RM_PaintGraffitiJob` within 300 ticks | `pawn_force_mental_break` → `pawn_mental` + `pawn_get` | yes |
| `painting_toggle_blocks` (new) | with `paintingEnabled=false`, a forced spree paints **0** marks over 1500 ticks; with it true, it paints ≥ 1 | `jawa/mod_settings_field` write + read-back, then count **M** | yes |
| `viewer_reaction_setting_flips`, `breach_bias_setting_flips` (existing) | setting write + read-back | `jawa/mod_settings_field` | yes |
| `raid_exit_tag_setting_flips`, `auto_clean_protection_setting_flips` (new) | setting write + read-back; closes the floor gap (§1 fact 4) | `jawa/mod_settings_field` | yes |

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
- **Test site:** one 40×40 rect at the anchor (cleared), plus a **6-cell exclusion margin** in which
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
- Every chain ends with `session.sweep()`, which already runs in `finally`. It also
  `destroy_batch`es the whole 52×52 for Filth, Pawn and Building, then asserts 0 **M** things in the
  rect before the next chain's pre-flight.
- Painters still in `RM_GraffitiPaintingSpreeState` are despawned, not left to wander. The spree lasts
  25–45 k ticks.
- Restore Mod Settings defaults (§3.3) and weather, time and work priorities if a chain changed
  them.

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
| 7 | chain `gallery`: bars 3, 4, 5, 6, 8, 9, 10 | < 1 min |
| 8 | toggle chains (6 settings, plus the `paintingEnabled` negative) | < 1 min |
| 9 | judge: 10 ids, one `claude -p` each, ≤ 180 s each, run in parallel | ~1–3 min |
| 10 | write sheet; `emit_verify`; restore FULL ModsConfig; diff vs backup; release bridge | s |
| 11 | owner reads the sheet → `modcheck review Graffiti --owner-said "…"` (needed once before the first GREEN; status reads PENDING-OWNER-REVIEW until then) | his time |

**Minimal rung total ≈ 10 min of machine time.** The full rung adds a ~15 min cold load (MEASURED
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
6. **Walk prose** outside the hashed section is false (§1 fact 3). Fixed in WIRED.
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

---

## 7. GPT review

(filled after the codex review, below)

=== THE VALIDATION WALK (bars are in '## north star') ===
# RimMandrake: Graffiti Framework — validation walk
subject: src/RimMandrake/Graffiti  (packageId `mandrake.rm.graffiti`)
deps: none listed in modDependencies (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: engine for the graffiti program, superseding Mlie.GraffitiMod's vandal-spree mechanic — an idle/unhappy artistic pawn seeks the "paint graffiti" joy job or, on a mental break, is forced to paint repeatedly, spawning `RM_Graffiti_Vandal` filth on nearby walls

## must be true
- `RM_PaintGraffitiJob`/`RM_PaintGraffitiJoy` let a pawn walk to a nearby wall and paint `RM_Graffiti_Vandal` filth there as Meditative joy (`JobDriver_PaintGraffiti`, `JoyGiver_PaintGraffiti`).
- The forced mental break `RM_GraffitiPaintingSpreeBreak` (worker `MentalState_GraffitiSpree`, think tree `RM_GraffitiPaintingSpreeThinkTree`, state def `RM_GraffitiPaintingSpreeState`) drives repeated painting for a stretch rather than one job.
- `RM_Graffiti_Vandal` filth actually places — its `placementMask` requires the target terrain's own `filthAcceptanceMask` cover `Unnatural`; on a terrain that does NOT declare `Unnatural` acceptance, `TryMakeFilth` must legitimately produce nothing (that is not a bug, per the file's own comment about the prior all-sources regression).
- `ModExtension_Graffiti` is present on `RM_Graffiti_Vandal` (category/quality/maker-subject/god-satiation-hook fields) but nothing reads it yet this pass — a check should confirm the extension is attached, not that anything consumes it.
- `RM_BaseGraffiti` (abstract parent) is `thingClass Filth`, not the retired donor's custom Filth_Graffiti subclass.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.graffiti" and no XML error naming `ThingDefs_Graffiti.xml`/`JobDefs_Graffiti.xml`/`MentalStateDefs_Graffiti.xml`   # load-time
2. [D] def read-back: `ThingDef` `RM_Graffiti_Vandal` exists; `ParentName` chain includes `RM_BaseGraffiti`; `thingClass` = `Filth`; `filth/placementMask` contains `Unnatural`
3. [D] def read-back: `JobDef` `RM_PaintGraffitiJob` exists; `driverClass` = `RimMandrake.Graffiti.JobDriver_PaintGraffiti`
4. [D] def read-back: `JoyGiverDef`/joy-source `RM_PaintGraffitiJoy` exists and names `RM_PaintGraffitiJob`
5. [D] def read-back: `MentalStateDef` `RM_GraffitiPaintingSpreeBreak` exists; its worker resolves to `RimMandrake.Graffiti.MentalState_GraffitiSpree`
6. [D] def read-back: `RM_Graffiti_Vandal` carries a `RimMandrake.Graffiti.ModExtension_Graffiti` modExtension (non-null `GetModExtension`)
7. [B] jawa/spawn_pawn a colonist onto a fresh player-faction map cell next to a wall with an `Unnatural`-accepting floor, `jawa/order_pawn` (or `jawa/pawn_force_mental_break` with `breakDef=RM_GraffitiPaintingSpreeBreak`) to force the paint job → expect the pawn's current job resolves to `RM_PaintGraffitiJob`/`RM_GraffitiPaintingSpreeBreak` state (jawa/pawn_get or jawa/pawn_mental)
8. [B] jawa/list_things `defName=RM_Graffiti_Vandal` near the wall after the job/break runs some ticks → expect at least one `RM_Graffiti_Vandal` filth thing to have spawned
9. [D] read the spawned `RM_Graffiti_Vandal` filth thing's Beauty stat (jawa/thing_stats) → expect negative, per "negative Beauty" in the mod's own description

## [S]
Whether the six shipped texture variants of `RM_Graffiti_Vandal` (Graffiti Mod (Continued)'s art) actually read as legible marks on a wall at normal zoom is a human-pass concern (MOD_HUMAN_EXPLORATION_PASS_1). ⬇️ **Superseded as the authority by the `## north star` section below** — that question is now a binding bar, not a deferred concern.

## north star
state: VALIDATED
validated-hash: 335bccf3b6cbda91ab995e52922ffd51ae11365b0652dc0481dc6bf8fc10693c

✅ **BINDING.** Every line below was ruled or accepted in the owner's sitting of
2026-09-16 and validated on his word — *"Validate now, all 10 lines"* — at the hash
above. 8 must-show + 2 cannot-show now refuse Graffiti until a component claims each
with `shows=` and a screenshot satisfies it. Any later edit to this section reverts
it to DRAFT by hash mismatch, so amend it only in another sitting with him.

(`state:` is kept as a single bare token because `modcheck/cli.py` parses that field.)

### the experience  (OWNER'S WORDS — verbatim)

2026-08-30, filing `GRAFFITI_MOD_EXPANSION_1`:

> *"Add a queue item to assess the graffiti mod and expand it to include sacred
> graffiti, socially infuriating graffiti or amusing graffiti, or even beautiful
> graffiti."*

2026-08-31, `GRAFFITI_FRAMEWORK_BUILD_1`:

> *"Fully flesh out the graffiti mod now for tremendous application in the Jawa
> game. Jawas love graffiti. All the various kinds. Go for it!"*

2026-09-09, `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`:

> *"we want the base Graffiti mod to have a wide variety of functionality within
> it, not just the base examples we've provided in vanilla. It should be a mod
> more aligned to punk style graffiti such as is seen in urban settlements, as
> well as ideoligion-inspired sigils taken from the Rimworld ideoligions as they
> exist in the game."*

🔑 The through-line in all three: **variety, and marks that read as punk/urban
graffiti.** *"All the various kinds"* is a demand about appearance, not mechanism.

### must show

**A mark on a wall**
- [ ] `mark_actually_appears` — after a paint job or spree completes, a mark is
      visibly on the wall. Not an empty wall with a clean job log. (This is in the
      checklist because it has already failed silently: a colonist painted for
      ~20000 ticks with dozens of `TryMakeFilth` calls and produced nothing,
      because `placementMask` was `Any`. Every state assertion passed at the time.)
- [ ] `mark_reads_as_deliberate` — a mark reads at play zoom as something a hand
      made on purpose, not as scattered dirt or a smudge.
- [ ] `mark_reads_at_play_zoom` — every mark reads AS A MARK at normal play zoom
      (~64px), not only when zoomed in. 🔴 **Owner ruling, 2026-09-16**: this
      replaces a drafted `mark_scale_consistent` line. Scale *uniformity* is the
      wrong bar — real graffiti varies wildly in scale and a big piece beside a
      small tag is correct. The real defect is a mark that cannot be read at the
      zoom the game is played at.
- [ ] `mark_sits_on_the_wall` — a mark reads as being *on* the wall face, aligned
      to it, not as a decal floating over the floor beside it.

**Variety — his "all the various kinds"**
- [ ] `marks_visibly_various` — several marks in one colony are visibly different
      kinds of mark, not recolours of one.

**Register — punk/urban, and this world**
- [ ] `mark_register_is_punk_urban` — the mark set reads as urban/punk graffiti,
      not as clip-art icons or modern signage.
- [ ] `mark_carries_no_earth_signage` — no mark reads as a contemporary real-world
      sign (road-hazard triangle, exit sign, traffic glyph). 🔴 **Owner ruling,
      2026-09-16**: kept at FULL scope covering symbols, not narrowed to lettering
      only. He chose to replace the offending glyph rather than exempt it.

**Beauty legibility**
- [ ] `mark_ugliness_is_visible` — a Beauty −15 vandal scrawl looks worse than a
      Beauty −3 tally at a glance. The stat and the picture agree.

### cannot show

- [ ] `never_real_world_english` — legible real-world English words, or a
      third-party author's tag, in a mark. 🔴 **`RM_Graffiti_Vandal` shows this
      today**: "TARTE" is plainly legible in `vandal_0.png` (the donor author's own
      tag — Tarte/emipa606, art copied under MIT per About.xml), alongside further
      English tags in yellow, red and blue. Confirmed by looking at the sprite
      composited on a wall, 2026-09-16. `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` already
      put English lettering out of scope; the shipping default violates it.
- [ ] `never_reads_as_dirt` — a mark indistinguishable from vanilla filth at play
      zoom. If graffiti reads as a mess rather than a message, the mod is doing
      nothing his three quotes asked for.

### what this checklist refuses today, and why that is correct

Two of the four shipped marks fail it as written, both confirmed by eye
2026-09-16 rather than inferred:

1. **`RM_Graffiti_Vandal`** fails `never_real_world_english` and
   `mark_reads_at_play_zoom`. It is a dozen tiny doodles scattered across a 640²
   canvas, so at ~64px each is a few pixels of mush — and it is the mod's ONLY
   spontaneously-spawned mark, so the one mark players see unprompted is the one
   that does not read. → `GRAFFITI_VANDAL_ART_REGEN_1`.
2. **`RM_Graffiti_WarningGlyph`** fails `mark_carries_no_earth_signage` — a modern
   ISO hazard triangle with an exclamation mark. In fairness the brushwork is
   genuinely rough and hand-painted; it is the *iconography* that is Earth.
   → `GRAFFITI_WARNGLYPH_INUNIVERSE_1`.

`RM_Graffiti_TallyMarks` and `RM_Graffiti_Scratches` pass, and are the mod's best
art. (Noted honestly: groups-of-five-with-a-slash is also an Earth convention, but
a far more universal one than ISO signage, and it was not ruled against.)

### deliberately NOT a line here
A drafted `mark_variants_do_not_repeat` line was **cut by owner ruling
2026-09-16**: adjacent repeats depend on `Graphic_Random`'s pick rather than on the
art, so a run would pass or fail by luck. The underlying 6:2:2:2 variant imbalance
is real and is content work — `GRAFFITI_VARIANT_COUNTS_1`, not a visual bar.
