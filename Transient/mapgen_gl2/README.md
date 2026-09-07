# MAPGEN_GL_SHEET_1 round 2

Same 8 plans as round 1 (`Transient/mapgen_gl/`), rerun after two fixes:

1. **Mod list**: `ModsConfig.VANILLA_BRIDGE_GL.xml` (Core+5 DLC+Harmony+
   RimBridgeServer+GeologicalLandforms, 9 mods) instead of round 1's
   "minimal+GL" list, which included AlphaBiomes/OuterRim/our own
   vault-dungeons content -- proven contaminated by
   CORPUS_STATS_VANILLA_CONTROLS_1 the same night (Totemic/Spikecore/
   OuterRim floor tiles are not vanilla and would make the GL screenshot
   an unfair comparison against the painter's vanilla-only vocabulary).
2. **Camera**: round 1's own note said screenshots were "default-zoom
   partial views". `rimworld/screenshot_cell_rect` at the full 250x250 map
   simply REFUSES (`requiredRootSize` is always exactly `crop_size/2`, and
   the camera's root size is hard-capped at 100 even with
   `set_camera_zoom_extension` on -- 250 needs 125). Fix: a centred
   200x200 crop at `rootSize=100`, the largest crop that clears the cap;
   verified empirically before committing to the full 8-cycle run. Every
   one of these 8 plans has landform radius <=~77 cells, comfortably
   inside a 200x200 centre crop.

Also added: in-process retry (up to 3 tile re-rolls via
`go_to_main_menu` + `start_debug_game_ready`, no restart needed --
the custom landform file is already loaded for the session) when
`Landforms:` comes back empty, since round 1's `RUT_Gen_06` failed with an
otherwise byte-identical recipe (diff showed only RandSeed/Frequency
differ) -- consistent with a WorldTileReq that only some tiles satisfy,
not a malformed recipe.

## result: 6/8 (down from round 1's 7/8, but a materially better instrument)

- Canyon (01, 03, 04, 08): APPLIED, first try each.
- LoneMountain (02): APPLIED, first try.
- Crater (07): APPLIED, first try.
- **Sinkhole (05, 06): NOT applied, 3/3 tile re-rolls each, `Landforms: None`
  every time.** Round 1 had 1 of these 2 Sinkhole seeds succeed (05, tile
  7763) and the other fail (06) with an otherwise-identical recipe. Combined
  across both rounds: Sinkhole succeeded 1 time out of 8 attempts, every
  other category succeeded on the first or second try every time. The two
  Sinkhole recipes' WorldTileReq blocks are identical to each other and to
  Canyon's on every field checked (including RiverRequirement max=0, shared
  with the successful Canyon recipe) -- narrowed but NOT root-caused. Next
  step for whoever picks this up: compare gl_emit.py's Sinkhole base-graph
  mapping against the shipped Sinkhole landform's own WorldTileReq/node
  graph, or just budget more re-roll attempts for this one category.

## the sheet: comparator_gl_vs_painter_v2.png

Top row: in-game GL screenshot (framed via the fix above). Bottom row:
mapgen_paint.py round 2 (see MAPGEN_PAINTER_V1_1's own round-2 note).
`RUT_Gen_05`/`06` show an honest grey "no GL shot" tile (compose_gl_vs_painter.py's
existing behaviour) rather than being silently dropped.

**First real convergence signal** (FOUNDRY read, not an owner keep/cut):
GL's canyon is visibly WIDER and more braided/textured than the painter's,
which reads as a single clean, comparatively narrow, mostly-uniform-width
channel. The painter's wander/notch mechanism (mapgen_paint.py's
`_organic_channel`) produces a believable wandering line, but GL's actual
terrain carving clearly varies width and branches more aggressively along
the channel's length. This is a concrete target for the painter's round 3
(and/or the calibration MAPGEN_CONVERGENCE_LOOP_1's step 4 wants fed back
into gl_emit.py's knob mapping), not vague "make it more organic" -- the
gap is specifically channel-width variance and branching density.

Owner keep/cut still owed on both this sheet and MAPGEN_PAINTER_V1_1's.
