# RimBridge traps: camera, rendering and screenshots

Part of the trap catalogue indexed in [../traps.md](../traps.md); its first law and admission test are there. Append a new trap to the topic file it belongs to.

## A screenshot taken while paused can be the previous frame
**Symptom:** `screenshot_cell_rect` before and after a verified 36-cell terrain change produced **byte-identical** PNGs, same md5 — indistinguishable from the "terrain changed in the grid but does not redraw" failure.
**Cause:** the game was paused, so no new frame had been rendered between the two captures. The crop was real, the change was real, the image was stale.
**Fix:** `step_game_ticks` a few ticks before capturing, and `frame_cell_rect` on the target first — zoomed out over dense canopy a 6×6 patch is too small to see anyway.
**Recurs when:** `screenshot_cell_rect` with `set_time_speed` at 0. A screenshot is evidence about the *renderer*, not about game state; settle state with a data read and let the picture cover only what data cannot show.

## You cannot photograph a stale mesh — moving the camera repaints it
**Symptom:** paint a rect with `refresh=false`, screenshot, call `jawa/refresh_rect`, screenshot again — **the two images are identical and the "stale" one already shows the new terrain.** Reads as "refresh_rect does nothing".
**Cause:** every framed-shot tool moves the camera — `rimworld/screenshot_cell_rect` re-roots and re-zooms, `Session.look()` calls `jump_camera_to_cell` first — and camera movement re-enters the map sections, triggering the very redraw the test was trying to catch.
**Fix:** none available. `refresh_rect`'s **visible half is UNPROVEN** and this method cannot prove it; its data half is proven, in that it accepts a well-formed rect and refuses a malformed one. A real test needs a shot from an already-stationary camera taken before the unrefreshed paint, which no current tool composes.
**Recurs when:** any visual A/B over the bridge — ask what the act of looking changes. Also: the tool is `rimworld/jump_camera_to_cell`; there is no `jump_camera_to`.

## 🔴 Zooming below the engine's floor renders the whole map FLAT RED — and it looks exactly like catastrophic texture corruption
**Symptom:** terrain replaced by flat saturated red/cyan/yellow blocks while pawns and UI text still draw correctly. Reads unmistakably as a broken texture atlas.
**Cause:** `rimworld/set_camera_zoom_extension {"enabled": true}` widens the camera range to 0..100. **`rootSize` below the engine's normal floor (~11) breaks the world mesh render.** `rootSize 6` produced it; 11–15 are clean.
**Fix:** keep `rootSize` ≥ 11, and **turn the extension off when you are done** — `{"enabled": false}`. It is not harmless litter.
**How to tell it apart from real corruption, cheaply:**
- **It heals.** Return to a legal `rootSize` and the frame is correct again. A corrupted atlas does not heal in place.
- **PNG file size is the corroborator.** Flat colour compresses tiny: the red frame was **0.49 MB** against **2.4–3.7 MB** for clean frames of the same scene. Check `ls -la` on the screenshot before believing your eyes.
- Bracket it: shoot at a legal zoom 30 s either side.
**Recurs when:** any wide-area capture, because the temptation is to zoom out past the floor to fit a big structure in frame. Use `rimworld/screenshot_cell_rect` instead.
🔴 **This nearly cost two false verdicts in one session** — a retired seat almost condemned eight working art mods, and another seat diagnosed a corrupted texture atlas and told the owner to restart, wrongly blaming a peer's file prune. **The zoom artifact is more convincing than the real failure it imitates.**

## `take_screenshot` names files by the SECOND, so a burst silently collapses to one file
**Symptom:** four shots taken inside one second; four calls returned `success` with four paths; one file on disk. Three captures gone, no error.
**Cause:** the filename stamp has one-second resolution (`rimbridge_YYYYMMDD_HHMMSS`), and later writes overwrite earlier ones.
**Fix:** pass an explicit distinct `name` per shot, or space captures more than a second apart. Verify by `ls -la` on the directory, not by the returned path — the path is returned whether or not the file survived.
**Recurs when:** any scripted multi-shot pass, which is every contact sheet and every rotation audit.

