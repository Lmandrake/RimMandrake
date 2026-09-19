# TERRAIN_GRID_RENDERER_1 — offline terrain grid → PNG, one fixed palette

Spec source: `design/RimMandrake/map_content_injection_research.md` §9.3 step 2
(owner ruled 2026-09-06). The map generator is tuned by LOOKING at hundreds of
outputs; a quicktest per look is 90 s, a game load is 25 min. Today no offline
renderer of a terrain grid exists (`rimbench/crater.py` only screenshots). This
is the iteration loop, and it is a prerequisite for every later step.

## spec

- Input: a 2-D grid of terrain identifiers, from EITHER `savemap.py` (a corpus
  `.rws`, shortHash per cell) OR a generated grid (defName per cell). Both must
  render through the same path so comparator sheets are like-for-like.
- Output: a PNG at N px per cell (default 2, so 250² → 500 px) plus an optional
  thumbnail; deterministic; no game, no bridge, no mod set.
- Palette: one fixed colour per terrain family, derived from the captured terrain
  textures where they exist (`render-offline-from-live-captures` memory: terrain
  has no UVs, value beats hue for contrast) and a documented fallback for unknown
  hashes/defNames (render magenta — never silently grey). Corpus maps carry other
  creators' mod sets, so unresolvable hashes WILL occur; they must be visible, and
  counted in the render's stdout line.
- A `--sheet` mode: several grids on one contact sheet with captions, for the
  comparator sheets in §9.3 step 4 (reuse the review-sheets skill's patterns,
  don't reinvent).
- Lives in `src/RimMandrake/Utils/rimbench/` beside `savemap.py`; a selftest that
  renders one corpus map and one synthetic grid and checks dimensions + the
  unknown-count line.

## verify

Render `World_45_In_Memory_of_Rain/InMemoryOfRain.rws` and `World_29_Blood_Gulch`
(both arid) to `Transient/`; the owner LOOKS and can name the landform from the
thumbnail. Unknown-hash count printed and non-negative. Selftest green.

## not chasing

Things/buildings layer, roofs, elevation shading, in-game colour fidelity. Terrain
only; the point is telling a canyon from a crater at thumbnail size.
