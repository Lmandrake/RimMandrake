# The Helpful Transport — deck floor trials, 2026-08-27

Painted live through the bridge onto the printed ship (map rect `83,59 86x133`).

| file | what |
|---|---|
| `floor_candidates_sheet.png` | 15 candidate deck floors, one tile each, labelled with defName and map cell |
| `floor_tint_tests.png` | the COLOUR grid over an existing floor, plus the broken-substructure probe |
| `floor_patches.json` | patch id -> TerrainDef, and the screenshot each came from |
| `floor_patch_centres.json` | patch id -> the clearest deck cell in it, for panning to |
| `helpful_transport_floors_before.ops` | the ship's ORIGINAL floors, in `jawa/set_terrain_batch` ops grammar. Replay to restore |

Patch grid: rows **A (north) → D (south)**, columns **1 (west) → 4 (east)**, over the
ship's bounding box. `D1` holds no deck cells.

## Three things measured here

1. 🔴 **`VGE_DamagedSubstructure` and `BrokenSubstructure` are FOUNDATION-layer defs.**
   Written to `top` they report `cellsChanged` and leave the cell showing whatever was
   there; written to `foundation` they land. And a foundation is **invisible under a
   floor**, so they only read on cells with no floor at all.
2. 🔴 **`GU_MetalFloor2` is a natural/under terrain.** `SetTerrain` put it in the `under`
   grid, not `top` — so on a floored deck cell it vanishes, and on bare ground it looks
   like it worked. A non-layerable terrain cannot be a gravship deck.
3. ⭐ **The 1.6 colour grid tints any floor** — `jawa/set_terrain_layer layer='color'`
   with any of 181 `ColorDef`s, 144/144 cells, no refusals. This is the cheap lever: it
   multiplies 15 floors by 181 colours without authoring a pixel.

## Floor plan review, 2026-08-27

`deck_floors.html` (published) carries four candidate schemes over the same 4,034 deck
cells. Renders come from `src/RimMandrake/Utils/gravship_floor_designs.py`, which paints
the layout offline using **4-cell swatches cut from live captures at 30.17 px/cell** —
`tex/pal_*.png`. Nothing in the renders is an artist's impression.

🔑 **Why swatches and not the source 1024px PNG.** `SectionLayer_Terrain.Regenerate` sets
verts, colors and tris and **no UVs**, so RimWorld's terrain shader samples in WORLD space
— the on-screen repeat belongs to the shader, not the file. Measured by autocorrelation:
every palette terrain repeats on a 1-cell lattice with a 4-cell super-period, so a 4-cell
swatch tiles seamlessly and looks exactly like the game.

⭐ **The colour grid answers "can the greys be ancient hull".** Yes: `Structure_Granite`
over scaffold tile reads `73 66 68` against ancient hull's `71 71 71`. But it is a
MULTIPLY — every ColorDef darkens and none can lighten, so pick the lightest tile you
might want and tint down from it.