## 🔴 `set_camera_zoom` takes `rootSize` (a NUMBER), not `zoom` (a string)
`{"zoom": "Close"}` returns `success: true` and does **nothing** — the unknown
parameter name is dropped before the tool runs, exactly as the one law says. Every
screenshot in that session came out at max zoom while the calls all reported success,
and `get_camera_state` kept answering `zoomRange: "Closest"`.
Correct: `{"rootSize": 14.0}`. Roughly: 8–11 is nose-to-the-ground, **14 frames two
things six cells apart**, 60 is the far limit.
**Generalises to:** when a call succeeds and the picture does not change, read the
tool's own `inputSchema` off `list_tools` before doing anything else. Do not trust a
parameter name you inferred from a sibling tool.

## 🔴 A modal dialog FREEZES the rendered frame and corrupts its colours
While `Verse.Dialog_NodeTree` (a trade/comms offer) was open, `take_screenshot`
returned a **stale frame in wild false colour** — pure red ground, cyan water,
magenta pawns — with the clock frozen, while the UI layer on top drew correctly.
It is not a GPU fault and not a mod: `ticksGame` advanced exactly 60 on a stepped
call, so the SIM was alive and only the render was stuck.
🔑 `jawa/clear_ui` does **NOT** close it — it reports `closedCount: 0` and lists the
dialog in `remaining`. Use `rimworld/close_window {"windowType": "Dialog_NodeTree"}`,
which closes it cleanly; the very next screenshot renders correctly.
**Generalises to:** before believing anything you see in a screenshot, check
`clear_ui`'s `remaining` list. A window it cannot close can silently invalidate every
image you take, and false colour is easy to misread as an art or shader defect.

## `rimworld/screenshot_cell_rect` captures the SCREEN, top window and all

It returned `success: true` four times, for four different cell rects with four different
filenames, and wrote **four byte-identical PNGs** — of the **Debug log window**, which was
open over the map. No warning, no hint in the reply; the only tell was that the file sizes
matched to the byte.

⇒ Before any capture: `rimworld/get_ui_state` and look at `topWindowType`, then
`rimworld/close_window` it. Closing `LudeonTK.EditWindow_Log` made every capture distinct.
🔑 **And hash your screenshots.** Four identical md5s is the cheapest possible detector, and
nothing else would have caught it — the image was a perfectly good screenshot of the wrong
thing.
- **`screenshot_cell_rect` can crop the wrong screen region at far zoom**; crop from the full frame it saves beside the crop. It also draws NO pawns outside the MAIN camera's view rect (DynamicDrawManager culls by the live camera) while terrain, plants and buildings render: `jump_camera_to_cell` to the rect centre before every cell_rect shot that must show pawns. And on a paused game right after a map mutation (`destroy_batch` of 201 plants plus a zoom change) it returned a STALE image; `take_screenshot` showed the change, so prefer `take_screenshot` and crop, or compare against a full shot, before believing a cell_rect. Separately `get_cell_info` `cell.solidThingDefs` lists plants and filth, not only edifices: for an edifice check filter `cell.things` by `className` (Mineable/Building).

## `rimworld/jump_camera_to_pawn` — `pawnId` needs a `Thing_` prefix, and it is NOT animals

Measured 2026-08-26, full 582-mod list, 72 pawns.

`jawa/list_pawns` and `jawa/pawn_get` return `Human335585` / `Qormot62098`.
`rimworld/jump_camera_to_pawn`'s `pawnId` wants the `rimworld/list_colonists` form:

```
pawnId=Qormot62098   -> False     pawnId=Thing_Qormot62098   -> True
pawnId=Human335585   -> False     pawnId=Thing_Human335585   -> True
```

🔑 `pawnId = "Thing_" + <jawa id>`. Without it the call refuses **humans too**, so a failure
here is never evidence about species.

⚠️ **By `pawnName` it refuses on AMBIGUITY, not species.** Three pawns called `Qormot` on one
map produced `"Ambiguous current-map pawn name"`; `Loth-cat`, `Geralinura` and `Fungal ferret`
each aimed first try. ⛔ `rimworld/list_colonists` lists COLONISTS only (3 rows / 72 pawns) —
an animal never appears there, which is what made the id space look closed to animals.

