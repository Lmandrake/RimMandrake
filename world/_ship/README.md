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

## Corrosion Halo, laid on the live ship — 2026-08-27

Chosen by the owner. `plan_corrosion_halo.json` is the whole scheme in MAP coordinates,
emitted by `gravship_floor_v2.py --emit-plan`, applied by
`src/RimMandrake/Utils/apply_floor_plan.py` and `apply_wall_colors.py`.

🔑 **The one thing that decides the order:** `SetFoundation`-adjacent operations refuse a
cell carrying an UNDER layer, and painting a floor WRITES one. So holes are cut first —
`removeTop` pops the natural terrain back up and nulls `under`, then the foundation
strips — and only then are the floors painted.

🔴 **There is no bridge tool for building colour, and the dev tool reads the MOUSE.**
`Verse/DebugToolsGeneral.cs:549` takes its cell from `UI.MouseCell()`, not from a
parameter, and rebuilds its FloatMenu every time — so the button's targetId can never be
cached. Three calls per wall: execute (which places the virtual mouse), read the menu,
click. ~2,300 calls for this hull. ⚠️ `SetColor_All` colours **every** thing in the cell,
conduits included.

⚠️ **`layer='color'` cannot CLEAR a colour** — the tool requires a ColorDef and
`SetTerrainColor(c, null)` is unreachable. The nearest thing to an eraser is
`guy762_StructureColor_T3M4Silver` (235,255,255), a 92% multiply.

⚠️ **The live result is hotter than the render.** The offline renders model the colour
grid as a plain multiply over the tile; in game the oranges come out markedly more
saturated. Treat the renders as composition studies, not colour proofs.

## The AFK pass, 2026-08-27 night

Four saves, each a decision point, in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves`:

| save | what it holds |
|---|---|
| `HT_A_floors` | Corrosion Halo in browns, 140 holes, thrusters west. The restore point. |
| `HT_B_signage` | + 14 Aurebesh word decals naming what each bay used to be |
| `HT_C_pads` | + both feet opened into landing pads |
| `HT_D_graves` | + REFINERY, KITCHEN and ARMORY gutted to ruins, and 8 design-note letters |

### 🔴 Three mechanisms measured the hard way

1. **`T: Set Color` has a per-GAME-SESSION budget of roughly 380 invocations.**
   759 painted on the first run, then 384, 384, and 250+134+0 across FRESH PROCESSES —
   so it is the game that degrades and no reconnect clears it. After that every menu
   misses and `execute_debug_action` still answers success. ⇒ **Colour a hull with
   MATERIAL instead**: `GravshipHull` takes any Metallic stuff and stuff carries
   colour. `MA_MegaBone` where the plating is sound, `DinoChitin` where it corrodes.
   One call, permanent, survives a reload. `apply_wall_stuff.py`.
2. **A stale `Verse.FloatMenu` blocks every debug tool after it, silently** — and
   `get_context_menu_options` cannot see that window, because a FloatMenu is not a
   debug context menu. Detection has to go through `get_ui_layout`.
3. **A ZONE CANNOT CARRY TEXT.** `jawa/map_zones createZone` ignores the label it is
   given and auto-names `Stockpile zone 1`. The map-label idea is dead. What does
   carry readable text WITH a camera target is `jawa/send_letter` — click the letter
   and the camera jumps to what the note is about. That is where the design notes went.

### ⚠️ Two things to redo in daylight

* **`jawa/list_things` truncated at `limit`** and I read the empty result as "the
  decals never placed". They had. Read `countMatched`, not `len(things)` — and filter
  by `defName` when hunting for one kind.
* **The ruins in the gutted bays are hash-placed and collide.** `placed: 12 of 12` is
  spawn attempts, not survivors; several wiped each other. The bays read as ruins, but
  the specific props are not the ones intended.