## 🔴 Whole-map Set-terrain-(rect) cascaded into a per-frame NRE storm and render corruption (2026-08-29)

**What worked first:** rect debug tools ARE drivable stock: `execute_debug_action` on the
rect leaf arms the tool, then TWO `click_cell` calls (corner, corner) apply it — click-click,
not a drag; the tool stays armed for further pairs. Proven on a 10x10 (screenshot-verified).
**What then failed:** painting the full 250x250 map (10 bands x 2 passes, first with
VFEArch_Grass — a CONSTRUCTED lawn floor that renders error-red painted raw) alongside
destroy-non-colonists/clear-fog produced an every-frame `Root level exception in Update():
NullReferenceException` (one ref, repeated forever), map-wide magenta/blue material
corruption, and an unusable session. A 10x10 pass is NOT evidence for 62,500 cells x
thousands of plant destructions on a 585-mod stack.
**Also:** the debug LOG window auto-opens on the first error and then ABSORBS `click_cell`
clicks (the dispatcher clicks center-screen after jumping the camera), so follow-up rect
corners silently do nothing while the tool reads "First corner...". `rimworld/close_window`
(stock) closes it — but by then the storm may already be running.
**Fix:** terrain at scale is `jawa/set_terrain_batch`'s job; keep rect debug tools to small
patches; pick NATURAL terrain defs (GrasslandSoil), never constructed floors; check
`get_ui_state` for an open EditWindow_Log before any click_cell sequence.
**Generalises to:** any stock click-driven tool — a window that auto-opens on error eats
every later click, so the first error silently invalidates the rest of the batch.

## CORRECTION on the 2026-08-29 render-death: it is the WALL-MOUNT/shielded turret spawns, and it happened twice identically

Both sessions (worldmap, then gravship_scratch) died with the SAME per-frame NRE
(`[Ref 36A0E3C1]` PowerConnectionMaker.TryConnectToAnyPowerNet <- PowerNetManager <-
Map.MapUpdate), and in BOTH logs the storm begins immediately after the last stuffable
1x1's MakeThing line — i.e. among the spawns that log nothing: VQE_AncientShieldedTurret
+ the 10 wall-mounted turrets (HMC_Wall_*, ShipWallMountMiniTurret) spawned free-standing.
`MakeThing ... stuff=null, assigning default` is BENIGN (fired for the large batch that
rendered fine). Once the exception is on the map, every frame aborts before the map
drawer runs — the "wildly colorful"/blue screen is UNRENDERED frames, not texture
corruption — and it persists until the save is reloaded, because the broken power comp
is still spawned. Fog-clear and terrain-paint were exonerated by the second incident.
**Rule:** never bridge-spawn wall-mounted or shield-comp turrets onto open ground;
exclude `HMC_Wall_*`, `ShipWallMountMiniTurret`, `VQE_AncientShieldedTurret` from any
free-standing lineup, or give walls first.

## 🔴 A `world_tile_map_generate`'d map can render as a blank void — correct data, dead mesh

Measured 2026-09-13 (RIVER_STEAM_ANIMATION_1). Founded a Player settlement at a
fresh tile (`jawa/colony_found` + `jawa/world_tile_map_generate`, real
`ZBiome_Grasslands` tile with real river — `riverCount: 2` confirmed live via
`jawa/world_tile_get` before generating), switched to it (`Actions\Change Map`
debug action, confirmed via `jawa/map_info` → correct `mapId`/`mapBiome`), and
every DATA-level check was clean: `jawa/get_terrain_batch` read back real
`WaterMovingShallow`/`VEE_FertileRiverbank` cells, `rimworld/get_cell_info`
reported `"fogged": false` for the exact cell being screenshotted, and a
full-map `jawa/set_fog {"action":"unfog","rect":"0,0,250,250"}` drove fogged
cells to **0**. Every screenshot of that map (`take_screenshot`,
`screenshot_cell_rect`, at multiple zooms and coordinates, after
`jawa/refresh_rect` mesh-dirty calls) still rendered as a **uniform blank
brown void** with the bottom-left status bar reading **"Not visible area"** —
no terrain, no river, nothing recognisable. `get_camera_state` confirmed the
camera WAS at the requested map/position throughout.

**The very next screenshot, same session, same connection, on the PLAYER'S
NORMAL colony map (`Map_3`, loaded the ordinary way at game start) was
perfectly sharp** — full detail, correct lighting, no void. So this is not a
bridge-wide rendering failure, a fog bug, or a stale-mesh issue fixable by
`jawa/refresh_rect` (tried, no change). The one structural difference: Map_3
went through the game's normal `EnterMap`/`Current.Game.CurrentMap` setter
transition at world/game start; Map_4 was switched into via the **debug**
`Actions\Change Map` action after a `world_tile_map_generate` call, which
generates the `Map` object and its data but — on this evidence — does not
trigger whatever `MapDrawer` section-mesh regeneration a normal map-enter
does. The underlying `Map`/`FogGrid`/`TerrainGrid` are all genuinely correct;
only the drawn mesh is dead.

⇒ **Do not trust a screenshot of a `world_tile_map_generate`'d map you
entered via the `Change Map` debug action to show anything.** If a live visual
check is owed on such a map and it renders blank, this is very likely why —
it is not proof the feature/terrain/mechanism is missing. **No workaround
found this session** (tried: `jawa/refresh_rect` over the full map rect
before AND after switching, full `unfogAll`, re-jumping the camera, multiple
zoom levels). Candidates for a future session: look for a `[Tool]` that calls
`MapDrawer.RegenerateEverythingIn(...)`/`MapDrawer.MapMeshDirty` across the
WHOLE map (not just a rect — `refresh_rect` may only dirty the grid data
layer a section reads, not force the section's mesh rebuild), or find whether
entering via an actual caravan arrival (the normal `EnterMap` path) renders
correctly where `Change Map` does not.

**Generalises to:** any debug-shortcut that creates or switches to a map
without going through the game's normal map-entry code path — verified data
is not verified pixels; a screenshot of a debug-reached map needs its OWN
positive sanity check (screenshot a KNOWN-good already-rendering map first,
or a thing you spawned there, before trusting a blank result as meaningful).

## `rimworld/screenshot_cell_rect` cannot frame a whole 250x250+ map, even with zoom extension on

Measured 2026-09-07 (MAPGEN_GL_SHEET_1 round 2). A bare `{"x":0,"z":0,"width":250,
"height":250,"paddingCells":2}` call refuses: `success:false`,
`"Requested cell rectangle does not fit in the viewport at the selected camera root
size."`, `requiredRootSize: 125.0`. Enabling
`rimworld/set_camera_zoom_extension {"enabled":true}` raises `sizeRange.max` from 60
to 100 — still short of 125, and passing an explicit `rootSize` of 130 or 150 does
NOT override the cap: `appliedRootSize` silently clamps back to 100 and the call
still refuses on the same "does not fit" message. **The tool always insists the
WHOLE requested rect be visible; there is no partial-capture mode.**

Empirically, `requiredRootSize` is always exactly `crop_size / 2` for a square crop
(confirmed at 180/200/220 — 90/100/110 respectively) — so the largest square crop
that fits under the extended 100 cap is exactly **200x200**, never the bare map size
for anything bigger than that.

⇒ **For a map ≥220 cells on a side, request a CENTRED crop ≤200x200, not the full
map**, after `set_camera_zoom_extension{"enabled":true}` and an explicit
`"rootSize":100.0`. A crop this size loses only the outer margin — fine for framing
a landform/relief feature that is itself centred and well under radius 100, not fine
for anything that spans the map edges (a coastal or edge-anchored feature needs a
different approach, not attempted here).

**Generalises to:** any "frame X and screenshot" tool that computes a required zoom
and refuses below it — the FIX is a smaller request, not a bigger zoom number; the
zoom range itself has a real ceiling that no parameter on this call can raise past
100. Silent partial-view screenshots (RimWorld's own default zoom, pre-fix) are a
DIFFERENT failure from this one: default zoom shows an arbitrary small window with
no refusal at all, while this refuses loudly and produces nothing — cross-check
`success` on the response before trusting a screenshot exists, in both cases.
